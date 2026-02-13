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
public class IdeaScoreRequest {

    @JsonProperty("idea_name")
    private String ideaName;

    @JsonProperty("idea_description")
    private String ideaDescription;

    @JsonProperty("target_market")
    private String targetMarket;

    @JsonProperty("monthly_searches")
    private int monthlySearches;

    @JsonProperty("growth_rate_30d")
    private double growthRate30d;

    @JsonProperty("youtube_video_count")
    private int youtubeVideoCount;

    @JsonProperty("youtube_total_views")
    private int youtubeTotalViews;

    @JsonProperty("reddit_post_count")
    private int redditPostCount;

    @JsonProperty("reddit_total_score")
    private int redditTotalScore;

    @JsonProperty("wikipedia_daily_views")
    private int wikipediaDailyViews;

    @JsonProperty("news_articles_30d")
    private int newsArticles30d;

    @JsonProperty("news_unique_sources")
    private int newsUniqueSources;

    @JsonProperty("trend_values_30d")
    private List<Double> trendValues30d;

    @JsonProperty("trend_values_90d")
    private List<Double> trendValues90d;

    @JsonProperty("trend_values_180d")
    private List<Double> trendValues180d;

    @JsonProperty("competitor_count")
    private int competitorCount;

    @JsonProperty("top_player_market_shares")
    private List<Double> topPlayerMarketShares;

    @JsonProperty("new_entrants_12m")
    private int newEntrants12m;

    @JsonProperty("exits_12m")
    private int exits12m;

    @JsonProperty("substitute_count")
    private int substituteCount;

    @JsonProperty("tech_stack")
    private TechStackInput techStack;

    @JsonProperty("estimated_capital_needed")
    private Integer estimatedCapitalNeeded;

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class TechStackInput {
        @JsonProperty("technologies")
        private List<String> technologies;

        @JsonProperty("team_experience")
        private Map<String, String> teamExperience;
    }
}
