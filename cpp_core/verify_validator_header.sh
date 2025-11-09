#!/bin/bash
# Verify validator.h syntax without requiring OpenSubdiv installation
# This creates temporary mock headers to satisfy dependencies

set -e

echo "=== Validator Header Syntax Verification ==="
echo

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create temporary directory for mocks
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Create mock geometry headers
mkdir -p "$TEMP_DIR/geometry"

cat > "$TEMP_DIR/geometry/types.h" << 'EOF'
#pragma once
#include <vector>
namespace latent {
    struct Point3D {
        float x, y, z;
        Point3D() : x(0), y(0), z(0) {}
        Point3D(float _x, float _y, float _z) : x(_x), y(_y), z(_z) {}
    };
    using Vector3 = Point3D;  // Vector3 alias defined here too
    struct SubDControlCage {};
    struct TessellationResult {};
}
EOF

cat > "$TEMP_DIR/geometry/subd_evaluator.h" << 'EOF'
#pragma once
#include "types.h"
namespace latent {
    class SubDEvaluator {
    public:
        SubDEvaluator() = default;
    };
}
EOF

# Copy validator.h to temp location with adjusted includes
mkdir -p "$TEMP_DIR/constraints"
sed 's|#include "../geometry/|#include "geometry/|g' "$SCRIPT_DIR/constraints/validator.h" > "$TEMP_DIR/constraints/validator.h"

# Create test file
cat > "$TEMP_DIR/test.cpp" << 'EOF'
#include "constraints/validator.h"
#include <iostream>

int main() {
    using namespace latent;

    // Test 1: Enum compiles
    ConstraintLevel level = ConstraintLevel::ERROR;
    std::cout << "✓ ConstraintLevel enum" << std::endl;

    // Test 2: ConstraintViolation struct compiles
    ConstraintViolation violation;
    violation.level = ConstraintLevel::WARNING;
    violation.description = "test";
    violation.face_id = 0;
    violation.severity = 0.5f;
    violation.suggestion = "test";
    std::cout << "✓ ConstraintViolation struct" << std::endl;

    // Test 3: ConstraintReport class compiles
    ConstraintReport report;
    std::cout << "✓ ConstraintReport class" << std::endl;

    // Test 4: Vector3 type alias
    Vector3 vec(1.0f, 0.0f, 0.0f);
    std::cout << "✓ Vector3 type alias" << std::endl;

    // Test 5: Constants accessible
    float min_draft = DraftChecker::MIN_DRAFT_ANGLE;
    float rec_draft = DraftChecker::RECOMMENDED_DRAFT_ANGLE;
    std::cout << "✓ Draft constants: MIN=" << min_draft << "°, REC=" << rec_draft << "°" << std::endl;

    std::cout << "\n=== All syntax checks PASSED ===" << std::endl;
    return 0;
}
EOF

# Compile
echo "Compiling validator.h syntax check..."
g++ -std=c++17 -I"$TEMP_DIR" "$TEMP_DIR/test.cpp" -o "$TEMP_DIR/test" 2>&1

# Run
echo
"$TEMP_DIR/test"

echo
echo "=== validator.h is syntactically correct! ==="
