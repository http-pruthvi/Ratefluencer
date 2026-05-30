import os
import logging
import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("ratefluencer.youtube")

class YouTubeCollector:
    """Collects trending technology and programming videos using YouTube Data API v3."""
    
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        self.youtube_active = False
        
        if self.api_key:
            try:
                from googleapiclient.discovery import build
                self.youtube = build("youtube", "v3", developerKey=self.api_key)
                self.youtube_active = True
                logger.info("YouTube Data API v3 client initialized successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize YouTube API client: {e}. Switching to mock simulator.")
        else:
            logger.info("YouTube API key missing. YouTube collector running in mock simulator mode.")

    def fetch_trends(self, region_code: str = "US", max_results: int = 10) -> List[Dict[str, Any]]:
        """Fetches trending videos in the Technology category (category ID 28)."""
        if self.youtube_active:
            try:
                # Video Category ID 28 is standard for 'Science & Technology'
                request = self.youtube.videos().list(
                    part="snippet,statistics",
                    chart="mostPopular",
                    regionCode=region_code,
                    videoCategoryId="28",
                    maxResults=max_results
                )
                response = request.execute()
                
                trends = []
                for item in response.get("items", []):
                    snippet = item.get("snippet", {})
                    stats = item.get("statistics", {})
                    
                    trends.append({
                        "title": snippet.get("title", ""),
                        "view_count": int(stats.get("viewCount", 0)),
                        "like_count": int(stats.get("likeCount", 0)),
                        "comment_count": int(stats.get("commentCount", 0)),
                        "published_at": snippet.get("publishedAt", ""),
                        "channel_title": snippet.get("channelTitle", ""),
                        "url": f"https://youtube.com/watch?v={item.get('id')}",
                        "source": "YouTube"
                    })
                return trends
            except Exception as e:
                logger.error(f"YouTube Data API fetch error: {e}. Falling back to trend simulator.")
                
        # High fidelity simulated fallback
        logger.info("Generating simulated YouTube trend data...")
        simulated_videos = [
            {
                "title": "I built a full SaaS in 2 hours using only autonomous AI developers",
                "channel_title": "TechVlog Daily",
                "base_views": 85000
            },
            {
                "title": "Unboxing the world's first true AR glasses in 2026",
                "channel_title": "GadgetUnbox",
                "base_views": 250000
            },
            {
                "title": "Why you should stop writing Python boilerplate code immediately",
                "channel_title": "CodeLab Pro",
                "base_views": 45000
            },
            {
                "title": "How neural interface headsets are actually performing in tests",
                "channel_title": "ScienceNow",
                "base_views": 120000
            },
            {
                "title": "The ultimate minimalist developer setup update: 2026 edition",
                "channel_title": "WorkspaceDesign",
                "base_views": 190000
            }
        ]
        
        trends = []
        for i, vid in enumerate(simulated_videos):
            views = int(vid["base_views"] * random.uniform(0.8, 1.4))
            likes = int(views * random.uniform(0.02, 0.05))
            comments = int(likes * random.uniform(0.05, 0.15))
            published_at = (datetime.now(timezone.utc) - timedelta(hours=i * 5)).isoformat()
            
            trends.append({
                "title": vid["title"],
                "view_count": views,
                "like_count": likes,
                "comment_count": comments,
                "published_at": published_at,
                "channel_title": vid["channel_title"],
                "url": f"https://youtube.com/watch?v=mock_video_{i}",
                "source": "YouTube"
            })
            
        return trends

if __name__ == "__main__":
    collector = YouTubeCollector()
    results = collector.fetch_trends(max_results=3)
    print(f"Fetched {len(results)} YouTube trends:")
    for r in results:
        print(f"- {r['title']} by {r['channel_title']} (Views: {r['view_count']}, Likes: {r['like_count']})")
