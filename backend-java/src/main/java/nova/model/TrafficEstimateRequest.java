package nova.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class TrafficEstimateRequest {

    @JsonProperty("idea_name")
    private String ideaName;

    @JsonProperty("idea_description")
    private String ideaDescription;

    private String industry;

    @JsonProperty("target_audience")
    private String targetAudience;

    private double budget;

    private List<String> keywords;

    @JsonProperty("cpc_override")
    private Double cpcOverride;
}
