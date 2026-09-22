import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import PromptInput from './components/PromptInput';
import AgentMonitor from './components/AgentMonitor';
import WordCountTracker from './components/WordCountTracker';
import ExportActions from './components/ExportActions';
import BlueprintViewer from './components/BlueprintViewer';
import SettingsModal from './components/SettingsModal';

const API_BASE = 'http://localhost:8000/api';

export default function App() {
  const [providers, setProviders] = useState({ cohere: true, groq: true, gemini: true, mistral: true });
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null); // 'queued', 'processing', 'completed', 'failed'
  const [activeAgent, setActiveAgent] = useState('');
  const [currentStep, setCurrentStep] = useState('');
  const [logs, setLogs] = useState([]);
  const [wordCounts, setWordCounts] = useState({});
  const [totalWords, setTotalWords] = useState(0);
  const [finalBlueprint, setFinalBlueprint] = useState('');
  const [isComplete, setIsComplete] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Fetch initial provider status
  useEffect(() => {
    fetch(`${API_BASE}/config/providers`)
      .then((res) => res.json())
      .then((data) => {
        if (data.providers) setProviders(data.providers);
      })
      .catch((err) => console.log('Backend not connected yet or loading:', err));
  }, []);

  const handleLaunch = async (payload) => {
    setErrorMsg(null);
    setStatus('processing');
    setLogs(['Initiating Multi-Agent Swarm...']);
    setWordCounts({});
    setTotalWords(0);
    setFinalBlueprint('');
    setIsComplete(false);

    try {
      const res = await fetch(`${API_BASE}/blueprint/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to start swarm');
      }

      const data = await res.json();
      const currentJobId = data.job_id;
      setJobId(currentJobId);

      // Connect to SSE stream
      const eventSource = new EventSource(`${API_BASE}/blueprint/stream/${currentJobId}`);

      eventSource.addEventListener('progress', (e) => {
        try {
          const progress = JSON.parse(e.data);
          if (progress.active_agent) setActiveAgent(progress.active_agent);
          if (progress.current_step) setCurrentStep(progress.current_step);
          if (progress.new_logs && progress.new_logs.length > 0) {
            setLogs((prev) => [...prev, ...progress.new_logs]);
          }
          if (progress.word_counts) setWordCounts(progress.word_counts);
          if (progress.total_words) setTotalWords(progress.total_words);
          if (progress.status) setStatus(progress.status);
          if (progress.is_complete) setIsComplete(true);
        } catch (err) {
          console.error('Error parsing SSE progress', err);
        }
      });

      eventSource.addEventListener('done', (e) => {
        try {
          const doneData = JSON.parse(e.data);
          if (doneData.final_blueprint) setFinalBlueprint(doneData.final_blueprint);
          setStatus(doneData.status);
          setIsComplete(doneData.status === 'completed');
        } catch (err) {
          console.error('Error parsing SSE done', err);
        }
        eventSource.close();
      });

      eventSource.onerror = (err) => {
        console.error('SSE Stream Error:', err);
        eventSource.close();
      };

    } catch (err) {
      console.error(err);
      setErrorMsg(err.message);
      setStatus('failed');
      setLogs((prev) => [...prev, `[Error] ${err.message}`]);
    }
  };

  const handleSaveKeys = async (keys) => {
    const res = await fetch(`${API_BASE}/config/providers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(keys)
    });
    const data = await res.json();
    if (data.providers) setProviders(data.providers);
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col">
      <Header providers={providers} onOpenSettings={() => setSettingsOpen(true)} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8 space-y-8">
        {/* Error Alert */}
        {errorMsg && (
          <div className="p-4 rounded-xl bg-red-950/40 border border-red-500/50 text-red-300 text-sm">
            <strong>Execution Error:</strong> {errorMsg}
          </div>
        )}

        {/* Section 1: Prompt Input */}
        <PromptInput onSubmit={handleLaunch} isGenerating={status === 'processing'} />

        {/* Section 2: Agent Monitor & Live Telemetry */}
        <AgentMonitor
          activeAgent={activeAgent}
          currentStep={currentStep}
          logs={logs}
          status={status}
          isComplete={isComplete}
        />

        {/* Section 3: Word Count Quota Auditor */}
        <WordCountTracker wordCounts={wordCounts} totalWords={totalWords} />

        {/* Section 4: Export Actions (when ready) */}
        {finalBlueprint && (
          <ExportActions
            jobId={jobId}
            finalBlueprint={finalBlueprint}
          />
        )}

        {/* Section 5: Rendered Markdown Blueprint */}
        {finalBlueprint && (
          <BlueprintViewer finalBlueprint={finalBlueprint} />
        )}
      </main>

      <footer className="border-t border-zinc-900 bg-zinc-950/90 py-6 text-center text-xs text-zinc-500">
        <p className="m-0">
          Prompt Builder Swarm • Engineered for Cursor, Claude Code, and Antigravity • Free-Tier Multi-LLM Architecture
        </p>
      </footer>

      <SettingsModal
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        onSaveKeys={handleSaveKeys}
      />
    </div>
  );
}
