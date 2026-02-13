"""
Innovation 2: Time-Series Momentum Analysis

Analyzes market momentum using time-series data to identify
growth patterns, acceleration, and volatility.

100% deterministic - NO LLM usage.
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import statistics


@dataclass
class TimeSeriesData:
    """Time-series data points"""
    values: List[float]  # Ordered from oldest to newest
    period_days: int     # Period length (30, 90, 180, etc.)
    
    def __post_init__(self):
        """Validate data"""
        assert len(self.values) > 0, "Must have at least one data point"
        assert self.period_days > 0, "Period must be positive"


class MomentumAnalyzer:
    """Analyzes market momentum using time-series data"""
    
    def analyze_momentum(
        self,
        trends_30d: TimeSeriesData,
        trends_90d: TimeSeriesData,
        trends_180d: TimeSeriesData
    ) -> Dict[str, Any]:
        """
        Analyze momentum across multiple time windows.
        
        Returns:
        - momentum_score: 0-100 composite momentum score
        - trend_pattern: Classification (RISING_FAST, RISING, STABLE, etc.)
        - breakdown: Per-window analysis
        - volatility: Market stability indicator
        """
        # Calculate metrics for each window
        short_term = self._analyze_window(trends_30d)
        medium_term = self._analyze_window(trends_90d)
        long_term = self._analyze_window(trends_180d)
        
        # Calculate weighted momentum (favor recent data)
        weighted_slope = (
            0.5 * short_term['slope'] +
            0.3 * medium_term['slope'] +
            0.2 * long_term['slope']
        )
        
        # Calculate overall volatility
        avg_volatility = (
            0.5 * short_term['volatility'] +
            0.3 * medium_term['volatility'] +
            0.2 * long_term['volatility']
        )
        
        # Classify pattern
        trend_pattern = self._classify_pattern(
            weighted_slope,
            short_term['acceleration'],
            avg_volatility
        )
        
        # Calculate momentum score
        momentum_score = self._calculate_momentum_score(
            weighted_slope,
            avg_volatility,
            trend_pattern
        )
        
        return {
            'momentum_score': int(momentum_score),
            'trend_pattern': trend_pattern,
            'weighted_slope': round(weighted_slope, 4),
            'volatility': round(avg_volatility, 2),
            'breakdown': {
                'short_term_30d': {
                    'slope': round(short_term['slope'], 4),
                    'slope_percentage': f"{short_term['slope']*100:.1f}%",
                    'acceleration': round(short_term['acceleration'], 6),
                    'volatility': round(short_term['volatility'], 2),
                    'trend_strength': short_term['trend_strength']
                },
                'medium_term_90d': {
                    'slope': round(medium_term['slope'], 4),
                    'slope_percentage': f"{medium_term['slope']*100:.1f}%",
                    'acceleration': round(medium_term['acceleration'], 6),
                    'volatility': round(medium_term['volatility'], 2),
                    'trend_strength': medium_term['trend_strength']
                },
                'long_term_180d': {
                    'slope': round(long_term['slope'], 4),
                    'slope_percentage': f"{long_term['slope']*100:.1f}%",
                    'acceleration': round(long_term['acceleration'], 6),
                    'volatility': round(long_term['volatility'], 2),
                    'trend_strength': long_term['trend_strength']
                }
            },
            'interpretation': self._interpret_momentum(
                trend_pattern,
                weighted_slope,
                avg_volatility
            )
        }
    
    def _analyze_window(self, data: TimeSeriesData) -> Dict[str, Any]:
        """
        Analyze a single time window.
        
        Calculates:
        - Slope (linear regression)
        - Acceleration (slope of slope)
        - Volatility (coefficient of variation)
        - Trend strength (R² measure)
        """
        values = data.values
        n = len(values)
        
        if n < 2:
            return {
                'slope': 0.0,
                'acceleration': 0.0,
                'volatility': 0.0,
                'trend_strength': 'INSUFFICIENT_DATA'
            }
        
        # Calculate slope using linear regression
        slope = self._calculate_slope(values)
        
        # Calculate acceleration (second derivative)
        acceleration = self._calculate_acceleration(values)
        
        # Calculate volatility (coefficient of variation)
        volatility = self._calculate_volatility(values)
        
        # Classify trend strength
        trend_strength = self._classify_trend_strength(slope, volatility)
        
        return {
            'slope': slope,
            'acceleration': acceleration,
            'volatility': volatility,
            'trend_strength': trend_strength
        }
    
    def _calculate_slope(self, values: List[float]) -> float:
        """
        Calculate slope using simple linear regression.
        
        Returns slope as decimal (e.g., 0.15 for +15% per period)
        """
        n = len(values)
        if n < 2:
            return 0.0
        
        # Use index as x-axis (0, 1, 2, ...)
        x = list(range(n))
        y = values
        
        # Calculate means
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        # Calculate slope: β = Σ((x - x̄)(y - ȳ)) / Σ((x - x̄)²)
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        
        # Normalize to percentage change relative to mean
        if y_mean > 0:
            normalized_slope = slope / y_mean
        else:
            normalized_slope = 0.0
        
        return normalized_slope
    
    def _calculate_acceleration(self, values: List[float]) -> float:
        """
        Calculate acceleration (second derivative).
        
        Measures if growth is speeding up or slowing down.
        """
        n = len(values)
        if n < 3:
            return 0.0
        
        # Split into two halves
        mid = n // 2
        first_half = values[:mid]
        second_half = values[mid:]
        
        # Calculate slope for each half
        slope_first = self._calculate_slope(first_half)
        slope_second = self._calculate_slope(second_half)
        
        # Acceleration is the change in slope
        acceleration = slope_second - slope_first
        
        return acceleration
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """
        Calculate volatility using coefficient of variation.
        
        CV = (standard deviation / mean) * 100
        
        Returns percentage (0-100+)
        """
        if len(values) < 2:
            return 0.0
        
        mean = statistics.mean(values)
        if mean == 0:
            return 0.0
        
        stdev = statistics.stdev(values)
        cv = (stdev / mean) * 100
        
        return cv
    
    def _classify_trend_strength(self, slope: float, volatility: float) -> str:
        """Classify trend strength based on slope and volatility"""
        abs_slope = abs(slope)
        
        if volatility > 50:
            return "VOLATILE"  # Too noisy to trust
        elif abs_slope > 0.20:
            return "STRONG"
        elif abs_slope > 0.10:
            return "MODERATE"
        elif abs_slope > 0.05:
            return "WEAK"
        else:
            return "FLAT"
    
    def _classify_pattern(
        self,
        slope: float,
        acceleration: float,
        volatility: float
    ) -> str:
        """
        Classify overall trend pattern.
        
        Patterns:
        - RISING_FAST: Strong upward momentum
        - RISING: Moderate upward momentum
        - STABLE: Flat with low volatility
        - DECLINING: Downward momentum
        - COLLAPSING: Rapid decline
        - VOLATILE: High volatility, unreliable
        """
        if volatility > 60:
            return "VOLATILE"
        
        if slope > 0.20:
            return "RISING_FAST"
        elif slope > 0.10:
            return "RISING"
        elif slope > -0.05:
            return "STABLE"
        elif slope > -0.20:
            return "DECLINING"
        else:
            return "COLLAPSING"
    
    def _calculate_momentum_score(
        self,
        slope: float,
        volatility: float,
        pattern: str
    ) -> float:
        """
        Calculate 0-100 momentum score.
        
        Higher score = Better momentum for startup opportunity
        """
        # Base score from slope
        if slope > 0.20:
            base_score = 90
        elif slope > 0.10:
            base_score = 75
        elif slope > 0:
            base_score = 60
        elif slope > -0.10:
            base_score = 45
        else:
            base_score = 20
        
        # Penalty for high volatility (risky/unpredictable)
        if volatility > 60:
            volatility_penalty = 30
        elif volatility > 40:
            volatility_penalty = 15
        elif volatility > 20:
            volatility_penalty = 5
        else:
            volatility_penalty = 0
        
        # Calculate final score
        score = base_score - volatility_penalty
        
        return max(0, min(100, score))
    
    def _interpret_momentum(
        self,
        pattern: str,
        slope: float,
        volatility: float
    ) -> str:
        """Generate human-readable interpretation"""
        interpretations = {
            "RISING_FAST": f"Strong upward momentum (+{slope*100:.1f}%/period). Market is rapidly growing.",
            "RISING": f"Positive momentum (+{slope*100:.1f}%/period). Steady market growth.",
            "STABLE": f"Stable market ({slope*100:+.1f}%/period). Low volatility, predictable demand.",
            "DECLINING": f"Declining momentum ({slope*100:.1f}%/period). Market interest is waning.",
            "COLLAPSING": f"Rapid decline ({slope*100:.1f}%/period). Market may be saturating or dying.",
            "VOLATILE": f"High volatility ({volatility:.0f}% CV). Momentum is unpredictable and risky."
        }
        
        return interpretations.get(pattern, f"Pattern: {pattern}")
