import os
import csv
import json
import random
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

# Import DB configurations
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from api.database import init_db, SessionLocal, InfluencerORM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ratefluencer.generator")

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

CATEGORIES = ["tech", "finance", "fitness", "fashion", "food", "travel", "gaming"]

BIO_TEMPLATES = {
    "tech": [
        "Software Engineer sharing the latest in AI, coding tutorials, and tech reviews. Let's build the future! 🚀",
        "Gadget enthusiast, reviewer, and minimalist workspace curator. Business: techreviews@inbox.com",
        "Deep diving into cybersecurity, web development, and cloud computing. Code daily. 💻",
        "Helping you navigate the digital landscape. Web3, DevOps, and future tech insights.",
        "Founder & tech builder. Building cool apps and discussing SaaS growth strategies."
    ],
    "finance": [
        "Personal finance coach helping you invest smarter, save more, and build generational wealth. 📈",
        "Ex-investment banker explaining economics, stocks, and crypto in plain English. Disclaimer: Not financial advice.",
        "Budgeting hacks and passive income strategies for millennials. Let's get financially free! 💸",
        "Real estate investor, dividend growth enthusiast, and credit score strategist.",
        "Financial freedom advocate. Helping you escape the 9-to-5 grind through smart investing."
    ],
    "fitness": [
        "Certified personal trainer | Online coaching available. Empowering you to build strength and confidence. 💪",
        "Yoga teacher, plant-based nutrition enthusiast, and mindfulness advocate. Breath and move.",
        "Calisthenics athlete. No gym, no excuses. Just pure dedication and gravity-defying moves. 🤸‍♂️",
        "Helping busy professionals lose fat and gain muscle. Science-based training & macro-friendly meals.",
        "Marathon runner, hybrid athlete, and wellness speaker. Run with purpose."
    ],
    "fashion": [
        "Stylist & fashion enthusiast. Curating daily outfit inspiration, vintage finds, and capsule wardrobes. 👗",
        "Minimalist menswear, grooming tips, and lifestyle aesthetics. Business inquiries: contact@style.com",
        "Thrift store champion and sustainable style advocate. Upcycling old clothing into new trends. 🌱",
        "Streetwear culture, sneaker reviews, and urban fashion lookbooks. Stay fly.",
        "Creative director. Sharing high-fashion editorial concepts, makeup tips, and seasonal lookbooks."
    ],
    "food": [
        "Recipe developer sharing quick, easy, and delicious 30-minute meals for family dinners. 🍳",
        "Professional pastry chef | Baking tutorials and sweet treats. Life is short, eat dessert first! 🧁",
        "Street food hunter, culinary traveler, and restaurant reviewer. Eating my way around the world. 🌍",
        "Plant-based food blogger making vegan recipes that actually taste amazing. 🌱",
        "Gourmet cooking made simple. Let's make restaurant-quality dishes in your home kitchen."
    ],
    "travel": [
        "Digital nomad traveling full-time. Documenting hidden gems, budget tips, and solo female travel. ✈️",
        "Adventure photographer capturing the world's most epic landscapes, hikes, and road trips. 🏔️",
        "Luxury hotel reviewer, flight hacker, and cultural explorer. 80+ countries and counting.",
        "Van life creator traveling across North America with my dog. Living on the open road. 🚐",
        "Travel smarter. Sharing destination guides, packing checklists, and local secrets."
    ],
    "gaming": [
        "FPS competitive player and streamer. Daily highlights, game patch analysis, and pro tips. 🎮",
        "Indie game developer & reviewer. Behind-the-scenes game creation and gameplay analysis.",
        "Cozy gamer sharing wholesome reviews, Stardew Valley layouts, and Nintendo setup guides. 🍄",
        "Speedrunner, gaming historian, and RPG enthusiast. Completing games 100% so you don't have to.",
        "E-sports caster and tech setup reviewer. Streaming live every Mon-Wed-Fri."
    ]
}

