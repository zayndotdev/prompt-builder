import React from 'react';
import { Target, CheckCircle2, TrendingUp, AlertCircle, Award } from 'lucide-react';

const SECTIONS_DEF = [
  { key: 'section_1_vision', title: '1. Vision & Problem', min: 500, target: 800 },
  { key: 'section_2_market', title: '2. Market Intel', min: 1000, target: 1500 },
  { key: 'section_3_personas', title: '3. Personas & Routine', min: 1200, target: 1500 },
  { key: 'section_4_competitors', title: '4. Competitors & Moat', min: 1200, target: 1500 },
  { key: 'section_5_features', title: '5. MVP Feature Specs', min: 2500, target: 3000 },
  { key: 'section_6_tech_arch', title: '6. Tech Architecture', min: 1500, target: 2000 },
  { key: 'section_7_api_contract', title: '7. REST API Contract', min: 1500, target: 2000 },
  { key: 'section_8_file_arch', title: '8. File Architecture', min: 600, target: 800 },
  { key: 'section_9_ui_ux', title: '9. UI/UX Design System', min: 1200, target: 1500 },
  { key: 'section_10_security', title: '10. Security & Perf', min: 800, target: 1000 },
  { key: 'section_11_execution_phases', title: '11. Phased IDE Steps', min: 1500, target: 2000 },
  { key: 'section_12_risks', title: '12. Risks & Exclusions', min: 500, target: 800 },
];

export default function WordCountTracker({ wordCounts = {}, totalWords = 0 }) {
  const TARGET_TOTAL = 15000;
  const progressPercent = Math.min(Math.round((totalWords / TARGET_TOTAL) * 100), 100);
  const isGoalReached = totalWords >= TARGET_TOTAL;

  return (
    <div className="bg-zinc-900/70 border border-zinc-800 rounded-2xl p-6 shadow-xl backdrop-blur">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5">
        <div className="flex items-center gap-2">
          <div className={`p-1.5 rounded-lg border ${
            isGoalReached 
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
              : 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
          }`}>
            {isGoalReached ? <Award className="w-5 h-5 text-emerald-400" /> : <Target className="w-5 h-5 text-indigo-400" />}
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white m-0">15,000+ Word Quality Auditor</h2>
            <p className="text-xs text-zinc-400 m-0">Enforcing zero-degrees-of-freedom density across all 12 sections</p>
          </div>
        </div>

        {/* Word count summary badge */}
        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="text-2xl font-bold font-mono text-white tracking-tight">
              {totalWords.toLocaleString()} <span className="text-sm font-normal text-zinc-500">/ 15,000 words</span>
            </div>
            <div className="text-xs text-zinc-400">
              {isGoalReached ? '100% Target Met (Full Depth)' : `${(TARGET_TOTAL - totalWords).toLocaleString()} words remaining to quota`}
            </div>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-zinc-950 rounded-full h-3 border border-zinc-800 overflow-hidden mb-6 relative">
        <div
          className={`h-full transition-all duration-700 ease-out rounded-full ${
            isGoalReached
              ? 'bg-gradient-to-r from-emerald-500 to-teal-400'
              : 'bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500'
          }`}
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* 12 Sections Breakdown Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2.5">
        {SECTIONS_DEF.map((sec) => {
          const count = wordCounts[sec.key] || 0;
          const meetsMin = count >= sec.min;
          const hasContent = count > 0;

          return (
            <div
              key={sec.key}
              className={`p-2.5 rounded-xl border transition-all ${
                meetsMin
                  ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300'
                  : hasContent
                  ? 'bg-amber-950/20 border-amber-500/30 text-amber-300'
                  : 'bg-zinc-950/40 border-zinc-800/80 text-zinc-500'
              }`}
            >
              <div className="flex items-center justify-between text-[11px] font-medium mb-1 line-clamp-1">
                <span className="text-zinc-200">{sec.title}</span>
                {meetsMin ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                ) : hasContent ? (
                  <TrendingUp className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
                ) : (
                  <span className="text-[10px] text-zinc-600">Pending</span>
                )}
              </div>

              <div className="flex items-baseline justify-between">
                <span className="font-mono text-sm font-bold text-white">{count.toLocaleString()}</span>
                <span className="text-[10px] text-zinc-400 font-mono">min {sec.min}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
