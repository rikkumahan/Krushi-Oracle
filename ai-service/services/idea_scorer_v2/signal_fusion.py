"""
Innovation 1: Composite Signal Fusion

Fuses multiple weak signals into strong demand indicators using
Bayesian aggregation with fixed priors.

Signals:
- Google Trends search volume
- Google Trends growth rate
- YouTube video count
- YouTube engagement (views)
- Reddit discussion volume
- Wikipedia page views
- News article count
- News source diversity

100% deterministic - NO LLM usage.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import math


@dataclass
class SignalWeights:
    """Fixed Bayesian priors for signal reliability"""
    
    google_trends_volume: float = 0.25      # Primary demand signal
    google_trends_growth: float = 0.15      # Momentum indicator
    youtube_coverage: float = 0.15          # Content market proxy
    youtube_engagement: float = 0.10        # Audience interest
    reddit_activity: float = 0.10           # Community discussion
    wikipedia_views: float = 0.10           # Educational interest
    news_coverage: float = 0.10             # Media attention
    news_diversity: float = 0.05            # Source breadth
    
    def __post_init__(self):
        """Validate weights sum to 1.0"""
        total = (
            self.google_trends_volume +
            self.google_trends_growth +
            self.youtube_coverage +
            self.youtube_engagement +
            self.reddit_activity +
            self.wikipedia_views +
            self.news_coverage +
            self.news_diversity
        )
        assert abs(total - 1.0) < 0.001, f"Weights must sum to 1.0, got {total}"


@dataclass
class MarketSignals:
    """Raw market data for a keyword"""
    
    # Google Trends
    monthly_searches: int = 0
    growth_rate_30d: float = 0.0         # Decimal (0.15 = +15%)
    
    # YouTube
    video_count: int = 0
    total_views: int = 0
    
    # Reddit
    post_count: int = 0
    total_score: int = 0
    
    # Wikipedia
    daily_views: int = 0
    
    # News
    article_count_30d: int = 0
    unique_sources: int = 0


class CompositeSignalScorer:
    """Fuses multiple weak signals into strong demand indicators"""
    
    def __init__(self, weights: Optional[SignalWeights] = None):
        self.weights = weights or SignalWeights()
    
    def score_market_demand(self, signals: MarketSignals) -> Dict[str, Any]:
        """
        Aggregate signals using Bayesian fusion.
        
        Returns:
        - demand_score: 0-100 composite score
        - breakdown: Individual signal contributions
        - confidence: Reliability confidence (0-100)
        """
        # Normalize each signal to 0-100 scale
        normalized = self._normalize_signals(signals)
        
        # Calculate weighted composite score
        demand_score = (
            self.weights.google_trends_volume * normalized['trends_volume'] +
            self.weights.google_trends_growth * normalized['trends_growth'] +
            self.weights.youtube_coverage * normalized['youtube_count'] +
            self.weights.youtube_engagement * normalized['youtube_engagement'] +
            self.weights.reddit_activity * normalized['reddit_activity'] +
            self.weights.wikipedia_views * normalized['wikipedia_views'] +
            self.weights.news_coverage * normalized['news_coverage'] +
            self.weights.news_diversity * normalized['news_diversity']
        )
        
        # Calculate confidence based on signal coverage
        confidence = self._calculate_confidence(normalized)
        
        return {
            'demand_score': int(demand_score),
            'confidence': int(confidence),
            'breakdown': {
                'google_trends_volume': {
                    'raw': signals.monthly_searches,
                    'normalized': int(normalized['trends_volume']),
                    'contribution': int(self.weights.google_trends_volume * normalized['trends_volume']),
                    'weight': self.weights.google_trends_volume
                },
                'google_trends_growth': {
                    'raw': signals.growth_rate_30d,
                    'normalized': int(normalized['trends_growth']),
                    'contribution': int(self.weights.google_trends_growth * normalized['trends_growth']),
                    'weight': self.weights.google_trends_growth
                },
                'youtube_coverage': {
                    'raw': signals.video_count,
                    'normalized': int(normalized['youtube_count']),
                    'contribution': int(self.weights.youtube_coverage * normalized['youtube_count']),
                    'weight': self.weights.youtube_coverage
                },
                'youtube_engagement': {
                    'raw': signals.total_views,
                    'normalized': int(normalized['youtube_engagement']),
                    'contribution': int(self.weights.youtube_engagement * normalized['youtube_engagement']),
                    'weight': self.weights.youtube_engagement
                },
                'reddit_activity': {
                    'raw': signals.post_count,
                    'normalized': int(normalized['reddit_activity']),
                    'contribution': int(self.weights.reddit_activity * normalized['reddit_activity']),
                    'weight': self.weights.reddit_activity
                },
                'wikipedia_views': {
                    'raw': signals.daily_views,
                    'normalized': int(normalized['wikipedia_views']),
                    'contribution': int(self.weights.wikipedia_views * normalized['wikipedia_views']),
                    'weight': self.weights.wikipedia_views
                },
                'news_coverage': {
                    'raw': signals.article_count_30d,
                    'normalized': int(normalized['news_coverage']),
                    'contribution': int(self.weights.news_coverage * normalized['news_coverage']),
                    'weight': self.weights.news_coverage
                },
                'news_diversity': {
                    'raw': signals.unique_sources,
                    'normalized': int(normalized['news_diversity']),
                    'contribution': int(self.weights.news_diversity * normalized['news_diversity']),
                    'weight': self.weights.news_diversity
                }
            },
            'rule_applied': self._classify_demand_level(int(demand_score))
        }
    
    def _normalize_signals(self, signals: MarketSignals) -> Dict[str, float]:
        """
        Normalize each signal to 0-100 scale using logarithmic scaling
        for better distribution across orders of magnitude.
        """
        return {
            'trends_volume': self._log_scale(signals.monthly_searches, max_val=100000, scale=100),
            'trends_growth': self._linear_scale(signals.growth_rate_30d, min_val=-0.5, max_val=0.5),
            'youtube_count': self._log_scale(signals.video_count, max_val=10000, scale=100),
            'youtube_engagement': self._log_scale(signals.total_views, max_val=10000000, scale=100),
            'reddit_activity': self._log_scale(signals.post_count, max_val=1000, scale=100),
            'wikipedia_views': self._log_scale(signals.daily_views, max_val=10000, scale=100),
            'news_coverage': self._log_scale(signals.article_count_30d, max_val=500, scale=100),
            'news_diversity': self._linear_scale(signals.unique_sources, min_val=0, max_val=50),
        }
    
    def _log_scale(self, value: float, max_val: float, scale: float = 100) -> float:
        """
        Logarithmic scaling for values that span multiple orders of magnitude.
        
        Maps [0, max_val] → [0, scale] using log transformation.
        """
        if value <= 0:
            return 0.0
        
        # log(value + 1) to handle value=0 gracefully
        # Normalize to [0, scale]
        normalized = (math.log(value + 1) / math.log(max_val + 1)) * scale
        return min(scale, max(0, normalized))
    
    def _linear_scale(
        self,
        value: float,
        min_val: float,
        max_val: float,
        scale: float = 100
    ) -> float:
        """
        Linear scaling for values in a known range.
        
        Maps [min_val, max_val] → [0, scale].
        """
        if value <= min_val:
            return 0.0
        if value >= max_val:
            return scale
        
        normalized = ((value - min_val) / (max_val - min_val)) * scale
        return min(scale, max(0, normalized))
    
    def _calculate_confidence(self, normalized_signals: Dict[str, float]) -> float:
        """
        Calculate confidence based on number of non-zero signals.
        
        More signals = Higher confidence.
        """
        non_zero_signals = sum(1 for v in normalized_signals.values() if v > 0)
        total_signals = len(normalized_signals)
        
        # Base confidence from signal coverage
        coverage_confidence = (non_zero_signals / total_signals) * 100
        
        # Boost if primary signal (trends_volume) is strong
        primary_boost = min(20, normalized_signals['trends_volume'] / 5)
        
        confidence = min(100, coverage_confidence + primary_boost)
        return confidence
    
    def _classify_demand_level(self, score: int) -> str:
        """Classify demand level from composite score"""
        if score >= 80:
            return "ELITE_DEMAND"
        elif score >= 60:
            return "HIGH_DEMAND"
        elif score >= 40:
            return "MODERATE_DEMAND"
        elif score >= 20:
            return "LOW_DEMAND"
        else:
            return "MINIMAL_DEMAND"
