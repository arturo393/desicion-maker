import React from 'react';
import { Criterion, Option } from '../types';

interface Props {
  options: Option[];
  criteria: Criterion[];
  onConfirm: (options: Option[], criteria: Criterion[]) => void;
  isProcessing: boolean;
}

export const RefineSection: React.FC<Props> = ({ options: initialOptions, criteria: initialCriteria, onConfirm, isProcessing }) => {
  const [options, setOptions] = React.useState<Option[]>(initialOptions);
  const [criteria, setCriteria] = React.useState<Criterion[]>(initialCriteria);

  const handleCriterionWeightChange = (id: string, newWeight: number) => {
    setCriteria(prev => prev.map(c => c.id === id ? { ...c, weight: newWeight } : c));
  };

  const removeOption = (id: string) => {
    setOptions(prev => prev.filter(o => o.id !== id));
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-8 animate-fade-in">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Options Column */}
        <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span className="w-8 h-8 rounded-full bg-emerald-900/50 text-emerald-400 flex items-center justify-center text-sm border border-emerald-500/30">1</span>
            Confirmed Options
          </h2>
          <div className="space-y-3">
            {options.map(opt => (
              <div key={opt.id} className="bg-slate-900/50 p-4 rounded-lg border border-slate-700 flex justify-between items-start group">
                <div>
                  <div className="font-semibold text-white">{opt.name}</div>
                  <div className="text-xs text-slate-400 mt-1">{opt.description}</div>
                </div>
                <button 
                  onClick={() => removeOption(opt.id)}
                  className="text-slate-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Criteria Column */}
        <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span className="w-8 h-8 rounded-full bg-purple-900/50 text-purple-400 flex items-center justify-center text-sm border border-purple-500/30">2</span>
            Criteria Weighting
          </h2>
          <p className="text-xs text-slate-400 mb-4">Adjust sliders to reflect importance (1-10).</p>
          <div className="space-y-4">
            {criteria.map(crit => (
              <div key={crit.id} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-white font-medium">{crit.name}</span>
                  <span className="text-blue-400 font-mono">{crit.weight}</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  step="0.5"
                  value={crit.weight}
                  onChange={(e) => handleCriterionWeightChange(crit.id, parseFloat(e.target.value))}
                  className="w-full h-2 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-blue-500"
                />
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="flex justify-center">
        <button
          onClick={() => onConfirm(options, criteria)}
          disabled={isProcessing || options.length < 2}
          className={`px-8 py-3 rounded-xl font-bold text-lg transition-all shadow-lg ${
            isProcessing || options.length < 2
              ? 'bg-slate-700 text-slate-500'
              : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-900/50 hover:scale-105'
          }`}
        >
           {isProcessing ? 'Simulating Scenarios...' : 'Run Stochastic Analysis'}
        </button>
      </div>
    </div>
  );
};
