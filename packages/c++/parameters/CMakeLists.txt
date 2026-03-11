add_library(parameters_lib
    src/parameters_lib.cpp
)

target_include_directories(parameters_lib PUBLIC include)
target_link_libraries(parameters_lib PUBLIC Eigen3::Eigen)
