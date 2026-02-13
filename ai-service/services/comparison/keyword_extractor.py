from typing import List
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.openai_helper import get_openai_client

class KeywordExtractor:
    def __init__(self):
        self.client = get_openai_client()
    
    def extract_keywords(self, idea: str, target_market: str) -> List[str]:
        """Extract 3-5 search keywords from idea description using LLM"""
        
        prompt = f"""
        Extract 3-5 high-impact search keywords to find real-world similar startups.
        
        Idea: {idea}
        Target Market: {target_market}
        
        Return keywords that would help find:
        - Startups in the same industry niche
        - Companies solving the exact same problem
        - Businesses with the same business model (e.g. B2B SaaS, D2C)
        
        Format: Return ONLY a comma-separated list of keywords. No explanations.
        Example: "meal planning, nutrition app, grocery tech, SaaS"
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Using gpt-4o for speed and accuracy
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=100
            )
            
            keywords_str = response.choices[0].message.content.strip()
            # Clean up potential markdown or quotes
            keywords_str = keywords_str.replace('"', '').replace('`', '')
            keywords = [k.strip() for k in keywords_str.split(",")]
            
            return keywords[:5]
        except Exception as e:
            print(f"Error in keyword extraction: {e}")
            # Fallback: simple split of idea name
            return [w for w in idea.split() if len(w) > 3][:3]
