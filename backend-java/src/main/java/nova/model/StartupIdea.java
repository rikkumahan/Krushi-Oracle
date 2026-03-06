package nova.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class StartupIdea {
    private String id;
    private String name;
    private String tagline;
    private String description;
    private String industry;

    @JsonProperty("target_customer")
    private String targetCustomer;

    @JsonProperty("problem_solved")
    private String problemSolved;

    @JsonProperty("mvp_features")
    private List<MVPFeature> mvpFeatures;

    @JsonProperty("business_model")
    private BusinessModel businessModel;

    @JsonProperty("moonshot_channel")
    private String moonshotChannel;

    @JsonProperty("estimated_initial_cost")
    private int estimatedInitialCost;

    private IdeaScore score;

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
        @JsonProperty("revenue_streams")
        private List<String> revenueStreams;

        @JsonProperty("key_partners")
        private List<String> keyPartners;

        @JsonProperty("cost_structure")
        private List<String> costStructure;

        @JsonProperty("value_proposition")
        private String valueProposition;

        @JsonProperty("customer_segments")
        private List<String> customerSegments;

        private List<String> channels;
    }

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class IdeaScore {
        @JsonProperty("market_size")
        private int marketSize;

        private int differentiation;

        @JsonProperty("execution_complexity")
        private int executionComplexity;

        @JsonProperty("capital_intensity")
        private int capitalIntensity;

        private int overall;
    }
}
