from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# --- Shared Models ---
class BaseResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

# --- Track 1: Influencer Intelligence Schemas ---
class InfluencerProfile(BaseModel):
    username: str
    platform: str
    followers: int
    following: int
    posts_count: int
    engagement_rate: float
    avg_likes: float
    avg_comments: float
    avg_shares: float
    avg_saves: float
    posting_frequency: float
    audience_age_18_24_pct: float
    audience_india_pct: float
    content_category: str
    bio: Optional[str] = None

class InfluencerScorecard(BaseModel):
    profile: InfluencerProfile
    authenticity_score: float = Field(..., description="Authenticity rating from 0-100")
    growth_score: float = Field(..., description="Growth rating from 0-100")
    ratefluencer_score: float = Field(..., description="Proprietary XGBoost success rating from 0-100")
    growth_rate_30d_pct: float
    historical_history: List[int]
    predicted_history: List[int]

class BrandMatchItem(BaseModel):
    brand_id: int
    name: str
    industry: str
    aesthetic: str
    description: str
    match_score: float

class BrandBriefRequest(BaseModel):
    brief: str = Field(..., description="Text details of the marketing campaign brief")

class CreatorMatchItem(BaseModel):
    username: str
    platform: str
    followers: int
    content_category: str
    bio: Optional[str] = None
    match_score: float

# --- Track 2: Viral Reel Creator Agent Schemas ---
class TrendItem(BaseModel):
    title: str
    topic: str
    source: str
    url: str
    trend_score: float

class TrendScoreRequest(BaseModel):
    topic: str

class ScriptRequest(BaseModel):
    topic: str
    category: str = "tech"

class ContentScript(BaseModel):
    topic: str
    category: str
    script: str

class PostRequest(BaseModel):
    topic: str
    script: str
    category: str = "tech"

class GeneratedPosts(BaseModel):
    linkedin_post: str
    instagram_caption: str
    hashtags: List[str]

class ViralityRequest(BaseModel):
    script: str
    trend_score: float
    category: str = "tech"
    hashtags: List[str] = []

class ViralityPrediction(BaseModel):
    virality_score: float
    expected_views: int
    expected_likes: int
    expected_shares: int
    insights: List[str]
