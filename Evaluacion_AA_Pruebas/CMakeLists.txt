cmake_minimum_required(VERSION 3.16)
project(Evaluacion_AA_Pruebas CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -Wall -Wextra")

set(LEVELDB_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../engines/leveldb-1.23")
include_directories(
    "${CMAKE_CURRENT_SOURCE_DIR}/src"
    "${LEVELDB_ROOT}/include"
    "${LEVELDB_ROOT}"
)

find_package(Threads REQUIRED)
find_package(Snappy)

# Test de correctitud e invariantes
add_executable(test_correctness src/test_correctness.cpp)

# Benchmark experimental integrado con LevelDB
add_executable(rap_bench src/rap_bench.cpp)
target_link_libraries(rap_bench PRIVATE
    "${LEVELDB_ROOT}/build/libleveldb.a"
    Threads::Threads
    snappy
)
