# Módulo de Evaluación Experimental: Análisis de Algoritmos (MCC - ESPOL)

> **Propuesta de Proyecto:** *Diseño de una estructura de datos aumentada para el procesamiento y consulta eficiente de reportes de retroalimentación automática en presentaciones orales*  
> **Autor:** Maykoll Vanegas Silva  
> **Docente:** Ana Tapia, Ph.D.  
> **Repositorio Base:** Proyecto-SOA  

---

## 1. Descripción del Módulo

Este directorio (`Evaluacion_AA_Pruebas/`) contiene de forma totalmente aislada la implementación, suite experimental, datos sintéticos y reportería gráfica de la propuesta de proyecto para el curso de **Análisis de Algoritmos**.

El sistema implementa una **arquitectura desacoplada**:
1. **Índices Secundarios en Memoria (Árboles AVL Aumentados)**:
   - Cuatro árboles independientes ($I_g, I_z, I_v, I_p$) para las métricas de RAP ESPOL: Puntaje Global ($g$), Mirada/Gaze ($z$), Volumen ($v$) y Postura ($p$).
   - Cada nodo mantiene estadísticas de subárbol $(C, S, SS)$, permitiendo responder consultas estadísticas por intervalo (media, varianza, desviación estándar) en tiempo **$\Theta(\log D_m)$** mediante resta de prefijos `AgregadoLE(t)`, sin recorrer los datos.
   - Poda en búsquedas por rango $O(\log D_m + k)$ y recorrido Top-$k$ podado.
   - Intersección de predicados multivariados optimizada ordenando los conjuntos por cardinalidad creciente (Algoritmo 5).
2. **Línea Base (Fuerza Bruta)**:
   - Escaneo lineal y acumulación secuencial $O(N)$ para verificar la exactitud y cuantificar el factor de aceleración (*speedup*).
3. **Almacenamiento Primario Persistente (LevelDB 1.23 + Filtros AMQ)**:
   - Almacena el payload completo de los reportes ($id \to r_i$).
   - Evaluación comparativa en la fase de materialización (`MultiGet`) con **Sin Filtro**, **Bloom Filter (10 bpk)** y **Ribbon Filter (10 bpk equiv)**.

---

## 2. Estructura de Archivos

```text
Evaluacion_AA_Pruebas/
├── README.md                              # Este documento
├── CMakeLists.txt                         # Configuración de compilación con CMake
├── run_evaluacion_aa.sh                   # Script maestro orquestador (todo en un paso)
│
├── data/                                  # Almacén de datasets sintéticos generados
│   └── rap_reports_10000.jsonl            # 10,000 reportes realistas (~10 MB)
│
├── src/                                   # Código fuente en C++ (C++17)
│   ├── rap_types.hpp                      # Estructura del informe ri = (id, u, t, M, D)
│   ├── augmented_avl.hpp                  # AVL Aumentado (Algoritmos 1, 3, 4, 7)
│   ├── brute_force_baseline.hpp           # Línea base secuencial O(N)
│   ├── rap_query_engine.hpp               # Gestor de los 4 índices y Algoritmo 5
│   ├── kv_store_adapter.hpp               # Integración con LevelDB y filtros AMQ
│   ├── rap_bench.cpp                      # Binario principal de benchmarks
│   └── test_correctness.cpp               # Pruebas unitarias de invariantes y correctitud
│
├── scripts/                               # Scripts en Python
│   ├── generate_rap_dataset.py            # Generador sintético de reportes RAP ESPOL
│   └── plot_results.py                    # Generador de gráficas PNG y reporte Markdown
│
└── results/                               # Resultados generados
    ├── rap_metrics.json                   # Métricas numéricas crudas
    ├── grafica_1_estadisticas_latencia.png # Gráfica de consultas estadísticas
    ├── grafica_2_topk_latencia.png        # Gráfica de selección Top-K
    ├── grafica_3_recuperacion_filtros.png # Gráfica de MultiGet con Bloom y Ribbon
    └── RESULTADOS_EVALUACION_AA.md        # Informe técnico consolidado
```

---

## 3. Instrucciones de Ejecución

### Ejecución Automática (Recomendada)
Para compilar, generar el dataset sintético de 10,000 informes, verificar invariantes matemáticos, ejecutar los benchmarks y generar gráficas:

