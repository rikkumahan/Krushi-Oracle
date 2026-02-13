const API_BASE_URL = 'http://localhost:8000/api/v2';

/**
 * Validates a startup idea using the Universal Validation endpoint.
 */
export const validateIdea = async (description, sector = "software") => {
    const payload = {
        // We derive name and description from the single input for simplicity
        idea_name: description.split('\n')[0].substring(0, 100) || "New Idea",
        idea_description: description,
        sector: sector, // Sector selection
        keywords: [],
        team_size: 1,
        timeline_months: 6,
        budget_usd: 0
    };

    try {
        const response = await fetch(`${API_BASE_URL}/validation/validate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Validation failed');
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
};

/**
 * Scores an idea using the V2 Deterministic Engine.
 */
export const scoreIdea = async (payload) => {
    try {
        const response = await fetch(`${API_BASE_URL}/score-idea`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Scoring failed');
        }

        return await response.json();
    } catch (error) {
        console.error('Scoring API Error:', error);
        throw error;
    }
};

/**
 * Gets a strategic explanation from the Strategic Audit Agent.
 */
export const explainScore = async (ideaName, question) => {
    try {
        const response = await fetch(`${API_BASE_URL}/explain-score`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                idea_name: ideaName,
                question: question
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Explanation failed');
        }

        return await response.json();
    } catch (error) {
        console.error('Audit Agent Error:', error);
        throw error;
    }
};

/**
 * Gets the health status of the AI service.
 */
export const checkServiceHealth = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        return await response.json();
    } catch {
        return { status: 'offline' };
    }
};
