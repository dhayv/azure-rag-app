import os
import itertools
from pathlib import Path
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline.policies import RetryPolicy
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI
from tenacity import retry, wait_exponential, stop_after_attempt
import tiktoken

load_dotenv(Path(__file__).parent.parent / ".env")

INDEX = os.environ["AZURE_SEARCH_INDEX"]

# Configure retry policy for Azure Search
search_retry_policy = RetryPolicy(
    retry_total=3,
    retry_backoff_factor=1.0,
    retry_backoff_max=60,
    retry_on_status_codes=[429, 503, 504]
)

search_client = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=INDEX,
    credential=AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]),
    retry_policy=search_retry_policy
)


openai_client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
)

deployment_name = os.environ["AZURE_OPENAI_EMBED_DEPLOYMENT"]
CHAT_DEPLOYMENT = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]

# ==== Request & Token Tracking ====
call_id = itertools.count(1)
total_requests = 0
total_tokens = 0


def count_tokens(text: str):
    enc = tiktoken.encoding_for_model("gpt-35-turbo")
    return len(enc.encode(text))


def log_request(req_type: str, prompt: str, max_tokens=0):
    global total_requests, total_tokens
    # n = next(call_id)  # Commented out since print is disabled
    prompt_tokens = count_tokens(prompt)
    est_tokens = prompt_tokens + max_tokens
    total_requests += 1
    total_tokens += est_tokens
    # print(f"📡 Request #{n} → {req_type} | Prompt: {prompt_tokens} tokens | "
    #       f"Max out: {max_tokens} | Est total: {est_tokens} | "
    #       f"Cumulative: {total_requests} req / {total_tokens} tokens this run")
    return est_tokens


GROUNDED_PROMPT = """
You are an AI assistant.
Answer the question using only the sources provided.
- Use bullet points if there are multiple facts.
- If the answer is longer than 3 sentences, give a short summary.
- Always cite the source.
- If the sources don’t have enough info, say “I don’t know.”
Sources:
{sources}

Question: {query}
"""


def tracked_embeddings(query):
    log_request("Embedding", query)
    return openai_client.embeddings.create(input=query, model=deployment_name)


@retry(wait=wait_exponential(multiplier=1, min=2, max=15), stop=stop_after_attempt(5))
def tracked_chat(prompt, max_tokens=300):
    est_tokens = log_request("Chat", prompt, max_tokens=max_tokens)
    return openai_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=CHAT_DEPLOYMENT,
        max_tokens=max_tokens,
        temperature=0.2,
    ), est_tokens


query = "ArgoCD app-of-apps created but nothing shows in the UI. What's wrong?"

# Embedding call
embed = tracked_embeddings(query).data[0].embedding

# create VectorizedQuery with the embedding
vector_query = VectorizedQuery(vector=embed, k_nearest_neighbors=5, fields="contentVector", kind="vector")

# search using the query
result = search_client.search(
    search_text=None,
    vector_queries=[vector_query],
    select=["id", "title", "source", "chunk_index", "content", "topics"],
    top=3,
)


def truncate_to_tokens(text: str, max_tokens: int = 250):
    enc = tiktoken.encoding_for_model("gpt-35-turbo")
    tokens = enc.encode(text)
    return enc.decode(tokens[:max_tokens])


sources_formatted = "=================\n".join([f"TITLE: {document['title']}, CONTENT: {truncate_to_tokens(document['content'], 250)}" for document in result])

# Chat call
response, used_tokens = tracked_chat(
    GROUNDED_PROMPT.format(query=query, sources=sources_formatted),
    max_tokens=300
)

# print("💬 Model response:", response.choices[0].message.content)
print(response.choices[0].message.content)
