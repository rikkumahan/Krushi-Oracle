package nova.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class ExplainRequest {

    @JsonProperty("idea_name")
    private String ideaName;

    private String question;

    @JsonProperty("session_id")
    private String sessionId;
}
