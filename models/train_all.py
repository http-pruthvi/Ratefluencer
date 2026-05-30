import os
import logging
import pandas as pd

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.track1.authenticity_detector import AuthenticityDetector
from models.track1.ratefluencer_score import RatefluencerScorer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ratefluencer.trainer")

def train_and_save_all():
    """Loads dataset and trains both Track 1 models, saving weights to the saved directory."""
    csv_path = "c:/Users/pruthvi/Desktop/projects/Ratefluencer/data/synthetic/influencers.csv"
    
    if not os.path.exists(csv_path):
        logger.error(f"Dataset not found at {csv_path}. Please run synthetic data generator first.")
        return
        
    logger.info(f"Loading training data from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # 1. Train Authenticity Detector
    logger.info("--- Step 1: Training Authenticity Detector (Isolation Forest) ---")
    detector = AuthenticityDetector()
    detector.train(df)
    
    # 2. Train Ratefluencer Scorer
    logger.info("--- Step 2: Training Ratefluencer Scorer (XGBoost/GradientBoosting) ---")
    scorer = RatefluencerScorer()
    scorer.train(df)
    
    logger.info("All models trained and saved successfully!")

if __name__ == "__main__":
    train_and_save_all()
