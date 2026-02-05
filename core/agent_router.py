from typing import Dict, Any
from core.config import get_llm_config
from core.llm_interface import get_llm
from agents.query_agent import QueryAgent
from agents.retrieval_agent import RetrievalAgent
from agents.synthesis_agent import SynthesisAgent
from agents.verifier_agent import VerifierAgent

class AgentRouter:
    """
    Orchestrates the agentic workflow:
    Query -> [Analysis] -> [Retrieval (Optional)] -> Synthesis -> Verification -> Answer
    """
    def __init__(self):
        self.config = get_llm_config()
        self.llm = get_llm(self.config)
        
        # Initialize Agents
        self.query_agent = QueryAgent(self.llm)
        self.retrieval_agent = RetrievalAgent()
        self.synthesis_agent = SynthesisAgent(self.llm)
        self.verifier_agent = VerifierAgent(self.llm)

    def process_query(self, query: str):
        """
        Main execution loop. Yields events for real-time UI updates.
        """
        yield {"step": "start", "message": f"Processing query: {query}"}
        
        # Step 1: Query Analysis
        yield {"step": "router", "message": "Delegating to Query Analysis Agent..."}
        analysis = self.query_agent.analyze(query)
        yield {"step": "query_agent", "message": f"Analysis Complete.", "data": analysis}
        
        context = []
        if analysis.get("needs_retrieval", False):
            # Step 2: Retrieval
            yield {"step": "router", "message": "Retrieval required. Delegating to Retrieval Agent..."}
            context = self.retrieval_agent.retrieve(query)
            yield {"step": "retrieval_agent", "message": f"Retrieved {len(context)} chunks.", "data": context}
        else:
            yield {"step": "router", "message": "No retrieval needed. Proceeding to synthesis."}

        # Step 3: Synthesis
        yield {"step": "router", "message": "Delegating to Synthesis Agent..."}
        answer = self.synthesis_agent.synthesize(query, context)
        yield {"step": "synthesis_agent", "message": "Answer generated.", "data": {"answer": answer}}

        # Step 4: Verification
        yield {"step": "router", "message": "Delegating to Verifier Agent..."}
        verification = self.verifier_agent.verify(query, answer, context)
        yield {"step": "verifier_agent", "message": "Verification complete.", "data": verification}

        # Final Decision
        final_response = {
            "query": query,
            "answer": answer,
            "context_used": context,
            "verification": verification
        }

        if not verification.get("is_valid", False):
            final_response["warning"] = "The generated answer could not be verified against the provided context."
        
        yield {"step": "complete", "message": "Workflow finished", "final_response": final_response}
        return final_response
