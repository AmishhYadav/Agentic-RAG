# Agentic RAG AWS Architecture

This document describes the high-level architecture for deploying the Agentic RAG system on AWS.

## Core Components

1.  **Amazon S3 (Simple Storage Service)**
    -   **Purpose**: Stores the raw documents (PDF, TXT) and the serialized FAISS index.
    -   **Lifecycle**:
        -   Users upload documents to an S3 bucket (`input/`).
        -   The ingestion script (running on EC2 or Lambda) reads from S3, processes text, updates the FAISS index, and saves it back to S3 (`index/`).

2.  **Amazon Bedrock**
    -   **Purpose**: Provides serverless access to foundation models (Anthropic Claude 3).
    -   **Usage**: The `BedrockLLM` class in `core/llm_interface.py` interacts with the Bedrock Runtime API.
    -   **Benefits**: No infrastructure management for LLMs, pay-per-token pricing, and compliance/security features.

3.  **Compute Layer (EC2 / Fargate / Lambda)**
    -   **Development**: Local machine (current state).
    -   **Production**:
        -   The agent orchestration (Python code) can run on AWS Lambda (for event-driven flows) or AWS Fargate (for long-running services).
        -   Given `faiss-cpu` dependencies, a containerized approach (ECS/Fargate) is recommended over Lambda to avoid size limit issues with the vector library.

4.  **IAM (Identity and Access Management)**
    -   Strict least-privilege policies.
    -   The application role needs:
        -   `s3:GetObject` on the document bucket.
        -   `bedrock:InvokeModel` on the specific foundation model ARN.

## Data Flow (Production)

1.  **User Query** -> API Gateway -> Lambda/Fargate (Agent Router).
2.  **Query Agent** analyzes intent (using Bedrock).
3.  **Retrieval Agent**:
    -   Loads FAISS index from S3 (cached in memory if possible).
    -   Embeds query (locally via `sentence-transformers` or via Bedrock Titan Embeddings).
    -   Retrieves top-k context.
4.  **Synthesis Agent** generates response (using Bedrock).
5.  **Verifier Agent** validates response (using Bedrock).
6.  **Response** -> User.

## Cost Considerations

-   **Bedrock**: Pay per input/output token. Using Claude 3 Sonnet is a good balance of cost/intelligence. For simpler agents (Router), Claude 3 Haiku is faster and cheaper.
-   **S3**: Standard storage costs (cheap for text).
-   **Compute**: Fargate Spot instances can reduce runtime costs significantly.
