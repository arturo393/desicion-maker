cmake_minimum_required(VERSION 3.12)
project(DecisionMaker VERSION 2.0.0 LANGUAGES CXX)

# Configuración del estándar C++
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Configuración de compilación
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")
set(CMAKE_CXX_FLAGS_DEBUG "-g -DDEBUG -O0")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")

# Configurar tipo de build por defecto
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Encontrar dependencias del sistema
find_package(Threads REQUIRED)

# Nueva opción: Deep Research Pro
option(ENABLE_DEEP_RESEARCH "Enable Google Deep Research Pro integration" ON)

# Definir directorios
set(SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src")
set(EXAMPLES_DIR "${CMAKE_CURRENT_SOURCE_DIR}/examples")
set(TESTS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/tests")

# Archivos fuente del framework
# Framework base + mejoras V4: todos los 5 módulos + framework genérico
set(FRAMEWORK_SOURCES
    "${SRC_DIR}/decision_framework.cpp"
    "${SRC_DIR}/real_time_monitor.cpp"
    "${SRC_DIR}/bayesian_updater.cpp"
    "${SRC_DIR}/scenario_analysis.cpp"
    "${SRC_DIR}/ml_demand_predictor.cpp"
    "${SRC_DIR}/value_at_risk.cpp"
)

# Crear biblioteca estática del framework
add_library(decisionmaker STATIC ${FRAMEWORK_SOURCES})

# Configurar includes
target_include_directories(decisionmaker 
    PUBLIC 
        $<BUILD_INTERFACE:${SRC_DIR}>
        $<INSTALL_INTERFACE:include>
)

target_link_libraries(decisionmaker PUBLIC Threads::Threads)

# Propiedades de la biblioteca
set_target_properties(decisionmaker PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION 1
    POSITION_INDEPENDENT_CODE ON
)

# Función helper para crear ejemplos
function(add_decision_example name source_file)
    add_executable(${name} ${source_file})
    target_link_libraries(${name} PRIVATE decisionmaker)
    target_include_directories(${name} PRIVATE ${SRC_DIR})
endfunction()

# Agregar ejemplos si existen
if(EXISTS "${EXAMPLES_DIR}/v4_improvements_demo.cpp")
    add_decision_example(v4_improvements_demo "${EXAMPLES_DIR}/v4_improvements_demo.cpp")
endif()

if(EXISTS "${EXAMPLES_DIR}/v4_complete_analysis.cpp")
    add_decision_example(v4_complete_analysis "${EXAMPLES_DIR}/v4_complete_analysis.cpp")
endif()

if(EXISTS "${EXAMPLES_DIR}/template_new_decision.cpp")
    add_decision_example(template_new_decision "${EXAMPLES_DIR}/template_new_decision.cpp")
endif()

# Agregar ejemplo con Deep Research Pro (NUEVO)
if(ENABLE_DEEP_RESEARCH)
    if(EXISTS "${EXAMPLES_DIR}/deep_research_decision_example.cpp")
        add_decision_example(deep_research_example "${EXAMPLES_DIR}/deep_research_decision_example.cpp")
        message(STATUS "✓ Deep Research Pro Integration ENABLED")
    endif()
else()
    message(STATUS "✗ Deep Research Pro Integration DISABLED")
endif()

# Habilitar testing
enable_testing()

# Mostrar información de compilación
message(STATUS "====================================")
message(STATUS "📊 DECISION MAKER V2 - BUILD SYSTEM")
message(STATUS "====================================")
message(STATUS "✓ Framework de Decisiones (5 metodologías)")
message(STATUS "✓ Deep Research Pro Integration (v2.0)")
message(STATUS "✓ Real-Time Market Monitoring")
message(STATUS "✓ Bayesian Updater")
message(STATUS "✓ Scenario Analysis")
message(STATUS "====================================")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ compiler: ${CMAKE_CXX_COMPILER}")
message(STATUS "Deep Research: ${ENABLE_DEEP_RESEARCH}")
message(STATUS "C++ standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Install prefix: ${CMAKE_INSTALL_PREFIX}")
message(STATUS "====================================")