
import unittest
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.agent_router import AgentRouter

class TestAgentFlow(unittest.TestCase):
    def setUp(self):
        self.router = AgentRouter()
        # Ensure we are in mock mode for consistent testing
        if self.router.config["provider"] != "mock":
            print(f"WARNING: Running tests with provider {self.router.config['provider']}. Mock is recommended.")

    def run_query(self, query):
        """Helper to run query and collect events"""
        events = []
        final_response = None
        for event in self.router.process_query(query):
            events.append(event)
            if event["step"] == "complete":
                final_response = event["final_response"]
        return events, final_response

    def test_retrieval_triggered(self):
        """Test Case 1: Retrieval Triggered (Happy Path)"""
        print("\nRunning Test Case 1: Retrieval Triggered")
        query = "What is Amazon Bedrock and does it support Claude?"
        events, response = self.run_query(query)
        
        # Verify steps
        steps = [e["step"] for e in events]
        self.assertIn("query_agent", steps)
        self.assertIn("retrieval_agent", steps, "Retrieval should be triggered")
        self.assertIn("synthesis_agent", steps)
        self.assertIn("verifier_agent", steps)
        
        # Verify Context
        self.assertTrue(len(response["context_used"]) > 0, "Should have retrieved context")
        
    def test_no_retrieval_needed(self):
        """Test Case 3: No Retrieval Needed (Chitchat)"""
        print("\nRunning Test Case 3: No Retrieval Needed")
        query = "Hello, who are you?"
        events, response = self.run_query(query)
        
        steps = [e["step"] for e in events]
        self.assertIn("query_agent", steps)
        self.assertNotIn("retrieval_agent", steps, "Retrieval should be skipped for chitchat")
        self.assertIn("synthesis_agent", steps)

    def test_general_knowledge(self):
        """Test Case 4: General Knowledge (Mock Limitation)"""
        print("\nRunning Test Case 4: General Knowledge")
        query = "What is the capital of France?"
        events, response = self.run_query(query)
        
        # In mock mode, this might just skip retrieval or return generic
        # We mostly check that it runs through without error
        self.assertIsNotNone(response)

if __name__ == "__main__":
    unittest.main()
