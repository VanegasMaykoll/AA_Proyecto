#ifndef AUGMENTED_AVL_HPP
#define AUGMENTED_AVL_HPP

#include "rap_types.hpp"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <string>
#include <vector>

enum class TopKOrder {
    HIGHEST,  // Mejores resultados
    LOWEST    // Peores resultados
};

struct AVLNode {
    double key;                       // kx: Valor de la métrica
    std::vector<std::string> ids;     // Lx: Lista de identificadores con este valor
    int height;                       // Altura estructural para balanceo AVL
    AVLNode* left;                    // xL
    AVLNode* right;                   // xR

    // Información aumentada del subárbol cuya raíz es este nodo:
    uint64_t C;                       // C(x): Cantidad total de informes en el subárbol
    double S;                         // S(x): Suma de las métricas en el subárbol
    double SS;                        // SS(x): Suma de los cuadrados de las métricas en el subárbol

    AVLNode(double k, const std::string& id)
        : key(k), ids{id}, height(1), left(nullptr), right(nullptr),
          C(1), S(k), SS(k * k) {}
};

class AugmentedAVL {
private:
    AVLNode* root_ = nullptr;
    size_t distinct_keys_ = 0;
    size_t total_items_ = 0;
    static constexpr double EPSILON = 1e-7;

    static int height(const AVLNode* n) {
        return n ? n->height : 0;
    }

    static uint64_t count(const AVLNode* n) {
        return n ? n->C : 0;
    }

    static double sum(const AVLNode* n) {
        return n ? n->S : 0.0;
    }

    static double sumSquares(const AVLNode* n) {
        return n ? n->SS : 0.0;
    }

    static int getBalance(const AVLNode* n) {
        return n ? (height(n->left) - height(n->right)) : 0;
    }

    // Algoritmo 1: ActualizarNodo(x)
    // Se ejecuta en Theta(1)
    static void actualizarNodo(AVLNode* x) {
        if (!x) return;
        x->height = 1 + std::max(height(x->left), height(x->right));
        uint64_t lx = x->ids.size();
        x->C = count(x->left) + lx + count(x->right);
        x->S = sum(x->left) + (x->key * static_cast<double>(lx)) + sum(x->right);
        x->SS = sumSquares(x->left) + (x->key * x->key * static_cast<double>(lx)) + sumSquares(x->right);
    }

    // Rotación Simple a la Derecha
    static AVLNode* rotateRight(AVLNode* y) {
        AVLNode* x = y->left;
        AVLNode* T2 = x->right;

        x->right = y;
        y->left = T2;

        actualizarNodo(y);
        actualizarNodo(x);

        return x;
    }

    // Rotación Simple a la Izquierda
    static AVLNode* rotateLeft(AVLNode* x) {
        AVLNode* y = x->right;
        AVLNode* T2 = y->left;

        y->left = x;
        x->right = T2;

        actualizarNodo(x);
        actualizarNodo(y);

        return y;
    }

    // Inserción recursiva manteniendo balance e información aumentada
    AVLNode* insertNode(AVLNode* node, double key, const std::string& id, bool& is_new_key) {
        if (!node) {
            is_new_key = true;
            return new AVLNode(key, id);
        }

        if (std::fabs(key - node->key) < EPSILON) {
            node->ids.push_back(id);
            is_new_key = false;
            actualizarNodo(node);
            return node;
        }

        if (key < node->key) {
            node->left = insertNode(node->left, key, id, is_new_key);
        } else {
            node->right = insertNode(node->right, key, id, is_new_key);
        }

        actualizarNodo(node);

        int balance = getBalance(node);

        // Caso 1: Izquierda - Izquierda
        if (balance > 1 && key < node->left->key) {
            return rotateRight(node);
        }

        // Caso 2: Derecha - Derecha
        if (balance < -1 && key > node->right->key) {
            return rotateLeft(node);
        }

        // Caso 3: Izquierda - Derecha
        if (balance > 1 && key > node->left->key) {
            node->left = rotateLeft(node->left);
            return rotateRight(node);
        }

        // Caso 4: Derecha - Izquierda
        if (balance < -1 && key < node->right->key) {
            node->right = rotateRight(node->right);
            return rotateLeft(node);
        }

        return node;
    }

    // Algoritmo 3: BuscarRango(x, a, b, R)
    // O(log Dm + k)
    void buscarRangoRec(const AVLNode* x, double a, double b, std::vector<std::string>& R) const {
        if (!x) return;

        // Poda: si a < x.clave, explorar subárbol izquierdo
        if (a < x->key) {
            buscarRangoRec(x->left, a, b, R);
        }

        // Si x.clave cae en el intervalo [a, b], agregar todos sus identificadores
        if (x->key >= a - EPSILON && x->key <= b + EPSILON) {
            R.insert(R.end(), x->ids.begin(), x->ids.end());
        }

        // Poda: si x.clave < b, explorar subárbol derecho
        if (x->key < b) {
            buscarRangoRec(x->right, a, b, R);
        }
    }

