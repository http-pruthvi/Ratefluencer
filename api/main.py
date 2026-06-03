import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api.database import init_db
from api.routes import influencer, trends, content
from api.schemas import BaseResponse

# Config logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ratefluencer.api_root")

# Initialize database tables
try:
    logger.info("Initializing database schemas...")
    init_db()
except Exception as e:
    logger.error(f"Error initializing database: {e}")

# Instantiate FastAPI
app = FastAPI(
    title="Ratefluencer AI Platform Backend",
    description="REST API powering Influencer Intelligence Scoring & LangGraph Viral Reels Agent.",
    version="1.0.0"
)

# CORS Policy configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(influencer.router)
app.include_router(trends.router)
app.include_router(content.router)

@app.get("/")
def root_handler(request: Request):
    """Serve index.html for browsers, and health check JSON for API requests/tests."""
    accept = request.headers.get("accept", "")
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "public"))
    if "text/html" in accept:
        html_path = os.path.join(static_dir, "index.html")
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read(), status_code=200)
    
    # Fallback to the JSON health check so the test suite passes
    return {
        "success": True,
        "data": {
            "status": "Online",
            "service": "Ratefluencer Core API Engine",
            "version": "1.0.0",
            "environment": os.getenv("DATABASE_URL", "sqlite")
        }
    }

# Mount static files (HTML, CSS, JS) so they are served directly from the root in local dev.
# Skip this on Vercel to avoid "directory not found" lambda startup errors (handled by vercel.json routes instead).
if os.getenv("VERCEL") != "1":
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "public"))
    if os.path.exists(static_dir):
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="public")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting uvicorn server locally on port 8000...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
