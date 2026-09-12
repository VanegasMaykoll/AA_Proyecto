#include "rap_types.hpp"
#include "augmented_avl.hpp"
#include "brute_force_baseline.hpp"
#include "rap_query_engine.hpp"
#include "kv_store_adapter.hpp"

#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <sstream>
#include <string>
#include <vector>
#include <map>

template <class T>
inline void doNotOptimize(T const& val) {
    asm volatile("" : : "r,m"(val) : "memory");
}

bool parseReportLine(const std::string& line, RAPReport& r) {
    auto extractString = [&](const std::string& key) -> std::string {
        std::string pattern = "\"" + key + "\": \"";
        size_t pos = line.find(pattern);
        if (pos == std::string::npos) return "";
        pos += pattern.size();
        size_t end_pos = line.find("\"", pos);
        if (end_pos == std::string::npos) return "";
        return line.substr(pos, end_pos - pos);
    };

    auto extractDouble = [&](const std::string& key) -> double {
        std::string pattern = "\"" + key + "\": ";
        size_t pos = line.find(pattern);
        if (pos == std::string::npos) return 0.0;
        pos += pattern.size();
        size_t end_pos = line.find_first_of(",}\n\r", pos);
        if (end_pos == std::string::npos) end_pos = line.size();
        try {
            return std::stod(line.substr(pos, end_pos - pos));
        } catch (...) {
            return 0.0;
        }
    };

    r.id = extractString("id");
    r.user_id = extractString("user_id");
    r.timestamp = extractString("timestamp");
    r.g = extractDouble("g");
    r.z = extractDouble("z");
    r.v = extractDouble("v");
    r.p = extractDouble("p");

    std::string p_key = "\"payload\": ";
    size_t p_pos = line.find(p_key);
    if (p_pos != std::string::npos) {
        p_pos += p_key.size();
        r.payload = line.substr(p_pos);
        while (!r.payload.empty() && (r.payload.back() == '}' || r.payload.back() == '\n' || r.payload.back() == '\r')) {
            r.payload.pop_back();
        }
    } else {
        r.payload = "{}";
    }

    return !r.id.empty();
}

std::vector<RAPReport> loadDataset(const std::string& path) {
    std::ifstream file(path);
    if (!file.is_open()) {
        std::cerr << "Error al abrir el dataset en: " << path << std::endl;
        return {};
    }

    std::vector<RAPReport> reports;
    std::string line;
    while (std::getline(file, line)) {
        if (line.empty()) continue;
        RAPReport r;
        if (parseReportLine(line, r)) {
            reports.push_back(r);
        }
    }
    return reports;
}

