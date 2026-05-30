import os
import json
import logging
from models.track2.content_generator import ContentGenerator

logger = logging.getLogger("ratefluencer.agent.caption_node")

def run_caption_node(topic: str, script: str, category: str) -> dict:
    """Generates professional LinkedIn posts and Instagram captions using Claude (or mock fallback from mock_scripts.json)."""
    # Initialize the generator which checks for ANTHROPIC_API_KEY
    generator = ContentGenerator()
    
    # Generate the posts
    posts = generator.generate_posts(topic, script, category)
    return posts
