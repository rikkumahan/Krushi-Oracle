import React from 'react';
import { useTheme } from '../../context/ThemeContext';
import { Sun, Moon } from 'lucide-react';

export function ThemeToggle({ className = '' }) {
    const { theme, toggleTheme } = useTheme();

    return (
        <button
            onClick={toggleTheme}
            className={`p-2 rounded-lg transition-colors duration-200 ${theme === 'dark'
                    ? 'bg-white/5 hover:bg-white/10 text-yellow-400'
                    : 'bg-slate-100 hover:bg-slate-200 text-indigo-600'
                } ${className}`}
            aria-label="Toggle theme"
        >
            {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>
    );
}
