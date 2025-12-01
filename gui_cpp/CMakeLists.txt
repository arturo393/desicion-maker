cmake_minimum_required(VERSION 3.16)
project(DecisionMakerQt)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Qt6 packages
find_package(Qt6 REQUIRED COMPONENTS Core Widgets)

# Enable Qt6 MOC
set(CMAKE_AUTOMOC ON)

# Add executable
add_executable(qt_gui qt_gui_minimal.cpp)

# Link Qt libraries
target_link_libraries(qt_gui Qt6::Core Qt6::Widgets)

# macOS specific settings
if(APPLE)
    set_target_properties(qt_gui PROPERTIES
        MACOSX_BUNDLE TRUE
        MACOSX_BUNDLE_GUI_IDENTIFIER com.decisionmaker.app
        MACOSX_BUNDLE_BUNDLE_NAME "Decision Maker"
    )
endif()