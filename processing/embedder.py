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
        
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading SentenceTransformer model: {model_name}...")
            self.model = SentenceTransformer(model_name)
            logger.info("SentenceTransformer loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer: {e}. Activating premium TF-IDF/frequency fallback.")
            self.use_fallback = True
            self.vocabulary = [
                "ai", "tech", "coding", "software", "development", "personal", "finance", "investing",
                "stocks", "budgeting", "wealth", "fitness", "coaching", "training", "gym", "muscle",
                "yoga", "fashion", "styling", "vintage", "thrift", "streetwear", "recipes", "pastry",
                "cooking", "restaurant", "food", "travel", "nomad", "adventure", "luxury", "gaming",
                "streamer", "keyboard", "esports", "minimalist"
            ]

    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Converts a single string or a list of strings into dense embeddings (numpy array)."""
        if isinstance(texts, str):
            texts = [texts]
            
        if not self.use_fallback and self.model is not None:
            try:
                embeddings = self.model.encode(texts, show_progress_bar=False)
                return np.array(embeddings, dtype=np.float32)
            except Exception as e:
                logger.warning(f"Error during SentenceTransformer encoding: {e}. Falling back to frequency encoding.")
                
        # Pure Python / NumPy TF-IDF fallback vectorizer
        vectors = []
        for text in texts:
            text_lower = text.lower()
            vec = []
            for word in self.vocabulary:
                # Basic frequency count of vocabulary words as mock semantic features
                count = text_lower.count(word)
                vec.append(float(count))
            # Add basic length feature
            vec.append(float(len(text)) / 100.0)
            
            # Normalize vector to unit length (L2 norm)
            arr = np.array(vec, dtype=np.float32)
            norm = np.linalg.norm(arr)
            if norm > 0:
                arr = arr / norm
            vectors.append(arr)
            
        return np.array(vectors, dtype=np.float32)

    def calculate_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculates cosine similarity between two 1D vectors."""
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / (norm1 * norm2))
