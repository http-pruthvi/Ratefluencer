import os
from fastapi import APIRouter
from typing import List, Dict, Any

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from api.schemas import (
    BaseResponse, ScriptRequest, ContentScript, PostRequest, 
    GeneratedPosts, ViralityRequest, ViralityPrediction
)
from models.track2.content_generator import ContentGenerator
from models.track2.virality_predictor import ViralityPredictor
from agent.graph import run_agent_pipeline

router = APIRouter(prefix="/api/content", tags=["AI Viral Content Agent"])

# Instantiate engines
content_generator = ContentGenerator()
virality_predictor = ViralityPredictor()

@router.post("/generate-script", response_model=BaseResponse)
def api_generate_script(payload: ScriptRequest):
    """Generates a vertical video script optimized for millennial and Gen Z attention."""
    try:
        script = content_generator.generate_script(payload.topic, payload.category)
        return BaseResponse(
            success=True, 
            data={"topic": payload.topic, "category": payload.category, "script": script}
        )
    except Exception as e:
        return BaseResponse(success=False, error=str(e))

@router.post("/generate-caption", response_model=BaseResponse)
def api_generate_captions(payload: PostRequest):
    """Generates LinkedIn professional post and Instagram aesthetic caption with trending tags."""
    try:
        posts = content_generator.generate_posts(payload.topic, payload.script, payload.category)
        return BaseResponse(success=True, data=posts)
    except Exception as e:
        return BaseResponse(success=False, error=str(e))

@router.post("/predict-virality", response_model=BaseResponse)
def api_predict_virality(payload: ViralityRequest):
    """Feeds script characteristics to RandomForest ML to predict virality score, views, likes, shares."""
    try:
        preds = virality_predictor.predict(
            script_text=payload.script,
            trend_score=payload.trend_score,
            category=payload.category,
            hashtags=payload.hashtags
        )
        return BaseResponse(success=True, data=preds)
    except Exception as e:
        return BaseResponse(success=False, error=str(e))

@router.post("/agent-pipeline", response_model=BaseResponse)
def run_autonomous_agent(payload: ScriptRequest):
    """Triggers the compiled LangGraph Agent StateGraph (trend -> script -> caption -> virality) to generate all campaign assets in sequence."""
    try:
        # We trigger the agent graph with a custom topic and category
        # If trend_score is not specified, we supply a premium default
        result = run_agent_pipeline(
            custom_topic=payload.topic,
            category=payload.category,
            custom_trend_score=85.0
        )
        
        if result.get("error"):
            return BaseResponse(success=False, error=result["error"])
            
        return BaseResponse(success=True, data=result)
    except Exception as e:
        return BaseResponse(success=False, error=str(e))
