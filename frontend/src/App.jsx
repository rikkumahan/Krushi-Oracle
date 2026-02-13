import React from 'react';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import { ChatInterface } from './components/ChatInterface';
import { ThemeToggle } from './components/ui/ThemeToggle';
import { LayoutGrid, Globe, BarChart3, Settings } from 'lucide-react';
import { Card } from './components/ui/Card';
import { Button } from './components/ui/Button';
import { NeuralInput } from './components/ui/NeuralInput';

function AppContent() {
  const { theme } = useTheme();

  return (
    <div className={`flex h-screen w-screen overflow-hidden font-sans transition-colors duration-300 ${theme === 'dark' ? 'bg-[#050505]' : 'bg-slate-50'
      }`}>
      {/* Noise Texture Overlay */}
      <div className="bg-noise"></div>

      {/* Glass Sidebar */}
      <aside className={`w-20 lg:w-64 border-r flex flex-col items-center lg:items-stretch py-6 z-20 transition-all duration-300 ${theme === 'dark' ? 'border-white/5 bg-black/20' : 'border-slate-200 bg-white/80'
        } backdrop-blur-xl`}>
        <div className="px-4 mb-10 flex items-center justify-center lg:justify-start gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 shadow-[0_0_15px_rgba(99,102,241,0.5)] flex items-center justify-center text-white font-bold text-xs">
            IL
          </div>
          <span className={`hidden lg:block font-bold text-lg tracking-tight ${theme === 'dark' ? 'text-white/90' : 'text-slate-800'
            }`}>
            IdeaLab <span className="text-xs font-mono text-indigo-500 ml-1">v2.0</span>
          </span>
        </div>

        <nav className="flex-1 px-2 space-y-1">
          <NavItem icon={LayoutGrid} label="New Chat" active={true} />
          <NavItem icon={Globe} label="Discover" />
          <NavItem icon={BarChart3} label="History" />
        </nav>

        <div className="p-4 border-t space-y-4">
          <ThemeToggle className="w-full flex justify-center lg:justify-start" />
          <NavItem icon={Settings} label="Settings" />
        </div>
      </aside>

      {/* Main Stage */}
      <main className="flex-1 relative z-10 flex flex-col">
        {/* Top Decoration */}
        <div className={`absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-${theme === 'dark' ? 'white/10' : 'slate-200'} to-transparent`}></div>

        <ChatInterface />

      </main>
    </div>
  );
}

// eslint-disable-next-line no-unused-vars
function NavItem({ icon: Icon, label, active, onClick }) {
  const { theme } = useTheme();
  return (
    <button
      onClick={onClick}
      className={`w-full flex lg:justify-start justify-center items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group ${active
        ? theme === 'dark'
          ? 'bg-white/10 text-white shadow-lg shadow-black/20 border border-white/5'
          : 'bg-white text-indigo-600 shadow-sm border border-slate-200'
        : theme === 'dark'
          ? 'text-slate-400 hover:text-white hover:bg-white/5'
          : 'text-slate-500 hover:text-indigo-600 hover:bg-slate-100'
        }`}
    >
      <Icon className={`w-5 h-5 ${active ? 'text-indigo-500' : 'text-current transition-colors'}`} />
      <span className="hidden lg:block text-sm font-medium">{label}</span>
      {active && <div className="hidden lg:block ml-auto w-1 h-1 rounded-full bg-indigo-500 shadow-[0_0_5px_rgba(99,102,241,1)]"></div>}
    </button>
  )
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;
