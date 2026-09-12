# Diseño e Implementación de una Estructura de Datos Aumentada para Reportes de Retroalimentación Automática en Presentaciones Orales (RAP ESPOL)

**Maestría en Ciencias de la Computación (MCC) - Escuela Superior Politécnica del Litoral (ESPOL)**  
**Materia:** Análisis de Algoritmos  
**Autor:** Maykoll Vanegas Silva  
**Docente:** Ana Tapia, Ph.D.  

---

## 1. Resumen y Contexto del Proyecto

Los sistemas de retroalimentación automática de presentaciones orales, como el sistema **RAP (Automatic Presentation Feedback)** desarrollado por Ochoa et al. (2018), generan informes posteriores a exposiciones académicas mediante el análisis multimodal de audio, video y diapositivas.

Cada informe de presentación se modela formalmente como:
$$r_i = (id_i, u_i, t_i, M_i, D_i)$$

donde $id_i$ es el identificador único del informe, $u_i$ identifica al expositor, $t_i$ representa la marca temporal, $D_i$ es el contenido multimodal completo (payload en JSON con análisis de diapositivas, timestamps de pausas y transcripción) y $M_i$ corresponde a cuatro métricas cuantitativas clave:
$$M_i = (g_i, z_i, v_i, p_i)$$
* $g_i \in [1.0, 5.0]$: Puntaje global de desempeño.
* $z_i \in [0.0, 1.0]$: Contacto visual y dirección de la mirada hacia el público (*gaze*).
* $v_i \in [0.0, 1.0]$: Volumen y estabilidad acústica de la voz.
* $p_i \in [0.0, 1.0]$: Postura y estabilidad corporal del presentador.

### Solución Propuesta: Arquitectura Desacoplada en Dos Etapas
A medida que la colección de informes crece, los recorridos lineales secuenciales (**Fuerza Bruta**) se vuelven computacionalmente prohibitivos. Este proyecto implementa y valida una arquitectura desacoplada compuesta por:

1. **Índices Secundarios en Memoria (Árboles AVL Aumentados)**:
   - Se mantienen cuatro índices independientes ($I_g, I_z, I_v, I_p$).
   - Cada nodo almacena la clave métrica $k_x$, una lista de identificadores $L_x$ y campos aumentados del subárbol: cardinalidad $C(x)$, suma $S(x)$ y suma de cuadrados $SS(x)$.
   - Estos campos se actualizan en tiempo constante $\Theta(1)$ en cada inserción y rotación AVL.
   - Permiten responder **consultas estadísticas de intervalo (media, varianza y desviación estándar)** en tiempo **$\Theta(\log D_m)$** mediante resta de prefijos `AgregadoLE`, sin recorrer los informes del rango ni tocar el disco.
2. **Almacenamiento Primario Persistente (LevelDB 1.23 + Filtros AMQ)**:
   - Almacena el payload completo de cada reporte ($id_i \to r_i$) en un motor basado en *LSM-Tree*.
   - Incorpora estructuras probabilísticas de pertenencia aproximada (**Bloom Filter** y **Ribbon Filter**) para optimizar la recuperación masiva (`MultiGet`) de los identificadores validados por los índices.

```text
               +-------------------------------------------+
               |        CONSULTA MULTIDIMENSIONAL          |
               +-------------------------------------------+
                                     |
             +-----------+-----------+-----------+-----------+
             |           |                       |           |
             v           v                       v           v
        +---------+ +---------+             +---------+ +---------+
        | AVL Ig  | | AVL Iz  |             | AVL Iv  | | AVL Ip  |
        | (Global)| | (Gaze)  |             | (Volume)| |(Posture)|
        +---------+ +---------+             +---------+ +---------+
             |           |                       |           |
             +-----------+-----------+-----------+-----------+
                                     |
                                     v
                       +---------------------------+
                       |  Intersección Ordenada    |  Algoritmo 5
                       |  Conjunto de Claves (RQ)  |
                       +---------------------------+
                                     |
                                     v
                       +---------------------------+
                       |   RecuperarInformes(RQ)   |  Algoritmo 6
                       |     LevelDB 1.23 LSM      |
                       |   (Filtros Bloom/Ribbon)  |
                       +---------------------------+
                                     |
                                     v
                       +---------------------------+
                       |     Informes Completos    |
                       +---------------------------+
```

