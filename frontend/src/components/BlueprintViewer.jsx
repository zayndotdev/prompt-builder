import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { BookOpen, List, Search, Copy, Check, ChevronRight } from 'lucide-react';

const SECTIONS_INDEX = [
  { id: 'sec-1', name: 'Section 1: Verified Product Vision', match: 'SECTION 1' },
  { id: 'sec-2', name: 'Section 2: Market & Industry Intel', match: 'SECTION 2' },
  { id: 'sec-3', name: 'Section 3: Target Audience & Personas', match: 'SECTION 3' },
  { id: 'sec-4', name: 'Section 4: Competitor Analysis & Moat', match: 'SECTION 4' },
  { id: 'sec-5', name: 'Section 5: Feature Specifications', match: 'SECTION 5' },
  { id: 'sec-6', name: 'Section 6: Technical Architecture', match: 'SECTION 6' },
  { id: 'sec-7', name: 'Section 7: Full REST API Contract', match: 'SECTION 7' },
  { id: 'sec-8', name: 'Section 8: File Architecture', match: 'SECTION 8' },
  { id: 'sec-9', name: 'Section 9: UI/UX & Design System', match: 'SECTION 9' },
  { id: 'sec-10', name: 'Section 10: Security & Benchmarks', match: 'SECTION 10' },
  { id: 'sec-11', name: 'Section 11: Phased IDE Instructions', match: 'SECTION 11' },
  { id: 'sec-12', name: 'Section 12: Known Risks & Exclusions', match: 'SECTION 12' },
];

export default function BlueprintViewer({ finalBlueprint }) {
  const [copied, setCopied] = useState(false);
  const [filterText, setFilterText] = useState('');

  const handleCopyFull = async () => {
    try {
      await navigator.clipboard.writeText(finalBlueprint);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy', err);
    }
  };

  const scrollToSection = (matchStr) => {
    // Find heading in the document containing matchStr
    const headings = document.querySelectorAll('h2');
    for (const h of headings) {
      if (h.innerText.includes(matchStr)) {
        h.scrollIntoView({ behavior: 'smooth', block: 'start' });
        break;
      }
    }
  };

  if (!finalBlueprint) return null;

  return (
    <div className="bg-zinc-900/70 border border-zinc-800 rounded-2xl p-6 shadow-xl backdrop-blur">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <BookOpen className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white m-0">Generated Master Blueprint</h2>
            <p className="text-xs text-zinc-400 m-0">Zero degrees of freedom architecture document</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleCopyFull}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 hover:text-white text-xs font-medium border border-zinc-700 transition-colors cursor-pointer"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied Document' : 'Copy All Markdown'}</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Sticky Table of Contents */}
        <div className="lg:col-span-3">
          <div className="sticky top-24 bg-zinc-950/80 border border-zinc-800/80 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-3 text-xs font-semibold uppercase tracking-wider text-zinc-400">
              <List className="w-3.5 h-3.5 text-indigo-400" />
              <span>Table of Contents</span>
            </div>
            
            <nav className="space-y-1">
              {SECTIONS_INDEX.map((sec, idx) => (
                <button
                  key={sec.id}
                  onClick={() => scrollToSection(sec.match)}
                  className="w-full text-left px-2.5 py-1.5 rounded-lg text-xs text-zinc-400 hover:text-white hover:bg-zinc-900 transition-colors flex items-center justify-between group cursor-pointer"
                >
                  <span className="truncate">{sec.name}</span>
                  <ChevronRight className="w-3 h-3 opacity-0 group-hover:opacity-100 text-indigo-400 transition-opacity" />
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Rendered Markdown Document */}
        <div className="lg:col-span-9 bg-zinc-950 border border-zinc-800/80 rounded-xl p-6 sm:p-8 overflow-x-auto text-left">
          <article className="prose prose-invert max-w-none prose-headings:text-white prose-h1:text-2xl prose-h2:text-xl prose-h2:border-b prose-h2:border-zinc-800 prose-h2:pb-2 prose-h2:mt-8 prose-h3:text-lg prose-p:text-zinc-300 prose-p:leading-relaxed prose-code:text-indigo-300 prose-code:bg-zinc-900 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-pre:bg-zinc-900 prose-pre:border prose-pre:border-zinc-800 prose-table:border prose-table:border-zinc-800 prose-th:bg-zinc-900 prose-th:p-2 prose-td:p-2 prose-td:border-t prose-td:border-zinc-800">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {finalBlueprint}
            </ReactMarkdown>
          </article>
        </div>
      </div>
    </div>
  );
}
