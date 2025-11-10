# Guide: Creating Example .3dm Files

**Version**: 1.0
**Date**: November 2025
**Author**: Agent 67 - Day 10 API Sprint

---

## Overview

This guide provides step-by-step instructions for creating all example .3dm files referenced in the tutorials. Since .3dm files are binary Rhino files, they must be created in Rhino 8 (or later).

**Note**: These files are not included in the git repository due to their binary nature. Follow these instructions to create them yourself.

---

## Prerequisites

- **Rhino 8** (or later)
- Basic familiarity with Rhino commands
- Understanding of SubD modeling

---

## Example 1: simple_vessel.3dm

**Purpose**: Tutorial 1 - Simple 4-piece mold
**Difficulty**: Beginner
**Time to create**: 5 minutes

### Step-by-Step Instructions

1. **Open Rhino**:
   ```
   File → New
   Template: Small Objects - Millimeters
   ```

2. **Create base sphere**:
   ```
   Command: SubDSphere
   Center of sphere: 0,0,0
   Radius: 50
   ```

3. **Elongate to vessel shape**:
   ```
   Command: SetPt
   Prompt: Select objects
   Action: Click top control point (at 0,0,50)

   Prompt: Point to move from
   Action: Click on the point

   Prompt: Point to move to
   Action: Type 0,0,80 and press Enter
   ```

4. **Elongate bottom**:
   ```
   Command: SetPt
   Action: Select bottom point (at 0,0,-50)
   From: Click the point
   To: 0,0,-80
   ```

5. **Create opening at top**:
   ```
   Command: SelSubDFace
   Action: Click top face (or a few faces at the top)

   Command: Delete
   ```

6. **Smooth if needed**:
   ```
   Command: SubDDisplayToggle
   Action: Verify smooth appearance
   ```

7. **Verify geometry**:
   ```
   Command: What
   Action: Select the object
   Verify: Shows "SubD" (not mesh or Brep)

   Command: ShowEdges
   Action: Check edges at opening (should be clean)
   ```

8. **Save**:
   ```
   File → Save As
   Name: simple_vessel.3dm
   Location: examples/
   ```

### Expected Result

- **Vertices**: ~20 control points
- **Faces**: ~16 quad faces (some at opening may be triangles)
- **Shape**: Elongated ellipsoid with opening at top
- **Curvature**: Smooth, uniform positive curvature
- **File size**: ~50-100 KB

---

## Example 2: complex_form.3dm

**Purpose**: Tutorial 2 & 3 - Complex organic form
**Difficulty**: Intermediate
**Time to create**: 10-15 minutes

### Step-by-Step Instructions

1. **Open Rhino**:
   ```
   File → New
   Template: Small Objects - Millimeters
   ```

2. **Create base sphere**:
   ```
   Command: SubDSphere
   Center: 0,0,0
   Radius: 60
   ```

3. **Add edge loops for detail**:
   ```
   Command: SubDInsertEdge
   Action: Click edges horizontally around middle
   Repeat: Add 2-3 horizontal edge loops

   Command: SubDInsertEdge
   Action: Click edges vertically
   Repeat: Add 2-3 vertical edge loops
   ```

4. **Create bulge on right side**:
   ```
   Command: SetPt
   Action: Select control points on right side (~4 points)
   From: Click one of them
   To: Move outward ~20 units in +X direction

   Result: Convex bulge on right
   ```

5. **Create indentation on left**:
   ```
   Command: SetPt
   Action: Select control points on left side (~4 points)
   From: Click one
   To: Move inward ~15 units in +X direction (toward center)

   Result: Concave indentation on left
   ```

6. **Create neck region**:
   ```
   Command: SetPt
   Action: Select control points around middle horizontal loop
   From: Click one
   To: Move inward ~10 units radially (toward Z axis)

   Result: Narrowed waist/neck
   ```

7. **Add subtle asymmetry**:
   ```
   Command: SetPt
   Action: Select random individual control points
   From: Original position
   To: Move in various directions by 5-10 units

   Result: Organic, non-symmetric form

   Repeat: 5-6 times with different points
   ```

