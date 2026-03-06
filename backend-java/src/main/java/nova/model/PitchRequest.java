package nova.model;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Request model for Pitch Deck generation
 */
public class PitchRequest {

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

    @JsonProperty("business_model")
    private String businessModel;

    // Constructors
    public PitchRequest() {
    }

    public PitchRequest(String ideaName, String ideaDescription, String targetMarket, String problem, String solution,
            String businessModel) {
        this.ideaName = ideaName;
        this.ideaDescription = ideaDescription;
        this.targetMarket = targetMarket;
        this.problem = problem;
        this.solution = solution;
        this.businessModel = businessModel;
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

    public String getBusinessModel() {
        return businessModel;
    }

    public void setBusinessModel(String businessModel) {
        this.businessModel = businessModel;
    }
}
