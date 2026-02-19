# ⚡ Agentic RAG v2.0

A production-grade, multi-agent Retrieval-Augmented Generation system with **intelligent query routing**, **speculative retrieval**, **semantic caching**, and a **premium dashboard UI**.

> **What makes it "Agentic"?** Unlike traditional RAG pipelines that blindly retrieve-then-generate, this system uses autonomous agents that _decide_ whether retrieval is needed, _verify_ their own answers, and _cache_ results for near-duplicate queries — all while streaming their reasoning to the user in real time.

---

## 🌟 Key Features

### Intelligence
- **Autonomous Query Routing** — AI decides if retrieval is even necessary
- **Answer Verification** — A dedicated agent cross-checks answers against source context
- **Source Attribution** — Every response links back to the exact documents used

### Performance
- **🏎️ Model Tiering** — Fast model (Claude 3.5 Haiku) for routing & verification, smart model (Claude 3.7 Sonnet) for answer synthesis
- **⚡ Speculative Retrieval** — Query analysis and document retrieval run in parallel via `asyncio.gather()` 
- **🧠 Semantic Caching** — Near-duplicate queries return instantly from an SQLite vector cache (cosine similarity ≥ 0.96)

### User Experience
- **Premium Dark Dashboard** — Glassmorphism, micro-animations, and agent color coding
- **Live Reasoning Panel** — Watch agents think in real time with step-by-step visualization
- **Document Management** — Drag-and-drop upload with knowledge base management
- **Settings Dashboard** — Configure LLM provider, temperature, and retrieval depth from the UI

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Query                           │
└─────────────────┬───────────────────────────────────────────┘
                  ▼
         ┌────────────────┐
         │ Semantic Cache  │──── HIT ──▶ ⚡ Instant Response
         └───────┬────────┘
                 │ MISS
                 ▼
    ┌────────────────────────────┐
    │   Parallel Execution       │
    │  ┌──────────┐ ┌─────────┐ │
    │  │  Query    │ │Retrieval│ │
    │  │  Agent    │ │ Agent   │ │
    │  │ (Haiku)  │ │ (FAISS) │ │
    │  └────┬─────┘ └────┬────┘ │
    └───────┼─────────────┼──────┘
            ▼             ▼
     Needs retrieval? ─── Yes ──▶ Keep results
           │                      
           No ──▶ Discard         
            ▼
    ┌───────────────┐
    │  Synthesis    │
    │  Agent        │  (Claude 3.7 Sonnet)
    │  (Smart)      │
    └───────┬───────┘
            ▼
    ┌───────────────┐
    │  Verifier     │
    │  Agent        │  (Claude 3.5 Haiku)
    │  (Fast)       │
    └───────┬───────┘
            ▼
    Store in Cache ──▶ ✅ Verified Response
```

### Agent Breakdown

| Agent | Model Tier | Purpose |
|-------|-----------|---------|
| **Query Agent** | 🏎️ Fast (Haiku) | Analyzes intent, decides if retrieval is needed |
| **Retrieval Agent** | — (FAISS) | Fetches top-k relevant document chunks |
| **Synthesis Agent** | 🧠 Smart (Sonnet) | Generates the final answer from context |
| **Verifier Agent** | 🏎️ Fast (Haiku) | Cross-checks answer against source documents |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.9+, FastAPI, Uvicorn, SSE |
| **LLM (Production)** | AWS Bedrock — Claude 3.7 Sonnet + Claude 3.5 Haiku |
| **LLM (Development)** | Mock LLM (rule-based, zero cost) |
| **Vector Search** | FAISS (CPU), Sentence Transformers (`all-MiniLM-L6-v2`) |
| **Caching** | SQLite + cosine similarity |
| **Frontend** | HTML5, CSS3 (glassmorphism, dark theme), Vanilla JS |
| **Deployment** | Docker, AWS (S3, IAM) |

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/AmishhYadav/Agentic-RAG.git
cd Agentic-RAG
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
```

**Local Testing (no AWS needed):**
```env
LLM_PROVIDER=mock
APP_ENV=development
```