def generate_synthetic_data(num_records=1000):
    """Generates synthetic influencer records with realistic features & anomalies."""
    logger.info(f"Generating {num_records} synthetic influencer records...")
    
    records = []
    
    # 90% authentic, 10% fake anomalies
    num_fake = int(num_records * 0.10)
    num_authentic = num_records - num_fake
    
    for i in range(num_records):
        is_fake = (i < num_fake)
        category = random.choice(CATEGORIES)
        bio = random.choice(BIO_TEMPLATES[category])
        username = f"@{category}_creator_{i}" if not is_fake else f"@{category}_growth_hacks_{i}"
        
        # Follower ranges: 1K to 5M (log normal distribution for realistic skew)
        followers = int(np.random.lognormal(mean=11.5, sigma=1.5))
        followers = max(1000, min(followers, 10000000)) # bound between 1K and 10M
        
        if is_fake:
            # Fake: high followers, low following, or massive bot numbers
            following = int(random.uniform(50, 400))
            posts_count = int(random.uniform(10, 80))
            
            # Anomaly: low engagement relative to followers
            engagement_rate = random.uniform(0.0005, 0.003) # 0.05% to 0.3%
            avg_likes = followers * engagement_rate * random.uniform(0.8, 0.95)
            avg_comments = followers * engagement_rate * random.uniform(0.05, 0.2)
            
            # Fake follower profiles have low shares and saves
            avg_shares = avg_likes * random.uniform(0.01, 0.03)
            avg_saves = avg_likes * random.uniform(0.01, 0.03)
            
            posting_frequency = random.uniform(0.1, 1.5) # Posts very rarely or inconsistently
            
            # Random follower spikes in time-series
            base_f = followers - 50000 if followers > 60000 else 1000
            history = []
            current_f = base_f
            for day in range(30):
                if day == 15:
                    current_f += int(followers * 0.8) # massive sudden spike of bots
                else:
                    current_f += int(random.uniform(-100, 100))
                history.append(max(100, current_f))
            
            audience_age_18_24_pct = random.uniform(10.0, 40.0)
            audience_india_pct = random.uniform(60.0, 95.0) # concentrated in bot farms
            
        else:
            # Authentic creators: following and posts are organic
            following = int(random.uniform(200, 3000))
            posts_count = int(random.uniform(100, 3000))
            
            # Engagement rate naturally decreases as follower count increases
            if followers < 20000:
                engagement_rate = random.uniform(0.04, 0.15) # 4% - 15%
            elif followers < 200000:
                engagement_rate = random.uniform(0.02, 0.07) # 2% - 7%
            else:
                engagement_rate = random.uniform(0.008, 0.03) # 0.8% - 3%
                
            avg_likes = followers * engagement_rate * random.uniform(0.85, 0.92)
            avg_comments = followers * engagement_rate * random.uniform(0.08, 0.15)
            avg_shares = avg_likes * random.uniform(0.05, 0.25)
            avg_saves = avg_likes * random.uniform(0.05, 0.20)
            
            posting_frequency = random.uniform(1.5, 10.0) # Posts 1-10 times/week
            
            # Natural steady growth history
            growth_rate_daily = random.uniform(-0.001, 0.003)
            history = []
            current_f = int(followers * (1 - growth_rate_daily * 30))
            for day in range(30):
                current_f = int(current_f * (1 + growth_rate_daily + random.uniform(-0.001, 0.0015)))
                history.append(max(100, current_f))
            
            audience_age_18_24_pct = random.uniform(25.0, 75.0)
            audience_india_pct = random.uniform(15.0, 45.0)

        # Force correct types
        record = {
            "username": username,
            "platform": "Instagram",
            "followers": int(followers),
            "following": int(following),
            "posts_count": int(posts_count),
            "engagement_rate": float(engagement_rate),
            "avg_likes": float(avg_likes),
            "avg_comments": float(avg_comments),
            "avg_shares": float(avg_shares),
            "avg_saves": float(avg_saves),
            "posting_frequency": float(posting_frequency),
            "audience_age_18_24_pct": float(audience_age_18_24_pct),
            "audience_india_pct": float(audience_india_pct),
            "is_fake_flag": bool(is_fake),
            "follower_history_30d": json.dumps(history),
            "content_category": category,
            "bio": bio
        }
        records.append(record)
        
    return records

