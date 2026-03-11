add_library(optimization_lib
    src/differential_evolution.cpp
)

target_include_directories(optimization_lib PUBLIC include)
target_link_libraries(optimization_lib PUBLIC parameters_lib Eigen3::Eigen)
