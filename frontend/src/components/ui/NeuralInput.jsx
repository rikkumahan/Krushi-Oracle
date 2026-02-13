import React from 'react';
import { useTheme } from '../../context/ThemeContext';

export function NeuralInput({ value, onChange, onKeyDown, placeholder, disabled, className = '' }) {
    const { theme } = useTheme();

    return (
        <textarea
            value={value}
            onChange={onChange}
            onKeyDown={onKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className={`w-full p-4 rounded-xl border transition-all duration-300 outline-none resize-none overflow-hidden ${theme === 'dark'
                    ? 'bg-black/40 border-white/10 text-white placeholder:text-slate-600 focus:border-indigo-500/50 focus:shadow-[0_0_15px_rgba(99,102,241,0.2)]'
                    : 'bg-white border-slate-200 text-slate-800 placeholder:text-slate-400 focus:border-indigo-400 focus:shadow-md'
                } ${className}`}
            style={{ minHeight: '50px' }}
        />
    );
}
