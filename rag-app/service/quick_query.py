import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI

load_dotenv()

INDEX = os.environ["AZURE_SEARCH_INDEX"]
search_client = SearchClient(os.environ["AZURE_SEARCH_ENDPOINT"], INDEX, AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]))

openai_client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
)

deployment_name = os.environ["AZURE_OPENAI_EMBED_DEPLOYMENT"]

query = "ArgoCD app-of-apps created but nothing shows in the UI. What's wrong?"

# generate embedding for a query
embed = openai_client.embeddings.create(input=query, model=deployment_name).data[0].embedding

# create VectorizedQuery with the embedding
vector_query = VectorizedQuery(vector=embed, k_nearest_neighbors=5, fields="contentVector", kind="vector")

# search using the query
result = search_client.search(
    search_text=None,            
    vector_queries=[vector_query],
    select=["id", "title", "source", "chunk_index"],
)

# display results
for r in result:
    print(r["id"])
    print(r["title"])
    print(r["source"])