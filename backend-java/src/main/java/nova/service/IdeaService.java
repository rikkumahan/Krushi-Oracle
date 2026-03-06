package nova.service;

import reactor.core.publisher.Flux;
import nova.client.AIServiceClient;
import nova.model.*;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Service;

/**
 * Service layer for Idea Lab operations
 * Orchestrates business logic and calls to AI service
 */
@Service
public class IdeaService {

    private final AIServiceClient aiServiceClient;

    public IdeaService(AIServiceClient aiServiceClient) {
        this.aiServiceClient = aiServiceClient;
    }

    /**
     * Generate ideas by calling the Python AI service
     */
    public IdeaGenerationResponse generateIdeas(@NonNull IdeaGenerationRequest request) {
        return aiServiceClient.generateIdeas(request);
    }

    /**
     * Score an idea using the V2 Deterministic Engine
     */
    public IdeaScoreResponse scoreIdea(@NonNull IdeaScoreRequest request) {
        return aiServiceClient.scoreIdea(request);
    }

    /**
     * Get explanation for a score from Strategic Audit Agent
     */
    public ExplanationResponse explainScore(@NonNull ExplainRequest request) {
        return aiServiceClient.explainScore(request);
    }

    /**
     * Validate wizard input
     */
    public boolean validateInput(Object input) {
        // Basic validation - can be extended
        return input != null;
    }

    /**
     * Check unit economics (V2 Innovative)
     */
    public UnitEconomicsResponse checkUnitEconomics(@NonNull UnitEconomicsInput inputs) {
        return aiServiceClient.checkUnitEconomics(inputs);
    }

    /**
     * Check tech feasibility (V2 Interaction Matrix)
     */
    public TechFeasibilityResponse checkTechFeasibility(@NonNull TechFeasibilityRequest request) {
        return aiServiceClient.checkTechFeasibility(request);
    }

    /**
     * Validate a startup idea (Universal Validation)
     */
    public ValidationResponse validateStartupIdea(@NonNull ValidateIdeaRequest request) {
        return aiServiceClient.validateStartupIdea(request);
    }

    /**
     * Find similar companies (Smart Comparison)
     */
    public ComparisonResponse findSimilarCompanies(@NonNull ComparisonRequest request) {
        return aiServiceClient.findSimilarCompanies(request);
    }

    /**
     * Estimate traffic (Traffic Estimator)
     */
    public TrafficEstimateResponse estimateTraffic(@NonNull TrafficEstimateRequest request) {
        return aiServiceClient.estimateTraffic(request);
    }

    /**
     * Generate landing page (Assets)
     */
    public LandingPageResponse generateLandingPage(@NonNull LandingPageRequest request) {
        return aiServiceClient.generateLandingPage(request);
    }

    /**
     * Chat with Nova (V2 Conversational Orchestrator)
     */
    public ChatResponse chat(@NonNull ChatRequest request) {
        return aiServiceClient.chat(request);
    }

    public Flux<String> chatStream(@NonNull ChatRequest request) {
        return aiServiceClient.chatStream(request);
    }

    /**
     * Generate Lean Canvas (Assets)
     */
    public CanvasResponse generateCanvas(@NonNull CanvasRequest request) {
        return aiServiceClient.generateCanvas(request);
    }

    /**
     * Generate Pitch Deck (Assets)
     */
    public PitchResponse generatePitch(@NonNull PitchRequest request) {
        return aiServiceClient.generatePitch(request);
    }
}
