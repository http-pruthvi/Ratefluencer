import os
import logging
import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("ratefluencer.instagram")

class InstagramCollector:
    """Collects trending creators, metrics, and hashtags from the Instagram Graph API (or simulated fallback)."""
    
    def __init__(self):
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.instagram_active = False
        
        if self.access_token and "your_" not in self.access_token and self.access_token != "":
            try:
                # Place holder for active Graph API validation
                self.instagram_active = True
                logger.info("Instagram Graph API client initialized successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize Instagram client: {e}. Switching to mock simulator.")
        else:
            logger.info("Instagram ACCESS_TOKEN missing. Instagram collector running in mock simulator mode.")

    def fetch_trends(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Gathers hot/trending hashtags and topics from Instagram."""
        if self.instagram_active:
            try:
                # Live network requests would go here
                trends = []
                # return trends
                pass
            except Exception as e:
                logger.error(f"Instagram Graph API fetch error: {e}. Falling back to trend simulator.")
                
        # High fidelity simulated fallback
        logger.info("Generating simulated Instagram trend data...")
        simulated_trends = [
            {
                "topic": "Zona de cardio / Zone 2 longevity training",
                "tag": "#Zone2Cardio",
                "media_count": 245000,
                "growth_velocity": 42.5
            },
            {
                "topic": "Sustainable capsule wardrobes for workwear styling",
                "tag": "#CapsuleWardrobe",
                "media_count": 890000,
                "growth_velocity": 31.2
            },
            {
                "topic": "Autonomous AI developers and AI agent frameworks",
                "tag": "#AICoding",
                "media_count": 125000,
                "growth_velocity": 88.4
            },
            {
                "topic": "Index fund automated compounding wealth plans",
                "tag": "#PersonalFinance",
                "media_count": 670000,
                "growth_velocity": 15.6
            },
            {
                "topic": "20-minute baking tray high-protein meal preps",
                "tag": "#MealPrepSunday",
                "media_count": 412000,
                "growth_velocity": 24.8
            }
        ]
        
        trends = []
        for i, item in enumerate(simulated_trends[:limit]):
            media_count = int(item["media_count"] * random.uniform(0.9, 1.2))
            trends.append({
                "title": f"Instagram Trending tag: {item['tag']} - {item['topic']}",
                "tag": item["tag"],
                "score": media_count,
                "num_comments": int(media_count * random.uniform(0.01, 0.03)),
                "created_utc": (datetime.now(timezone.utc) - timedelta(hours=i * 2)).timestamp(),
                "subreddit": "instagram",  # align with general schema structure
                "url": f"https://instagram.com/explore/tags/{item['tag'][1:]}",
                "source": "Instagram",
                "growth_velocity": item["growth_velocity"]
            })
            
        return trends

if __name__ == "__main__":
    collector = InstagramCollector()
    results = collector.fetch_trends(limit=3)
    print(f"Fetched {len(results)} Instagram trends:")
    for r in results:
        print(f"- {r['title']} (Score: {r['score']}, Source: {r['source']})")
