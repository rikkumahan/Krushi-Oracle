from typing import List
import numpy as np
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.comparison_schemas import SimilarCompany
from utils.openai_helper import get_openai_client

class SimilarityRanker:
    """Ranks similar companies by semantic similarity to the user's idea"""
    
    def __init__(self):
        self.client = get_openai_client()
    
    def rank_companies(
        self, 
        companies: List[SimilarCompany],
        user_idea: str,
        target_market: str
    ) -> List[SimilarCompany]:
        """Rank companies by similarity using OpenAI embeddings"""
        
        if not companies:
            return []
            
        # 1. Get embedding for user idea
        user_text = f"{user_idea} {target_market}"
        try:
            user_embedding = self._get_embedding(user_text)
        except Exception as e:
            print(f"Error getting embedding for user idea: {e}")
            return companies  # Return unranked if embedding fails
        
        # 2. Get embeddings for each company and calculate similarity
        for company in companies:
            company_text = f"{company.name} {company.description}"
            try:
                company_embedding = self._get_embedding(company_text)
                
                # Cosine similarity
                similarity = self._cosine_similarity(user_embedding, company_embedding)
                company.similarity_score = float(similarity * 100)
            except Exception as e:
                print(f"Error ranking company {company.name}: {e}")
                company.similarity_score = 0.0
        
        # 3. Sort by similarity (descending)
        companies.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return companies
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get OpenAI embedding for text"""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors using numpy"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
            
        return dot_product / (norm_v1 * norm_v2)
