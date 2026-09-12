#ifndef RAP_QUERY_ENGINE_HPP
#define RAP_QUERY_ENGINE_HPP

#include "rap_types.hpp"
#include "augmented_avl.hpp"
#include <algorithm>
#include <unordered_set>
#include <string_view>
#include <vector>
#include <string>

class RAPQueryEngine {
private:
    AugmentedAVL tree_global_;   // Ig: Puntaje global
    AugmentedAVL tree_gaze_;     // Iz: Mirada hacia audiencia
    AugmentedAVL tree_volume_;   // Iv: Volumen de voz
    AugmentedAVL tree_posture_;  // Ip: Postura corporal

    const AugmentedAVL& getTree(MetricType m) const {
        switch (m) {
            case MetricType::GLOBAL:  return tree_global_;
            case MetricType::GAZE:    return tree_gaze_;
            case MetricType::VOLUME:  return tree_volume_;
            case MetricType::POSTURE: return tree_posture_;
        }
        return tree_global_;
    }

    AugmentedAVL& getTree(MetricType m) {
        switch (m) {
            case MetricType::GLOBAL:  return tree_global_;
            case MetricType::GAZE:    return tree_gaze_;
            case MetricType::VOLUME:  return tree_volume_;
            case MetricType::POSTURE: return tree_posture_;
        }
        return tree_global_;
    }

public:
    RAPQueryEngine() = default;

    // Algoritmo 2: InsertarInforme(r)
    void insertReport(const RAPReport& r) {
        tree_global_.insert(r.g, r.id);
        tree_gaze_.insert(r.z, r.id);
        tree_volume_.insert(r.v, r.id);
        tree_posture_.insert(r.p, r.id);
    }

    // Algoritmo 3: BuscarRango(m, a, b)
    std::vector<std::string> buscarRango(MetricType m, double a, double b) const {
        return getTree(m).buscarRango(a, b);
    }

    // Algoritmo 4: Consulta Estadística por Aumentación
    AggregatedStats estadisticasRango(MetricType m, double a, double b) const {
        return getTree(m).estadisticasRango(a, b);
    }

    // Algoritmo 7: TopK
    std::vector<std::string> topK(MetricType m, size_t k, TopKOrder order) const {
        return getTree(m).topK(k, order);
    }

    // Algoritmo 5: ConsultaCompuesta(Q) con ordenamiento por cardinalidad
    std::vector<std::string> consultaCompuesta(const std::vector<Predicate>& preds) const {
        if (preds.empty()) return {};

        // 1. Obtener candidatos de cada índice
        std::vector<std::vector<std::string>> cand_lists;
        cand_lists.reserve(preds.size());
        for (const auto& p : preds) {
            cand_lists.push_back(buscarRango(p.metric, p.a, p.b));
        }

        // 2. Ordenar por cardinalidad creciente: |R1| <= |R2| <= ... <= |Rs|
        std::sort(cand_lists.begin(), cand_lists.end(),
            [](const std::vector<std::string>& a, const std::vector<std::string>& b) {
                return a.size() < b.size();
            });

        // Poda inmediata: si el conjunto más pequeño está vacío, el resultado es vacío
        if (cand_lists[0].empty()) {
            return {};
        }

        // 3. Intersección progresiva utilizando hash sets de string_view para evitar copias
        std::vector<std::string_view> current;
        current.reserve(cand_lists[0].size());
        for (const auto& s : cand_lists[0]) {
            current.emplace_back(s);
        }

        for (size_t i = 1; i < cand_lists.size(); ++i) {
            std::unordered_set<std::string_view> next_set;
            next_set.reserve(cand_lists[i].size());
            for (const auto& s : cand_lists[i]) {
                next_set.emplace(s);
            }

            std::vector<std::string_view> next_current;
            next_current.reserve(current.size());
            for (const auto& item : current) {
                if (next_set.find(item) != next_set.end()) {
                    next_current.push_back(item);
                }
            }

            current = std::move(next_current);
            if (current.empty()) {
                break; // Poda temprana por conjunto vacío
            }
        }

        std::vector<std::string> result;
        result.reserve(current.size());
        for (const auto& sv : current) {
            result.emplace_back(sv);
        }
        return result;
    }

    // Versión sin optimizar de consulta compuesta (intersección en orden arbitrario)
    std::vector<std::string> consultaCompuestaSinOrdenar(const std::vector<Predicate>& preds) const {
        if (preds.empty()) return {};

        std::vector<std::vector<std::string>> cand_lists;
        cand_lists.reserve(preds.size());
        for (const auto& p : preds) {
            cand_lists.push_back(buscarRango(p.metric, p.a, p.b));
        }

        if (cand_lists[0].empty()) return {};

        std::vector<std::string_view> current;
        current.reserve(cand_lists[0].size());
        for (const auto& s : cand_lists[0]) {
            current.emplace_back(s);
        }

        for (size_t i = 1; i < cand_lists.size(); ++i) {
            std::unordered_set<std::string_view> next_set;
            next_set.reserve(cand_lists[i].size());
            for (const auto& s : cand_lists[i]) {
                next_set.emplace(s);
            }

            std::vector<std::string_view> next_current;
            for (const auto& item : current) {
                if (next_set.find(item) != next_set.end()) {
                    next_current.push_back(item);
                }
            }
            current = std::move(next_current);
            if (current.empty()) break;
        }

        std::vector<std::string> result;
        result.reserve(current.size());
        for (const auto& sv : current) {
            result.emplace_back(sv);
        }
        return result;
    }

    size_t totalReportsIndexed() const {
        return tree_global_.size();
    }
};

#endif // RAP_QUERY_ENGINE_HPP
