import React from 'react';
import { Sparkles, Trophy, Building2, BarChart, FileJson, ShieldAlert } from 'lucide-react';
import { Button } from '../ui/Button';

export function ActionPanel({ onAction, isLoading }) {
    const actions = [
        { id: 'audit', label: 'Strategic Audit', icon: Sparkles, color: 'text-yellow-400' },
        { id: 'score', label: 'V2 Score', icon: Trophy, color: 'text-purple-400' },
        { id: 'competitors', label: 'Competitors', icon: Building2, color: 'text-blue-400' },
        { id: 'traffic', label: 'Traffic Est.', icon: BarChart, color: 'text-green-400' },
        { id: 'assets', label: 'Landing Page', icon: FileJson, color: 'text-pink-400' },
        { id: 'feasibility', label: 'Tech Check', icon: ShieldAlert, color: 'text-red-400' },
    ];

    return (
        <div className="max-w-3xl mx-auto mt-4 p-4 rounded-2xl border border-indigo-500/20 bg-indigo-500/5 backdrop-blur-sm animate-fade-in">
            <div className="flex items-center gap-2 mb-3">
                <Sparkles className="w-4 h-4 text-indigo-400" />
                <span className="text-xs font-semibold uppercase tracking-wider text-indigo-300">
                    Smart Actions Available
                </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {actions.map((action) => (
                    <Button
                        key={action.id}
                        onClick={() => onAction(action.id)}
                        variant="ghost"
                        size="sm"
                        disabled={isLoading}
                        className="justify-start bg-white/5 border border-white/5 hover:bg-white/10 hover:border-indigo-500/30 group"
                    >
                        <action.icon className={`w-4 h-4 mr-2 ${action.color} group-hover:scale-110 transition-transform`} />
                        <span className="text-slate-300 group-hover:text-white transition-colors">
                            {action.label}
                        </span>
                    </Button>
                ))}
            </div>
        </div>
    );
}
