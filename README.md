# Azure RAG AI Application – Workload Layer

**Azure | FastAPI | OpenAI | AI Search | Vector Database | GitOps | Platform Architecture**

This repository governs the **workload layer** of the Azure RAG Platform.  
It delivers a **repeatable workload pattern** for Retrieval-Augmented Generation (RAG) services — engineered for production scale with FastAPI, Azure OpenAI, and Azure AI Search.  

The service is architected for **resilience and governance**: retries, caching, rate limits, and guardrails are built in by design.  
Application logic is fully separated from infrastructure governance, ensuring workloads remain modular and platform-ready under GitOps control.  

> A governed workload pattern — resilient, modular, and architected for multi-service scale.

🔗 **System Architecture** → This repository owns the **application layer**.  
The companion repo [rag-infra](https://github.com/dhayv/azure-rag-infra) governs the **delivery control layer**.  
Together, they define the Azure RAG Platform — a unified, declarative architecture for AI workloads in AKS.  

---

## 🏗️ Architecture Overview

- **Service Layer** → FastAPI application exposing query, health, and admin endpoints.  
- **Embedding Module** → Generates vector embeddings using Azure OpenAI.  
- **Vector Store Module** → Azure AI Search indexes and executes similarity queries.  
- **Guardrail Layer** → Enforces factual grounding, explicit citations, structured summarization, and controlled fallbacks.  
- **Separation of Concerns** → This repo owns workload logic; [rag-infra] governs deployment and delivery.  

---

## 🚀 Core Capabilities

- **Production-Grade RAG Workload**  
  Orchestrates embeddings, vector search, and completions through modular service classes designed for scale.  

- **Explicit Separation of Concerns**  
  - Runtime logic (FastAPI, RAGService class).  
  - Data pipeline (ingestion, indexing, caching).  
  - Guardrails (prompt template, retries, token trimming).  
  - Delivery governance fully delegated to [rag-infra].  

- **Guardrails by Design**  
  - Grounded prompts enforce source fidelity and factual answers.  
  - Explicit citations and structured summaries.  
  - Deliberate safety constraint: refusal when no valid context exists.  
  - Retry and exponential backoff ensure stability under load.  

- **Operational Resilience**  
  - Embedding cache reduces redundant calls.  
  - Token counting prevents overflow.  
  - API-level rate limiting aligns with Azure quotas.  
  - GitOps workflow guarantees reproducible delivery.  

---

## 🔄 End-to-End Flow

1. Client request enters FastAPI API.  
2. Embedding module generates vector representation.  
3. Vector search module queries Azure AI Search.  
4. Guardrail layer shapes results into grounded prompt.  
5. Azure OpenAI chat model returns factual, cited completion.  
6. Response is delivered back to the client.  

---

## 📌 Takeaway

This repository defines the **RAG workload pattern** of the Azure GitOps Platform.  
It delivers an AI application that is:  
- **Modular** → clear layers for service, pipeline, and guardrails.  
- **Governed** → workload logic separated from infra control.  
- **Production-Aware** → caching, retries, rate limits, token controls.  
- **Scalable** → repeatable under GitOps delivery across multiple workloads.  

**An AI-ready workload type — governed, resilient, and architected for platform operations.**
