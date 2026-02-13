"""
Innovation 3: Competitive Density Mapping

Multi-dimensional competitive analysis that goes beyond simple counts.

Metrics:
- Direct competitors (commercial entities)
- Substitutes (alternative solutions)
- Market concentration (HHI index)
- Entry barriers
- Innovation rate
- Market power distribution

100% deterministic - NO LLM usage.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class CompetitiveData:
    """Raw competitive landscape data"""
    
    # Direct competitors
    commercial_entity_count: int = 0       # Companies offering similar products
    top_player_market_shares: List[float] = None  # Market share of top 3-5 players (as %)
    
    # Market dynamics
    new_entrants_12m: int = 0              # New companies in last 12 months
    exits_12m: int = 0                     # Companies that shut down/pivoted
    
    # Substitute products
    substitute_count: int = 0              # Alternative solutions
    
    # Innovation signals
    patent_filings_12m: int = 0            # Patent activity (if available)
    funding_rounds_12m: int = 0            # VC funding activity
    
    # Content saturation
    youtube_video_count: int = 0           # Educational/commercial content
    blog_post_count: int = 0               # Written content
    
    def __post_init__(self):
        """Set defaults"""
        if self.top_player_market_shares is None:
            self.top_player_market_shares = []


class CompetitiveDensityMapper:
    """Maps competitive landscape across multiple dimensions"""
    
    def map_competition(self, data: CompetitiveData) -> Dict[str, Any]:
        """
        Analyze competitive landscape comprehensively.
        
        Returns:
        - competition_score: 0-100 (higher = easier to compete)
        - market_structure: Classification (MONOPOLY, OLIGOPOLY, etc.)
        - entry_difficulty: Ease of market entry
        - saturation_level: Content/product saturation
        - breakdown: Detailed metrics
        """
        # Calculate HHI index
        hhi = self._calculate_hhi(data.top_player_market_shares)
        
        # Classify market structure
        market_structure = self._classify_market_structure(hhi)
        
        # Calculate entry difficulty
        entry_difficulty = self._assess_entry_difficulty(
            hhi,
            data.new_entrants_12m,
            data.exits_12m
        )
        
        # Calculate saturation level
        saturation = self._assess_saturation(
            data.commercial_entity_count,
            data.youtube_video_count,
            data.blog_post_count
        )
        
        # Calculate innovation rate
        innovation_rate = self._calculate_innovation_rate(
            data.patent_filings_12m,
            data.funding_rounds_12m,
            data.new_entrants_12m
        )
        
        # Calculate substitute threat
        substitute_threat = self._assess_substitute_threat(
            data.substitute_count,
            data.commercial_entity_count
        )
        
        # Calculate final competition score (higher = easier to compete)
        competition_score = self._calculate_competition_score(
            hhi,
            entry_difficulty,
            saturation,
            substitute_threat
        )
        
        return {
            'competition_score': int(competition_score),
            'market_structure': market_structure,
            'hhi_index': hhi,
            'entry_difficulty': entry_difficulty,
            'saturation_level': saturation,
            'innovation_rate': innovation_rate,
            'substitute_threat': substitute_threat,
            'breakdown': {
                'direct_competitors': {
                    'count': data.commercial_entity_count,
                    'top_player_shares': data.top_player_market_shares,
                    'market_concentration': self._describe_concentration(hhi)
                },
                'market_dynamics': {
                    'new_entrants_12m': data.new_entrants_12m,
                    'exits_12m': data.exits_12m,
                    'churn_rate': self._calculate_churn_rate(
                        data.new_entrants_12m,
                        data.exits_12m,
                        data.commercial_entity_count
                    )
                },
                'content_saturation': {
                    'youtube_videos': data.youtube_video_count,
                    'blog_posts': data.blog_post_count,
                    'saturation_level': saturation
                },
                'innovation_activity': {
                    'patent_filings_12m': data.patent_filings_12m,
                    'funding_rounds_12m': data.funding_rounds_12m,
                    'innovation_rate': innovation_rate
                },
                'substitutes': {
                    'count': data.substitute_count,
                    'threat_level': substitute_threat
                }
            },
            'strategic_insight': self._generate_insight(
                market_structure,
                competition_score,
                saturation,
                entry_difficulty
            )
        }
    
    def _calculate_hhi(self, market_shares: List[float]) -> int:
        """
        Calculate Herfindahl-Hirschman Index.
        
        HHI = Σ(market_share_i²)
        
        Returns:
        - 10000: Pure monopoly (one player with 100%)
        - >2500: Highly concentrated
        - 1500-2500: Moderately concentrated
        - <1500: Competitive
        """
        if not market_shares:
            return 0  # Unknown/highly fragmented
        
        hhi = sum(share ** 2 for share in market_shares)
        return int(hhi)
    
    def _classify_market_structure(self, hhi: int) -> str:
        """Classify market structure from HHI"""
        if hhi == 0:
            return "UNKNOWN"
        elif hhi > 2500:
            return "MONOPOLY"
        elif hhi > 1500:
            return "OLIGOPOLY"
        elif hhi > 600:
            return "MODERATE_COMPETITION"
        else:
            return "FRAGMENTED"
    
    def _assess_entry_difficulty(
        self,
        hhi: int,
        new_entrants: int,
        exits: int
    ) -> str:
        """
        Assess difficulty of market entry.
        
        Considers:
        - Market concentration (HHI)
        - Historical entry rate
        - Exit rate (failure indicator)
        """
        # High HHI = Hard to enter (entrenched players)
        if hhi > 2500:
            base_difficulty = "VERY_HIGH"
        elif hhi > 1500:
            base_difficulty = "HIGH"
        elif hhi > 600:
            base_difficulty = "MODERATE"
        else:
            base_difficulty = "LOW"
        
        # Adjust based on entry/exit dynamics
        if new_entrants > 10 and exits < new_entrants / 2:
            # Lots of successful entries
            if base_difficulty == "VERY_HIGH":
                return "HIGH"
            elif base_difficulty == "HIGH":
                return "MODERATE"
        
        if exits > new_entrants * 2:
            # High failure rate
            if base_difficulty == "LOW":
                return "MODERATE"
            elif base_difficulty == "MODERATE":
                return "HIGH"
        
        return base_difficulty
    
    def _assess_saturation(
        self,
        commercial_count: int,
        youtube_count: int,
        blog_count: int
    ) -> str:
        """
        Assess market saturation from content/product density.
        
        Returns: MINIMAL, LOW, MODERATE, HIGH, EXTREME
        """
        # Weighted saturation score
        saturation_score = (
            0.4 * min(100, commercial_count) +
            0.3 * min(100, youtube_count / 100) +
            0.3 * min(100, blog_count / 500)
        )
        
        if saturation_score > 80:
            return "EXTREME"
        elif saturation_score > 60:
            return "HIGH"
        elif saturation_score > 40:
            return "MODERATE"
        elif saturation_score > 20:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _calculate_innovation_rate(
        self,
        patents: int,
        funding_rounds: int,
        new_entrants: int
    ) -> str:
        """
        Calculate innovation rate from patent and funding activity.
        
        Returns: STAGNANT, LOW, MODERATE, HIGH, EXPLOSIVE
        """
        innovation_score = (
            0.4 * min(50, patents) +
            0.4 * min(50, funding_rounds) +
            0.2 * min(50, new_entrants)
        )
        
        if innovation_score > 40:
            return "EXPLOSIVE"
        elif innovation_score > 25:
            return "HIGH"
        elif innovation_score > 15:
            return "MODERATE"
        elif innovation_score > 5:
            return "LOW"
        else:
            return "STAGNANT"
    
    def _assess_substitute_threat(
        self,
        substitute_count: int,
        commercial_count: int
    ) -> str:
        """
        Assess threat from substitute products.
        
        Returns: MINIMAL, LOW, MODERATE, HIGH, CRITICAL
        """
        if commercial_count == 0:
            ratio = substitute_count
        else:
            ratio = substitute_count / commercial_count
        
        if ratio > 2.0:
            return "CRITICAL"
        elif ratio > 1.0:
            return "HIGH"
        elif ratio > 0.5:
            return "MODERATE"
        elif ratio > 0.2:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _calculate_churn_rate(
        self,
        entries: int,
        exits: int,
        total: int
    ) -> float:
        """Calculate market churn rate"""
        if total == 0:
            return 0.0
        
        churn = (exits / max(1, total)) * 100
        return round(churn, 1)
    
    def _calculate_competition_score(
        self,
        hhi: int,
        entry_difficulty: str,
        saturation: str,
        substitute_threat: str
    ) -> float:
        """
        Calculate final competition score (0-100).
        
        Higher score = Easier to compete (better for startup)
        """
        # HHI component (inverted - lower HHI = easier to compete)
        if hhi > 2500:
            hhi_score = 20  # Monopoly - very hard
        elif hhi > 1500:
            hhi_score = 40  # Oligopoly - hard
        elif hhi > 600:
            hhi_score = 70  # Moderate - sweet spot
        else:
            hhi_score = 85  # Fragmented - easy entry
        
        # Entry difficulty penalty
        entry_penalties = {
            "VERY_HIGH": 30,
            "HIGH": 20,
            "MODERATE": 10,
            "LOW": 0
        }
        entry_penalty = entry_penalties.get(entry_difficulty, 10)
        
        # Saturation penalty
        saturation_penalties = {
            "EXTREME": 25,
            "HIGH": 15,
            "MODERATE": 5,
            "LOW": 0,
            "MINIMAL": 0
        }
        saturation_penalty = saturation_penalties.get(saturation, 5)
        
        # Substitute threat penalty
        substitute_penalties = {
            "CRITICAL": 20,
            "HIGH": 15,
            "MODERATE": 8,
            "LOW": 3,
            "MINIMAL": 0
        }
        substitute_penalty = substitute_penalties.get(substitute_threat, 5)
        
        # Calculate final score
        score = hhi_score - entry_penalty - saturation_penalty - substitute_penalty
        
        return max(0, min(100, score))
    
    def _describe_concentration(self, hhi: int) -> str:
        """Human-readable HHI description"""
        if hhi > 2500:
            return "Highly concentrated (monopoly/duopoly)"
        elif hhi > 1500:
            return "Moderately concentrated (oligopoly)"
        elif hhi > 600:
            return "Low concentration (competitive)"
        else:
            return "Highly fragmented (many small players)"
    
    def _generate_insight(
        self,
        market_structure: str,
        score: int,
        saturation: str,
        entry_difficulty: str
    ) -> str:
        """Generate strategic insight"""
        if score >= 70:
            return f"{market_structure} market with {saturation.lower()} saturation. Good opportunity for differentiation."
        elif score >= 50:
            return f"{market_structure} market. {entry_difficulty.replace('_', ' ').title()} entry difficulty. Requires strong differentiation."
        else:
            return f"{market_structure} market with {entry_difficulty.replace('_', ' ').lower()} entry barriers. Very challenging competitive landscape."
