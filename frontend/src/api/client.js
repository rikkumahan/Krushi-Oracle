import axios from 'axios';

// Point to Java Backend — override via VITE_API_BASE_URL in .env.local
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api';

// Generate a unique session ID once per browser tab
function getSessionId() {
    let id = sessionStorage.getItem('nova_session_id');
    if (!id) {
        id = 'user_' + Math.random().toString(36).slice(2, 8).toUpperCase();
        sessionStorage.setItem('nova_session_id', id);
    }
    return id;
}

export const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 120000, // 2 minutes for long-running AI tasks
    headers: {
        'Content-Type': 'application/json',
        'X-Session-ID': getSessionId(),
    }
});

// Response interceptor for clean error handling
client.interceptors.response.use(
    response => response.data,
    error => {
        console.error("API Error:", error.response?.data || error.message);
        return Promise.reject(error.response?.data || { message: "Network Error" });
    }
);

export const api = {
    // Conversational AI
    chat: (messages) => client.post('/ideas/v2/chat', { messages }),
    chatStream: (messages) => fetch(`${API_BASE_URL}/ideas/v2/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages })
    }),

    // Core Idea Generation
    generateIdeas: (input) => client.post('/ideas/generate', { wizard_input: input, num_ideas: 3 }),

    // DETERMINISTIC CORE (Zero Hallucination Risk)
    validate: (payload) => client.post('/ideas/v2/validation/validate', payload),
    score: (payload) => client.post('/ideas/v2/score-idea', payload),
    economics: (payload) => client.post('/ideas/v2/verification/economics', payload),

    // HYBRID (Low Hallucination Risk - Grounded in Deterministic Data)
    audit: (idea, question) => client.post('/ideas/v2/explain-score', { idea_name: idea, user_question: question }),
    feasibility: (payload) => client.post('/ideas/v2/verification/feasibility', payload),
    traffic: (payload) => client.post('/ideas/v2/verification/traffic', payload),
    similar: (payload) => client.post('/ideas/v2/comparison/find-similar', payload),

    // CREATIVE (LLM-Generated - Acceptable for Creative Tasks)
    assets: (payload) => client.post('/ideas/v2/assets/landing-page', payload),
    canvas: (payload) => client.post('/ideas/v2/assets/lean-canvas', payload),
    pitch: (payload) => client.post('/ideas/v2/assets/pitch-deck', payload),
};
