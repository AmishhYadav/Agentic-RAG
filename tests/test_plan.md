# Agentic RAG Manual Test Plan

Run these queries in the `python scripts/run_app.py` CLI to verify the different agent behaviors.

## Test Case 1: Retrieval Triggered (Happy Path)
**Goal**: Verify the `QueryAgent` detects intent and `RetrievalAgent` finds relevant docs.
**Input**:
> "What is Amazon Bedrock and does it support Claude?"
**Expected Output**:
- `[Query Agent]`: returns `needs_retrieval: True`.
- `[Retrieval Agent]`: returns chunks from `amazon_bedrock.txt`.
- `[Synthesis Agent]`: Mentions Bedrock is a managed service and supports Claude 3.
- `[Verifier Agent]`: Result `is_valid: True`.

## Test Case 2: Retrieval Triggered (Security Topic)
**Goal**: Verify retrieval works for different topics in the corpus.
**Input**:
> "Explain the concept of least privilege in AWS."
**Expected Output**:
- `[Retrieval Agent]`: returns chunks from `cloud_security.txt`.
- `[Synthesis Agent]`: Explains granting minimum necessary permissions.

## Test Case 3: No Retrieval Needed (Chitchat)
**Goal**: Verify `QueryAgent` correctly skips retrieval for general inputs.
**Input**:
> "Hello, who are you?"
**Expected Output**:
- `[Query Agent]`: returns `needs_retrieval: False`.
- `[Retrieval Agent]`: **Skipped**.
- `[Synthesis Agent]`: Generates a generic response.

## Test Case 4: No Retrieval Needed (General Knowledge)
**Goal**: Verify exclusion of external knowledge (Mock LLM limitation).
**Input**:
> "What is the capital of France?"
**Expected Output**:
- `[Query Agent]`: returns `needs_retrieval: False` (or True but finds nothing).
- `[Synthesis Agent]`: Might answer generally, but system emphasizes context keying.

## Test Case 5: Missing Information (Edge Case)
**Goal**: Verify the system handles queries about missing topics.
**Input**:
> "How do I cook pasta?"
**Expected Output**:
- `[Query Agent]`: might guess `needs_retrieval: True` (if keywords match) or `False`.
- `[Retrieval Agent]`: If run, should return low relevance/random chunks.
- `[Synthesis Agent]`: Should ideally say "I cannot answer this based on the provided context" (depending on LLM strictness).
