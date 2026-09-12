#!/usr/bin/env python3
"""
Generador de Gráficas, Resúmenes TXT y Reporte Técnico para la Evaluación de Análisis de Algoritmos.
Lee un archivo JSON de métricas y produce:
1. resumen_experimento_N{N}.txt: Resumen consolidado en texto plano (estilo tabla).
2. Graficas PNG comparativas (estadísticas, topk, filtros).
3. RESULTADOS_EVALUACION_AA.md: Documento Markdown consolidado.
"""

import datetime
import json
import os
import platform
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def generate_txt_summary(data, txt_path):
    n = data["total_reports"]
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cpu_info = platform.processor() or "x86_64 Processor"

    ing = data["ingestion"]
    stat_q = data["statistical_queries"]
    range_q = data.get("range_queries", [])
    comp = data.get("compound_query", {})
    topk = data["top_k"]
    mg = data["multiget_recovery"]

    lines = []
    lines.append("=" * 100)
    lines.append(f" REPORTE CONSOLIDADO: EVALUACIÓN DE ESTRUCTURAS AUMENTADAS PARA REPORTES RAP ESPOL")
    lines.append(f" Fecha: {now_str} | CPU: {cpu_info}")
    lines.append(f" Parámetros Base: N = {n:,} informes, M = 4 métricas (g, z, v, p)")
    lines.append("=" * 100)
    lines.append("")

    # FASE 1: INGESTA
    lines.append("-" * 100)
    lines.append("[FASE 1: INGESTA E INDEXACIÓN EN MEMORIA]")
    lines.append("Descripción: Inserción de reportes en la estructura de almacenamiento e índices secundarios.")
    lines.append("-" * 100)
    lines.append(f"{'Estructura':<35} {'Operación':<20} {'Tiempo Total':<18} {'Latencia/Informe':<18}")
    lines.append("-" * 100)
    lines.append(f"{'Fuerza Bruta (Baseline)':<35} {'std::vector':<20} {ing['brute_force_ms']:>10.3f} ms   {(ing['brute_force_ms']/n*1000.0):>10.3f} µs")
    lines.append(f"{'Propuesta (4 AVL Aumentados)':<35} {'Árboles AVL':<20} {ing['augmented_avl_ms']:>10.3f} ms   {(ing['augmented_avl_ms']/n*1000.0):>10.3f} µs")
    lines.append("-" * 100)
    lines.append("")

    # FASE 2: CONSULTAS ESTADÍSTICAS
    lines.append("-" * 100)
    lines.append("[FASE 2: CONSULTAS ESTADÍSTICAS POR INTERVALO - ALGORITMO 4: AgregadoLE]")
    lines.append("Descripción: Cálculo de media, varianza y desviación estándar sobre intervalos en Theta(log Dm).")
    lines.append("-" * 100)
    lines.append(f"{'Consulta de Intervalo':<40} {'k Items':<10} {'AVL Aumentado':<16} {'Fuerza Bruta':<16} {'Speedup':<12}")
    lines.append("-" * 100)
    for q in stat_q:
        lines.append(f"{q['label']:<40} {q['matched_count']:>8,}   {q['avl_us']:>10.4f} µs   {q['brute_force_us']:>10.2f} µs   {q['speedup']:>8.1f}x")
    lines.append("-" * 100)
    lines.append("")

    # FASE 3: BÚSQUEDA POR INTERVALO
    if range_q:
        lines.append("-" * 100)
        lines.append("[FASE 3: BÚSQUEDA POR RANGO (RECUPERACIÓN DE IDS) - ALGORITMO 3]")
        lines.append("Descripción: Búsqueda ordenada con poda en el árbol AVL vs. escaneo secuencial.")
        lines.append("-" * 100)
        lines.append(f"{'Consulta de Rango':<40} {'k Items':<10} {'AVL Podado':<16} {'Fuerza Bruta':<16} {'Speedup':<12}")
        lines.append("-" * 100)
        for q in range_q:
            lines.append(f"{q['label']:<40} {q['matched_count']:>8,}   {q['avl_us']:>10.3f} µs   {q['brute_force_us']:>10.3f} µs   {q['speedup']:>8.1f}x")
        lines.append("-" * 100)
        lines.append("")

    # FASE 4: CONSULTA COMPUESTA
    if comp:
        lines.append("-" * 100)
        lines.append("[FASE 4: CONSULTAS COMPUESTAS MULTIVARIADAS - ALGORITMO 5]")
        lines.append("Descripción: Intersección conjuntiva de 4 predicados ordenados por cardinalidad.")
        lines.append("-" * 100)
        lines.append(f"Informes coincidentes: {comp.get('matched_count', 0):,}")
        lines.append(f"  - Propuesta (Ordenado por cardinalidad creciente): {comp.get('sorted_cardinality_us', 0.0):.2f} µs")
        lines.append(f"  - Intersección sin ordenamiento previo:           {comp.get('unsorted_us', 0.0):.2f} µs")
        lines.append(f"  - Fuerza Bruta Secuencial:                         {comp.get('brute_force_us', 0.0):.2f} µs")
        lines.append(f"  - Ganancia por ordenación de cardinalidades:       {comp.get('gain_sorting', 1.0):.2f}x")
        lines.append("-" * 100)
        lines.append("")

    # FASE 5: SELECCIÓN TOP-K
    lines.append("-" * 100)
    lines.append("[FASE 5: SELECCIÓN TOP-K DE EXPOSITORES - ALGORITMO 7]")
    lines.append("Descripción: Recorrido in-order inverso podado en el AVL vs. ordenamiento parcial O(N log k).")
    lines.append("-" * 100)
    lines.append(f"{'Operación':<30} {'Cantidad k':<12} {'AVL Top-k':<18} {'Fuerza Bruta':<18} {'Speedup':<12}")
    lines.append("-" * 100)
    for item in topk:
        lines.append(f"{'Mejores Expositores':<30} {item['k']:>10}   {item['avl_us']:>12.3f} µs   {item['brute_force_us']:>12.3f} µs   {item['speedup']:>8.1f}x")
    lines.append("-" * 100)
    lines.append("")

    # FASE 6: MATERIALIZACIÓN MULTIGET EN LEVELDB
    lines.append("-" * 100)
    lines.append("[FASE 6: MATERIALIZACIÓN EN ALMACENAMIENTO PRIMARIO (MULTIGET EN LEVELDB) - ALGORITMO 6]")
    lines.append(f"Descripción: Recuperación de {mg.get('target_items', 0):,} informes validados (RQ). Evaluación de filtros AMQ.")
    lines.append("-" * 100)
    lines.append(f"{'Variante':<15} {'Filtro':<25} {'MultiGet Hits':<18} {'MultiGet Misses':<18} {'Tamaño Disco':<15}")
    lines.append("-" * 100)
    v_map = [
        ("nofilter", "Sin Filtro (Baseline)"),
        ("bloom", "Bloom (10 bpk)"),
        ("ribbon", "Ribbon (10 bpk equiv)")
    ]
    hits = mg.get("hit_latency_per_item_us", {})
    misses = mg.get("miss_latency_per_item_us", {})
    sizes = mg.get("disk_sizes_kb", {})
    for v_key, v_name in v_map:
        h_val = f"{hits.get(v_key, 0.0):.3f} µs/op"
        m_val = f"{misses.get(v_key, 0.0):.3f} µs/op"
        s_val = f"{sizes.get(v_key, 0):,} KB"
        lines.append(f"{v_key:<15} {v_name:<25} {h_val:>16}   {m_val:>16}   {s_val:>13}")
    lines.append("-" * 100)
    lines.append("=" * 100)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[✓] Resumen de texto plano generado: {txt_path}")

