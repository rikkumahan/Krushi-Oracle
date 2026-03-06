package nova.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

public class ChatResponse {
    @JsonProperty("reply")
    private String reply;

    @JsonProperty("suggested_actions")
    private List<String> suggestedActions;

    @JsonProperty("extracted_data")
    private Map<String, Object> extractedData;

    @JsonProperty("confidence")
    private double confidence;

    @JsonProperty("tool_results")
    private List<Map<String, Object>> toolResults;

    public String getReply() {
        return reply;
    }

    public void setReply(String reply) {
        this.reply = reply;
    }

    public List<String> getSuggestedActions() {
        return suggestedActions;
    }

    public void setSuggestedActions(List<String> suggestedActions) {
        this.suggestedActions = suggestedActions;
    }

    public Map<String, Object> getExtractedData() {
        return extractedData;
    }

    public void setExtractedData(Map<String, Object> extractedData) {
        this.extractedData = extractedData;
    }

    public double getConfidence() {
        return confidence;
    }

    public void setConfidence(double confidence) {
        this.confidence = confidence;
    }

    public List<Map<String, Object>> getToolResults() {
        return toolResults;
    }

    public void setToolResults(List<Map<String, Object>> toolResults) {
        this.toolResults = toolResults;
    }
}
