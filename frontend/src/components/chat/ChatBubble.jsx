import React from 'react';
import { Bot, User } from 'lucide-react';
import { cn } from '../../utils/cn';
import ReactMarkdown from 'react-markdown';

export function ChatBubble({ message }) {
    const isAi = message.role === 'assistant';

    return (
        <div className={cn(
            "flex gap-2 md:gap-4 max-w-3xl mx-auto animate-fade-in group",
            !isAi && "flex-row-reverse"
        )}>
            {/* Avatar — slightly smaller on mobile to give text more room */}
            <div className={cn(
                "w-7 h-7 md:w-8 md:h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-1 shadow-lg",
                isAi ? "bg-indigo-600 text-white shadow-indigo-500/20" : "bg-slate-700 text-slate-300"
            )}>
                {isAi ? <Bot className="w-4 h-4 md:w-5 md:h-5" /> : <User className="w-4 h-4 md:w-5 md:h-5" />}
            </div>

            {/* Content */}
            <div className={cn(
                "overflow-hidden min-w-0",
                isAi
                    ? "flex-1 text-slate-200 pt-1"
                    // max-w-[90%] on mobile gives more breathing room vs tight 80%
                    : "bg-indigo-600/80 text-white px-3 py-3 md:p-4 rounded-3xl max-w-[90%] md:max-w-[75%] shadow-sm"
            )}>
                {isAi && (
                    <div className="flex items-center gap-2 mb-2 text-xs font-medium text-indigo-400">
                        <span>NOVA</span>
                        <div className="px-1.5 py-0.5 bg-indigo-500/20 rounded text-[10px] border border-indigo-500/30">
                            PRO
                        </div>
                    </div>
                )}

                <div className="prose prose-invert prose-sm max-w-none">
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>

                {message.status && (
                    <div className="mt-2 text-xs text-indigo-500 italic flex items-center gap-1">
                        <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></span>
                        {message.status}
                    </div>
                )}
            </div>
        </div>
    );
}
