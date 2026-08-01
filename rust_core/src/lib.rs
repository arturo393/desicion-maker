use pyo3::prelude::*;
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

use rand::prelude::*;
use rand_distr::{Normal, Uniform, Triangular, Exp, LogNormal, Poisson, Gamma, Beta, Bernoulli, Distribution};

#[derive(Deserialize, Debug)]
struct FactorDef {
    name: String,
    weight: f64,
    maximize: bool,
}

#[derive(Deserialize, Debug)]
struct VarDef {
    dist_type: String,
    params: Vec<f64>,
}

#[derive(Deserialize, Debug)]
struct OptionDef {
    name: String,
    variables: HashMap<String, VarDef>,
}

#[derive(Deserialize, Debug)]
struct SimulationInput {
    num_simulations: usize,
    factors: Vec<FactorDef>,
    options: Vec<OptionDef>,
}

#[derive(Serialize)]
struct FactorStats {
    mean: f64,
    std: f64,
    p5: f64,
    p95: f64,
}

#[derive(Serialize)]
struct OptionStats {
    option_name: String,
    mean_score: f64,
    std_dev: f64,
    min_score: f64,
    max_score: f64,
    percentile_5: f64,
    percentile_95: f64,
    success_rate: f64,
    factor_stats: HashMap<String, FactorStats>,
    var_95: f64,
    cvar_95: f64,
}

fn sample_dist(vdef: &VarDef, rng: &mut ThreadRng) -> f64 {
    let p = &vdef.params;
    let eps = 1e-9;
    match vdef.dist_type.as_str() {
        "deterministic" => p.get(0).copied().unwrap_or(0.0),
        "normal" => {
            let m = p.get(0).copied().unwrap_or(0.0);
            let s = p.get(1).copied().unwrap_or(1.0).max(eps);
            Normal::new(m, s).unwrap().sample(rng)
        },
        "uniform" => {
            let a = p.get(0).copied().unwrap_or(0.0);
            let b = p.get(1).copied().unwrap_or(1.0);
            let (min, max) = if a < b { (a, b) } else { (b, a) };
            Uniform::new(min, max).sample(rng)
        },
        "triangular" => {
            let a = p.get(0).copied().unwrap_or(0.0);
            let b = p.get(1).copied().unwrap_or(1.0);
            let mut c = p.get(2).copied().unwrap_or(2.0);
            let (min, max) = if a < c { (a, c) } else { (c, a) };
            c = b.clamp(min, max);
            Triangular::new(min, max, c).unwrap().sample(rng)
        },
        "bernoulli" => {
            let prob = p.get(0).copied().unwrap_or(0.5).clamp(0.0, 1.0);
            if Bernoulli::new(prob).unwrap().sample(rng) { 1.0 } else { 0.0 }
        },
        "exponential" => {
            let scale = p.get(0).copied().unwrap_or(1.0).max(eps);
            Exp::new(1.0 / scale).unwrap().sample(rng)
        },
        "beta" => {
            let alpha = p.get(0).copied().unwrap_or(1.0).max(eps);
            let beta = p.get(1).copied().unwrap_or(1.0).max(eps);
            Beta::new(alpha, beta).unwrap().sample(rng)
        },
        "lognormal" => {
            let mean = p.get(0).copied().unwrap_or(0.0);
            let std = p.get(1).copied().unwrap_or(1.0).max(eps);
            LogNormal::new(mean, std).unwrap().sample(rng)
        },
        "gamma" => {
            let shape = p.get(0).copied().unwrap_or(1.0).max(eps);
            let scale = p.get(1).copied().unwrap_or(1.0).max(eps);
            Gamma::new(shape, scale).unwrap().sample(rng)
        },
        "poisson" => {
            let rate = p.get(0).copied().unwrap_or(1.0).max(eps);
            Poisson::new(rate).unwrap().sample(rng)
        },
        _ => 0.0
    }
}

