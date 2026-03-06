package nova.client;

import nova.model.*;
import org.springframework.lang.NonNull;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.http.HttpStatusCode;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

/**
 * HTTP Client for communicating with Python AI Service
 */
@Component
public class AIServiceClient {

        private final WebClient webClient;

        public AIServiceClient(@Value("${ai-service.url}") String aiServiceUrl) {
                this.webClient = WebClient.builder()
                                .baseUrl(java.util.Objects.requireNonNull(aiServiceUrl,
                                                "AI Service URL must not be null"))
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
                                                                new RuntimeException("Client error calling AI Service: "
                                                                                + response.statusCode())))
                                .onStatus(HttpStatusCode::is5xxServerError,
                                                response -> Mono.error(
                                                                new RuntimeException("Server error calling AI Service: "
                                                                                + response.statusCode())))
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
                                                                "Client error calling AI Service (Scoring): "
                                                                                + response.statusCode())))
                                .onStatus(HttpStatusCode::is5xxServerError,
                                                response -> Mono.error(new RuntimeException(
                                                                "Server error calling AI Service (Scoring): "
                                                                                + response.statusCode())))
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
                                                                "Client error calling AI Service (Explanation): "
                                                                                + response.statusCode())))
                                .onStatus(HttpStatusCode::is5xxServerError,
                                                response -> Mono.error(new RuntimeException(
                                                                "Server error calling AI Service (Explanation): "
                                                                                + response.statusCode())))
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
                                                                "Client error calling AI Service (Economics): "
                                                                                + response.statusCode())))
                                .onStatus(HttpStatusCode::is5xxServerError,
                                                response -> Mono.error(new RuntimeException(
                                                                "Server error calling AI Service (Economics): "
                                                                                + response.statusCode())))
                                .bodyToMono(UnitEconomicsResponse.class)
                                .block();
        }

        /**
         * Call AI service for tech feasibility (V2 Interaction Matrix)
         */
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
                                                                "Client error calling AI Service (Feasibility): "
                                                                                + response.statusCode())))
                                .onStatus(HttpStatusCode::is5xxServerError,
                                                response -> Mono.error(new RuntimeException(
                                                                "Server error calling AI Service (Feasibility): "
                                                                                + response.statusCode())))
                                .bodyToMono(TechFeasibilityResponse.class)
                                .block();
        }

        /**
         * Call AI service for universal validation
         */
        public ValidationResponse validateStartupIdea(@NonNull ValidateIdeaRequest request) {
                return webClient.post()
                                .uri("/api/v2/validation/validate")
                                .header("Content-Type", "application/json")
                                .bodyValue(request)
                                .retrieve()
                                .onStatus(HttpStatusCode::is4xxClientError,
                                                response -> Mono.error(new RuntimeException(
                                                                "Client error calling AI Service (Validation): "
                                                                                + response.statusCode())))
                                .onStatus(HttpStatusCode::is5xxServerError,
                                                response -> Mono.error(new RuntimeException(
                                                                "Server error calling AI Service (Validation): "
                                                                                + response.statusCode())))
                                .bodyToMono(ValidationResponse.class)
                                .block();
        }

        /**
         * Call AI service for smart comparison
         */
        public ComparisonResponse findSimilarCompanies(@NonNull ComparisonRequest request) {
                return webClient.post()
                                .uri("/api/v2/comparison/find-similar")
                                .header("Content-Type", "application/json")
                                .bodyValue(request)
                                .retrieve()
                                .onStatus(HttpStatusCode::is4xxClientError,
                                                response -> Mono.error(new RuntimeException(
                                                                "Client error calling AI Service (Comparison): "
                                                                                + response.statusCode())))
                                .onStatus(HttpStatusCode::is5xxServerError,
                                                response -> Mono.error(new RuntimeException(
                                                                "Server error calling AI Service (Comparison): "
                                                                                + response.statusCode())))
                                .bodyToMono(ComparisonResponse.class)
                                .block();
        }

        /**
         * Call AI service for traffic estimation
         */
        public TrafficEstimateResponse estimateTraffic(@NonNull TrafficEstimateRequest request) {
                return webClient.post()
                                .uri("/api/v2/verification/traffic")
                                .header("Content-Type", "application/json")
                                .bodyValue(request)
                                .retrieve()
                                .onStatus(HttpStatusCode::is4xxClientError,
                                                response -> Mono.error(new RuntimeException(
                                                                "Client error calling AI Service (Traffic): "
                                                                                + response.statusCode())))
                                .onStatus(HttpStatusCode::is5xxServerError,
                                                response -> Mono.error(new RuntimeException(
                                                                "Server error calling AI Service (Traffic): "
                                                                                + response.statusCode())))
                                .bodyToMono(TrafficEstimateResponse.class)
                                .block();
        }

        /**
         * Call AI service for landing page generation
         */
        public LandingPageResponse generateLandingPage(@NonNull LandingPageRequest request) {
                return webClient.post()
                                .uri("/api/v2/assets/landing-page")
                                .header("Content-Type", "application/json")
                                .bodyValue(request)
                                .retrieve()
                                .onStatus(HttpStatusCode::is4xxClientError,
                                                response -> Mono.error(new RuntimeException(
                                                                "Client error calling AI Service (Landing Page): "
                                                                                + response.statusCode())))
                                .onStatus(HttpStatusCode::is5xxServerError,
                                                response -> Mono.error(new RuntimeException(
                                                                "Server error calling AI Service (Landing Page): "
                                                                                + response.statusCode())))
                                .bodyToMono(LandingPageResponse.class)
                                .block();
        }

        /**
         * Call AI service for chat (V2 Orchestrator)
         */
        public ChatResponse chat(@NonNull ChatRequest request) {
                return webClient.post()
                                .uri("/api/v2/chat/")
                                .header("Content-Type", "application/json")
                                .bodyValue(request)
                                .retrieve()
                                .onStatus(HttpStatusCode::is4xxClientError,
                                                response -> Mono.error(new RuntimeException(
                                                                "Client error calling AI Service (Chat): "
                                                                                + response.statusCode())))
                                .onStatus(HttpStatusCode::is5xxServerError,
                                                response -> Mono.error(new RuntimeException(
                                                                "Server error calling AI Service (Chat): "
                                                                                + response.statusCode())))
                                .bodyToMono(ChatResponse.class)
                                .block();
        }

        /**
         * Call AI service for streaming chat (SSE)
         */
        public Flux<String> chatStream(@NonNull ChatRequest request) {
                return webClient.post()
                                .uri("/api/v2/chat/stream")
                                .header("Content-Type", "application/json")
                                .bodyValue(request)
                                .retrieve()
                                .bodyToFlux(String.class);
        }

        /**
         * Call AI service for Lean Canvas generation
         */
        public CanvasResponse generateCanvas(@NonNull CanvasRequest request) {
                return webClient.post()
                                .uri("/api/v2/assets/lean-canvas")
                                .header("Content-Type", "application/json")
                                .bodyValue(request)
                                .retrieve()
                                .onStatus(HttpStatusCode::is4xxClientError,
                                                response -> Mono.error(new RuntimeException(
                                                                "Client error calling AI Service (Canvas): "
                                                                                + response.statusCode())))
                                .onStatus(HttpStatusCode::is5xxServerError,
                                                response -> Mono.error(new RuntimeException(
                                                                "Server error calling AI Service (Canvas): "
                                                                                + response.statusCode())))
                                .bodyToMono(CanvasResponse.class)
                                .block();
        }

        /**
         * Call AI service for Pitch Deck generation
         */
        public PitchResponse generatePitch(@NonNull PitchRequest request) {
                return webClient.post()
                                .uri("/api/v2/assets/pitch-deck")
                                .header("Content-Type", "application/json")
                                .bodyValue(request)
                                .retrieve()
                                .onStatus(HttpStatusCode::is4xxClientError,
                                                response -> Mono.error(new RuntimeException(
                                                                "Client error calling AI Service (Pitch): "
                                                                                + response.statusCode())))
                                .onStatus(HttpStatusCode::is5xxServerError,
                                                response -> Mono.error(new RuntimeException(
                                                                "Server error calling AI Service (Pitch): "
                                                                                + response.statusCode())))
                                .bodyToMono(PitchResponse.class)
                                .block();
        }
}