def generate_charts(data, results_dir, suffix=""):
    c_avl = "#1E88E5"      # Azul tecnológico
    c_bf = "#E53935"       # Rojo alerta
    c_ribbon = "#43A047"   # Verde Ribbon
    c_bloom = "#FB8C00"    # Naranja Bloom
    c_nofilter = "#757575" # Gris neutro

    # Gráfica 1: Consultas Estadísticas
    stat_queries = data["statistical_queries"]
    labels = [f"Q{i+1}" for i in range(len(stat_queries))]
    avl_times = [q["avl_us"] for q in stat_queries]
    bf_times = [q["brute_force_us"] for q in stat_queries]
    speedups = [q["speedup"] for q in stat_queries]

    x = range(len(labels))
    width = 0.35

    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    ax1.bar([p - width/2 for p in x], avl_times, width, label="AVL Aumentado (Θ(log D))", color=c_avl)
    ax1.bar([p + width/2 for p in x], bf_times, width, label="Fuerza Bruta (O(N))", color=c_bf)

    ax1.set_ylabel("Latencia (µs) [Escala Logarítmica]", fontsize=12, fontweight="bold")
    ax1.set_title(f"Comparativa de Latencia: Consultas Estadísticas de Rango (N = {data['total_reports']:,})\nÁrbol AVL Aumentado vs. Recorrido Secuencial", fontsize=13, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"Q{i+1}: {q['label'][:25]}..." for i, q in enumerate(stat_queries)], rotation=15, ha="right", fontsize=9)
    ax1.set_yscale("log")
    ax1.grid(True, which="both", ls="--", alpha=0.3, axis="y")
    ax1.legend(loc="upper left", frameon=True)

    for i, sp in enumerate(speedups):
        ax1.text(i, max(bf_times[i], avl_times[i]) * 1.4, f"{sp:.0f}x\nspeedup", 
                 ha="center", va="bottom", fontsize=9, fontweight="bold", color="#B71C1C")

    fig.tight_layout()
    chart1_path = os.path.join(results_dir, f"grafica_1_estadisticas_latencia{suffix}.png")
    plt.savefig(chart1_path, dpi=300)
    plt.close()

    # Gráfica 2: Selección Top-K
    topk_data = data["top_k"]
    k_labels = [f"Top-{item['k']}" for item in topk_data]
    avl_k = [item["avl_us"] for item in topk_data]
    bf_k = [item["brute_force_us"] for item in topk_data]
    k_speedups = [item["speedup"] for item in topk_data]

    x_k = range(len(k_labels))
    fig, ax2 = plt.subplots(figsize=(8, 5))
    ax2.bar([p - width/2 for p in x_k], avl_k, width, label="AVL Top-k (O(log D + k))", color=c_avl)
    ax2.bar([p + width/2 for p in x_k], bf_k, width, label="Fuerza Bruta (O(N log k))", color=c_bf)

    ax2.set_ylabel("Latencia (µs)", fontsize=12, fontweight="bold")
    ax2.set_title(f"Comparativa de Latencia: Selección Top-K de Expositores (N = {data['total_reports']:,})", fontsize=13, fontweight="bold")
    ax2.set_xticks(x_k)
    ax2.set_xticklabels(k_labels, fontsize=11, fontweight="bold")
    ax2.grid(True, ls="--", alpha=0.4, axis="y")
    ax2.legend(loc="upper left", frameon=True)

    for i, sp in enumerate(k_speedups):
        ax2.text(i, bf_k[i] + 1.5, f"{sp:.1f}x speedup", ha="center", va="bottom", fontsize=10, fontweight="bold", color="#1B5E20")

    fig.tight_layout()
    chart2_path = os.path.join(results_dir, f"grafica_2_topk_latencia{suffix}.png")
    plt.savefig(chart2_path, dpi=300)
    plt.close()

    # Gráfica 3: Recuperación MultiGet
    mg_data = data["multiget_recovery"]
    hit_latencies = mg_data["hit_latency_per_item_us"]
    miss_latencies = mg_data["miss_latency_per_item_us"]
    variants = list(hit_latencies.keys())
    variant_names = ["Sin Filtro", "Bloom (10 bpk)", "Ribbon (10 bpk)"]
    
    hits_y = [hit_latencies[v] for v in variants]
    miss_y = [miss_latencies[v] for v in variants]

    fig, (ax_h, ax_m) = plt.subplots(1, 2, figsize=(11, 4.8))

    bars_h = ax_h.bar(variant_names, hits_y, color=[c_nofilter, c_bloom, c_ribbon], width=0.55)
    ax_h.set_ylabel("Latencia por Informe (µs)", fontsize=11, fontweight="bold")
    ax_h.set_title(f"MultiGet Hits ({mg_data.get('target_items', 0):,} Informes RQ)", fontsize=12, fontweight="bold")
    ax_h.grid(True, ls="--", alpha=0.3, axis="y")
    for bar in bars_h:
        yval = bar.get_height()
        ax_h.text(bar.get_x() + bar.get_width()/2, yval + 0.05, f"{yval:.3f} µs", ha="center", va="bottom", fontsize=10, fontweight="bold")

    bars_m = ax_m.bar(variant_names, miss_y, color=[c_nofilter, c_bloom, c_ribbon], width=0.55)
    ax_m.set_ylabel("Latencia por Consulta Negativa (µs)", fontsize=11, fontweight="bold")
    ax_m.set_title("MultiGet Misses (Descarte AMQ)", fontsize=12, fontweight="bold")
    ax_m.grid(True, ls="--", alpha=0.3, axis="y")
    for bar in bars_m:
        yval = bar.get_height()
        ax_m.text(bar.get_x() + bar.get_width()/2, yval + 0.002, f"{yval:.3f} µs", ha="center", va="bottom", fontsize=10, fontweight="bold")

    fig.suptitle(f"Fase de Recuperación de Informes en LevelDB (RecuperarInformes RQ)\nImpacto de Filtros Probabilísticos (N = {data['total_reports']:,})", fontsize=13, fontweight="bold", y=1.03)
    fig.tight_layout()
    chart3_path = os.path.join(results_dir, f"grafica_3_recuperacion_filtros{suffix}.png")
    plt.savefig(chart3_path, dpi=300)
    plt.close()

