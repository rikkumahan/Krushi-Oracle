package nova.model;

import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import java.util.List;

/**
 * Response DTO for idea generation
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class IdeaGenerationResponse {

    private List<StartupIdea> ideas;
    private String generationId;
    private String inputSummary;
}
