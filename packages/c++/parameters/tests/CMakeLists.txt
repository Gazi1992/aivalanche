add_executable(test_transforms test_transforms.cpp)
target_link_libraries(test_transforms PRIVATE parameters_lib GTest::gtest_main)
add_test(NAME test_transforms COMMAND test_transforms)

add_executable(test_parameters test_parameters.cpp)
target_link_libraries(test_parameters PRIVATE parameters_lib GTest::gtest_main)
add_test(NAME test_parameters COMMAND test_parameters)
