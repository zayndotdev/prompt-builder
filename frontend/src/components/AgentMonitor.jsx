import React, { useRef, useEffect } from 'react';
import { 
  ShieldAlert, 
  Globe, 
  Cpu, 
  ListChecks, 
  Users, 
  Crosshair, 
  Palette, 
  Network, 
  Lock, 
  AlertTriangle, 
  FileCheck2, 
  Terminal as TerminalIcon,
  CheckCircle2,
  Loader2,
  Clock
} from 'lucide-react';

const AGENTS = [
  { id: 'red_team', name: 'Agent 1: Red Team Critic', role: 'Adversarial grill & survival concept', icon: ShieldAlert },
  { id: 'research', name: 'Agent 2: Web Intelligence', role: '5-category DuckDuckGo market scan', icon: Globe },
  { id: 'architect', name: 'Agent 3: Systems Architect', role: 'DB schemas, stack, & integrations', icon: Cpu },
  { id: 'features', name: 'Agent 4: Feature Architect', role: 'Zero-ambiguity MVP feature specs', icon: ListChecks },
  { id: 'personas', name: 'Agent 5: Audience & Personas', role: 'Daily routine, pain, WCAG AA', icon: Users },
  { id: 'competitors', name: 'Agent 6: Competitor Analyst', role: 'Top 5 direct/indirect & moat matrix', icon: Crosshair },
  { id: 'ui_ux', name: 'Agent 7: UI/UX & Design', role: 'Hex palette, layout, screens', icon: Palette },
  { id: 'api_contract', name: 'Agent 8: API Contract Lead', role: 'Every endpoint request/response JSON', icon: Network },
  { id: 'security', name: 'Agent 9: Security & Benchmarks', role: 'Auth, OWASP, p95 benchmarks', icon: Lock },
  { id: 'risks', name: 'Agent 10: Risks & Exclusions', role: 'Anti-patterns & explicit scope bounds', icon: AlertTriangle },
  { id: 'compiler', name: 'Agent 11: Inspector & Compiler', role: '15,000+ word audit & assembly', icon: FileCheck2 },
];

export default function AgentMonitor({ activeAgent, currentStep, logs = [], status, isComplete }) {
  const terminalRef = useRef(null);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  const getAgentState = (agentName) => {
    if (isComplete) return 'done';
    if (!status || status === 'queued') return 'pending';
    
    // Check if current agent matches
    if (activeAgent && activeAgent.toLowerCase().includes(agentName.toLowerCase().replace(/agent \d+: /i, ''))) {
      return 'active';
    }
    
    // Check if agent was previously completed in logs
    const completedInLogs = logs.some(l => 
      l.toLowerCase().includes(agentName.toLowerCase()) || 
      l.toLowerCase().includes(agentName.split(':')[1]?.trim()?.toLowerCase() || '___')
    );

    if (completedInLogs) return 'done';
    return 'pending';
  };

  return (
    <div className="bg-zinc-900/70 border border-zinc-800 rounded-2xl p-6 shadow-xl backdrop-blur">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <Cpu className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white m-0">11-Agent Swarm Pipeline</h2>
            <p className="text-xs text-zinc-400 m-0">
              {currentStep || 'Ready for activation'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${
            isComplete
              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
              : status === 'processing'
              ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse'
              : 'bg-zinc-800 text-zinc-400'
          }`}>
            {isComplete ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5" />
                Swarm Complete
              </>
            ) : status === 'processing' ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                Active Execution
              </>
            ) : (
              <>
                <Clock className="w-3.5 h-3.5" />
                Standby
              </>
            )}
          </span>
        </div>
      </div>

      {/* Agents Flowchart Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2.5 mb-6">
        {AGENTS.map((agent, i) => {
          const state = getAgentState(agent.name);
          const Icon = agent.icon;
          return (
            <div
              key={agent.id}
              className={`p-3 rounded-xl border transition-all relative overflow-hidden flex flex-col justify-between ${
                state === 'active'
                  ? 'bg-indigo-950/40 border-indigo-500/60 ring-1 ring-indigo-500/40 shadow-lg shadow-indigo-500/10'
                  : state === 'done'
                  ? 'bg-zinc-900/90 border-emerald-500/30'
                  : 'bg-zinc-950/40 border-zinc-800/80 opacity-60'
              }`}
            >
              {state === 'active' && (
                <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-500 to-purple-500 animate-pulse" />
              )}
              
              <div className="flex items-center justify-between mb-2">
                <div className={`p-1.5 rounded-lg ${
                  state === 'active'
                    ? 'bg-indigo-500/20 text-indigo-400'
                    : state === 'done'
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : 'bg-zinc-800/60 text-zinc-500'
                }`}>
                  <Icon className="w-4 h-4" />
                </div>
                {state === 'done' && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                {state === 'active' && <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />}
              </div>

              <div>
                <div className="text-xs font-semibold text-zinc-200 line-clamp-1">{agent.name.split(':')[1]?.trim() || agent.name}</div>
                <div className="text-[10px] text-zinc-400 line-clamp-1 mt-0.5">{agent.role}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Live Terminal Output */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <TerminalIcon className="w-3.5 h-3.5 text-zinc-400" />
          <span className="text-xs font-mono font-medium text-zinc-400 uppercase tracking-wider">Live Agent Telemetry & Logs</span>
        </div>
        <div
          ref={terminalRef}
          className="w-full h-44 bg-zinc-950 border border-zinc-800/80 rounded-xl p-3.5 font-mono text-xs text-zinc-300 overflow-y-auto space-y-1.5 scrollbar-thin scrollbar-thumb-zinc-800"
        >
          {logs.length === 0 ? (
            <div className="text-zinc-600 italic">Telemetry stream will initialize once swarm is dispatched...</div>
          ) : (
            logs.map((log, index) => (
              <div key={index} className="flex items-start gap-2 leading-relaxed">
                <span className="text-zinc-600 select-none">{String(index + 1).padStart(2, '0')}</span>
                <span className={
                  log.includes('[Error]') 
                    ? 'text-red-400 font-semibold' 
                    : log.includes('Successfully') || log.includes('Complete') || log.includes('passed')
                    ? 'text-emerald-400'
                    : log.includes('===>')
                    ? 'text-indigo-400'
                    : log.includes('Expanded')
                    ? 'text-amber-400'
                    : 'text-zinc-300'
                }>
                  {log}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
