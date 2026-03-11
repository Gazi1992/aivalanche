add_executable(test_de test_de.cpp)
target_link_libraries(test_de PRIVATE optimization_lib GTest::gtest_main)
add_test(NAME test_de COMMAND test_de)
