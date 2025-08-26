import glob
import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv
from openai import AzureOpenAI
from tqdm import tqdm

load_dotenv(Path(__file__).parent.parent / ".env")

DATA_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data_samples", "stack_overflow")
)
INDEX_NAME = os.environ["AZURE_SEARCH_INDEX"]
DEPLOYMENT_NAME = os.environ["AZURE_OPENAI_EMBED_DEPLOYMENT"]
CACHE_FILE = Path(__file__).parent / "embeddings_cache.json"

SEARCH_CLIENT = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=os.getenv("AZURE_SEARCH_INDEX", "threads-index"),
    credential=AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]),
)

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-10-21",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n*", re.DOTALL)


def load_cache() -> Dict[str, List[float]]:
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_cache(cache: Dict[str, List[float]]) -> None:
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)


def hash_text(text: str) -> str:
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def iter_md_files() -> List[str]:
    return sorted(glob.glob(os.path.join(DATA_ROOT, "**", "*.md"), recursive=True))


def parse_front_matter(text: str) -> Tuple[Dict[str, Any], str]:
    m = FRONT_MATTER_RE.match(text)
    meta: Dict[str, Any] = {}
    body = text
    if m:
        meta = yaml.safe_load(m.group(1)) or {}
        body = text[m.end():]
    return meta, body


def chunk_preserve_code(text: str, max_len: int = 1600, overlap: int = 200) -> List[str]:
    parts: List[str] = []
    segments = re.split(r"(```.*?```)", text, flags=re.DOTALL)
    buf = ""
    for seg in segments:
        if len(buf) + len(seg) <= max_len:
            buf += seg
        else:
            if buf.strip():
                parts.append(buf.strip())
            buf = (buf[-overlap:] if overlap and len(buf) > overlap else "") + seg
            while len(buf) > max_len:
                parts.append(buf[:max_len].strip())
                buf = buf[max_len - overlap:]
    if buf.strip():
        parts.append(buf.strip())
    return parts


def embed_with_retry(texts: List[str], max_retries: int = 3, delay: float = 2.0) -> List[List[float]]:
    for attempt in range(max_retries):
        try:
            resp = client.embeddings.create(input=texts, model=DEPLOYMENT_NAME)
            return [d.embedding for d in resp.data]
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt)  # Exponential backoff
                print(f"Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                time.sleep(wait_time)
                continue
            else:
                raise e


def get_embeddings_with_cache(texts: List[str], cache: Dict[str, List[float]]) -> List[List[float]]:
    embeddings = []
    texts_to_embed = []
    text_indices = []
    
    for i, text in enumerate(texts):
        text_hash = hash_text(text)
        if text_hash in cache:
            embeddings.append(cache[text_hash])
        else:
            texts_to_embed.append(text)
            text_indices.append(i)
    
    if texts_to_embed:
        print(f"Computing embeddings for {len(texts_to_embed)} new chunks...")
        new_embeddings = embed_with_retry(texts_to_embed)
        
        for i, (text, embedding) in enumerate(zip(texts_to_embed, new_embeddings)):
            text_hash = hash_text(text)
            cache[text_hash] = embedding
            embeddings.insert(text_indices[i], embedding)
        
        time.sleep(0.5)  # Polite delay between batches
    
    return embeddings


def make_doc_id(slug: str, idx: int) -> str:
    return f"{slug}::chunk{idx}"


def slug_from_path(p: str) -> str:
    base = os.path.splitext(os.path.basename(p))[0]
    return base.lower()


def to_docs(path: str, cache: Dict[str, List[float]]) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    meta, body = parse_front_matter(raw)

    assert meta.get("source") and meta.get(
        "title"
    ), f"Missing required front-matter in {path}"
    assert "# RAW_THREAD" in body or len(body) > 300, f"Body looks too short in {path}"

    body = re.sub(r"^# RAW_THREAD\s*\n", "", body.strip())

    chunks = chunk_preserve_code(body)
    slug = slug_from_path(path)

    vectors = get_embeddings_with_cache(chunks, cache)

    docs = []
    for i, (txt, vec) in enumerate(zip(chunks, vectors)):
        docs.append(
            {
                "id": make_doc_id(slug, i),
                "content": txt,
                "contentVector": vec,
                "source": meta.get("source", ""),
                "title": meta.get("title", ""),
                "topics": meta.get("topic", []),
                "captured_at": meta.get("captured_at", ""),
                "license": meta.get("license", ""),
                "attribution": meta.get("attribution", ""),
                "chunk_index": i,
                "doc_type": "stackoverflow_thread",
            }
        )
    return docs


def upload_batch(docs: List[Dict[str, Any]]) -> None:
    result = SEARCH_CLIENT.upload_documents(docs)
    failed = [r for r in result if not r.succeeded]
    if failed:
        raise RuntimeError(f"Failed uploads: {failed[:3]} ... total={len(failed)}")


def main() -> None:
    cache = load_cache()
    print(f"Loaded cache with {len(cache)} cached embeddings")
    
    paths = iter_md_files()
    print(f"Found {len(paths)} .md files under {DATA_ROOT}")
    total_docs = 0
    
    for p in tqdm(paths, desc="Ingesting"):
        try:
            docs = to_docs(p, cache)
            upload_batch(docs)
            total_docs += len(docs)
            time.sleep(1)  # Rate limiting between files
        except Exception as e:
            print(f"Error processing {p}: {e}")
            continue
    
    save_cache(cache)
    print(f"Saved cache with {len(cache)} embeddings")
    print(f"Uploaded {total_docs} chunks to index '{INDEX_NAME}'")


if __name__ == "__main__":
    main()
