import os
import json
import logging
from models.track2.content_generator import ContentGenerator

logger = logging.getLogger("ratefluencer.agent.script_node")

def run_script_node(topic: str, category: str) -> str:
    """Generates a premium video script using Claude (or mock fallback from mock_scripts.json)."""
    # Initialize the generator which checks for ANTHROPIC_API_KEY
    generator = ContentGenerator()
    
    # Generate the script
    script = generator.generate_script(topic, category)
    return script
