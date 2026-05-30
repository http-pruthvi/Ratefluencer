import os
import logging
from typing import Dict, Any, List, TypedDict
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_ACTIVE = True
except ImportError:
    LANGGRAPH_ACTIVE = False

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import collectors, models and rankers
from ingestion.reddit_collector import RedditCollector
from ingestion.youtube_collector import YouTubeCollector
from ingestion.news_rss_collector import RSSCollector
from models.track2.trend_ranker import TrendRanker
from models.track2.content_generator import ContentGenerator
from models.track2.virality_predictor import ViralityPredictor

logger = logging.getLogger("ratefluencer.agent")

class AgentState(TypedDict):
    """Orchestrates variables passed through nodes in the LangGraph workflow."""
    topic: str
    category: str
    trend_score: float
    script: str
    linkedin_post: str
    instagram_caption: str
    hashtags: List[str]
    virality_score: float
    expected_views: int
    expected_likes: int
    expected_shares: int
    insights: List[str]
    error: str

# Instantiate global clients for agent workflows
reddit_client = RedditCollector()
youtube_client = YouTubeCollector()
rss_client = RSSCollector()
trend_ranker = TrendRanker()
content_generator = ContentGenerator()
virality_predictor = ViralityPredictor()

def trend_node_handler(state: AgentState) -> Dict[str, Any]:
    """Node 1: Scrapes, consolidates and ranks live tech/niche topics."""
    logger.info("Executing LangGraph node: trend_node...")
    
    # If the user already provided a specific topic, skip collection
    if state.get("topic") and state.get("trend_score", 0.0) > 0.0:
        logger.info(f"User supplied target topic detected: {state['topic']}. Skipping scraping.")
        return {
            "category": state.get("category", "tech"),
            "trend_score": state.get("trend_score", 85.0)
        }
        
    try:
        # Scrape raw news feeds
        reddit_raw = reddit_client.fetch_trends(limit=5)
        youtube_raw = youtube_client.fetch_trends(max_results=5)
        rss_raw = rss_client.fetch_trends(limit=4)
        
        # Concat lists
        all_raw = reddit_raw + youtube_raw + rss_raw
        
        # Rank topics
        ranked = trend_ranker.rank_trends(all_raw, limit=5)
        
        if ranked:
            top_trend = ranked[0]
            # Map source and subreddit keywords to one of the 7 standard categories
            title_l = top_trend["title"].lower()
            category = "tech"
            if "fit" in title_l or "cardi" in title_l:
                category = "fitness"
            elif "finance" in title_l or "stock" in title_l or "saving" in title_l:
                category = "finance"
            elif "game" in title_l or "gaming" in title_l or "esport" in title_l:
                category = "gaming"
            elif "travel" in title_l or "wander" in title_l:
                category = "travel"
            elif "food" in title_l or "recipe" in title_l:
                category = "food"
            elif "style" in title_l or "dress" in title_l or "fashion" in title_l:
                category = "fashion"
                
            return {
                "topic": top_trend["topic"],
                "category": category,
                "trend_score": float(top_trend["trend_score"])
            }
            
    except Exception as e:
        logger.error(f"Error in trend discovery node: {e}")
        
    # Standard safety fallback
    return {
        "topic": "AI agents are taking over coding in 2026",
        "category": "tech",
        "trend_score": 88.0
    }

def script_node_handler(state: AgentState) -> Dict[str, Any]:
    """Node 2: Generates a premium 30-60s script with standard Hook/Story/Insights/CTA structure."""
    logger.info("Executing LangGraph node: script_node...")
    topic = state.get("topic", "AI agents are taking over coding in 2026")
    category = state.get("category", "tech")
    
    script_text = content_generator.generate_script(topic, category)
    return {"script": script_text}

