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
#include <QtWidgets/QTableWidget>
#include <QtWidgets/QTableWidgetItem>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QGroupBox>
#include <QtWidgets/QMessageBox>
#include <QTimer>
#include <vector>
#include <random>
#include <cmath>

/**
 * 🎯 GUI SIMPLIFICADA EN C++ CON QT
 * Versión más simple para evitar problemas de compilación
 */

struct DecisionOption {
    QString name;
    double cost;
    double satisfaction;
    double reliability;
    
    DecisionOption(const QString& n = "Nueva Opción", double c = 100.0, 
                   double s = 7.0, double r = 8.0)
        : name(n), cost(c), satisfaction(s), reliability(r) {}
};

struct SimulationResult {
    QString optionName;
    double avgCost;
    double avgSatisfaction;
    double valueScore;
    int rank;
};

class DecisionMakerWindow : public QMainWindow {
    Q_OBJECT

public:
    DecisionMakerWindow(QWidget *parent = nullptr) : QMainWindow(parent) {
        setupUI();
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
        
        // Actualizar opciones desde la tabla
        updateOptionsFromTable();
        
        // Configuración
        int numSims = simulationsSpinBox_->value();
        int timeHorizon = timeHorizonSpinBox_->value();
        
        // Simular
        auto results = executeSimulation(numSims, timeHorizon);
        
        // Mostrar resultados
        showResults(results);
    }

private:
    void setupUI() {
        setWindowTitle("🎲 Decision Maker - Monte Carlo Simulator");
        setMinimumSize(900, 600);
        
        auto centralWidget = new QWidget(this);
        setCentralWidget(centralWidget);
        
        auto mainLayout = new QVBoxLayout(centralWidget);
        
        // Header
        auto headerLabel = new QLabel("🎲 Decision Maker - Simulador Monte Carlo");
        headerLabel->setStyleSheet("QLabel { font-size: 18px; font-weight: bold; "
                                  "color: #2c3e50; padding: 10px; }");
        headerLabel->setAlignment(Qt::AlignCenter);
        mainLayout->addWidget(headerLabel);
        
        // Parámetros de simulación
        auto simGroup = new QGroupBox("Parámetros de Simulación");
        auto simLayout = new QHBoxLayout(simGroup);
        
        simLayout->addWidget(new QLabel("Simulaciones:"));
        simulationsSpinBox_ = new QSpinBox();
        simulationsSpinBox_->setRange(1000, 50000);
        simulationsSpinBox_->setValue(10000);
        simulationsSpinBox_->setSingleStep(1000);
        simLayout->addWidget(simulationsSpinBox_);
        
        simLayout->addWidget(new QLabel("Años:"));
        timeHorizonSpinBox_ = new QSpinBox();
        timeHorizonSpinBox_->setRange(1, 10);
        timeHorizonSpinBox_->setValue(2);
        simLayout->addWidget(timeHorizonSpinBox_);
        
        simLayout->addStretch();
        mainLayout->addWidget(simGroup);
        
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
        
        // Tabla de opciones
        optionsTable_ = new QTableWidget();
        optionsTable_->setColumnCount(4);
        QStringList headers = {"Nombre", "Costo ($)", "Satisfacción (1-10)", "Confiabilidad (1-10)"};
        optionsTable_->setHorizontalHeaderLabels(headers);
        optionsTable_->horizontalHeader()->setStretchLastSection(true);
        optionsLayout->addWidget(optionsTable_);
        
        mainLayout->addWidget(optionsGroup);
        
        // Botón de simulación
        runButton_ = new QPushButton("🚀 Ejecutar Simulación Monte Carlo");
        runButton_->setStyleSheet("QPushButton { background-color: #27ae60; color: white; "
                                 "font-weight: bold; padding: 10px; }");
        connect(runButton_, &QPushButton::clicked, this, &DecisionMakerWindow::runSimulation);
        mainLayout->addWidget(runButton_);
        
        // Tabla de resultados
        auto resultsGroup = new QGroupBox("Resultados de Simulación");
        auto resultsLayout = new QVBoxLayout(resultsGroup);
        
        resultsTable_ = new QTableWidget();
        resultsTable_->setColumnCount(5);
        QStringList resHeaders = {"Rank", "Opción", "Costo Promedio", "Satisfacción", "Score Valor"};
        resultsTable_->setHorizontalHeaderLabels(resHeaders);
        resultsTable_->horizontalHeader()->setStretchLastSection(true);
        resultsLayout->addWidget(resultsTable_);
        
        mainLayout->addWidget(resultsGroup);
        
        // Recomendación
        auto recGroup = new QGroupBox("🎯 Recomendación");
        auto recLayout = new QVBoxLayout(recGroup);
        
        recommendationText_ = new QTextEdit();
        recommendationText_->setMaximumHeight(120);
        recommendationText_->setReadOnly(true);
        recLayout->addWidget(recommendationText_);
        
        mainLayout->addWidget(recGroup);
    }
    
    void loadDefaultOptions() {
        options_ = {
            DecisionOption("Seguir con actual", 50, 6.5, 8.5),
            DecisionOption("Mini PC AMD", 290, 8.7, 9.0),
            DecisionOption("Mac Mini usado", 280, 7.5, 7.5),
            DecisionOption("Laptop ThinkPad", 270, 8.1, 7.8)
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
        }
    }
    
