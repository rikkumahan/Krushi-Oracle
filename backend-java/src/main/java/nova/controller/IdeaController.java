package nova.controller;

import nova.model.*;
import nova.service.IdeaService;
import org.springframework.lang.NonNull;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

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
    public ResponseEntity<ValidationResponse> validateInput(
            @NonNull @Valid @RequestBody WizardInput input) {
        boolean valid = ideaService.validateInput(input);
        return ResponseEntity.ok(new ValidationResponse(valid, "Input validated successfully"));
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

    // Inner classes for simple responses
    record ValidationResponse(boolean valid, String message) {
    }

    record WizardInput(
            String industry,
            String targetAudience,
            String skillLevel,
            int budget,
            String timeFrame) {
    }
}
