import re
import logging
from typing import Dict, Any, Union

logger = logging.getLogger("ratefluencer.cleaner")

def clean_username(username: str) -> str:
    """Normalizes an influencer handle (adds leading @, lowercases, strips whitespace)."""
    if not username:
        return ""
    cleaned = username.strip().lower()
    if not cleaned.startswith("@"):
        cleaned = "@" + cleaned
    # Remove any invalid characters
    cleaned = re.sub(r"[^a-z0-9__@]", "", cleaned)
    return cleaned

def parse_abbreviated_number(val: Union[str, int, float]) -> int:
    """Converts abbreviated numbers (e.g. '1.5M', '100K') to standard integer."""
    if isinstance(val, (int, float)):
        return int(val)
    if not val:
        return 0
    
    val_str = str(val).strip().upper()
    multiplier = 1
    
    if val_str.endswith("K"):
        multiplier = 1000
        val_str = val_str[:-1]
    elif val_str.endswith("M"):
        multiplier = 1000000
        val_str = val_str[:-1]
    elif val_str.endswith("B"):
        multiplier = 1000000000
        val_str = val_str[:-1]
        
    try:
        return int(float(val_str) * multiplier)
    except ValueError:
        logger.warning(f"Unable to parse number: {val}. Returning 0.")
        return 0

def clean_influencer_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitizes raw influencer input dicts to consistent typed dicts."""
    cleaned = {}
    cleaned["username"] = clean_username(raw_data.get("username", ""))
    cleaned["platform"] = str(raw_data.get("platform", "Instagram")).strip()
    
    cleaned["followers"] = parse_abbreviated_number(raw_data.get("followers", 0))
    cleaned["following"] = parse_abbreviated_number(raw_data.get("following", 0))
    cleaned["posts_count"] = parse_abbreviated_number(raw_data.get("posts_count", 0))
    
    cleaned["engagement_rate"] = float(raw_data.get("engagement_rate", 0.0))
    # If engagement rate is given as percentage (e.g. 5.5 instead of 0.055), convert it
    if cleaned["engagement_rate"] > 1.0:
        cleaned["engagement_rate"] /= 100.0
        
    cleaned["avg_likes"] = float(raw_data.get("avg_likes", 0.0))
    cleaned["avg_comments"] = float(raw_data.get("avg_comments", 0.0))
    cleaned["avg_shares"] = float(raw_data.get("avg_shares", 0.0))
    cleaned["avg_saves"] = float(raw_data.get("avg_saves", 0.0))
    
    cleaned["posting_frequency"] = float(raw_data.get("posting_frequency", 1.0))
    cleaned["audience_age_18_24_pct"] = float(raw_data.get("audience_age_18_24_pct", 0.0))
    cleaned["audience_india_pct"] = float(raw_data.get("audience_india_pct", 0.0))
    cleaned["is_fake_flag"] = bool(raw_data.get("is_fake_flag", False))
    
    history = raw_data.get("follower_history_30d", [])
    if isinstance(history, str):
        import json
        try:
            history = json.loads(history)
        except json.JSONDecodeError:
            history = []
    cleaned["follower_history_30d"] = [int(h) for h in history if str(h).isdigit()]
    
    cleaned["content_category"] = str(raw_data.get("content_category", "tech")).strip().lower()
    cleaned["bio"] = str(raw_data.get("bio", "")).strip()
    
    return cleaned
