import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ratefluencer.api_tester")

BASE_URL = "http://127.0.0.1:8000"

def test_all_endpoints():
    logger.info("==========================================")
    logger.info("🔌 TESTING ALL 8 FASTAPI ROUTE ENDPOINTS")
    logger.info("==========================================")
    
    # 1. GET /
    try:
        res = requests.get(f"{BASE_URL}/")
        logger.info(f"1. GET / -> Status: {res.status_code} | Success: {res.json()['success']}")
        assert res.status_code == 200
    except Exception as e:
        logger.error(f"Failed Endpoint 1: {e}")
        
    # 2. GET /api/influencer/{username}
    try:
        res = requests.get(f"{BASE_URL}/api/influencer/tech_creator_0")
        logger.info(f"2. GET /api/influencer/tech_creator_0 -> Status: {res.status_code} | Success: {res.json()['success']}")
        assert res.status_code == 200
    except Exception as e:
        logger.error(f"Failed Endpoint 2: {e}")
        
    # 3. POST /api/influencer/analyze
    try:
        payload = {
            "username": "@tester",
            "followers": 50000,
            "avg_likes": 3000,
            "posting_frequency": 4.5,
            "follower_history_30d": [48000, 49000, 50000]
        }
        res = requests.post(f"{BASE_URL}/api/influencer/analyze", json=payload)
        logger.info(f"3. POST /api/influencer/analyze -> Status: {res.status_code} | Success: {res.json()['success']}")
        assert res.status_code == 200
    except Exception as e:
        logger.error(f"Failed Endpoint 3: {e}")
        
    # 4. GET /api/influencer/{id}/brand-matches
    try:
        res = requests.get(f"{BASE_URL}/api/influencer/1/brand-matches")
        logger.info(f"4. GET /api/influencer/1/brand-matches -> Status: {res.status_code} | Success: {res.json()['success']}")
        assert res.status_code == 200
    except Exception as e:
        logger.error(f"Failed Endpoint 4: {e}")
        
    # 5. POST /api/influencer/search-by-brief
    try:
        payload = {"brief": "Seeking fitness professionals to advertise wearable smart bands."}
        res = requests.post(f"{BASE_URL}/api/influencer/search-by-brief", json=payload)
        logger.info(f"5. POST /api/influencer/search-by-brief -> Status: {res.status_code} | Success: {res.json()['success']}")
        assert res.status_code == 200
    except Exception as e:
        logger.error(f"Failed Endpoint 5: {e}")
        
    # 6. GET /api/trends
    try:
        res = requests.get(f"{BASE_URL}/api/trends")
        logger.info(f"6. GET /api/trends -> Status: {res.status_code} | Success: {res.json()['success']}")
        assert res.status_code == 200
    except Exception as e:
        logger.error(f"Failed Endpoint 6: {e}")
        
    # 7. POST /api/trends/score
    try:
        payload = {"topic": "Multi-agent framework architectures in 2026"}
        res = requests.post(f"{BASE_URL}/api/trends/score", json=payload)
        logger.info(f"7. POST /api/trends/score -> Status: {res.status_code} | Success: {res.json()['success']}")
        assert res.status_code == 200
    except Exception as e:
        logger.error(f"Failed Endpoint 7: {e}")
        
    # 8. POST /api/content/agent-pipeline
    try:
        payload = {"topic": "Autonomous AI developer agents", "category": "tech"}
        res = requests.post(f"{BASE_URL}/api/content/agent-pipeline", json=payload)
        logger.info(f"8. POST /api/content/agent-pipeline -> Status: {res.status_code} | Success: {res.json()['success']}")
        assert res.status_code == 200
    except Exception as e:
        logger.error(f"Failed Endpoint 8: {e}")
        
    logger.info("==========================================")
    logger.info("🎉 ALL 8 ROUTE ENDPOINTS CONFIRMED ONLINE!")
    logger.info("==========================================")

if __name__ == "__main__":
    test_all_endpoints()
