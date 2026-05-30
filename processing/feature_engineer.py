import numpy as np
import pandas as pd
from typing import Dict, Any, List

CATEGORIES_MAPPING = {
    "tech": 0,
    "finance": 1,
    "fitness": 2,
    "fashion": 3,
    "food": 4,
    "travel": 5,
    "gaming": 6
}

def extract_features(influencer: Dict[str, Any], audience_quality: float = None) -> Dict[str, float]:
    """Extracts the 9 core ML features from an influencer data dictionary."""
    followers = influencer.get("followers", 1000)
    followers = max(1, followers)
    
    avg_likes = influencer.get("avg_likes", 0)
    avg_comments = influencer.get("avg_comments", 0)
    avg_shares = influencer.get("avg_shares", 0)
    avg_saves = influencer.get("avg_saves", 0)
    
    # Feature 1: Engagement Rate
    engagement_rate = influencer.get("engagement_rate", 0.0)
    if engagement_rate == 0.0:
        engagement_rate = (avg_likes + avg_comments) / followers
    
    # Feature 2: Share Rate
    share_rate = avg_shares / followers
    
    # Feature 3: Save Rate
    save_rate = avg_saves / followers
    
    # Feature 4: Audience Quality Score (from authenticity detector)
    is_fake = influencer.get("is_fake_flag", False)
    if audience_quality is not None:
        audience_quality_score = audience_quality
    else:
        # Fallback heuristic if model is not loaded
        audience_quality_score = 0.15 if is_fake else 0.88
        
    # Feature 5: Posting Consistency
    # Scaled value [0, 1] derived from posting_frequency
    freq = influencer.get("posting_frequency", 3.0)
    if is_fake:
        posting_consistency = min(0.3, freq / 10.0)
    else:
        posting_consistency = min(1.0, freq / 7.0)
        
    # Feature 6: Growth Rate 30d
    history = influencer.get("follower_history_30d", [])
    if isinstance(history, str):
        import json
        try:
            history = json.loads(history)
        except json.JSONDecodeError:
            history = []
            
    if len(history) >= 2 and history[0] > 0:
        growth_rate_30d = (history[-1] - history[0]) / history[0]
    else:
        growth_rate_30d = 0.02 # default 2% growth
        
    # Feature 7: Comment Quality Score (simulating NLP sentiment)
    if is_fake:
        comment_quality_score = float(np.random.uniform(0.1, 0.3))
    else:
        comment_quality_score = float(np.random.uniform(0.7, 0.9))
        
    # Feature 8: Content Category Encoded
    cat = str(influencer.get("content_category", "tech")).strip().lower()
    content_category_encoded = float(CATEGORIES_MAPPING.get(cat, 0))
    
    # Feature 9: Audience Demographics Score
    age_pct = influencer.get("audience_age_18_24_pct", 50.0) / 100.0
    india_pct = influencer.get("audience_india_pct", 30.0) / 100.0
    # Higher demographic score if they have good Gen-Z audience and balanced geographic reach
    audience_demographics_score = float(age_pct * 0.6 + (1.0 - india_pct) * 0.4)
    
    return {
        "engagement_rate": float(engagement_rate),
        "share_rate": float(share_rate),
        "save_rate": float(save_rate),
        "audience_quality_score": float(audience_quality_score),
        "posting_consistency": float(posting_consistency),
        "growth_rate_30d": float(growth_rate_30d),
        "comment_quality_score": float(comment_quality_score),
        "content_category_score": float(content_category_encoded), # mapping name to score
        "audience_demographics": float(audience_demographics_score)
    }

def extract_features_df(df: pd.DataFrame) -> pd.DataFrame:
    """Takes a Pandas DataFrame and returns a DataFrame of the 9 engineered features."""
    features_list = []
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        # Parse JSON columns if necessary
        if isinstance(row_dict.get("follower_history_30d"), str):
            import json
            try:
                row_dict["follower_history_30d"] = json.loads(row_dict["follower_history_30d"])
            except json.JSONDecodeError:
                row_dict["follower_history_30d"] = []
        features_list.append(extract_features(row_dict))
    return pd.DataFrame(features_list)
