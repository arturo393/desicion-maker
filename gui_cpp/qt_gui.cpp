#include <QtWidgets/QApplication>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QGridLayout>
#include <QtWidgets/QWidget>
#include <QtWidgets/QLabel>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QSpinBox>
#include <QtWidgets/QDoubleSpinBox>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QProgressBar>
#include <QtWidgets/QTextEdit>
#include <QtWidgets/QTabWidget>
#include <QtWidgets/QGroupBox>
#include <QtWidgets/QTableWidget>
#include <QtWidgets/QTableWidgetItem>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QMessageBox>
#include <QtCharts/QChartView>
#include <QtCharts/QBarSeries>
#include <QtCharts/QBarSet>
#include <QtCharts/QBarCategoryAxis>
#include <QtCharts/QValueAxis>
#include <QtCharts/QScatterSeries>
#include <QTimer>
#include <QThread>
#include <QMutex>
#include <vector>
#include <random>
#include <memory>

/**
 * 🎯 GUI NATIVA EN C++ CON QT
 * Simulador Monte Carlo profesional con interfaz gráfica nativa
 * 
 * VENTAJAS:
 * - Performance máxima (100% C++ nativo)
 * - Integración perfecta con el sistema operativo
 * - Aspecto nativo en macOS/Windows/Linux
 * - Control total sobre la UI y lógica
 * 
 * DESVENTAJAS:
 * - Requiere instalar Qt (brew install qt)
 * - Desarrollo más complejo
 * - Compilación específica por plataforma
 */

using namespace QtCharts;

// Estructura para una opción de decisión
struct DecisionOption {
    QString name;
    double cost;
    double satisfaction;
    double reliability;
    double performance;
    bool enabled;
    
    DecisionOption(const QString& n = "Nueva Opción", double c = 100.0, 
                   double s = 7.0, double r = 8.0, double p = 7.5)
        : name(n), cost(c), satisfaction(s), reliability(r), performance(p), enabled(true) {}
};

// Resultados de simulación
struct SimulationResults {
    QString optionName;
    double avgCost;
    double stdCost;
    double minCost;
    double maxCost;
    double avgSatisfaction;
    double avgProblems;
    double valueScore;
    int rank;
};

// Worker thread para simulaciones
class SimulationWorker : public QObject {
    Q_OBJECT

public:
    SimulationWorker(const std::vector<DecisionOption>& options, 
                     int numSimulations, int timeHorizon)
        : options_(options), numSimulations_(numSimulations), 
          timeHorizon_(timeHorizon), shouldStop_(false) {}

public slots:
    void runSimulation() {
        std::random_device rd;
        std::mt19937 gen(rd());
        
        std::vector<SimulationResults> results;
        results.resize(options_.size());
        
        // Inicializar resultados
        for (size_t i = 0; i < options_.size(); ++i) {
            results[i].optionName = options_[i].name;
            results[i].avgCost = 0;
            results[i].avgSatisfaction = 0;
            results[i].avgProblems = 0;
        }
        
        std::vector<std::vector<double>> allCosts(options_.size());
        std::vector<std::vector<double>> allSatisfactions(options_.size());
        std::vector<std::vector<double>> allProblems(options_.size());
        
        // Ejecutar simulaciones
        for (int sim = 0; sim < numSimulations_ && !shouldStop_; ++sim) {
            // Actualizar progreso cada 100 simulaciones
            if (sim % 100 == 0) {
                int progress = (sim * 100) / numSimulations_;
                emit progressUpdated(progress, sim, numSimulations_);
            }
            
            // Simular cada opción
            for (size_t i = 0; i < options_.size(); ++i) {
                if (!options_[i].enabled) continue;
                
                auto result = simulateSingleOption(options_[i], gen);
                allCosts[i].push_back(result.totalCost);
                allSatisfactions[i].push_back(result.satisfaction);
                allProblems[i].push_back(result.problems);
            }
        }
        
        if (shouldStop_) {
            emit simulationCancelled();
            return;
        }
        
        // Calcular estadísticas finales
        for (size_t i = 0; i < options_.size(); ++i) {
            if (!options_[i].enabled || allCosts[i].empty()) continue;
            
            results[i].avgCost = calculateMean(allCosts[i]);
            results[i].stdCost = calculateStdDev(allCosts[i]);
            results[i].minCost = *std::min_element(allCosts[i].begin(), allCosts[i].end());
            results[i].maxCost = *std::max_element(allCosts[i].begin(), allCosts[i].end());
            results[i].avgSatisfaction = calculateMean(allSatisfactions[i]);
            results[i].avgProblems = calculateMean(allProblems[i]);
            results[i].valueScore = results[i].avgSatisfaction / (results[i].avgCost / 100.0);
        }
        
        // Rankear opciones por value score
        std::sort(results.begin(), results.end(), 
                  [](const SimulationResults& a, const SimulationResults& b) {
                      return a.valueScore > b.valueScore;
                  });
        
        for (size_t i = 0; i < results.size(); ++i) {
            results[i].rank = i + 1;
        }
        
        emit simulationCompleted(results);
    }
    