8. **Create saddle region** (optional, advanced):
   ```
   Command: SetPt
   Action: Select 4 points forming a square on surface
   From: Original positions
   To: Move alternating points in/out (creates saddle)

   Result: Hyperbolic (saddle) curvature area
   ```

9. **Smooth and verify**:
   ```
   Command: SubDDisplayToggle
   Action: Toggle to see smooth limit surface
   Verify: Organic shape with varying curvature

   Command: SubDRepair
   Action: Fix any topology issues
   ```

10. **Final check**:
    ```
    Command: What
    Verify: SubD object

    Command: ShowEdges
    Verify: No naked edges (closed surface)
    ```

11. **Save**:
    ```
    File → Save As
    Name: complex_form.3dm
    Location: examples/
    ```

### Expected Result

- **Vertices**: ~40-50 control points
- **Faces**: ~35-45 quad faces
- **Shape**: Organic blob with bulges, indentations, and transitions
- **Curvature**: Mixed - elliptic, hyperbolic, and parabolic regions
- **Features**:
  - Right bulge (convex)
  - Left indentation (concave)
  - Narrow neck
  - Asymmetric
- **File size**: ~100-150 KB

---

## Example 3: cylinder_vessel.3dm

**Purpose**: Standalone example for Differential lens
**Difficulty**: Beginner
**Time to create**: 5 minutes

### Step-by-Step Instructions

1. **Open Rhino**:
   ```
   File → New
   Template: Small Objects - Millimeters
   ```

2. **Create cylinder**:
   ```
   Command: SubDCylinder
   Center of base: 0,0,0
   Radius: 40
   End of axis: 0,0,100
   ```

3. **Round bottom cap**:
   ```
   Command: SetPt
   Action: Select center bottom point (at 0,0,0)
   From: 0,0,0
   To: 0,0,-20

   Result: Rounded bottom instead of flat
   ```

4. **Round top rim**:
   ```
   Command: SetPt
   Action: Select edge loop at top
   From: Current positions
   To: Move outward radially by ~10 units

   Result: Flared rim
   ```

5. **Smooth transitions**:
   ```
   Command: SubDDisplayToggle
   Verify: Smooth transitions between zones
   ```

6. **Verify**:
   ```
   Command: What
   Verify: SubD

   Command: ShowEdges
   Verify: No naked edges
   ```

7. **Save**:
   ```
   File → Save As
   Name: cylinder_vessel.3dm
   Location: examples/
   ```

### Expected Result

- **Vertices**: ~24 control points (8 around × 3 height)
- **Faces**: ~18 quad faces
- **Shape**: Cylindrical vessel with rounded bottom and flared top
- **Curvature**:
  - Parabolic (cylindrical body)
  - Elliptic (rounded bottom)
  - Mixed (flared rim)
- **File size**: ~70 KB

---

## Example 4: double_bulge.3dm

**Purpose**: Symmetry detection example
**Difficulty**: Intermediate
**Time to create**: 8 minutes

### Step-by-Step Instructions

1. **Open Rhino**:
   ```
   File → New
   Template: Small Objects - Millimeters
   ```

2. **Create elongated sphere**:
   ```
   Command: SubDSphere
   Center: 0,0,0
   Radius: 40

   Command: SetPt
   Action: Select top point
   To: 0,0,80

   Action: Select bottom point
   To: 0,0,-80

   Result: Elongated in Z direction
   ```

3. **Add edge loops**:
   ```
   Command: SubDInsertEdge
   Action: Add horizontal edge loop at Z=40

   Command: SubDInsertEdge
   Action: Add horizontal edge loop at Z=-40
   ```

4. **Create right bulge**:
   ```
   Command: SetPt
   Action: Select points on right side (+X) near Z=40
   From: Original
   To: Move in +X direction by 25 units

   Result: Bulge on right at upper area
   ```

