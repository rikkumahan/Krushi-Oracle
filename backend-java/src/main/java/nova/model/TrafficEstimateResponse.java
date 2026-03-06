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
public class TrafficEstimateResponse {

    @JsonProperty("estimated_cpc")
    private double estimatedCpc;

    @JsonProperty("estimated_clicks")
    private int estimatedClicks;

    @JsonProperty("confidence_score")
    private int confidenceScore;

    @JsonProperty("search_volume_trend")
    private String searchVolumeTrend;

    @JsonProperty("recommended_channels")
    private List<String> recommendedChannels;

    @JsonProperty("keywords_analyzed")
    private List<String> keywordsAnalyzed;

    @JsonProperty("trend_insights")
    private Map<String, Object> trendInsights;
}
