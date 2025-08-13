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
    SimpleField(name="HotelId", type=SearchFieldDataType.String, key=True, filterable=True),
    SearchableField(name="HotelName", type=SearchFieldDataType.String, sortable=True),
    SearchableField(name="Description", type=SearchFieldDataType.String),
    SearchField(
        name="DescriptionVector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=1536,
        vector_search_profile_name="my-vector-profile"
    ),
    SearchableField(name="Category", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchField(name="Tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String), searchable=True, filterable=True, facetable=True),
    SimpleField(name="ParkingIncluded", type=SearchFieldDataType.Boolean, filterable=True, sortable=True, facetable=True),
    SimpleField(name="LastRenovationDate", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True, facetable=True),
    SimpleField(name="Rating", type=SearchFieldDataType.Double, filterable=True, sortable=True, facetable=True),
    ComplexField(name="Address", fields=[
        SearchableField(name="StreetAddress", type=SearchFieldDataType.String),
        SearchableField(name="City", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
        SearchableField(name="StateProvince", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
        SearchableField(name="PostalCode", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
        SearchableField(name="Country", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
    ]),
    SimpleField(name="Location", type=SearchFieldDataType.GeographyPoint, filterable=True, sortable=True),
]

vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(name="my-hnsw-vector-config-1", kind="hnsw"),
        ExhaustiveKnnAlgorithmConfiguration(name="my-eknn-vector-config", kind="exhaustiveKnn")
    ],
    profiles=[
        VectorSearchProfile(name="my-vector-profile", algorithm_configuration_name="my-hnsw-vector-config-1")
    ]
)

semantic_config = SemanticConfiguration(
    name="my-semantic-config",
    prioritized_fields=SemanticPrioritizedFields(
        title_field=SemanticField(field_name="HotelName"), 
        content_fields=[SemanticField(field_name="Description")], 
        keywords_fields=[SemanticField(field_name="Category")]
    )
)

# Create the semantic settings with the configuration
semantic_search = SemanticSearch(configurations=[semantic_config])

semantic_settings = SemanticSearch(configurations=[semantic_config])
scoring_profiles = []
suggester = [{'name': 'sg', 'source_fields': ['Tags', 'Address/City', 'Address/Country']}]

# Create the search index with the semantic settings
index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search, semantic_search=semantic_search)
result = index_client.create_or_update_index(index)
print(f' {result.name} created')