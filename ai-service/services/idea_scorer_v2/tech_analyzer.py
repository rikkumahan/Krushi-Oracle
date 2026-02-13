"""
Innovation 4: Tech Stack Interaction Matrix

Analyzes technology stack feasibility considering not just individual
complexity but also interaction penalties, learning curves, and synergies.

100% deterministic - NO LLM usage.
"""

from typing import Dict, Any, List, Set
from dataclasses import dataclass
from enum import Enum


class TechCategory(str, Enum):
    """Technology categories"""
    FRONTEND = "FRONTEND"
    BACKEND = "BACKEND"
    DATABASE = "DATABASE"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    AI_ML = "AI_ML"
    BLOCKCHAIN = "BLOCKCHAIN"
    MOBILE = "MOBILE"
    DEVOPS = "DEVOPS"


@dataclass
class Technology:
    """Individual technology definition"""
    name: str
    category: TechCategory
    complexity: int  # 1-10 scale
    maturity: str    # EXPERIMENTAL, EMERGING, STABLE, MATURE, LEGACY
    learning_curve_months: float  # Time to proficiency


@dataclass
class TechStack:
    """Complete technology stack"""
    technologies: List[Technology]
    team_experience: Dict[str, str] = None  # {tech_name: "EXPERT|FAMILIAR|BEGINNER|NONE"}
    
    def __post_init__(self):
        """Set defaults"""
        if self.team_experience is None:
            self.team_experience = {}


