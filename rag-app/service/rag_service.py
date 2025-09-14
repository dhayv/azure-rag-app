import os
from pathlib import Path
from typing import Any, Tuple
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


def truncate_to_tokens(text: str, max_tokens: int = 250):
    enc = tiktoken.encoding_for_model("gpt-35-turbo")
    tokens = enc.encode(text)
    return enc.decode(tokens[:max_tokens])


class RAGService:
    def __init__(self):
        self.index = os.environ["AZURE_SEARCH_INDEX"]

        # Configure retry policy for Azure Search
        self.search_client = search_client
        self.openai_client = openai_client
        self.deployment_name = os.environ["AZURE_OPENAI_EMBED_DEPLOYMENT"]
        self.chat_deployment = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]

    def _get_embeddings(self, query: str):
        return self.openai_client.embeddings.create(input=query, model=self.deployment_name).data[0].embedding

    def _search_docs(self, embedding, top: int = 3):
        vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=5, fields="contentVector", kind="vector")

        result = search_client.search(
            search_text=None,
            vector_queries=[vector_query],
            select=["id", "title", "source", "chunk_index", "content", "topics"],
            top=top,
        )

        return result

    @retry(wait=wait_exponential(multiplier=1, min=2, max=15), stop=stop_after_attempt(5))
    def _chat(self, prompt: str, max_tokens: int = 300) -> Tuple[Any, int]:
        return self.openai_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.chat_deployment,
            max_tokens=max_tokens,
            temperature=0.2,
        )

    def query(self, query: str, top: int = 3, max_tokens: int = 300):
        embedding = self._get_embeddings(query)
        results = self._search_docs(embedding, top=top)

        sources_formatted = "=================\n".join([f"TITLE: {document['title']}, CONTENT: {truncate_to_tokens(document['content'], 250)}" for document in results])

        # Chat call
        response = self._chat(
            GROUNDED_PROMPT.format(query=query, sources=sources_formatted),
            max_tokens=max_tokens
        )

        # print("💬 Model response:", response.choices[0].message.content)
        return response.choices[0].message.content
