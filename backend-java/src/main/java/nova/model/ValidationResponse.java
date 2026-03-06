package nova.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import java.util.Map;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class ValidationResponse {

    @JsonProperty("idea_name")
    private String ideaName;

    private String sector;

    @JsonProperty("market_validation")
    private Map<String, Object> marketValidation;

    @JsonProperty("social_proof")
    private Map<String, Object> socialProof;

    @JsonProperty("execution_risk")
    private Map<String, Object> executionRisk;

    @JsonProperty("sector_signals")
    private Map<String, Object> sectorSignals;

    @JsonProperty("overall_confidence")
    private int overallConfidence;

    private String verdict;

    @JsonProperty("data_quality")
    private Map<String, Object> dataQuality;
}
