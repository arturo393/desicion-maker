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
set(SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src)
set(INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src)
set(EXAMPLES_DIR ${CMAKE_CURRENT_SOURCE_DIR}/examples)
set(TESTS_DIR ${CMAKE_CURRENT_SOURCE_DIR}/tests)

# Archivos fuente del framework
file(GLOB_RECURSE FRAMEWORK_SOURCES
    "${SRC_DIR}/core/*.cpp"
    "${SRC_DIR}/distributions/*.cpp"
    "${SRC_DIR}/scenarios/*.cpp"
    "${SRC_DIR}/utils/*.cpp"
)

file(GLOB_RECURSE FRAMEWORK_HEADERS
    "${SRC_DIR}/core/*.h"
    "${SRC_DIR}/distributions/*.h"
    "${SRC_DIR}/scenarios/*.h"
    "${SRC_DIR}/utils/*.h"
)

# Crear biblioteca estática del framework
add_library(decisionmaker STATIC ${FRAMEWORK_SOURCES})

# Configurar includes y enlaces
target_include_directories(decisionmaker PUBLIC ${INCLUDE_DIR})
target_link_libraries(decisionmaker PUBLIC Threads::Threads)

# Propiedades de la biblioteca
set_target_properties(decisionmaker PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION 1
    PUBLIC_HEADER "${FRAMEWORK_HEADERS}"
)

# Función helper para crear ejemplos
function(add_example name source_file)
    add_executable(${name} ${source_file})
    target_link_libraries(${name} PRIVATE decisionmaker)
    target_include_directories(${name} PRIVATE ${INCLUDE_DIR})
    
    # Agregar al target de ejemplos
    add_dependencies(examples ${name})
endfunction()

# Target para construir todos los ejemplos
add_custom_target(examples)

# Agregar ejemplos
add_example(basic_dice ${EXAMPLES_DIR}/basic_dice.cpp)
add_example(simple_decision ${EXAMPLES_DIR}/simple_decision.cpp)
add_example(investment_vs_education ${EXAMPLES_DIR}/investment_vs_education.cpp)

# Función helper para crear tests
function(add_test_executable name source_file)
    add_executable(${name} ${source_file})
    target_link_libraries(${name} PRIVATE decisionmaker)
    target_include_directories(${name} PRIVATE ${INCLUDE_DIR})
    
    # Agregar como test de CTest
    add_test(NAME ${name} COMMAND ${name})
    
    # Agregar al target de tests
    add_dependencies(tests ${name})
endfunction()

# Habilitar testing
enable_testing()

# Target para construir todos los tests
add_custom_target(tests)

# Agregar tests (cuando los creemos)
# add_test_executable(test_distributions ${TESTS_DIR}/test_distributions.cpp)
# add_test_executable(test_engine ${TESTS_DIR}/test_engine.cpp)

# Target para ejecutar todos los tests
add_custom_target(run_tests
    COMMAND ${CMAKE_CTEST_COMMAND} --verbose
    DEPENDS tests
)

# Instalación
include(GNUInstallDirs)

# Instalar biblioteca
install(TARGETS decisionmaker
    EXPORT DecisionMakerTargets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/decisionmaker
)

# Instalar headers manteniendo estructura de directorios
install(DIRECTORY ${SRC_DIR}/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/decisionmaker
    FILES_MATCHING PATTERN "*.h"
)

# Instalar ejemplos (opcional)
install(TARGETS basic_dice simple_decision investment_vs_education
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}/examples
    OPTIONAL
)

# Crear archivo de configuración para find_package
install(EXPORT DecisionMakerTargets
    FILE DecisionMakerTargets.cmake
    NAMESPACE DecisionMaker::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/DecisionMaker
)

# Generar archivo de configuración
include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    DecisionMakerConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY AnyNewerVersion
)

configure_package_config_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/DecisionMakerConfig.cmake.in
    DecisionMakerConfig.cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/DecisionMaker
)

install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/DecisionMakerConfig.cmake
    ${CMAKE_CURRENT_BINARY_DIR}/DecisionMakerConfigVersion.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/DecisionMaker
)

# Target para generar documentación (requiere Doxygen)
find_package(Doxygen QUIET)
if(DOXYGEN_FOUND)
    set(DOXYGEN_IN ${CMAKE_CURRENT_SOURCE_DIR}/docs/Doxyfile.in)
    set(DOXYGEN_OUT ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile)
    
    configure_file(${DOXYGEN_IN} ${DOXYGEN_OUT} @ONLY)
    
    add_custom_target(docs
        COMMAND ${DOXYGEN_EXECUTABLE} ${DOXYGEN_OUT}
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        COMMENT "Generating API documentation with Doxygen"
        VERBATIM
    )
