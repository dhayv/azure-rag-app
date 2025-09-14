from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

from models import QueryRequest, QueryResponse
from rag_service import RAGService

# Load environment variables
load_dotenv()

app = FastAPI(
    title="RAG AI App",
    description="Retrieval-Augmented Generation AI Application",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instance
rag_service = RAGService()


def get_rag_service() -> RAGService:
    """Dependency injection for RAG service"""
    return rag_service


@app.get("/", response_model=Dict[str, str])
async def root():
    return {"message": "RAG AI App is running!"}


@app.get("/health", )
async def health_check():
    return {"status": "healthy", "service": "rag-ai-app"}


@app.get("/api/v1/status")
async def api_status():
    return {
        "status": "operational",
        "version": "1.0.0",
        "service": "rag-ai-backend"
    }


@app.post("/api/v1/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    try:
        answer = rag_service.query(
            query=request.query,
            top=request.top,
            max_tokens=request.max_tokens
        )
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
