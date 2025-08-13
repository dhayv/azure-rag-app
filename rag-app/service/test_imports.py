#!/usr/bin/env python3
"""
Test script to verify all Azure imports work correctly
"""


def test_imports():
    """Test all Azure imports without connecting to services"""
    try:
        # Test Azure Core imports
        from azure.core.credentials import AzureKeyCredential
        print("✅ azure.core.credentials imported successfully")
        
        # Test Azure Identity imports
        from azure.identity import DefaultAzureCredential, AzureAuthorityHosts
        print("✅ azure.identity imported successfully")
        
        # Test Azure Search imports
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
        print("✅ azure.search.documents.indexes imported successfully")
        
        # Test dotenv import
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
        load_dotenv()  # Test the function
        
        # Test FastAPI imports
        from fastapi import FastAPI
        print("✅ FastAPI imported successfully")
        
        # Test uvicorn import
        import uvicorn
        print("✅ uvicorn imported successfully")
        
        # Use the imports to verify they work
        _ = AzureKeyCredential("test")
        _ = DefaultAzureCredential()
        _ = AzureAuthorityHosts.AZURE_PUBLIC_CLOUD
        _ = SearchIndexClient(endpoint="https://test.search.windows.net/", credential="test")
        _ = SimpleField(name="test", type=SearchFieldDataType.String)
        _ = ComplexField(name="test", fields=[])
        _ = SearchField(name="test", type=SearchFieldDataType.String)
        _ = SearchableField(name="test", type=SearchFieldDataType.String)
        _ = SearchIndex(name="test", fields=[])
        _ = SemanticConfiguration(name="test", prioritized_fields=None)
        _ = SemanticField(field_name="test")
        _ = SemanticPrioritizedFields(title_field=None)
        _ = SemanticSearch(configurations=[])
        _ = VectorSearch(algorithms=[], profiles=[])
        _ = VectorSearchProfile(name="test", algorithm_configuration_name="test")
        _ = HnswAlgorithmConfiguration(name="test", kind="hnsw")
        _ = ExhaustiveKnnAlgorithmConfiguration(name="test", kind="exhaustiveKnn")
        _ = FastAPI()
        _ = uvicorn.__version__
        
        print("\n🎉 All imports successful! Your environment is properly configured.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    test_imports()