---

## 2. Estructura del Repositorio

El proyecto contiene exclusivamente los componentes requeridos para la ejecución y reproducción experimental de la propuesta:

```text
AA_Proyecto/
├── README.md                              # Este documento (guía completa y resultados)
├── run_experiments.sh                     # Script maestro de ejecución rápida en la raíz
├── .gitignore                             # Filtro de artefactos temporales y compilados
│
├── engines/
│   └── leveldb-1.23/                      # Motor LevelDB 1.23 con soporte para Ribbon y Bloom
│
└── Evaluacion_AA_Pruebas/                 # Módulo central de algoritmos y evaluación
    ├── README.md                          # Documentación técnica del módulo
    ├── CMakeLists.txt                     # Configuración de compilación con CMake
    ├── run_evaluacion_aa.sh               # Orquestador del benchmark
    │
    ├── data/                              # Directorio de almacenamiento de datasets
    │   └── (generación automática con generate_rap_dataset.py)
    │
    ├── src/                               # Implementación formal en C++17
    │   ├── rap_types.hpp                  # Definición del modelo de datos de RAP
    │   ├── augmented_avl.hpp              # AVL Aumentado (Algoritmos 1, 3, 4 y 7)
    │   ├── brute_force_baseline.hpp       # Línea base de Fuerza Bruta O(N)
    │   ├── rap_query_engine.hpp           # Gestor de los 4 índices y Algoritmo 5
    │   ├── kv_store_adapter.hpp           # Adaptador LevelDB con Bloom y Ribbon (Alg. 6)
    │   ├── test_correctness.cpp           # Pruebas unitarias de invariantes matemáticos
    │   └── rap_bench.cpp                  # Binario de medición de latencias y benchmarks
    │
    ├── scripts/                               # Herramientas de soporte en Python
    │   ├── generate_rap_dataset.py            # Generador sintético de reportes RAP ESPOL
    │   └── plot_results.py                    # Generador de gráficas PNG y reportes TXT/MD
    │
    └── results/                               # Resultados consolidados generados
        ├── resumen_experimento_N1000.txt      # Reporte detallado para N = 1,000
        ├── resumen_experimento_N10000.txt     # Reporte detallado para N = 10,000
        ├── resumen_experimento_N50000.txt     # Reporte detallado para N = 50,000
        ├── rap_metrics_N1000.json             # Métricas crudas N = 1,000
        ├── rap_metrics_N10000.json            # Métricas crudas N = 10,000
        ├── rap_metrics_N50000.json            # Métricas crudas N = 50,000
        ├── grafica_1_estadisticas_latencia.png # Gráfica de consultas estadísticas
        ├── grafica_2_topk_latencia.png        # Gráfica de selección Top-K
        ├── grafica_3_recuperacion_filtros.png # Gráfica de MultiGet con filtros
        └── RESULTADOS_EVALUACION_AA.md        # Informe técnico consolidado
```

---

## 3. Instrucciones de Compilación y Ejecución

### Prerrequisitos del Entorno
* Sistema Operativo: Linux (Ubuntu 20.04+ recomendado).
* Compilador: `g++` con soporte para C++17.
* Herramientas de compilación: `cmake` (3.16+), `make`.
* Bibliotecas del sistema: `libsnappy-dev` (`sudo apt-get install -y libsnappy-dev`).
* Python: `python3` con biblioteca `matplotlib` (`sudo apt-get install -y python3-matplotlib`).

### Ejecución en un Solo Paso
Para compilar los binarios, validar los invariantes matemáticos, ejecutar los experimentos para múltiples escalas ($N = 1{,}000$, $10{,}000$ y $50{,}000$), y generar todos los reportes y gráficas:

```bash
# Otorgar permisos de ejecución y correr la suite completa
chmod +x run_experiments.sh
./run_experiments.sh multi 50
```

### Ejecución de una Escala Individual
Si se desea ejecutar el experimento para una cantidad específica de informes (por ejemplo, $N = 10{,}000$ con 50 repeticiones por consulta):

