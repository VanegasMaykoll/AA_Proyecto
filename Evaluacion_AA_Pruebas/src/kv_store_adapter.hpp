#ifndef KV_STORE_ADAPTER_HPP
#define KV_STORE_ADAPTER_HPP

#include "rap_types.hpp"
#include "leveldb/db.h"
#include "leveldb/filter_policy.h"
#include "leveldb/write_batch.h"
#include "util/ribbon_filter.h"
#include <chrono>
#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include <cstdlib>
#include <sys/stat.h>
#include <dirent.h>

enum class FilterKind {
    NO_FILTER,
    BLOOM,
    RIBBON
};

inline const char* filterKindToTag(FilterKind f) {
    switch (f) {
        case FilterKind::NO_FILTER: return "nofilter";
        case FilterKind::BLOOM:     return "bloom";
        case FilterKind::RIBBON:    return "ribbon";
    }
    return "unknown";
}

inline const char* filterKindToString(FilterKind f) {
    switch (f) {
        case FilterKind::NO_FILTER: return "Sin Filtro (Baseline)";
        case FilterKind::BLOOM:     return "Bloom Filter (10 bpk)";
        case FilterKind::RIBBON:    return "Ribbon Filter (10 bpk equiv)";
    }
    return "Unknown";
}

class KVStoreAdapter {
private:
    std::string db_path_;
    FilterKind filter_kind_;
    const leveldb::FilterPolicy* filter_policy_ = nullptr;
    leveldb::DB* db_ = nullptr;

public:
    KVStoreAdapter(const std::string& db_path, FilterKind filter_kind)
        : db_path_(db_path), filter_kind_(filter_kind) {}

    ~KVStoreAdapter() {
        close();
    }

    bool open(bool clean_existing = true) {
        if (clean_existing) {
            std::string cmd = "rm -rf \"" + db_path_ + "\"";
            int ret = std::system(cmd.c_str());
            (void)ret;
        }

        leveldb::Options options;
        options.create_if_missing = true;
        options.write_buffer_size = 512 * 1024; // 512 KB para forzar creación de SSTables representativas
        options.max_file_size = 512 * 1024;     // Tablas de 512 KB

        switch (filter_kind_) {
            case FilterKind::NO_FILTER:
                filter_policy_ = nullptr;
                break;
            case FilterKind::BLOOM:
                filter_policy_ = leveldb::NewBloomFilterPolicy(10);
                break;
            case FilterKind::RIBBON:
                filter_policy_ = leveldb::NewRibbonFilterPolicy(10);
                break;
        }
        options.filter_policy = filter_policy_;

        leveldb::Status status = leveldb::DB::Open(options, db_path_, &db_);
        if (!status.ok()) {
            std::cerr << "Error al abrir LevelDB en " << db_path_ << ": " << status.ToString() << std::endl;
            return false;
        }
        return true;
    }

    void close() {
        if (db_) {
            delete db_;
            db_ = nullptr;
        }
        if (filter_policy_) {
            delete filter_policy_;
            filter_policy_ = nullptr;
        }
    }

    // Fuerza compactación y generación de SSTables con filtros probabilísticos
    void compact() {
        if (db_) {
            db_->CompactRange(nullptr, nullptr);
        }
    }

    // Ingesta por lotes (Batch Write)
    bool putBatch(const std::vector<RAPReport>& reports) {
        if (!db_) return false;
        leveldb::WriteBatch batch;
        for (const auto& r : reports) {
            batch.Put(r.id, r.payload);
        }
        leveldb::WriteOptions write_opts;
        leveldb::Status s = db_->Write(write_opts, &batch);
        return s.ok();
    }

    struct MultiGetResult {
        uint64_t duration_us = 0;
        size_t items_found = 0;
        size_t items_missed = 0;
        size_t total_bytes = 0;
    };

    // Algoritmo 6: RecuperarInformes(RQ)
    MultiGetResult multiGet(const std::vector<std::string>& rq, bool fill_cache = false) {
        MultiGetResult res;
        if (!db_ || rq.empty()) return res;

        leveldb::ReadOptions read_opts;
        read_opts.fill_cache = fill_cache;

        auto t_start = std::chrono::high_resolution_clock::now();
        for (const auto& id : rq) {
            std::string value;
            leveldb::Status s = db_->Get(read_opts, id, &value);
            if (s.ok()) {
                res.items_found++;
                res.total_bytes += value.size();
            } else {
                res.items_missed++;
            }
        }
        auto t_end = std::chrono::high_resolution_clock::now();
        res.duration_us = std::chrono::duration_cast<std::chrono::microseconds>(t_end - t_start).count();

        return res;
    }

    // Cálculo del tamaño en disco del directorio LevelDB
    uint64_t getDiskSizeBytes() const {
        uint64_t total_size = 0;
        DIR* dir = opendir(db_path_.c_str());
        if (!dir) return 0;
        struct dirent* entry;
        while ((entry = readdir(dir)) != nullptr) {
            if (std::string(entry->d_name) == "." || std::string(entry->d_name) == "..") continue;
            std::string full_path = db_path_ + "/" + entry->d_name;
            struct stat st;
            if (stat(full_path.c_str(), &st) == 0) {
                total_size += st.st_size;
            }
        }
        closedir(dir);
        return total_size;
    }
};

#endif // KV_STORE_ADAPTER_HPP
