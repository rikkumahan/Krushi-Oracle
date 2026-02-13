"""
Rule Engine for Deterministic Classification

This module provides threshold-based classification functions
that map quantitative data to qualitative categories.

NO LLM or AI judgment - just pure deterministic rules.
"""

from typing import Dict, Any, Optional
from enum import Enum


class MarketSize(str, Enum):
    """Market size classifications"""
    ELITE = "ELITE"              # > 100K monthly searches
    HIGH = "HIGH"                # 15K - 100K
    MODERATE = "MODERATE"        # 5K - 15K
    LOW = "LOW"                  # 1K - 5K
    MINIMAL = "MINIMAL"          # < 1K


class TrendPattern(str, Enum):
    """Market trend patterns"""
    RISING_FAST = "RISING_FAST"        # > 20% growth
    RISING = "RISING"                  # 10-20% growth
    STABLE = "STABLE"                  # -5% to 10% growth
    DECLINING = "DECLINING"            # -20% to -5%
    COLLAPSING = "COLLAPSING"          # < -20%


class CompetitiveIntensity(str, Enum):
    """Competition level"""
    MONOPOLY = "MONOPOLY"              # HHI > 2500
    OLIGOPOLY = "OLIGOPOLY"            # HHI 1500-2500
    MODERATE = "MODERATE"              # HHI 600-1500
    FRAGMENTED = "FRAGMENTED"          # HHI < 600


class TechComplexity(str, Enum):
    """Technical complexity levels"""
    SIMPLE = "SIMPLE"                  # Score < 3
    MODERATE = "MODERATE"              # Score 3-5
    COMPLEX = "COMPLEX"                # Score 5-7
    ADVANCED = "ADVANCED"              # Score 7-9
    MOONSHOT = "MOONSHOT"              # Score > 9