def caption_node_handler(state: AgentState) -> Dict[str, Any]:
    """Node 3: Generates professional LinkedIn posts and catchy Instagram captions."""
    logger.info("Executing LangGraph node: caption_node...")
    topic = state.get("topic", "AI agents are taking over coding in 2026")
    category = state.get("category", "tech")
    script = state.get("script", "")
    
    post_data = content_generator.generate_posts(topic, script, category)
    return {
        "linkedin_post": post_data["linkedin"],
        "instagram_caption": post_data["instagram"],
        "hashtags": post_data["hashtags"]
    }

def virality_node_handler(state: AgentState) -> Dict[str, Any]:
    """Node 4: Assesses structural traits of script to forecast views, likes, shares, and virality score."""
    logger.info("Executing LangGraph node: virality_node...")
    script = state.get("script", "")
    trend_score = state.get("trend_score", 80.0)
    category = state.get("category", "tech")
    hashtags = state.get("hashtags", [])
    
    prediction = virality_predictor.predict(
        script_text=script,
        trend_score=trend_score,
        category=category,
        hashtags=hashtags
    )
    
    return {
        "virality_score": prediction["virality_score"],
        "expected_views": prediction["expected_views"],
        "expected_likes": prediction["expected_likes"],
        "expected_shares": prediction["expected_shares"],
        "insights": prediction["insights"]
    }

if LANGGRAPH_ACTIVE:
    # Build StateGraph
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("trend", trend_node_handler)
    workflow.add_node("script", script_node_handler)
    workflow.add_node("caption", caption_node_handler)
    workflow.add_node("virality", virality_node_handler)
    
    # Set Entry Point
    workflow.set_entry_point("trend")
    
    # Connect Nodes Sequentially
    workflow.add_edge("trend", "script")
    workflow.add_edge("script", "caption")
    workflow.add_edge("caption", "virality")
    workflow.add_edge("virality", END)
    
    # Compile Graph
    agent_executor = workflow.compile()
    logger.info("LangGraph Agent Pipeline compiled successfully.")
else:
    agent_executor = None
    logger.info("LangGraph package not found. Compiled graph set to None; fallback sequential runner is active.")

def run_agent_pipeline(custom_topic: str = None, category: str = "tech", custom_trend_score: float = None) -> Dict[str, Any]:
    """Triggers the full autonomous or customizable viral campaign generation agent."""
    initial_state = {
        "topic": custom_topic or "",
        "category": category,
        "trend_score": custom_trend_score or 0.0,
        "script": "",
        "linkedin_post": "",
        "instagram_caption": "",
        "hashtags": [],
        "virality_score": 0.0,
        "expected_views": 0,
        "expected_likes": 0,
        "expected_shares": 0,
        "insights": [],
        "error": ""
    }
    
    try:
        if LANGGRAPH_ACTIVE and agent_executor is not None:
            final_state = agent_executor.invoke(initial_state)
            return final_state
        else:
            logger.info("Executing pipeline sequentially (no LangGraph dependency)...")
            # Step 1: Trend
            trend_res = trend_node_handler(initial_state)
            initial_state.update(trend_res)
            
            # Step 2: Script
            script_res = script_node_handler(initial_state)
            initial_state.update(script_res)
            
            # Step 3: Caption
            caption_res = caption_node_handler(initial_state)
            initial_state.update(caption_res)
            
            # Step 4: Virality
            virality_res = virality_node_handler(initial_state)
            initial_state.update(virality_res)
            
            return initial_state
    except Exception as e:
        logger.error(f"Failed to execute LangGraph Agent: {e}")
        return {
            **initial_state,
            "error": str(e)
        }

if __name__ == "__main__":
    # Test script
    print("Testing compiled agent executor...")
    res = run_agent_pipeline()
    print(f"Discovered Trend Topic: {res['topic']}")
    print(f"Script Hook: {res['script'][:80]}...")
    print(f"Expected Views: {res['expected_views']}")
    print(f"Predicted Virality Score: {res['virality_score']:.1f}")
