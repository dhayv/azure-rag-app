import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI

load_dotenv()
INDEX = os.environ["AZURE_SEARCH_INDEX"]
search = SearchClient(os.environ["AZURE_SEARCH_ENDPOINT"], INDEX, AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]))
aoai = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
)
DEP = os.environ["AZURE_OPENAI_EMBED_DEPLOYMENT"]

question = "ArgoCD app-of-apps created but nothing shows in the UI. What's wrong?"
emb = aoai.embeddings.create(input=question, model=DEP).data[0].embedding

results = search.search(
    search_text=None,                          # vector-only
    vectors=[VectorizedQuery(vector=emb, k=5, fields="contentVector")],
    select=["id", "title", "source", "chunk_index"]
)
for r in results:
    print(r["id"], r["title"], r["source"])
