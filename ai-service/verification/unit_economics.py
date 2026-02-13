from pydantic import BaseModel, Field
from typing import Optional

class UnitEconomicsInput(BaseModel):
    # Revenue
    arpu_monthly: float = Field(..., description="Average Revenue Per User (Monthly)")
    gross_margin_pct: float = Field(..., description="Gross Margin Percentage (0.0 - 1.0)")
    
    # Retention
    churn_rate_monthly: float = Field(..., description="Monthly Churn Rate (0.0 - 1.0)")
    
    # Acquisition
    cpc: float = Field(..., description="Cost Per Click")
    conversion_rate_landing: float = Field(..., description="Landing Page Conversion Rate (0.0 - 1.0)")
    conversion_rate_payment: float = Field(..., description="Payment Conversion Rate (0.0 - 1.0)")

class UnitEconomicsResult(BaseModel):
    ltv: float
    cac: float
    ltv_cac_ratio: float
    payback_months: float
    is_viable: bool
    viability_score: int # 0-100
    kill_reason: Optional[str] = None

class UnitEconomicsSimulator:
    
    MIN_LTV_CAC_RATIO = 3.0
    MVP_THRESHOLD_RATIO = 1.5
    
    @staticmethod
    def calculate(inputs: UnitEconomicsInput) -> UnitEconomicsResult:
        # 1. Calculate CAC
        # Visitors needed for 1 customer = 1 / (ConvLanding * ConvPayment)
        visit_conv = inputs.conversion_rate_landing * inputs.conversion_rate_payment
        visitors_per_customer = 1 / visit_conv if visit_conv > 0 else 999999.0
        cac = inputs.cpc * visitors_per_customer
        
        # 2. Calculate LTV
        # Lifetime months = 1 / Churn
        lifetime_months = 1 / inputs.churn_rate_monthly if inputs.churn_rate_monthly > 0 else 60.0 # Cap at 5 years
        gross_profit_monthly = inputs.arpu_monthly * inputs.gross_margin_pct
        ltv = gross_profit_monthly * lifetime_months
        
        # 3. Ratios
        ratio = ltv / cac if cac > 0 else 0.0
        payback = cac / gross_profit_monthly if gross_profit_monthly > 0 else 999.0
        
        # 4. Viability
        is_viable = ratio >= UnitEconomicsSimulator.MVP_THRESHOLD_RATIO
        
        score = 0
        if ratio >= 5.0: score = 100
        elif ratio >= 3.0: score = 80
        elif ratio >= 1.5: score = 50
        elif ratio >= 1.0: score = 20
        else: score = 0
        
        reason = None
        if not is_viable:
            if ratio < 1.0: reason = "Negative Unit Economics (Lose money on every customer)"
            else: reason = f"LTV:CAC {ratio:.1f} is below MVP threshold ({UnitEconomicsSimulator.MVP_THRESHOLD_RATIO})"
            
        return UnitEconomicsResult(
            ltv=round(ltv, 2),
            cac=round(cac, 2),
            ltv_cac_ratio=round(ratio, 2),
            payback_months=round(payback, 1),
            is_viable=is_viable,
            viability_score=score,
            kill_reason=reason
        )