    void stopSimulation() {
        shouldStop_ = true;
    }

signals:
    void progressUpdated(int percentage, int current, int total);
    void simulationCompleted(const std::vector<SimulationResults>& results);
    void simulationCancelled();

private:
    struct SingleSimResult {
        double totalCost;
        double satisfaction;
        double problems;
    };
    
    SingleSimResult simulateSingleOption(const DecisionOption& option, std::mt19937& gen) {
        std::normal_distribution<double> normal(0.0, 1.0);
        std::uniform_real_distribution<double> uniform(0.0, 1.0);
        
        SingleSimResult result;
        
        // Simular costo total
        double totalCost = option.cost;
        
        // Mantenimiento anual basado en confiabilidad
        double maintenanceRate = (10.0 - option.reliability) / 10.0 * 0.15;
        for (int year = 1; year <= timeHorizon_; ++year) {
            if (uniform(gen) < maintenanceRate) {
                std::normal_distribution<double> maintenanceCost(option.cost * 0.05, option.cost * 0.02);
                totalCost += std::max(0.0, maintenanceCost(gen));
            }
        }
        
        // Depreciación
        double depreciationRate = 0.15 + uniform(gen) * 0.1; // 15-25%
        double residualValue = option.cost * std::pow(1.0 - depreciationRate, timeHorizon_);
        totalCost -= residualValue;
        
        result.totalCost = std::max(0.0, totalCost);
        
        // Simular satisfacción
        std::normal_distribution<double> satisfactionDist(option.satisfaction, 0.5);
        result.satisfaction = std::max(1.0, std::min(10.0, satisfactionDist(gen)));
        
        // Simular problemas
        double problemProbability = (10.0 - option.reliability) / 10.0 * 0.3;
        if (uniform(gen) < problemProbability) {
            result.problems = uniform(gen) * 20.0; // 0-20 horas
        } else {
            result.problems = 0.0;
        }
        
        return result;
    }
    
    double calculateMean(const std::vector<double>& values) {
        if (values.empty()) return 0.0;
        double sum = 0.0;
        for (double val : values) sum += val;
        return sum / values.size();
    }
    
    double calculateStdDev(const std::vector<double>& values) {
        if (values.size() < 2) return 0.0;
        double mean = calculateMean(values);
        double variance = 0.0;
        for (double val : values) {
            variance += (val - mean) * (val - mean);
        }
        return std::sqrt(variance / (values.size() - 1));
    }
    
    std::vector<DecisionOption> options_;
    int numSimulations_;
    int timeHorizon_;
    bool shouldStop_;
};

// Ventana principal
class DecisionMakerWindow : public QMainWindow {
    Q_OBJECT

public:
    DecisionMakerWindow(QWidget *parent = nullptr) : QMainWindow(parent) {
        setupUI();
        setupConnections();
        loadDefaultOptions();
    }

private slots:
    void addNewOption() {
        DecisionOption newOption(QString("Opción %1").arg(options_.size() + 1));
        options_.push_back(newOption);
        updateOptionsTable();
    }
    