class TechStackAnalyzer:
    """Analyzes tech stack feasibility with interaction penalties"""
    
    # Known technology database (simplified - real version would be much larger)
    TECH_DB = {
        # Frontend
        "React": Technology("React", TechCategory.FRONTEND, 5, "MATURE", 2),
        "Next.js": Technology("Next.js", TechCategory.FRONTEND, 6, "STABLE", 2.5),
        "Vue": Technology("Vue", TechCategory.FRONTEND, 4, "MATURE", 1.5),
        "Svelte": Technology("Svelte", TechCategory.FRONTEND, 4, "EMERGING", 1.5),
        
        # Backend
        "Node.js": Technology("Node.js", TechCategory.BACKEND, 5, "MATURE", 2),
        "FastAPI": Technology("FastAPI", TechCategory.BACKEND, 6, "STABLE", 2),
        "Django": Technology("Django", TechCategory.BACKEND, 6, "MATURE", 3),
        "Express": Technology("Express", TechCategory.BACKEND, 4, "MATURE", 1.5),
        
        # Database
        "PostgreSQL": Technology("PostgreSQL", TechCategory.DATABASE, 6, "MATURE", 3),
        "MongoDB": Technology("MongoDB", TechCategory.DATABASE, 5, "MATURE", 2),
        "Redis": Technology("Redis", TechCategory.DATABASE, 4, "MATURE", 1),
        "Prisma": Technology("Prisma", TechCategory.DATABASE, 5, "STABLE", 2),
        
        # Infrastructure/DevOps
        "Docker": Technology("Docker", TechCategory.DEVOPS, 6, "MATURE", 2),
        "Kubernetes": Technology("Kubernetes", TechCategory.DEVOPS, 9, "STABLE", 6),
        "AWS": Technology("AWS", TechCategory.INFRASTRUCTURE, 7, "MATURE", 4),
        "Vercel": Technology("Vercel", TechCategory.INFRASTRUCTURE, 3, "STABLE", 0.5),
        
        # AI/ML
        "OpenAI API": Technology("OpenAI API", TechCategory.AI_ML, 4, "STABLE", 1),
        "TensorFlow": Technology("TensorFlow", TechCategory.AI_ML, 9, "MATURE", 6),
        "PyTorch": Technology("PyTorch", TechCategory.AI_ML, 9, "MATURE", 6),
        
        # Blockchain
        "Ethereum": Technology("Ethereum", TechCategory.BLOCKCHAIN, 10, "STABLE", 8),
        "Solana": Technology("Solana", TechCategory.BLOCKCHAIN, 9, "EMERGING", 6),
    }
    
    # Interaction matrix: {(tech1, tech2): penalty/bonus}
    # Positive = Synergy (bonus), Negative = Conflict (penalty)
    INTERACTIONS = {
        ("Next.js", "Vercel"): -1.5,        # Great synergy
        ("React", "Next.js"): -1.0,         # Natural fit
        ("Node.js", "Express"): -0.5,       # Compatible
        ("FastAPI", "PostgreSQL"): -0.5,    # Good combo
        ("Prisma", "PostgreSQL"): -1.0,     # Excellent ORM match
        
        # Conflicts (penalties)
        ("MongoDB", "PostgreSQL"): +2.0,    # Mixing SQL/NoSQL adds complexity
        ("Django", "Node.js"): +1.5,        # Mixing Python/JS backend
        ("Kubernetes", "Vercel"): +2.0,     # Over-engineering
    }
    
    def analyze_stack(self, stack: TechStack) -> Dict[str, Any]:
        """
        Analyze tech stack feasibility comprehensively.
        
        Returns:
        - execution_score: 0-100 (higher = easier to execute)
        - complexity_rating: Classification (SIMPLE, MODERATE, etc.)
        - total_learning_time: Estimated months to proficiency
        - interaction_analysis: Synergies and conflicts
        - risk_factors: Showstoppers and warnings
        """
        # Calculate base complexity
        base_complexity = self._calculate_base_complexity(stack)
        
        # Calculate interaction penalty/bonus
        interaction_effect = self._calculate_interactions(stack)
        
        # Calculate learning curve adjustment
        learning_adjustment = self._calculate_learning_curve(stack)
        
        # Calculate team readiness
        team_readiness = self._assess_team_readiness(stack)
        
        # Calculate maturity risk
        maturity_risk = self._assess_maturity_risk(stack)
        
        # Calculate total complexity
        total_complexity = (
            base_complexity +
            interaction_effect['penalty'] +
            learning_adjustment -
            interaction_effect['bonus']
        )
        
        # Classify complexity
        complexity_rating = self._classify_complexity(total_complexity)
        
        # Calculate execution score (inverse of complexity)
        execution_score = self._calculate_execution_score(
            total_complexity,
            team_readiness,
            maturity_risk
        )
        
        # Identify risk factors
        risk_factors = self._identify_risks(
            stack,
            total_complexity,
            team_readiness,
            maturity_risk
        )
        
        return {
            'execution_score': int(execution_score),
            'complexity_rating': complexity_rating,
            'total_complexity': round(total_complexity, 2),
            'estimated_learning_months': round(learning_adjustment, 1),
            'team_readiness_score': int(team_readiness),
            'breakdown': {
                'base_complexity': round(base_complexity, 2),
                'interaction_penalty': round(interaction_effect['penalty'], 2),
                'interaction_bonus': round(interaction_effect['bonus'], 2),
                'learning_curve_penalty': round(learning_adjustment, 2),
                'maturity_risk': round(maturity_risk, 2)
            },
            'interactions': interaction_effect['details'],
            'risk_factors': risk_factors,
            'technologies': [
                {
                    'name': tech.name,
                    'category': tech.category,
                    'complexity': tech.complexity,
                    'maturity': tech.maturity,
                    'learning_months': tech.learning_curve_months,
                    'team_experience': stack.team_experience.get(tech.name, "NONE")
                }
                for tech in stack.technologies
            ]
        }
    
    def _calculate_base_complexity(self, stack: TechStack) -> float:
        """Sum of individual technology complexities"""
        return sum(tech.complexity for tech in stack.technologies)
    
    def _calculate_interactions(self, stack: TechStack) -> Dict[str, Any]:
        """
        Calculate interaction effects between technologies.
        
        Returns total penalty and bonus separately.
        """
        total_penalty = 0.0
        total_bonus = 0.0
        details = []
        
        tech_names = [tech.name for tech in stack.technologies]
        
        # Check all pairs
        for i, tech1_name in enumerate(tech_names):
            for tech2_name in tech_names[i+1:]:
                pair = (tech1_name, tech2_name)
                reverse_pair = (tech2_name, tech1_name)
                
                effect = self.INTERACTIONS.get(pair) or self.INTERACTIONS.get(reverse_pair)
                
                if effect:
                    if effect > 0:
                        total_penalty += effect
                        details.append({
                            'pair': [tech1_name, tech2_name],
                            'type': 'CONFLICT',
                            'penalty': effect,
                            'description': f"{tech1_name} + {tech2_name} creates complexity"
                        })
                    else:
                        total_bonus += abs(effect)
                        details.append({
                            'pair': [tech1_name, tech2_name],
                            'type': 'SYNERGY',
                            'bonus': abs(effect),
                            'description': f"{tech1_name} + {tech2_name} work well together"
                        })
        
        return {
            'penalty': total_penalty,
            'bonus': total_bonus,
            'details': details
        }
    
    def _calculate_learning_curve(self, stack: TechStack) -> float:
        """
        Calculate learning curve penalty based on team experience.
        
        Higher penalty for unfamiliar complex technologies.
        """
        total_learning_penalty = 0.0
        
        for tech in stack.technologies:
            experience = stack.team_experience.get(tech.name, "NONE")
            
            # Learning multiplier based on experience
            multipliers = {
                "EXPERT": 0.0,       # No penalty
                "FAMILIAR": 0.3,     # 30% penalty
                "BEGINNER": 0.7,     # 70% penalty
                "NONE": 1.0          # Full penalty
            }
            
            multiplier = multipliers.get(experience, 1.0)
            learning_penalty = tech.learning_curve_months * multiplier
            
            total_learning_penalty += learning_penalty
        
        return total_learning_penalty
    
    def _assess_team_readiness(self, stack: TechStack) -> float:
        """
        Assess team readiness score (0-100).
        
        Higher score = More experienced team.
        """
        if not stack.technologies:
            return 0.0
        
        experience_scores = {
            "EXPERT": 100,
            "FAMILIAR": 70,
            "BEGINNER": 40,
            "NONE": 0
        }
        
        total_score = 0
        for tech in stack.technologies:
            experience = stack.team_experience.get(tech.name, "NONE")
            total_score += experience_scores.get(experience, 0)
        
        avg_score = total_score / len(stack.technologies)
        return avg_score
    
    def _assess_maturity_risk(self, stack: TechStack) -> float:
        """
        Assess risk from using immature technologies.
        
        Returns penalty (0-5)
        """
        maturity_penalties = {
            "EXPERIMENTAL": 3.0,  # High risk
            "EMERGING": 1.5,      # Moderate risk
            "STABLE": 0.5,        # Low risk
            "MATURE": 0.0,        # No risk
            "LEGACY": 1.0         # Maintenance risk
        }
        
        total_penalty = sum(
            maturity_penalties.get(tech.maturity, 1.0)
            for tech in stack.technologies
        )
        
        return total_penalty
    
    def _classify_complexity(self, total_complexity: float) -> str:
        """Classify overall complexity"""
        if total_complexity < 15:
            return "SIMPLE"
        elif total_complexity < 30:
            return "MODERATE"
        elif total_complexity < 50:
            return "COMPLEX"
        elif total_complexity < 70:
            return "ADVANCED"
        else:
            return "MOONSHOT"
    
    def _calculate_execution_score(
        self,
        complexity: float,
        team_readiness: float,
        maturity_risk: float
    ) -> float:
        """
        Calculate execution score (0-100).
        
        Higher score = Easier to execute.
        """
        # Base score from complexity (inverse)
        if complexity < 15:
            base_score = 90
        elif complexity < 30:
            base_score = 75
        elif complexity < 50:
            base_score = 60
        elif complexity < 70:
            base_score = 40
        else:
            base_score = 20
        
        # Boost from team readiness
        readiness_boost = (team_readiness - 50) / 5  # Max ±10 points
        
        # Penalty from maturity risk
        maturity_penalty = maturity_risk * 3  # Each point = 3% penalty
        
        score = base_score + readiness_boost - maturity_penalty
        
        return max(0, min(100, score))
    
    def _identify_risks(
        self,
        stack: TechStack,
        complexity: float,
        team_readiness: float,
        maturity_risk: float
    ) -> List[Dict[str, Any]]:
        """Identify specific risk factors"""
        risks = []
        
        # High complexity risk
        if complexity > 70:
            risks.append({
                'level': 'CRITICAL',
                'factor': 'EXTREME_COMPLEXITY',
                'description': f"Total complexity ({complexity:.1f}) is extremely high. High risk of delays and technical debt."
            })
        elif complexity > 50:
            risks.append({
                'level': 'HIGH',
                'factor': 'HIGH_COMPLEXITY',
                'description': f"Total complexity ({complexity:.1f}) is high. May require experienced team and longer timeline."
            })
        
        # Team readiness risk
        if team_readiness < 40:
            risks.append({
                'level': 'CRITICAL',
                'factor': 'LOW_TEAM_READINESS',
                'description': f"Team readiness ({team_readiness:.0f}/100) is very low. Significant learning curve ahead."
            })
        elif team_readiness < 60:
            risks.append({
                'level': 'MODERATE',
                'factor': 'TEAM_SKILL_GAP',
                'description': f"Team readiness ({team_readiness:.0f}/100) indicates skill gaps. Budget time for learning."
            })
        
        # Maturity risk
        if maturity_risk > 5:
            risks.append({
                'level': 'HIGH',
                'factor': 'IMMATURE_TECH_STACK',
                'description': f"Stack includes experimental/emerging technologies. Expect breaking changes and limited support."
            })
        
        # Specific technology warnings
        for tech in stack.technologies:
            if tech.complexity >= 9:
                risks.append({
                    'level': 'HIGH',
                    'factor': 'COMPLEX_TECHNOLOGY',
                    'description': f"{tech.name} is highly complex ({tech.complexity}/10). Requires deep expertise."
                })
            
            if tech.maturity == "EXPERIMENTAL":
                risks.append({
                    'level': 'HIGH',
                    'factor': 'EXPERIMENTAL_TECH',
                    'description': f"{tech.name} is experimental. High risk of instability."
                })
        
        return risks
