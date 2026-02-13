import React from 'react';
import { useTheme } from '../../context/ThemeContext';

export function Button({ children, onClick, disabled, className = '', variant = 'primary', size = 'md' }) {
    const { theme } = useTheme();

    const variants = {
        primary: 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-lg shadow-indigo-500/25',
        outline: theme === 'dark'
            ? 'border border-white/10 hover:bg-white/5 text-slate-300'
            : 'border border-slate-200 hover:bg-slate-50 text-slate-600',
        ghost: 'hover:bg-white/5 text-slate-400 hover:text-white',
    };

    const sizes = {
        sm: 'px-3 py-1.5 text-xs',
        md: 'px-4 py-2 text-sm',
        lg: 'px-6 py-3 text-base',
    };

    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className={`rounded-lg font-medium transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed ${variants[variant]} ${sizes[size]} ${className}`}
        >
            {children}
        </button>
    );
}
