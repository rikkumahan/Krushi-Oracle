import React from 'react';
import { cn } from '../../utils/cn';

export function Card({ className, children, ...props }) {
    return (
        <div
            className={cn(
                "glass-dark rounded-2xl p-6",
                "border border-white/5",
                className
            )}
            {...props}
        >
            {children}
        </div>
    );
}
