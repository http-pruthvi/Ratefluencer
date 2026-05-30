import os
import json
import logging
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ratefluencer.database")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ratefluencer.db")

# Dynamic database fallback logic
try:
    engine = create_engine(DATABASE_URL)
    # Check connection
    with engine.connect() as conn:
        pass
    logger.info(f"Successfully connected to database using: {DATABASE_URL}")
except Exception as e:
    logger.warning(f"Failed to connect to primary DB {DATABASE_URL}: {e}. Falling back to SQLite local db.")
    DATABASE_URL = "sqlite:///./ratefluencer.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class InfluencerORM(Base):
    __tablename__ = "influencers"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    platform = Column(String, default="Instagram")
    followers = Column(Integer, nullable=False)
    following = Column(Integer, nullable=False)
    posts_count = Column(Integer, nullable=False)
    engagement_rate = Column(Float, nullable=False) # e.g. 0.045 for 4.5%
    avg_likes = Column(Float, nullable=False)
    avg_comments = Column(Float, nullable=False)
    avg_shares = Column(Float, nullable=False)
    avg_saves = Column(Float, nullable=False)
    posting_frequency = Column(Float, nullable=False) # posts per week
    audience_age_18_24_pct = Column(Float, nullable=False) # percentage
    audience_india_pct = Column(Float, nullable=False) # percentage
    is_fake_flag = Column(Boolean, default=False)
    follower_history_30d = Column(Text, nullable=False) # JSON list serialized as text
    content_category = Column(String, nullable=False) # e.g., 'tech', 'finance'
    bio = Column(Text, nullable=True) # Creator bio for Sentence-BERT semantic search

    def to_dict(self):
        """Convert ORM object to python dict."""
        return {
            "id": self.id,
            "username": self.username,
            "platform": self.platform,
            "followers": self.followers,
            "following": self.following,
            "posts_count": self.posts_count,
            "engagement_rate": self.engagement_rate,
            "avg_likes": self.avg_likes,
            "avg_comments": self.avg_comments,
            "avg_shares": self.avg_shares,
            "avg_saves": self.avg_saves,
            "posting_frequency": self.posting_frequency,
            "audience_age_18_24_pct": self.audience_age_18_24_pct,
            "audience_india_pct": self.audience_india_pct,
            "is_fake_flag": self.is_fake_flag,
            "follower_history_30d": json.loads(self.follower_history_30d) if self.follower_history_30d else [],
            "content_category": self.content_category,
            "bio": self.bio
        }

def init_db():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")

def get_db():
    """Dependency for API routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
