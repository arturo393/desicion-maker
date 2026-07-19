import React, { useState } from 'react';

interface Props {
  onAnalyze: (topic: string, context: string) => void;
  isAnalyzing: boolean;
}

export const InputSection: React.FC<Props> = ({ onAnalyze, isAnalyzing }) => {
  const [topic, setTopic] = useState('');
  const [context, setContext] = useState('');

  return (
    <div className="w-full max-w-2xl mx-auto p-8 bg-slate-800 rounded-2xl shadow-xl border border-slate-700">
      <div className="mb-6 text-center">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
          Stochastic Decision Architect
        </h1>
        <p className="text-slate-400 mt-2">
          Make data-driven decisions using Google Search & Probabilistic Modeling
        </p>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            What decision do you need to make?
          </label>
          <input
            type="text"
            className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none transition"
            placeholder="e.g., Which framework should I use for my startup?"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Additional Context (Optional)
          </label>
          <textarea
            className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none transition h-24"
            placeholder="e.g., We are a team of 3 Python developers, looking for speed of development."
            value={context}
            onChange={(e) => setContext(e.target.value)}
          />
        </div>

        <button
          onClick={() => onAnalyze(topic, context)}
          disabled={!topic || isAnalyzing}
          className={`w-full py-4 rounded-lg font-bold text-lg transition-all flex items-center justify-center gap-2 ${
            !topic || isAnalyzing
              ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-900/50'
          }`}
        >
          {isAnalyzing ? (
            <>
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Researching Options...
            </>
          ) : (
            'Analyze Decision Space'
          )}
        </button>
      </div>
    </div>
  );
};
