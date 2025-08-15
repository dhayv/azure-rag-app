import glob
import os
import re
from pathlib import Path
from typing import Any, Dict, List

import yaml
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv
from openai import AzureOpenAI
from tqdm import tqdm

load_dotenv(Path(__file__).parent.parent / ".env")

DATA_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data_samples", "stack_overflow")
)
INDEX_NAME = os.environ["SEARCH_INDEX"]

SEARCH_CLIENT = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=os.getenv("AZURE_SEARCH_INDEX", "vector-search-quickstart"),
    credential=DefaultAzureCredential(),
)

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-10-21",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

EMBED_DEPLOYMENT = os.environ["AZURE_OPENAI_EMBED_DEPLOYMENT"]

FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n*", re.DOTALL)


def iter_md_files() -> List[str]:
    return sorted(glob.glob(os.path.join(DATA_ROOT, "**", "*.md"), recursive=True))


def parse_front_matter(text: str) -> (Dict[str, Any], str):
    m = FRONT_MATTER_RE.match(text)
    meta = {}
    body = text
    if m:
        meta = yaml.safe_load(m.group(1)) or {}
        body = text[m.end():]
    return meta, body


def chunk_preserve_code(text: str, max_len=1600, overlap=200) -> List[str]:
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


def embed(texts: List[str]) -> List[List[float]]:
    resp = client.embeddings.create(input=texts, model=EMBED_DEPLOYMENT)
    return [d.embedding for d in resp.data]


def make_doc_id(slug: str, idx: int) -> str:
    return f"{slug}::chunk{idx}"


def slug_from_path(p: str) -> str:
    base = os.path.splitext(os.path.basename(p))[0]
    return base.lower()


def to_docs(path: str) -> List[Dict[str, Any]]:
    raw = open(path, "r", encoding="utf-8").read()
    meta, body = parse_front_matter(raw)

    assert meta.get("source") and meta.get(
        "title"
    ), f"Missing required front-matter in {path}"
    assert "

    body = re.sub(r"^

    chunks = chunk_preserve_code(body)
    slug = slug_from_path(path)

    vectors = embed(chunks)

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


def upload_batch(docs: List[Dict[str, Any]]):
    result = SEARCH_CLIENT.upload_documents(docs)
    failed = [r for r in result if not r.succeeded]
    if failed:
        raise RuntimeError(f"Failed uploads: {failed[:3]} ... total={len(failed)}")


def main():
    paths = iter_md_files()
    print(f"Found {len(paths)} .md files under {DATA_ROOT}")
    total_docs = 0
    for p in tqdm(paths, desc="Ingesting"):
        docs = to_docs(p)
        upload_batch(docs)
        total_docs += len(docs)
    print(f"Uploaded {total_docs} chunks to index '{INDEX_NAME}'")


if __name__ == "__main__":
    main()
