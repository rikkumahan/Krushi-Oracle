import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict


class DataBootstrapService:
    """
    Seeds the system with synthetic data to solve the 'Cold Start' problem.
    """
    
    SECTORS = ["SaaS", "EdTech", "FinTech", "HealthTech", "Consumer", "AI Tools"]
    OUTCOMES = ["UNICORN", "SUCCESS", "LIFESTYLE", "ZOMBIE", "FAILURE"]
    
    @staticmethod
    def generate_synthetic_history(count: int = 50) -> List[Dict]:
        """
        Generates mock 'ProductHunt' launch history.
        """
        history = []
        
        for _ in range(count):
            sector = random.choice(DataBootstrapService.SECTORS)
            outcome = random.choices(
                DataBootstrapService.OUTCOMES, 
                weights=[0.02, 0.15, 0.30, 0.30, 0.23], 
                k=1
            )[0]
            
            # Correlate features with outcome logic (simple synthetic rules)
            has_technical_founder = random.random() > 0.3
            market_size_score = random.randint(20, 100)
            if outcome in ["UNICORN", "SUCCESS"]:
                market_size_score = random.randint(70, 100)
                has_technical_founder = True
            
            launch_date = datetime.now() - timedelta(days=random.randint(100, 1000))
            
            entry = {
                "id": str(uuid.uuid4()),
                "name": f"{sector} Startup {random.randint(1000,9999)}",
                "sector": sector,
                "launch_date": launch_date.isoformat(),
                "outcome": outcome,
                "features": {
                    "has_technical_founder": has_technical_founder,
                    "market_size_score": market_size_score,
                    "execution_speed": random.randint(1, 10),
                    "competitor_count": random.randint(0, 20)
                }
            }
            history.append(entry)
            
        return history

    @staticmethod
    def get_sector_benchmarks(sector: str) -> Dict:
        """
        Returns mock benchmarks for the Unit Economics Engine & Sector Cache.
        """
        benchmarks = {
            "SaaS": {"cac": 150.0, "churn": 0.05, "arpu": 50.0, "lvt_cac_target": 3.0},
            "EdTech": {"cac": 80.0, "churn": 0.08, "arpu": 25.0, "lvt_cac_target": 2.5},
            "FinTech": {"cac": 250.0, "churn": 0.03, "arpu": 100.0, "lvt_cac_target": 4.0},
            "AI Tools": {"cac": 50.0, "churn": 0.10, "arpu": 30.0, "lvt_cac_target": 2.0},
        }
        return benchmarks.get(sector, benchmarks["SaaS"])
