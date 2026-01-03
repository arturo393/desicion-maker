import React, { useState } from 'react';
import { DecisionState, Option, Criterion } from './types';
import { InputSection } from './components/InputSection';
import { RefineSection } from './components/RefineSection';
import { ResultsSection } from './components/ResultsSection';
import { analyzeTopicAndSuggest, scoreOptions } from './services/gemini';
import { runMonteCarloSimulation } from './services/math';

const App: React.FC = () => {
  const [state, setState] = useState<DecisionState>({
    topic: '',
    context: '',
    options: [],
    criteria: [],
    evaluations: [],
    simulationResults: [],
    groundingSources: [],
    step: 'input'
  });

  const [error, setError] = useState<string | null>(null);

  // Phase 1: Topic -> Options/Criteria
  const handleAnalyze = async (topic: string, context: string) => {
    setState(prev => ({ ...prev, step: 'processing_search', topic, context }));
    setError(null);
    try {
      const result = await analyzeTopicAndSuggest(topic, context);
      
      // Assign IDs if missing
      const optionsWithIds = result.options.map((o, i) => ({ ...o, id: `opt_${i}` }));
      const criteriaWithIds = result.criteria.map((c, i) => ({ ...c, id: `crit_${i}` }));

      setState(prev => ({
        ...prev,
        step: 'refine',
        options: optionsWithIds,
        criteria: criteriaWithIds,
        groundingSources: result.sources
      }));
    } catch (err: any) {
      console.error(err);
      setError("Unable to analyze the topic. Please try again or check your API Key.");
      setState(prev => ({ ...prev, step: 'input' }));
    }
  };

  // Phase 2: Refined -> Scores -> Simulation
  const handleConfirmRefinement = async (options: Option[], criteria: Criterion[]) => {
    setState(prev => ({ ...prev, step: 'processing_scores', options, criteria }));
    setError(null);
    try {
      const result = await scoreOptions(state.topic, options, criteria);
      
      // Combine new sources with previous sources (deduplicated)
      const allSources = [...state.groundingSources, ...result.sources];
      const uniqueSources = Array.from(new Set(allSources.map(s => s.uri)))
        .map(uri => allSources.find(s => s.uri === uri)!);

      // Run Stochastic Simulation locally
      const simResults = runMonteCarloSimulation(
        options,
        criteria,
        result.evaluations
      );

      setState(prev => ({
        ...prev,
        step: 'results',
        evaluations: result.evaluations,
        groundingSources: uniqueSources,
        simulationResults: simResults
      }));

    } catch (err: any) {
      console.error(err);
      setError("Unable to score options. Please try again.");
      setState(prev => ({ ...prev, step: 'refine' }));
    }
  };

  const handleReset = () => {
    setState({
        topic: '',
        context: '',
        options: [],
        criteria: [],
        evaluations: [],
        simulationResults: [],
        groundingSources: [],
        step: 'input'
    });
    setError(null);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 font-sans selection:bg-blue-500/30">
      
      {/* Background Ambience */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-900/20 rounded-full blur-[100px]"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-emerald-900/10 rounded-full blur-[100px]"></div>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8 md:py-16">
        
        {error && (
            <div className="max-w-md mx-auto mb-8 p-4 bg-red-900/50 border border-red-500/50 text-red-200 rounded-lg text-center">
                {error}
            </div>
        )}

        {state.step === 'input' && (
          <InputSection onAnalyze={handleAnalyze} isAnalyzing={false} />
        )}

        {state.step === 'processing_search' && (
           <InputSection onAnalyze={() => {}} isAnalyzing={true} />
        )}

        {state.step === 'refine' && (
          <RefineSection 
            options={state.options} 
            criteria={state.criteria} 
            onConfirm={handleConfirmRefinement}
            isProcessing={false}
          />
        )}

        {state.step === 'processing_scores' && (
           <RefineSection 
            options={state.options} 
            criteria={state.criteria} 
            onConfirm={() => {}}
            isProcessing={true}
          />
        )}

        {state.step === 'results' && (
          <ResultsSection state={state} onReset={handleReset} />
        )}

      </div>
    </div>
  );
};

export default App;
