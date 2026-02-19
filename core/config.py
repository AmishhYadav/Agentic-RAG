import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).parent.parent.absolute()
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "documents"
EMBEDDINGS_DIR = BASE_DIR / "embeddings"
FAISS_INDEX_PATH = EMBEDDINGS_DIR / "faiss_index"

# App Configuration
APP_ENV = os.getenv("APP_ENV", "development")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_PROFILE = os.getenv("AWS_PROFILE", "default")

# Model Configuration
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
BEDROCK_MODEL_ID_SMART = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"   # Synthesis (accurate)
BEDROCK_MODEL_ID_FAST  = "us.anthropic.claude-3-5-haiku-20241022-v1:0"    # Router & Verifier (fast)

def get_llm_config(tier: str = "smart"):
    """Return LLM config. tier='smart' for Sonnet, tier='fast' for Haiku."""
    model_id = BEDROCK_MODEL_ID_FAST if tier == "fast" else BEDROCK_MODEL_ID_SMART
    return {
        "provider": LLM_PROVIDER,
        "region": AWS_REGION,
        "model_id": model_id,
        "tier": tier
    }

def print_config():
    print(f"--- Configuration ---")
    print(f"Environment: {APP_ENV}")
    print(f"LLM Provider: {LLM_PROVIDER}")
    print(f"Base Dir: {BASE_DIR}")
    print(f"---------------------")
