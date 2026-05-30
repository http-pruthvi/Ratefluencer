import logging
from datetime import datetime, timezone
import numpy as np
from typing import Dict, Any, List

logger = logging.getLogger("ratefluencer.trend_ranker")

class TrendRanker:
    """Ranks and scores trending topics from 0-100 based on volume, engagement, and novelty."""
    
    def __init__(self):
        pass

    def calculate_novelty(self, created_at_ts: float) -> float:
        """Returns a novelty factor in range [0, 1] based on post recency (higher is newer)."""
        now = datetime.now(timezone.utc).timestamp()
        age_hours = (now - created_at_ts) / 3600.0
        
        # Max novelty if post is under 1 hour old, decays down to 0.1 at 48 hours
        if age_hours <= 0:
            return 1.0
        return float(np.clip(1.0 - (age_hours / 48.0) * 0.9, 0.1, 1.0))

    def score_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates a normalized 0-100 trend score for a single social piece."""
        source = item.get("source", "Reddit")
        title = item.get("title", "")
        
        # Extracted sub-factors
        novelty = 1.0
        velocity = 0.5
        volume = 0.5
        engagement = 0.5
        
        if source == "Reddit":
            score = float(item.get("score", 100))
            comments = float(item.get("num_comments", 10))
            created_ts = float(item.get("created_utc", datetime.now(timezone.utc).timestamp()))
            
            # Normalize volume relative to typical high-ranking posts (e.g. 5000 score)
            volume = min(1.0, score / 3500.0)
            
            # Engagement potential (ratio of comments to score)
            engagement = min(1.0, (comments / max(1.0, score)) * 4.0)
            
            # Time novelty
            novelty = self.calculate_novelty(created_ts)
            
            # Velocity: volume combined with recency
            velocity = min(1.0, volume / max(0.05, 1.0 - novelty))
            
        elif source == "YouTube":
            views = float(item.get("view_count", 10000))
            likes = float(item.get("like_count", 500))
            comments = float(item.get("comment_count", 50))
            
            # Volume relative to 500,000 views
            volume = min(1.0, views / 250000.0)
            
            # Engagement ratio (likes + comments) / views
            engagement = min(1.0, ((likes + comments) / max(1.0, views)) * 15.0)
            
            # YouTube velocity (approximated based on category average)
            velocity = min(1.0, volume * 1.5)
            novelty = 0.9 # assumed recent
            
        elif source == "TechCrunch" or source == "Wired" or source == "VentureBeat" or item.get("category") == "Technology":
            # RSS articles represent high expert relevance
            volume = 0.7
            engagement = 0.6
            novelty = 0.95
            velocity = 0.8
            
        # Weighted Final Trend Score (0-100)
        # Volume: 30%, Novelty: 20%, Engagement potential: 25%, Growth Velocity: 25%
        raw_score = (volume * 30.0) + (novelty * 20.0) + (engagement * 25.0) + (velocity * 25.0)
        
        # Add slight boost to AI topics to mimic 2026 tech trends
        title_lower = title.lower()
        if any(kw in title_lower for kw in ["ai", "gpt", "agent", "neural", "openai", "claude", "autonomous"]):
            raw_score += 8.0
            
        trend_score = float(np.clip(raw_score, 10.0, 100.0))
        
        # Extracted keyword/topic representation
        topic = self._extract_niche_topic(title)
        
        return {
            "title": title,
            "topic": topic,
            "source": source,
            "url": item.get("url", ""),
            "volume_factor": float(volume),
            "novelty_factor": float(novelty),
            "engagement_factor": float(engagement),
            "velocity_factor": float(velocity),
            "trend_score": trend_score
        }

    def _extract_niche_topic(self, title: str) -> str:
        """Helper to extract a clean topic hook from a technical headline."""
        clean = title.strip()
        # Remove trailing periods
        if clean.endswith("."):
            clean = clean[:-1]
        # Truncate clean title into a strong subject line if too long
        if len(clean) > 55:
            words = clean.split()
            # Try to grab the first 6-8 words
            clean = " ".join(words[:7]) + "..."
        return clean

    def rank_trends(self, items: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
        """Scores and ranks a list of items, returning the top N structured trends."""
        scored_items = [self.score_item(item) for item in items]
        scored_items.sort(key=lambda x: x["trend_score"], reverse=True)
        
        # Filter duplicates by topic keywords
        seen_topics = set()
        unique_trends = []
        for trend in scored_items:
            # Check basic uniqueness
            words = set(trend["topic"].lower().replace("...", "").split())
            if not words:
                continue
            is_duplicate = False
            for seen in seen_topics:
                # If there's high word overlap, treat as duplicate
                if len(words.intersection(seen)) >= 3:
                    is_duplicate = True
                    break
            if not is_duplicate:
                seen_topics.add(frozenset(words))
                unique_trends.append(trend)
                
        return unique_trends[:limit]

if __name__ == "__main__":
    ranker = TrendRanker()
    mock_reddit_item = {
        "title": "OpenAI launches new GPT-5 model with real-time video understanding",
        "score": 4200,
        "num_comments": 850,
        "created_utc": datetime.now(timezone.utc).timestamp() - 7200,
        "source": "Reddit"
    }
    result = ranker.score_item(mock_reddit_item)
    print(f"Topic: {result['topic']}")
    print(f"Trend Score: {result['trend_score']:.1f}")
