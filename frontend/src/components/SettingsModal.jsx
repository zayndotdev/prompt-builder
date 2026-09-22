import React, { useState } from 'react';
import { X, Key, ShieldCheck, Save, ExternalLink } from 'lucide-react';

export default function SettingsModal({ isOpen, onClose, onSaveKeys }) {
  const [keys, setKeys] = useState({
    groq_key: '',
    gemini_key: '',
    cohere_key: '',
    mistral_key: '',
  });
  const [saving, setSaving] = useState(false);
  const [savedMsg, setSavedMsg] = useState(false);

  if (!isOpen) return null;

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await onSaveKeys(keys);
      setSavedMsg(true);
      setTimeout(() => setSavedMsg(false), 2000);
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl relative text-left">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Key className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white m-0">Free Tier API Keys</h3>
            <p className="text-xs text-zinc-400 m-0">
              Provide or update your free provider keys. Stored in memory on backend.
            </p>
          </div>
        </div>

        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="text-xs font-semibold text-zinc-300">Groq API Key (Fast Inference)</label>
              <a href="https://console.groq.com/keys" target="_blank" rel="noreferrer" className="text-[11px] text-indigo-400 hover:underline flex items-center gap-0.5">
                Get free key <ExternalLink className="w-2.5 h-2.5" />
              </a>
            </div>
            <input
              type="password"
              placeholder="gsk_..."
              value={keys.groq_key}
              onChange={(e) => setKeys({ ...keys, groq_key: e.target.value })}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3.5 py-2 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="text-xs font-semibold text-zinc-300">Google Gemini API Key</label>
              <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer" className="text-[11px] text-indigo-400 hover:underline flex items-center gap-0.5">
                Get free key <ExternalLink className="w-2.5 h-2.5" />
              </a>
            </div>
            <input
              type="password"
              placeholder="AIza..."
              value={keys.gemini_key}
              onChange={(e) => setKeys({ ...keys, gemini_key: e.target.value })}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3.5 py-2 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="text-xs font-semibold text-zinc-300">Cohere API Key</label>
              <a href="https://dashboard.cohere.com/api-keys" target="_blank" rel="noreferrer" className="text-[11px] text-indigo-400 hover:underline flex items-center gap-0.5">
                Get free key <ExternalLink className="w-2.5 h-2.5" />
              </a>
            </div>
            <input
              type="password"
              placeholder="cohere_..."
              value={keys.cohere_key}
              onChange={(e) => setKeys({ ...keys, cohere_key: e.target.value })}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3.5 py-2 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="text-xs font-semibold text-zinc-300">Mistral API Key</label>
              <a href="https://console.mistral.ai/api-keys" target="_blank" rel="noreferrer" className="text-[11px] text-indigo-400 hover:underline flex items-center gap-0.5">
                Get free key <ExternalLink className="w-2.5 h-2.5" />
              </a>
            </div>
            <input
              type="password"
              placeholder="Enter Mistral key..."
              value={keys.mistral_key}
              onChange={(e) => setKeys({ ...keys, mistral_key: e.target.value })}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3.5 py-2 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="pt-2 flex items-center justify-between">
            {savedMsg ? (
              <span className="text-xs text-emerald-400 font-medium flex items-center gap-1">
                <ShieldCheck className="w-4 h-4" /> Keys updated in runtime!
              </span>
            ) : <span />}

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-medium transition-colors cursor-pointer"
              >
                Close
              </button>
              <button
                type="submit"
                disabled={saving}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-all cursor-pointer shadow-md active:scale-95 disabled:opacity-50"
              >
                <Save className="w-3.5 h-3.5" />
                <span>{saving ? 'Updating...' : 'Save Keys'}</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
