# Azure RAG AI Application

A production-ready Retrieval-Augmented Generation (RAG) application built with FastAPI, Azure OpenAI, and Azure AI Search. This project demonstrates how to build a scalable RAG system using Azure services with proper GitOps practices and infrastructure separation.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Azure OpenAI    │    │ Azure AI Search │
│                 │    │                  │    │                 │
│ • Health APIs   │───▶│ • Embeddings     │───▶│ • Vector Store  │
│ • Query Endpoint│    │ • Text Generation│    │ • Semantic Search│
│ • Admin APIs    │    │                  │    │ • Index Mgmt    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Features

- **FastAPI Backend**: Modern, fast web framework with automatic API documentation
- **Azure OpenAI Integration**: Text embeddings and chat completions
- **Azure AI Search**: Vector storage and semantic search capabilities
- **Data Ingestion Pipeline**: Automated processing of Stack Overflow Q&A data
- **Caching & Rate Limiting**: Production-grade API management
- **GitOps Workflow**: Infrastructure and application code separation
- **Modern Python Tooling**: `uv` package manager, `ruff` linting, type hints

## 📁 Project Structure

```
azure-rag-app/
├── rag-app/                          # Main application
│   ├── service/                      # FastAPI backend
│   │   ├── main.py                   # FastAPI application
│   │   ├── ingest_so.py              # Data ingestion pipeline
│   │   ├── quick_query.py            # Query testing script
│   │   ├── create_index.py           # Search index creation
│   │   ├── pyproject.toml            # Dependencies & config
│   │   └── embeddings_cache.json     # Embedding cache
│   ├── data_samples/                 # Sample data
│   │   └── stack_overflow/           # Stack Overflow Q&A files
│   └── .env                          # Environment variables
├── infra/                            # Infrastructure repository
│   └── create_index.py               # Index management script
└── rag-workspace.code-workspace      # VS Code multi-root workspace
```

## 🛠️ Prerequisites

- **Python 3.11+**
- **Azure Account** with:
  - Azure OpenAI Service
  - Azure AI Search Service
- **Git** for version control
- **VS Code** (recommended) with Python extension

## ⚙️ Setup

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd azure-rag-app

# Install uv package manager (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Navigate to service directory
cd rag-app/service

# Install dependencies
uv sync
```

### 2. Configure Azure Services

Create a `.env` file in `rag-app/` with your Azure credentials:

```bash
# Azure Cognitive Search Configuration
AZURE_SEARCH_ENDPOINT="https://your-search-service.search.windows.net"
AZURE_SEARCH_INDEX="threads-index"
AZURE_SEARCH_API_KEY="your-search-api-key"

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY="your-openai-api-key"
AZURE_OPENAI_ENDPOINT="https://your-openai-resource.openai.azure.com/"
AZURE_OPENAI_API_VERSION="2024-10-21"
AZURE_OPENAI_EMBED_DEPLOYMENT="embeddings"

# Index Configuration (from Azure Portal)
ALGORITHM_NAME="your-algorithm-name"
INDEX_PROFILE_NAME="your-profile-name"
```

### 3. Create Search Index

```bash
# Create the Azure AI Search index
uv run python create_index.py
```

### 4. Ingest Data

```bash
# Process and upload Stack Overflow data
uv run python ingest_so.py
```

## 🚀 Usage

### Start the FastAPI Server

```bash
# Development server with auto-reload
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use the provided script
./run.sh
```

### Test the Application

```bash
# Health check
curl http://localhost:8000/health

# API status
curl http://localhost:8000/api/v1/status
```

### Query the RAG System

```bash
# Test vector search
uv run python quick_query.py
```

## 📊 Data Pipeline

The ingestion pipeline (`ingest_so.py`) processes Stack Overflow Q&A data with:

- **Front-matter Parsing**: Extracts metadata from YAML headers
- **Code-aware Chunking**: Preserves code blocks during text splitting
- **Embedding Generation**: Creates vector embeddings using Azure OpenAI
- **Caching**: Stores embeddings to avoid recomputation
- **Rate Limiting**: Respects API limits (60 requests/minute)
- **Batch Processing**: Efficient handling of multiple documents

## 🔧 Development

### Code Quality

```bash
# Run linter with auto-fix
./ruff.sh

# Type checking
uv run mypy .
```

### Jupyter Notebooks

```bash
# Start Jupyter server
uv run jupyter notebook
```

### Git Workflow

This project follows GitOps principles:

- **Application Code**: Lives in `rag-app/`
- **Infrastructure Code**: Lives in `infra/` (separate repository)
- **Atomic Commits**: One commit per logical change
- **Meaningful Messages**: Clear, descriptive commit messages

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint |
| `/health` | GET | Health check |
| `/api/v1/status` | GET | API status |
| `/docs` | GET | Interactive API documentation |

## 🔒 Security

- Environment variables for sensitive data
- `.env` files excluded from version control
- Azure Key Credentials for service authentication
- Rate limiting to prevent API abuse

## 📈 Performance Features

- **Embedding Caching**: Avoids redundant API calls
- **Batch Processing**: Efficient bulk operations
- **Rate Limiting**: Respects Azure API limits
- **Exponential Backoff**: Robust error handling
- **Vector Search**: Fast similarity matching

## 🚨 Troubleshooting

### Common Issues

1. **Rate Limiting**: The ingestion script includes built-in rate limiting
2. **Missing Environment Variables**: Ensure all required variables are set in `.env`
3. **Index Not Found**: Run `create_index.py` before ingestion
4. **Import Errors**: Run `uv sync` to install dependencies

### Debug Mode

```bash
# Test imports without connecting to Azure
uv run python test_imports.py
```

## 📚 Dependencies

Key dependencies managed by `uv`:

- **FastAPI**: Web framework
- **Azure SDKs**: `azure-core`, `azure-identity`, `azure-search-documents`
- **OpenAI**: `openai` for Azure OpenAI integration
- **Data Processing**: `pandas`, `numpy`, `scikit-learn`
- **Utilities**: `python-dotenv`, `pyyaml`, `tqdm`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Stack Overflow community for the Q&A data
- Azure team for excellent AI services
- FastAPI team for the amazing framework
- The open-source Python community

---

**Built with ❤️ using Azure AI Services and FastAPI**