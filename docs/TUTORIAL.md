# Ceramic Mold Analyzer Tutorial

**Version**: 1.0
**Date**: November 2025
**Author**: Agent 67 - Day 10 API Sprint

---

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Tutorial 1: Simple Vessel (15 minutes)](#tutorial-1-simple-vessel-15-minutes)
4. [Tutorial 2: Complex Form (30 minutes)](#tutorial-2-complex-form-30-minutes)
5. [Tutorial 3: Custom Workflow (30 minutes)](#tutorial-3-custom-workflow-30-minutes)
6. [Troubleshooting](#troubleshooting)
7. [Next Steps](#next-steps)

---

## Introduction

Welcome to the **Ceramic Mold Analyzer**! This tutorial will guide you through the complete workflow of creating translucent porcelain slip-casting molds using mathematical decomposition.

### What You'll Learn

- How to connect Rhino to the desktop application
- Running mathematical analysis lenses (Differential & Spectral)
- Discovering and refining regions
- Validating constraints (undercuts, draft angles)
- Generating NURBS molds
- Exporting back to Rhino for fabrication

### Philosophy

This tool is based on the principle that **"every form contains inherent mathematical coherences."** Different analytical lenses reveal different ways to decompose your geometry. The goal is to find decompositions that create profound mathematical poetry written in light through translucent porcelain.

---

## Prerequisites

### Required Software

- **Rhino 8** (or later) with Grasshopper
- **Python 3.10+** with PyQt6 and VTK installed
- **OpenSubdiv 3.6+** (for C++ core)
- **Ceramic Mold Analyzer** desktop application

### Installation

1. **Install Python dependencies**:
   ```bash
   cd /path/to/Latent
   pip install -r requirements.txt
   ```

2. **Build C++ core**:
   ```bash
   python setup.py build_ext --inplace
   ```

3. **Verify installation**:
   ```bash
   python3 launch.py
   ```

   You should see the application window with four viewports.

### Grasshopper Setup

See the complete [Rhino Bridge Setup Guide](RHINO_BRIDGE_SETUP.md) for detailed instructions. Quick version:

1. Open Grasshopper in Rhino
2. Create a GhPython component
3. Load `rhino/grasshopper_http_server.py`
4. Connect your SubD to the component
5. Server should start on port 8888

---

## Tutorial 1: Simple Vessel (15 minutes)

**Goal**: Learn the basic workflow by creating a 4-piece mold for a simple vessel.

**Expected Time**: 15 minutes
**Difficulty**: Beginner
**Example File**: `examples/simple_vessel.3dm`

### Step 1: Create a Simple Vessel in Rhino (3 min)

1. **Open Rhino** and create a new document

2. **Create a SubD sphere**:
   ```
   Command: SubDSphere
   Center: 0,0,0
   Radius: 50
   ```

3. **Elongate to vessel shape**:
   ```
   Command: SetPt
   - Select top control point
   - Move to: 0,0,80

   - Select bottom control point
   - Move to: 0,0,-80
   ```

4. **Create opening at top**:
   ```
   Command: SubD → Edit → Delete Faces
   - Select top face
   - Delete
   ```

5. **Verify**:
   - Type `SubDDisplayToggle` to see control cage
   - Should have smooth vessel shape with opening
   - Save as `my_simple_vessel.3dm`

### Step 2: Send to Desktop App (2 min)

1. **Open Grasshopper** (type `Grasshopper` in Rhino)

2. **Create GhPython component**:
   - Double-click canvas
   - Type "Python"
   - Select "GhPython Script"

3. **Configure inputs**:
   - Right-click component → "Manage Inputs/Outputs"
   - Add input named `subd`, type hint: `SubD`, access: `Item`
   - Add output named `status`

4. **Load server script**:
   - Double-click component to open editor
   - Copy contents of `rhino/grasshopper_http_server.py`
   - Paste and click OK

5. **Connect SubD**:
   - Right-click canvas → "Param" → "Geometry" → "SubD"
   - Right-click SubD param → "Set one SubD"
   - Select your vessel in Rhino viewport
   - Connect SubD param to `subd` input

6. **Verify server running**:
   - Component should show: "✅ Server running on http://localhost:8888"

### Step 3: Connect from Desktop App (1 min)

1. **Launch application**:
   ```bash
   python3 launch.py
   ```

2. **Connect to Rhino**:
   - Menu: **File → Connect to Rhino**
   - Should see green "Connected" indicator in status bar
   - Your vessel appears in all four viewports

3. **Inspect the geometry**:
   - Use mouse to navigate (Rhino-style controls):
     - **Right drag**: Rotate view
     - **Shift + Right drag**: Pan
     - **Ctrl + Right drag** or **wheel**: Zoom
   - Verify smooth SubD surface rendering

### Step 4: Run Spectral Analysis (3 min)

1. **Open Analysis Panel**:
   - Look for "Analysis" panel on the right side
   - If not visible: **View → Panels → Analysis Panel**

2. **Select Spectral Lens**:
   - Click "Lens Type" dropdown
   - Select **"Spectral Decomposition"**

3. **Configure parameters**:
   - Number of Eigenfunctions: **4** (for 4-piece mold)
   - Samples per Face: **20** (good balance)
   - Boundary Influence: **0.5** (default)

4. **Run analysis**:
   - Click **"Discover Regions"** button
   - Progress dialog appears
   - Wait ~5-10 seconds

5. **View results**:
   - Regions appear in "Region List" panel (left side)
   - Each region shown in different color
   - Should see 4 regions discovered

### Step 5: Inspect and Pin Regions (2 min)

1. **Examine each region**:
   - Click on a region in the list
   - Selected region highlights in yellow in viewports
   - Properties panel shows:
     - Unity Principle: "Spectral Mode 1" (or 2, 3, 4)
     - Unity Strength: 0.7-0.9 (higher is better)
     - Face Count
     - Curvature statistics

2. **Pin all regions**:
   - For each region in the list:
     - Click the pin icon (📌) or checkbox
     - Pinned regions have checkmark
   - This locks them for mold generation

3. **Verify coverage**:
   - All faces should be assigned to regions
   - No gaps or overlaps
   - Each region forms contiguous area

### Step 6: Generate 4-Piece Mold (3 min)

1. **Open mold generation dialog**:
   - Menu: **Mold → Generate Molds...**
   - Or click "Generate Molds" button in toolbar

2. **Set parameters**:
   - **Draft Angle**: 3.0 degrees (standard)
   - **Wall Thickness**: 8.0 mm (for porcelain)
   - **Pull Direction**: Auto-detect (recommended)
   - **Add Registration Keys**: Yes (checked)
   - **Key Diameter**: 10.0 mm
   - **Key Depth**: 5.0 mm

3. **Validate constraints**:
   - Click **"Validate Constraints"** button
   - Should show all green checkmarks:
     - ✅ No undercuts detected
     - ✅ Draft angles satisfied
     - ✅ Wall thickness valid
     - ✅ Regions form valid solids

4. **Generate**:
   - Click **"Generate Molds"** button
   - Progress dialog shows:
     - Evaluating limit surfaces...
     - Fitting NURBS surfaces...
     - Applying draft transformations...
     - Creating solid Breps...
     - Adding registration keys...
   - Wait ~10-15 seconds

5. **Preview results**:
   - 4 mold pieces appear in viewport
   - Each mold is a solid with:
     - Inner surface matching your vessel
     - Outer shell (8mm thick)
     - Draft angle applied
     - Registration keys on parting lines

### Step 7: Export to Rhino (1 min)

1. **Send molds back**:
   - Menu: **Mold → Export to Rhino**
   - Or click "Export" button

2. **Verify in Rhino**:
   - Switch to Rhino window
   - 4 new Brep objects appear in model
   - Each is a solid mold piece
   - Move apart to inspect: `Move` command

3. **Inspect molds**:
   - Check registration keys align
   - Verify draft angles
   - Inner surface should match vessel exactly

### Step 8: Next Steps

**Congratulations!** You've completed your first mold decomposition.

**To export for 3D printing**:
1. In Rhino: Select all mold pieces
2. `Export` → Save as STL
3. Set tolerance: 0.01mm for high quality
4. Import STL into slicer (Cura, PrusaSlicer, etc.)
5. Print with 100% infill (watertight required)

**Expected Output**:
- 4 solid mold pieces
- Each piece fits together with registration keys
- Inner surface exactly matches your vessel
- Ready for slip-casting

---

## Tutorial 2: Complex Form (30 minutes)

**Goal**: Learn advanced techniques for complex organic forms.

**Expected Time**: 30 minutes
**Difficulty**: Intermediate
**Example File**: `examples/complex_form.3dm`

### Overview

This tutorial explores:
- Comparing Differential vs Spectral lenses
- Manual region refinement
- Constraint validation and fixing
- Handling undercuts
- Advanced mold generation

### Step 1: Create Complex Organic Form (5 min)

1. **Start with SubD primitive**:
   ```
   Command: SubDSphere
   Center: 0,0,0
   Radius: 60
   ```

2. **Add complexity**:
   ```
   Command: SubD → Edit → Insert Edge
   - Add several edge loops

   Command: SetPt
   - Move various control points to create organic shape
   - Create bulges, indentations, varying curvature
   ```

3. **Create interesting features**:
   - Add a bulge on one side (convex region)
   - Add an indentation opposite (concave region)
   - Create a neck or narrow section
   - Add subtle curves and transitions

4. **Result**:
   - Organic form with varying curvature
   - Mix of convex, concave, and saddle regions
   - Save as `my_complex_form.3dm`

### Step 2: Connect to Desktop App (2 min)

1. Follow same Grasshopper setup as Tutorial 1
2. Connect your complex form to server
3. Launch desktop app and connect
4. Verify geometry appears correctly

### Step 3: Try Differential Lens First (5 min)

The **Differential Lens** analyzes curvature to discover regions.

1. **Select Differential Lens**:
   - Analysis panel → Lens Type: **"Differential Decomposition"**

2. **Configure parameters**:
   - Samples per Face: **25** (higher for complex forms)
   - Mean Curvature Threshold: **0.08**
   - Curvature Tolerance: **0.15** (how similar adjacent faces must be)
   - Min Region Size: **3** faces
   - Ridge Percentile: **80** (top 20% curvature = ridges)
   - Valley Percentile: **20** (bottom 20% = valleys)

3. **Run analysis**:
   - Click **"Discover Regions"**
   - Wait for processing (~8-12 seconds)

4. **Examine results**:
   - Likely 6-10 regions discovered
   - Regions based on curvature coherence
   - Each region labeled by curvature type:
     - **Elliptic**: Positive Gaussian curvature (sphere-like)
     - **Hyperbolic**: Negative Gaussian curvature (saddle-like)
     - **Parabolic**: Zero Gaussian curvature (cylinder-like)
     - **Ridge**: High mean curvature
     - **Valley**: Low/negative mean curvature

5. **Analyze region properties**:
   - Click each region to inspect
   - Look at Unity Strength (0.6+ is good)
   - Check face counts (too small = may need merging)

### Step 4: Compare with Spectral Lens (5 min)

The **Spectral Lens** uses eigenfunctions of the Laplace-Beltrami operator.

1. **Clear previous results**:
   - Menu: **Edit → Clear All Regions**
   - Or Cmd/Ctrl+Shift+N

2. **Select Spectral Lens**:
   - Analysis panel → Lens Type: **"Spectral Decomposition"**

3. **Configure parameters**:
   - Number of Eigenfunctions: **6** (try 6-piece decomposition)
   - Samples per Face: **25**
   - K-means Clustering: **Yes** (recommended)
   - Boundary Influence: **0.5**

4. **Run analysis**:
   - Click **"Discover Regions"**
   - Wait ~10-15 seconds (spectral analysis is more expensive)

5. **Compare results**:
   - Different decomposition than differential lens
   - Regions based on global harmonic modes, not local curvature
   - Often reveals symmetries and mathematical structure
   - May better respect form's "natural" divisions

6. **Visualize eigenfunctions** (optional):
   - Click **"Visualize Spectral Field"** button
   - See heatmap of eigenfunction values
   - Helps understand why regions formed this way

### Step 5: Choose and Refine (8 min)

Let's use the Spectral result and refine it.

1. **Evaluate decomposition quality**:
   - Look at Unity Strength scores
   - Check region sizes
   - Visual assessment: Do regions make sense?
   - Consider: Will these mold pieces be manufacturable?

2. **Merge small regions**:
   - Find regions with <5 faces
   - Select two adjacent regions to merge:
     - Click first region → hold Shift → click second
     - Menu: **Region → Merge Selected Regions**
     - Or right-click → "Merge"
   - Merged region inherits stronger unity principle

3. **Split regions if needed**:
   - If region too large or complex:
     - Select region
     - Menu: **Region → Split Region...**
     - Choose split criterion:
       - By curvature gradient
       - By spectral mode
       - Manual face selection
   - Creates two new regions

4. **Adjust boundaries manually**:
   - Switch to **Face Edit Mode** (toolbar or press `F`)
   - Click faces to select
   - Right-click → "Assign to Region..."
   - Choose destination region
   - Use this for fine-tuning problematic boundaries

5. **Pin final regions**:
   - Once satisfied, pin all regions
   - Verify complete coverage (no unassigned faces)

### Step 6: Validate Constraints (5 min)

Before generating molds, check manufacturability.

1. **Open Constraint Panel**:
   - View → Panels → Constraint Panel
   - Or click "Constraints" tab

2. **Set pull directions**:
   - For each region:
     - Select region
     - Click "Set Pull Direction"
     - Choose:
       - **Auto-detect**: Algorithm finds best direction
       - **World Axis**: +X, -X, +Y, -Y, +Z, -Z
       - **Custom Vector**: Enter coordinates
     - Recommended: Start with auto-detect

3. **Run undercut detection**:
   - Click **"Check Undercuts"** button
   - Algorithm tests each region:
     - Projects faces along pull direction
     - Detects backward-facing surfaces
   - Results show:
     - ✅ Green: No undercuts
     - ⚠️ Yellow: Minor undercuts (<5% faces)
     - ❌ Red: Significant undercuts (>5% faces)

4. **Fix undercuts** (if any):

   **Option A: Change pull direction**
   - Try different direction
   - Re-run undercut check

   **Option B: Refine regions**
   - Undercut faces should be in different region
   - Use Face Edit Mode to reassign
   - May need to split region

   **Option C: Accept and add draft**
   - Increase draft angle (try 5-7 degrees)
   - Steep draft can eliminate minor undercuts

5. **Validate draft angles**:
   - Click **"Check Draft Angles"** button
   - Shows minimum draft angle for each region
   - All should be ≥ your target draft (3-5 degrees)

### Step 7: Generate Molds (5 min)

1. **Open generation dialog**:
   - Mold → Generate Molds...

2. **Advanced parameters**:
   - **Draft Angle**: 5.0 degrees (higher for complex forms)
   - **Wall Thickness**: 10.0 mm (thicker for strength)
   - **Pull Direction**: Use validated directions
   - **NURBS Fitting**:
     - Degree U: 3 (cubic)
     - Degree V: 3 (cubic)
     - Tolerance: 0.01 mm (high quality)
   - **Registration Keys**:
     - Enabled: Yes
     - Diameter: 12.0 mm
     - Depth: 6.0 mm
     - Count: 3-4 per parting line

3. **Quality settings**:
   - **Sampling Density**: High (for complex curvature)
   - **Evaluation Points per Face**: 30
   - **Adaptive Refinement**: Yes (densifies high curvature areas)

4. **Generate**:
   - Click "Generate Molds"
   - Progress shows each step
   - May take 20-30 seconds for complex forms

5. **Inspect results**:
   - 6 mold pieces appear
   - Check parting line quality
   - Verify registration keys align
   - Inner surfaces should match form exactly

### Step 8: Troubleshooting Complex Forms

**Problem**: Regions don't capture form's structure

**Solution**:
- Try different lens (Differential vs Spectral)
- Adjust lens parameters
- Try different number of eigenfunctions (Spectral)
- Manual refinement with Face Edit Mode

**Problem**: Undercuts detected

**Solution**:
- Refine region boundaries
- Change pull directions
- Increase draft angle
- May require splitting region differently

**Problem**: NURBS fitting errors

**Solution**:
- Increase tolerance
- Reduce NURBS degree (try 2 instead of 3)
- Check for extreme curvature in region
- May need to split region

**Problem**: Molds don't align properly

**Solution**:
- Check pull directions are consistent
- Verify registration key alignment
- Increase key count
- Check for floating-point tolerance issues

### Expected Output

- 6 solid mold pieces
- Each piece validated for manufacturability
- No undercuts
- Proper draft angles applied
- Registration keys on all parting lines
- Inner surfaces exactly match complex form
- Ready for 3D printing and slip-casting

---

## Tutorial 3: Custom Workflow (30 minutes)

**Goal**: Master advanced features for complete control.

**Expected Time**: 30 minutes
**Difficulty**: Advanced
**Example File**: `examples/complex_form.3dm` (reuse)

### Overview

This tutorial covers:
- Pinning specific regions
- Advanced merging strategies
- Custom draft angle per region
- Adding and positioning registration keys
- Complete fabrication export workflow
- Quality control and verification

### Step 1: Start with Analyzed Form (2 min)

1. Use the complex form from Tutorial 2
2. Already connected to desktop app
3. Run Spectral Lens with 8 eigenfunctions
4. Initial 8-region decomposition discovered

### Step 2: Strategic Region Pinning (5 min)

Not all regions need molds! Pin only essential ones.

1. **Identify base region**:
   - Find region that will sit on table (bottom)
   - Select it
   - Right-click → **"Exclude from Molds"**
   - This region won't generate a mold piece
   - Saves material and reduces complexity

2. **Pin critical regions first**:
   - Select regions with highest Unity Strength
   - These are mathematically "truest"
   - Pin them: Click pin icon
   - These boundaries are locked

3. **Evaluate unpinned regions**:
   - Remaining regions are flexible
   - Can be merged or split
   - Adjust to optimize mold count

4. **Strategic considerations**:
   - **Fewer pieces** = easier assembly, weaker seams
   - **More pieces** = stronger seams, more alignment work
   - **Target**: 4-6 pieces for most forms
   - **Balance**: Mathematical truth vs practical fabrication

### Step 3: Advanced Region Merging (8 min)

1. **Analyze merge candidates**:
   - Look for adjacent regions with:
     - Similar curvature types
     - Compatible pull directions
     - Small individual sizes
   - Menu: **Analysis → Show Merge Suggestions**
   - Algorithm highlights good merge pairs

2. **Curvature-based merging**:
   - Select two elliptic regions
   - Check curvature coherence:
     - Region Properties → Curvature Statistics
     - If mean curvature within 10-15%, good merge
   - Merge: Right-click → "Merge Regions"
   - Result: Single elliptic region with stronger unity

3. **Symmetry-aware merging**:
   - If form has symmetry:
     - Mirror regions should be similar size
     - Merge to maintain symmetry
   - Example: Cylindrical form
     - Merge front regions to match back
     - Creates balanced 4-piece decomposition

4. **Test manufacturability after merge**:
   - Select merged region
   - Run undercut check
   - If undercuts appear, undo merge (Cmd/Ctrl+Z)
   - Try different merge or adjust pull direction

5. **Iterative refinement**:
   - Merge → Test → Evaluate
   - Undo if worse (full history available)
   - Try multiple strategies
   - Save promising versions:
     - File → Save Decomposition As...
     - Can load and compare later

### Step 4: Custom Draft Angles per Region (5 min)

Different regions may need different draft.

1. **Understand draft requirements**:
   - **High curvature regions**: Need less draft (2-3°)
   - **Low curvature regions**: Need more draft (5-7°)
   - **Vertical walls**: Maximum draft (7-10°)

2. **Set per-region draft**:
   - Select region
   - Region Properties → Draft Angle Override
   - Enable "Custom Draft"
   - Set angle: e.g., 6.0 degrees
   - Applies only to this region

3. **Example: Vessel with opening**:
   - **Bottom region** (curves outward): 3° draft
   - **Middle region** (vertical sides): 7° draft
   - **Rim region** (curves inward): 5° draft
   - Optimizes each for moldability

4. **Validate custom drafts**:
   - Constraints → Check All Draft Angles
   - Should show ✅ for each region
   - If ❌, increase that region's draft

5. **Global vs local draft**:
   - Global draft (in Generation dialog): Default
   - Local override: Only where needed
   - Best practice: Use global unless specific issue

### Step 5: Advanced Registration Key Placement (5 min)

Precise key placement ensures perfect alignment.

1. **Automatic key placement** (default):
   - Algorithm places keys on parting lines
   - Spaced evenly
   - Avoids high curvature areas
   - Usually sufficient

2. **Manual key placement**:
   - Switch to **Edge Edit Mode** (toolbar or press `E`)
   - Click edge on parting line
   - Right-click → **"Add Registration Key Here"**
   - Dialog appears:
     - Diameter: 10-15mm
     - Depth: 5-8mm (50-60% of diameter)
     - Shape: Cylindrical, Conical, or Custom
     - Orientation: Auto or Manual
   - Click "Add"

3. **Key placement strategy**:
   - **Minimum 3 keys** per parting line
   - **More keys** = better alignment, harder assembly
   - **Avoid** areas with:
     - High curvature (keys may be weak)
     - Thin walls
     - Sharp edges
   - **Place near**:
     - Corners (strong regions)
     - Low curvature areas
     - Critical alignment points

4. **Asymmetric key pattern**:
   - For foolproof assembly
   - Make keys non-symmetric
   - Only one way to fit pieces together
   - Example: 3 keys in L-shape, not triangle

5. **Test key alignment**:
   - Generate molds with keys
   - Inspect in viewport
   - Measure distances between keys
   - Should be consistent across parting line

### Step 6: Complete Fabrication Export (10 min)

Full workflow from analysis to 3D printer.

1. **Final validation checklist**:
   ```
   ✅ All regions pinned
   ✅ No unassigned faces
   ✅ No undercuts detected
   ✅ Draft angles validated
   ✅ Wall thickness ≥ 8mm
   ✅ Registration keys added
   ✅ Pull directions set
   ```

2. **Generate molds**:
   - Mold → Generate Molds
   - Use validated settings
   - Wait for completion

3. **Export to Rhino**:
   - Mold → Export to Rhino
   - Molds appear in Rhino model
   - Each as separate Brep

4. **Rhino post-processing**:

   **Separate mold pieces**:
   ```
   Command: Move
   - Select mold 1 → Move 300,0,0
   - Select mold 2 → Move 0,300,0
   - Select mold 3 → Move -300,0,0
   - etc.
   ```

   **Add labels** (optional):
   ```
   Command: Text
   - Add "Piece 1", "Piece 2", etc.
   - Helps track during assembly
   ```

   **Check for issues**:
   ```
   Command: ShowEdges
   - Should be no naked edges (watertight)

   Command: Check
   - Should pass all geometry checks
   ```

5. **Export STL for 3D printing**:
   ```
   Command: SelAll
   Command: Export

   File Type: STL (*.stl)
   Settings:
     - File Type: Binary
     - Tolerance: 0.01mm (high quality)
     - Angle Tolerance: 5 degrees
     - Min Edge Length: 0.001mm
     - Max Edge Length: Unlimited
     - Refine: Yes

   Save as: vessel_molds.stl
   ```

6. **Import to slicer** (Cura, PrusaSlicer, etc.):
   - Import all mold STLs
   - Settings for slip-casting molds:
     - **Infill**: 100% (must be watertight)
     - **Wall thickness**: 3-4 perimeters
     - **Layer height**: 0.1-0.2mm
     - **Material**: PLA or PETG
     - **Support**: None needed (draft angles eliminate)
   - Slice and export G-code

7. **Quality verification**:
   - In slicer, check:
     - No gaps in walls
     - Smooth inner surfaces
     - Registration keys visible
     - No support required
   - Preview layer-by-layer
   - Estimate print time

8. **Documentation**:
   - Screenshot of decomposition
   - Note region count
   - Record draft angles used
   - Assembly order diagram
   - Save project file:
     - File → Save Decomposition
     - Includes all regions, settings, history

### Step 7: Advanced Tips and Tricks (5 min)

**Workflow optimization**:

1. **Save intermediate states**:
   - After each major step (analysis, refinement, validation)
   - File → Save Decomposition As...
   - Can revert if needed

2. **Batch processing** (if you have multiple forms):
   - Create Python script
   - Use API to automate:
     - Load geometry
     - Run analysis
     - Apply standard settings
     - Export
   - See `examples/batch_processing.py`

3. **Custom lens parameters**:
   - Create presets for different form types:
     - Vessels: High curvature tolerance
     - Sculptures: Low tolerance, more regions
     - Geometric: Spectral lens, boundary emphasis
   - Save presets: Analysis → Save Lens Preset

4. **Curvature visualization**:
   - View → Show Curvature Analysis
   - Heatmap overlay on geometry
   - Helps understand why regions formed
   - Modes:
     - Gaussian curvature (K)
     - Mean curvature (H)
     - Principal curvatures (κ1, κ2)

5. **Iteration comparison**:
   - Analysis → Enable Iteration History
   - See timeline of decomposition attempts
   - Compare resonance scores
   - Click to restore previous iteration
   - Helps find best decomposition

6. **Export options**:
   - **Rhino**: Native Brep (lossless)
   - **STL**: For 3D printing
   - **OBJ**: With normals (for rendering)
   - **STEP**: For CAD (OpenCASCADE format)
   - **G-code**: Direct to printer (via slicer integration)

### Expected Output

- Fully optimized mold decomposition
- 4-6 mold pieces (customized to your form)
- Each piece validated for manufacturability
- Custom draft angles where needed
- Strategic registration key placement
- Complete documentation
- Ready for fabrication
- STL files for 3D printing

---

## Troubleshooting

### Connection Issues

**Problem**: "Could not connect to Rhino HTTP server"

**Solutions**:
1. Verify Grasshopper component shows "Server running"
2. Check port 8888 not blocked by firewall
3. Try restarting Grasshopper
4. Reconnect SubD to input wire
5. Check SubD is valid (not mesh or Brep)

**Problem**: "Failed to serialize SubD"

**Solutions**:
1. Run `SubDRepair` in Rhino
2. Check for naked edges: `ShowEdges`
3. Simplify complex SubDs
4. Ensure SubD is single object (not joined)

### Analysis Issues

**Problem**: No regions discovered

**Solutions**:
1. Increase samples per face (try 30-40)
2. Adjust threshold parameters
3. Try different lens (Differential vs Spectral)
4. Check geometry has varying curvature
5. Verify control cage transferred correctly

**Problem**: Too many small regions

**Solutions**:
1. Increase `min_region_size` parameter
2. Increase `curvature_tolerance` (Differential)
3. Reduce number of eigenfunctions (Spectral)
4. Manually merge small regions

**Problem**: Regions don't make sense

**Solutions**:
1. Try different lens
2. Adjust lens parameters
3. Use custom workflow (Tutorial 3)
4. Manual refinement with Face Edit Mode

### Constraint Validation Issues

**Problem**: Undercuts detected

**Solutions**:
1. Change pull direction (try all 6 axes)
2. Increase draft angle
3. Refine region boundaries
4. Split region into multiple pieces
5. Some forms may need multi-part regions

**Problem**: Draft angle validation fails

**Solutions**:
1. Increase draft angle globally
2. Use per-region custom draft
3. Check pull direction is optimal
4. May indicate region needs splitting

### Mold Generation Issues

**Problem**: NURBS fitting fails

**Solutions**:
1. Increase tolerance (try 0.05-0.1mm)
2. Reduce NURBS degree (2 instead of 3)
3. Reduce evaluation points
4. Check for degenerate faces in region
5. May need to exclude problematic faces

**Problem**: Molds have gaps or overlaps

**Solutions**:
1. Check region boundaries are exact
2. Verify all faces assigned to exactly one region
3. Increase NURBS fitting quality
4. Check registration key alignment
5. May need tighter tolerance

**Problem**: Molds too thin/thick

**Solutions**:
1. Adjust wall thickness parameter
2. Check unit scaling (mm vs cm)
3. Verify SubD scale in Rhino
4. May need to adjust export scale

### Export Issues

**Problem**: Rhino export fails

**Solutions**:
1. Check HTTP bridge still connected
2. Verify molds generated successfully
3. Try exporting one piece at a time
4. Check Rhino accepts Brep format
5. Restart Grasshopper server

**Problem**: STL has holes

**Solutions**:
1. Check molds are valid solids in Rhino
2. Reduce export tolerance
3. Run `Check` command in Rhino
4. Look for naked edges: `ShowEdges`
5. May need to cap open edges

---

## Next Steps

### Learning Resources

1. **API Reference**: `docs/API_REFERENCE.md`
   - Complete API documentation
   - Python and C++ interfaces
   - Advanced programming

2. **Build Instructions**: `docs/BUILD_INSTRUCTIONS.md`
   - Compiling C++ core
   - Troubleshooting builds
   - Platform-specific notes

3. **Technical Specifications**:
   - `docs/reference/subdivision_surface_ceramic_mold_generation_v5.md`
   - Mathematical foundations
   - Algorithm details

4. **Example Scripts**: `examples/`
   - Curvature visualization demo
   - Differential lens demo
   - Constraint visualization
   - Batch processing templates

### Advanced Topics

1. **Custom Mathematical Lenses**:
   - Implement new decomposition algorithms
   - See `app/analysis/differential_lens.py` for template
   - Use `cpp_core` API for limit surface evaluation

2. **Scripting Workflows**:
   - Python API for automation
   - Batch process multiple forms
   - Custom analysis pipelines

3. **GPU Acceleration**:
   - Enable Metal backend (macOS)
   - Faster analysis for complex forms
   - See build instructions

4. **Custom NURBS Fitting**:
   - Adjust fitting algorithms
   - Implement adaptive refinement
   - Optimize for specific geometry types

### Community and Support

1. **Documentation**: Full docs in `docs/` directory
2. **Examples**: Reference implementations in `examples/`
3. **Source Code**: MIT licensed, available on GitHub
4. **Issues**: Report bugs and feature requests

### Philosophical Exploration

The Ceramic Mold Analyzer embodies a unique artistic philosophy:

**"Seams are not flaws to hide but truths to celebrate."**

As you use this tool:
- Experiment with different lenses
- Trust the mathematics
- Seek resonance, not perfection
- Let the form guide the decomposition
- Embrace the seams as poetry written in light

Different lenses reveal different truths about the same form. The "best" decomposition is one that resonates with both:
1. **Mathematical coherence** (high unity strength)
2. **Your artistic vision** (meaningful boundaries)

The tool provides the analysis; you provide the judgment.

### Final Thoughts

You now have complete knowledge to:
- ✅ Connect Rhino to desktop app
- ✅ Run mathematical analysis
- ✅ Discover and refine regions
- ✅ Validate manufacturability
- ✅ Generate production molds
- ✅ Export for 3D printing
- ✅ Create translucent porcelain art

**Go forth and create beautiful mathematical decompositions!**

---

**Document Version**: 1.0
**Last Updated**: November 2025
**Author**: Agent 67 - Day 10 API Sprint
**Next Tutorial**: Advanced Custom Lens Development (coming soon)
