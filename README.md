# Azure RAG Platform – Application & Delivery Layers

**Azure | FastAPI | OpenAI | Azure AI Search | Kubernetes | Argo CD | Terraform | GitOps**

The project has evolved into a **two-layer platform** that now lives side-by-side inside this workspace:

- `rag-app/` – the FastAPI Retrieval-Augmented Generation workload (code, data utilities, and Argo CD workload manifests).
- `infra/` – the GitOps control plane that bootstraps AKS, installs Argo CD, and keeps each environment (dev/staging/prod) in sync with Git.

Both folders remain independent repositories, but keeping them in a single workspace makes it easy to reason about the full path from data ingestion → API → Kubernetes delivery.

---

## 📁 Repository Map

| Path | Purpose |
| --- | --- |
| `rag-app/service/` | FastAPI app, ingestion scripts, and CLI helpers. |
| `rag-app/argocd/{dev,staging,prod}` | Environment-specific manifests synced by Argo CD. |
| `infra/terraform/` | Azure + AKS bootstrap (cluster, namespaces, secrets, workload identity). |
| `infra/apps/` | App-of-apps definitions that tell Argo CD which environments to track. |

---

## 🧠 Application Layer (`rag-app/`)

- **Service Contracts** → `/api/v1/query`, `/health`, `/api/v1/status` served by `service/main.py`.
- **RAG Orchestration** → `service/rag_service.py` wires embeddings, Azure AI Search vector lookups, conversational guardrails, and retries.
- **Data Utilities** → `service/create_index.py`, `service/ingest_so.py`, and `service/quick_query.py` manage search indexes, embeddings, and validation queries.
- **Operational Guardrails** → token trimming via `tiktoken`, exponential backoff with `tenacity`, request throttling in ingestion, and embedding caching (`embeddings_cache.json`).

### Local Development Flow
1. Copy `rag-app/.env.example` (if provided) or populate `rag-app/.env` with Azure OpenAI + AI Search values.
2. (Optional) Initialize your search index: `python rag-app/service/create_index.py`.
3. Ingest data samples: `python rag-app/service/ingest_so.py`.
4. Run the API: `cd rag-app/service && uvicorn main:app --reload --host 0.0.0.0 --port 8000` or `bash run.sh`.
5. Hit `http://localhost:8000/api/v1/query` with a JSON payload to validate end-to-end behaviour.

### Build & Publish
1. `docker build -t <acr-name>.azurecr.io/rag-app:<tag> -f rag-app/Dockerfile rag-app`
2. `docker push <acr-name>.azurecr.io/rag-app:<tag>`
3. Update the image tag in `rag-app/argocd/<env>/deployment.yaml` and commit.

---

## 🚢 Delivery Layer (`infra/`)

- **Terraform Bootstrap** (`infra/terraform/`):
  - Provisions AKS, workload identity, and grants AcrPull to the cluster.
  - Creates namespaces (`ragapp-dev`, `ragapp-staging`, `ragapp-prod`) and injects the `rag-api-env` secret per environment.
- **Argo CD App-of-Apps** (`infra/apps/`):
  - `apps/apps.yaml` seeds the root Argo CD application.
  - Environment apps (`dev-apps1.yaml`, `staging-apps1.yaml`, `prod-apps1.yaml`) track `rag-app/argocd/<env>` folders from the workload repo.
- **Namespace Bootstrap** (`infra/argo-cdnamespace.yaml`) ensures Argo CD installs into a dedicated namespace.

### GitOps Flow
1. `cd infra/terraform && terraform init && terraform apply` (fill `terraform.tfvars` with your resource group, AKS, OpenAI, and Search settings).
2. Point Argo CD at `infra/apps/apps.yaml` (either via `kubectl apply -f` or through the Argo UI). This registers the root app.
3. Each root app rehydrates the environment-specific Application objects, which then reconcile the manifests under `rag-app/argocd/<env>`.
4. Image/tag changes in `rag-app/argocd` automatically roll out via Argo CD once merged.

---

## 🔄 End-to-End Lifecycle

1. **Data Plane** – Author content, run ingestion, and validate search relevance locally.
2. **Service Layer** – Update FastAPI logic, prompts, or dependencies in `rag-app/service`.
3. **Container** – Build/push a new image referencing the latest code.
4. **GitOps** – Update the corresponding `rag-app/argocd/<env>` manifest with the new tag.
5. **Infra** – Ensure Terraform + Argo CD are converged so the workload redeploys automatically.

This structure keeps **workload logic modular** while the **delivery system stays declarative**, allowing each piece to evolve independently but still live together for a complete platform view.