    void removeSelectedOption() {
        int currentRow = optionsTable_->currentRow();
        if (currentRow >= 0 && currentRow < static_cast<int>(options_.size())) {
            options_.erase(options_.begin() + currentRow);
            updateOptionsTable();
        }
    }
    
    void runSimulation() {
        if (options_.size() < 2) {
            QMessageBox::warning(this, "Error", "Necesitas al menos 2 opciones para comparar.");
            return;
        }
        
        // Configurar simulación
        int numSims = simulationsSpinBox_->value();
        int timeHorizon = timeHorizonSpinBox_->value();
        
        // Actualizar opciones desde la tabla
        updateOptionsFromTable();
        
        // Crear worker thread
        simulationWorker_ = std::make_unique<SimulationWorker>(options_, numSims, timeHorizon);
        workerThread_ = std::make_unique<QThread>();
        
        simulationWorker_->moveToThread(workerThread_.get());
        
        connect(workerThread_.get(), &QThread::started, 
                simulationWorker_.get(), &SimulationWorker::runSimulation);
        connect(simulationWorker_.get(), &SimulationWorker::progressUpdated,
                this, &DecisionMakerWindow::updateProgress);
        connect(simulationWorker_.get(), &SimulationWorker::simulationCompleted,
                this, &DecisionMakerWindow::showResults);
        connect(simulationWorker_.get(), &SimulationWorker::simulationCancelled,
                this, &DecisionMakerWindow::simulationCancelled);
        
        // UI changes
        runButton_->setEnabled(false);
        stopButton_->setEnabled(true);
        progressBar_->setVisible(true);
        progressLabel_->setVisible(true);
        progressBar_->setValue(0);
        
        workerThread_->start();
    }
    
    void stopSimulation() {
        if (simulationWorker_) {
            simulationWorker_->stopSimulation();
        }
    }
    
    void updateProgress(int percentage, int current, int total) {
        progressBar_->setValue(percentage);
        progressLabel_->setText(QString("Simulación %1 de %2").arg(current).arg(total));
    }
    
    void showResults(const std::vector<SimulationResults>& results) {
        // Cleanup thread
        workerThread_->quit();
        workerThread_->wait();
        workerThread_.reset();
        simulationWorker_.reset();
        
        // UI changes
        runButton_->setEnabled(true);
        stopButton_->setEnabled(false);
        progressBar_->setVisible(false);
        progressLabel_->setVisible(false);
        
        // Show results
        updateResultsTable(results);
        createCharts(results);
        generateRecommendation(results);
        
        // Switch to results tab
        tabWidget_->setCurrentIndex(1);
    }
    
    void simulationCancelled() {
        // Cleanup thread
        workerThread_->quit();
        workerThread_->wait();
        workerThread_.reset();
        simulationWorker_.reset();
        
        // UI changes
        runButton_->setEnabled(true);
        stopButton_->setEnabled(false);
        progressBar_->setVisible(false);
        progressLabel_->setVisible(false);
        
        progressLabel_->setText("Simulación cancelada");
    }

private:
    void setupUI() {
        setWindowTitle("🎲 Decision Maker - Monte Carlo Simulator");
        setMinimumSize(1000, 700);
        
        auto centralWidget = new QWidget(this);
        setCentralWidget(centralWidget);
        
        // Layout principal
        auto mainLayout = new QVBoxLayout(centralWidget);
        
        // Header
        auto headerLabel = new QLabel("🎲 Decision Maker - Simulador Monte Carlo");
        headerLabel->setStyleSheet("QLabel { font-size: 18px; font-weight: bold; "
                                  "color: #2c3e50; padding: 10px; }");
        headerLabel->setAlignment(Qt::AlignCenter);
        mainLayout->addWidget(headerLabel);
        
        // Tab widget
        tabWidget_ = new QTabWidget();
        mainLayout->addWidget(tabWidget_);
        
        setupConfigTab();
        setupResultsTab();
    }
    
