#!/usr/bin/env bash
# ==============================================================================
# PROYECTO DE ANÁLISIS DE ALGORITMOS (MCC - ESPOL)
# Script de Ejecución Rápida de Benchmarks y Evaluación Experimental
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/Evaluacion_AA_Pruebas"

# Por defecto ejecuta la suite multi-escala (N = 1000, 10000, 50000)
MODE="${1:-multi}"
RUNS="${2:-50}"

./run_evaluacion_aa.sh "${MODE}" "${RUNS}"
