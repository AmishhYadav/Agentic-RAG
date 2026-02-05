# Agentic RAG System

A production-ready, modular Retrieval-Augmented Generation (RAG) system with autonomous agents for intelligent query processing, retrieval, synthesis, and verification.

## 🌟 Key Features

- **Agentic Architecture**: Autonomous agents make intelligent decisions about when and how to retrieve information
- **Conditional Retrieval**: Smart query analysis determines if retrieval is necessary
- **Multi-Agent Workflow**: Specialized agents for query analysis, retrieval, synthesis, and verification
- **AWS Integration**: Production-ready deployment with Amazon Bedrock and S3
- **Flexible LLM Providers**: Switch between Mock LLM (local testing) and AWS Bedrock (production)
- **Web Interface**: Real-time streaming UI showing agent reasoning steps

## 🏗️ Architecture

Unlike traditional RAG pipelines (`retrieve → generate`), this system uses **autonomous agents**:

1. **Query Agent**: Analyzes user intent and decides if retrieval is needed
2. **Retrieval Agent**: Fetches relevant context using FAISS vector similarity
3. **Synthesis Agent**: Generates responses using retrieved context
4. **Verifier Agent**: Validates response quality and factual accuracy

## 🛠️ Tech Stack

### Core
- **Python 3.9+**
- **FastAPI**: Web framework for API and UI
- **Uvicorn**: ASGI server

### LLM & AI
- **Amazon Bedrock**: Claude 3.7 Sonnet (production)
- **Boto3**: AWS SDK for Python
- **Mock LLM**: Rule-based local testing

### Vector Store & Embeddings
- **FAISS**: CPU-based vector similarity search
- **Sentence Transformers**: `all-MiniLM-L6-v2` for embeddings
- **PyTorch**: ML framework (CPU-only)

### Infrastructure
- **Docker**: Containerization
- **AWS S3**: Document storage (production)
- **AWS IAM**: Access control

## 📋 Prerequisites

- Python 3.9 or higher
- AWS Account (for Bedrock usage)
- Docker (optional, for containerized deployment)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/AmishhYadav/Agentic-RAG.git
cd Agentic-RAG
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` to configure your LLM provider:

**For Local Testing (No AWS Required):**
```env
LLM_PROVIDER=mock
APP_ENV=development
```

**For AWS Bedrock (Production):**
```env
LLM_PROVIDER=bedrock
AWS_REGION=us-east-1
AWS_PROFILE=default
APP_ENV=production
```

### 4. AWS Setup (If Using Bedrock)

#### Configure AWS CLI
```bash
aws configure
```
Enter your AWS Access Key, Secret Key, and region (`us-east-1`).

#### Request Model Access
1. Log in to AWS Console
2. Navigate to **Bedrock → Model Access**
3. Request access to **Claude 3.7 Sonnet**
4. Update your IAM policy using `aws/iam_policy.json`

See [`aws/architecture.md`](aws/architecture.md) for detailed AWS setup instructions.

### 5. Ingest Documents
```bash
python scripts/ingest.py
```
This creates embeddings from files in `data/documents/`.

### 6. Run the Application
```bash
python app_server.py
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

## 🐳 Docker Deployment

### Build the Image
```bash
docker build -t agentic-rag .
```

### Run the Container
```bash
docker run -p 8000:8000 --env-file .env -v ~/.aws:/root/.aws agentic-rag
```

**Note**: The `-v ~/.aws:/root/.aws` flag mounts your AWS credentials into the container (required for Bedrock).

## 🔧 Configuration Options

### LLM Provider

| Provider | Use Case | Configuration |
|----------|----------|---------------|
| `mock` | Local testing, no AWS costs | `LLM_PROVIDER=mock` |
| `bedrock` | Production with Claude 3.7 | `LLM_PROVIDER=bedrock` + AWS credentials |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM backend (`mock` or `bedrock`) | `mock` |
| `AWS_REGION` | AWS region for Bedrock | `us-east-1` |
| `AWS_PROFILE` | AWS credentials profile | `default` |
| `APP_ENV` | Environment (`development` or `production`) | `development` |
| `VECTOR_STORE_PATH` | Path to FAISS index | `embeddings/faiss_index` |

## 📚 Usage Examples

### Query Requiring Retrieval
**Input**: "What is Amazon Bedrock?"
- **Query Agent**: Decides `needs_retrieval=True`
- **Retrieval Agent**: Fetches relevant documents
- **Synthesis Agent**: Generates answer using context
- **Verifier Agent**: Validates response accuracy

### Simple Conversational Query
**Input**: "Hello!"
- **Query Agent**: Decides `needs_retrieval=False`
- **Synthesis Agent**: Generates greeting directly
- Retrieval is skipped for efficiency

## 🗂️ Project Structure

```
agentic-rag/
├── agents/              # Autonomous agent implementations
├── aws/                 # AWS architecture docs and IAM policies
├── core/                # Core logic (config, LLM interface, router)
├── data/documents/      # Input documents for ingestion
├── embeddings/          # FAISS index storage
├── scripts/             # Utility scripts (ingest, run)
├── ui/                  # Web interface (HTML/CSS/JS)
├── app_server.py        # FastAPI application
├── Dockerfile           # Container configuration
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## 🔒 Security

- **`.env` is gitignored**: Your AWS credentials are never committed
- **IAM Least Privilege**: Use the policy in `aws/iam_policy.json`
- **Docker Isolation**: Credentials are mounted at runtime, not baked into images

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 📧 Contact

For questions or support, please open an issue on GitHub.
