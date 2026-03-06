import React from 'react';
import { cn } from '../../utils/cn';

export function Input({ className, ...props }) {
    return (
        <input
            className={cn(
                "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm",
                "text-slate-200 placeholder:text-slate-500",
                "focus:outline-none focus:border-indigo-500/50 focus:bg-white/10 transition-all",
                className
            )}
            {...props}
        />
    );
}
