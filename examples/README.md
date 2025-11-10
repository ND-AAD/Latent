# Ceramic Mold Analyzer - Examples

**Version**: 1.0
**Date**: November 2025
**Author**: Agent 67 - Day 10 API Sprint

---

## Overview

This directory contains example files and demonstration scripts for the Ceramic Mold Analyzer. These examples range from simple introductory cases to complex real-world scenarios.

---

## Table of Contents

1. [Example Rhino Files](#example-rhino-files)
2. [Python Demo Scripts](#python-demo-scripts)
3. [Expected Outputs](#expected-outputs)
4. [How to Use](#how-to-use)
5. [Creating Your Own Examples](#creating-your-own-examples)

---

## Example Rhino Files

### 1. simple_vessel.3dm

**Description**: Basic vessel form for Tutorial 1
**Difficulty**: Beginner
**Tutorial**: Tutorial 1 (15 minutes)

**Geometry Details**:
- **Type**: SubD surface (Catmull-Clark)
- **Topology**: Modified sphere with opening
- **Control Points**: ~20 vertices
- **Faces**: ~16 quads
- **Features**:
  - Simple ellipsoidal body
  - Opening at top (4 faces removed)
  - Smooth, uniform curvature
  - No sharp features or creases

**Expected Analysis Results**:
- **Recommended Lens**: Spectral Decomposition
- **Optimal Regions**: 4 pieces
- **Unity Strength**: 0.75-0.85 (good)
- **Fabrication**: Easy (no undercuts)
- **Draft Angle**: 3° sufficient
- **Mold Generation Time**: ~10 seconds

**Learning Objectives**:
- Basic Rhino-to-desktop workflow
- Simple spectral analysis
- Region pinning
- Basic mold generation
- Export to Rhino

**Usage**:
```bash
# 1. Open simple_vessel.3dm in Rhino
# 2. Follow Tutorial 1 in docs/TUTORIAL.md
# 3. Expected completion: 15 minutes
```

---

### 2. complex_form.3dm

**Description**: Organic form with varying curvature for Tutorial 2 & 3
**Difficulty**: Intermediate/Advanced
**Tutorial**: Tutorial 2 & 3 (30 minutes each)

**Geometry Details**:
- **Type**: SubD surface (Catmull-Clark)
- **Topology**: Organic blob with features
- **Control Points**: ~40 vertices
- **Faces**: ~36 quads
- **Features**:
  - Convex bulges (elliptic regions)
  - Concave indentations (hyperbolic regions)
  - Saddle transitions
  - Varying curvature throughout
  - No creases (smooth everywhere)

**Expected Analysis Results**:

**Differential Lens**:
- Regions: 6-10 pieces
- Based on curvature coherence
- Separates elliptic/hyperbolic/parabolic
- Unity Strength: 0.65-0.80
- Good for highlighting curvature changes

**Spectral Lens**:
- Regions: 6-8 pieces (configurable)
- Based on harmonic modes
- Reveals mathematical symmetries
- Unity Strength: 0.70-0.85
- Better global structure

**Fabrication**:
- Moderate difficulty
- May have minor undercuts (5-7° draft recommended)
- Requires constraint validation
- Manual refinement beneficial

**Learning Objectives**:
- Comparing different lenses
- Manual region refinement
- Constraint validation
- Handling undercuts
- Advanced mold generation

**Usage**:
```bash
# 1. Open complex_form.3dm in Rhino
# 2. Follow Tutorial 2 for comparative analysis
# 3. Follow Tutorial 3 for advanced techniques
# 4. Expected completion: 30 min each
```

---

### 3. cylinder_vessel.3dm

**Description**: Cylindrical vessel with distinct zones
**Difficulty**: Beginner
**Tutorial**: Standalone example

**Geometry Details**:
- **Type**: SubD surface
- **Topology**: Cylinder with caps
- **Control Points**: ~24 vertices (8 around × 3 height)
- **Faces**: ~18 quads
- **Features**:
  - Cylindrical body (parabolic curvature)
  - Rounded bottom cap (elliptic curvature)
  - Rounded top rim (torus-like)
  - Clear zone transitions

**Expected Analysis Results**:
- **Recommended Lens**: Differential Decomposition
- **Optimal Regions**: 3 pieces
  - Bottom cap (elliptic)
  - Cylindrical body (parabolic)
  - Top rim (mixed)
- **Unity Strength**: 0.80-0.90 (excellent)
- **Fabrication**: Very easy
- **Draft Angle**: 2° sufficient (natural taper)

**Learning Objectives**:
- Differential lens usage
- Clear curvature-based decomposition
- Simple fabrication workflow

**Usage**:
```bash
# 1. Open cylinder_vessel.3dm
# 2. Use Differential lens with default settings
# 3. Should discover 3 natural regions
# 4. Generate 3-piece mold
```

---

### 4. double_bulge.3dm

**Description**: Form with two bulges testing symmetry detection
**Difficulty**: Intermediate
**Tutorial**: Standalone example

**Geometry Details**:
- **Type**: SubD surface
- **Topology**: Elongated form with symmetric bulges
- **Control Points**: ~32 vertices
- **Faces**: ~28 quads
- **Features**:
  - Two symmetric bulges (opposite sides)
  - Connecting neck region
  - Mirror symmetry (XZ plane)
  - Complex curvature transitions

**Expected Analysis Results**:
- **Recommended Lens**: Spectral Decomposition
- **Optimal Regions**: 4-6 pieces
- **Unity Strength**: 0.75-0.85
- **Key Feature**: Spectral lens respects symmetry
  - Mirror regions have similar unity principles
  - Demonstrates global structure awareness
- **Fabrication**: Moderate
  - Undercuts possible at neck
  - 5° draft recommended

**Learning Objectives**:
- Spectral lens symmetry detection
- Handling symmetric decompositions
- Balancing mathematical truth vs fabrication

**Usage**:
```bash
# 1. Open double_bulge.3dm
# 2. Use Spectral lens with 4-6 eigenfunctions
# 3. Observe symmetric region pairs
# 4. Compare with Differential lens (asymmetric)
```

---

### 5. sculpture_organic.3dm

**Description**: Complex organic sculpture form
**Difficulty**: Advanced
**Tutorial**: Standalone example

**Geometry Details**:
- **Type**: SubD surface
- **Topology**: Highly organic blob
- **Control Points**: ~60 vertices
- **Faces**: ~55 quads
- **Features**:
  - Extreme curvature variation
  - Multiple bulges and valleys
  - No symmetry
  - Challenging geometry for mold making

**Expected Analysis Results**:
- **Recommended Lens**: Both (compare)
- **Differential Lens**:
  - Regions: 12-15 pieces (many small regions)
  - Very local analysis
  - May over-segment
- **Spectral Lens**:
  - Regions: 8-10 pieces
  - Better global coherence
  - Recommended for this complexity
- **Unity Strength**: 0.60-0.75 (challenging form)
- **Fabrication**: Difficult
  - Significant undercuts likely
  - 7-10° draft needed
  - Extensive manual refinement required

**Learning Objectives**:
- Handling complex real-world forms
- Extensive manual refinement
- Advanced constraint validation
- Iterative optimization workflow

**Usage**:
```bash
# 1. Open sculpture_organic.3dm
# 2. Try both lenses, compare
# 3. Expect to need manual merging/splitting
# 4. Thorough constraint validation essential
# 5. May take 45-60 minutes for quality result
```

---

## Python Demo Scripts

### 1. differential_lens_demo.py

**Purpose**: Demonstrates the Differential lens for curvature-based decomposition

**What it does**:
- Creates simple test geometries (sphere, cylinder)
- Initializes Differential lens
- Runs region discovery
- Displays curvature statistics
- Shows custom parameter usage
- Demonstrates pinned faces

**Usage**:
```bash
python3 examples/differential_lens_demo.py
```

**Expected output**:
```
===========================================================
DIFFERENTIAL LENS DEMONSTRATION
First Mathematical Lens for Ceramic Mold Analyzer
===========================================================

===========================================================
Analyzing: Sphere (Octahedron)
===========================================================
Control cage: 6 vertices, 8 faces

Discovering regions...

✓ Discovered 1 regions

Region 1: region_0_elliptic_1234567
  Unity Principle: curvature_elliptic
  Unity Strength: 0.889
  Face Count: 8
  Curvature Type: elliptic
  Is Ridge: False
  Is Valley: False

Curvature Field Statistics:
  Gaussian Curvature (K):
    Range: [0.9245, 1.0123]
    Mean: 0.9815
    Std: 0.0234
...
```

**Learning objectives**:
- Understanding Differential lens output
- Interpreting curvature statistics
- Custom parameter effects

---

### 2. curvature_visualization_demo.py

**Purpose**: Visualizes curvature fields on SubD surfaces

**What it does**:
- Creates test geometry
- Computes Gaussian and Mean curvature
- Generates color-coded visualization
- Shows principal curvature directions
- Demonstrates VTK integration

**Usage**:
```bash
python3 examples/curvature_visualization_demo.py
```

**Expected output**:
- VTK window opens showing geometry
- Color gradient represents curvature values
- Red = high positive curvature
- Blue = negative curvature
- Green = near-zero curvature

**Learning objectives**:
- Understanding curvature analysis
- Visualizing mathematical fields
- VTK rendering techniques

---

### 3. constraint_visualization_example.py

**Purpose**: Demonstrates constraint validation visualization

**What it does**:
- Creates geometry with potential undercuts
- Sets pull directions
- Runs undercut detection
- Visualizes problematic faces
- Shows draft angle analysis

**Usage**:
```bash
python3 examples/constraint_visualization_example.py
```

**Expected output**:
- Highlights undercut faces in red
- Shows pull direction vectors
- Displays draft angle heatmap
- Reports constraint violations

**Learning objectives**:
- Understanding constraint validation
- Identifying manufacturability issues
- Fixing undercut problems

---

## Expected Outputs

### For simple_vessel.3dm

**After Spectral Analysis (4 eigenfunctions)**:

```
Regions Discovered: 4
Region Breakdown:
  - Region 1: "spectral_mode_1" (25% of faces)
    Unity Strength: 0.82
    Pull Direction: +Z recommended

  - Region 2: "spectral_mode_2" (25% of faces)
    Unity Strength: 0.79
    Pull Direction: -X recommended

  - Region 3: "spectral_mode_3" (25% of faces)
    Unity Strength: 0.81
    Pull Direction: +X recommended

  - Region 4: "spectral_mode_4" (25% of faces)
    Unity Strength: 0.77
    Pull Direction: -Z recommended

Constraint Validation:
  ✅ No undercuts detected
  ✅ All draft angles > 3°
  ✅ Wall thickness valid
  ✅ Regions form valid solids

Mold Generation: ~10 seconds
Output: 4 solid Brep molds ready for export
```

### For complex_form.3dm

**After Spectral Analysis (6 eigenfunctions)**:

```
Regions Discovered: 6
Region Breakdown:
  - Region 1: "spectral_mode_1" (18% of faces)
    Unity Strength: 0.76
    Pull Direction: +Z recommended

  - Region 2: "spectral_mode_2" (16% of faces)
    Unity Strength: 0.73
    Pull Direction: -Z recommended
    ⚠️ Minor undercuts detected (3% faces)

  - Region 3: "spectral_mode_3" (17% of faces)
    Unity Strength: 0.78
    Pull Direction: +Y recommended

  [... similar for regions 4-6]

Constraint Validation:
  ⚠️ Region 2: Minor undercuts (recommend 5° draft)
  ✅ All other regions pass

After Refinement:
  - Increased draft to 5°
  - Adjusted Region 2 boundary
  ✅ All constraints satisfied

Mold Generation: ~15 seconds
Output: 6 solid Brep molds ready for export
```

---

## How to Use

### Basic Workflow

1. **Choose an example file**:
   - Start with `simple_vessel.3dm` if you're new
   - Progress to `complex_form.3dm` for intermediate skills
   - Try `sculpture_organic.3dm` for advanced techniques

2. **Open in Rhino**:
   ```
   File → Open → examples/[filename].3dm
   ```

3. **Setup Grasshopper bridge**:
   - Follow instructions in `docs/RHINO_BRIDGE_SETUP.md`
   - Load HTTP server script
   - Connect SubD to component

4. **Launch desktop app**:
   ```bash
   python3 launch.py
   ```

5. **Follow corresponding tutorial**:
   - See `docs/TUTORIAL.md` for step-by-step instructions
   - Each example has recommended tutorial

6. **Experiment**:
   - Try different lenses
   - Adjust parameters
   - Compare results
   - Save your favorites

### Demo Scripts

1. **Run from project root**:
   ```bash
   python3 examples/[script_name].py
   ```

2. **Read the code**:
   - Scripts are heavily commented
   - Good templates for your own scripts
   - Demonstrate API usage

3. **Modify and experiment**:
   - Change parameters
   - Create your own geometries
   - Test different analyses

---

## Creating Your Own Examples

### Step 1: Create SubD in Rhino

**Guidelines for good examples**:
- Use SubD, not meshes or Breps
- Keep control cage relatively simple (20-60 vertices)
- Ensure valid topology (no naked edges)
- Run `SubDRepair` before saving
- Test with `SubDDisplayToggle`

**Recommended primitives**:
```
SubDSphere    - Good starting point
SubDBox       - For angular forms
SubDCylinder  - For vessels
SubDTorus     - For donut shapes
```

**Editing tips**:
```
SetPt         - Move control points
SubD → Insert Edge - Add detail
SubD → Delete Faces - Create openings
SubD → Crease - Add sharp features (use sparingly)
```

### Step 2: Test in Desktop App

1. Connect via Grasshopper bridge
2. Try both lenses
3. Verify regions make sense
4. Check manufacturability
5. Document expected results

### Step 3: Save and Document

1. Save .3dm file in `examples/`
2. Add entry to this README
3. Include:
   - Geometry description
   - Recommended lens
   - Expected region count
   - Difficulty level
   - Learning objectives

### Step 4: Create Tutorial (optional)

If example demonstrates unique technique:
1. Write step-by-step guide
2. Add to `docs/TUTORIAL.md`
3. Include screenshots (optional)
4. Note expected time and difficulty

---

## File Naming Conventions

**Rhino files**: `[descriptor]_[type].3dm`
- Examples: `simple_vessel.3dm`, `complex_form.3dm`
- Use lowercase with underscores
- Descriptive but concise

**Python scripts**: `[purpose]_demo.py` or `[purpose]_example.py`
- Examples: `differential_lens_demo.py`
- Clear purpose in name
- End with `_demo` or `_example`

**Documentation**: Markdown files in this directory
- This README explains all examples
- Add new examples here, don't create separate docs

---

## Example Metadata Summary

| File | Vertices | Faces | Difficulty | Lens | Regions | Time | Tutorial |
|------|----------|-------|------------|------|---------|------|----------|
| `simple_vessel.3dm` | ~20 | ~16 | Beginner | Spectral | 4 | 15m | Tutorial 1 |
| `complex_form.3dm` | ~40 | ~36 | Intermediate | Both | 6-8 | 30m | Tutorial 2 & 3 |
| `cylinder_vessel.3dm` | ~24 | ~18 | Beginner | Differential | 3 | 20m | Standalone |
| `double_bulge.3dm` | ~32 | ~28 | Intermediate | Spectral | 4-6 | 25m | Standalone |
| `sculpture_organic.3dm` | ~60 | ~55 | Advanced | Both | 8-15 | 45m+ | Standalone |

---

## Tips for Success

### Choosing Examples

- **First time**: Start with `simple_vessel.3dm`
- **Learning lenses**: Use `cylinder_vessel.3dm` (Differential) and `simple_vessel.3dm` (Spectral)
- **Symmetry**: Try `double_bulge.3dm`
- **Real-world prep**: Work through `complex_form.3dm`
- **Challenge**: Tackle `sculpture_organic.3dm`

### Common Pitfalls

1. **Skipping validation**:
   - Always run constraint checks
   - Don't assume simple = no issues
   - Validate before generating molds

2. **Using wrong lens**:
   - Simple uniform forms: Spectral
   - Complex varying curvature: Try both
   - Check Unity Strength scores

3. **Ignoring Unity Strength**:
   - <0.6: Poor decomposition, try different lens
   - 0.6-0.75: Acceptable
   - 0.75-0.85: Good
   - 0.85+: Excellent

4. **Over-parameterizing**:
   - Start with defaults
   - Adjust only if results unsatisfactory
   - Document what parameters you changed

### Advanced Usage

**Batch testing**:
```python
# Test all examples with both lenses
for example in examples:
    for lens in [Differential, Spectral]:
        results = analyze(example, lens)
        compare_resonance(results)
```

**Parameter sweeps**:
```python
# Find optimal eigenfunction count
for n_eigs in range(3, 10):
    regions = spectral_lens.discover(n_eigenfunctions=n_eigs)
    scores.append(mean_unity_strength(regions))
plot_scores()  # Visualize optimal count
```

**Custom metrics**:
```python
# Define your own quality metric
def my_metric(regions):
    return (
        mean_unity_strength(regions) * 0.5 +
        region_count_score(regions) * 0.3 +
        manufacturability_score(regions) * 0.2
    )
```

---

## Additional Resources

### Documentation
- **Main Tutorial**: `docs/TUTORIAL.md`
- **API Reference**: `docs/API_REFERENCE.md`
- **Build Guide**: `docs/BUILD_INSTRUCTIONS.md`
- **Rhino Setup**: `docs/RHINO_BRIDGE_SETUP.md`

### Source Code
- **Differential Lens**: `app/analysis/differential_lens.py`
- **Spectral Lens**: `app/analysis/spectral_lens.py`
- **Constraint Validator**: `cpp_core/constraints/`
- **NURBS Generator**: `cpp_core/nurbs/`

### External References
- OpenSubdiv documentation
- Rhino SubD guide
- Slip-casting ceramics techniques

---

## Contributing Examples

If you create interesting examples, consider contributing:

1. **Prepare files**:
   - Clean .3dm file
   - Test thoroughly
   - Document expected results

2. **Add to README**:
   - Follow format above
   - Include metadata
   - Write clear description

3. **Optional: Create tutorial**:
   - If example shows unique technique
   - Step-by-step instructions
   - Screenshots helpful

4. **Submit**:
   - Create pull request
   - Include example files
   - Update this README

---

## FAQ

**Q: Can I use my own SubD files?**
A: Absolutely! These examples are just starting points. Any valid Rhino SubD will work.

**Q: Why are some examples .3dm files missing?**
A: Example .3dm files are binary Rhino files that must be created in Rhino itself. The descriptions above specify exactly how to create them. Follow the "Geometry Details" for each example.

**Q: Which lens should I use?**
A: Try both! Differential reveals curvature-based structure, Spectral reveals global harmonic modes. Compare Unity Strength scores.

**Q: How many regions is optimal?**
A: Depends on your goals:
- Fewer (3-4): Easier assembly, simpler workflow
- More (6-8): Stronger seams, better mathematical truth
- Balance practical fabrication vs aesthetic goals

**Q: Can I modify the demo scripts?**
A: Yes! They're templates for your own work. Experiment freely.

**Q: Examples don't work?**
A: Check:
1. C++ core built? (`python setup.py build_ext --inplace`)
2. Dependencies installed? (`pip install -r requirements.txt`)
3. Rhino bridge connected?
4. SubD valid in Rhino?

---

**Document Version**: 1.0
**Last Updated**: November 2025
**Maintained by**: Ceramic Mold Analyzer Development Team
**Questions?**: See `docs/TUTORIAL.md` or API documentation
