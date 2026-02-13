from typing import Dict, Tuple
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.comparison_schemas import CompanyOutcome
from utils.openai_helper import get_openai_client

class OutcomeClassifier:
    """Classifies company outcomes and generates lessons learned using LLM"""
    
    def __init__(self):
        self.client = get_openai_client()
    
    def classify_outcome(self, company_data: Dict) -> Tuple[CompanyOutcome, str]:
        """
        Classifies company outcome (Acquired/Failed/Growing) and generates a key lesson.
        
        Returns: (outcome_enum, lesson_string)
        """
        
        # 1. Look for explicit status in metadata/description
        description = company_data.get("description", "").lower()
        metadata = company_data.get("metadata", {})
        
        # Default to GROWING if it's a newer Product Hunt launch with upvotes
        outcome = CompanyOutcome.GROWING
        
        # Heuristics for failure/acquisition if not coming from Crunchbase
        if any(word in description for word in ["shut down", "discontinued", "closed its doors", "no longer available"]):
            outcome = CompanyOutcome.FAILED
        elif any(word in description for word in ["acquired by", "joined forces with", "part of"]):
            outcome = CompanyOutcome.ACQUIRED
            
        # 2. Use LLM to refine classification and generate lesson
        lesson = self._generate_lesson_and_refine(company_data, outcome)
        
        return outcome, lesson
    
    def _generate_lesson_and_refine(self, company_data: Dict, current_outcome: CompanyOutcome) -> str:
        """Generate a concise lesson learned from the company's trajectory"""
        
        prompt = f"""
        Analyze this startup's data and provide a key lesson for other founders.
        
        Name: {company_data.get('name')}
        Description: {company_data.get('description')}
        Metadata: {company_data.get('metadata')}
        Likely Outcome: {current_outcome.value}
        
        Generate a concise, high-impact lesson (max 15 words) about why they succeeded, failed, or are growing.
        Focus on: product-market fit, execution, or business model.
        
        Format: Return ONLY the lesson string.
        Example: "Focus on a narrow niche before expanding to broader markets."
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=50
            )
            
            return response.choices[0].message.content.strip().replace('"', '')
        except Exception as e:
            print(f"Error generating lesson for {company_data.get('name')}: {e}")
            return "Execution and persistence are key to navigating early-stage challenges."