    double normalRandom(double mean, double stdDev) {
        static std::random_device rd;
        static std::mt19937 gen(rd());
        std::normal_distribution<double> dist(mean, stdDev);
        return dist(gen);
    }
    
    double uniformRandom(double min, double max) {
        static std::random_device rd;
        static std::mt19937 gen(rd());
        std::uniform_real_distribution<double> dist(min, max);
        return dist(gen);
    }
    
    std::vector<SimulationResult> executeSimulation(int numSims, int timeHorizon) {
        std::vector<SimulationResult> results;
        results.resize(options_.size());
        
        // Inicializar resultados
        for (size_t i = 0; i < options_.size(); ++i) {
            results[i].optionName = options_[i].name;
            results[i].avgCost = 0;
            results[i].avgSatisfaction = 0;
        }
        
        std::vector<std::vector<double>> allCosts(options_.size());
        std::vector<std::vector<double>> allSatisfactions(options_.size());
        
        // Ejecutar simulaciones
        for (int sim = 0; sim < numSims; ++sim) {
            for (size_t i = 0; i < options_.size(); ++i) {
                // Simular costo total
                double totalCost = options_[i].cost;
                
                // Mantenimiento anual
                double maintenanceRate = (10.0 - options_[i].reliability) / 10.0 * 0.15;
                for (int year = 1; year <= timeHorizon; ++year) {
                    if (uniformRandom(0, 1) < maintenanceRate) {
                        totalCost += options_[i].cost * normalRandom(0.05, 0.02);
                    }
                }
                
                // Depreciación
                double depreciationRate = 0.15 + uniformRandom(0, 0.1); // 15-25%
                double residualValue = options_[i].cost * std::pow(1.0 - depreciationRate, timeHorizon);
                totalCost -= residualValue;
                
                totalCost = std::max(0.0, totalCost);
                
                // Simular satisfacción
                double satisfaction = std::max(1.0, std::min(10.0, 
                    normalRandom(options_[i].satisfaction, 0.5)));
                
                allCosts[i].push_back(totalCost);
                allSatisfactions[i].push_back(satisfaction);
            }
        }
        
        // Calcular estadísticas
        for (size_t i = 0; i < options_.size(); ++i) {
            double sumCost = 0, sumSat = 0;
            for (size_t j = 0; j < allCosts[i].size(); ++j) {
                sumCost += allCosts[i][j];
                sumSat += allSatisfactions[i][j];
            }
            
            results[i].avgCost = sumCost / allCosts[i].size();
            results[i].avgSatisfaction = sumSat / allSatisfactions[i].size();
            results[i].valueScore = results[i].avgSatisfaction / (results[i].avgCost / 100.0);
        }
        
        // Rankear por value score
        std::sort(results.begin(), results.end(), 
                  [](const SimulationResult& a, const SimulationResult& b) {
                      return a.valueScore > b.valueScore;
                  });
        
        for (size_t i = 0; i < results.size(); ++i) {
            results[i].rank = i + 1;
        }
        
        return results;
    }
    
    void showResults(const std::vector<SimulationResult>& results) {
        // Actualizar tabla de resultados
        resultsTable_->setRowCount(results.size());
        
        for (size_t i = 0; i < results.size(); ++i) {
            const auto& result = results[i];
            
            resultsTable_->setItem(i, 0, new QTableWidgetItem(QString::number(result.rank)));
            resultsTable_->setItem(i, 1, new QTableWidgetItem(result.optionName));
            resultsTable_->setItem(i, 2, new QTableWidgetItem(QString("$%1").arg(result.avgCost, 0, 'f', 0)));
            resultsTable_->setItem(i, 3, new QTableWidgetItem(QString::number(result.avgSatisfaction, 'f', 1)));
            resultsTable_->setItem(i, 4, new QTableWidgetItem(QString::number(result.valueScore, 'f', 2)));
            
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
        
        // Generar recomendación
        if (!results.empty()) {
            const auto& winner = results[0];
            QString recommendation = QString(
                "<h3>🏆 Recomendación: %1</h3>"
                "<p><b>Esta es tu mejor opción</b> según %2 simulaciones Monte Carlo.</p>"
                "<p><b>Costo promedio:</b> $%3 | <b>Satisfacción:</b> %4/10 | <b>Score:</b> %5</p>"
                "<p>Esta opción te da <b>%6 puntos de satisfacción por cada $100 invertidos</b>.</p>"
            ).arg(winner.optionName)
             .arg(simulationsSpinBox_->value())
             .arg(winner.avgCost, 0, 'f', 0)
             .arg(winner.avgSatisfaction, 0, 'f', 1)
             .arg(winner.valueScore, 0, 'f', 2)
             .arg(winner.valueScore, 0, 'f', 2);
            
            recommendationText_->setHtml(recommendation);
        }
    }
    
    // UI Components
    QTableWidget* optionsTable_;
    QTableWidget* resultsTable_;
    QSpinBox* simulationsSpinBox_;
    QSpinBox* timeHorizonSpinBox_;
    QPushButton* runButton_;
    QTextEdit* recommendationText_;
    
    // Data
    std::vector<DecisionOption> options_;
};

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    
    DecisionMakerWindow window;
    window.show();
    
    return app.exec();
}

#include "qt_gui_simple.moc"