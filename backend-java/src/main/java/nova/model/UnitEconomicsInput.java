package nova.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class UnitEconomicsInput {

    @JsonProperty("arpu_monthly")
    private double arpuMonthly;

    @JsonProperty("gross_margin_pct")
    private double grossMarginPct;

    @JsonProperty("churn_rate_monthly")
    private double churnRateMonthly;

    @JsonProperty("cpc")
    private double cpc;

    @JsonProperty("conversion_rate_landing")
    private double conversionRateLanding;

    @JsonProperty("conversion_rate_payment")
    private double conversionRatePayment;
}
