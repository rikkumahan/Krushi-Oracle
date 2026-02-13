import React, { useState, useEffect, useRef } from 'react';
import { Send, User, Bot, Loader2, Sparkles, Copy, RefreshCw, Paperclip, Mic } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { validateIdea } from '../services/api';
import { NeuralInput } from './ui/NeuralInput';
import { Button } from './ui/Button';

export function ChatInterface() {
    const { theme } = useTheme();
    const [messages, setMessages] = useState([]); // Start empty to show suggestions
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);
    const isMounted = useRef(true);

    const SUGGESTIONS = [
        { id: 'crypto', label: 'Analyze Crypto App', prompt: "I have an idea for a crypto wallet that tracks whale movements." },
        { id: 'saas', label: 'Validate SaaS Idea', prompt: "Validate a B2B SaaS for automated employee onboarding." },
        { id: 'mkt', label: 'Market Scan', prompt: "Scan the current market for AI copywriting tools." },
        { id: 'audit', label: 'Strategic Audit', prompt: "Audit my startup's moat and competitive advantage." },
    ];

    useEffect(() => {
        isMounted.current = true;
        return () => { isMounted.current = false };
    }, []);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, loading]);

    const handleSend = async (text = input) => {
        if (!text.trim() || loading) return;

        const userMsg = {
            id: Date.now().toString(),
            role: 'user',
            content: text,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const response = await validateIdea(userMsg.content, 'software');

            if (isMounted.current) {
                const aiMsg = {
                    id: (Date.now() + 1).toString(),
                    role: 'ai',
                    content: `I've analyzed your idea "${response.idea_name}". \n\n**Verdict:** ${response.verdict} (${response.overall_confidence}/100)\n\n**Market:** ${response.market_validation.overall_score}/100\n**Social Proof:** ${response.social_proof.overall_score}/100\n**Execution Risk:** ${response.execution_risk.risk_level}`,
                    data: response,
                    timestamp: new Date()
                };
                setMessages(prev => [...prev, aiMsg]);
            }
        } catch (e) {
            console.error(e);
            if (isMounted.current) {
                const errorMsg = {
                    id: (Date.now() + 1).toString(),
                    role: 'ai',
                    content: "I encountered an error analyzing your request. Please try again.",
                    isError: true,
                    timestamp: new Date()
                };
                setMessages(prev => [...prev, errorMsg]);
            }
        } finally {
            if (isMounted.current) {
                setLoading(false);
            }
        }
    };

    return (
        <div className={`flex flex-col h-full w-full max-w-5xl mx-auto ${theme === 'dark' ? 'text-slate-300' : 'text-slate-800'}`}>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto px-4 py-6 space-y-8 scrollbar-thin">
                {messages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center animate-fade-in">
                        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center mb-6 shadow-xl shadow-indigo-500/20">
                            <Sparkles className="w-8 h-8 text-white" />
                        </div>
                        <h2 className="text-2xl font-bold mb-2 tracking-tight">How can I help you today?</h2>
                        <p className="text-slate-400 mb-8 max-w-md text-center">I can validate startup ideas, analyze markets, and provide strategic audits.</p>

                        <div className="grid grid-cols-2 gap-4 w-full max-w-2xl">
                            {SUGGESTIONS.map(s => (
                                <button
                                    key={s.id}
                                    onClick={() => handleSend(s.prompt)}
                                    className={`p-4 text-left rounded-xl border transition-all duration-200 group ${theme === 'dark'
                                        ? 'bg-white/5 border-white/5 hover:bg-white/10 hover:border-white/10'
                                        : 'bg-white border-slate-100 hover:border-indigo-200 hover:shadow-md'
                                        }`}
                                >
                                    <span className="block font-medium mb-1 group-hover:text-indigo-500 transition-colors">{s.label}</span>
                                    <span className="text-xs text-slate-400 truncate block">{s.prompt}</span>
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    <>
                        {messages.map((msg) => (
                            <MessageBubble key={msg.id} msg={msg} theme={theme} />
                        ))}
                        {loading && <LoadingBubble theme={theme} />}
                        <div ref={messagesEndRef} />
                    </>
                )}
            </div>

            {/* Input Area */}
            <div className="p-4 relative z-20">
                <div className="max-w-3xl mx-auto relative">
                    <NeuralInput
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                        placeholder="Ask anything..."
                        disabled={loading}
                        className={`w-full pl-4 pr-32 py-4 rounded-3xl shadow-2xl border transition-all resize-none overflow-hidden min-h-[60px] max-h-48 ${theme === 'dark'
                            ? 'bg-[#1a1a1a] border-white/10 text-white placeholder:text-slate-500 focus:border-white/20'
                            : 'bg-white/90 border-white/50 text-slate-800 placeholder:text-slate-400 shadow-indigo-500/5 backdrop-blur-xl focus:border-indigo-200'
                            }`}
                    />

                    <div className="absolute right-3 bottom-3 flex items-center gap-2">
                        <Button variant="ghost" size="sm" className="rounded-full w-8 h-8 p-0 text-slate-400 hover:text-slate-600 hover:bg-slate-100">
                            <Paperclip className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="sm" className="rounded-full w-8 h-8 p-0 text-slate-400 hover:text-slate-600 hover:bg-slate-100">
                            <Mic className="w-4 h-4" />
                        </Button>
                        <Button
                            onClick={() => handleSend()}
                            disabled={!input.trim() || loading}
                            className={`rounded-full w-9 h-9 p-0 flex items-center justify-center transition-all duration-300 ${input.trim()
                                ? 'bg-black text-white hover:bg-slate-800 shadow-lg'
                                : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                                }`}
                        >
                            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                        </Button>
                    </div>
                </div>
                <div className="text-center mt-3 text-xs text-slate-400 font-medium">
                    Nova AI v2.0 • Pro Strategic Advisor
                </div>
            </div>
        </div>
    );
}

function MessageBubble({ msg, theme }) {
    const isUser = msg.role === 'user';
    const isAi = msg.role === 'ai';

    return (
        <div className={`flex gap-4 max-w-3xl mx-auto group ${isUser ? 'flex-row-reverse' : 'flex-row'} animate-fade-in`}>
            {/* Avatar */}
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-1 ${isAi
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/20'
                : 'bg-slate-200 text-slate-500'
                }`}>
                {isAi ? <Bot className="w-5 h-5" /> : <User className="w-5 h-5" />}
            </div>

            {/* Bubble */}
            <div className={`flex-1 overflow-hidden ${isUser
                ? 'bg-slate-100 text-slate-800 rounded-2xl rounded-tr-sm px-5 py-3.5'
                : ''
                }`}>
                {isAi && (
                    <div className="text-sm font-semibold mb-1 text-slate-900 flex items-center gap-2">
                        Nova
                        <span className="text-[10px] bg-indigo-100 text-indigo-700 px-1.5 py-0.5 rounded font-mono">PRO</span>
                    </div>
                )}

                <div className={`prose prose-sm max-w-none ${theme === 'dark' ? 'dark:prose-invert' : 'text-slate-700 leading-relaxed'}`}>
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>

                {isAi && (
                    <div className="flex gap-2 mt-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                        <button className="p-1.5 rounded hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors" title="Copy">
                            <Copy className="w-3.5 h-3.5" />
                        </button>
                        <button className="p-1.5 rounded hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors" title="Regenerate">
                            <RefreshCw className="w-3.5 h-3.5" />
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

function LoadingBubble() {
    return (
        <div className="flex gap-4 max-w-3xl mx-auto animate-pulse">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center flex-shrink-0 mt-1">
                <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="flex items-center gap-1 mt-2">
                <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></span>
            </div>
        </div>
    );
}

// Re-export InputArea if needed, though fully integrated above
function InputArea() { return null; }