**Production (AWS Bedrock):**
```env
LLM_PROVIDER=bedrock
AWS_REGION=us-east-1
AWS_PROFILE=default
APP_ENV=production
```

### 3. Ingest Documents
```bash
python scripts/ingest.py
```
Place your `.txt` or `.md` files in `data/documents/` before running.

### 4. Launch
```bash
python app_server.py
```
Open **http://localhost:8000** — you'll see the full dashboard.

---

## 🐳 Docker

```bash
# Build
docker build -t agentic-rag .

# Run (mount AWS creds for Bedrock)
docker run -p 8000:8000 --env-file .env -v ~/.aws:/root/.aws agentic-rag
```

---

## 🖥️ UI Overview

The dashboard has three main panels accessible via the sidebar:

| Panel | Description |
|-------|-------------|
| **Chat** | Query interface with suggestion chips, typing indicators, source tags, and verification badges |
| **Documents** | Drag-and-drop file upload to manage the knowledge base |
| **Settings** | Configure LLM provider, AWS region, temperature, and retrieval chunk count (k) |

The **Agent Reasoning** panel on the right shows live, color-coded steps as each agent processes your query.

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | `mock` or `bedrock` | `mock` |
| `AWS_REGION` | AWS region for Bedrock API | `us-east-1` |
| `AWS_PROFILE` | AWS credentials profile | `default` |
| `APP_ENV` | `development` or `production` | `development` |

### Model Tiering (Automatic)

| Agent | Model | Why |
|-------|-------|-----|
| Query Agent | Claude 3.5 Haiku | Routing is a simple classification task |
| Verifier Agent | Claude 3.5 Haiku | Consistency checking doesn't need heavy reasoning |
| Synthesis Agent | Claude 3.7 Sonnet | Answer generation requires deep comprehension |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the dashboard UI |
| `GET` | `/health` | System status and provider info |
| `GET` | `/stream_query?q=...` | SSE stream of agent workflow steps |
| `POST` | `/upload_document` | Upload a file to the knowledge base |
| `GET` | `/documents` | List all documents in the knowledge base |
| `DELETE` | `/documents/{filename}` | Remove a document |

---

## 🗂️ Project Structure

```
agentic-rag/
├── agents/                  # Autonomous agent implementations
│   ├── query_agent.py       #   Query analysis & routing
│   ├── retrieval_agent.py   #   FAISS vector search
│   ├── synthesis_agent.py   #   Answer generation
│   └── verifier_agent.py    #   Answer verification
├── core/                    # Core infrastructure
│   ├── agent_router.py      #   Async orchestrator (tiering + caching + parallelism)
│   ├── cache_manager.py     #   SQLite semantic cache
│   ├── config.py            #   Environment config & model tiers
│   └── llm_interface.py     #   LLM abstraction (Mock + Bedrock)
├── ui/                      # Premium dashboard
│   ├── index.html           #   Layout (sidebar, panels, reasoning)
│   ├── styles.css           #   Dark theme, glassmorphism, animations
│   └── script.js            #   Navigation, streaming, upload, settings
├── data/documents/          # Input documents for RAG
├── embeddings/              # FAISS index storage
├── scripts/                 # Utilities
│   └── ingest.py            #   Document chunking & embedding
├── aws/                     # AWS architecture & IAM policies
├── app_server.py            # FastAPI application (async SSE)
├── Dockerfile               # Container configuration
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## 🔒 Security

- **`.env` is gitignored** — credentials never committed
- **IAM Least Privilege** — use the policy in `aws/iam_policy.json`
- **Docker Isolation** — AWS credentials mounted at runtime, not baked in

---

## 📊 Performance Optimizations

| Optimization | Impact | How It Works |
|-------------|--------|-------------|
| **Model Tiering** | 3-5x faster routing | Haiku for simple tasks, Sonnet only for synthesis |
| **Speculative Retrieval** | ~1-2s saved per query | Query analysis + retrieval run concurrently |
| **Semantic Cache** | Near-instant for repeats | SQLite vector cache bypasses entire pipeline |
| **Async Pipeline** | Non-blocking I/O | All agent calls wrapped in `asyncio` executors |

---

## 📄 License

MIT License — see LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.
