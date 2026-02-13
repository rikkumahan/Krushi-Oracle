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
public class ExplanationResponse {

    private String answer;

    @JsonProperty("tools_used")
    private List<String> toolsUsed;

    @JsonProperty("data_cited")
    private List<Map<String, Object>> dataCited;

    private String confidence;
}
