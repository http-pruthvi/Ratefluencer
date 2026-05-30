import os
import json
import logging
import numpy as np
from typing import Dict, Any, List, Tuple

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from processing.embedder import Embedder
from api.database import SessionLocal, InfluencerORM

logger = logging.getLogger("ratefluencer.brand_matcher")

class BrandMatcher:
    """Matches brands to creators semantically using SBERT vector embeddings."""
    
    def __init__(self, brands_json_path: str = "c:/Users/pruthvi/Desktop/projects/Ratefluencer/data/synthetic/brands.json"):
        self.brands_json_path = brands_json_path
        self.embedder = Embedder()
        self.brands = []
        self.brand_embeddings = None
        self.load_brands()

    def load_brands(self):
        """Loads brand campaigns and pre-embeds their descriptions."""
        if os.path.exists(self.brands_json_path):
            with open(self.brands_json_path, "r") as f:
                self.brands = json.load(f)
            logger.info(f"Loaded {len(self.brands)} brand profiles for semantic matching.")
            
            # Embed all brand descriptions
            descriptions = [b["description"] for b in self.brands]
            self.brand_embeddings = self.embedder.encode(descriptions)
        else:
            logger.warning(f"Brands database not found at {self.brands_json_path}. Mocking brand templates.")
            self.brands = [
                {"id": 1, "name": "FitCorp", "description": "High performance sportswear and daily workout training gear."},
                {"id": 2, "name": "TechStart", "description": "AI-powered developer productivity automation and code testing SaaS."}
            ]
            self.brand_embeddings = self.embedder.encode([b["description"] for b in self.brands])

    def get_top_brands_for_creator(self, creator_bio: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """Finds the top N brands that match a creator's bio description."""
        if not creator_bio:
            return []
            
        creator_vector = self.embedder.encode(creator_bio)[0]
        
        scores = []
        for i, brand in enumerate(self.brands):
            brand_vector = self.brand_embeddings[i]
            similarity = self.embedder.calculate_similarity(creator_vector, brand_vector)
            
            # Scale similarity [0, 1] to 0-100 score
            # SBERT cosine similarities often sit between 0.2 and 0.8
            score = 10.0 + similarity * 90.0
            if similarity < 0.15:
                score = similarity * 50.0
                
            scores.append({
                "brand_id": brand["id"],
                "name": brand["name"],
                "industry": brand.get("industry", "other"),
                "aesthetic": brand.get("aesthetic", "Standard"),
                "description": brand["description"],
                "match_score": float(np.clip(score, 0.0, 100.0)),
                "raw_similarity": float(similarity)
            })
            
        # Sort descending by match score
        scores.sort(key=lambda x: x["match_score"], reverse=True)
        return scores[:top_n]

    def get_top_creators_for_brand(self, brand_description: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """Finds the top N creators from the database that match a brand campaign brief."""
        brand_vector = self.embedder.encode(brand_description)[0]
        
        # Pull all influencers from the database
        db = SessionLocal()
        try:
            creators = db.query(InfluencerORM).all()
            if not creators:
                logger.warning("No creators in database to match against.")
                return []
                
            bios = [c.bio or "" for c in creators]
            usernames = [c.username for c in creators]
            
            # Embed all creator bios
            creator_embeddings = self.embedder.encode(bios)
            
            matches = []
            for i, creator in enumerate(creators):
                creator_vector_i = creator_embeddings[i]
                similarity = self.embedder.calculate_similarity(brand_vector, creator_vector_i)
                
                # Scale to 0-100
                score = 15.0 + similarity * 85.0
                
                matches.append({
                    "username": creator.username,
                    "platform": creator.platform,
                    "followers": creator.followers,
                    "content_category": creator.content_category,
                    "bio": creator.bio,
                    "match_score": float(np.clip(score, 0.0, 100.0)),
                    "raw_similarity": float(similarity)
                })
                
            matches.sort(key=lambda x: x["match_score"], reverse=True)
            return matches[:top_n]
            
        except Exception as e:
            logger.error(f"Error matching creators for brand: {e}")
            return []
        finally:
            db.close()

if __name__ == "__main__":
    # Test script
    matcher = BrandMatcher()
    
    test_bio = "Building high-growth AI products, coding daily in Python, and reviewing standard software developer setups."
    matches = matcher.get_top_brands_for_creator(test_bio, top_n=3)
    print("Top Brands for Creator:")
    for match in matches:
        print(f"- {match['name']} ({match['industry']}): Score = {match['match_score']:.1f}")
        
    test_brief = "We are seeking fitness models and active athletes to advertise our smart heart rate monitors."
    print("\nTop Creators for Brand Brief:")
    creator_matches = matcher.get_top_creators_for_brand(test_brief, top_n=3)
    for c in creator_matches:
        print(f"- {c['username']} ({c['content_category']}): Score = {c['match_score']:.1f}")
