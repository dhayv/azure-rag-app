from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
import os
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SimpleField,
    ComplexField,
    SearchField,
    SearchFieldDataType,    
    SearchableField,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    VectorSearch, 
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
    ExhaustiveKnnAlgorithmConfiguration    
)

load_dotenv(override=True) # take environment variables from .env.

search_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
credential = DefaultAzureCredential()
index_name = os.getenv("AZURE_SEARCH_INDEX", "vector-search-quickstart")

# Create credential
credential = DefaultAzureCredential() if not search_key or search_key == "Your search service admin key" else search_key

# Create a search schema
index_client = SearchIndexClient(
    endpoint=search_endpoint, credential=credential)
fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=False, sortable=False, facetable=False, searchable=False),
    SimpleField(name="content", type=SearchFieldDataType.String, searchable=True, filterable=False, sortable=False, facetable=False),
    SimpleField(name="source", type=SearchFieldDataType.String, searchable=True, filterable=True, sortable=False, facetable=True),
    SimpleField(
        name="title",
        type=SearchFieldDataType.String,
        searchable=True, searchable=True, filterable=True, sortable=False, facetable=True
    ),
    SimpleField(name="topics", type=SearchFieldDataType.String, sortable=False, filterable=True, facetable=True),
    SearchField(name="captured_at", type=SearchFieldDataType.String, searchable=True, filterable=True, facetable=True),
    SimpleField(name="license", type=SearchFieldDataType.String, filterable=True, sortable=False, facetable=True),
    SimpleField(name="attribution", type=SearchFieldDataType.String, filterable=False, sortable=False, facetable=False),
    SimpleField(name="chunk_index", type=SearchFieldDataType.Int32, filterable=True, sortable=True, facetable=False),
    SimpleField(name="doc_type", type=SearchFieldDataType.String, filterable=True, sortable=False, facetable=True),
    SearchField(
        name="contentVector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,  # must be True for vector fields
        vector_search_dimensions=1536,
        vector_search_profile_name="SO_QA"
    ),
]

vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(
            name="hnsw",
            kind="hnsw",
            parameters={"m": 4, "efConstruction": 400, "efSearch": 500, "metric": VectorSearchAlgorithmMetric.COSINE}
        ),
    ],
    profiles=[
        VectorSearchProfile(name="SO_QA", algorithm_configuration_name="hnsw")
    ]
)


# Create the search index with the semantic settings
index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search, semantic_search=semantic_search)
result = index_client.create_or_update_index(index)
print(f"Index '{index_name}' created with vector field dims={EMBED_DIMS}.")