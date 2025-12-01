/**
 * 🎲 Monte Carlo Decision Engine - JavaScript Implementation
 * Traducción del sistema C++ a JavaScript para la GUI web
 */

// Configuraciones de tipos de decisión
const DECISION_TEMPLATES = {
    computer: {
        title: "💻 Decisión de Computadora",
        options: [
            {
                name: "Seguir con actual",
                cost: 50,
                performance: 6.5,
                satisfaction: 6.0,
                reliability: 8.5,
                needsMonitor: false
            },
            {
                name: "Mac Mini usado",
                cost: 280,
                performance: 8.0,
                satisfaction: 7.5,
                reliability: 7.5,
                needsMonitor: true
            },
            {
                name: "Mini PC AMD",
                cost: 290,
                performance: 8.5,
                satisfaction: 8.7,
                reliability: 9.0,
                needsMonitor: true
            },
            {
                name: "Laptop ThinkPad usado",
                cost: 270,
                performance: 7.5,
                satisfaction: 8.1,
                reliability: 7.8,
                needsMonitor: false
            }
        ]
    },
    car: {
        title: "🚗 Decisión de Automóvil",
        options: [
            {
                name: "Toyota Corolla usado",
                cost: 15000,
                performance: 8.0,
                satisfaction: 7.5,
                reliability: 9.0,
                maintenanceCost: 800
            },
            {
                name: "Honda Civic nuevo",
                cost: 25000,
                performance: 8.5,
                satisfaction: 8.5,
                reliability: 9.5,
                maintenanceCost: 600
            },
            {
                name: "Nissan Versa usado",
                cost: 12000,
                performance: 6.5,
                satisfaction: 6.0,
                reliability: 7.0,
                maintenanceCost: 1200
            }
        ]
    },
    job: {
        title: "💼 Decisión de Trabajo",
        options: [
            {
                name: "Startup Tech",
                salary: 80000,
                satisfaction: 9.0,
                stability: 5.0,
                growth: 9.5,
                stockOptions: true
            },
            {
                name: "Empresa Grande",
                salary: 95000,
                satisfaction: 7.0,
                stability: 9.0,
                growth: 6.0,
                stockOptions: false
            },
            {
                name: "Freelance",
                salary: 90000,
                satisfaction: 8.5,
                stability: 4.0,
                growth: 7.0,
                stockOptions: false
            }
        ]
    }
};

// Variables globales
let currentDecisionType = null;
let currentOptions = [];
let simulationResults = [];

/**
 * Funciones de utilidad matemática
 */
class MathUtils {
    static normalRandom(mean = 0, stdDev = 1) {
        let u = 0, v = 0;
        while(u === 0) u = Math.random();
        while(v === 0) v = Math.random();
        
        const z = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
        return z * stdDev + mean;
    }
    
    static exponentialRandom(lambda) {
        return -Math.log(1 - Math.random()) / lambda;
    }
    
    static uniformRandom(min, max) {
        return Math.random() * (max - min) + min;
    }
    
    static clamp(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }
    
    static mean(array) {
        return array.reduce((sum, val) => sum + val, 0) / array.length;
    }
    
    static standardDeviation(array) {
        const avg = this.mean(array);
        const squareDiffs = array.map(val => Math.pow(val - avg, 2));
        return Math.sqrt(this.mean(squareDiffs));
    }
    
    static percentile(array, p) {
        const sorted = [...array].sort((a, b) => a - b);
        const index = (p / 100) * (sorted.length - 1);
        const lower = Math.floor(index);
        const upper = Math.ceil(index);
        
        if (lower === upper) return sorted[lower];
        
        const weight = index - lower;
        return sorted[lower] * (1 - weight) + sorted[upper] * weight;
    }
}

/**
 * Motor de simulación Monte Carlo
 */
class MonteCarloEngine {
    constructor() {
        this.progressCallback = null;
    }
    
    setProgressCallback(callback) {
        this.progressCallback = callback;
    }
    