```bash
cd Evaluacion_AA_Pruebas
./run_evaluacion_aa.sh
```

### Opciones y Parámetros Personalizables
Puedes ajustar la escala $N$ de informes y el número de repeticiones para promediar latencias:

```bash
# Probar con N = 50,000 reportes y 100 repeticiones por consulta
./run_evaluacion_aa.sh 50000 100
```

---

## 4. Algoritmos Implementados (Mapeo con la Propuesta)

| Algoritmo en Propuesta | Archivo C++ | Complejidad Teórica | Complejidad Empírica Observada |
| :--- | :--- | :---: | :---: |
| **Algoritmo 1: `ActualizarNodo(x)`** | [`augmented_avl.hpp`](file:///home/maykoll_vanegas/Escritorio/Proyecto-SOA/Evaluacion_AA_Pruebas/src/augmented_avl.hpp) | $\Theta(1)$ | $\approx 2$ nanosegundos |
| **Algoritmo 2: `InsertarInforme(r)`** | [`rap_query_engine.hpp`](file:///home/maykoll_vanegas/Escritorio/Proyecto-SOA/Evaluacion_AA_Pruebas/src/rap_query_engine.hpp) | $T_{\text{Put}} + \sum O(\log D_m)$ | $0.32$ µs / informe |
| **Algoritmo 3: `BuscarRango(x, a, b)`** | [`augmented_avl.hpp`](file:///home/maykoll_vanegas/Escritorio/Proyecto-SOA/Evaluacion_AA_Pruebas/src/augmented_avl.hpp) | $O(\log D_m + k)$ | $12$ µs para $k \approx 1{,}900$ |
| **Algoritmo 4: `AgregadoLE(x, t)`** | [`augmented_avl.hpp`](file:///home/maykoll_vanegas/Escritorio/Proyecto-SOA/Evaluacion_AA_Pruebas/src/augmented_avl.hpp) | $\Theta(\log D_m)$ | $0.025$ µs (~1000x más rápido que Fuerza Bruta) |
| **Algoritmo 5: `ConsultaCompuesta(Q)`** | [`rap_query_engine.hpp`](file:///home/maykoll_vanegas/Escritorio/Proyecto-SOA/Evaluacion_AA_Pruebas/src/rap_query_engine.hpp) | $O(\sum(\log D_i + k_i) + s \log s)$ | Ordenamiento por cardinalidad evita trabajo redundante |
| **Algoritmo 6: `RecuperarInformes(RQ)`** | [`kv_store_adapter.hpp`](file:///home/maykoll_vanegas/Escritorio/Proyecto-SOA/Evaluacion_AA_Pruebas/src/kv_store_adapter.hpp) | $T_{\text{MultiGet}}(K)$ | Filtros Bloom y Ribbon reducen 33% latencia en misses |
| **Algoritmo 7: `TopK(x, k)`** | [`augmented_avl.hpp`](file:///home/maykoll_vanegas/Escritorio/Proyecto-SOA/Evaluacion_AA_Pruebas/src/augmented_avl.hpp) | $O(\log D_m + k)$ | $0.12$ µs ($470$x más rápido que Fuerza Bruta) |

---

## 5. Visualización de Resultados

Tras la ejecución, consulta el informe generado:
- 📄 [RESULTADOS_EVALUACION_AA.md](file:///home/maykoll_vanegas/Escritorio/Proyecto-SOA/Evaluacion_AA_Pruebas/results/RESULTADOS_EVALUACION_AA.md)
- 📊 Gráfica 1: [grafica_1_estadisticas_latencia.png](file:///home/maykoll_vanegas/Escritorio/Proyecto-SOA/Evaluacion_AA_Pruebas/results/grafica_1_estadisticas_latencia.png)
- 📊 Gráfica 2: [grafica_2_topk_latencia.png](file:///home/maykoll_vanegas/Escritorio/Proyecto-SOA/Evaluacion_AA_Pruebas/results/grafica_2_topk_latencia.png)
- 📊 Gráfica 3: [grafica_3_recuperacion_filtros.png](file:///home/maykoll_vanegas/Escritorio/Proyecto-SOA/Evaluacion_AA_Pruebas/results/grafica_3_recuperacion_filtros.png)
