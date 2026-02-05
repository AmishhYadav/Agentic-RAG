import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
from pathlib import Path
from core.agent_router import AgentRouter

app = FastAPI()

# Mount static files for UI
BASE_DIR = Path(__file__).parent
app.mount("/ui", StaticFiles(directory=BASE_DIR / "ui"), name="ui")

router = AgentRouter()

@app.get("/")
async def get_index():
    index_path = BASE_DIR / "ui" / "index.html"
    return HTMLResponse(index_path.read_text())

@app.get("/stream_query")
async def stream_query(q: str):
    """
    SSE Endpoint that streams the agent workflow steps to the UI.
    """
    async def event_generator():
        try:
            # Run the synchronous generator in a thread pool to avoid blocking async loop
            # We iterate over the generator and yield SSE formatted events
            for event in router.process_query(q):
                yield json.dumps(event)
                await asyncio.sleep(0.1) # small throttle for visual effect
        except Exception as e:
            yield json.dumps({"step": "error", "message": str(e)})

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    print("Starting Agentic RAG Web Interface on http://localhost:8000")
    uvicorn.run("app_server:app", host="0.0.0.0", port=8000, reload=True)
