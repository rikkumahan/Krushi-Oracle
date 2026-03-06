import React from 'react';
import { cn } from '../../utils/cn';

export function Button({
    className,
    variant = 'primary',
    size = 'md',
    isLoading,
    children,
    ...props
}) {
    const variants = {
        primary: "bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg hover:shadow-indigo-500/30",
        secondary: "bg-slate-800 text-slate-200 hover:bg-slate-700",
        ghost: "bg-transparent hover:bg-white/5 text-slate-400 hover:text-white",
        outline: "border border-white/10 hover:bg-white/5 text-slate-300"
    };

    const sizes = {
        sm: "px-3 py-1.5 text-xs",
        md: "px-4 py-2 text-sm",
        lg: "px-6 py-3 text-base"
    };

    return (
        <button
            className={cn(
                "rounded-xl font-medium transition-all duration-200 flex items-center justify-center gap-2",
                "disabled:opacity-50 disabled:cursor-not-allowed active:scale-95",
                variants[variant],
                sizes[size],
                className
            )}
            disabled={isLoading}
            {...props}
        >
            {isLoading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : children}
        </button>
    );
}
