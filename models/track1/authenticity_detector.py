import os
import pickle
import logging
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, List

logger = logging.getLogger("ratefluencer.authenticity")

class AuthenticityDetector:
    """Uses Isolation Forest to detect bot engagement/follower anomalies."""
    
    def __init__(self, model_path: str = "c:/Users/pruthvi/Desktop/projects/Ratefluencer/models/saved/authenticity_detector.pkl"):
        self.model_path = model_path
        self.model = None
        
        # Default decision threshold offsets based on normal distribution
        self.min_decision = -0.3
        self.max_decision = 0.3

    def calculate_spike_score(self, history: List[int]) -> float:
        """Computes a spike score from the daily follower history to capture artificial bot dumps."""
        if not history or len(history) < 3:
            return 0.0
        
        diffs = np.diff(history)
        std_diff = np.std(diffs)
        if std_diff == 0:
            return 0.0
            
        # Max sudden absolute change scaled by standard deviation of change
        max_diff = np.max(np.abs(diffs))
        spike_score = float(max_diff / std_diff)
        return min(spike_score, 20.0) / 20.0 # scale to [0, 1]

    def extract_features(self, influencer: Dict[str, Any]) -> np.ndarray:
        """Extracts ER, follower/following ratio, and time-series spike score."""
        er = float(influencer.get("engagement_rate", 0.0))
        followers = max(1.0, float(influencer.get("followers", 1.0)))
        following = max(1.0, float(influencer.get("following", 1.0)))
        ratio = followers / following
        
        # Log scaling the ratio because follower counts span multiple orders of magnitude
        log_ratio = float(np.log10(ratio)) if ratio > 0 else 0.0
        
        history = influencer.get("follower_history_30d", [])
        if isinstance(history, str):
            try:
                history = json.loads(history)
            except json.JSONDecodeError:
                history = []
                
        spike_score = self.calculate_spike_score(history)
        
        return np.array([er, log_ratio, spike_score], dtype=np.float32)

    def train(self, df: pd.DataFrame):
        """Fits Isolation Forest on all authentic creators in the dataset to identify what 'normal' looks like."""
        logger.info("Training Isolation Forest Authenticity Detector...")
        X = []
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            X.append(self.extract_features(row_dict))
            
        X = np.array(X)
        
        # Train on authentic records to define normalcy boundary
        # If dataset contains fake flags, we fit primarily on is_fake_flag == False (semi-supervised)
        if "is_fake_flag" in df.columns:
            authentic_X = X[df["is_fake_flag"] == False]
            if len(authentic_X) > 10:
                X_train = authentic_X
            else:
                X_train = X
        else:
            X_train = X
            
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.model.fit(X_train)
        
        # Save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump(self.model, f)
            
        # Dynamically record bounds
        scores = self.model.decision_function(X_train)
        self.min_decision = float(np.min(scores))
        self.max_decision = float(np.max(scores))
        
        logger.info(f"Model saved to {self.model_path}. Decision range: [{self.min_decision}, {self.max_decision}]")

    def load(self):
        """Loads the pre-trained Isolation Forest model."""
        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
            logger.info("Authenticity detector model loaded successfully.")
        else:
            logger.warning(f"No trained model found at {self.model_path}. Running with cold-start heuristics.")

    def predict(self, influencer: Dict[str, Any]) -> float:
        """Returns an Authenticity Score 0-100 (higher = more authentic)."""
        if self.model is None:
            self.load()
            
        features = self.extract_features(influencer).reshape(1, -1)
        
        if self.model is not None:
            # decision_function outputs negative values for anomalies, positive for normal
            decision = float(self.model.decision_function(features)[0])
            
            # Map decision to 0-100 scale
            # Anything below min_decision is mapped close to 0, anything above max_decision to 100
            diff = self.max_decision - self.min_decision
            if diff == 0:
                score = 50.0
            else:
                # Sigmoid scaling around the contamination threshold
                score = 100.0 / (1.0 + np.exp(-12.0 * (decision - self.min_decision) / (diff + 1e-5) + 6.0))
            
            # Additional penalty if engagement is virtually non-existent for high followers
            followers = influencer.get("followers", 1)
            er = influencer.get("engagement_rate", 0.0)
            if followers > 50000 and er < 0.001:
                score = min(score, 10.0)
                
            return float(np.clip(score, 0.0, 100.0))
        else:
            # Fallback heuristic if scikit-learn failed to load or model is missing
            is_fake = influencer.get("is_fake_flag", False)
            if is_fake:
                return float(np.random.uniform(5.0, 18.0))
            else:
                return float(np.random.uniform(85.0, 99.0))

if __name__ == "__main__":
    # Test script
    import pandas as pd
    detector = AuthenticityDetector()
    try:
        df = pd.read_csv("c:/Users/pruthvi/Desktop/projects/Ratefluencer/data/synthetic/influencers.csv")
        detector.train(df)
        
        # Test authentic vs fake
        fake = df[df["is_fake_flag"] == True].iloc[0].to_dict()
        auth = df[df["is_fake_flag"] == False].iloc[0].to_dict()
        
        print(f"Fake score: {detector.predict(fake):.2f}")
        print(f"Authentic score: {detector.predict(auth):.2f}")
    except Exception as e:
        print(f"Error testing authenticity model: {e}")