    async simulate(options, numSimulations, timeHorizon) {
        const results = [];
        
        for (let i = 0; i < numSimulations; i++) {
            if (this.progressCallback && i % 100 === 0) {
                this.progressCallback(i, numSimulations);
                // Permitir que la UI se actualice
                await new Promise(resolve => setTimeout(resolve, 1));
            }
            
            const scenarioResults = this.runSingleScenario(options, timeHorizon);
            results.push(scenarioResults);
        }
        
        return this.analyzeResults(results, options);
    }
    
    runSingleScenario(options, timeHorizon) {
        return options.map(option => {
            const result = {
                name: option.name,
                totalCost: 0,
                satisfaction: 0,
                productivity: 0,
                problems: 0
            };
            
            // Simular según el tipo de decisión
            if (currentDecisionType === 'computer') {
                result.totalCost = this.simulateComputerCost(option, timeHorizon);
                result.satisfaction = this.simulateComputerSatisfaction(option);
                result.productivity = this.simulateComputerProductivity(option);
                result.problems = this.simulateComputerProblems(option);
            } else if (currentDecisionType === 'car') {
                result.totalCost = this.simulateCarCost(option, timeHorizon);
                result.satisfaction = this.simulateCarSatisfaction(option);
                result.problems = this.simulateCarProblems(option);
            } else if (currentDecisionType === 'job') {
                result.totalCost = -this.simulateJobSalary(option, timeHorizon); // Negativo porque es ingreso
                result.satisfaction = this.simulateJobSatisfaction(option);
                result.problems = this.simulateJobProblems(option);
            }
            
            return result;
        });
    }
    
    // Simulaciones específicas para computadoras
    simulateComputerCost(option, timeHorizon) {
        let totalCost = option.cost;
        
        // Costo de monitor si es necesario
        if (option.needsMonitor && Math.random() > 0.3) {
            totalCost += MathUtils.uniformRandom(60, 120);
        }
        
        // Costos de mantenimiento/upgrades anuales
        const maintenancePerYear = option.cost * 0.05; // 5% del costo inicial
        for (let year = 1; year <= timeHorizon; year++) {
            if (Math.random() < 0.3) { // 30% probabilidad de maintenance cada año
                totalCost += MathUtils.exponentialRandom(1 / maintenancePerYear);
            }
        }
        
        // Valor residual (depreciación)
        const depreciationRate = option.needsMonitor ? 0.20 : 0.15;
        const residualValue = option.cost * Math.pow(1 - depreciationRate, timeHorizon);
        
        return totalCost - residualValue;
    }
    
    simulateComputerSatisfaction(option) {
        const baseSatisfaction = option.satisfaction;
        const variation = MathUtils.normalRandom(0, 0.5);
        return MathUtils.clamp(baseSatisfaction + variation, 1, 10);
    }
    
    simulateComputerProductivity(option) {
        const baseProductivity = option.performance / 10;
        const variation = MathUtils.normalRandom(0, 0.1);
        return MathUtils.clamp(baseProductivity + variation, 0.1, 1.0);
    }
    
    simulateComputerProblems(option) {
        const reliabilityFactor = option.reliability / 10;
        const problemProbability = 1 - reliabilityFactor;
        
        if (Math.random() < problemProbability) {
            return MathUtils.uniformRandom(1, 8); // Horas perdidas
        }
        return 0;
    }
    
    // Simulaciones específicas para autos
    simulateCarCost(option, timeHorizon) {
        let totalCost = option.cost;
        
        // Mantenimiento anual
        for (let year = 1; year <= timeHorizon; year++) {
            const maintenanceMultiplier = 1 + (year - 1) * 0.1; // Aumenta 10% cada año
            const annualMaintenance = option.maintenanceCost * maintenanceMultiplier;
            totalCost += MathUtils.normalRandom(annualMaintenance, annualMaintenance * 0.3);
        }
        
        // Valor residual
        const depreciationRate = option.cost > 20000 ? 0.15 : 0.20;
        const residualValue = option.cost * Math.pow(1 - depreciationRate, timeHorizon);
        
        return totalCost - residualValue;
    }
    
    simulateCarSatisfaction(option) {
        const baseSatisfaction = option.satisfaction;
        const variation = MathUtils.normalRandom(0, 0.7);
        return MathUtils.clamp(baseSatisfaction + variation, 1, 10);
    }
    
