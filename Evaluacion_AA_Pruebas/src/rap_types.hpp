#ifndef RAP_TYPES_HPP
#define RAP_TYPES_HPP

#include <string>
#include <vector>
#include <cmath>
#include <cstdint>

enum class MetricType {
    GLOBAL,   // g: [1.0, 5.0]
    GAZE,     // z: [0.0, 1.0]
    VOLUME,   // v: [0.0, 1.0]
    POSTURE   // p: [0.0, 1.0]
};

inline const char* metricToString(MetricType m) {
    switch (m) {
        case MetricType::GLOBAL:  return "global (g)";
        case MetricType::GAZE:    return "gaze (z)";
        case MetricType::VOLUME:  return "volume (v)";
        case MetricType::POSTURE: return "posture (p)";
    }
    return "unknown";
}

struct RAPReport {
    std::string id;
    std::string user_id;
    std::string timestamp;
    double g = 0.0;
    double z = 0.0;
    double v = 0.0;
    double p = 0.0;
    std::string payload;

    double getMetric(MetricType m) const {
        switch (m) {
            case MetricType::GLOBAL:  return g;
            case MetricType::GAZE:    return z;
            case MetricType::VOLUME:  return v;
            case MetricType::POSTURE: return p;
        }
        return 0.0;
    }
};

struct Predicate {
    MetricType metric;
    double a;
    double b;
};

struct AggregatedStats {
    uint64_t count = 0;
    double sum = 0.0;
    double sum_squares = 0.0;

    AggregatedStats() = default;
    AggregatedStats(uint64_t c, double s, double ss) : count(c), sum(s), sum_squares(ss) {}

    AggregatedStats operator+(const AggregatedStats& o) const {
        return AggregatedStats(count + o.count, sum + o.sum, sum_squares + o.sum_squares);
    }

    AggregatedStats operator-(const AggregatedStats& o) const {
        return AggregatedStats(
            count >= o.count ? count - o.count : 0,
            sum - o.sum,
            sum_squares - o.sum_squares
        );
    }

    double mean() const {
        return count > 0 ? (sum / static_cast<double>(count)) : 0.0;
    }

    double variance() const {
        if (count == 0) return 0.0;
        double m = mean();
        double var = (sum_squares / static_cast<double>(count)) - (m * m);
        return var > 0.0 ? var : 0.0;
    }

    double stddev() const {
        return std::sqrt(variance());
    }
};

#endif // RAP_TYPES_HPP