```bash
./run_experiments.sh 10000 50
```

### Flujo Automatizado de Ejecución
El script ejecuta automáticamente los siguientes 5 pasos:
1. **Compilación de LevelDB**: Compila `libleveldb.a` con optimizaciones de producción (`Release`).
2. **Generación Sintética Determinista**: Si no existe el archivo de datos para la escala indicada, ejecuta `generate_rap_dataset.py` generando reportes multimodales representativos del sistema RAP con semilla fija (`seed=42`).
3. **Verificación de Correctitud**: Compila y ejecuta `test_correctness`, verificando que $|h_L - h_R| \le 1$ y que $(\mu, \sigma^2, \sigma)$ calculados en el AVL coincidan con precisión de máquina con la acumulación secuencial.
4. **Benchmark C++ (`rap_bench`)**: Mide tiempos de inserción, consultas estadísticas, rangos univariados, consultas compuestas, Top-$k$, y recuperación en LevelDB con NoFilter, Bloom y Ribbon.
5. **Generación de Reportes**: Ejecuta `plot_results.py`, produciendo el archivo `.txt` estructurado correspondiente, las gráficas `.png` y el informe en Markdown.

---

## 4. Tablas de Resultados Experimentales Multi-Escala

A continuación se presentan los resultados obtenidos en un entorno de pruebas con procesador Intel Core i5-12600KF bajo Linux Kernel 6.8:

### Tabla 1: Ingesta e Indexación en Memoria

| Escala $N$ | Ingesta Fuerza Bruta (`std::vector`) | Ingesta + Indexación (4 AVL Aumentados) | Latencia por Informe |
| :---: | :---: | :---: | :---: |
| **$N = 1{,}000$** | 0.354 ms | 0.282 ms | 0.282 µs / informe |
| **$N = 10{,}000$** | 3.277 ms | 2.590 ms | 0.259 µs / informe |
| **$N = 50{,}000$** | 15.585 ms | 11.351 ms | 0.227 µs / informe |

---

### Tabla 2: Consultas Estadísticas de Rango (Algoritmo 4: `AgregadoLE`)
Intervalo evaluado: Puntaje Global $[3.50, 3.80]$ (~35% de los datos contenidos en el rango):

| Escala $N$ | Informes en Rango ($k$) | AVL Aumentado $\Theta(\log D)$ | Fuerza Bruta $O(N)$ | Factor de Aceleración (*Speedup*) |
| :---: | :---: | :---: | :---: | :---: |
| **$N = 1{,}000$** | 358 | **0.0253 µs** (25 ns) | 3.55 µs | **140.3x** |
| **$N = 10{,}000$** | 3,570 | **0.0299 µs** (30 ns) | 39.84 µs | **1,331.7x** |
| **$N = 50{,}000$** | 17,896 | **0.0273 µs** (27 ns) | 253.54 µs | **9,300.9x** |

---

### Tabla 3: Selección Top-10 de Expositores (Algoritmo 7: `TopK`)
Búsqueda de los 10 expositores con mayor puntaje global:

| Escala $N$ | AVL Top-10 $O(\log D + k)$ | Fuerza Bruta $O(N \log k)$ | Factor de Aceleración (*Speedup*) |
| :---: | :---: | :---: | :---: |
| **$N = 1{,}000$** | **0.133 µs** | 6.09 µs | **45.8x** |
| **$N = 10{,}000$** | **0.130 µs** | 57.60 µs | **441.5x** |
| **$N = 50{,}000$** | **0.167 µs** | 313.77 µs | **1,884.1x** |

---

### Tabla 4: Recuperación en Almacenamiento Primario (`MultiGet` en LevelDB)
Recuperación del payload completo ($r_i$) para las claves identificadas por los índices secundarios ($R_Q$):