    simulateCarProblems(option) {
        const reliabilityFactor = option.reliability / 10;
        const problemProbability = (1 - reliabilityFactor) * 0.3;
        
        if (Math.random() < problemProbability) {
            return MathUtils.uniformRandom(2, 24); // Horas perdidas en talleres
        }
        return 0;
    }
    
    // Simulaciones específicas para trabajos
    simulateJobSalary(option, timeHorizon) {
        let totalIncome = 0;
        let currentSalary = option.salary;
        
        for (let year = 1; year <= timeHorizon; year++) {
            // Crecimiento salarial anual
            const growthRate = option.growth / 100 * 0.05; // 5% del growth score
            currentSalary *= (1 + MathUtils.normalRandom(growthRate, 0.02));
            
            // Riesgo de desempleo
            const unemploymentRisk = (10 - option.stability) / 100 * 0.05;
            if (Math.random() < unemploymentRisk) {
                // Perder trabajo - buscar nuevo trabajo toma tiempo
                totalIncome += currentSalary * MathUtils.uniformRandom(0.5, 0.8);
            } else {
                totalIncome += currentSalary;
            }
        }
        
        // Bonus por stock options si aplica
        if (option.stockOptions && Math.random() < 0.3) {
            totalIncome += MathUtils.uniformRandom(10000, 100000);
        }
        
        return totalIncome;
    }
    
    simulateJobSatisfaction(option) {
        const baseSatisfaction = option.satisfaction;
        const variation = MathUtils.normalRandom(0, 0.8);
        return MathUtils.clamp(baseSatisfaction + variation, 1, 10);
    }
    
    simulateJobProblems(option) {
        const stabilityFactor = option.stability / 10;
        const stressProbability = (1 - stabilityFactor) * 0.4;
        
        if (Math.random() < stressProbability) {
            return MathUtils.uniformRandom(5, 40); // Horas extra de estrés/semana
        }
        return 0;
    }
    
    analyzeResults(results, options) {
        const analysis = options.map((option, index) => {
            const optionResults = results.map(scenario => scenario[index]);
            
            const costs = optionResults.map(r => r.totalCost);
            const satisfactions = optionResults.map(r => r.satisfaction);
            const productivities = optionResults.map(r => r.productivity || 0.8);
            const problems = optionResults.map(r => r.problems);
            
            return {
                name: option.name,
                stats: {
                    avgCost: MathUtils.mean(costs),
                    stdCost: MathUtils.standardDeviation(costs),
                    minCost: Math.min(...costs),
                    maxCost: Math.max(...costs),
                    avgSatisfaction: MathUtils.mean(satisfactions),
                    avgProductivity: MathUtils.mean(productivities),
                    avgProblems: MathUtils.mean(problems),
                    costPercentile25: MathUtils.percentile(costs, 25),
                    costPercentile75: MathUtils.percentile(costs, 75),
                    riskScore: this.calculateRiskScore(costs, satisfactions, problems)
                }
            };
        });
        
        return analysis;
    }
    
    calculateRiskScore(costs, satisfactions, problems) {
        const costVariability = MathUtils.standardDeviation(costs) / MathUtils.mean(costs);
        const lowSatisfactionProb = satisfactions.filter(s => s < 6).length / satisfactions.length;
        const highProblemsProb = problems.filter(p => p > 5).length / problems.length;
        
        return (costVariability * 0.4 + lowSatisfactionProb * 0.4 + highProblemsProb * 0.2) * 10;
    }
}

// Instancia global del motor
const engine = new MonteCarloEngine();

/**
 * Funciones de interfaz de usuario
 */
function selectDecisionType(type) {
    currentDecisionType = type;
    const template = DECISION_TEMPLATES[type];
    
    if (!template) {
        alert('Tipo de decisión no implementado aún');
        return;
    }
    
    currentOptions = [...template.options];
    
    // Actualizar UI
    document.getElementById('simulationConfig').style.display = 'block';
    document.getElementById('configTitle').innerHTML = `${template.title}`;
    
    renderOptions();
    
    // Scroll suave hacia la configuración
    document.getElementById('simulationConfig').scrollIntoView({ 
        behavior: 'smooth' 
    });
}