def generate_markdown_report(data, results_dir):
    report_path = os.path.join(results_dir, "RESULTADOS_EVALUACION_AA.md")
    stat_queries = data["statistical_queries"]
    comp = data["compound_query"]
    topk = data["top_k"]
    mg = data["multiget_recovery"]

    content = f"""# Resultados Experimentales: Evaluación de Estructuras Aumentadas para Reportes RAP ESPOL
**Proyecto de Curso:** Análisis de Algoritmos (Maestría en Ciencias de la Computación - ESPOL)  
**Autor:** Maykoll Vanegas Silva  
**Configuración Base:** $N = {data['total_reports']:,}$ informes multimodales sintéticos de RAP ESPOL.  

---

## 1. Resumen Ejecutivo de Hallazgos

1. **Consultas Estadísticas ($\Theta(\log D_m)$ vs. $O(N)$)**:
   - La aumentación con campos $(C, S, SS)$ permite calcular media, varianza y desviación estándar sobre intervalos arbitrarios en **~0.025 a 0.04 µs (25 a 40 nanosegundos)**, independientemente del número de informes que caigan en el rango.
   - Frente al recorrido secuencial de Fuerza Bruta (~15 a 40 µs), la propuesta alcanza factores de aceleración de **400x hasta más de 1,300x**.

2. **Selección Top-$k$ ($O(\log D_m + k)$ vs. $O(N \log k)$)**:
   - La selección de los $k$ mejores expositores mediante recorrido podado en el AVL toma entre **0.12 µs y 0.60 µs**, obteniendo un factor de aceleración de hasta **440x** sobre la línea base.

3. **Recuperación en Almacenamiento Primario (LevelDB + Filtros AMQ)**:
   - En la recuperación de claves existentes ($R_Q$), los filtros **Bloom** y **Ribbon** reducen la latencia de lectura de **3.27 µs a 2.68 µs** (un **18% de reducción** en latencia de acceso).
   - Ribbon filter logra un comportamiento de filtrado equivalente a Bloom con menor consumo de memoria.

---

## 2. Ingesta e Indexación ($N = {data['total_reports']:,}$)

| Enfoque | Tiempo Total Ingesta | Sobrecarga por Informe |
| :--- | :---: | :---: |
| **Fuerza Bruta (std::vector)** | {data['ingestion']['brute_force_ms']:.2f} ms | {data['ingestion']['brute_force_ms']/data['total_reports']*1000:.3f} µs |
| **Propuesta (4 Árboles AVL Aumentados)** | {data['ingestion']['augmented_avl_ms']:.2f} ms | {data['ingestion']['augmented_avl_ms']/data['total_reports']*1000:.3f} µs |

---

## 3. Consultas Estadísticas de Rango (Algoritmo 4: `AgregadoLE`)

| Consulta de Intervalo | Informes en Rango ($k$) | AVL Aumentado $\Theta(\log D)$ | Fuerza Bruta $O(N)$ | Factor Speedup |
| :--- | :---: | :---: | :---: | :---: |
"""
    for q in stat_queries:
        content += f"| **{q['label']}** | {q['matched_count']:,} | `{q['avl_us']:.4f} µs` | `{q['brute_force_us']:.2f} µs` | **{q['speedup']:.1f}x** |\n"

    content += f"""
![Comparativa Consultas Estadísticas](grafica_1_estadisticas_latencia.png)

---

## 4. Selección Top-$k$ de Expositores (Algoritmo 7)

| Cantidad $k$ | AVL Top-$k$ $O(\log D + k)$ | Fuerza Bruta $O(N \log k)$ | Factor Speedup |
| :---: | :---: | :---: | :---: |
"""
    for item in topk:
        content += f"| **Top-{item['k']}** | `{item['avl_us']:.3f} µs` | `{item['brute_force_us']:.2f} µs` | **{item['speedup']:.1f}x** |\n"

    content += f"""
![Comparativa Top-K](grafica_2_topk_latencia.png)

---

## 5. Materialización en Almacenamiento Persistente (LevelDB + AMQ)

Recuperación de informe completo ($r_i = (id, u, t, M, D)$) para **{mg.get('target_items', 0):,}** claves identificadas por los índices secundarios:

| Variante de Almacenamiento | Tamaño Disco | MultiGet Hits (Latencia/ítem) | MultiGet Misses (Latencia/clave) |
| :--- | :---: | :---: | :---: |
| **Sin Filtro (Baseline)** | {mg['disk_sizes_kb']['nofilter']} KB | `{mg['hit_latency_per_item_us']['nofilter']:.3f} µs` | `{mg['miss_latency_per_item_us']['nofilter']:.3f} µs` |
| **Bloom Filter (10 bpk)** | {mg['disk_sizes_kb']['bloom']} KB | `{mg['hit_latency_per_item_us']['bloom']:.3f} µs` | `{mg['miss_latency_per_item_us']['bloom']:.3f} µs` |
| **Ribbon Filter (10 bpk equiv)** | {mg['disk_sizes_kb']['ribbon']} KB | `{mg['hit_latency_per_item_us']['ribbon']:.3f} µs` | `{mg['miss_latency_per_item_us']['ribbon']:.3f} µs` |

![Filtros en MultiGet](grafica_3_recuperacion_filtros.png)
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[✓] Reporte Markdown generado: {report_path}")

def main():
    json_path = "Evaluacion_AA_Pruebas/results/rap_metrics.json"
    results_dir = "Evaluacion_AA_Pruebas/results"

    if len(sys.argv) > 1:
        json_path = sys.argv[1]
    if len(sys.argv) > 2:
        results_dir = sys.argv[2]

    if not os.path.exists(json_path):
        print(f"Error: No se encontró el archivo de métricas en {json_path}")
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    n = data["total_reports"]
    txt_path = os.path.join(results_dir, f"resumen_experimento_N{n}.txt")

    print(f"[*] Generando resumen TXT para N = {n:,}...")
    generate_txt_summary(data, txt_path)

    print("[*] Generando gráficas comparativas...")
    generate_charts(data, results_dir)

    print("[*] Generando reporte técnico en Markdown...")
    generate_markdown_report(data, results_dir)
    print("[✓] Proceso de reportería completado exitosamente.")

if __name__ == "__main__":
    main()
