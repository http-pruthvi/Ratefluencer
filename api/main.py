import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/", response_model=BaseResponse)
def root_health_check():
    """Simple API health check endpoint."""
    return BaseResponse(
        success=True,
        data={
            "status": "Online",
            "service": "Ratefluencer Core API Engine",
            "version": "1.0.0",
            "environment": os.getenv("DATABASE_URL", "sqlite")
        }
    )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting uvicorn server locally on port 8000...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
