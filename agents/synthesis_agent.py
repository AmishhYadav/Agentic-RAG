from typing import Any, Dict, List

from core.llm_interface import LLMProvider


class SynthesisAgent:
    """
    Synthesizes a final answer given the user query and retrieved context.
    """

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def synthesize(self, query: str, context: List[Dict[str, Any]]) -> str:
        """
        Generates the answer.
        """
        context_str = "\n\n".join(
            [f"Source ({c['source']}): {c['content']}" for c in context]
        )

        system_prompt = (
            "You are a Synthesis Agent. Your task is to synthesize an answer to the user's query "
            "based STRICTLY on the provided retrieved context. "
            "Do not use outside knowledge. If the context is insufficient, state that clearly."
            "\n\nRetrieved Context:\n" + context_str
        )

        response = self.llm.generate(system_prompt, query, temperature=0.1)
        return response