5. **Create left bulge (symmetric)**:
   ```
   Command: SetPt
   Action: Select points on left side (-X) near Z=-40
   From: Original
   To: Move in -X direction by 25 units

   Result: Bulge on left at lower area (mirror of right)
   ```

6. **Create connecting neck**:
   ```
   Command: SetPt
   Action: Select edge loop at Z=0 (middle)
   From: Original
   To: Move radially inward by 15 units

   Result: Narrow waist connecting two bulges
   ```

7. **Verify symmetry**:
   ```
   Command: Front view (F)
   Action: Check silhouette is symmetric about XZ plane

   Command: Right view (R)
   Action: Verify bulges visible and balanced
   ```

8. **Final checks**:
   ```
   Command: SubDDisplayToggle
   Command: SubDRepair
   Command: ShowEdges
   ```

9. **Save**:
   ```
   File → Save As
   Name: double_bulge.3dm
   Location: examples/
   ```

### Expected Result

- **Vertices**: ~32 control points
- **Faces**: ~28 quad faces
- **Shape**: Two bulges connected by narrow neck
- **Symmetry**: Mirror symmetric about XZ plane
- **Curvature**: Complex with symmetric features
- **File size**: ~90 KB

---

## Example 5: sculpture_organic.3dm

**Purpose**: Advanced complex form
**Difficulty**: Advanced
**Time to create**: 15-20 minutes

### Step-by-Step Instructions

1. **Open Rhino**:
   ```
   File → New
   Template: Small Objects - Millimeters
   ```

2. **Create detailed base**:
   ```
   Command: SubDSphere
   Center: 0,0,0
   Radius: 50
   ```

3. **Add extensive edge loops**:
   ```
   Command: SubDInsertEdge
   Action: Add 4-5 horizontal edge loops

   Command: SubDInsertEdge
   Action: Add 4-5 vertical edge loops

   Result: ~60 control points
   ```

4. **Create multiple bulges**:
   ```
   Command: SetPt
   Action: Select cluster of points (upper right)
   To: Move outward 20-30 units

   Repeat: 2-3 more bulges in different locations
   Result: Multiple convex regions
   ```

5. **Create valleys**:
   ```
   Command: SetPt
   Action: Select clusters between bulges
   To: Move inward 15-25 units

   Repeat: 2-3 valleys
   Result: Multiple concave regions
   ```

6. **Add asymmetric features**:
   ```
   Command: SetPt
   Action: Randomly move individual points
   Magnitude: 5-15 units in various directions

   Repeat: 10-15 times
   Result: Highly organic, no symmetry
   ```

7. **Create dramatic transitions**:
   ```
   Command: SetPt
   Action: Select points at transition between bulge and valley
   To: Adjust to create sharp transition

   Repeat: Multiple locations
   Result: Saddle regions and dramatic curvature changes
   ```

8. **Add fine detail**:
   ```
   Command: SetPt
   Action: Individual point adjustments for character

   Repeat: 5-10 times
   Result: Unique sculptural form
   ```

9. **Verify complexity**:
   ```
   Command: SubDDisplayToggle
   Action: Check for extreme curvature variation

   Command: CurvatureAnalysis (if available)
   Action: Verify mix of curvature types
   ```

10. **Final repairs**:
    ```
    Command: SubDRepair
    Command: ShowEdges
    Command: What
    ```

11. **Save**:
    ```
    File → Save As
    Name: sculpture_organic.3dm
    Location: examples/
    ```

### Expected Result

- **Vertices**: ~60 control points
- **Faces**: ~55 quad faces
- **Shape**: Highly complex organic sculpture
- **Curvature**: Extreme variation - all types present
- **Features**:
  - Multiple bulges
  - Multiple valleys
  - Saddle regions
  - No symmetry
  - Dramatic transitions
- **File size**: ~150-200 KB

---

## General Tips

### Best Practices

1. **Use SubD primitives**:
   - Start with SubDSphere, SubDCylinder, SubDBox
   - Don't convert from meshes or Breps

