#include <QtWidgets/QApplication>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QWidget>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QLabel>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QSpinBox>
#include <QtWidgets/QTableWidget>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QTextEdit>
#include <QtWidgets/QGroupBox>
#include <QMessageBox>
#include <vector>
#include <random>
#include <algorithm>

// Struct simple para opciones
struct Option {
    std::string name;
    double cost;
    double satisfaction;
    double reliability;
};

// Struct para resultados
struct Result {
    std::string name;
    double avgCost;
    double avgSat;
    double score;
    int rank;
};

class MainWindow : public QMainWindow {
    Q_OBJECT

private:
    QTableWidget* optionsTable;
    QTableWidget* resultsTable;
    QSpinBox* simsSpinBox;
    QTextEdit* recommendText;
    std::vector<Option> options;

public:
    MainWindow() {
        setWindowTitle("Decision Maker - Monte Carlo");
        setMinimumSize(800, 600);
        
        // Widget central
        QWidget* central = new QWidget(this);
        setCentralWidget(central);
        QVBoxLayout* mainLayout = new QVBoxLayout(central);
        
        // Título
        QLabel* title = new QLabel("🎲 Decision Maker - Monte Carlo Simulator");
        QFont font;
        font.setPointSize(16);
        font.setBold(true);
        title->setFont(font);
        title->setAlignment(Qt::AlignCenter);
        mainLayout->addWidget(title);
        
        // Parámetros
        QGroupBox* paramsGroup = new QGroupBox("Parametros");
        QHBoxLayout* paramsLayout = new QHBoxLayout(paramsGroup);
        paramsLayout->addWidget(new QLabel("Simulaciones:"));
        simsSpinBox = new QSpinBox();
        simsSpinBox->setRange(1000, 50000);
        simsSpinBox->setValue(10000);
        simsSpinBox->setSingleStep(1000);
        paramsLayout->addWidget(simsSpinBox);
        paramsLayout->addStretch();
        mainLayout->addWidget(paramsGroup);
        
        // Tabla de opciones
        QGroupBox* optionsGroup = new QGroupBox("Opciones");
        QVBoxLayout* optLayout = new QVBoxLayout(optionsGroup);
        
        optionsTable = new QTableWidget();
        optionsTable->setColumnCount(4);
        QStringList headers;
        headers << "Nombre" << "Costo" << "Satisfaccion" << "Confiabilidad";
        optionsTable->setHorizontalHeaderLabels(headers);
        optLayout->addWidget(optionsTable);
        
        mainLayout->addWidget(optionsGroup);
        
        // Botón simular
        QPushButton* runBtn = new QPushButton("🚀 Ejecutar Simulacion");
        runBtn->setMinimumHeight(40);
        connect(runBtn, &QPushButton::clicked, this, &MainWindow::runSim);
        mainLayout->addWidget(runBtn);
        
        // Tabla resultados
        QGroupBox* resultsGroup = new QGroupBox("Resultados");
        QVBoxLayout* resLayout = new QVBoxLayout(resultsGroup);
        
        resultsTable = new QTableWidget();
        resultsTable->setColumnCount(5);
        QStringList resHeaders;
        resHeaders << "Rank" << "Opcion" << "Costo Avg" << "Satisfaccion" << "Score";
        resultsTable->setHorizontalHeaderLabels(resHeaders);
        resLayout->addWidget(resultsTable);
        
        mainLayout->addWidget(resultsGroup);
        
        // Recomendación
        QGroupBox* recGroup = new QGroupBox("Recomendacion");
        QVBoxLayout* recLayout = new QVBoxLayout(recGroup);
        recommendText = new QTextEdit();
        recommendText->setMaximumHeight(100);
        recommendText->setReadOnly(true);
        recLayout->addWidget(recommendText);
        mainLayout->addWidget(recGroup);
        
        // Cargar datos default
        loadDefaults();
    }

private slots:
    void runSim() {
        if (options.size() < 2) {
            QMessageBox::warning(this, "Error", "Necesitas al menos 2 opciones");
            return;
        }
        
        int numSims = simsSpinBox->value();
        std::vector<Result> results = simulate(numSims);
        showResults(results);
    }

private:
    void loadDefaults() {
        options.clear();
        options.push_back({"Actual", 50, 6.5, 8.5});
        options.push_back({"Mini PC AMD", 290, 8.7, 9.0});
        options.push_back({"Mac Mini", 280, 7.5, 7.5});
        options.push_back({"ThinkPad", 270, 8.1, 7.8});
        
        updateTable();
    }
    
    void updateTable() {
        optionsTable->setRowCount(options.size());
        
        for (size_t i = 0; i < options.size(); i++) {
            optionsTable->setItem(i, 0, new QTableWidgetItem(QString::fromStdString(options[i].name)));
            optionsTable->setItem(i, 1, new QTableWidgetItem(QString::number(options[i].cost)));
            optionsTable->setItem(i, 2, new QTableWidgetItem(QString::number(options[i].satisfaction)));
            optionsTable->setItem(i, 3, new QTableWidgetItem(QString::number(options[i].reliability)));
        }
    }
    
    std::vector<Result> simulate(int numSims) {
        std::vector<Result> results;
        std::random_device rd;
        std::mt19937 gen(rd());
        
        for (const auto& opt : options) {
            double totalCost = 0;
            double totalSat = 0;
            
            std::normal_distribution<> costDist(opt.cost, opt.cost * 0.1);
            std::normal_distribution<> satDist(opt.satisfaction, 0.5);
            
            for (int i = 0; i < numSims; i++) {
                double c = std::max(0.0, costDist(gen));
                double s = std::max(1.0, std::min(10.0, satDist(gen)));
                
                totalCost += c;
                totalSat += s;
            }
            
            double avgC = totalCost / numSims;
            double avgS = totalSat / numSims;
            double score = avgS / (avgC / 100.0);
            
            Result r;
            r.name = opt.name;
            r.avgCost = avgC;
            r.avgSat = avgS;
            r.score = score;
            r.rank = 0;
            
            results.push_back(r);
        }
        
        // Rankear
        std::sort(results.begin(), results.end(), 
                  [](const Result& a, const Result& b) { return a.score > b.score; });
        
        for (size_t i = 0; i < results.size(); i++) {
            results[i].rank = i + 1;
        }
        
        return results;
    }
    
    void showResults(const std::vector<Result>& results) {
        resultsTable->setRowCount(results.size());
        
        for (size_t i = 0; i < results.size(); i++) {
            resultsTable->setItem(i, 0, new QTableWidgetItem(QString::number(results[i].rank)));
            resultsTable->setItem(i, 1, new QTableWidgetItem(QString::fromStdString(results[i].name)));
            resultsTable->setItem(i, 2, new QTableWidgetItem(QString("$%1").arg(results[i].avgCost, 0, 'f', 0)));
            resultsTable->setItem(i, 3, new QTableWidgetItem(QString::number(results[i].avgSat, 'f', 1)));
            resultsTable->setItem(i, 4, new QTableWidgetItem(QString::number(results[i].score, 'f', 2)));
        }
        
        // Recomendación
        if (!results.empty()) {
            QString rec = QString("<h3>🏆 %1</h3><p>Score: %2</p>")
                .arg(QString::fromStdString(results[0].name))
                .arg(results[0].score, 0, 'f', 2);
            recommendText->setHtml(rec);
        }
    }
};

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    MainWindow window;
    window.show();
    return app.exec();
}

#include "qt_gui_minimal.moc"