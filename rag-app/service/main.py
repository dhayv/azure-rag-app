from fastapi import FastAPI

app = FastAPI(
    title="RAG AI App",
    description="Retrieval-Augmented Generation AI Application",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {"message": "RAG AI App is running!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "rag-ai-app"}


@app.get("/api/v1/status")
async def api_status():
    return {
        "status": "operational",
        "version": "1.0.0",
        "service": "rag-ai-backend"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
