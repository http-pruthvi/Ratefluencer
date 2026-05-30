import os
import numpy as np
import logging
from typing import List, Union

logger = logging.getLogger("ratefluencer.embedder")

class Embedder:
    """Handles text vectorization for semantic searching and brand matching."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.use_fallback = False
        
        # Standard offline pre-fit corpus to warm up fallback TF-IDF vocab
        self.corpus = [
            "High performance sportswear and daily workout training gear.",
            "AI-powered developer productivity automation and code testing SaaS.",
            "Personal finance, index fund investing, stock portfolios, and budgeting guides.",
            "Autonomous AI coding agents, DevOps terminal prompt planners, and python tutorials.",
            "Classic capsule wardrobes, sustainable clothing choices, and vintage minimalist fashion.",
            "Competitive esports gaming tournaments, live streams, mechanical keyboards, and reviews.",
            "Airtight meal preparation containers, calorie-conscious high-protein baking tray recipes.",
            "Slow travel remote work visas, co-working spaces, and city guides for nomads."
        ]
        
        # Instantiate fallback vectorizer and pre-fit it on the corpus so it is ready
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self.vectorizer = TfidfVectorizer(stop_words='english')
            self.vectorizer.fit(self.corpus)
        except Exception as e:
            logger.warning(f"Failed to pre-fit sklearn TfidfVectorizer: {e}")
            self.vectorizer = None
        
        # Check if we should force fallback (e.g. offline testing speed)
        force_fallback = os.getenv("FORCE_TFIDF_FALLBACK", "false").lower() == "true"
        
        if not force_fallback:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading SentenceTransformer model: {model_name}...")
                self.model = SentenceTransformer(model_name)
                logger.info("SentenceTransformer loaded successfully.")
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer: {e}. Activating premium TF-IDF/frequency fallback.")
                self.use_fallback = True
        else:
            logger.info("FORCE_TFIDF_FALLBACK active in environment. Bypassing SentenceTransformer.")
            self.use_fallback = True

    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Converts a single string or a list of strings into dense embeddings (numpy array)."""
        if isinstance(texts, str):
            texts = [texts]
            
        if not self.use_fallback and self.model is not None:
            try:
                embeddings = self.model.encode(texts, show_progress_bar=False)
                return np.array(embeddings, dtype=np.float32)
            except Exception as e:
                logger.warning(f"Error during SentenceTransformer encoding: {e}. Falling back to TF-IDF.")
                self.use_fallback = True
                
        # Premium Offline TF-IDF Fallback Vectorizer using sklearn
        try:
            # Use stable pre-fitted vocabulary transform to keep dimensions aligned!
            vectors_sparse = self.vectorizer.transform(texts)
            vectors = vectors_sparse.toarray().astype(np.float32)
            return vectors
        except Exception as e:
            logger.warning(f"Sklearn TF-IDF fallback failed: {e}. Using basic count vectorizer.")
            
            # In-memory keyword matching fallback as last resort
            vocabulary = [
                "ai", "tech", "coding", "software", "development", "personal", "finance", "investing",
                "stocks", "budgeting", "wealth", "fitness", "coaching", "training", "gym", "muscle",
                "yoga", "fashion", "styling", "vintage", "thrift", "streetwear", "recipes", "pastry",
                "cooking", "restaurant", "food", "travel", "nomad", "adventure", "luxury", "gaming",
                "streamer", "keyboard", "esports", "minimalist"
            ]
            vectors = []
            for text in texts:
                text_lower = text.lower()
                vec = []
                for word in vocabulary:
                    count = text_lower.count(word)
                    vec.append(float(count))
                vec.append(float(len(text)) / 100.0)
                
                arr = np.array(vec, dtype=np.float32)
                norm = np.linalg.norm(arr)
                if norm > 0:
                    arr = arr / norm
                vectors.append(arr)
                
            return np.array(vectors, dtype=np.float32)

    def calculate_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculates cosine similarity between two 1D vectors."""
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            v1 = vec1.reshape(1, -1)
            v2 = vec2.reshape(1, -1)
            return float(cosine_similarity(v1, v2)[0][0])
        except Exception:
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return float(np.dot(vec1, vec2) / (norm1 * norm2))