    void setupConfigTab() {
        auto configWidget = new QWidget();
        tabWidget_->addTab(configWidget, "⚙️ Configuración");
        
        auto layout = new QVBoxLayout(configWidget);
        
        // Parámetros de simulación
        auto simGroup = new QGroupBox("Parámetros de Simulación");
        auto simLayout = new QHBoxLayout(simGroup);
        
        simLayout->addWidget(new QLabel("Simulaciones:"));
        simulationsSpinBox_ = new QSpinBox();
        simulationsSpinBox_->setRange(1000, 100000);
        simulationsSpinBox_->setValue(10000);
        simulationsSpinBox_->setSingleStep(1000);
        simLayout->addWidget(simulationsSpinBox_);
        
        simLayout->addWidget(new QLabel("Años:"));
        timeHorizonSpinBox_ = new QSpinBox();
        timeHorizonSpinBox_->setRange(1, 10);
        timeHorizonSpinBox_->setValue(2);
        simLayout->addWidget(timeHorizonSpinBox_);
        
        simLayout->addStretch();
        layout->addWidget(simGroup);
        
        // Tabla de opciones
        auto optionsGroup = new QGroupBox("Opciones de Decisión");
        auto optionsLayout = new QVBoxLayout(optionsGroup);
        
        // Botones
        auto buttonsLayout = new QHBoxLayout();
        auto addButton = new QPushButton("➕ Agregar Opción");
        auto removeButton = new QPushButton("➖ Remover Opción");
        connect(addButton, &QPushButton::clicked, this, &DecisionMakerWindow::addNewOption);
        connect(removeButton, &QPushButton::clicked, this, &DecisionMakerWindow::removeSelectedOption);
        
        buttonsLayout->addWidget(addButton);
        buttonsLayout->addWidget(removeButton);
        buttonsLayout->addStretch();
        optionsLayout->addLayout(buttonsLayout);
        
        // Tabla
        optionsTable_ = new QTableWidget();
        optionsTable_->setColumnCount(5);
        QStringList headers = {"Nombre", "Costo ($)", "Satisfacción (1-10)", "Confiabilidad (1-10)", "Habilitada"};
        optionsTable_->setHorizontalHeaderLabels(headers);
        optionsTable_->horizontalHeader()->setStretchLastSection(true);
        optionsLayout->addWidget(optionsTable_);
        
        layout->addWidget(optionsGroup);
        
        // Botones de simulación
        auto runLayout = new QHBoxLayout();
        
        runButton_ = new QPushButton("🚀 Ejecutar Simulación");
        runButton_->setStyleSheet("QPushButton { background-color: #27ae60; color: white; "
                                 "font-weight: bold; padding: 10px; }");
        stopButton_ = new QPushButton("⏹️ Detener");
        stopButton_->setEnabled(false);
        
        connect(runButton_, &QPushButton::clicked, this, &DecisionMakerWindow::runSimulation);
        connect(stopButton_, &QPushButton::clicked, this, &DecisionMakerWindow::stopSimulation);
        
        runLayout->addWidget(runButton_);
        runLayout->addWidget(stopButton_);
        layout->addLayout(runLayout);
        
        // Progress bar
        progressBar_ = new QProgressBar();
        progressBar_->setVisible(false);
        progressLabel_ = new QLabel();
        progressLabel_->setVisible(false);
        
        layout->addWidget(progressBar_);
        layout->addWidget(progressLabel_);
    }
    
