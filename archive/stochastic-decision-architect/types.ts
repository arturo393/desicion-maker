export interface Option {
  id: string;
  name: string;
  description: string;
}

export interface Criterion {
  id: string;
  name: string;
  description: string;
  weight: number; // 1-10 importance
}

export interface Evaluation {
  optionId: string;
  criterionId: string;
  score: number; // 0-100 raw score
  reasoning: string; // AI generated reasoning
}

export interface SimulationResult {
  optionId: string;
  winProbability: number; // 0-1
  averageScore: number;
  confidenceInterval: [number, number]; // 95% CI
}

export interface GroundingSource {
  uri: string;
  title: string;
}

export interface DecisionState {
  topic: string;
  context: string; // Additional user context
  options: Option[];
  criteria: Criterion[];
  evaluations: Evaluation[];
  simulationResults: SimulationResult[];
  groundingSources: GroundingSource[];
  step: 'input' | 'processing_search' | 'refine' | 'processing_scores' | 'results';
}
