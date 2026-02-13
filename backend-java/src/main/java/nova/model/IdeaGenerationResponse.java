package nova.model;

import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import java.util.List;

/**
 * Response DTO for idea generation
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class IdeaGenerationResponse {

    private List<StartupIdea> ideas;
    private String generationId;
    private String inputSummary;

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class StartupIdea {
        private String id;
        private String name;
        private String tagline;
        private String description;
        private String targetCustomer;
        private String problemSolved;
        private List<MVPFeature> mvpFeatures;
        private BusinessModel businessModel;
        private String moonshotChannel;
        private int estimatedInitialCost;
        private IdeaScore score;
    }

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class MVPFeature {
        private String name;
        private String description;
        private int priority;
    }

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class BusinessModel {
        private List<String> revenueStreams;
        private List<String> keyPartners;
        private List<String> costStructure;
        private String valueProposition;
        private List<String> customerSegments;
        private List<String> channels;
    }

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class IdeaScore {
        private int marketSize;
        private int differentiation;
        private int executionComplexity;
        private int capitalIntensity;
        private int overall;
    }
}
