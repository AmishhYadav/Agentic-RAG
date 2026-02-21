import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.agent_router import AgentRouter


def main():
    print("Initializing Agentic RAG System...")
    router = AgentRouter()

    print("\nSystem Ready. Enter a query (or 'exit' to quit).")

    while True:
        try:
            query = input("\n> ")
            if query.lower() in ["exit", "quit", "q"]:
                break

            if not query.strip():
                continue

            # Iterate/consume the generator to get final response
            events = router.process_query(query)
            final_evt = None
            for evt in events:
                print(f"[{evt['step'].upper()}] {evt['message']}")
                if evt["step"] == "complete":
                    final_evt = evt

            response = final_evt["final_response"]

            print("\n=== FINAL RESPONSE ===")
            print(response["answer"])

            if "warning" in response:
                print(f"\n[!] WARNING: {response['warning']}")

            print(f"\n[Verification Logic]: {response['verification']['reasoning']}")
            print("======================\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error during execution: {e}")


if __name__ == "__main__":
    main()
