import os
import sys
import logging
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.track2.trend_ranker import TrendRanker
from models.track2.virality_predictor import ViralityPredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ratefluencer.track2_trainer")

def train_and_eval_track2():
    logger.info("==================================================")
    logger.info("🎬 RUNNING TRACK 2 TRAINING & SAMPLE PREDICTIONS")
    logger.info("==================================================")
    
    # ---------------------------------------------
    # 1. Trend Ranker evaluation
    # ---------------------------------------------
    logger.info("\n1. Running Trend Ranker Scorer...")
    ranker = TrendRanker()
    
    sample_reddit_post = {
        "title": "OpenAI drops next-generation reasoning model capable of planning",
        "score": 3800,
        "num_comments": 780,
        "created_utc": datetime.now(timezone.utc).timestamp() - 7200, # 2 hours ago
        "source": "Reddit"
    }
    
    trend_result = ranker.score_item(sample_reddit_post)
    logger.info("✅ Trend Ranker evaluated successfully.")
    logger.info("📊 [Sample Trend Scorecard]:")
    logger.info(f"   - Topic        : {trend_result['topic']}")
    logger.info(f"   - Trend Score  : {trend_result['trend_score']:.1f}/100")
    logger.info(f"   - Novelty      : {trend_result['novelty_factor']*100:.0f}%")
    logger.info(f"   - Velocity     : {trend_result['velocity_factor']*100:.0f}%")
    logger.info(f"   - Engagement   : {trend_result['engagement_factor']*100:.0f}%")
    
    # ---------------------------------------------
    # 2. Virality Predictor Training & Evaluation
    # ---------------------------------------------
    logger.info("\n2. Training Virality Predictor (Random Forest)...")
    
    # Instantiating ViralityPredictor automatically triggers self-training on 500 campaign records
    # and saves the pre-trained weights to models/saved/virality_predictor.pkl
    predictor = ViralityPredictor()
    
    sample_script = (
        "[HOOK]\n(0-5s): Pointing at screen. \"This new AI model can plan out full SaaS software systems in seconds!\"\n\n"
        "[STORY]\n(5-25s): \"OpenAI just dropped their latest reasoning engine, and developers are completely shocked. It doesn't just write code; it plans architectures!\"\n\n"
        "[INSIGHTS]\n(25-50s): \"The future developer isn't a code writer—they are an agent supervisor. Focus on system flows rather than syntax!\"\n\n"
        "[CTA]\n(50-60s): \"Are you building with agents yet? Let me know in the comments and follow for daily tech!\""
    )
    
    virality_result = predictor.predict(
        script_text=sample_script,
        trend_score=trend_result["trend_score"],
        category="tech",
        hashtags=["#ai", "#coding", "#tech", "#programming", "#developer"]
    )
    
    logger.info("✅ Virality Predictor trained and saved to models/saved/virality_predictor.pkl")
    logger.info("📊 [Script Virality Predictions]:")
    logger.info(f"   - Virality Score : {virality_result['virality_score']:.2f}/100")
    logger.info(f"   - Expected Views : {virality_result['expected_views']:,} views")
    logger.info(f"   - Expected Likes : {virality_result['expected_likes']:,} likes")
    logger.info(f"   - Expected Shares: {virality_result['expected_shares']:,} shares")
    logger.info("   - Critiques:")
    for ins in virality_result["insights"]:
        logger.info(f"     * {ins}")
    logger.info("==================================================")

if __name__ == "__main__":
    train_and_eval_track2()
