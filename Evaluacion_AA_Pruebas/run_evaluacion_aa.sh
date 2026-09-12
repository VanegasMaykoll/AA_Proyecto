#!/usr/bin/env bash
# ==============================================================================
# PROYECTO DE ANÁLISIS DE ALGORITMOS (MCC - ESPOL)
# SUITE DE EVALUACIÓN EXPERIMENTAL: ÁRBOL AVL AUMENTADO vs. FUERZA BRUTA & KV
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DATA_DIR="${SCRIPT_DIR}/data"
SRC_DIR="${SCRIPT_DIR}/src"
RESULTS_DIR="${SCRIPT_DIR}/results"
SCRIPTS_DIR="${SCRIPT_DIR}/scripts"

LEVELDB_DIR="${PROJECT_ROOT}/engines/leveldb-1.23"
LEVELDB_LIB="${LEVELDB_DIR}/build/libleveldb.a"

MODE="${1:-10000}"
NUM_RUNS="${2:-50}"

echo "===================================================================="
echo "    EVALUACIÓN EXPERIMENTAL - ANÁLISIS DE ALGORITMOS (ESPOL)"
echo "    Propuesta: Estructuras Aumentadas para Reportes RAP"
echo "===================================================================="

# 1. Verificar LevelDB
if [ ! -f "${LEVELDB_LIB}" ]; then
    echo "[!] Compilando LevelDB 1.23..."
    mkdir -p "${LEVELDB_DIR}/build"
    cmake -S "${LEVELDB_DIR}" -B "${LEVELDB_DIR}/build" -DCMAKE_BUILD_TYPE=Release
    cmake --build "${LEVELDB_DIR}/build" --target leveldb -j$(nproc)
fi

# 2. Compilar binarios de pruebas si no están compilados
echo "\n[*] Compilando componentes C++ (O3 + LevelDB)..."
g++ -std=c++17 -O3 -I"${SRC_DIR}" \
    "${SRC_DIR}/test_correctness.cpp" \
    -o "${SRC_DIR}/test_correctness"

g++ -std=c++17 -O3 -I"${SRC_DIR}" -I"${LEVELDB_DIR}/include" -I"${LEVELDB_DIR}" \
    "${SRC_DIR}/rap_bench.cpp" "${LEVELDB_LIB}" -lpthread -lsnappy \
    -o "${SRC_DIR}/rap_bench"

echo "[✓] Verificando correctitud matemática..."
"${SRC_DIR}/test_correctness"

# Función para ejecutar un experimento individual con tamaño N
run_experiment_for_n() {
    local N="$1"
    local RUNS="$2"
    local DATASET="${DATA_DIR}/rap_reports_${N}.jsonl"
    local METRICS_JSON="${RESULTS_DIR}/rap_metrics_N${N}.json"
    local TXT_SUMMARY="${RESULTS_DIR}/resumen_experimento_N${N}.txt"

    echo ""
    echo "===================================================================="
    echo ">>> INICIANDO EXPERIMENTO PARA ESCALA N = ${N} (Repeticiones: ${RUNS})"
    echo "===================================================================="

    # Generar datos sintéticos si no existen
    if [ ! -f "${DATASET}" ]; then
        echo "[*] Generando dataset sintético de RAP ESPOL para N = ${N}..."
        python3 "${SCRIPTS_DIR}/generate_rap_dataset.py" --n "${N}" --output "${DATASET}"
    else
        echo "[*] Dataset existente detectado: ${DATASET}"
    fi

    # Ejecutar benchmark en C++
    "${SRC_DIR}/rap_bench" \
        --dataset="${DATASET}" \
        --output="${METRICS_JSON}" \
        --runs="${RUNS}"

    # Generar visualizaciones, resumen TXT y Markdown
    python3 "${SCRIPTS_DIR}/plot_results.py" "${METRICS_JSON}" "${RESULTS_DIR}"

    echo "[✓] Resumen de experimento generado: ${TXT_SUMMARY}"
}

# Evaluar según el modo recibido: "multi", "suite", o un número directo N
if [ "${MODE}" = "multi" ] || [ "${MODE}" = "suite" ] || [ "${MODE}" = "all" ]; then
    echo "\n[*] Modo Multi-Escala seleccionado: Ejecutando para N = 1,000, N = 10,000 y N = 50,000..."
    run_experiment_for_n 1000 "${NUM_RUNS}"
    run_experiment_for_n 10000 "${NUM_RUNS}"
    run_experiment_for_n 50000 "${NUM_RUNS}"
else
    # Modo para una escala única especificada por el usuario
    run_experiment_for_n "${MODE}" "${NUM_RUNS}"
fi

echo "\n===================================================================="
echo "    TODAS LAS PRUEBAS FINALIZARON CON ÉXITO"
echo "===================================================================="
echo "Archivos TXT de resumen disponibles en: ${RESULTS_DIR}/resumen_experimento_N*.txt"
echo "===================================================================="
