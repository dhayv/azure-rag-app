# RAG App – Azure GitOps Platform

This repository contains the **Retrieval-Augmented Generation (RAG) application code**, Helm chart, and CI pipeline for containerization and chart release.

🔗 **Part of the full project:**  
→ [azure-gitops-platform](https://github.com/dhayv/azure-gitops-platform)

---

## 🧱 Structure


---

## 🚀 Responsibilities

- Containerizes the backend app with FastAPI
- Builds and pushes Docker image to ACR
- Packages Helm chart as OCI artifact or Git path
- Tags chart version for ArgoCD to deploy

> CI pipeline in this repo handles **build + delivery**.  
> Deployment is handled by [`rag-infra`](https://github.com/dhayv/azure-rag-infra) using GitOps.

---

## 🧪 Coming Soon

- Unit tests for FastAPI app  
- Frontend UI (optional)  
- Full chart publishing via GitHub Actions

