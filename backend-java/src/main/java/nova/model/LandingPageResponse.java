package nova.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class LandingPageResponse {

    @JsonProperty("html_content")
    private String htmlContent;

    @JsonProperty("preview_url")
    private String previewUrl;
}
