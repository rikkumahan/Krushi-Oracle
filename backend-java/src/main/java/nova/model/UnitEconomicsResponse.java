package nova.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class UnitEconomicsResponse {

    private double ltv;
    private double cac;

    @JsonProperty("ltv_cac_ratio")
    private double ltvCacRatio;

    @JsonProperty("payback_months")
    private double paybackMonths;

    @JsonProperty("is_viable")
    private boolean isViable;

    @JsonProperty("viability_score")
    private int viabilityScore;

    @JsonProperty("kill_reason")
    private String killReason;
}