    void setupResultsTab() {
        auto resultsWidget = new QWidget();
        tabWidget_->addTab(resultsWidget, "📊 Resultados");
        
        auto layout = new QVBoxLayout(resultsWidget);
        
        // Tabla de resultados
        auto resultsGroup = new QGroupBox("Resultados de Simulación");
        auto resultsLayout = new QVBoxLayout(resultsGroup);
        
        resultsTable_ = new QTableWidget();
        resultsTable_->setColumnCount(7);
        QStringList headers = {"Rank", "Opción", "Costo Promedio", "Satisfacción", 
                              "Rango Costo", "Problemas (h)", "Score Valor"};
        resultsTable_->setHorizontalHeaderLabels(headers);
        resultsTable_->horizontalHeader()->setStretchLastSection(true);
        resultsLayout->addWidget(resultsTable_);
        
        layout->addWidget(resultsGroup);
        
        // Gráficos (placeholder)
        auto chartsGroup = new QGroupBox("Análisis Visual");
        auto chartsLayout = new QHBoxLayout(chartsGroup);
        
        costChartView_ = new QChartView();
        costChartView_->setMinimumHeight(300);
        chartsLayout->addWidget(costChartView_);
        
        layout->addWidget(chartsGroup);
        
        // Recomendación
        auto recGroup = new QGroupBox("🎯 Recomendación");
        auto recLayout = new QVBoxLayout(recGroup);
        
        recommendationText_ = new QTextEdit();
        recommendationText_->setMaximumHeight(150);
        recommendationText_->setReadOnly(true);
        recLayout->addWidget(recommendationText_);
        
        layout->addWidget(recGroup);
    }
    
    void setupConnections() {
        // Connections are set up in slot functions
    }
    
    void loadDefaultOptions() {
        options_ = {
            DecisionOption("Seguir con actual", 50, 6.5, 8.5, 6.5),
            DecisionOption("Mini PC AMD", 290, 8.7, 9.0, 8.5),
            DecisionOption("Mac Mini usado", 280, 7.5, 7.5, 8.0),
            DecisionOption("Laptop ThinkPad", 270, 8.1, 7.8, 7.5)
        };
        
        updateOptionsTable();
    }
    
    void updateOptionsTable() {
        optionsTable_->setRowCount(options_.size());
        
        for (size_t i = 0; i < options_.size(); ++i) {
            optionsTable_->setItem(i, 0, new QTableWidgetItem(options_[i].name));
            optionsTable_->setItem(i, 1, new QTableWidgetItem(QString::number(options_[i].cost, 'f', 0)));
            optionsTable_->setItem(i, 2, new QTableWidgetItem(QString::number(options_[i].satisfaction, 'f', 1)));
            optionsTable_->setItem(i, 3, new QTableWidgetItem(QString::number(options_[i].reliability, 'f', 1)));
            
            auto checkBox = new QTableWidgetItem();
            checkBox->setCheckState(options_[i].enabled ? Qt::Checked : Qt::Unchecked);
            optionsTable_->setItem(i, 4, checkBox);
        }
    }
    
    void updateOptionsFromTable() {
        for (int i = 0; i < optionsTable_->rowCount() && i < static_cast<int>(options_.size()); ++i) {
            if (auto item = optionsTable_->item(i, 0)) {
                options_[i].name = item->text();
            }
            if (auto item = optionsTable_->item(i, 1)) {
                options_[i].cost = item->text().toDouble();
            }
            if (auto item = optionsTable_->item(i, 2)) {
                options_[i].satisfaction = item->text().toDouble();
            }
            if (auto item = optionsTable_->item(i, 3)) {
                options_[i].reliability = item->text().toDouble();
            }
            if (auto item = optionsTable_->item(i, 4)) {
                options_[i].enabled = (item->checkState() == Qt::Checked);
            }
        }
    }
    
