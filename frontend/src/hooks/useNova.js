import { useState, useCallback, useRef } from 'react';
import { api } from '../api/client';

export function useNova() {
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const [actionData, setActionData] = useState(null); // Data ready for actions (audit, score, etc.)
    const abortController = useRef(null);

    const sendMessage = useCallback(async (content) => {
        if (!content.trim()) return;

        const userMsg = {
            role: 'user',
            content,
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMsg]);
        setLoading(true);
        setActionData(null);

        // Create empty assistant message placeholder
        const aiMsgId = Date.now();
        setMessages(prev => [...prev, {
            role: 'assistant',
            content: '',
            timestamp: new Date().toISOString(),
            id: aiMsgId,
            isStreaming: true
        }]);

        try {
            const history = messages.map(m => ({
                role: m.role,
                content: m.content
            }));
            history.push({ role: 'user', content });

            const response = await api.chatStream(history);
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            let assistantContent = '';
            let buffer = '';

            console.log("Starting stream reader...");

            while (true) {
                const { value, done } = await reader.read();
                if (done) {
                    console.log("Stream complete");
                    break;
                }

                // Decode chunk
                const chunk = decoder.decode(value, { stream: true });
                buffer += chunk;

                // Split by double newline (standard SSE delimiter) or single newline
                // Using single newline because our Python service sends "data: {...}\n\n" but sometimes they get split
                const lines = buffer.split('\n');

                // Keep the last part in the buffer if it doesn't end with a newline
                // This means it's an incomplete line
                buffer = lines.pop();

                for (const line of lines) {
                    const trimmedLine = line.trim();
                    if (!trimmedLine) continue;

                    if (trimmedLine.startsWith('data:')) {
                        try {
                            const jsonStr = trimmedLine.replace(/^data:\s*/, '');
                            // console.log("Received chunk:", jsonStr.substring(0, 50) + "...");
                            const data = JSON.parse(jsonStr);

                            if (data.type === 'token') {
                                assistantContent += data.content;
                                setMessages(prev => prev.map(m =>
                                    m.id === aiMsgId ? { ...m, content: assistantContent } : m
                                ));
                            } else if (data.type === 'status') {
                                // console.log("Status update:", data.content);
                                setMessages(prev => prev.map(m =>
                                    m.id === aiMsgId ? { ...m, status: data.content } : m
                                ));
                            } else if (data.type === 'tool_result') {
                                // console.log("Tool result:", data.tool);
                                const toolResult = data;
                                let formattedContent = '';

                                if (toolResult.tool === 'score_idea') {
                                    const r = toolResult.content;
                                    formattedContent = `## 🏆 Deterministic Score: ${r.mvs_score}/100\n\n**Grade**: ${r.mvs_grade}\n**Class**: ${r.validation_class}\n\n**Dimensions**:\n- Market: ${r.dimension_scores.market}/100\n- Differentiation: ${r.dimension_scores.differentiation}/100\n- Execution: ${r.dimension_scores.execution}/100\n- Capital: ${r.dimension_scores.capital}/100\n\n**Recommendations**:\n${r.recommendations.map(rec => `- ${rec}`).join('\n')}`;
                                } else if (toolResult.tool === 'explain_score') {
                                    const r = toolResult.content;
                                    formattedContent = `## ✨ Strategic Audit\n\n${r.answer}\n\n**Confidence**: ${r.confidence}\n**Tools Used**: ${r.tools_used.join(', ')}`;
                                } else if (toolResult.tool === 'estimate_traffic') {
                                    const r = toolResult.content;
                                    formattedContent = `## 🚦 Traffic Estimate\n\n**Monthly Clicks**: ${r.estimated_clicks?.toLocaleString() || 'N/A'}\n**CPC**: $${r.estimated_cpc || 'N/A'}\n**Trend**: ${r.search_volume_trend || 'Stable'}\n\n**Top Channels**: ${r.recommended_channels?.join(', ') || 'N/A'}\n**Searches Analyzed**: ${r.keywords_analyzed?.join(', ') || 'N/A'}`;
                                }

                                if (formattedContent) {
                                    setMessages(prev => [...prev, {
                                        role: 'assistant',
                                        content: formattedContent,
                                        timestamp: new Date().toISOString(),
                                        isToolOutput: true
                                    }]);
                                }
                            }
                        } catch (e) {
                            console.error("Error parsing SSE data line:", trimmedLine, e);
                        }
                    }
                }
            }

            // Finalize message
            setMessages(prev => prev.map(m =>
                m.id === aiMsgId ? { ...m, isStreaming: false, status: null } : m
            ));

        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "I'm having trouble connecting to my neural network.",
                isError: true,
                timestamp: new Date().toISOString()
            }]);
        } finally {
            setLoading(false);
        }
    }, [messages]);

    const clearHistory = useCallback(() => {
        setMessages([]);
        setActionData(null);
    }, []);

    const runAction = useCallback(async (actionType, explicitData = null) => {
        const data = explicitData || actionData;
        if (!data) return;

        setLoading(true);
        try {
            let response;
            let messageContent = '';

            switch (actionType) {
                case 'score':
                    // Call Deterministic Scoring Engine
                    response = await api.score({
                        ...actionData,
                        // Add default V2 required fields if missing from orchestrator
                        monthly_searches: 1000,
                        growth_rate_30d: 0.1,
                        competitor_count: 5,
                        tech_stack: { technologies: [], team_experience: {} }
                    });
                    messageContent = `## 🏆 V2 Score: ${response.mvs_score}/100\n\n**Grade**: ${response.mvs_grade}\n**Class**: ${response.validation_class}\n\n${response.recommendations.map(r => `- ${r}`).join('\n')}`;
                    break;

                case 'audit':
                    // Call Strategic Audit Agent
                    // First ensure we have a score (Audit requires it)
                    // We assume score exists or run it implicitly. For now, we request explain-score directly
                    // Note: In production, we'd ensure score_idea is called first, but our mock/orchestrator handles this via Redis
                    response = await api.audit(actionData.idea_name, "Perform a deep strategic audit of this idea.");
                    messageContent = `## ✨ Strategic Audit\n\n${response.answer}\n\n**Confidence**: ${response.confidence}\n**Tools Used**: ${response.tools_used.join(', ')}`;
                    break;

                case 'traffic':
                    response = await api.traffic({
                        idea_name: actionData.idea_name,
                        idea_description: actionData.idea_description
                    });
                    messageContent = `## 🚦 Traffic Estimate\n\n**Monthly Visits**: ${response.estimated_monthly_visits.toLocaleString()}\n**CPP**: $${response.cost_per_click}\n\n${response.explanation}`;
                    break;

                default:
                    messageContent = `Executed action: ${actionType}`;
            }

            const systemMsg = {
                role: 'assistant',
                content: messageContent,
                timestamp: new Date().toISOString(),
                isActionOutput: true
            };

            setMessages(prev => [...prev, systemMsg]);

        } catch (error) {
            console.error("Action error:", error);
            const errorMsg = {
                role: 'assistant',
                content: `❌ Error executing ${actionType}: ${error.message || "Unknown error"}`,
                isError: true,
                timestamp: new Date().toISOString()
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setLoading(false);
        }
    }, [actionData]);

    const injectMessage = useCallback((msg) => {
        setMessages(prev => [...prev, msg]);
    }, []);

    return {
        messages,
        loading,
        actionData,
        sendMessage,
        clearHistory,
        runAction,
        injectMessage // NEW
    };
}
