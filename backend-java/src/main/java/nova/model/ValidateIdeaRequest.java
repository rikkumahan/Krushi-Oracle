package nova.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class ValidateIdeaRequest {

    @JsonProperty("idea_name")
    private String ideaName;

    @JsonProperty("idea_description")
    private String ideaDescription;

    private List<String> keywords = new java.util.ArrayList<>();

    private String sector;

    @JsonProperty("tech_stack")
    private List<String> techStack = new java.util.ArrayList<>();

    @JsonProperty("team_size")
    private int teamSize;

    @JsonProperty("timeline_months")
    private int timelineMonths;

    @JsonProperty("budget_usd")
    private double budgetUsd;
}
