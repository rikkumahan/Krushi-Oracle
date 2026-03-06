package nova.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class ComparisonResponse {

    @JsonProperty("similar_companies")
    private List<SimilarCompany> similarCompanies;

    @JsonProperty("search_keywords")
    private List<String> searchKeywords;

    @JsonProperty("total_found")
    private int totalFound;

    @JsonProperty("data_quality_score")
    private double dataQualityScore;

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class SimilarCompany {
        private String name;
        private String description;

        @JsonProperty("business_model")
        private String businessModel;

        private String outcome;

        @JsonProperty("outcome_year")
        private Integer outcomeYear;

        @JsonProperty("funding_raised_usd")
        private Long fundingRaisedUsd;

        @JsonProperty("exit_value_usd")
        private Long exitValueUsd;

        @JsonProperty("founded_year")
        private Integer foundedYear;

        @JsonProperty("time_to_exit_years")
        private Double timeToExitYears;

        @JsonProperty("key_lesson")
        private String keyLesson;

        @JsonProperty("similarity_score")
        private double similarityScore;

        @JsonProperty("data_sources")
        private List<String> dataSources;

        private String url;
    }
}
