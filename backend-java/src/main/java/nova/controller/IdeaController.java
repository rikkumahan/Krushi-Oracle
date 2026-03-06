package nova.controller;

import nova.model.*;
import nova.service.IdeaService;
import org.springframework.lang.NonNull;
import org.springframework.http.ResponseEntity;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;

import jakarta.validation.Valid;

/**
 * REST Controller for Idea Lab endpoints
 * Routes requests to the AI service via IdeaService
 */
@RestController
@RequestMapping("/api/ideas")
@CrossOrigin(origins = { "http://localhost:5173", "http://localhost:3000" })
public class IdeaController {

    private final IdeaService ideaService;

    public IdeaController(IdeaService ideaService) {
        this.ideaService = ideaService;
    }

    /**
     * Generate startup ideas based on wizard input
     */
    @PostMapping("/generate")
    public ResponseEntity<IdeaGenerationResponse> generateIdeas(
            @NonNull @Valid @RequestBody IdeaGenerationRequest request) {
        IdeaGenerationResponse response = ideaService.generateIdeas(request);
        return ResponseEntity.ok(response);
    }

    /**
     * Validate wizard input before generation
     */
    @PostMapping("/validate")
    public ResponseEntity<LegacyValidationResponse> validateInput(
            @NonNull @Valid @RequestBody LegacyWizardInput input) {
        boolean valid = ideaService.validateInput(input);
        return ResponseEntity.ok(new LegacyValidationResponse(valid, "Input validated successfully"));
    }

    /**
     * Health check endpoint
     */
    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("Idea Lab API is running");
    }

    /**
     * Score an idea using V2 engine (Gateway)
     */
    @PostMapping("/v2/score-idea")
    public ResponseEntity<IdeaScoreResponse> scoreIdea(@NonNull @RequestBody IdeaScoreRequest request) {
        return ResponseEntity.ok(ideaService.scoreIdea(request));
    }

    /**
     * Explain a score using Strategic Audit Agent (Gateway)
     */
    @PostMapping("/v2/explain-score")
    public ResponseEntity<ExplanationResponse> explainScore(@NonNull @RequestBody ExplainRequest request) {
        return ResponseEntity.ok(ideaService.explainScore(request));
    }

    /**
     * Verify unit economics (V2 Innovative)
     */
    @PostMapping("/v2/verification/economics")
    public ResponseEntity<UnitEconomicsResponse> verifyEconomics(@NonNull @RequestBody UnitEconomicsInput request) {
        return ResponseEntity.ok(ideaService.checkUnitEconomics(request));
    }

    /**
     * Verify tech feasibility (V2 Interaction Matrix)
     */
    @PostMapping("/v2/verification/feasibility")
    public ResponseEntity<TechFeasibilityResponse> verifyFeasibility(
            @NonNull @RequestBody TechFeasibilityRequest request) {
        return ResponseEntity.ok(ideaService.checkTechFeasibility(request));
    }

    /**
     * Universal Validation (V2)
     */
    @PostMapping("/v2/validation/validate")
    public ResponseEntity<ValidationResponse> validateStartupIdea(
            @NonNull @RequestBody ValidateIdeaRequest request) {
        return ResponseEntity.ok(ideaService.validateStartupIdea(request));
    }

    /**
     * Smart Comparison Search (V2)
     */
    @PostMapping("/v2/comparison/find-similar")
    public ResponseEntity<ComparisonResponse> findSimilarCompanies(
            @NonNull @RequestBody ComparisonRequest request) {
        return ResponseEntity.ok(ideaService.findSimilarCompanies(request));
    }

    /**
     * Traffic Estimator (V2)
     */
    @PostMapping("/v2/verification/traffic")
    public ResponseEntity<TrafficEstimateResponse> estimateTraffic(
            @NonNull @RequestBody TrafficEstimateRequest request) {
        return ResponseEntity.ok(ideaService.estimateTraffic(request));
    }

    /**
     * Generate Landing Page (Assets)
     */
    @PostMapping("/v2/assets/landing-page")
    public ResponseEntity<LandingPageResponse> generateLandingPage(
            @NonNull @RequestBody LandingPageRequest request) {
        return ResponseEntity.ok(ideaService.generateLandingPage(request));
    }

    /**
     * Service Health (Proxy or Gateway)
     */
    @GetMapping("/v2/health")
    public ResponseEntity<String> healthV2() {
        return ResponseEntity.ok("{\"status\": \"healthy\", \"service\": \"Nova Gateway\"}");
    }

    /**
     * Chat with Nova (V2 Conversational Orchestrator)
     */
    @PostMapping("/v2/chat")
    public ResponseEntity<ChatResponse> chat(@NonNull @RequestBody ChatRequest request) {
        return ResponseEntity.ok(ideaService.chat(request));
    }

    /**
     * Stream chat response (SSE) - V2
     */
    @PostMapping(value = "/v2/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> chatStream(@NonNull @RequestBody ChatRequest request) {
        return ideaService.chatStream(request);
    }

    /**
     * Generate Lean Canvas (Assets)
     */
    @PostMapping("/v2/assets/lean-canvas")
    public ResponseEntity<CanvasResponse> generateCanvas(@NonNull @RequestBody CanvasRequest request) {
        return ResponseEntity.ok(ideaService.generateCanvas(request));
    }

    /**
     * Generate Pitch Deck (Assets)
     */
    @PostMapping("/v2/assets/pitch-deck")
    public ResponseEntity<PitchResponse> generatePitch(@NonNull @RequestBody PitchRequest request) {
        return ResponseEntity.ok(ideaService.generatePitch(request));
    }

    // Inner classes for simple responses

    record LegacyValidationResponse(boolean valid, String message) {
    }

    record LegacyWizardInput(
            String industry,
            String targetAudience,
            String skillLevel,
            int budget,
            String timeFrame) {
    }
}
