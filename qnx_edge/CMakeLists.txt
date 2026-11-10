cmake_minimum_required(VERSION 3.12)
project(MedOrqisQNX VERSION 1.0.0 LANGUAGES C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

add_definitions(-D_POSIX_C_SOURCE=200809L)

include_directories(include)

# Core library
add_library(medorqis_qnx_core STATIC
    src/news2_deterministic.c
    src/patient_simulator.c
    src/vitals_acq.c
    src/vitals_resmgr.c
)
find_package(Threads REQUIRED)
target_link_libraries(medorqis_qnx_core PUBLIC Threads::Threads)

# Unit test executable
add_executable(test_news2_deterministic
    tests/test_news2_deterministic.c
    src/news2_deterministic.c
)
target_link_libraries(test_news2_deterministic PRIVATE Threads::Threads)

# Bedside Monitor executable
add_executable(medorqis_qnx_monitor
    src/qnx_monitor_main.c
)
target_link_libraries(medorqis_qnx_monitor PRIVATE medorqis_qnx_core Threads::Threads)

enable_testing()
add_test(NAME TestNEWS2Deterministic COMMAND test_news2_deterministic)
