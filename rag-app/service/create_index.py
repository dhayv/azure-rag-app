import os
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
    VectorSearch,
    VectorSearchAlgorithmMetric,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch,
    ScoringProfile,
    TagScoringFunction,
    TagScoringParameters
)
from dotenv import load_dotenv

# Load .env from the rag-app directory (parent of service)
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

search_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
credential = AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"])
index_name = os.getenv("AZURE_SEARCH_INDEX", "threads-index")


index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
fields = [
    SimpleField(
        name="id",
        type=SearchFieldDataType.String,
        key=True,
        filterable=False,
        sortable=False,
        facetable=False,
        searchable=False,
    ),
    SimpleField(
        name="content",
        type=SearchFieldDataType.String,
        searchable=True,
        filterable=False,
        sortable=False,
        facetable=False,
    ),
    SimpleField(
        name="source",
        type=SearchFieldDataType.String,
        searchable=True,
        filterable=True,
        sortable=False,
        facetable=True,
    ),
    SimpleField(
        name="title",
        type=SearchFieldDataType.String,
        searchable=True,
        filterable=True,
        sortable=False,
        facetable=True,
    ),
    SimpleField(
        name="topics",
        type=SearchFieldDataType.Collection(SearchFieldDataType.String),
        sortable=False,
        filterable=True,
        facetable=True,
    ),
    SearchField(
        name="captured_at",
        type=SearchFieldDataType.String,
        searchable=True,
        filterable=True,
        facetable=True,
    ),
    SimpleField(
        name="license",
        type=SearchFieldDataType.String,
        filterable=True,
        sortable=False,
        facetable=True,
    ),
    SimpleField(
        name="attribution",
        type=SearchFieldDataType.String,
        filterable=False,
        sortable=False,
        facetable=False,
    ),
    SimpleField(
        name="chunk_index",
        type=SearchFieldDataType.Int32,
        filterable=True,
        sortable=True,
        facetable=False,
    ),
    SimpleField(
        name="doc_type",
        type=SearchFieldDataType.String,
        filterable=True,
        sortable=False,
        facetable=True,
    ),
    SearchField(
        name="contentVector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,  # must be True for vector fields
        vector_search_dimensions=1536,
        vector_search_profile_name="vdb",
    ),
]

vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(
            name="hnsw-config",
            kind="hnsw",
            parameters={
                "m": 4,
                "efConstruction": 400,
                "efSearch": 500,
                "metric": VectorSearchAlgorithmMetric.COSINE,
            },
        ),
    ],
    profiles=[VectorSearchProfile(name="vdb", algorithm_configuration_name="hnsw-config")],
)

semantic_config = SemanticConfiguration(
    name="my-semantic-config",
    prioritized_fields=SemanticPrioritizedFields(
        title_field=SemanticField(field_name="title"),
        keywords_fields=[SemanticField(field_name="topics")],
        content_fields=[SemanticField(field_name="content")]
    )
)


semantic_search = SemanticSearch(configurations=[semantic_config])


scoring_profiles = [
    ScoringProfile(  
        name="my-scoring-profile",
        functions=[
            TagScoringFunction(
                field_name="topics",
                boost=5.0,
                parameters=TagScoringParameters(
                    tags_parameter="tags",
                ),
            )
        ]
    )
]


index = SearchIndex(
    name=index_name,
    fields=fields,
    vector_search=vector_search,
    semantic_search=semantic_search,
    scoring_profiles=scoring_profiles
)
result = index_client.create_or_update_index(index)
print(f"Index '{index_name}' updated")
