package nova.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class LandingPageRequest {

    @JsonProperty("idea_name")
    private String ideaName;

    private String tagline;
    private String description;

    @JsonProperty("target_audience")
    private String targetAudience;

    private List<String> features;

    @JsonProperty("style_preference")
    private String stylePreference;
}
