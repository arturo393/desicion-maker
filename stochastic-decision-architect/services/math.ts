import { Criterion, Evaluation, Option, SimulationResult } from '../types';

/**
 * Runs a Monte Carlo simulation to determine the probabilistic winner.
 * We introduce noise (stochasticity) to both the weights and the scores
 * to model uncertainty in the decision process.
 */
export const runMonteCarloSimulation = (
  options: Option[],
  criteria: Criterion[],
  evaluations: Evaluation[],
  iterations: number = 2000
): SimulationResult[] => {
  const wins: Record<string, number> = {};
  const totalScores: Record<string, number[]> = {};

  // Initialize
  options.forEach(opt => {
    wins[opt.id] = 0;
    totalScores[opt.id] = [];
  });

  for (let i = 0; i < iterations; i++) {
    let maxScore = -Infinity;
    let winningOptionId = '';

    // Calculate score for each option in this iteration
    options.forEach(opt => {
      let optionTotalScore = 0;

      criteria.forEach(crit => {
        const evaluation = evaluations.find(e => e.optionId === opt.id && e.criterionId === crit.id);
        const rawScore = evaluation ? evaluation.score : 0;

        // STOCHASTICITY:
        // 1. Perturb the user's weight preference (standard deviation of ~1.5 on a 10 scale)
        // This models that "Importance" is subjective and fluctuates.
        const noisyWeight = Math.max(0, crit.weight + generateGaussian(0, 1.5));

        // 2. Perturb the AI's score (standard deviation of ~5 on a 100 scale)
        // This models data uncertainty.
        const noisyScore = Math.max(0, Math.min(100, rawScore + generateGaussian(0, 5)));

        optionTotalScore += (noisyScore * noisyWeight);
      });

      totalScores[opt.id].push(optionTotalScore);

      if (optionTotalScore > maxScore) {
        maxScore = optionTotalScore;
        winningOptionId = opt.id;
      }
    });

    if (winningOptionId) {
      wins[winningOptionId]++;
    }
  }

  // Aggregate results
  return options.map(opt => {
    const scores = totalScores[opt.id].sort((a, b) => a - b);
    const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
    
    // 95% Confidence Interval
    const lowerIdx = Math.floor(iterations * 0.025);
    const upperIdx = Math.floor(iterations * 0.975);

    return {
      optionId: opt.id,
      winProbability: wins[opt.id] / iterations,
      averageScore: avgScore,
      confidenceInterval: [scores[lowerIdx], scores[upperIdx]]
    };
  });
};

// Box-Muller transform for normal distribution
function generateGaussian(mean: number, stdDev: number): number {
  const u1 = Math.random();
  const u2 = Math.random();
  const z = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
  return z * stdDev + mean;
}
