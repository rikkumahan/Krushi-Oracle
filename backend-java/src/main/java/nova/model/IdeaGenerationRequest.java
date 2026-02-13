package nova.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

/**
 * Request DTO for idea generation
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class IdeaGenerationRequest {

    @JsonProperty("wizard_input")
    private WizardInput wizardInput;

    @JsonProperty("num_ideas")
    private int numIdeas = 5;

    @JsonProperty("contrarian_override")
    private boolean contrarianOverride = false;

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class WizardInput {
        @JsonProperty("industry")
        private String industry;

        @JsonProperty("target_audience")
        private String targetAudience;

        @JsonProperty("skill_level")
        private String skillLevel;

        @JsonProperty("budget")
        private int budget;

        @JsonProperty("time_frame")
        private String timeFrame;

        private String interests;
        private String location;
    }
}
