import json
from typing import Dict, Any
from core.llm_interface import LLMProvider

class QueryAgent:
    """
    Analyzes the user query to determine intent and retrieval strategy.
    """
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def analyze(self, query: str) -> Dict[str, Any]:
        """
        Decides if retrieval is necessary.
        Returns a dict: {"needs_retrieval": bool, "retrieval_strategy": str, "reasoning": str}
        """
        system_prompt = (
            "You are a Query Analysis Agent. Your goal is to analyze the following user query "
            "and decide if information retrieval from the knowledge base is needed to answer it. "
            "The knowledge base contains information about Amazon Bedrock, AWS IAM, and RAG architectures. "
            "Return your decision in strict JSON format: "
            '{"needs_retrieval": bool, "retrieval_strategy": "vector_similarity" | null, "reasoning": str}'
        )
        
        response = self.llm.generate(system_prompt, query, temperature=0.0)
        
        try:
            # Clean up potential markdown code blocks if the LLM adds them
            clean_response = response.replace("```json", "").replace("```", "").strip()
            decision = json.loads(clean_response)
            return decision
        except json.JSONDecodeError:
            # Fallback for parsing errors
            return {
                "needs_retrieval": True,
                "retrieval_strategy": "vector_similarity",
                "reasoning": "Error parsing LLM response, defaulting to retrieval."
            }