    void updateResultsTable(const std::vector<SimulationResults>& results) {
        resultsTable_->setRowCount(results.size());
        
        for (size_t i = 0; i < results.size(); ++i) {
            const auto& result = results[i];
            
            resultsTable_->setItem(i, 0, new QTableWidgetItem(QString::number(result.rank)));
            resultsTable_->setItem(i, 1, new QTableWidgetItem(result.optionName));
            resultsTable_->setItem(i, 2, new QTableWidgetItem(QString("$%1").arg(result.avgCost, 0, 'f', 0)));
            resultsTable_->setItem(i, 3, new QTableWidgetItem(QString::number(result.avgSatisfaction, 'f', 1)));
            resultsTable_->setItem(i, 4, new QTableWidgetItem(QString("$%1 - $%2")
                .arg(result.minCost, 0, 'f', 0).arg(result.maxCost, 0, 'f', 0)));
            resultsTable_->setItem(i, 5, new QTableWidgetItem(QString::number(result.avgProblems, 'f', 1)));
            resultsTable_->setItem(i, 6, new QTableWidgetItem(QString::number(result.valueScore, 'f', 2)));
            
            // Highlight winner
            if (result.rank == 1) {
                for (int col = 0; col < resultsTable_->columnCount(); ++col) {
                    if (auto item = resultsTable_->item(i, col)) {
                        item->setBackground(QColor(212, 237, 218)); // Light green
                    }
                }
            }
        }
        
        resultsTable_->resizeColumnsToContents();
    }
    
    void createCharts(const std::vector<SimulationResults>& results) {
        auto chart = new QChart();
        auto series = new QBarSeries();
        
        auto costSet = new QBarSet("Costo Promedio");
        QStringList categories;
        
        for (const auto& result : results) {
            *costSet << result.avgCost;
            categories << result.optionName;
        }
        
        series->append(costSet);
        chart->addSeries(series);
        chart->setTitle("Comparación de Costos");
        chart->setAnimationOptions(QChart::SeriesAnimations);
        
        auto axisX = new QBarCategoryAxis();
        axisX->append(categories);
        chart->addAxis(axisX, Qt::AlignBottom);
        series->attachAxis(axisX);
        
        auto axisY = new QValueAxis();
        axisY->setTitleText("Costo ($)");
        chart->addAxis(axisY, Qt::AlignLeft);
        series->attachAxis(axisY);
        
        costChartView_->setChart(chart);
    }
    
    void generateRecommendation(const std::vector<SimulationResults>& results) {
        if (results.empty()) return;
        
        const auto& winner = results[0]; // Ya están ordenados por rank
        
        QString recommendation = QString(
            "<h3>🏆 Recomendación: %1</h3>"
            "<p><b>Esta es tu mejor opción</b> según %2 simulaciones Monte Carlo.</p>"
            "<ul>"
            "<li><b>Costo promedio:</b> $%3</li>"
            "<li><b>Satisfacción:</b> %4/10</li>"
            "<li><b>Score de valor:</b> %5</li>"
            "<li><b>Riesgo:</b> ±$%6</li>"
            "</ul>"
            "<p><b>¿Por qué es la mejor?</b> Ofrece %7 puntos de satisfacción por cada $100 invertidos, "
            "la mejor relación valor-beneficio de todas las opciones analizadas.</p>"
        ).arg(winner.optionName)
         .arg(simulationsSpinBox_->value())
         .arg(winner.avgCost, 0, 'f', 0)
         .arg(winner.avgSatisfaction, 0, 'f', 1)
         .arg(winner.valueScore, 0, 'f', 2)
         .arg(winner.stdCost, 0, 'f', 0)
         .arg(winner.valueScore, 0, 'f', 2);
        
        recommendationText_->setHtml(recommendation);
    }
    
    // UI Components
    QTabWidget* tabWidget_;
    QTableWidget* optionsTable_;
    QTableWidget* resultsTable_;
    QSpinBox* simulationsSpinBox_;
    QSpinBox* timeHorizonSpinBox_;
    QPushButton* runButton_;
    QPushButton* stopButton_;
    QProgressBar* progressBar_;
    QLabel* progressLabel_;
    QChartView* costChartView_;
    QTextEdit* recommendationText_;
    
    // Data
    std::vector<DecisionOption> options_;
    std::unique_ptr<SimulationWorker> simulationWorker_;
    std::unique_ptr<QThread> workerThread_;
};

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    
    DecisionMakerWindow window;
    window.show();
    
    return app.exec();
}

#include "qt_gui.moc"