/**
 * Minimal syntax check for validator.h
 * This verifies the header is syntactically correct without needing OpenSubdiv
 */

// Mock minimal dependencies to check syntax
namespace latent {
    struct Point3D { float x, y, z; Point3D() = default; Point3D(float, float, float) {} };
    struct SubDControlCage {};
    struct TessellationResult {};
    class SubDEvaluator {
    public:
        SubDEvaluator() = default;
        void initialize(const SubDControlCage&) {}
        bool is_initialized() const { return true; }
        Point3D evaluate_limit_point(int, float, float) const { return {}; }
        void evaluate_limit(int, float, float, Point3D&, Point3D&) const {}
    };
}

// Now include the actual header to verify syntax
#include "constraints/validator.h"

int main() {
    // Just verify types compile
    latent::ConstraintLevel level = latent::ConstraintLevel::ERROR;
    latent::ConstraintViolation violation;
    latent::ConstraintReport report;

    (void)level;
    (void)violation;
    (void)report;

    return 0;
}
