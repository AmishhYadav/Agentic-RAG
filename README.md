# Agentic RAG System

A modular, production-grade Agentic Retrieval-Augmented Generation (RAG) system designed for AWS. It features autonomous agents for query analysis, retrieval, synthesis, and verification.

## Architecturally Significant Features (Agentic)

Unlike a standard RAG pipeline (`retrieve -> generate`), this system is **agentic**:
1.  **Conditional Retrieval**: The `QueryAgent` decides *if* retrieval is actually necessary.
2.  **Autonomous Verification**: The `VerifierAgent` critiques the output. If the answer isn't supported by evidence, it is flagged (and can be rejected).
3.  **Modular Responsibility**: specialized classes (`QueryAgent`, `RetrievalAgent`, `SynthesisAgent`) interact via a central Router.

## Architecture

This system is built to run locally (dev) or on AWS (prod).

### Local Stack (Free Tier / Dev)
-   **LLM**: `MockLLM` (Local Rule-Based) or `BedrockLLM` (Amazon Bedrock).
-   **Vector Store**: FAISS (running on CPU).
-   **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (Local CPU).

### AWS Production Stack
-   **LLM**: Amazon Bedrock (Claude 3 Sonnet / Haiku).
-   **Storage**: Amazon S3 (Documents & Index).
-   **Compute**: AWS Fargate or Lambda.

## Setup & Running Locally

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Setup**:
    ```bash
    cp .env.example .env
    # Edit .env to set LLM_PROVIDER=mock (default) or LLM_PROVIDER=bedrock
    ```

3.  **Ingest Documents**:
    Create embeddings from files in `data/documents/`:
    ```bash
    python scripts/ingest.py
    ```

4.  **Run the Agentic App**:
    ```bash
    python scripts/run_app.py
    ```

## Usage Example

**Query**: "Is retrieval needed for complex questions?"
-   **Query Agent**: Decides `needs_retrieval=True`.
-   **Retrieval Agent**: Fetches docs about RAG.
-   **Synthesis Agent**: Generates answer using context.
-   **Verifier Agent**: Confirms validity.

**Query**: "Hello there"
-   **Query Agent**: Decides `needs_retrieval=False`.
-   **Router**: Skips retrieval.
-   **Synthesis Agent**: Generates a greeting.
