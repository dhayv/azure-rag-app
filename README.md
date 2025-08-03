# RAG App – Azure GitOps Platform

This repository contains the **Retrieval-Augmented Generation (RAG) application code**,  plus the CI/CD systems to ship it as a Helm-deployable artifact. It’s not a toy repo — it’s designed to run under real infra constraints and GitOps flows.

🔗 **Part of the full project:**  → [azure-gitops-platform](https://github.com/dhayv/azure-gitops-platform)

---

## 🧱 Structure

---

## 🧠 Why This Repo?

Too many apps ignore deployability. This one is built **from day one** to fit into an automated delivery pipeline, use OCI artifact standards, and respond to real Helm version signals.

This is not "just a backend." It’s a **delivery-optimized AI service** in a system context.

---

## 🚀 Responsibilities


- 🧠 Hosts **FastAPI-based RAG backend**, containerized for AKS
- 🐳 CI builds and pushes Docker image to Azure Container Registry
- 🪙 Packages Helm chart + pushes to OCI or Git path
- 🔖 Tags version for ArgoCD to consume declaratively
  
> Delivery lives here. Deployment is owned by [`rag-infra`](https://github.com/dhayv/azure-rag-infra) using GitOps.

---

## 🧪 Coming Soon

- Unit tests for FastAPI app  
- Frontend UI (optional)  
- Full chart publishing via GitHub Actions

