import React from 'react';
import { cn } from '../../lib/utils';

export function Card({ className, children, ...props }) {
    return (
        <div
            className={cn(
                "glass-panel rounded-xl p-6 relative overflow-hidden group transition-all duration-300 hover:shadow-cyan-500/10 hover:border-white/10",
                className
            )}
            {...props}
        >
            {/* Subtle glare effect on hover */}
            <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

            <div className="relative z-10">
                {children}
            </div>
        </div>
    );
}