class RuleEngine:
    """Deterministic rule-based classifier"""
    
    @staticmethod
    def classify_market_size(monthly_searches: int) -> tuple[MarketSize, int]:
        """
        Classify market size from monthly search volume.
        
        Returns: (MarketSize enum, score 0-100)
        """
        if monthly_searches == 0:
            return MarketSize.MINIMAL, 0
        elif monthly_searches < 1000:
            score = int((monthly_searches / 1000) * 20)  # 0-20
            return MarketSize.MINIMAL, score
        elif monthly_searches < 5000:
            score = 20 + int(((monthly_searches - 1000) / 4000) * 20)  # 20-40
            return MarketSize.LOW, score
        elif monthly_searches < 15000:
            score = 40 + int(((monthly_searches - 5000) / 10000) * 20)  # 40-60
            return MarketSize.MODERATE, score
        elif monthly_searches < 100000:
            score = 60 + int(((monthly_searches - 15000) / 85000) * 20)  # 60-80
            return MarketSize.HIGH, score
        else:
            # Cap at 100
            score = min(100, 80 + int(((monthly_searches - 100000) / 100000) * 20))
            return MarketSize.ELITE, score
    
    @staticmethod
    def classify_trend_pattern(
        growth_rate_30d: float,
        growth_rate_90d: float,
        growth_rate_180d: float
    ) -> tuple[TrendPattern, int]:
        """
        Classify trend pattern from growth rates.
        
        Args:
            growth_rate_*: Growth rate as decimal (e.g., 0.15 for +15%)
        
        Returns: (TrendPattern enum, score 0-100)
        """
        # Weight recent data more heavily
        weighted_growth = (
            0.5 * growth_rate_30d +
            0.3 * growth_rate_90d +
            0.2 * growth_rate_180d
        )
        
        # Classify pattern
        if weighted_growth > 0.20:
            pattern = TrendPattern.RISING_FAST
            score = min(100, 80 + int(weighted_growth * 100))
        elif weighted_growth > 0.10:
            pattern = TrendPattern.RISING
            score = 60 + int((weighted_growth - 0.10) / 0.10 * 20)
        elif weighted_growth > -0.05:
            pattern = TrendPattern.STABLE
            score = 40 + int((weighted_growth + 0.05) / 0.15 * 20)
        elif weighted_growth > -0.20:
            pattern = TrendPattern.DECLINING
            score = 20 + int((weighted_growth + 0.20) / 0.15 * 20)
        else:
            pattern = TrendPattern.COLLAPSING
            score = max(0, int((weighted_growth + 0.50) / 0.30 * 20))
        
        return pattern, score
    
    @staticmethod
    def calculate_hhi_index(market_shares: list[float]) -> int:
        """
        Calculate Herfindahl-Hirschman Index.
        
        Args:
            market_shares: List of market shares as percentages (0-100)
        
        Returns:
            HHI index (0-10000)
        """
        hhi = sum(share ** 2 for share in market_shares)
        return int(hhi)
    
    @staticmethod
    def classify_competitive_intensity(hhi: int) -> tuple[CompetitiveIntensity, int]:
        """
        Classify competitive intensity from HHI index.
        
        Higher competition = Lower score (harder to differentiate)
        Lower competition = Higher score (easier to capture market)
        
        Returns: (CompetitiveIntensity enum, score 0-100)
        """
        if hhi > 2500:
            # Monopoly - hard to enter
            pattern = CompetitiveIntensity.MONOPOLY
            score = 30  # Low score - very hard to compete
        elif hhi > 1500:
            # Oligopoly - challenging but possible
            pattern = CompetitiveIntensity.OLIGOPOLY
            score = 50
        elif hhi > 600:
            # Moderate competition - sweet spot
            pattern = CompetitiveIntensity.MODERATE
            score = 75
        else:
            # Fragmented - easy to enter
            pattern = CompetitiveIntensity.FRAGMENTED
            score = 85
        
        return pattern, score
    
    @staticmethod
    def classify_tech_complexity(
        base_complexity: float,
        interaction_penalty: float,
        learning_curve: float
    ) -> tuple[TechComplexity, int]:
        """
        Classify technical complexity.
        
        Args:
            base_complexity: Sum of individual tech complexities (0-10)
            interaction_penalty: Penalty for conflicts/incompatibilities (0-5)
            learning_curve: Team learning curve factor (0-3)
        
        Returns: (TechComplexity enum, score 0-100)
        """
        total_complexity = base_complexity + interaction_penalty + learning_curve
        
        # Classify
        if total_complexity < 3:
            pattern = TechComplexity.SIMPLE
            score = 90 - int(total_complexity * 10)
        elif total_complexity < 5:
            pattern = TechComplexity.MODERATE
            score = 70 - int((total_complexity - 3) * 10)
        elif total_complexity < 7:
            pattern = TechComplexity.COMPLEX
            score = 50 - int((total_complexity - 5) * 10)
        elif total_complexity < 9:
            pattern = TechComplexity.ADVANCED
            score = 30 - int((total_complexity - 7) * 10)
        else:
            pattern = TechComplexity.MOONSHOT
            score = max(0, 10 - int((total_complexity - 9) * 5))
        
        return pattern, score
    
    @staticmethod
    def apply_quality_gates(
        market_score: int,
        differentiation_score: int,
        execution_score: int,
        capital_score: int
    ) -> int:
        """
        Apply quality gates to calculate final MVS with showstopper detection.
        
        Quality Gates:
        - Any dimension < 30 caps overall at 50
        - Market demand < 40 caps overall at 60
        
        Returns: Final MVS score (0-100)
        """
        # Check showstopper: any dimension critically low
        if any(score < 30 for score in [market_score, differentiation_score, execution_score, capital_score]):
            # Cap at 50 - critical weakness
            base_score = (
                0.35 * market_score +
                0.30 * differentiation_score +
                0.20 * execution_score +
                0.15 * capital_score
            )
            return int(min(50, base_score))
        
        # Check showstopper: no market demand
        if market_score < 40:
            # Cap at 60 - risky market
            base_score = (
                0.35 * market_score +
                0.30 * differentiation_score +
                0.20 * execution_score +
                0.15 * capital_score
            )
            return int(min(60, base_score))
        
        # No quality gates triggered - calculate normally
        mvs = (
            0.35 * market_score +
            0.30 * differentiation_score +
            0.20 * execution_score +
            0.15 * capital_score
        )
        
        return int(mvs)
    
    @staticmethod
    def explain_rule(rule_name: str) -> str:
        """
        Get explanation for a specific rule.
        
        Returns detailed description of the rule logic.
        """
        explanations = {
            "MODERATE_DEMAND": """
                Applied when search volume is between 5K-15K monthly searches.
                This indicates a validated niche market with proven demand but
                not yet mass-market scale. Market size scores 40-60.
                
                Threshold reasoning:
                - < 5K: Too small for VC scale
                - 5K-15K: Proven niche, scalable
                - > 15K: Mass market opportunity
            """,
            "HIGH_DEMAND": """
                Applied when search volume exceeds 15K monthly searches.
                This indicates strong commercial interest and mass-market potential.
                Market size scores 60-80.
            """,
            "ELITE_DEMAND": """
                Applied when search volume exceeds 100K monthly searches.
                This indicates a massive, validated market with mainstream appeal.
                Market size scores 80-100.
            """,
            "FRAGMENTED_MARKET": """
                Applied when HHI index < 600.
                This indicates a highly fragmented market with many small players,
                making it easier to enter but potentially harder to dominate.
                Differentiation scores 75-85.
            """,
            "OLIGOPOLY_MARKET": """
                Applied when HHI index 1500-2500.
                This indicates a market dominated by a few large players.
                Challenging to enter but profitable if successful.
                Differentiation scores ~50.
            """,
        }
        
        return explanations.get(rule_name, "No explanation available for this rule.")


# Global instance
rule_engine = RuleEngine()