def create_brands_json():
    """Generates standard brand targets for brand matcher similarity searching."""
    brands = [
        {
            "id": 1,
            "name": "FitTrack Pro",
            "industry": "fitness",
            "aesthetic": "High energy, athletic, clean, scientific",
            "description": "Premium wearable brand focusing on fitness trackers, heart rate monitors, and metabolic state coaching. Target audience is active athletes, gym-goers, and bio-hackers."
        },
        {
            "id": 2,
            "name": "DevFlow AI",
            "industry": "tech",
            "aesthetic": "Futuristic, sleek, dark-mode, developer-oriented",
            "description": "AI-powered developer productivity tool that autocomplete code, formats PRs, and creates instant integration plans. Target audience is software engineers, tech startup founders, and students."
        },
        {
            "id": 3,
            "name": "SustainaThread",
            "industry": "fashion",
            "aesthetic": "Earth tones, minimalist, organic, cozy",
            "description": "Eco-friendly capsule wardrobe clothing line utilizing organic hemp, linen, and recycled plastics. Target audience is conscious shoppers, vintage enthusiasts, and minimalists."
        },
        {
            "id": 4,
            "name": "FinSimple",
            "industry": "finance",
            "aesthetic": "Modern, trustworthy, vibrant, educational",
            "description": "Zero-fee investing and savings app with micro-investing and automated round-ups. Target audience is Gen Z and millennials starting their personal finance journey."
        },
        {
            "id": 5,
            "name": "SpiceRoute MealPrep",
            "industry": "food",
            "aesthetic": "Colorful, high contrast, family-friendly, tasty",
            "description": "Fast and gourmet meal-prep delivery box providing organic ingredients and global recipes in under 30 minutes. Target audience is busy professionals, healthy eaters, and home chefs."
        },
        {
            "id": 6,
            "name": "ApexGamer",
            "industry": "gaming",
            "aesthetic": "RGB, neon, high contrast, competitive",
            "description": "Pro-grade gaming mechanical keyboards, customizable mice, and ergonomic gaming chairs. Target audience is streamers, esports competitive players, and heavy PC gamers."
        },
        {
            "id": 7,
            "name": "RoamFree Gear",
            "industry": "travel",
            "aesthetic": "Rugged, raw, beautiful wilderness, cinematic",
            "description": "Ultra lightweight, modular travel backpacks and weather-proof outdoor gear. Target audience is digital nomads, hikers, backpackers, and travel vloggers."
        }
    ]
    
    path = "c:/Users/pruthvi/Desktop/projects/Ratefluencer/data/synthetic/brands.json"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(brands, f, indent=4)
    logger.info(f"Created brands target database at {path}")