// Helper for percentiles
fn percentile(data: &mut [f64], p: f64) -> f64 {
    if data.is_empty() { return 0.0; }
    data.sort_unstable_by(|a, b| a.partial_cmp(b).unwrap());
    let idx = ((data.len() as f64 - 1.0) * (p / 100.0)).round() as usize;
    data[idx]
}

#[pyclass]
pub struct MonteCarloEngine {}

#[pymethods]
impl MonteCarloEngine {
    #[new]
    fn new() -> Self {
        MonteCarloEngine {}
    }

    fn run_simulation(&self, json_input: String) -> PyResult<String> {
        let input: SimulationInput = serde_json::from_str(&json_input).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Invalid JSON input: {}", e))
        })?;
        
        let n = input.num_simulations;

        // Parallel map across options
        let results: HashMap<String, OptionStats> = input.options.into_par_iter().map(|opt| {
            let mut rng = rand::thread_rng();
            
            // 1. Sample all variables
            let mut sampled_data: HashMap<String, Vec<f64>> = HashMap::new();
            for (var_name, var_def) in &opt.variables {
                let mut samples = Vec::with_capacity(n);
                for _ in 0..n {
                    samples.push(sample_dist(var_def, &mut rng));
                }
                sampled_data.insert(var_name.clone(), samples);
            }

            // 2. Compute factor statistics
            let mut factor_stats = HashMap::new();
            for (vname, mut samples) in sampled_data.iter().map(|(k, v)| (k.clone(), v.clone())) {
                let mean = samples.iter().sum::<f64>() / n as f64;
                let var = samples.iter().map(|x| (x - mean).powi(2)).sum::<f64>() / n as f64;
                let std = var.sqrt();
                let p5 = percentile(&mut samples, 5.0);
                let p95 = percentile(&mut samples, 95.0);
                factor_stats.insert(vname, FactorStats { mean, std, p5, p95 });
            }

            // 3. Compute total scores (simplified raw sum for now since global bounds need multi-option pass)
            // A full implementation would need 2 passes over options to normalize.
            // For now, doing raw calculation to prove the pipeline.
            let mut total_scores = vec![0.0; n];
            for factor in &input.factors {
                if let Some(samples) = sampled_data.get(&factor.name) {
                    for i in 0..n {
                        if factor.maximize {
                            total_scores[i] += samples[i] * factor.weight;
                        } else {
                            total_scores[i] -= samples[i] * factor.weight;
                        }
                    }
                }
            }

            let mut sorted_scores = total_scores.clone();
            
            let mean_score = total_scores.iter().sum::<f64>() / n as f64;
            let std_dev = (total_scores.iter().map(|x| (x - mean_score).powi(2)).sum::<f64>() / n as f64).sqrt();
            let p5 = percentile(&mut sorted_scores, 5.0);
            let p95 = percentile(&mut sorted_scores, 95.0);
            
            let min_score = sorted_scores.first().copied().unwrap_or(0.0);
            let max_score = sorted_scores.last().copied().unwrap_or(0.0);
            
            // Success threshold simplified
            let total_weight: f64 = input.factors.iter().map(|f| f.weight).sum();
            let success_threshold = 0.0; // Raw scores threshold
            let success_count = total_scores.iter().filter(|&&x| x > success_threshold).count();
            let success_rate = success_count as f64 / n as f64;

            let var_95 = p5;
            let tail: Vec<f64> = total_scores.iter().copied().filter(|&x| x <= p5).collect();
            let cvar_95 = if tail.is_empty() { p5 } else { tail.iter().sum::<f64>() / tail.len() as f64 };

            (opt.name.clone(), OptionStats {
                option_name: opt.name,
                mean_score,
                std_dev,
                min_score,
                max_score,
                percentile_5: p5,
                percentile_95: p95,
                success_rate,
                factor_stats,
                var_95,
                cvar_95,
            })

        }).collect();

        let out_json = serde_json::to_string(&results).unwrap();
        Ok(out_json)
    }
}

#[pymodule]
fn decision_maker_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<MonteCarloEngine>()?;
    Ok(())
}