2. **Gradual edits**:
   - Make small adjustments
   - Use SubDDisplayToggle frequently to check
   - Undo (Ctrl+Z) if result looks wrong

3. **Keep valid topology**:
   - Run SubDRepair before saving
   - Check for naked edges
   - Verify with What command

4. **Test in app**:
   - After creating, test in Ceramic Mold Analyzer
   - Verify it transfers correctly
   - Check analysis results match expectations

### Common Issues

**Problem**: SubD looks faceted

**Solution**:
```
Command: SubDDisplayToggle
Action: Switch to smooth display
```

**Problem**: Naked edges appear

**Solution**:
```
Command: SubDRepair
Command: SubDFillHole (if holes exist)
```

**Problem**: Object becomes mesh instead of SubD

**Solution**:
- Don't use mesh operations
- Don't use standard transformation tools on faces
- Use SubD-specific commands only

**Problem**: Too much detail

**Solution**:
```
Command: SubDReduceEdges
Action: Simplify by removing edge loops
```

---

## Verification Checklist

Before saving each example, verify:

- [ ] Object type is SubD (not mesh or Brep)
- [ ] No naked edges
- [ ] Smooth display looks good
- [ ] Appropriate complexity (vertex/face count)
- [ ] Curvature variation appropriate for example
- [ ] SubDRepair runs without errors
- [ ] File saves successfully

---

## File Organization

```
examples/
├── simple_vessel.3dm          (Create first)
├── cylinder_vessel.3dm        (Create second)
├── complex_form.3dm           (Create third)
├── double_bulge.3dm           (Create fourth)
├── sculpture_organic.3dm      (Create fifth - most complex)
├── README.md                  (Already created)
└── CREATE_EXAMPLE_FILES.md    (This file)
```

---

## Testing Your Examples

After creating each file:

1. **Test in Rhino**:
   ```
   Command: What
   Command: ShowEdges
   Command: Check
   ```

2. **Test in desktop app**:
   - Setup Grasshopper bridge
   - Load example
   - Connect to app
   - Verify geometry appears

3. **Test analysis**:
   - Run recommended lens
   - Verify expected region count
   - Check Unity Strength scores
   - Compare with expected results in README.md

---

## Advanced: Creating Custom Examples

To create your own examples:

1. **Start simple**: Use primitives
2. **Add purpose**: What technique does it demonstrate?
3. **Target difficulty**: Beginner, Intermediate, or Advanced
4. **Document**:
   - Add to examples/README.md
   - Include expected results
   - Note learning objectives
5. **Test thoroughly**: Multiple lenses, different parameters
6. **Consider tutorial**: If unique, write step-by-step guide

---

## Troubleshooting

### Rhino Commands Not Working

**Issue**: SubD commands not available

**Solution**:
- Ensure Rhino 8 or later
- Rhino 7 has limited SubD support
- Check command spelling (case-insensitive)

### SubD Looks Wrong

**Issue**: Unexpected shape after edits

**Solution**:
- Undo (Ctrl+Z) to last good state
- Use SubDDisplayToggle to see both cage and limit
- Check control point positions
- Verify topology hasn't changed unexpectedly

### File Too Large

**Issue**: .3dm file is very large

**Solution**:
- Reduce edge loops
- Simplify control cage
- Remove render mesh (should be automatic for SubD)
- Check for duplicate objects

---

## Time Estimates

Creating all 5 examples:

- simple_vessel.3dm: 5 minutes
- cylinder_vessel.3dm: 5 minutes
- double_bulge.3dm: 8 minutes
- complex_form.3dm: 15 minutes
- sculpture_organic.3dm: 20 minutes

**Total**: ~50-60 minutes

---

## Next Steps

After creating example files:

1. Follow tutorials in `docs/TUTORIAL.md`
2. Experiment with different lenses
3. Try parameter variations
4. Create your own examples
5. Share interesting results!

---

**Document Version**: 1.0
**Last Updated**: November 2025
**Author**: Agent 67 - Day 10 API Sprint
**Related Files**: `examples/README.md`, `docs/TUTORIAL.md`