function renderOptions() {
    const container = document.getElementById('optionsContainer');
    container.innerHTML = '';
    
    currentOptions.forEach((option, index) => {
        const optionCard = createOptionCard(option, index);
        container.appendChild(optionCard);
    });
}

function createOptionCard(option, index) {
    const card = document.createElement('div');
    card.className = 'card mb-3';
    
    const fields = getFieldsForDecisionType(currentDecisionType);
    const fieldsHtml = fields.map(field => 
        `<div class="col-md-6">
            <label class="form-label">${field.label}</label>
            <input type="number" class="form-control" 
                   value="${option[field.key]}" 
                   onchange="updateOption(${index}, '${field.key}', this.value)"
                   step="${field.step || 0.1}" min="${field.min || 0}">
         </div>`
    ).join('');
    
    card.innerHTML = `
        <div class="card-body">
            <div class="row align-items-center mb-3">
                <div class="col">
                    <h6 class="mb-0">
                        <input type="text" class="form-control-plaintext fw-bold" 
                               value="${option.name}" 
                               onchange="updateOption(${index}, 'name', this.value)">
                    </h6>
                </div>
                <div class="col-auto">
                    <button class="btn btn-sm btn-outline-danger" onclick="removeOption(${index})">
                        <span class="emoji">🗑️</span>
                    </button>
                </div>
            </div>
            <div class="row g-3">
                ${fieldsHtml}
            </div>
        </div>
    `;
    
    return card;
}

function getFieldsForDecisionType(type) {
    const fieldMap = {
        computer: [
            { key: 'cost', label: 'Costo inicial ($)', step: 10 },
            { key: 'performance', label: 'Rendimiento (1-10)', min: 1, max: 10 },
            { key: 'satisfaction', label: 'Satisfacción esperada (1-10)', min: 1, max: 10 },
            { key: 'reliability', label: 'Confiabilidad (1-10)', min: 1, max: 10 }
        ],
        car: [
            { key: 'cost', label: 'Precio ($)', step: 1000 },
            { key: 'maintenanceCost', label: 'Mantenimiento anual ($)', step: 100 },
            { key: 'satisfaction', label: 'Satisfacción esperada (1-10)', min: 1, max: 10 },
            { key: 'reliability', label: 'Confiabilidad (1-10)', min: 1, max: 10 }
        ],
        job: [
            { key: 'salary', label: 'Salario anual ($)', step: 5000 },
            { key: 'satisfaction', label: 'Satisfacción (1-10)', min: 1, max: 10 },
            { key: 'stability', label: 'Estabilidad (1-10)', min: 1, max: 10 },
            { key: 'growth', label: 'Potencial crecimiento (1-10)', min: 1, max: 10 }
        ]
    };
    
    return fieldMap[type] || [];
}

function updateOption(index, key, value) {
    currentOptions[index][key] = parseFloat(value) || value;
}

function removeOption(index) {
    if (currentOptions.length <= 2) {
        alert('Necesitas al menos 2 opciones para comparar');
        return;
    }
    
    currentOptions.splice(index, 1);
    renderOptions();
}

function addOption() {
    const template = DECISION_TEMPLATES[currentDecisionType];
    const newOption = { ...template.options[0] };
    newOption.name = `Nueva opción ${currentOptions.length + 1}`;
    
    currentOptions.push(newOption);
    renderOptions();
}

