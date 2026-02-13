/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // The Void: Deepest backgrounds
                void: "#050505",
                obsidian: "#0a0a0a",
                mantle: "#111111",

                // Glass Accents
                "glass-border": "rgba(255, 255, 255, 0.08)",
                "glass-surface": "rgba(255, 255, 255, 0.03)",
                "glass-highlight": "rgba(255, 255, 255, 0.15)",

                // Functional Colors
                primary: {
                    DEFAULT: "#3b82f6", // Professional Blue
                    foreground: "#ffffff",
                },
                secondary: {
                    DEFAULT: "#64748b", // Slate
                    foreground: "#ffffff",
                }
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
            animation: {
                'spotlight': 'spotlight 2s ease .75s 1 forwards',
                'fade-in': 'fadeIn 0.5s ease-out forwards',
                'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
            keyframes: {
                spotlight: {
                    '0%': { opacity: 0, transform: 'translate(-72%, -62%) scale(0.5)' },
                    '100%': { opacity: 1, transform: 'translate(-50%,-40%) scale(1)' },
                },
                fadeIn: {
                    '0%': { opacity: 0, transform: 'translateY(10px)' },
                    '100%': { opacity: 1, transform: 'translateY(0)' },
                },
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                'obsidian-gradient': 'linear-gradient(to bottom right, #050505, #111111)',
            }
        },
    },
    plugins: [],
}
