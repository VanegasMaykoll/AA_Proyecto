#include "rap_types.hpp"
#include "augmented_avl.hpp"
#include "brute_force_baseline.hpp"
#include "rap_query_engine.hpp"
#include <cassert>
#include <cmath>
#include <iostream>
#include <random>
#include <set>
#include <vector>

void testAVLInvariants() {
    std::cout << "[TEST] 1. Verificando invariantes de balance y aumentación en AVL..." << std::endl;
    AugmentedAVL avl;
    BruteForceBaseline bf;

    std::mt19937 rng(1337);
    std::uniform_real_distribution<double> dist_val(1.0, 5.0);

    const int N = 10000;
    for (int i = 0; i < N; ++i) {
        double val = std::round(dist_val(rng) * 100.0) / 100.0; // simular 2 decimales
        std::string id = "REP-" + std::to_string(i);
        avl.insert(val, id);

        RAPReport r;
        r.id = id;
        r.g = val;
        bf.addReport(r);
    }

    assert(avl.isBalanced() && "ERROR: El árbol AVL no cumple la condición de balance!");
    assert(avl.size() == N && "ERROR: La cantidad total de elementos no coincide!");
    
    // Altura esperada log2(Dm)
    std::cout << "       - N = " << N << ", Claves distintas = " << avl.distinctKeys() 
              << ", Altura = " << avl.treeHeight() << " (Balanceado: OK)" << std::endl;

    // Comparación de estadísticas globales
    AggregatedStats avl_total = avl.totalStats();
    AggregatedStats bf_total = bf.estadisticasRango(MetricType::GLOBAL, 0.0, 10.0);

    assert(avl_total.count == bf_total.count);
    assert(std::fabs(avl_total.sum - bf_total.sum) < 1e-4);
    assert(std::fabs(avl_total.mean() - bf_total.mean()) < 1e-5);
    assert(std::fabs(avl_total.stddev() - bf_total.stddev()) < 1e-5);

    std::cout << "       - Estadísticas globales: Media AVL = " << avl_total.mean() 
              << " vs BF = " << bf_total.mean() << " (OK)" << std::endl;
    std::cout << "[PASS] Invariantes de AVL y aumentación verificados con éxito." << std::endl;
}

void testRangeAndStatistics() {
    std::cout << "[TEST] 2. Verificando consultas por intervalo y estadísticas de rango..." << std::endl;
    AugmentedAVL avl;
    BruteForceBaseline bf;

    std::mt19937 rng(42);
    std::normal_distribution<double> dist_val(3.5, 0.8);

    const int N = 5000;
    for (int i = 0; i < N; ++i) {
        double val = std::clamp(std::round(dist_val(rng) * 100.0) / 100.0, 1.0, 5.0);
        std::string id = "ID-" + std::to_string(i);
        avl.insert(val, id);

        RAPReport r;
        r.id = id;
        r.g = val;
        bf.addReport(r);
    }

    // Probar 20 intervalos aleatorios
    std::uniform_real_distribution<double> rand_a(1.0, 4.0);
    for (int q = 0; q < 20; ++q) {
        double a = std::round(rand_a(rng) * 10.0) / 10.0;
        double b = a + std::round(std::uniform_real_distribution<double>(0.3, 1.5)(rng) * 10.0) / 10.0;
        if (b > 5.0) b = 5.0;

        // 1. Verificar BuscarRango
        auto avl_ids = avl.buscarRango(a, b);
        auto bf_ids = bf.buscarRango(MetricType::GLOBAL, a, b);

        std::set<std::string> set_avl(avl_ids.begin(), avl_ids.end());
        std::set<std::string> set_bf(bf_ids.begin(), bf_ids.end());
        assert(set_avl == set_bf && "ERROR: Los identificadores de BuscarRango no coinciden!");

        // 2. Verificar Estadísticas por Aumentación vs Recorrido Lineal
        AggregatedStats st_avl = avl.estadisticasRango(a, b);
        AggregatedStats st_bf = bf.estadisticasRango(MetricType::GLOBAL, a, b);

        assert(st_avl.count == st_bf.count);
        if (st_avl.count > 0) {
            assert(std::fabs(st_avl.sum - st_bf.sum) < 1e-4);
            assert(std::fabs(st_avl.mean() - st_bf.mean()) < 1e-5);
            assert(std::fabs(st_avl.variance() - st_bf.variance()) < 1e-5);
            assert(std::fabs(st_avl.stddev() - st_bf.stddev()) < 1e-5);
        }
    }

    std::cout << "[PASS] Intervalos y consultas estadísticas O(log D) verificadas al 100% contra Fuerza Bruta." << std::endl;
}

void testCompoundQueries() {
    std::cout << "[TEST] 3. Verificando ConsultaCompuesta conjuntiva..." << std::endl;
    RAPQueryEngine engine;
    BruteForceBaseline bf;

    std::mt19937 rng(999);
    for (int i = 0; i < 3000; ++i) {
        RAPReport r;
        r.id = "REP-" + std::to_string(i);
        r.g = std::round(std::uniform_real_distribution<double>(1.0, 5.0)(rng) * 10.0) / 10.0;
        r.z = std::round(std::uniform_real_distribution<double>(0.0, 1.0)(rng) * 10.0) / 10.0;
        r.v = std::round(std::uniform_real_distribution<double>(0.0, 1.0)(rng) * 10.0) / 10.0;
        r.p = std::round(std::uniform_real_distribution<double>(0.0, 1.0)(rng) * 10.0) / 10.0;

        engine.insertReport(r);
        bf.addReport(r);
    }

    // Consulta con 3 predicados: (3.0 <= g <= 4.5) AND (z >= 0.6) AND (v >= 0.5)
    std::vector<Predicate> preds = {
        {MetricType::GLOBAL, 3.0, 4.5},
        {MetricType::GAZE,   0.6, 1.0},
        {MetricType::VOLUME, 0.5, 1.0}
    };

    auto res_engine = engine.consultaCompuesta(preds);
    auto res_bf = bf.consultaCompuesta(preds);

    std::set<std::string> set_engine(res_engine.begin(), res_engine.end());
    std::set<std::string> set_bf(res_bf.begin(), res_bf.end());

    assert(set_engine == set_bf && "ERROR: ConsultaCompuesta no coincide con Fuerza Bruta!");
    std::cout << "       - Resultados encontrados: " << res_engine.size() << " coincidentes exactos." << std::endl;
    std::cout << "[PASS] ConsultaCompuesta verificada con éxito." << std::endl;
}

int main() {
    std::cout << "==================================================" << std::endl;
    std::cout << "SUITE DE PRUEBAS UNITARIAS: ALGORITMOS Y AUMENTACIÓN" << std::endl;
    std::cout << "==================================================" << std::endl;
    testAVLInvariants();
    testRangeAndStatistics();
    testCompoundQueries();
    std::cout << "==================================================" << std::endl;
    std::cout << "TODAS LAS PRUEBAS PASARON EXITOSAMENTE (CORRECTITUD VALIDADA)" << std::endl;
    std::cout << "==================================================" << std::endl;
    return 0;
}
