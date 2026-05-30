import os
from fastapi import APIRouter
from typing import List, Dict, Any

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from api.schemas import BaseResponse, TrendItem, TrendScoreRequest
from ingestion.reddit_collector import RedditCollector
from ingestion.youtube_collector import YouTubeCollector
from ingestion.news_rss_collector import RSSCollector
from models.track2.trend_ranker import TrendRanker

router = APIRouter(prefix="/api/trends", tags=["Trend Intelligence"])

# Load collectors and ranker
reddit_collector = RedditCollector()
youtube_collector = YouTubeCollector()
rss_collector = RSSCollector()
trend_ranker = TrendRanker()

@router.get("", response_model=BaseResponse)
def get_trending_topics(limit: int = 10):
    """Grapeshot collection from Reddit, YouTube and Tech RSS, consolidates, ranks and returns top trends."""
    try:
        reddit_trends = reddit_collector.fetch_trends(limit=5)
        youtube_trends = youtube_collector.fetch_trends(max_results=5)
        rss_trends = rss_collector.fetch_trends(limit=5)
        
        all_trends = reddit_trends + youtube_trends + rss_trends
        ranked = trend_ranker.rank_trends(all_trends, limit=limit)
        
        return BaseResponse(success=True, data=ranked)
    except Exception as e:
        return BaseResponse(success=False, error=str(e))

@router.post("/score", response_model=BaseResponse)
def score_custom_trend(payload: TrendScoreRequest):
    """Allows testing/scoring an arbitrary trending phrase using TrendRanker models."""
    try:
        # Construct simulated item to rank
        mock_item = {
            "title": payload.topic,
            "score": 1200, # default average
            "num_comments": 250,
            "source": "Reddit",
            "category": "Technology"
        }
        scored = trend_ranker.score_item(mock_item)
        return BaseResponse(success=True, data=scored)
    except Exception as e:
        return BaseResponse(success=False, error=str(e))