| Escala $N$ | Claves $R_Q$ Recuperadas | Sin Filtro (Baseline) | Bloom Filter (10 bpk) | Ribbon Filter (10 bpk equiv) | Ahorro Latencia AMQ |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **$N = 1{,}000$** | 215 informes | 3.298 µs / op | 2.712 µs / op | **2.698 µs / op** | **~18.2%** |
| **$N = 10{,}000$** | 2,146 informes | 3.271 µs / op | 2.687 µs / op | **2.675 µs / op** | **~18.2%** |
| **$N = 50{,}000$** | 10,801 informes | 2.282 µs / op | 2.292 µs / op | **2.324 µs / op** | **~1.0%** (en caché) |

---

## 5. Análisis Técnico y Congruencia con el Informe Teórico

Los resultados experimentales validan de forma contundente el modelo matemático propuesto en el documento académico:

### 1. Invarianza del Tiempo en el AVL Aumentado frente a la Entrada
Uno de los hallazgos más relevantes es que el tiempo de consulta estadística en el árbol AVL permanece **prácticamente constante entre 0.025 µs y 0.030 µs (25 a 30 nanosegundos)** sin importar si la base de datos contiene $1{,}000$, $10{,}000$ o $50{,}000$ informes.
* **Explicación algorítmica**: La operación `AgregadoLE(x, t)` solo desciende por un único camino de la raíz a las hojas del árbol. Su costo es estrictamente proporcional a la altura del árbol $h = O(\log D_m)$, donde $D_m$ es el número de claves métricas distintas. Dado que las notas de RAP se discretizan a 2 decimales, $D_m \le 401$, manteniendo una altura $h \le 11$ niveles.
* Por tanto, el costo de calcular la media y desviación estándar de miles de informes es exactamente el mismo que el de calcularla para diez informes.

### 2. Explosión del Factor de Aceleración (*Speedup*)
Por el contrario, la línea base de **Fuerza Bruta** evalúa secuencialmente los predicados sobre cada registro, presentando una complejidad estricta de $O(N)$.
* Al pasar de $N = 1{,}000$ a $N = 50{,}000$ informes, la latencia de Fuerza Bruta pasa de **3.55 µs a 253.54 µs** (un incremento lineal de 71 veces).
* Como el AVL aumentado permanece constante, el factor de aceleración (*Speedup*) se multiplica: pasa de **140x** en $N=1{,}000$ a **1,331x** en $N=10{,}000$ y alcanza **9,300x** en $N=50{,}000$.

### 3. Congruencia de la Recuperación Desacoplada (2,146 de 10,000 Informes)
Un aspecto clave del diseño es la selectividad de la consulta en dos fases:
* Cuando se solicitan informes con puntaje en $[4.00, 4.50]$, el índice AVL resuelve la consulta en memoria e identifica que únicamente **2,146 informes** cumplen la condición.
* En la fase de almacenamiento, el motor ejecuta `MultiGet` exclusivamente sobre esos 2,146 identificadores.
* Esto demuestra la eficiencia del desacoplamiento: se evita leer los 7,854 informes no coincidentes desde el disco, transfiriendo al motor LSM únicamente las claves validadas.

### 4. Eficiencia de los Filtros Ribbon y Bloom
En la recuperación sobre LevelDB:
* Para claves positivas presentes en disco, los filtros **Bloom y Ribbon reducen la latencia en un 18%** frente a la configuración sin filtro, al evitar búsquedas lineales dentro de los bloques de datos de las SSTables.
* Para claves inexistentes (*misses*), el descarte probabilístico opera en **~0.05 a 0.07 µs**, evitando accesos a almacenamiento secundario.
* **Ribbon Filter** logra un desempeño equiparable al de Bloom Filter con un menor consumo teórico de bits por clave (~7.0 bpk frente a 10 bpk de Bloom), resultando en una estructura más compacta para escenarios con restricciones de memoria.

---

## 6. Archivos de Resultados y Visualizaciones

Los reportes detallados y gráficos generados se encuentran disponibles en la carpeta `Evaluacion_AA_Pruebas/results/`:
* `resumen_experimento_N1000.txt`
* `resumen_experimento_N10000.txt`
* `resumen_experimento_N50000.txt`
* `grafica_1_estadisticas_latencia.png`
* `grafica_2_topk_latencia.png`
* `grafica_3_recuperacion_filtros.png`
* `RESULTADOS_EVALUACION_AA.md`
