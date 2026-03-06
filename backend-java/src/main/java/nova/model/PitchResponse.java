package nova.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

/**
 * Response model for Pitch Deck generation
 */
public class PitchResponse {

    @JsonProperty("slides")
    private List<Map<String, String>> slides;

    @JsonProperty("presentation_notes")
    private String presentationNotes;

    // Constructors
    public PitchResponse() {
    }

    public PitchResponse(List<Map<String, String>> slides, String presentationNotes) {
        this.slides = slides;
        this.presentationNotes = presentationNotes;
    }

    // Getters and Setters
    public List<Map<String, String>> getSlides() {
        return slides;
    }

    public void setSlides(List<Map<String, String>> slides) {
        this.slides = slides;
    }

    public String getPresentationNotes() {
        return presentationNotes;
    }

    public void setPresentationNotes(String presentationNotes) {
        this.presentationNotes = presentationNotes;
    }
}
