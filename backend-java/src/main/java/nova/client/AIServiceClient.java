package nova.client;

import nova.model.*;
import org.springframework.lang.NonNull;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.http.HttpStatusCode;
import reactor.core.publisher.Mono;

/**
 * HTTP Client for communicating with Python AI Service
 */
@Component
public class AIServiceClient {

    private final WebClient webClient;

    public AIServiceClient(@Value("${ai-service.url}") String aiServiceUrl) {
        this.webClient = WebClient.builder()
                .baseUrl(java.util.Objects.requireNonNull(aiServiceUrl, "AI Service URL must not be null"))
                .build();
    }

    /**
     * Call AI service to generate ideas
     */
    public IdeaGenerationResponse generateIdeas(@NonNull IdeaGenerationRequest request) {
        return webClient.post()
                .uri("/api/ideas/generate")
                .header("Content-Type", "application/json")
                .header("Accept", "application/json")
                .bodyValue(request)
                .retrieve()
                .onStatus(HttpStatusCode::is4xxClientError,
                        response -> Mono.error(
                                new RuntimeException("Client error calling AI Service: " + response.statusCode())))
                .onStatus(HttpStatusCode::is5xxServerError,
                        response -> Mono.error(
                                new RuntimeException("Server error calling AI Service: " + response.statusCode())))
                .bodyToMono(IdeaGenerationResponse.class)
                .block();
    }

    /**
     * Call AI service for scoring (v2)
     */
    public IdeaScoreResponse scoreIdea(@NonNull IdeaScoreRequest request) {
        return webClient.post()
                .uri("/api/v2/score-idea")
                .header("Content-Type", "application/json")
                .header("Accept", "application/json")
                .bodyValue(request)
                .retrieve()
                .onStatus(HttpStatusCode::is4xxClientError,
                        response -> Mono.error(new RuntimeException(
                                "Client error calling AI Service (Scoring): " + response.statusCode())))
                .onStatus(HttpStatusCode::is5xxServerError,
                        response -> Mono.error(new RuntimeException(
                                "Server error calling AI Service (Scoring): " + response.statusCode())))
                .bodyToMono(IdeaScoreResponse.class)
                .block();
    }

    /**
     * Call AI service for explanation (v2)
     */
    public ExplanationResponse explainScore(@NonNull ExplainRequest request) {
        return webClient.post()
                .uri("/api/v2/explain-score")
                .header("Content-Type", "application/json")
                .header("Accept", "application/json")
                .bodyValue(request)
                .retrieve()
                .onStatus(HttpStatusCode::is4xxClientError,
                        response -> Mono.error(new RuntimeException(
                                "Client error calling AI Service (Explanation): " + response.statusCode())))
                .onStatus(HttpStatusCode::is5xxServerError,
                        response -> Mono.error(new RuntimeException(
                                "Server error calling AI Service (Explanation): " + response.statusCode())))
                .bodyToMono(ExplanationResponse.class)
                .block();
    }

    /**
     * Call AI service for unit economics verification
     */
    public UnitEconomicsResponse checkUnitEconomics(@NonNull UnitEconomicsInput inputs) {
        return webClient.post()
                .uri("/api/v2/verification/economics")
                .header("Content-Type", "application/json")
                .bodyValue(inputs)
                .retrieve()
                .onStatus(HttpStatusCode::is4xxClientError,
                        response -> Mono.error(new RuntimeException(
                                "Client error calling AI Service (Economics): " + response.statusCode())))
                .onStatus(HttpStatusCode::is5xxServerError,
                        response -> Mono.error(new RuntimeException(
                                "Server error calling AI Service (Economics): " + response.statusCode())))
                .bodyToMono(UnitEconomicsResponse.class)
                .block();
    }

    /**
     * Call AI service for tech feasibility (V2 Interaction Matrix)
     */
    public TechFeasibilityResponse checkTechFeasibility(@NonNull TechFeasibilityRequest request) {
        return webClient.post()
                .uri("/api/v2/verification/feasibility")
                .header("Content-Type", "application/json")
                .bodyValue(request)
                .retrieve()
                .onStatus(HttpStatusCode::is4xxClientError,
                        response -> Mono.error(new RuntimeException(
                                "Client error calling AI Service (Feasibility): " + response.statusCode())))
                .onStatus(HttpStatusCode::is5xxServerError,
                        response -> Mono.error(new RuntimeException(
                                "Server error calling AI Service (Feasibility): " + response.statusCode())))
                .bodyToMono(TechFeasibilityResponse.class)
                .block();
    }
}