def create_mock_scripts_json():
    """Creates cached content scripts for flawless demo execution when Anthropic key is missing."""
    mock_scripts = {
        "tech": {
            "topic": "AI agents are taking over coding in 2026",
            "script": "[HOOK]\n(0-5s): Pointing at screen with shocked face. \"Stop writing code by hand! In 2026, AI agents are officially writing 80% of production-ready software!\"\n\n[STORY]\n(5-25s): Cut to sitting at desk typing rapidly. \"Here is what's crazy. Two years ago, we used AI for code autocompletes. Today, companies are deploying autonomous coding frameworks that plan, build, test, and containerize complete apps from a single terminal prompt!\"\n\n[INSIGHTS]\n(25-50s): Graphic of Developer vs Agent workflow. \"This doesn't mean developer jobs are dead. It means you need to shift from a code writer to a system architect. Focus on prompt design, testing frameworks, and multi-agent system orchestration!\"\n\n[CTA]\n(50-60s): Smile and point down. \"Are you building with agents yet? Let me know in the comments and hit follow for daily tech deep dives!\"",
            "linkedin": "The software engineering landscape in 2026 is undergoing a paradigm shift. We are moving from 'AI-assisted coding' to 'autonomous software agents'.\n\nRecent data shows that over 80% of standard repository scaffolding and test generation is now entirely orchestrated by multi-agent developer flows. As systems architects, our role is transitioning from writing syntax to designing workflows, reviewing agent outputs, and ensuring safety boundaries.\n\nAre you integrating AI agents into your development stack? Let's discuss in the comments!\n\n#SoftwareEngineering #AIAgents #FutureOfWork #DevOps #Coding",
            "instagram": "AI agents are changing coding forever in 2026! 🚀 Stop writing basic boilerplate code and start designing systems. The developers who thrive tomorrow are the ones who orchestrate agents today. \n\nCheck out the full breakdown in my bio! 🔗\n\n#ai #coding #programmer #tech #softwaredeveloper #webdev #starthere #computerscience #softwareengineer #trends",
            "hashtags": ["#ai", "#coding", "#programmer", "#tech", "#softwaredeveloper"]
        },
        "fitness": {
            "topic": "Zone 2 Cardio is the ultimate fat burning hack",
            "script": "[HOOK]\n(0-5s): Running on a treadmill comfortably. \"You are running too fast! If you want to burn fat, stop sprinting and start moving at a conversational pace. Here is why.\"\n\n[STORY]\n(5-25s): Diagram showing energy pathways. \"When you train in Zone 2 cardio, your body relies almost entirely on fat oxidation rather than carbohydrates. This means your cells are optimized to burn fat stores for fuel directly.\"\n\n[INSIGHTS]\n(25-50s): Show smartwatch screen. \"Keep your heart rate at 60-70% of your max. You should be able to hold a full conversation without gasping. 150 minutes a week of this is the ultimate longevity and body recomposition hack!\"\n\n[CTA]\n(50-60s): Stepping off. \"Save this video for your next gym session and follow for science-backed fitness tips!\"",
            "linkedin": "Optimal physical health is the foundation of peak professional performance. One of the most under-utilized fitness strategies in high-stress corporate environments is Zone 2 training.\n\nZone 2 cardio (conversational pace) improves mitochondrial density, lowers resting heart rate, and significantly increases metabolic flexibility. By prioritizing low-intensity steady-state (LISS) exercise, we build the endurance necessary to handle high cognitive loads without burning out.\n\nWhat is your preferred recovery training method? \n\n#FitnessScience #ExecutiveHealth #Zone2Cardio #CorporateWellness #Biohacking",
            "instagram": "You're running too fast! 🛑 Burn fat and boost longevity with Zone 2 cardio. Conversational pace, maximum fat oxidation, and zero burnout. \n\nSave this for your next gym day! 💪\n\n#fitness #zone2 #cardio #gymmotivation #healthylifestyle #fatloss #workouttips #fitfam #sciencebasedfitness",
            "hashtags": ["#fitness", "#zone2", "#cardio", "#gymmotivation", "#healthylifestyle"]
        }
    }
    
    path = "c:/Users/pruthvi/Desktop/projects/Ratefluencer/data/synthetic/mock_scripts.json"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(mock_scripts, f, indent=4)
    logger.info(f"Created mock scripts library at {path}")

def save_and_insert():
    """Main execution function to generate, save as CSV, and insert into DB."""
    # Ensure synthetic folder exists
    os.makedirs("c:/Users/pruthvi/Desktop/projects/Ratefluencer/data/synthetic", exist_ok=True)
    
    # Generate records
    records = generate_synthetic_data(1000)
    
    # Save as CSV
    csv_path = "c:/Users/pruthvi/Desktop/projects/Ratefluencer/data/synthetic/influencers.csv"
    keys = records[0].keys()
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(records)
    logger.info(f"Successfully saved synthetic dataset to CSV: {csv_path}")
    
    # Initialize DB schema
    init_db()
    
    # Insert records to Database
    db: Session = SessionLocal()
    try:
        # Delete existing to prevent duplication
        db.query(InfluencerORM).delete()
        
        db_records = [InfluencerORM(**rec) for rec in records]
        db.bulk_save_objects(db_records)
        db.commit()
        logger.info(f"Successfully inserted {len(db_records)} records into the database.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error inserting into database: {e}")
    finally:
        db.close()
        
    # Generate supporting JSON files
    create_brands_json()
    create_mock_scripts_json()

if __name__ == "__main__":
    save_and_insert()
