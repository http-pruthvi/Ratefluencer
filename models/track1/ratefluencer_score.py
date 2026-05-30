import os
import pickle
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from processing.feature_engineer import extract_features, extract_features_df

logger = logging.getLogger("ratefluencer.score")

class RatefluencerScorer:
    """Uses XGBoost/Gradient Boosting to calculate the proprietary 0-100 Campaign Performance Score."""
    
    def __init__(self, model_path: str = "c:/Users/pruthvi/Desktop/projects/Ratefluencer/models/saved/ratefluencer_score.pkl"):
        self.model_path = model_path
        self.model = None

    def train(self, df: pd.DataFrame):
        """Prepares target labels, extracts features, and trains the performance classifier."""
        logger.info("Extracting features for Ratefluencer Scorer training...")
        
        # 1. Feature Engineering
        X = extract_features_df(df)
        
        # 2. Define target label: High Campaign Performer
        # Criteria: Not a bot (is_fake_flag is False) AND good engagement rate (> 1.5%) AND active consistency (> 2 posts/week)
        y = (
            (df["is_fake_flag"] == False) & 
            (df["engagement_rate"] >= 0.015) & 
            (df["posting_frequency"] >= 2.0)
        ).astype(int)
        
        logger.info(f"Training set sizes. Total: {len(X)}, High Performers: {sum(y)}")
        
        # Try XGBoost, fallback to scikit-learn GradientBoosting if it has binary linking errors
        try:
            from xgboost import XGBClassifier
            logger.info("Initializing XGBClassifier...")
            self.model = XGBClassifier(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.08,
                random_state=42,
                eval_metric="logloss"
            )
        except Exception as e:
            logger.warning(f"XGBoost Classifier initialization failed: {e}. Falling back to scikit-learn GradientBoostingClassifier.")
            from sklearn.ensemble import GradientBoostingClassifier
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.08,
                random_state=42
            )
            
        self.model.fit(X, y)
        
        # Save trained model to saved folder
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump(self.model, f)
        logger.info(f"Ratefluencer Scorer saved successfully to {self.model_path}")

    def load(self):
        """Loads the pre-trained performance model."""
        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
            logger.info("Ratefluencer Scorer model loaded successfully.")
        else:
            logger.warning(f"No trained model found at {self.model_path}. Running with fallback heuristic scoring.")

    def predict(self, influencer: Dict[str, Any], authenticity_score: float = None) -> float:
        """Predicts the probability * 100 of campaign success."""
        if self.model is None:
            self.load()
            
        # Convert authenticity score (0-100) to quality factor [0, 1]
        quality = float(authenticity_score / 100.0) if authenticity_score is not None else None
        
        features_dict = extract_features(influencer, audience_quality=quality)
        
        # Convert dictionary to ordered feature array
        features_ordered = [
            features_dict["engagement_rate"],
            features_dict["share_rate"],
            features_dict["save_rate"],
            features_dict["audience_quality_score"],
            features_dict["posting_consistency"],
            features_dict["growth_rate_30d"],
            features_dict["comment_quality_score"],
            features_dict["content_category_score"],
            features_dict["audience_demographics"]
        ]
        
        X = np.array(features_ordered).reshape(1, -1)
        
        if self.model is not None:
            # predict_proba returns [prob_class_0, prob_class_1]
            try:
                prob = float(self.model.predict_proba(X)[0][1])
                score = prob * 100.0
            except Exception as e:
                logger.warning(f"Error predicting with model: {e}. Defaulting to weighted formula.")
                score = self._weighted_score_fallback(features_dict)
            return float(np.clip(score, 1.0, 100.0))
        else:
            # Cold-start formula based on features weights
            score = self._weighted_score_fallback(features_dict)
            return float(np.clip(score, 1.0, 100.0))

    def _weighted_score_fallback(self, f: Dict[str, float]) -> float:
        """Alternative weighted formula to calculate campaign potential when models are cold."""
        score = (
            f["engagement_rate"] * 10.0 * 25.0 + # scaled ER
            f["audience_quality_score"] * 30.0 + # authenticity weight
            f["posting_consistency"] * 15.0 +   # consistency weight
            f["growth_rate_30d"] * 10.0 * 50.0 + # growth weight
            f["comment_quality_score"] * 15.0 + # comment quality weight
            f["audience_demographics"] * 15.0    # demographics fit weight
        )
        return float(score)

if __name__ == "__main__":
    # Test script
    scorer = RatefluencerScorer()
    try:
        df = pd.read_csv("c:/Users/pruthvi/Desktop/projects/Ratefluencer/data/synthetic/influencers.csv")
        scorer.train(df)
        
        # Test profile score
        sample = df.iloc[0].to_dict()
        score = scorer.predict(sample)
        print(f"Sample Creator: {sample['username']}")
        print(f"Calculated Ratefluencer Score™: {score:.2f} / 100")
    except Exception as e:
        print(f"Error training Ratefluencer Scorer: {e}")
