import React, { useRef, useEffect, useState } from 'react';
import { ThemeProvider } from './context/ThemeContext';
import { useNova } from './hooks/useNova';
import { Button } from './components/ui/Button';
import { Input } from './components/ui/Input';
import { ChatBubble } from './components/chat/ChatBubble';
import { ActionPanel } from './components/chat/ActionPanel';
import { IdeaGenerator } from './components/features/IdeaGenerator'; // Keep for now, will embed
import { Send, Zap, MessageSquare, Lightbulb } from 'lucide-react';

function AppContent() {
    const {
        messages,
        loading,
        actionData,
        sendMessage,
        runAction,
        injectMessage // New
    } = useNova();

    // Mode state for overlay
    const [generatorMode, setGeneratorMode] = useState(false);
    const messagesEndRef = useRef(null);
    const [input, setInput] = React.useState('');

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, loading]);

    const handleSend = () => {
        if (!input.trim()) return;
        sendMessage(input);
        setInput('');
    };

    // Handle V2 Actions
    const handleActionClick = async (actionId) => {
        if (actionId === 'assets') {
            sendMessage("Generate a landing page for this idea.");
            return;
        }
        await runAction(actionId);
    };

    // Handle Generator Completion
    const handleGeneratorComplete = (ideas) => {
        setGeneratorMode(false);
        // Inject results into chat
        injectMessage({
            role: 'assistant',
            content: `## 🚀 I found ${ideas.length} validated opportunities for you!\n\n${ideas.map(i => `**${i.name}**: ${i.tagline}`).join('\n')}\n\n*Which one would you like to build?*`,
            timestamp: new Date().toISOString()
        });
    };

    return (
        <div className="flex h-screen w-screen bg-[#050505] text-slate-200 font-sans overflow-hidden relative">
            {/* Background Effects */}
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/20 via-black to-purple-900/20 pointer-events-none" />
            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none" />

            {/* Sidebar (Glass) */}
            <aside className="w-20 lg:w-64 border-r border-white/5 bg-black/40 backdrop-blur-xl flex flex-col items-center lg:items-stretch py-6 z-10">
                <div className="px-6 mb-8 flex items-center justify-center lg:justify-start gap-3">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg shadow-indigo-500/20 flex items-center justify-center">
                        <Zap className="w-5 h-5 text-white" />
                    </div>
                    <span className="hidden lg:block font-bold text-lg tracking-tight text-white/90">
                        Nova <span className="text-indigo-400">Pro</span>
                    </span>
                </div>

                {/* Nav Items */}
                <nav className="flex-1 space-y-2 px-3">
                    <Button
                        variant="ghost"
                        className="w-full justify-start bg-white/10 text-white"
                        onClick={() => window.location.reload()}
                    >
                        <MessageSquare className="w-4 h-4 lg:mr-2" />
                        <span className="hidden lg:inline">New Chat</span>
                    </Button>
                </nav>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 flex flex-col relative z-0">

                {generatorMode ? (
                    <div className="flex-1 overflow-y-auto">
                        <div className="p-4">
                            <Button variant="ghost" onClick={() => setGeneratorMode(false)} className="mb-4">
                                ← Back to Chat
                            </Button>
                        </div>
                        <IdeaGenerator onComplete={handleGeneratorComplete} />
                    </div>
                ) : (
                    <>
                        <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
                            {messages.length === 0 && (
                                <div className="h-full flex flex-col items-center justify-center p-8 animate-fade-in relative z-10">
                                    <div className="text-center mb-12">
                                        <h1 className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400 mb-6 drop-shadow-2xl">
                                            Nova <span className="text-white">Orchestrator</span>
                                        </h1>
                                        <p className="text-slate-400 text-lg max-w-xl mx-auto leading-relaxed">
                                            I am your deterministic co-founder. Specify your path to begin.
                                        </p>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-4xl">
                                        {/* Option 1: Generate Ideas */}
                                        <button
                                            onClick={() => setGeneratorMode(true)}
                                            className="group relative p-8 rounded-3xl bg-gradient-to-br from-indigo-900/40 to-black border border-white/10 hover:border-indigo-500/50 hover:shadow-2xl hover:shadow-indigo-500/20 transition-all duration-300 text-left"
                                        >
                                            <div className="absolute inset-0 bg-indigo-500/5 opacity-0 group-hover:opacity-100 transition-opacity rounded-3xl" />
                                            <div className="w-14 h-14 bg-indigo-500/20 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                                <Lightbulb className="w-7 h-7 text-indigo-400" />
                                            </div>
                                            <h3 className="text-2xl font-bold text-white mb-2">Generate Ideas</h3>
                                            <p className="text-slate-400">
                                                I don't have an idea yet. Analyze market gaps and generate validated opportunities for me.
                                            </p>
                                        </button>

                                        {/* Option 2: Validate Idea */}
                                        <button
                                            onClick={() => document.querySelector('input')?.focus()}
                                            className="group relative p-8 rounded-3xl bg-gradient-to-br from-purple-900/40 to-black border border-white/10 hover:border-purple-500/50 hover:shadow-2xl hover:shadow-purple-500/20 transition-all duration-300 text-left"
                                        >
                                            <div className="absolute inset-0 bg-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity rounded-3xl" />
                                            <div className="w-14 h-14 bg-purple-500/20 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                                <Zap className="w-7 h-7 text-purple-400" />
                                            </div>
                                            <h3 className="text-2xl font-bold text-white mb-2">Validate Idea</h3>
                                            <p className="text-slate-400">
                                                I have an idea. Run a strategic audit, check unit economics, and scoring.
                                            </p>
                                        </button>
                                    </div>
                                </div>
                            )}

                            {messages.map((msg, idx) => (
                                <ChatBubble key={idx} message={msg} />
                            ))}

                            {loading && (
                                <div className="flex justify-center py-4">
                                    <div className="flex gap-1">
                                        <span className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                                        <span className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                                        <span className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce"></span>
                                    </div>
                                </div>
                            )}

                            {/* Action Panel (Conditional) */}
                            {actionData && !loading && (
                                <ActionPanel onAction={handleActionClick} isLoading={loading} />
                            )}

                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input Area */}
                        <div className="p-4 border-t border-white/5 bg-black/60 backdrop-blur-md">
                            <div className="max-w-3xl mx-auto relative flex gap-2">
                                <Input
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                    placeholder="Describe your idea..."
                                    className="pr-12"
                                    autoFocus
                                />
                                <Button
                                    onClick={handleSend}
                                    disabled={!input.trim() || loading}
                                    className="absolute right-2 top-1.5 bottom-1.5 px-3 rounded-lg"
                                >
                                    <Send className="w-4 h-4" />
                                </Button>
                            </div>
                        </div>
                    </>
                )}
            </main>
        </div>
    );
}

export default function App() {
    return (
        <ThemeProvider>
            <AppContent />
        </ThemeProvider>
    );
}
