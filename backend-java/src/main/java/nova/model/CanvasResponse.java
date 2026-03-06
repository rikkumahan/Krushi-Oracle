package nova.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Map;

/**
 * Response model for Lean Canvas generation
 */
public class CanvasResponse {

    @JsonProperty("canvas_data")
    private Map<String, Object> canvasData;

    @JsonProperty("html_view")
    private String htmlView;

    // Constructors
    public CanvasResponse() {
    }

    public CanvasResponse(Map<String, Object> canvasData, String htmlView) {
        this.canvasData = canvasData;
        this.htmlView = htmlView;
    }

    // Getters and Setters
    public Map<String, Object> getCanvasData() {
        return canvasData;
    }

    public void setCanvasData(Map<String, Object> canvasData) {
        this.canvasData = canvasData;
    }

    public String getHtmlView() {
        return htmlView;
    }

    public void setHtmlView(String htmlView) {
        this.htmlView = htmlView;
    }
}
