import React from 'react';
import { Cpu, Settings as SettingsIcon, ShieldCheck, Sparkles } from 'lucide-react';

export default function Header({ providers, onOpenSettings }) {
  const providerList = [
    { key: 'cohere', name: 'Cohere', active: providers?.cohere },
    { key: 'groq', name: 'Groq', active: providers?.groq },
    { key: 'gemini', name: 'Gemini', active: providers?.gemini },
    { key: 'mistral', name: 'Mistral', active: providers?.mistral },
  ];

  return (
    <header className="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="p-2.5 rounded-xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-indigo-500/30 text-indigo-400">
          <Cpu className="w-6 h-6 animate-pulse" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold tracking-tight text-white m-0">PROMPT BUILDER</h1>
            <span className="px-2 py-0.5 text-xs font-semibold uppercase tracking-wider bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-full">
              v1.0 Swarm
            </span>
          </div>
          <p className="text-xs text-zinc-400 m-0">
            Autonomous Adversarial Multi-Agent Engine • 15,000+ Word Guaranteed Blueprints
          </p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Active Providers Badges */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs">
          <span className="text-zinc-500 font-medium mr-1">Free Tier Swarm:</span>
          {providerList.map((p) => (
            <div
              key={p.key}
              className={`flex items-center gap-1.5 px-2 py-0.5 rounded-md font-medium transition-colors ${
                p.active
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : 'bg-zinc-800 text-zinc-500 border border-zinc-700/50'
              }`}
            >
              <span
                className={`w-1.5 h-1.5 rounded-full ${
                  p.active ? 'bg-emerald-400 animate-pulse' : 'bg-zinc-600'
                }`}
              />
              {p.name}
            </div>
          ))}
        </div>

        {/* Settings button */}
        <button
          onClick={onOpenSettings}
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-zinc-300 hover:text-white border border-zinc-800 transition-all text-sm font-medium cursor-pointer shadow-sm hover:border-zinc-700"
        >
          <SettingsIcon className="w-4 h-4 text-zinc-400" />
          <span>API Keys</span>
        </button>
      </div>
    </header>
  );
}
