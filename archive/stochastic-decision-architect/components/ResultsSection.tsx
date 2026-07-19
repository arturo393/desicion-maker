import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';
import { DecisionState, Evaluation, SimulationResult } from '../types';

interface Props {
  state: DecisionState;
  onReset: () => void;
}

export const ResultsSection: React.FC<Props> = ({ state, onReset }) => {
  const sortedResults = [...state.simulationResults].sort((a, b) => b.winProbability - a.winProbability);
  const winner = state.options.find(o => o.id === sortedResults[0].optionId);

  const chartData = sortedResults.map(res => {
    const opt = state.options.find(o => o.id === res.optionId);
    return {
      name: opt?.name || res.optionId,
      probability: (res.winProbability * 100).toFixed(1),
      avgScore: res.averageScore.toFixed(0),
    };
  });

  return (
    <div className="w-full max-w-6xl mx-auto space-y-8 pb-12">
      {/* Top Banner: Winner */}
      <div className="bg-gradient-to-r from-emerald-900/40 to-blue-900/40 border border-emerald-500/30 p-8 rounded-3xl text-center relative overflow-hidden">
        <div className="relative z-10">
          <h2 className="text-emerald-400 font-mono text-sm uppercase tracking-widest mb-2">Recommended Decision</h2>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">{winner?.name}</h1>
          <p className="text-slate-300 max-w-2xl mx-auto">{winner?.description}</p>
          <div className="mt-6 inline-flex items-center gap-2 bg-emerald-500/20 text-emerald-300 px-4 py-2 rounded-full border border-emerald-500/30">
            <span className="font-bold">{(sortedResults[0].winProbability * 100).toFixed(1)}%</span>
            <span>Win Probability in 2000 Simulations</span>
          </div>
        </div>
        <div className="absolute top-0 left-0 w-full h-full bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Chart */}
        <div className="lg:col-span-2 bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-xl">
           <h3 className="text-lg font-bold text-white mb-6">Stochastic Win Probability</h3>
           <div className="h-80 w-full">
             <ResponsiveContainer width="100%" height="100%">
               <BarChart data={chartData} layout="vertical" margin={{ left: 40, right: 40 }}>
                 <XAxis type="number" domain={[0, 100]} hide />
                 <YAxis dataKey="name" type="category" width={120} stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false}/>
                 <Tooltip 
                    cursor={{fill: 'rgba(255,255,255,0.05)'}}
                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }}
                 />
                 <Bar dataKey="probability" radius={[0, 4, 4, 0]} barSize={32}>
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={index === 0 ? '#10b981' : '#3b82f6'} />
                    ))}
                 </Bar>
               </BarChart>
             </ResponsiveContainer>
           </div>
           <p className="text-xs text-slate-400 mt-4 text-center">
             *Results based on Monte Carlo simulation considering weight and data uncertainty.
           </p>
        </div>

        {/* Data Sources */}
        <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-xl">
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <span className="text-blue-400">G</span>
            Google Grounding Sources
          </h3>
          <div className="space-y-3 max-h-80 overflow-y-auto pr-2 custom-scrollbar">
            {state.groundingSources.length === 0 ? (
                <p className="text-slate-500 text-sm">No specific web sources cited.</p>
            ) : (
                state.groundingSources.map((source, idx) => (
                <a 
                    key={idx} 
                    href={source.uri} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="block p-3 bg-slate-900/50 rounded-lg border border-slate-700 hover:border-blue-500 transition text-sm group"
                >
                    <div className="font-medium text-blue-300 group-hover:underline truncate">{source.title}</div>
                    <div className="text-slate-500 text-xs truncate mt-1">{source.uri}</div>
                </a>
                ))
            )}
          </div>
        </div>
      </div>

      {/* Detailed Matrix */}
      <div className="bg-slate-800 rounded-2xl border border-slate-700 overflow-hidden shadow-xl">
        <div className="p-6 border-b border-slate-700">
           <h3 className="text-lg font-bold text-white">Detailed Evaluation Matrix</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-900 text-xs uppercase font-medium text-slate-400">
              <tr>
                <th className="px-6 py-4">Criteria</th>
                {state.options.map(opt => (
                  <th key={opt.id} className="px-6 py-4">{opt.name}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {state.criteria.map(crit => (
                <tr key={crit.id} className="hover:bg-slate-700/30">
                  <td className="px-6 py-4 font-medium text-white">
                    {crit.name}
                    <div className="text-xs text-slate-500 font-normal mt-0.5">Weight: {crit.weight}</div>
                  </td>
                  {state.options.map(opt => {
                    const evaluation = state.evaluations.find(e => e.optionId === opt.id && e.criterionId === crit.id);
                    return (
                      <td key={opt.id} className="px-6 py-4 relative group">
                        <div className="flex items-center gap-2">
                          <span className={`font-bold ${
                              (evaluation?.score || 0) > 80 ? 'text-emerald-400' : 
                              (evaluation?.score || 0) > 50 ? 'text-yellow-400' : 'text-red-400'
                          }`}>
                            {evaluation?.score}
                          </span>
                          <span className="text-slate-600">/100</span>
                        </div>
                        {evaluation?.reasoning && (
                          <div className="absolute z-20 left-4 bottom-full mb-2 w-64 p-3 bg-slate-900 text-xs text-white rounded-lg shadow-xl border border-slate-600 opacity-0 group-hover:opacity-100 transition pointer-events-none">
                            {evaluation.reasoning}
                          </div>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="flex justify-center pt-8">
        <button 
          onClick={onReset}
          className="text-slate-400 hover:text-white transition flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
          Start New Decision
        </button>
      </div>
    </div>
  );
};
