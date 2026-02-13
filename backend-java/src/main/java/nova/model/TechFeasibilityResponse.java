package nova.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class TechFeasibilityResponse {

    @JsonProperty("idea_name")
    private String ideaName;

    @JsonProperty("execution_score")
    private int executionScore;

    @JsonProperty("complexity_rating")
    private String complexityRating;

    @JsonProperty("technologies_analyzed")
    private List<String> technologiesAnalyzed;

    @JsonProperty("risk_factors")
    private List<String> riskFactors;

    @JsonProperty("synergy_bonus")
    private int synergyBonus;

    @JsonProperty("innovation_level")
    private String innovationLevel;
}