else()
    add_custom_target(docs
        COMMAND ${CMAKE_COMMAND} -E echo "Doxygen not found, cannot generate documentation"
    )
endif()

# Target para formato de código (requiere clang-format)
find_program(CLANG_FORMAT_EXECUTABLE clang-format)
if(CLANG_FORMAT_EXECUTABLE)
    file(GLOB_RECURSE ALL_SOURCE_FILES
        ${SRC_DIR}/*.cpp ${SRC_DIR}/*.h
        ${EXAMPLES_DIR}/*.cpp
        ${TESTS_DIR}/*.cpp
    )
    
    add_custom_target(format
        COMMAND ${CLANG_FORMAT_EXECUTABLE} -i ${ALL_SOURCE_FILES}
        COMMENT "Formatting code with clang-format"
    )
else()
    add_custom_target(format
        COMMAND ${CMAKE_COMMAND} -E echo "clang-format not found, cannot format code"
    )
endif()

# Target para análisis estático (requiere cppcheck)
find_program(CPPCHECK_EXECUTABLE cppcheck)
if(CPPCHECK_EXECUTABLE)
    add_custom_target(analyze
        COMMAND ${CPPCHECK_EXECUTABLE} --enable=all --std=c++17 
                --suppress=missingIncludeSystem ${SRC_DIR}
        COMMENT "Running static analysis with cppcheck"
    )
else()
    add_custom_target(analyze
        COMMAND ${CMAKE_COMMAND} -E echo "cppcheck not found, cannot run analysis"
    )
endif()

# Mostrar información de compilación
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ compiler: ${CMAKE_CXX_COMPILER}")
message(STATUS "C++ flags: ${CMAKE_CXX_FLAGS}")
message(STATUS "C++ flags (Release): ${CMAKE_CXX_FLAGS_RELEASE}")
message(STATUS "C++ flags (Debug): ${CMAKE_CXX_FLAGS_DEBUG}")
message(STATUS "Install prefix: ${CMAKE_INSTALL_PREFIX}")

# Target de ayuda personalizado
add_custom_target(help-custom
    COMMAND ${CMAKE_COMMAND} -E echo ""
    COMMAND ${CMAKE_COMMAND} -E echo "Decision Maker Framework - Targets disponibles:"
    COMMAND ${CMAKE_COMMAND} -E echo ""
    COMMAND ${CMAKE_COMMAND} -E echo "  all              - Construir framework y ejemplos"
    COMMAND ${CMAKE_COMMAND} -E echo "  decisionmaker    - Construir solo la biblioteca"
    COMMAND ${CMAKE_COMMAND} -E echo "  examples         - Construir todos los ejemplos"
    COMMAND ${CMAKE_COMMAND} -E echo "  tests            - Construir todos los tests"
    COMMAND ${CMAKE_COMMAND} -E echo "  run_tests        - Ejecutar todos los tests"
    COMMAND ${CMAKE_COMMAND} -E echo "  docs             - Generar documentación"
    COMMAND ${CMAKE_COMMAND} -E echo "  format           - Formatear código"
    COMMAND ${CMAKE_COMMAND} -E echo "  analyze          - Análisis estático"
    COMMAND ${CMAKE_COMMAND} -E echo "  install          - Instalar framework"
    COMMAND ${CMAKE_COMMAND} -E echo ""
    COMMAND ${CMAKE_COMMAND} -E echo "Ejemplos específicos:"
    COMMAND ${CMAKE_COMMAND} -E echo "  basic_dice                - Ejemplo básico con dados"
    COMMAND ${CMAKE_COMMAND} -E echo "  simple_decision           - Decisión simple (paraguas)"
    COMMAND ${CMAKE_COMMAND} -E echo "  investment_vs_education   - Ejemplo complejo"
    COMMAND ${CMAKE_COMMAND} -E echo ""
    COMMAND ${CMAKE_COMMAND} -E echo "Uso:"
    COMMAND ${CMAKE_COMMAND} -E echo "  mkdir build && cd build"
    COMMAND ${CMAKE_COMMAND} -E echo "  cmake .."
    COMMAND ${CMAKE_COMMAND} -E echo "  make [target]"
    COMMAND ${CMAKE_COMMAND} -E echo ""
)