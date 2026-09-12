#ifndef BRUTE_FORCE_BASELINE_HPP
#define BRUTE_FORCE_BASELINE_HPP

#include "rap_types.hpp"
#include "augmented_avl.hpp"
#include <algorithm>
#include <vector>
#include <string>

class BruteForceBaseline {
private:
    std::vector<RAPReport> reports_;

public:
    BruteForceBaseline() = default;

    void addReport(const RAPReport& r) {
        reports_.push_back(r);
    }

    // Búsqueda por rango mediante recorrido secuencial O(N)
    std::vector<std::string> buscarRango(MetricType m, double a, double b) const {
        std::vector<std::string> results;
        for (const auto& r : reports_) {
            double val = r.getMetric(m);
            if (val >= a - 1e-7 && val <= b + 1e-7) {
                results.push_back(r.id);
            }
        }
        return results;
    }

    // Consulta estadística mediante recorrido secuencial O(N)
    AggregatedStats estadisticasRango(MetricType m, double a, double b) const {
        uint64_t count = 0;
        double sum = 0.0;
        double sum_squares = 0.0;

        for (const auto& r : reports_) {
            double val = r.getMetric(m);
            if (val >= a - 1e-7 && val <= b + 1e-7) {
                count++;
                sum += val;
                sum_squares += (val * val);
            }
        }

        return AggregatedStats(count, sum, sum_squares);
    }

    // Consulta compuesta mediante evaluación secuencial de predicados O(s * N)
    std::vector<std::string> consultaCompuesta(const std::vector<Predicate>& preds) const {
        std::vector<std::string> results;
        for (const auto& r : reports_) {
            bool matches = true;
            for (const auto& p : preds) {
                double val = r.getMetric(p.metric);
                if (val < p.a - 1e-7 || val > p.b + 1e-7) {
                    matches = false;
                    break;
                }
            }
            if (matches) {
                results.push_back(r.id);
            }
        }
        return results;
    }

    // Top-k mediante ordenamiento parcial O(N log k)
    std::vector<std::string> topK(MetricType m, size_t k, TopKOrder order) const {
        if (reports_.empty() || k == 0) return {};

        std::vector<std::pair<double, std::string>> items;
        items.reserve(reports_.size());
        for (const auto& r : reports_) {
            items.emplace_back(r.getMetric(m), r.id);
        }

        size_t take = std::min(k, items.size());
        if (order == TopKOrder::HIGHEST) {
            std::partial_sort(items.begin(), items.begin() + take, items.end(),
                [](const auto& a, const auto& b) {
                    return a.first > b.first;
                });
        } else {
            std::partial_sort(items.begin(), items.begin() + take, items.end(),
                [](const auto& a, const auto& b) {
                    return a.first < b.first;
                });
        }

        std::vector<std::string> results;
        results.reserve(take);
        for (size_t i = 0; i < take; ++i) {
            results.push_back(items[i].second);
        }
        return results;
    }

    size_t size() const { return reports_.size(); }
    const std::vector<RAPReport>& getReports() const { return reports_; }
};

#endif // BRUTE_FORCE_BASELINE_HPP
