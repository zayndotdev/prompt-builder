import React, { useState } from 'react';
import { Copy, Download, Check, Sparkles, Terminal, FileCode2, Share2 } from 'lucide-react';

export default function ExportActions({ jobId, finalBlueprint, onExport }) {
  const [copiedFormat, setCopiedFormat] = useState(null);

  const handleCopy = async (format) => {
    let contentToCopy = finalBlueprint;

    if (format === 'cursor') {
      contentToCopy = `# CURSOR PROJECT RULES & MASTER ARCHITECT SPECIFICATION\n# Place this file in your project root as .cursorrules or paste into Cursor Composer.\n# DIRECTIVE: Autonomous fullstack execution with zero assumptions.\n--------------------------------------------------------------------------------\n\n` + finalBlueprint;
    } else if (format === 'claude') {
      contentToCopy = `# CLAUDE CODE CLI MASTER DIRECTIVE\n# INSTRUCTION FOR CLAUDE: Follow the 12-section architecture with zero deviations.\n--------------------------------------------------------------------------------\n\n` + finalBlueprint;
    } else if (format === 'antigravity') {
      contentToCopy = `# GOOGLE ANTIGRAVITY MASTER PROMPT\n# DIRECTIVE: Multi-agent execution with zero degrees of freedom.\n--------------------------------------------------------------------------------\n\n` + finalBlueprint;
    }

    try {
      await navigator.clipboard.writeText(contentToCopy);
      setCopiedFormat(format);
      setTimeout(() => setCopiedFormat(null), 2500);
    } catch (err) {
      console.error('Failed to copy to clipboard', err);
    }
  };

  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([finalBlueprint], { type: 'text/markdown' });
    element.href = URL.createObjectURL(file);
    element.download = `MASTER_BLUEPRINT_${new Date().toISOString().slice(0, 10)}.md`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  if (!finalBlueprint) return null;

  return (
    <div className="bg-gradient-to-r from-zinc-900 to-indigo-950/40 border border-indigo-500/30 rounded-2xl p-6 shadow-2xl backdrop-blur flex flex-col md:flex-row items-center justify-between gap-4">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-white m-0">Master Blueprint Ready for AI IDEs</h3>
        </div>
        <p className="text-xs text-zinc-400 m-0">
          Export pre-formatted one-shot prompts with zero degrees of freedom for your IDE.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {/* Copy for Cursor */}
        <button
          onClick={() => handleCopy('cursor')}
          className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-semibold border border-zinc-700 transition-all cursor-pointer shadow-sm active:scale-95"
        >
          {copiedFormat === 'cursor' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Terminal className="w-3.5 h-3.5 text-indigo-400" />}
          <span>{copiedFormat === 'cursor' ? 'Copied Cursor Prompt!' : 'Copy for Cursor'}</span>
        </button>

        {/* Copy for Claude Code */}
        <button
          onClick={() => handleCopy('claude')}
          className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-semibold border border-zinc-700 transition-all cursor-pointer shadow-sm active:scale-95"
        >
          {copiedFormat === 'claude' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <FileCode2 className="w-3.5 h-3.5 text-amber-400" />}
          <span>{copiedFormat === 'claude' ? 'Copied Claude Prompt!' : 'Copy for Claude'}</span>
        </button>

        {/* Copy for Antigravity */}
        <button
          onClick={() => handleCopy('antigravity')}
          className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-semibold border border-zinc-700 transition-all cursor-pointer shadow-sm active:scale-95"
        >
          {copiedFormat === 'antigravity' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Sparkles className="w-3.5 h-3.5 text-purple-400" />}
          <span>{copiedFormat === 'antigravity' ? 'Copied Antigravity!' : 'Copy Antigravity'}</span>
        </button>

        {/* Download File */}
        <button
          onClick={handleDownload}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold border border-indigo-400/30 transition-all cursor-pointer shadow-md shadow-indigo-600/30 active:scale-95"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Download .md</span>
        </button>
      </div>
    </div>
  );
}