int main(int argc, char* argv[]) {
    std::string dataset_path = "Evaluacion_AA_Pruebas/data/rap_reports_10k.jsonl";
    std::string output_json = "Evaluacion_AA_Pruebas/results/rap_metrics.json";
    int num_runs = 50;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg.rfind("--dataset=", 0) == 0) {
            dataset_path = arg.substr(10);
        } else if (arg.rfind("--output=", 0) == 0) {
            output_json = arg.substr(9);
        } else if (arg.rfind("--runs=", 0) == 0) {
            num_runs = std::stoi(arg.substr(7));
        }
    }

    std::cout << "====================================================================" << std::endl;
    std::cout << "BENCHMARK EXPERIMENTAL: ÁRBOL AVL AUMENTADO vs. FUERZA BRUTA & KV" << std::endl;
    std::cout << "Propuesta: Procesamiento y Consulta Eficiente de Reportes RAP ESPOL" << std::endl;
    std::cout << "====================================================================" << std::endl;

    std::cout << "[*] Cargando dataset desde: " << dataset_path << "..." << std::endl;
    auto reports = loadDataset(dataset_path);
    if (reports.empty()) {
        std::cerr << "Error: No se cargaron reportes del dataset." << std::endl;
        return 1;
    }
    std::cout << "[✓] " << reports.size() << " reportes cargados en memoria." << std::endl;

    RAPQueryEngine query_engine;
    BruteForceBaseline brute_force;

    // -------------------------------------------------------------------------
    // PRUEBA 1: INGESTA E INDEXACIÓN EN MEMORIA
    // -------------------------------------------------------------------------
    std::cout << "\n--- [PRUEBA 1: TIEMPOS DE INSERCIÓN E INDEXACIÓN (N = " << reports.size() << ")] ---" << std::endl;

    auto t0 = std::chrono::high_resolution_clock::now();
    for (const auto& r : reports) {
        brute_force.addReport(r);
    }
    auto t1 = std::chrono::high_resolution_clock::now();
    double bf_insert_ms = std::chrono::duration<double, std::milli>(t1 - t0).count();

    auto t2 = std::chrono::high_resolution_clock::now();
    for (const auto& r : reports) {
        query_engine.insertReport(r);
    }
    auto t3 = std::chrono::high_resolution_clock::now();
    double avl_insert_ms = std::chrono::duration<double, std::milli>(t3 - t2).count();

    std::cout << "  - Ingesta Fuerza Bruta (std::vector):       " << std::fixed << std::setprecision(3) << bf_insert_ms << " ms" << std::endl;
    std::cout << "  - Ingesta + Indexación (4 AVL Aumentados):  " << avl_insert_ms << " ms (" 
              << (avl_insert_ms / reports.size() * 1000.0) << " us/informe)" << std::endl;

    // -------------------------------------------------------------------------
    // PRUEBA 2: CONSULTAS ESTADÍSTICAS POR INTERVALO: Theta(log Dm) vs. O(N)
    // -------------------------------------------------------------------------
    std::cout << "\n--- [PRUEBA 2: CONSULTAS ESTADÍSTICAS DE RANGO (MEDIA, VARIANZA, STDDEV)] ---" << std::endl;
    struct RangeTest {
        std::string label;
        MetricType metric;
        double a, b;
    };
    std::vector<RangeTest> stat_tests = {
        {"Puntaje Global [3.50, 3.80] (~35% datos)",  MetricType::GLOBAL, 3.50, 3.80},
        {"Puntaje Global [3.00, 4.20] (~90% datos)",  MetricType::GLOBAL, 3.00, 4.20},
        {"Puntaje Global [1.50, 4.50] (~99% datos)",  MetricType::GLOBAL, 1.50, 4.50},
        {"Mirada Audiencia [0.60, 0.85] (~55% datos)", MetricType::GAZE,   0.60, 0.85},
        {"Volumen de Voz [0.65, 0.90] (~60% datos)",   MetricType::VOLUME, 0.65, 0.90}
    };

    std::vector<double> avl_stat_times_us;
    std::vector<double> bf_stat_times_us;
    std::vector<double> speedup_stats;
    std::vector<uint64_t> stat_counts;

    for (const auto& test : stat_tests) {
        // Calentamiento
        query_engine.estadisticasRango(test.metric, test.a, test.b);
        brute_force.estadisticasRango(test.metric, test.a, test.b);

        // Medición AVL Aumentado
        auto start_avl = std::chrono::high_resolution_clock::now();
        AggregatedStats res_avl;
        for (int i = 0; i < num_runs; ++i) {
            res_avl = query_engine.estadisticasRango(test.metric, test.a, test.b);
            doNotOptimize(res_avl);
        }
        auto end_avl = std::chrono::high_resolution_clock::now();
        double avl_us = std::chrono::duration<double, std::micro>(end_avl - start_avl).count() / num_runs;

        // Medición Fuerza Bruta
        auto start_bf = std::chrono::high_resolution_clock::now();
        AggregatedStats res_bf;
        for (int i = 0; i < num_runs; ++i) {
            res_bf = brute_force.estadisticasRango(test.metric, test.a, test.b);
            doNotOptimize(res_bf);
        }
        auto end_bf = std::chrono::high_resolution_clock::now();
        double bf_us = std::chrono::duration<double, std::micro>(end_bf - start_bf).count() / num_runs;

        double sp = bf_us / avl_us;
        avl_stat_times_us.push_back(avl_us);
        bf_stat_times_us.push_back(bf_us);
        speedup_stats.push_back(sp);
        stat_counts.push_back(res_avl.count);

        std::cout << "  * Consulta: " << test.label << std::endl;
        std::cout << "    - Cantidad informes (k): " << res_avl.count << " | Media: " << std::setprecision(2) << res_avl.mean()
                  << " | StdDev: " << res_avl.stddev() << std::endl;
        std::cout << "    - Tiempo AVL Aumentado:  " << std::setprecision(4) << avl_us << " us  [Theta(log D)]" << std::endl;
        std::cout << "    - Tiempo Fuerza Bruta:    " << std::setprecision(4) << bf_us << " us  [O(N)]" << std::endl;
        std::cout << "    - Factor de Aceleración:  " << std::setprecision(1) << sp << "x MÁS RÁPIDO" << std::endl;
    }

    // -------------------------------------------------------------------------
    // PRUEBA 3: BÚSQUEDA POR INTERVALO (RECUPERACIÓN DE IDS)
    // -------------------------------------------------------------------------
    std::cout << "\n--- [PRUEBA 3: BÚSQUEDA POR RANGO (RECUPERACIÓN DE IDENTIFICADORES)] ---" << std::endl;
    std::vector<RangeTest> range_tests = {
        {"Rango Estrecho [3.40, 3.60] (~19% datos)", MetricType::GLOBAL, 3.40, 3.60},
        {"Rango Medio    [3.00, 4.00] (~78% datos)", MetricType::GLOBAL, 3.00, 4.00},
        {"Rango Amplio   [2.00, 4.50] (~99% datos)", MetricType::GLOBAL, 2.00, 4.50}
    };

    std::vector<double> avl_range_times_us;
    std::vector<double> bf_range_times_us;
    std::vector<size_t> range_counts;

    for (const auto& test : range_tests) {
        auto start_avl = std::chrono::high_resolution_clock::now();
        std::vector<std::string> ids_avl;
        for (int i = 0; i < num_runs; ++i) {
            ids_avl = query_engine.buscarRango(test.metric, test.a, test.b);
            doNotOptimize(ids_avl);
        }
        auto end_avl = std::chrono::high_resolution_clock::now();
        double avl_us = std::chrono::duration<double, std::micro>(end_avl - start_avl).count() / num_runs;

        auto start_bf = std::chrono::high_resolution_clock::now();
        std::vector<std::string> ids_bf;
        for (int i = 0; i < num_runs; ++i) {
            ids_bf = brute_force.buscarRango(test.metric, test.a, test.b);
            doNotOptimize(ids_bf);
        }
        auto end_bf = std::chrono::high_resolution_clock::now();
        double bf_us = std::chrono::duration<double, std::micro>(end_bf - start_bf).count() / num_runs;

        avl_range_times_us.push_back(avl_us);
        bf_range_times_us.push_back(bf_us);
        range_counts.push_back(ids_avl.size());

        std::cout << "  * " << test.label << " -> " << ids_avl.size() << " informes" << std::endl;
        std::cout << "    - AVL Podado:     " << std::setprecision(3) << avl_us << " us" << std::endl;
        std::cout << "    - Fuerza Bruta:   " << std::setprecision(3) << bf_us << " us" << std::endl;
        std::cout << "    - Speedup:        " << std::setprecision(1) << (bf_us / avl_us) << "x" << std::endl;
    }

    // -------------------------------------------------------------------------
    // PRUEBA 4: CONSULTA COMPUESTA MULTIDIMENSIONAL (Algoritmo 5)
    // -------------------------------------------------------------------------
    std::cout << "\n--- [PRUEBA 4: CONSULTAS COMPUESTAS MULTIVARIADAS (Algoritmo 5)] ---" << std::endl;
    std::vector<Predicate> comp_preds = {
        {MetricType::GLOBAL,  3.20, 4.80},
        {MetricType::GAZE,    0.60, 1.00},
        {MetricType::VOLUME,  0.65, 1.00},
        {MetricType::POSTURE, 0.70, 1.00}
    };

    auto start_opt = std::chrono::high_resolution_clock::now();
    std::vector<std::string> res_opt;
    for (int i = 0; i < num_runs; ++i) {
        res_opt = query_engine.consultaCompuesta(comp_preds);
        doNotOptimize(res_opt);
    }
    auto end_opt = std::chrono::high_resolution_clock::now();
    double opt_us = std::chrono::duration<double, std::micro>(end_opt - start_opt).count() / num_runs;

    auto start_unopt = std::chrono::high_resolution_clock::now();
    std::vector<std::string> res_unopt;
    for (int i = 0; i < num_runs; ++i) {
        res_unopt = query_engine.consultaCompuestaSinOrdenar(comp_preds);
        doNotOptimize(res_unopt);
    }
    auto end_unopt = std::chrono::high_resolution_clock::now();
    double unopt_us = std::chrono::duration<double, std::micro>(end_unopt - start_unopt).count() / num_runs;

    auto start_bf_comp = std::chrono::high_resolution_clock::now();
    std::vector<std::string> res_bf_comp;
    for (int i = 0; i < num_runs; ++i) {
        res_bf_comp = brute_force.consultaCompuesta(comp_preds);
        doNotOptimize(res_bf_comp);
    }
    auto end_bf_comp = std::chrono::high_resolution_clock::now();
    double bf_comp_us = std::chrono::duration<double, std::micro>(end_bf_comp - start_bf_comp).count() / num_runs;

    std::cout << "  * Predicados evaluados simultáneamente: 4 (g, z, v, p)" << std::endl;
    std::cout << "    - Informes coincidentes: " << res_opt.size() << std::endl;
    std::cout << "    - Propuesta (Ordenado por Cardinalidad): " << std::setprecision(3) << opt_us << " us" << std::endl;
    std::cout << "    - Intersección Sin Ordenar:               " << std::setprecision(3) << unopt_us << " us" << std::endl;
    std::cout << "    - Fuerza Bruta Secuencial:               " << std::setprecision(3) << bf_comp_us << " us" << std::endl;
    std::cout << "    - Ganancia de la ordenación por tamaño:  " << std::setprecision(2) << (unopt_us / opt_us) << "x" << std::endl;

    // -------------------------------------------------------------------------
    // PRUEBA 5: CONSULTAS TOP-K
    // -------------------------------------------------------------------------
    std::cout << "\n--- [PRUEBA 5: SELECCIÓN TOP-K (Algoritmo 7)] ---" << std::endl;
    std::vector<size_t> k_vals = {10, 50, 100};
    std::vector<double> avl_topk_us;
    std::vector<double> bf_topk_us;

    for (size_t k : k_vals) {
        auto start_avl = std::chrono::high_resolution_clock::now();
        std::vector<std::string> top_avl;
        for (int i = 0; i < num_runs; ++i) {
            top_avl = query_engine.topK(MetricType::GLOBAL, k, TopKOrder::HIGHEST);
            doNotOptimize(top_avl);
        }
        auto end_avl = std::chrono::high_resolution_clock::now();
        double avl_us = std::chrono::duration<double, std::micro>(end_avl - start_avl).count() / num_runs;

        auto start_bf = std::chrono::high_resolution_clock::now();
        std::vector<std::string> top_bf;
        for (int i = 0; i < num_runs; ++i) {
            top_bf = brute_force.topK(MetricType::GLOBAL, k, TopKOrder::HIGHEST);
            doNotOptimize(top_bf);
        }
        auto end_bf = std::chrono::high_resolution_clock::now();
        double bf_us = std::chrono::duration<double, std::micro>(end_bf - start_bf).count() / num_runs;

        avl_topk_us.push_back(avl_us);
        bf_topk_us.push_back(bf_us);

        std::cout << "  * Top-" << k << " Mejores Expositores (Puntaje Global):" << std::endl;
        std::cout << "    - AVL Top-k:      " << std::setprecision(3) << avl_us << " us" << std::endl;
        std::cout << "    - Fuerza Bruta:   " << std::setprecision(3) << bf_us << " us" << std::endl;
        std::cout << "    - Speedup:        " << std::setprecision(1) << (bf_us / avl_us) << "x" << std::endl;
    }

    // -------------------------------------------------------------------------
    // PRUEBA 6: MATERIALIZACIÓN (MultiGet en LevelDB con NoFilter, Bloom y Ribbon)
    // -------------------------------------------------------------------------
    std::cout << "\n--- [PRUEBA 6: MATERIALIZACIÓN (MultiGet en LevelDB: NoFilter vs Bloom vs Ribbon)] ---" << std::endl;
    
    auto target_rq = query_engine.buscarRango(MetricType::GLOBAL, 4.00, 4.50);
    std::cout << "  * Conjunto RQ obtenido de los índices: " << target_rq.size() << " informes." << std::endl;

    // Generamos también 1,000 claves inexistentes para medir el filtrado probabilístico estricto
    std::vector<std::string> miss_keys;
    for (int i = 0; i < 1000; ++i) {
        miss_keys.push_back("RAP-MISS-" + std::to_string(i));
    }

    std::vector<FilterKind> filters_to_eval = {FilterKind::NO_FILTER, FilterKind::BLOOM, FilterKind::RIBBON};
    std::map<std::string, double> hit_latencies_us;
    std::map<std::string, double> miss_latencies_us;
    std::map<std::string, uint64_t> disk_sizes;

    for (auto fk : filters_to_eval) {
        std::string tag = filterKindToTag(fk);
        std::string db_dir = "/tmp/soa_eval_rap_leveldb_" + tag;
        KVStoreAdapter store(db_dir, fk);
        if (!store.open(true)) continue;

        // Ingesta por lote de los 10,000 reportes en LevelDB
        store.putBatch(reports);

        // Forzar flush a SSTables y compactación
        store.compact();

        uint64_t dsize = store.getDiskSizeBytes();
        disk_sizes[tag] = dsize;

        // 1. Recuperación de los informes existentes (Hits)
        auto hit_res = store.multiGet(target_rq, false);
        double hit_per_item = target_rq.empty() ? 0.0 : (static_cast<double>(hit_res.duration_us) / target_rq.size());
        hit_latencies_us[tag] = hit_per_item;

        // 2. Recuperación de claves inexistentes (Misses: donde los filtros AMQ evitan lecturas de disco)
        auto miss_res = store.multiGet(miss_keys, false);
        double miss_per_item = miss_keys.empty() ? 0.0 : (static_cast<double>(miss_res.duration_us) / miss_keys.size());
        miss_latencies_us[tag] = miss_per_item;

        std::cout << "  * Configuración: " << std::left << std::setw(28) << filterKindToString(fk) << std::endl;
        std::cout << "    - Tamaño en disco: " << (dsize / 1024) << " KB" << std::endl;
        std::cout << "    - MultiGet Hits (" << target_rq.size() << " items):   " 
                  << std::setprecision(3) << hit_per_item << " us/informe (Total: " << hit_res.duration_us << " us)" << std::endl;
        std::cout << "    - MultiGet Misses (" << miss_keys.size() << " items): " 
                  << std::setprecision(3) << miss_per_item << " us/clave   (Total: " << miss_res.duration_us << " us)" << std::endl;

        store.close();
    }

    // -------------------------------------------------------------------------
    // EXPORTACIÓN DE MÉTRICAS EN JSON
    // -------------------------------------------------------------------------
    std::ofstream out_f(output_json);
    if (out_f.is_open()) {
        out_f << "{\n";
        out_f << "  \"total_reports\": " << reports.size() << ",\n";
        out_f << "  \"ingestion\": {\n";
        out_f << "    \"brute_force_ms\": " << bf_insert_ms << ",\n";
        out_f << "    \"augmented_avl_ms\": " << avl_insert_ms << "\n";
        out_f << "  },\n";
        out_f << "  \"statistical_queries\": [\n";
        for (size_t i = 0; i < stat_tests.size(); ++i) {
            out_f << "    {\n";
            out_f << "      \"label\": \"" << stat_tests[i].label << "\",\n";
            out_f << "      \"matched_count\": " << stat_counts[i] << ",\n";
            out_f << "      \"avl_us\": " << avl_stat_times_us[i] << ",\n";
            out_f << "      \"brute_force_us\": " << bf_stat_times_us[i] << ",\n";
            out_f << "      \"speedup\": " << speedup_stats[i] << "\n";
            out_f << "    }" << (i + 1 < stat_tests.size() ? "," : "") << "\n";
        }
        out_f << "  ],\n";
        out_f << "  \"range_queries\": [\n";
        for (size_t i = 0; i < range_tests.size(); ++i) {
            out_f << "    {\n";
            out_f << "      \"label\": \"" << range_tests[i].label << "\",\n";
            out_f << "      \"matched_count\": " << range_counts[i] << ",\n";
            out_f << "      \"avl_us\": " << avl_range_times_us[i] << ",\n";
            out_f << "      \"brute_force_us\": " << bf_range_times_us[i] << ",\n";
            out_f << "      \"speedup\": " << (bf_range_times_us[i] / avl_range_times_us[i]) << "\n";
            out_f << "    }" << (i + 1 < range_tests.size() ? "," : "") << "\n";
        }
        out_f << "  ],\n";
        out_f << "  \"compound_query\": {\n";
        out_f << "    \"matched_count\": " << res_opt.size() << ",\n";
        out_f << "    \"sorted_cardinality_us\": " << opt_us << ",\n";
        out_f << "    \"unsorted_us\": " << unopt_us << ",\n";
        out_f << "    \"brute_force_us\": " << bf_comp_us << ",\n";
        out_f << "    \"gain_sorting\": " << (unopt_us / opt_us) << "\n";
        out_f << "  },\n";
        out_f << "  \"top_k\": [\n";
        for (size_t i = 0; i < k_vals.size(); ++i) {
            out_f << "    {\n";
            out_f << "      \"k\": " << k_vals[i] << ",\n";
            out_f << "      \"avl_us\": " << avl_topk_us[i] << ",\n";
            out_f << "      \"brute_force_us\": " << bf_topk_us[i] << ",\n";
            out_f << "      \"speedup\": " << (bf_topk_us[i] / avl_topk_us[i]) << "\n";
            out_f << "    }" << (i + 1 < k_vals.size() ? "," : "") << "\n";
        }
        out_f << "  ],\n";
        out_f << "  \"multiget_recovery\": {\n";
        out_f << "    \"target_items\": " << target_rq.size() << ",\n";
        out_f << "    \"hit_latency_per_item_us\": {\n";
        size_t idx = 0;
        for (const auto& kv : hit_latencies_us) {
            out_f << "      \"" << kv.first << "\": " << kv.second << (idx + 1 < hit_latencies_us.size() ? "," : "") << "\n";
            idx++;
        }
        out_f << "    },\n";
        out_f << "    \"miss_latency_per_item_us\": {\n";
        idx = 0;
        for (const auto& kv : miss_latencies_us) {
            out_f << "      \"" << kv.first << "\": " << kv.second << (idx + 1 < miss_latencies_us.size() ? "," : "") << "\n";
            idx++;
        }
        out_f << "    },\n";
        out_f << "    \"disk_sizes_kb\": {\n";
        idx = 0;
        for (const auto& kv : disk_sizes) {
            out_f << "      \"" << kv.first << "\": " << (kv.second / 1024) << (idx + 1 < disk_sizes.size() ? "," : "") << "\n";
            idx++;
        }
        out_f << "    }\n";
        out_f << "  }\n";
        out_f << "}\n";
        out_f.close();
        std::cout << "\n[✓] Métricas experimentales exportadas exitosamente en: " << output_json << std::endl;
    }

    std::cout << "====================================================================" << std::endl;
    std::cout << "EVALUACIÓN EXPERIMENTAL COMPLETADA EXITOSAMENTE" << std::endl;
    std::cout << "====================================================================" << std::endl;

    return 0;
}
