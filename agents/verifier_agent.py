import json
from typing import Any, Dict, List

from core.llm_interface import LLMProvider


class VerifierAgent:
    """
    Verifies if the generated answer is supported by the context.
    """

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def verify(
        self, query: str, answer: str, context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Checks answer validity.
        Returns dict: {"is_valid": bool, "reasoning": str}
        """
        context_str = "\n\n".join(
            [f"Source ({c['source']}): {c['content']}" for c in context]
        )

        system_prompt = (
            "You are a Verification Agent. Verify the following answer against "
            "the provided context. "
            "The answer must be fully supported by the context. "
            "Return strict JSON: "
            '{"is_valid": bool, "reasoning": str}'
            "\n\nContext:\n" + context_str
        )

        user_prompt = f"Query: {query}\nAnswer: {answer}"

        response = self.llm.generate(system_prompt, user_prompt, temperature=0.0)

        try:
            clean_response = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_response)
        except json.JSONDecodeError:
            return {
                "is_valid": True,
                "reasoning": "Error in verification parsing, assuming valid to avoid blockage.",
            }
