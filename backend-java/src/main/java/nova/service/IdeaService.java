package nova.service;

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
}
