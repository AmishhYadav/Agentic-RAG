from typing import Dict, Any
import asyncio
import numpy as np
from core.config import get_llm_config
from core.llm_interface import get_llm
from core.cache_manager import SemanticCache
from agents.query_agent import QueryAgent
from agents.retrieval_agent import RetrievalAgent
from agents.synthesis_agent import SynthesisAgent
from agents.verifier_agent import VerifierAgent

class AgentRouter:
    """
    Orchestrates the agentic workflow with:
    - Tiered Intelligence: Haiku (fast) for routing/verification, Sonnet (smart) for synthesis
    - Speculative Retrieval: Query Analysis + Retrieval run in parallel
    - Semantic Caching: Skip the entire pipeline for near-duplicate queries
    """
    def __init__(self):
        # Tiered LLM instances
        fast_config  = get_llm_config(tier="fast")
        smart_config = get_llm_config(tier="smart")
        llm_fast  = get_llm(fast_config)
        llm_smart = get_llm(smart_config)
        
        # Initialize Agents with appropriate model tier
        self.query_agent     = QueryAgent(llm_fast)       # Fast: routing decision
        self.retrieval_agent = RetrievalAgent()            # No LLM needed
        self.synthesis_agent = SynthesisAgent(llm_smart)   # Smart: answer generation
        self.verifier_agent  = VerifierAgent(llm_fast)     # Fast: consistency check
        
        # Semantic Cache (reuses retrieval agent's embedding model)
        self.cache = SemanticCache()

    def _encode_query(self, query: str) -> np.ndarray:
        """Vectorize query using the retrieval agent's embedding model."""
        return self.retrieval_agent.model.encode([query])[0]

    async def process_query(self, query: str):
        """
        Async execution loop with semantic caching and speculative retrieval.
        Yields events for real-time UI updates via SSE.
        """
        yield {"step": "start", "message": f"Processing query: {query}"}
        
        # ── Step 0: Check Semantic Cache ──
        loop = asyncio.get_event_loop()
        query_vector = await loop.run_in_executor(None, self._encode_query, query)
        cache_hit = self.cache.lookup(query_vector)
        
        if cache_hit:
            yield {"step": "router", "message": f"⚡ Cache hit! (similarity: {cache_hit['similarity']})"}
            final_response = {
                "query": query,
                "answer": cache_hit["answer"],
                "context_used": cache_hit.get("sources", []),
                "verification": cache_hit.get("verification", {"is_valid": True, "reasoning": "Cached result"}),
                "cached": True
            }
            yield {"step": "complete", "message": "Returned cached answer", "final_response": final_response}
            return

        yield {"step": "router", "message": "Cache miss. Running full agent pipeline..."}

        # ── Step 1: Speculative Parallel Execution ──
        yield {"step": "router", "message": "⚡ Running Query Analysis + Speculative Retrieval in parallel..."}

        analysis_future   = loop.run_in_executor(None, self.query_agent.analyze, query)
        retrieval_future  = loop.run_in_executor(None, self.retrieval_agent.retrieve, query)
        
        analysis, speculative_context = await asyncio.gather(analysis_future, retrieval_future)

        yield {"step": "query_agent", "message": "Analysis Complete.", "data": analysis}

        # ── Step 2: Decide whether to keep speculative retrieval ──
        context = []
        if analysis.get("needs_retrieval", False):
            context = speculative_context
            yield {"step": "retrieval_agent", "message": f"Retrieved {len(context)} chunks (speculative hit ✅).", "data": context}
        else:
            yield {"step": "router", "message": "No retrieval needed. Speculative results discarded."}

        # ── Step 3: Synthesis (Smart model) ──
        yield {"step": "router", "message": "Delegating to Synthesis Agent (Smart model)..."}
        answer = await loop.run_in_executor(None, self.synthesis_agent.synthesize, query, context)
        yield {"step": "synthesis_agent", "message": "Answer generated.", "data": {"answer": answer}}

        # ── Step 4: Verification (Fast model) ──
        yield {"step": "router", "message": "Delegating to Verifier Agent (Fast model)..."}
        verification = await loop.run_in_executor(None, self.verifier_agent.verify, query, answer, context)
        yield {"step": "verifier_agent", "message": "Verification complete.", "data": verification}

        # ── Store in Cache ──
        sources = [chunk.get("source", "") for chunk in context] if context else []
        self.cache.store(query, query_vector, answer, sources, verification)

        # ── Final Decision ──
        final_response = {
            "query": query,
            "answer": answer,
            "context_used": context,
            "verification": verification
        }

        if not verification.get("is_valid", False):
            final_response["warning"] = "The generated answer could not be verified against the provided context."
        
        yield {"step": "complete", "message": "Workflow finished", "final_response": final_response}
