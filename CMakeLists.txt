cmake_minimum_required(VERSION 3.12)
project(DecisionMaker VERSION 1.0.0 LANGUAGES CXX)

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

# Definir directorios
set(SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src")
set(EXAMPLES_DIR "${CMAKE_CURRENT_SOURCE_DIR}/examples")
set(TESTS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/tests")

# Archivos fuente del framework
# Primero los 3 módulos nuevos (mejoras V4)
set(FRAMEWORK_SOURCES
    "${SRC_DIR}/real_time_monitor.cpp"
    "${SRC_DIR}/bayesian_updater.cpp"
    "${SRC_DIR}/scenario_analysis.cpp"
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

# Habilitar testing
enable_testing()

# Mostrar información de compilación
message(STATUS "====================================")
message(STATUS "📊 DECISION MAKER V4 - BUILD SYSTEM")
message(STATUS "====================================")
message(STATUS "✓ Real-Time Market Monitoring")
message(STATUS "✓ Bayesian Updater")
message(STATUS "✓ Scenario Analysis")
message(STATUS "====================================")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ compiler: ${CMAKE_CXX_COMPILER}")
message(STATUS "C++ standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Install prefix: ${CMAKE_INSTALL_PREFIX}")
message(STATUS "====================================")