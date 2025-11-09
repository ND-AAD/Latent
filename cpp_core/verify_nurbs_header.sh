#!/bin/bash
# Verification script for nurbs_generator.h

echo "==================================================="
echo "Agent 46: NURBS Generator Header Verification"
echo "==================================================="
echo ""

HEADER="geometry/nurbs_generator.h"

# Check file exists
if [ ! -f "$HEADER" ]; then
    echo "❌ FAIL: Header file not found at $HEADER"
    exit 1
fi
echo "✅ Header file exists: $HEADER"

# Check line count
LINES=$(wc -l < "$HEADER")
echo "✅ Header has $LINES lines"

# Check pragma once
if grep -q "#pragma once" "$HEADER"; then
    echo "✅ Include guard: #pragma once present"
else
    echo "❌ FAIL: Missing #pragma once"
    exit 1
fi

# Check namespace
if grep -q "namespace latent" "$HEADER"; then
    echo "✅ Namespace: latent namespace present"
else
    echo "❌ FAIL: Missing namespace latent"
    exit 1
fi

# Check class definition
if grep -q "class NURBSMoldGenerator" "$HEADER"; then
    echo "✅ Class: NURBSMoldGenerator defined"
else
    echo "❌ FAIL: Missing NURBSMoldGenerator class"
    exit 1
fi

# Check required includes
echo ""
echo "Checking required includes..."
for INCLUDE in "types.h" "subd_evaluator.h" "TopoDS_Shape.hxx" "Geom_BSplineSurface.hxx"; do
    if grep -q "$INCLUDE" "$HEADER"; then
        echo "  ✅ $INCLUDE"
    else
        echo "  ❌ FAIL: Missing $INCLUDE"
        exit 1
    fi
done

# Check required methods
echo ""
echo "Checking required method declarations..."
for METHOD in "fit_nurbs_surface" "apply_draft_angle" "create_mold_solid" "add_registration_keys" "check_fitting_quality"; do
    if grep -q "$METHOD" "$HEADER"; then
        echo "  ✅ $METHOD()"
    else
        echo "  ❌ FAIL: Missing $METHOD method"
        exit 1
    fi
done

# Check FittingQuality struct
if grep -q "struct FittingQuality" "$HEADER"; then
    echo "  ✅ FittingQuality struct"
else
    echo "  ❌ FAIL: Missing FittingQuality struct"
    exit 1
fi

# Check struct members
echo ""
echo "Checking FittingQuality struct members..."
for MEMBER in "max_deviation" "mean_deviation" "rms_deviation" "num_samples"; do
    if grep -q "$MEMBER" "$HEADER"; then
        echo "  ✅ $MEMBER"
    else
        echo "  ❌ FAIL: Missing $MEMBER in FittingQuality"
        exit 1
    fi
done

# Check constructor
if grep -q "NURBSMoldGenerator(const SubDEvaluator& evaluator)" "$HEADER"; then
    echo ""
    echo "✅ Constructor: Proper signature"
else
    echo ""
    echo "❌ FAIL: Missing or incorrect constructor"
    exit 1
fi

# Check private members
if grep -q "private:" "$HEADER"; then
    echo "✅ Private section: Present"
    if grep -q "const SubDEvaluator& evaluator_" "$HEADER"; then
        echo "✅ Private member: evaluator_ reference"
    else
        echo "❌ FAIL: Missing evaluator_ member"
        exit 1
    fi
else
    echo "❌ FAIL: Missing private section"
    exit 1
fi

# Check helper method
if grep -q "sample_limit_surface" "$HEADER"; then
    echo "✅ Helper method: sample_limit_surface()"
else
    echo "❌ FAIL: Missing sample_limit_surface helper"
    exit 1
fi

echo ""
echo "==================================================="
echo "✅ ALL CHECKS PASSED"
echo "==================================================="
echo ""
echo "Summary:"
echo "  - Header file structure: ✅ Valid"
echo "  - All includes: ✅ Present"
echo "  - All methods: ✅ Declared"
echo "  - FittingQuality struct: ✅ Complete"
echo "  - Class design: ✅ Correct"
echo ""
echo "Status: Ready for implementation (Agents 47-50)"
echo "Note: Full compilation requires OpenCASCADE installation"
echo ""
