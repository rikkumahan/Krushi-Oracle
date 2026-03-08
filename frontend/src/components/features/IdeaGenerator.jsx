import React, { useState } from 'react';
import { api } from '../../api/client';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Zap, Target, DollarSign, Clock, ArrowRight, Loader2, Lightbulb, MessageSquare } from 'lucide-react';

export function IdeaGenerator({ onComplete }) {
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [formData, setFormData] = useState({
        industry: '',
        target_audience: '',
        skill_level: 'intermediate',
        budget: 1000,
        time_frame: '3_months',
        interests: '',
        location: ''
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: name === 'budget' ? Number(value) : value
        }));
    };

    const handleGenerate = async () => {
        setLoading(true);
        try {
            const response = await api.generateIdeas(formData);
            setResults(response.ideas);
            setStep(3);
        } catch (error) {
            console.error("Generation failed:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        // Reduced padding on mobile; overflow scroll from parent handles the page
        <div className="flex flex-col items-center justify-center p-4 md:p-8">
            {step === 1 && (
                <div className="w-full max-w-2xl animate-fade-in">
                    <div className="text-center mb-6 md:mb-10">
                        <div className="w-12 h-12 md:w-16 md:h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl mx-auto flex items-center justify-center mb-4 shadow-xl shadow-indigo-500/20">
                            <Zap className="w-6 h-6 md:w-8 md:h-8 text-white" />
                        </div>
                        {/* Scaled heading: smaller on mobile */}
                        <h1 className="text-2xl md:text-4xl font-bold text-white mb-3">Startup Idea Generator</h1>
                        <p className="text-slate-400 text-sm md:text-lg">Define your constraints. We'll find the opportunities.</p>
                    </div>

                    {/* Reduced inner padding on mobile */}
                    <div className="space-y-5 bg-white/5 p-4 md:p-8 rounded-3xl border border-white/10 backdrop-blur-xl">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-300">Industry / Sector</label>
                                <div className="relative">
                                    <Target className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                                    <Input
                                        name="industry"
                                        value={formData.industry}
                                        onChange={handleChange}
                                        placeholder="e.g. SaaS, FinTech, Gardening"
                                        className="pl-10"
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-300">Target Audience</label>
                                <Input
                                    name="target_audience"
                                    value={formData.target_audience}
                                    onChange={handleChange}
                                    placeholder="e.g. Small Business Owners"
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-300">Budget (USD)</label>
                                <div className="relative">
                                    <DollarSign className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                                    <Input
                                        type="number"
                                        name="budget"
                                        value={formData.budget}
                                        onChange={handleChange}
                                        className="pl-10"
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-300">Time Frame</label>
                                <div className="relative">
                                    <Clock className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                                    <select
                                        name="time_frame"
                                        value={formData.time_frame}
                                        onChange={handleChange}
                                        className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-2.5 pl-10 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent appearance-none"
                                    >
                                        <option value="1_month">1 Month</option>
                                        <option value="3_months">3 Months</option>
                                        <option value="6_months">6 Months</option>
                                        <option value="1_year">1 Year</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <Button
                            className="w-full py-3 md:py-4 text-base md:text-lg font-semibold bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 shadow-lg shadow-indigo-500/25"
                            onClick={handleGenerate}
                            disabled={loading || !formData.industry}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                                    Analyzing Market Gaps...
                                </>
                            ) : (
                                <>
                                    Generate Ideas
                                    <ArrowRight className="w-5 h-5 ml-2" />
                                </>
                            )}
                        </Button>
                    </div>
                </div>
            )}

            {step === 3 && results && (
                <div className="w-full max-w-5xl animate-fade-in pb-8">
                    {/* Results header — stacks vertically on mobile, side-by-side on sm+ */}
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-6 md:mb-8">
                        <div>
                            <h2 className="text-2xl md:text-3xl font-bold text-white">Generated Opportunities</h2>
                            <p className="text-slate-400 text-sm md:text-base">Based on {formData.industry} analysis</p>
                        </div>
                        {/* Buttons wrap neatly on mobile */}
                        <div className="flex flex-wrap gap-2">
                            <Button variant="ghost" onClick={() => setStep(1)}>Generate More</Button>
                            <Button
                                className="bg-white text-black hover:bg-slate-200"
                                onClick={() => onComplete && onComplete(results)}
                            >
                                <MessageSquare className="w-4 h-4 mr-2" />
                                Analyze in Chat
                            </Button>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
                        {results.map((idea, idx) => (
                            <div key={idx} className="bg-white/5 border border-white/10 rounded-2xl p-5 md:p-6 hover:bg-white/10 transition-all hover:scale-[1.02] cursor-pointer group">
                                <div className="flex items-start justify-between mb-4">
                                    <div className="w-10 h-10 md:w-12 md:h-12 rounded-xl bg-indigo-500/20 flex items-center justify-center text-indigo-400 group-hover:bg-indigo-500 group-hover:text-white transition-colors">
                                        <Lightbulb className="w-5 h-5 md:w-6 md:h-6" />
                                    </div>
                                    <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400 border border-green-500/20">
                                        High Validity
                                    </span>
                                </div>

                                <h3 className="text-lg md:text-xl font-bold text-white mb-2">{idea.name}</h3>
                                <p className="text-slate-400 text-sm mb-4 line-clamp-3">{idea.description}</p>

                                <div className="space-y-3 pt-4 border-t border-white/5">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-slate-500">Target</span>
                                        <span className="text-slate-300">{idea.target_customer}</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-slate-500">Model</span>
                                        <span className="text-slate-300">{idea.business_model?.revenue_streams?.[0] || 'SaaS'}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
