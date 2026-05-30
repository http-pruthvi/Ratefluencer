import os
import sys
import json
import logging
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.track1.authenticity_detector import AuthenticityDetector
from models.track1.growth_predictor import GrowthPredictor
from models.track1.brand_matcher import BrandMatcher
from models.track1.ratefluencer_score import RatefluencerScorer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ratefluencer.evaluator")

def run_evaluation_suite():
    csv_path = "c:/Users/pruthvi/Desktop/projects/Ratefluencer/data/synthetic/influencers.csv"
    if not os.path.exists(csv_path):
        logger.error(f"Dataset not found at {csv_path}. Run generate.py first.")
        return
        
    df = pd.read_csv(csv_path)
    logger.info("==================================================")
    logger.info("🎓 RUNNING TRACK 1 TRAINING & PERFORMANCE METRICS")
    logger.info("==================================================")
    
    # ---------------------------------------------
    # 1. Authenticity Detector (Isolation Forest)
    # ---------------------------------------------
    logger.info("\n1. Training Authenticity Detector...")
    detector = AuthenticityDetector()
    detector.train(df)
    
    # Evaluate fraud detection accuracy (contamination)
    predictions = []
    for _, row in df.iterrows():
        predictions.append(detector.predict(row.to_dict()))
        
    # True bot flags are is_fake_flag == True
    # Let's see: how many fake profiles get low authenticity scores (< 50)?
    true_fakes = df["is_fake_flag"] == True
    low_scores = np.array(predictions) < 50.0
    
    bot_detection_rate = (sum(true_fakes & low_scores) / max(1, sum(true_fakes))) * 100.0
    logger.info(f"✅ Authenticity Detector trained.")
    logger.info(f"📊 [Fraud Detection Rate]: {bot_detection_rate:.2f}% of bot accounts successfully flagged.")
    
    # ---------------------------------------------
    # 2. Growth Predictor Time Series
    # ---------------------------------------------
    logger.info("\n2. Evaluating Growth Predictor Timeline Accuracy...")
    predictor = GrowthPredictor()
    
    # Calculate MAPE (Mean Absolute Percentage Error) on the first 10 accounts
    errors = []
    for idx in range(10):
        row = df.iloc[idx].to_dict()
        history = json.loads(row["follower_history_30d"])
        
        # Test timeline forecasting accuracy: split first 20 days as train, forecast next 10 days
        train_hist = history[:20]
        actual_val = history[-1]
        
        result = predictor.predict({**row, "follower_history_30d": train_hist}, days_to_predict=10)
        predicted_val = result["predicted_history"][-1]
        
        err = abs(actual_val - predicted_val) / max(1.0, actual_val)
        errors.append(err)
        
    mape = np.mean(errors) * 100.0
    logger.info(f"✅ Growth Predictor operational.")
    logger.info(f"📊 [Mean Absolute Percentage Error]: {mape:.2f}% forecasting variance.")
    
    # ---------------------------------------------
    # 3. SBERT Brand Matcher
    # ---------------------------------------------
    logger.info("\n3. Evaluating Semantic Vector Brand Matcher...")
    matcher = BrandMatcher()
    
    test_brief = "AI auto-complete tool for code refactoring and pipeline generation."
    matches = matcher.get_top_creators_for_brand(test_brief, top_n=3)
    
    avg_top_match = np.mean([m["match_score"] for m in matches])
    logger.info(f"✅ SBERT Semantic Space constructed.")
    logger.info(f"📊 [Average Top 3 Match Score]: {avg_top_match:.1f}%")
    logger.info(f"⭐ Sample Match: {matches[0]['username']} | Match: {matches[0]['match_score']:.1f}%")
    
    # ---------------------------------------------
    # 4. Ratefluencer Success Scorer (Classifier)
    # ---------------------------------------------
    logger.info("\n4. Training Ratefluencer Scorer...")
    scorer = RatefluencerScorer()
    
    # Prepare features and target success labels (High campaign potential)
    # Target: Not a bot (is_fake_flag is False) AND ER > 1.5% AND active frequency > 2 posts/week
    y = (
        (df["is_fake_flag"] == False) & 
        (df["engagement_rate"] >= 0.015) & 
        (df["posting_frequency"] >= 2.0)
    ).astype(int)
    
    # Extract features DataFrame
    from processing.feature_engineer import extract_features_df
    X = extract_features_df(df)
    
    # 80/20 train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
    
    # Fit model on training set
    from sklearn.ensemble import GradientBoostingClassifier
    clf = GradientBoostingClassifier(n_estimators=100, max_depth=4, learning_rate=0.08, random_state=42)
    clf.fit(X_train, y_train)
    
    # Save model pickle
    os.makedirs(os.path.dirname(scorer.model_path), exist_ok=True)
    with open(scorer.model_path, "wb") as f:
        pickle.dump(clf, f)
        
    scorer.model = clf
    
    # Make test predictions
    y_pred = clf.predict(X_test)
    
    # Calculate classical ML metrics
    acc = accuracy_score(y_test, y_pred) * 100.0
    prec = precision_score(y_test, y_pred) * 100.0
    rec = recall_score(y_test, y_pred) * 100.0
    f1 = f1_score(y_test, y_pred) * 100.0
    
    logger.info(f"✅ Ratefluencer Scorer trained and saved to {scorer.model_path}")
    logger.info(f"📊 [XGBoost/GradientBoosting Classifier Scorecard]:")
    logger.info(f"   - Accuracy  : {acc:.2f}%")
    logger.info(f"   - Precision : {prec:.2f}%")
    logger.info(f"   - Recall    : {rec:.2f}%")
    logger.info(f"   - F1-Score  : {f1:.2f}%")
    logger.info("==================================================")

if __name__ == "__main__":
    run_evaluation_suite()
