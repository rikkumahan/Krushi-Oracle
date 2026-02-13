package nova.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import java.util.List;
import java.util.Map;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class IdeaScoreResponse {

    private boolean success;

    @JsonProperty("mvs_score")
    private int mvsScore;

    @JsonProperty("mvs_grade")
    private String mvsGrade;

    @JsonProperty("validation_class")
    private String validationClass;

    private List<String> recommendations;

    @JsonProperty("dimension_scores")
    private Map<String, Integer> dimensionScores;

    @JsonProperty("audit_trail_url")
    private String auditTrailUrl;
}