    // Algoritmo 4: AgregadoLE(x, t) -> claves <= t en O(log Dm)
    AggregatedStats agregadoLERec(const AVLNode* x, double t) const {
        if (!x) return AggregatedStats(0, 0.0, 0.0);

        if (x->key > t + EPSILON) {
            return agregadoLERec(x->left, t);
        } else {
            AggregatedStats AL(count(x->left), sum(x->left), sumSquares(x->left));
            uint64_t lx = x->ids.size();
            AggregatedStats Ax(
                lx,
                x->key * static_cast<double>(lx),
                x->key * x->key * static_cast<double>(lx)
            );
            return AL + Ax + agregadoLERec(x->right, t);
        }
    }

    // Versión estricta: AgregadoLT(x, t) -> claves < t en O(log Dm)
    AggregatedStats agregadoLTRec(const AVLNode* x, double t) const {
        if (!x) return AggregatedStats(0, 0.0, 0.0);

        if (x->key >= t - EPSILON) {
            return agregadoLTRec(x->left, t);
        } else {
            AggregatedStats AL(count(x->left), sum(x->left), sumSquares(x->left));
            uint64_t lx = x->ids.size();
            AggregatedStats Ax(
                lx,
                x->key * static_cast<double>(lx),
                x->key * x->key * static_cast<double>(lx)
            );
            return AL + Ax + agregadoLTRec(x->right, t);
        }
    }

    // Algoritmo 7: TopK(x, k, order, R)
    // O(log Dm + k)
    void topKRec(const AVLNode* x, size_t k, TopKOrder order, std::vector<std::string>& R) const {
        if (!x || R.size() >= k) return;

        if (order == TopKOrder::HIGHEST) {
            topKRec(x->right, k, order, R);
            size_t remaining = k - R.size();
            size_t to_take = std::min(remaining, x->ids.size());
            R.insert(R.end(), x->ids.begin(), x->ids.begin() + to_take);
            if (R.size() < k) {
                topKRec(x->left, k, order, R);
            }
        } else { // LOWEST
            topKRec(x->left, k, order, R);
            size_t remaining = k - R.size();
            size_t to_take = std::min(remaining, x->ids.size());
            R.insert(R.end(), x->ids.begin(), x->ids.begin() + to_take);
            if (R.size() < k) {
                topKRec(x->right, k, order, R);
            }
        }
    }

    void destroyRec(AVLNode* node) {
        if (!node) return;
        destroyRec(node->left);
        destroyRec(node->right);
        delete node;
    }

    // Verificador de consistencia estructural AVL para pruebas unitarias
    bool isBalancedRec(const AVLNode* node) const {
        if (!node) return true;
        int bf = getBalance(node);
        if (std::abs(bf) > 1) return false;
        return isBalancedRec(node->left) && isBalancedRec(node->right);
    }

public:
    AugmentedAVL() = default;
    ~AugmentedAVL() {
        destroyRec(root_);
    }

    AugmentedAVL(const AugmentedAVL&) = delete;
    AugmentedAVL& operator=(const AugmentedAVL&) = delete;

    void insert(double key, const std::string& id) {
        bool is_new_key = false;
        root_ = insertNode(root_, key, id, is_new_key);
        if (is_new_key) distinct_keys_++;
        total_items_++;
    }

    std::vector<std::string> buscarRango(double a, double b) const {
        std::vector<std::string> results;
        buscarRangoRec(root_, a, b, results);
        return results;
    }

    // Consulta Estadística por Aumentación: Theta(log Dm)
    AggregatedStats estadisticasRango(double a, double b) const {
        AggregatedStats le_b = agregadoLERec(root_, b);
        AggregatedStats lt_a = agregadoLTRec(root_, a);
        return le_b - lt_a;
    }

    std::vector<std::string> topK(size_t k, TopKOrder order) const {
        std::vector<std::string> results;
        results.reserve(k);
        topKRec(root_, k, order, results);
        return results;
    }

    size_t size() const { return total_items_; }
    size_t distinctKeys() const { return distinct_keys_; }
    int treeHeight() const { return height(root_); }
    bool isBalanced() const { return isBalancedRec(root_); }

    AggregatedStats totalStats() const {
        return AggregatedStats(count(root_), sum(root_), sumSquares(root_));
    }
};

#endif // AUGMENTED_AVL_HPP