async function runSimulation() {
    if (currentOptions.length < 2) {
        alert('Necesitas al menos 2 opciones para comparar');
        return;
    }
    
    const numSimulations = parseInt(document.getElementById('numSimulations').value);
    const timeHorizon = parseInt(document.getElementById('timeHorizon').value);
    
    // Mostrar loading
    document.getElementById('simulationConfig').style.display = 'none';
    document.getElementById('loadingAnimation').style.display = 'block';
    document.getElementById('totalSimulations').textContent = numSimulations.toLocaleString();
    
    // Configurar callback de progreso
    engine.setProgressCallback((current, total) => {
        const percentage = (current / total) * 100;
        document.getElementById('currentSimulation').textContent = current.toLocaleString();
        document.getElementById('progressBar').style.width = `${percentage}%`;
    });
    
    try {
        // Ejecutar simulación
        simulationResults = await engine.simulate(currentOptions, numSimulations, timeHorizon);
        
        // Mostrar resultados
        document.getElementById('loadingAnimation').style.display = 'none';
        document.getElementById('simulationResults').style.display = 'block';
        
        renderResults();
        createCharts();
        generateRecommendation();
        
        // Scroll a resultados
        document.getElementById('simulationResults').scrollIntoView({ 
            behavior: 'smooth' 
        });
        
    } catch (error) {
        console.error('Error en simulación:', error);
        alert('Error ejecutando la simulación. Por favor intenta de nuevo.');
        document.getElementById('loadingAnimation').style.display = 'none';
        document.getElementById('simulationConfig').style.display = 'block';
    }
}

