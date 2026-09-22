import React, { useState } from 'react';
import { Sparkles, Terminal, Code2, Layers, Flame, ArrowRight, CheckCircle2 } from 'lucide-react';

const SAMPLE_IDEAS = [
  {
    title: 'Plumbing & HVAC Voice AI',
    desc: 'An AI voice agent for plumbing and HVAC contractors that answers emergency calls 24/7, qualifies leaks/furnace issues, and books dispatches into ServiceTitan or Jobber.'
  },
  {
    title: 'Autonomous Code Review Bot',
    desc: 'A GitHub App that runs AST-level static analysis, checks for OWASP Top 10 vulnerabilities, and posts inline pull request review comments with auto-fix patches.'
  },
  {
    title: 'Local-First Architecture Canvas',
    desc: 'An offline-capable collaborative infinite canvas for system architecture diagrams, built with CRDTs (Yjs), WebAssembly SQLite, and instant SVG/Terraform export.'
  }
];

export default function PromptInput({ onSubmit, isGenerating }) {
  const [idea, setIdea] = useState('');
  const [targetIde, setTargetIde] = useState('all');
  const [backendStack, setBackendStack] = useState('FastAPI (Python 3.11)');
  const [frontendStack, setFrontendStack] = useState('React + Vite + Tailwind');
  const [dbStack, setDbStack] = useState('PostgreSQL');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!idea.trim() || isGenerating) return;

    onSubmit({
      raw_idea: idea.trim(),
      user_constraints: {
        target_ide: targetIde,
        backend: backendStack,
        frontend: frontendStack,
        database: dbStack,
      }
    });
  };

  return (
    <div className="bg-zinc-900/70 border border-zinc-800 rounded-2xl p-6 shadow-xl backdrop-blur">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Flame className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white m-0">Input Your Raw Product Concept</h2>
            <p className="text-xs text-zinc-400 m-0">Our 11 adversarial agents will dissect, research, and engineer the 15,000+ word specification.</p>
          </div>
        </div>

        {/* Quick Sample Selector */}
        <div className="hidden sm:flex items-center gap-2 text-xs">
          <span className="text-zinc-500">Quick Samples:</span>
          {SAMPLE_IDEAS.map((sample, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => setIdea(sample.desc)}
              className="px-2.5 py-1 rounded-md bg-zinc-800 hover:bg-zinc-700 text-zinc-300 hover:text-white border border-zinc-700/50 transition-colors cursor-pointer"
            >
              {sample.title}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Main Text Area */}
        <div className="relative">
          <textarea
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            disabled={isGenerating}
            placeholder="Describe your product idea in plain English... e.g. A marketplace connecting freelance video editors with YouTubers, featuring automated video file transcoding, Stripe escrow payments, and timestamped frame-accurate review comments."
            rows={4}
            className="w-full bg-zinc-950/80 border border-zinc-800 rounded-xl p-4 text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all text-sm resize-none disabled:opacity-50"
          />
          <div className="absolute right-3 bottom-3 text-xs text-zinc-500">
            {idea.length} chars
          </div>
        </div>

        {/* Target IDE & Stack Configurations */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 pt-1">
          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1.5 flex items-center gap-1">
              <Terminal className="w-3.5 h-3.5 text-zinc-500" />
              Target AI IDE
            </label>
            <select
              value={targetIde}
              onChange={(e) => setTargetIde(e.target.value)}
              disabled={isGenerating}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-xs text-zinc-200 focus:outline-none focus:border-indigo-500 cursor-pointer"
            >
              <option value="all">Universal (Cursor / Claude / Antigravity)</option>
              <option value="cursor">Cursor Composer (.cursorrules)</option>
              <option value="claude">Claude Code CLI (CLAUDE.md)</option>
              <option value="antigravity">Google Antigravity Blueprint</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1.5 flex items-center gap-1">
              <Code2 className="w-3.5 h-3.5 text-zinc-500" />
              Backend Framework
            </label>
            <select
              value={backendStack}
              onChange={(e) => setBackendStack(e.target.value)}
              disabled={isGenerating}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-xs text-zinc-200 focus:outline-none focus:border-indigo-500 cursor-pointer"
            >
              <option value="FastAPI (Python 3.11)">FastAPI (Python 3.11)</option>
              <option value="Node.js + Express">Node.js + Express (TypeScript)</option>
              <option value="Go / Gin">Go / Gin REST API</option>
              <option value="Serverless Cloud Functions">Serverless Cloud Functions</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1.5 flex items-center gap-1">
              <Layers className="w-3.5 h-3.5 text-zinc-500" />
              Frontend UI
            </label>
            <select
              value={frontendStack}
              onChange={(e) => setFrontendStack(e.target.value)}
              disabled={isGenerating}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-xs text-zinc-200 focus:outline-none focus:border-indigo-500 cursor-pointer"
            >
              <option value="React + Vite + Tailwind">React + Vite + Tailwind</option>
              <option value="Next.js App Router">Next.js App Router</option>
              <option value="Vue 3 + Tailwind">Vue 3 + Tailwind</option>
              <option value="Headless / API Only">Headless / API Only</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1.5 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-zinc-500" />
              Database
            </label>
            <select
              value={dbStack}
              onChange={(e) => setDbStack(e.target.value)}
              disabled={isGenerating}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-xs text-zinc-200 focus:outline-none focus:border-indigo-500 cursor-pointer"
            >
              <option value="PostgreSQL">PostgreSQL (Relational)</option>
              <option value="SQLite / Turso">SQLite / Turso (Embedded)</option>
              <option value="Supabase">Supabase (Postgres + Auth)</option>
              <option value="MongoDB">MongoDB (Document)</option>
            </select>
          </div>
        </div>

        {/* Launch Button */}
        <div className="pt-2 flex justify-end">
          <button
            type="submit"
            disabled={!idea.trim() || isGenerating}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-sm transition-all shadow-lg cursor-pointer ${
              !idea.trim() || isGenerating
                ? 'bg-zinc-800 text-zinc-500 cursor-not-allowed border border-zinc-700/50'
                : 'bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-indigo-500/25 hover:shadow-indigo-500/40 hover:scale-[1.01] active:scale-[0.99]'
            }`}
          >
            {isGenerating ? (
              <>
                <Sparkles className="w-4 h-4 animate-spin text-indigo-300" />
                <span>Multi-Agent Swarm In Progress...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-indigo-200" />
                <span>Engineer Master Blueprint</span>
                <ArrowRight className="w-4 h-4 text-indigo-200" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
