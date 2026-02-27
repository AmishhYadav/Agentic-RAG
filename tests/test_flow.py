import sys
import unittest
from pathlib import Path
from unittest import IsolatedAsyncioTestCase

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.agent_router import AgentRouter  # noqa: E402
from core.config import LLM_PROVIDER  # noqa: E402


class TestAgentFlow(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.router = AgentRouter()
        # Clear semantic cache to ensure isolated test runs
        self.router.cache.clear()

        # Ensure we are in mock mode for consistent testing
        if LLM_PROVIDER != "mock":
            print(f"WARNING: Running tests with provider {LLM_PROVIDER}. " f"Mock is recommended.")

    async def run_query(self, query):
        """Helper to run query and collect events"""
        events = []
        final_response = None
        async for event in self.router.process_query(query):
            events.append(event)
            if event["step"] == "complete":
                final_response = event["final_response"]
        return events, final_response

    async def test_retrieval_triggered(self):
        """Test Case 1: Retrieval Triggered (Happy Path)"""
        print("\nRunning Test Case 1: Retrieval Triggered")
        query = "What is Amazon Bedrock and does it support Claude?"
        events, response = await self.run_query(query)

        # Verify steps
        steps = [e["step"] for e in events]
        self.assertIn("query_agent", steps)
        self.assertIn("retrieval_agent", steps, "Retrieval should be triggered")
        self.assertIn("synthesis_agent", steps)
        self.assertIn("verifier_agent", steps)

        # Verify Context
        self.assertTrue(len(response["context_used"]) > 0, "Should have retrieved context")

    async def test_no_retrieval_needed(self):
        """Test Case 3: No Retrieval Needed (Chitchat)"""
        print("\nRunning Test Case 3: No Retrieval Needed")
        query = "Hello, who are you?"
        events, response = await self.run_query(query)

        steps = [e["step"] for e in events]
        self.assertIn("query_agent", steps)
        self.assertNotIn("retrieval_agent", steps, "Retrieval should be skipped for chitchat")
        self.assertIn("synthesis_agent", steps)

    async def test_general_knowledge(self):
        """Test Case 4: General Knowledge (Mock Limitation)"""
        print("\nRunning Test Case 4: General Knowledge")
        query = "What is the capital of France?"
        events, response = await self.run_query(query)

        # In mock mode, this might just skip retrieval or return generic
        # We mostly check that it runs through without error
        self.assertIsNotNone(response)


if __name__ == "__main__":
    unittest.main()