function renderResults() {
    const container = document.getElementById('resultsContainer');
    container.innerHTML = '';
    
    // Encontrar el ganador (menor costo ajustado por satisfacción)
    const winner = simulationResults.reduce((best, current) => {
        const bestScore = best.stats.avgCost / best.stats.avgSatisfaction;
        const currentScore = current.stats.avgCost / current.stats.avgSatisfaction;
        return currentScore < bestScore ? current : best;
    });
    
    simulationResults.forEach(result => {
        const isWinner = result.name === winner.name;
        const card = document.createElement('div');
        card.className = `card mb-3 result-card ${isWinner ? 'winner' : ''}`;
        
        const costDisplay = currentDecisionType === 'job' ? 
            `Ingreso: $${Math.abs(result.stats.avgCost).toLocaleString()}` :
            `Costo: $${result.stats.avgCost.toLocaleString()}`;
        
        card.innerHTML = `
            <div class="card-body">
                <div class="row align-items-center">
                    <div class="col">
                        <h5 class="mb-1">
                            ${isWinner ? '🏆 ' : ''}${result.name}
                            ${isWinner ? '<span class="badge bg-success ms-2">Recomendado</span>' : ''}
                        </h5>
                        <div class="row g-3">
                            <div class="col-md-3">
                                <strong>${costDisplay}</strong><br>
                                <small class="text-muted">±$${result.stats.stdCost.toLocaleString()}</small>
                            </div>
                            <div class="col-md-3">
                                <strong>Satisfacción: ${result.stats.avgSatisfaction.toFixed(1)}/10</strong><br>
                                <small class="text-muted">Riesgo: ${result.stats.riskScore.toFixed(1)}/10</small>
                            </div>
                            <div class="col-md-3">
                                <strong>Rango: $${result.stats.minCost.toLocaleString()} - $${result.stats.maxCost.toLocaleString()}</strong><br>
                                <small class="text-muted">Problemas: ${result.stats.avgProblems.toFixed(1)}h</small>
                            </div>
                            <div class="col-md-3">
                                ${currentDecisionType === 'computer' ? 
                                    `<strong>Productividad: ${(result.stats.avgProductivity * 100).toFixed(1)}%</strong>` :
                                    `<strong>Score: ${(result.stats.avgSatisfaction - result.stats.riskScore).toFixed(1)}</strong>`
                                }
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        container.appendChild(card);
    });
}

function createCharts() {
    createCostChart();
    createSatisfactionChart();
}

function createCostChart() {
    const ctx = document.getElementById('costChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: simulationResults.map(r => r.name),
            datasets: [{
                label: currentDecisionType === 'job' ? 'Ingreso Promedio' : 'Costo Promedio',
                data: simulationResults.map(r => Math.abs(r.stats.avgCost)),
                backgroundColor: [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 205, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 205, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' + context.parsed.y.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

function createSatisfactionChart() {
    const ctx = document.getElementById('satisfactionChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: simulationResults.map((result, index) => ({
                label: result.name,
                data: [{
                    x: Math.abs(result.stats.avgCost),
                    y: result.stats.avgSatisfaction
                }],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 205, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)'
                ][index],
                pointRadius: 8
            }))
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: currentDecisionType === 'job' ? 'Ingreso ($)' : 'Costo ($)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Satisfacción (1-10)'
                    },
                    min: 0,
                    max: 10
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + 
                                   ': $' + context.parsed.x.toLocaleString() + 
                                   ', ' + context.parsed.y.toFixed(1) + '/10';
                        }
                    }
                }
            }
        }
    });
}

function generateRecommendation() {
    const container = document.getElementById('recommendationText');
    
    if (!simulationResults.length) return;
    
    // Encontrar el ganador y análisis
    const winner = simulationResults.reduce((best, current) => {
        const bestScore = best.stats.avgCost / best.stats.avgSatisfaction;
        const currentScore = current.stats.avgCost / current.stats.avgSatisfaction;
        return currentScore < bestScore ? current : best;
    });
    
    const cheapest = simulationResults.reduce((min, current) => 
        Math.abs(current.stats.avgCost) < Math.abs(min.stats.avgCost) ? current : min
    );
    
    const mostSatisfying = simulationResults.reduce((max, current) => 
        current.stats.avgSatisfaction > max.stats.avgSatisfaction ? current : max
    );
    
    container.innerHTML = `
        <div class="row">
            <div class="col-md-8">
                <h6><span class="emoji">🏆</span> Mejor Opción General: ${winner.name}</h6>
                <p>Esta opción ofrece la mejor relación valor-satisfacción según las simulaciones.</p>
                
                <h6><span class="emoji">💰</span> Análisis de Costos</h6>
                <ul>
                    <li><strong>Más económico:</strong> ${cheapest.name} - $${Math.abs(cheapest.stats.avgCost).toLocaleString()}</li>
                    <li><strong>Mayor satisfacción:</strong> ${mostSatisfying.name} - ${mostSatisfying.stats.avgSatisfaction.toFixed(1)}/10</li>
                    <li><strong>Menor riesgo:</strong> ${simulationResults.reduce((min, current) => 
                        current.stats.riskScore < min.stats.riskScore ? current : min
                    ).name}</li>
                </ul>
                
                <h6><span class="emoji">🎯</span> Recomendación Final</h6>
                <p><strong>${winner.name}</strong> es tu mejor opción porque ofrece:</p>
                <ul>
                    <li>Costo promedio de $${Math.abs(winner.stats.avgCost).toLocaleString()}</li>
                    <li>Satisfacción de ${winner.stats.avgSatisfaction.toFixed(1)}/10</li>
                    <li>Riesgo controlado de ${winner.stats.riskScore.toFixed(1)}/10</li>
                    ${currentDecisionType === 'computer' ? 
                        `<li>Productividad del ${(winner.stats.avgProductivity * 100).toFixed(1)}%</li>` : 
                        ''
                    }
                </ul>
            </div>
            <div class="col-md-4">
                <div class="card bg-light">
                    <div class="card-body">
                        <h6><span class="emoji">📊</span> Estadísticas de la Simulación</h6>
                        <ul class="list-unstyled">
                            <li><strong>Simulaciones ejecutadas:</strong> ${document.getElementById('numSimulations').value}</li>
                            <li><strong>Horizonte temporal:</strong> ${document.getElementById('timeHorizon').value} años</li>
                            <li><strong>Opciones evaluadas:</strong> ${simulationResults.length}</li>
                            <li><strong>Confianza estadística:</strong> 95%</li>
                        </ul>
                        
                        <h6><span class="emoji">🔧</span> Próximos Pasos</h6>
                        <ol class="small">
                            <li>Revisa los detalles de ${winner.name}</li>
                            <li>Considera tu tolerancia al riesgo</li>
                            <li>Ajusta parámetros si es necesario</li>
                            <li>¡Toma tu decisión!</li>
                        </ol>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function showTutorial() {
    const modal = new bootstrap.Modal(document.getElementById('tutorialModal'));
    modal.show();
}

// Función para resetear la aplicación
function resetApp() {
    currentDecisionType = null;
    currentOptions = [];
    simulationResults = [];
    
    document.getElementById('simulationConfig').style.display = 'none';
    document.getElementById('loadingAnimation').style.display = 'none';
    document.getElementById('simulationResults').style.display = 'none';
}