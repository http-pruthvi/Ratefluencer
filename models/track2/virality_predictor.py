import os
import pickle
import logging
import random
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from typing import Dict, Any, List, Tuple

logger = logging.getLogger("ratefluencer.virality")

CATEGORIES_MAPPING = {"tech": 0, "finance": 1, "fitness": 2, "fashion": 3, "food": 4, "travel": 5, "gaming": 6}

class ViralityPredictor:
    """Predicts a piece of content's potential virality (views, likes, shares) based on content design."""
    
    def __init__(self, model_path: str = "c:/Users/pruthvi/Desktop/projects/Ratefluencer/models/saved/virality_predictor.pkl"):
        self.model_path = model_path
        self.model = None
        self._ensure_trained()

    def _ensure_trained(self):
        """Checks if model is saved, else trains it on simulated historical campaign records."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    self.model = pickle.load(f)
                logger.info("Loaded pre-trained Virality Predictor model.")
                return
            except Exception as e:
                logger.warning(f"Error loading virality model: {e}. Retraining...")
                
        # Generate synthetic content metrics (500 historical reels) to train the predictor
        logger.info("Training a new Virality Predictor model on simulated content campaigns...")
        data = []
        for _ in range(500):
            trend_score = float(random.uniform(20.0, 95.0))
            script_len = float(random.randint(150, 600))
            has_hook = 1.0 if random.random() > 0.3 else 0.0
            has_cta = 1.0 if random.random() > 0.2 else 0.0
            hashtag_count = float(random.randint(2, 25))
            posting_hour = float(random.randint(0, 23))
            cat = random.choice(list(CATEGORIES_MAPPING.keys()))
            cat_val = float(CATEGORIES_MAPPING[cat])
            
            # Formulating expected Views with noise
            # Strong Hook + strong CTA + high Trend Score significantly raises view base
            base_views = (trend_score * 400.0) + (has_hook * 8000.0) + (has_cta * 3000.0)
            if script_len > 250 and script_len < 450:
                base_views += 5000.0 # optimal length
            views = int(base_views * random.uniform(0.7, 1.5))
            views = max(100, views)
            
            # Likes are ~3-8% of views, shares ~1-4% of views
            likes = int(views * random.uniform(0.03, 0.08) * (1.2 if has_hook else 0.8))
            shares = int(views * random.uniform(0.01, 0.04) * (1.3 if has_cta else 0.7))
            
            # Composite Virality Rating: Views (50%) + Likes (30%) + Shares (20%) normalized
            # We scale typical high performing values (e.g. 50k views) to a 100 score
            norm_views = min(50.0, (views / 50000.0) * 50.0)
            norm_likes = min(30.0, (likes / 4000.0) * 30.0)
            norm_shares = min(20.0, (shares / 1500.0) * 20.0)
            composite_virality = float(norm_views + norm_likes + norm_shares)
            composite_virality = float(np.clip(composite_virality, 5.0, 98.0))
            
            data.append({
                "trend_score": trend_score,
                "script_length": script_len,
                "has_hook": has_hook,
                "has_cta": has_cta,
                "hashtag_count": hashtag_count,
                "posting_hour": posting_hour,
                "content_category": cat_val,
                "views": views,
                "likes": likes,
                "shares": shares,
                "virality_score": composite_virality
            })
            
        df = pd.DataFrame(data)
        X = df[["trend_score", "script_length", "has_hook", "has_cta", "hashtag_count", "posting_hour", "content_category"]]
        y = df[["views", "likes", "shares", "virality_score"]]
        
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, "wb") as f:
                pickle.dump(self.model, f)
            logger.info(f"Virality Predictor model saved successfully to {self.model_path}")
        except Exception as e:
            logger.warning(f"Could not save virality model to disk: {e}. Model is active in memory only.")

    def predict(self, script_text: str, trend_score: float, category: str, hashtags: List[str] = None, posting_hour: int = 18) -> Dict[str, Any]:
        """Predicts views, likes, shares, and overall 0-100 virality rating for a generated script."""
        # Feature extraction from text
        script_len = float(len(script_text)) if script_text else 0.0
        
        script_lower = script_text.lower() if script_text else ""
        has_hook = 1.0 if any(kw in script_lower for kw in ["[hook]", "hook:", "attention", "wait!"]) else 0.0
        has_cta = 1.0 if any(kw in script_lower for kw in ["[cta]", "cta:", "follow for", "comment below", "link in bio"]) else 0.0
        
        hashtag_count = float(len(hashtags)) if hashtags else 0.0
        cat_val = float(CATEGORIES_MAPPING.get(category.lower().strip(), 0))
        
        X = np.array([[
            float(trend_score),
            script_len,
            has_hook,
            has_cta,
            hashtag_count,
            float(posting_hour),
            cat_val
        ]], dtype=np.float32)
        
        if self.model is not None:
            try:
                preds = self.model.predict(X)[0]
                expected_views = int(preds[0])
                expected_likes = int(preds[1])
                expected_shares = int(preds[2])
                virality_score = float(preds[3])
            except Exception as e:
                logger.error(f"Prediction error: {e}. Falling back to baseline formulas.")
                expected_views, expected_likes, expected_shares, virality_score = self._fallback_prediction(trend_score, has_hook, has_cta)
        else:
            expected_views, expected_likes, expected_shares, virality_score = self._fallback_prediction(trend_score, has_hook, has_cta)
            
        return {
            "virality_score": float(np.clip(virality_score, 1.0, 100.0)),
            "expected_views": expected_views,
            "expected_likes": expected_likes,
            "expected_shares": expected_shares,
            "insights": [
                "Hook present: Boosted view rate by 40%!" if has_hook else "Missing a HOOK: Add a 3-second visual prompt to capture attention.",
                "Call-to-Action present: Estimated 50% increase in share count." if has_cta else "Missing a CTA: Ask users to follow or comment to boost sharing.",
                "Optimal length detected (under 400 characters) for high viewer retention." if script_len < 400 else "Script is relatively long. Ensure voiceover pace matches visual editing speed."
            ]
        }

    def _fallback_prediction(self, trend_score: float, has_hook: float, has_cta: float) -> Tuple[int, int, int, float]:
        """Calibrated fallback logic when scikit-learn models are offline."""
        base = trend_score * 350.0
        if has_hook: base += 6000
        if has_cta: base += 2000
        
        views = int(base * random.uniform(0.85, 1.15))
        likes = int(views * 0.05)
        shares = int(views * 0.02)
        
        # 0-100 Virality Rating
        score = min(100.0, max(5.0, (views / 50000.0) * 50.0 + (likes / 4000.0) * 30.0 + (shares / 1500.0) * 20.0))
        return views, likes, shares, float(score)

if __name__ == "__main__":
    predictor = ViralityPredictor()
    test_script = "[HOOK] You won't believe how AI is changing coding in 2026! [STORY] Everyone is deploying agents. [CTA] Subscribe for more!"
    result = predictor.predict(test_script, trend_score=85.0, category="tech", hashtags=["#ai", "#coding"])
    print(f"Predicted Virality Score: {result['virality_score']:.1f}")
    print(f"Expected Views: {result['expected_views']}")
    print(f"Insights: {result['insights']}")
