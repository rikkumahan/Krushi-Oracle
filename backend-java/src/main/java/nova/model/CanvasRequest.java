package nova.model;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Request model for Lean Canvas generation
 */
public class CanvasRequest {

    @JsonProperty("idea_name")
    private String ideaName;

    @JsonProperty("idea_description")
    private String ideaDescription;

    @JsonProperty("target_market")
    private String targetMarket;

    @JsonProperty("problem")
    private String problem;

    @JsonProperty("solution")
    private String solution;

    // Constructors
    public CanvasRequest() {
    }

    public CanvasRequest(String ideaName, String ideaDescription, String targetMarket, String problem,
            String solution) {
        this.ideaName = ideaName;
        this.ideaDescription = ideaDescription;
        this.targetMarket = targetMarket;
        this.problem = problem;
        this.solution = solution;
    }

    // Getters and Setters
    public String getIdeaName() {
        return ideaName;
    }

    public void setIdeaName(String ideaName) {
        this.ideaName = ideaName;
    }

    public String getIdeaDescription() {
        return ideaDescription;
    }

    public void setIdeaDescription(String ideaDescription) {
        this.ideaDescription = ideaDescription;
    }

    public String getTargetMarket() {
        return targetMarket;
    }

    public void setTargetMarket(String targetMarket) {
        this.targetMarket = targetMarket;
    }

    public String getProblem() {
        return problem;
    }

    public void setProblem(String problem) {
        this.problem = problem;
    }

    public String getSolution() {
        return solution;
    }

    public void setSolution(String solution) {
        this.solution = solution;
    }
}
