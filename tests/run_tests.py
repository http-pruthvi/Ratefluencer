import os
import sys
import json
import logging

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ratefluencer.test_suite")
logger.info(f"Test suite initialized. Resolved project root: {project_root}")
logger.info(f"Active sys.path: {sys.path}")

def run_system_verification():
    """Runs functional integration tests across all components of the Ratefluencer platform."""
    logger.info("==============================================")
    logger.info("🛡️ STARTING RATEFLUENCER SYSTEM INTEGRATION TESTS")
    logger.info("==============================================")
    
    # --- Test 1: Database Operations ---
    logger.info("\n👉 TEST 1: Database & Model Verification")
    from api.database import SessionLocal, InfluencerORM
    db = SessionLocal()
    try:
        count = db.query(InfluencerORM).count()
        logger.info(f"🟢 Database holds {count} influencer records.")
        assert count > 0, "Database is empty!"
        
        sample = db.query(InfluencerORM).first()
        logger.info(f"🟢 Sample creator loaded: {sample.username} (Category: {sample.content_category})")
    except Exception as e:
        logger.error(f"🔴 DB Test Failed: {e}")
        return False
    finally:
        db.close()
        
    # --- Test 2: Track 1 ML Scoring Models ---
    logger.info("\n👉 TEST 2: Influencer Intelligence ML Models")
    try:
        from models.track1.authenticity_detector import AuthenticityDetector
        from models.track1.growth_predictor import GrowthPredictor
        from models.track1.ratefluencer_score import RatefluencerScorer
        
        detector = AuthenticityDetector()
        predictor = GrowthPredictor()
        scorer = RatefluencerScorer()
        
        sample_creator = sample.to_dict()
        
        auth = detector.predict(sample_creator)
        growth = predictor.predict(sample_creator)
        rate_score = scorer.predict(sample_creator, authenticity_score=auth)
        
        logger.info(f"🟢 Authenticity Score: {auth:.2f}/100")
        logger.info(f"🟢 Growth Score: {growth['growth_score']:.2f}/100 (30d Rate: {growth['growth_rate_30d_pct']:.2f}%)")
        logger.info(f"🟢 Ratefluencer Success Score™: {rate_score:.2f}/100")
        
        assert 0 <= auth <= 100, "Authenticity score out of bounds!"
        assert 0 <= rate_score <= 100, "Ratefluencer score out of bounds!"
    except Exception as e:
        logger.error(f"🔴 Track 1 ML Models Failed: {e}")
        return False
        
    # --- Test 3: SBERT Vector Brand Matcher ---
    logger.info("\n👉 TEST 3: Semantic Vector Brand Matcher")
    try:
        from models.track1.brand_matcher import BrandMatcher
        matcher = BrandMatcher()
        
        test_brief = "Seeking active gym-goers and fitness professionals to advertise premium tracking bands."
        results = matcher.get_top_creators_for_brand(test_brief, top_n=3)
        
        logger.info(f"🟢 Discovered {len(results)} creators for fitness brief:")
        for r in results:
            logger.info(f"  - Creator: {r['username']} | Category: {r['content_category']} | Match: {r['match_score']:.1f}%")
            
        assert len(results) > 0, "No vector brand matches returned!"
        assert results[0]["match_score"] > 0, "Invalid match scores!"
    except Exception as e:
        logger.error(f"🔴 SBERT Brand Matcher Failed: {e}")
        return False
        
    # --- Test 4: Trend Discovery Collectors ---
    logger.info("\n👉 TEST 4: Trend Collectors & Ranker")
    try:
        from ingestion.reddit_collector import RedditCollector
        from models.track2.trend_ranker import TrendRanker
        
        reddit = RedditCollector()
        ranker = TrendRanker()
        
        trends = reddit.fetch_trends(limit=5)
        ranked = ranker.rank_trends(trends, limit=3)
        
        logger.info(f"🟢 Collected {len(trends)} posts. Top Ranked Topic: {ranked[0]['topic']} (Score: {ranked[0]['trend_score']:.1f})")
        assert len(ranked) > 0, "No trends ranked!"
    except Exception as e:
        logger.error(f"🔴 Trend Collectors Failed: {e}")
        return False
        
    # --- Test 5: LangGraph Agent Pipeline ---
    logger.info("\n👉 TEST 5: LangGraph Agent Pipeline Sequential Execution")
    try:
        from agent.graph import run_agent_pipeline
        
        # Trigger full pipeline autonomously
        res = run_agent_pipeline(custom_topic="Automated AI developer agents in 2026", category="tech")
        
        logger.info(f"🟢 Discovered Topic Locked: {res['topic']}")
        logger.info(f"🟢 Generated Script Length: {len(res['script'])} characters")
        logger.info(f"🟢 Predicted Views: {res['expected_views']:,} | Virality Rating: {res['virality_score']:.2f}")
        
        assert len(res["script"]) > 20, "Script generation failed!"
        assert res["virality_score"] > 0.0, "Virality scoring failed!"
        assert len(res["linkedin_post"]) > 50, "LinkedIn post generation failed!"
    except Exception as e:
        import traceback
        logger.error(f"🔴 LangGraph Agent Pipeline Failed: {e}")
        traceback.print_exc()
        return False
        
    logger.info("\n==============================================")
    logger.info("🛡️ ALL SYSTEMS ONLINE - VERIFICATION SUCCESSFUL!")
    logger.info("==============================================")
    return True

if __name__ == "__main__":
    success = run_system_verification()
    sys.exit(0 if success else 1)
