#pragma once

#include <random>
#include <memory>
#include <unordered_map>
#include <string>
#include <any>

namespace DecisionMaker {

/**
 * @brief Clase base abstracta para distribuciones estadísticas
 * 
 * Proporciona una interfaz común para todas las distribuciones
 * que se pueden usar en las simulaciones Monte Carlo.
 */
class Distribution {
public:
    virtual ~Distribution() = default;
    
    /**
     * @brief Genera un valor aleatorio según la distribución
     * @param rng Generador de números aleatorios
     * @return Valor aleatorio generado
     */
    virtual double sample(std::mt19937& rng) const = 0;
    
    /**
     * @brief Obtiene la media de la distribución
     * @return Valor medio
     */
    virtual double mean() const = 0;
    
    /**
     * @brief Obtiene la desviación estándar de la distribución
     * @return Desviación estándar
     */
    virtual double stddev() const = 0;
    
    /**
     * @brief Clona la distribución
     * @return Puntero único a una copia de la distribución
     */
    virtual std::unique_ptr<Distribution> clone() const = 0;
    
    /**
     * @brief Obtiene el nombre de la distribución
     * @return Nombre de la distribución
     */
    virtual std::string name() const = 0;
};

/**
 * @brief Contenedor para parámetros de simulación
 * 
 * Permite almacenar parámetros de diferentes tipos (distribuciones, valores fijos, etc.)
 * usando std::any para máxima flexibilidad.
 */
class SimulationParameters {
private:
    std::unordered_map<std::string, std::any> parameters_;
    
public:
    /**
     * @brief Establece un parámetro de distribución
     * @param name Nombre del parámetro
     * @param distribution Distribución asociada
     */
    void setDistribution(const std::string& name, std::unique_ptr<Distribution> distribution);
    
    /**
     * @brief Establece un parámetro con valor fijo
     * @param name Nombre del parámetro
     * @param value Valor fijo
     */
    template<typename T>
    void setValue(const std::string& name, const T& value) {
        parameters_[name] = value;
    }
    
    /**
     * @brief Obtiene una distribución por nombre
     * @param name Nombre del parámetro
     * @return Puntero a la distribución o nullptr si no existe
     */
    const Distribution* getDistribution(const std::string& name) const;
    
    /**
     * @brief Obtiene un valor fijo por nombre
     * @param name Nombre del parámetro
     * @return Valor del parámetro
     * @throws std::bad_any_cast si el tipo no coincide
     */
    template<typename T>
    T getValue(const std::string& name) const {
        auto it = parameters_.find(name);
        if (it != parameters_.end()) {
            return std::any_cast<T>(it->second);
        }
        throw std::runtime_error("Parameter not found: " + name);
    }
    
    /**
     * @brief Verifica si existe un parámetro
     * @param name Nombre del parámetro
     * @return true si existe, false en caso contrario
     */
    bool hasParameter(const std::string& name) const;
    
    /**
     * @brief Obtiene todos los nombres de parámetros
     * @return Vector con los nombres
     */
    std::vector<std::string> getParameterNames() const;
};

} // namespace DecisionMaker