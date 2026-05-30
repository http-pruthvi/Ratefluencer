import os
import json
import logging
import random
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("ratefluencer.generator")

class ContentGenerator:
    """Uses Anthropic Claude API to generate viral scripts, LinkedIn posts, and Instagram captions."""
    
    def __init__(self, mock_json_path: str = "c:/Users/pruthvi/Desktop/projects/Ratefluencer/data/synthetic/mock_scripts.json"):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.mock_json_path = mock_json_path
        self.claude_active = False
        
        if self.api_key:
            try:
                from anthropic import Anthropic
                # Validate client setup
                self.client = Anthropic(api_key=self.api_key)
                self.claude_active = True
                logger.info("Anthropic Claude client initialized successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic client: {e}. Switching to mock templates.")
        else:
            logger.info("Anthropic API key missing. Content generator running in mock template mode.")
            
        self.mock_library = {}
        self.load_mock_library()

    def load_mock_library(self):
        """Loads cached high-quality mock scripts and templates."""
        if os.path.exists(self.mock_json_path):
            with open(self.mock_json_path, "r") as f:
                self.mock_library = json.load(f)
            logger.info(f"Loaded {len(self.mock_library)} mock categories from library.")
        else:
            logger.warning(f"Mock scripts library not found at {self.mock_json_path}. Instantiating default in-memory copy.")
            self.mock_library = {
                "tech": {
                    "topic": "Future Tech",
                    "script": "[HOOK]\n(0-5s): \"Hold on, this changes everything!\"\n\n[STORY]\n(5-25s): \"AI developers are launching automated apps in 2026.\"\n\n[INSIGHTS]\n(25-50s): \"Focus on architecture, design, and testing patterns.\"\n\n[CTA]\n(50-60s): \"What do you think? Comment below and follow!\"",
                    "linkedin": "Tech is shifting rapidly. Here is why autonomous agents are the future. #Tech #AI #Coding",
                    "instagram": "AI is changing software development! 🚀 Check out the details in bio. #tech #ai #developer",
                    "hashtags": ["#tech", "#ai", "#developer"]
                }
            }

    def generate_script(self, topic: str, category: str) -> str:
        """Generates a high-impact 30-60 second video script using Claude (or mock fallback)."""
        category = category.lower().strip()
        if category not in self.mock_library:
            # Fallback to tech if category is not mapped
            category = "tech"
            
        if self.claude_active:
            try:
                prompt = (
                    f"Generate a viral 30-60 second vertical video script about the topic: '{topic}' in the niche: '{category}'.\n"
                    f"Structure the script EXACTLY in this format:\n"
                    f"[HOOK] (0-5s attention grabber)\n"
                    f"[STORY] (5-25s narrative context)\n"
                    f"[INSIGHTS] (25-50s key value/lesson)\n"
                    f"[CTA] (50-60s call to action)\n\n"
                    f"Make the writing punchy, modern, fast-paced, and highly optimized for Gen Z and millennial viewers."
                )
                
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    temperature=0.8,
                    system="You are an expert viral content strategist and YouTube Shorts/TikTok writer.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                script_text = message.content[0].text
                return script_text
            except Exception as e:
                logger.error(f"Claude API script generation failed: {e}. Falling back to template matching.")

        # High-fidelity mock fallback with topic keyword swapping
        logger.info(f"Using pre-cached template for {category} script...")
        template_obj = self.mock_library.get(category, self.mock_library["tech"])
        script_template = template_obj["script"]
        
        # Simple dynamic keyword injection to customize the mock to the user's actual topic
        # Replace template hook text with the specific topic
        customized_script = script_template
        original_topic = template_obj.get("topic", "")
        if original_topic:
            customized_script = customized_script.replace(original_topic, topic)
            customized_script = customized_script.replace(original_topic.lower(), topic.lower())
            
        return customized_script

    def generate_posts(self, topic: str, script: str, category: str) -> Dict[str, Any]:
        """Generates both a professional LinkedIn post and a casual Instagram caption with hashtags."""
        category = category.lower().strip()
        if category not in self.mock_library:
            category = "tech"
            
        if self.claude_active:
            try:
                prompt = (
                    f"Based on this video script:\n'{script}'\n\n"
                    f"Generate two items:\n"
                    f"1. A high-engagement LinkedIn post (200-300 words, structured with spaces, professional yet conversational tone, 3-5 relevant hashtags).\n"
                    f"2. An Instagram caption (50-80 words, catchy and casual, includes an obvious CTA, accompanied by 10-15 highly trending hashtags).\n\n"
                    f"Return the response in structured JSON format with keys: 'linkedin', 'instagram', and 'hashtags' (list of strings)."
                )
                
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    temperature=0.7,
                    system="You are a social media copywriter. You must reply only with a valid JSON block containing 'linkedin', 'instagram', and 'hashtags'. Do not add comments or conversational prefixes.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                # Parse JSON output
                res_text = message.content[0].text.strip()
                # strip code block enclosures if present
                if res_text.startswith("```json"):
                    res_text = res_text[7:]
                if res_text.endswith("```"):
                    res_text = res_text[:-3]
                    
                data = json.loads(res_text.strip())
                return {
                    "linkedin": data.get("linkedin", ""),
                    "instagram": data.get("instagram", ""),
                    "hashtags": data.get("hashtags", [])
                }
            except Exception as e:
                logger.error(f"Claude API post generation failed: {e}. Falling back to template matching.")

        # High-fidelity mock fallback with topic keyword swapping
        logger.info(f"Using pre-cached template for {category} posts...")
        template_obj = self.mock_library.get(category, self.mock_library["tech"])
        
        linkedin = template_obj["linkedin"]
        instagram = template_obj["instagram"]
        hashtags = template_obj.get("hashtags", ["#viral", "#creator", f"#{category}"])
        
        original_topic = template_obj.get("topic", "")
        if original_topic:
            linkedin = linkedin.replace(original_topic, topic).replace(original_topic.lower(), topic.lower())
            instagram = instagram.replace(original_topic, topic).replace(original_topic.lower(), topic.lower())
            
        return {
            "linkedin": linkedin,
            "instagram": instagram,
            "hashtags": hashtags
        }

if __name__ == "__main__":
    generator = ContentGenerator()
    script = generator.generate_script("Next-gen AI agents in 2026", "tech")
    posts = generator.generate_posts("Next-gen AI agents in 2026", script, "tech")
    print("--- SCRIPT ---")
    print(script)
    print("\n--- LINKEDIN ---")
    print(posts["linkedin"])
