# Ceramic Mold Analyzer - User Guide

**Version**: 0.5.0
**Date**: November 10, 2025
**Status**: Phase 0 Complete + Day 10 Documentation

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Interface Overview](#2-interface-overview)
3. [Rhino Integration](#3-rhino-integration)
4. [Analysis Workflows](#4-analysis-workflows)
5. [Region Manipulation](#5-region-manipulation)
6. [Constraint Validation](#6-constraint-validation)
7. [Mold Generation](#7-mold-generation)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Getting Started

### 1.1 What is Ceramic Mold Analyzer?

Ceramic Mold Analyzer is a desktop application that discovers **natural mathematical decompositions** in subdivision surface (SubD) geometries to create slip-casting ceramic molds for translucent porcelain light fixtures.

**Core Philosophy**: *"The seams are not flaws to hide but truths to celebrate"* — Inspired by Peter Pincus

The application uses multiple mathematical "lenses" (curvature analysis, spectral decomposition, flow patterns) to reveal inherent structure in 3D forms, creating mold boundaries that align with the form's mathematical coherences rather than imposing arbitrary divisions.

**Key Principle - Lossless Until Fabrication**: The system maintains **exact mathematical representation** from input SubD through all analysis. Approximation occurs **only once** at final fabrication export (G-code/STL).

<!-- Screenshot: Main window overview -->

### 1.2 Installation

#### System Requirements

| Requirement | Minimum | Recommended |
|------------|---------|-------------|
| **OS** | macOS 12, Ubuntu 20.04, Debian 11 | macOS 14, Ubuntu 22.04 |
| **CPU** | 2 cores | 4+ cores |
| **RAM** | 4 GB | 8+ GB |
| **Python** | 3.11 | 3.12 |
| **CMake** | 3.20 | 3.28+ |
| **Rhino** | Rhino 8+ (for live sync) | Rhino 8+ |

#### Quick Installation

**Step 1: Clone Repository**
```bash
git clone https://github.com/yourusername/latent.git
cd latent
```

**Step 2: Install System Dependencies**

**macOS:**
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install cmake opensubdiv python@3.12
```

**Ubuntu 22.04+:**
```bash
sudo apt-get update
sudo apt-get install cmake libosd-dev pybind11-dev python3.11 python3.11-venv python3.11-dev
```

**Step 3: Create Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

**Step 4: Install Python Dependencies**
```bash
pip install -r requirements.txt
```

**Step 5: Build C++ Core**
```bash
cd cpp_core
mkdir -p build && cd build
cmake ..
make -j$(nproc)  # Linux
# OR
make -j$(sysctl -n hw.ncpu)  # macOS
cd ../..
```

**Step 6: Verify Installation**
```bash
python3 -c "import sys; sys.path.insert(0, 'cpp_core/build'); import cpp_core; print('✅ Installation successful!')"
```

**Detailed installation instructions**: See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)

### 1.3 Launching the Application

**Quick Launch (Recommended):**
```bash
python3 launch.py
```

**Or activate environment first:**
```bash
source venv/bin/activate && python3 launch.py
```

The application will open with:
- Main window with 4 viewports (default layout)
- Menu system (File, Edit, Analysis, View, Help)
- Dockable panels (Analysis, Regions, Constraints, Selection Info, Debug Console)
- Status bar with Rhino connection status

<!-- Screenshot: First launch window -->

### 1.4 First Analysis Walkthrough

**Quick Start: Analyzing Test Geometry**

1. **Launch the application**
   ```bash
   python3 launch.py
   ```

2. **Load test geometry**
   - Go to **View → Show Test SubD Sphere** or **Show Test SubD Torus**
   - You should see the geometry displayed in all viewports

3. **Run your first analysis**
   - Click the **📐 Curvature** button in the Analysis toolbar
   - Or go to **Analysis → Curvature Lens**
   - The application will analyze the geometry and discover natural regions

4. **Explore the results**
   - Check the **Regions** panel (right side) to see discovered regions
   - Each region shows its:
     - ID and name
     - Unity principle (mathematical coherence)
     - Resonance score (0.0-1.0, higher = better alignment)
     - Pin status

5. **Interact with regions**
   - Click a region in the list to select it
   - Click the **Pin** checkbox to lock it from re-analysis
   - Select different regions to see them highlighted in viewports

6. **Try different views**
   - Use **View → Viewport Layout** to change layouts:
     - **Alt+1**: Single viewport
     - **Alt+2**: Two horizontal
     - **Alt+3**: Two vertical
     - **Alt+4**: Four grid (default)

**Next Steps:**
- Connect to Rhino to analyze your own geometry (see Section 3)
- Try different mathematical lenses (see Section 4)
- Refine regions by pinning and re-analyzing (see Section 5)

---

## 2. Interface Overview

### 2.1 Main Window Layout

The application follows a professional CAD interface layout:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File  Edit  Analysis  View  Help          [Edit Toolbar] ┃
┃━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┃
┃ S P E V | 🌊 〰️ 📐 🔷 | 🔨 Generate | 📤 Send to Rhino  ┃
┃━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┃
┃                                        ┃                  ┃
┃                                        ┃   Analysis       ┃
┃         Viewport 1 (Top)               ┃   Panel          ┃
┃                                        ┃                  ┃
┃                                        ┣━━━━━━━━━━━━━━━━━━┃
┃━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┃                  ┃
┃                        ┃               ┃   Regions        ┃
┃  Viewport 3 (Front)    ┃  Viewport 4   ┃   List           ┃
┃                        ┃  (Perspective) ┃                  ┃
┃                        ┃               ┃                  ┃
┃━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┃                  ┃
┃                                        ┃  Constraints     ┃
┃      Debug Console                     ┃  (Tabbed)        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━┛
┃ ● Connected  |  Ready                                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

<!-- Screenshot: Annotated main window layout -->

**Components:**
1. **Menu Bar** - File operations, editing, analysis, view controls, help
2. **Edit Mode Toolbar** - Switch between S/P/E/V modes
3. **Analysis Toolbar** - Quick access to lenses and mold generation
4. **Viewports** - 3D visualization with Rhino-compatible controls
5. **Dockable Panels** - Analysis, Regions, Constraints, Selection Info, Debug Console
6. **Status Bar** - Connection status and messages

### 2.2 Viewports

#### Viewport Types

The application supports multiple viewport types that can be displayed simultaneously:

- **Top View** - Orthographic view from above (Z-axis)
- **Front View** - Orthographic view from front (Y-axis)
- **Right View** - Orthographic view from side (X-axis)
- **Perspective** - 3D perspective view with free rotation

#### Viewport Layouts

Switch layouts using **View → Viewport Layout** or keyboard shortcuts:

| Layout | Shortcut | Description |
|--------|----------|-------------|
| **Single** | Alt+1 | One large viewport |
| **Two Horizontal** | Alt+2 | Two viewports side-by-side |
| **Two Vertical** | Alt+3 | Two viewports stacked |
| **Four Grid** | Alt+4 | Four viewports in grid (default) |

<!-- Screenshot: Different viewport layouts -->

#### Viewport Navigation (Rhino-Compatible)

**IMPORTANT**: Controls match Rhino 8 for seamless workflow continuity.

**Mouse Controls:**

| Action | Control |
|--------|---------|
| **Select object** | LEFT click |
| **Rotate/Orbit view** | RIGHT drag or MIDDLE drag |
| **Pan view** | Shift + RIGHT drag |
| **Zoom** | Mouse wheel or Ctrl + RIGHT drag |
| **Reset camera** | Space bar |

**Multi-Selection:**
- **Shift + Left-click** - Add to selection
- **Ctrl + Left-click** - Remove from selection
- **Esc** - Clear selection

**Sub-object Selection:**
- **Ctrl + Shift + Left-click** - Select face/edge/vertex (in appropriate edit mode)

<!-- Screenshot: Viewport navigation controls diagram -->

### 2.3 Edit Modes

The application has four edit modes for working with different elements of the geometry:

| Mode | Key | Icon | Description | Use Case |
|------|-----|------|-------------|----------|
| **Solid** | S | 🔲 | View-only mode | Viewing, analysis, no selection |
| **Panel** | P | 🔷 | Select faces | Creating regions, face-level editing |
| **Edge** | E | 📏 | Select edges | Adjusting region boundaries |
| **Vertex** | V | ⚫ | Select vertices | Fine-tuning boundaries |

**Switching Modes:**
- Press **S**, **P**, **E**, or **V** keys
- Click mode buttons in Edit Mode Toolbar
- Selection behavior changes based on active mode

<!-- Screenshot: Edit mode toolbar with all modes -->

**Edit Mode Toolbar Features:**
- **Mode Selection** - Four toggle buttons (S/P/E/V)
- **Selection Info** - Shows count of selected elements
- **Selection Operations**:
  - Clear Selection (Esc)
  - Select All (Ctrl+A)
  - Invert Selection (Ctrl+I)
  - Grow Selection (Ctrl+>)
  - Shrink Selection (Ctrl+<)

### 2.4 Dockable Panels

#### Analysis Panel

Controls for running mathematical decomposition analyses.

**Features:**
- **Lens Selection** - Choose mathematical lens:
  - Flow (Geodesic) - Water flow patterns
  - Spectral (Vibration) - Laplace-Beltrami eigenfunctions
  - Curvature (Ridge/Valley) - Differential geometry
  - Topological - Morse function critical points
- **Parameters** - Adjust sensitivity, region size, tolerances
- **Analyze Button** - Run selected lens on current geometry
- **Status** - Shows current analysis state

<!-- Screenshot: Analysis panel -->

#### Regions Panel

Displays discovered regions from analysis.

**Region List shows:**
- **ID** - Unique region identifier
- **Unity Principle** - Mathematical coherence description
- **Strength** - Resonance score (0.0-1.0)
- **Pin Checkbox** - Lock region from re-analysis

**Interactions:**
- **Click region** - Select and highlight in viewport
- **Pin/Unpin** - Toggle pin checkbox
- **Right-click** - Context menu:
  - Edit Boundary
  - Properties
  - Merge with...
  - Split Region
  - Delete

<!-- Screenshot: Regions panel with multiple regions -->

**Region Colors:**

Regions are color-coded by resonance score:
- **Green tones** (0.8-1.0) - Excellent mathematical coherence
- **Yellow tones** (0.6-0.8) - Good coherence
- **Orange tones** (0.4-0.6) - Moderate coherence
- **Red tones** (0.0-0.4) - Poor coherence
- **Gray** - Pinned regions (locked)

#### Constraints Panel

Shows fabrication constraint validation results.

**Three-Tier Constraint System:**

1. **Physical Constraints** (MUST OBEY - Binary Pass/Fail)
   - ❌ Undercuts prevent demolding
   - ❌ Trapped volumes cause air pockets
   - ❌ Inaccessible surfaces can't receive slip

2. **Manufacturing Constraints** (SHOULD OBEY - Warnings)
   - ⚠️ Insufficient draft angle (<0.5°)
   - ⚠️ Wall thickness too thin (<3mm) or thick (>6mm)
   - ⚠️ Wall thickness variation >25%
   - ⚠️ Seam gap too large (>1.27mm)

3. **Mathematical Constraints** (DOCUMENT - Artistic Choices)
   - 📝 Departures from discovered mathematical truth
   - 📝 Manual boundary adjustments
   - 📝 Merged regions with different unity principles

<!-- Screenshot: Constraints panel showing violations -->

#### Selection Info Panel

Shows details about currently selected elements (faces/edges/vertices).

**Information displayed:**
- **Count** - Number of selected elements
- **Type** - Face, Edge, or Vertex
- **Indices** - Element IDs
- **Properties** - Curvature, normals, positions (context-dependent)
- **Export to Region** - Create new region from selection

#### Debug Console

Developer console showing real-time application messages.

**Message types:**
- 🎨 Initialization
- 📍 Control hints
- 📡 Connection status
- 🔄 Geometry updates
- ✅ Success messages
- ⚠️ Warnings
- ❌ Errors

### 2.5 Menus

#### File Menu

| Action | Shortcut | Description |
|--------|----------|-------------|
| Load from Rhino | Ctrl+R | Load SubD from Grasshopper server |
| Start Live Sync | Ctrl+L | Enable automatic geometry updates |
| Stop Live Sync | - | Disable automatic updates |
| Refresh | F5 | Force geometry refresh |
| Connect to Rhino | Ctrl+O | Establish Grasshopper connection |
| Save Session | Ctrl+S | Save window layout and session |
| Quit | Ctrl+Q | Exit application |

#### Edit Menu

| Action | Shortcut | Description |
|--------|----------|-------------|
| Undo | Ctrl+Z | Undo last action |
| Redo | Ctrl+Shift+Z | Redo last undone action |
| Clear Selection | Esc | Clear current selection |
| Select All | Ctrl+A | Select all elements in current mode |
| Invert Selection | Ctrl+I | Invert current selection |
| Grow Selection | Ctrl+> | Grow selection to neighbors |
| Shrink Selection | Ctrl+< | Shrink selection boundary |

#### Analysis Menu

| Action | Description |
|--------|-------------|
| Flow Lens | Run geodesic flow analysis |
| Spectral Lens | Run Laplace-Beltrami eigenfunction analysis |
| Curvature Lens | Run differential geometry analysis |
| Topological Lens | Run Morse function analysis |

#### View Menu

| Action | Shortcut | Description |
|--------|----------|-------------|
| Single Viewport | Alt+1 | Switch to single viewport |
| Two Horizontal | Alt+2 | Switch to two horizontal viewports |
| Two Vertical | Alt+3 | Switch to two vertical viewports |
| Four Grid | Alt+4 | Switch to four grid viewports |
| Reset All Cameras | Space | Reset all viewports to fit geometry |
| Show Test Cube | - | Display test cube geometry |
| Show Test SubD Sphere | - | Display test sphere geometry |
| Show Test SubD Torus | - | Display test torus geometry |
| Show Colored Cube | - | Display region color demo |

---

## 3. Rhino Integration

### 3.1 Overview

The Rhino HTTP Bridge enables **EXACT SubD transfer** between Rhino and the desktop application, maintaining the **"Lossless Until Fabrication"** principle.

**Key Features:**
- ✅ **Exact SubD Representation** - No mesh conversion
- ✅ **Live Updates** - Changes in Rhino appear instantly
- ✅ **Bidirectional** - Send molds back to Rhino
- ✅ **HTTP Protocol** - Simple, reliable connection

<!-- Screenshot: Rhino and Latent connected -->

### 3.2 Starting the Grasshopper Server

**Step 1: Prepare Your SubD in Rhino**

1. Open **Rhino 8** or later
2. Create or load your SubD surface
3. Verify it's a valid SubD:
   - Type `What` in command line and click your object
   - Should show "subdivision surface" object type
   - Use `SubDDisplayToggle` to verify

<!-- Screenshot: SubD in Rhino viewport -->

**Step 2: Setup Grasshopper Component**

1. Open **Grasshopper** in Rhino (type `Grasshopper` in command line)

2. Create a **GhPython Script** component:
   - Double-click canvas
   - Type "Python"
   - Select **GhPython Script**

3. **Configure component inputs:**
   - Right-click component → **Manage Inputs/Outputs**
   - Add one input named `subd`
   - Set **Type Hint** to `SubD` (scroll down in list)
   - Set **Access** to `Item Access`

4. **Configure component output:**
   - Add one output named `status`
   - Type remains generic

<!-- Screenshot: GhPython component setup -->

**Step 3: Load Server Script**

1. Double-click the GhPython component to open editor

2. Copy contents of:
   ```
   latent/rhino/grasshopper_http_server_control_cage.py
   ```

3. Paste into Python editor

4. Click **OK** to close editor

**Step 4: Connect Your SubD**

1. Create a **SubD** parameter in Grasshopper
2. Right-click it → **Set one SubD**
3. Select your SubD in Rhino viewport
4. Connect the SubD parameter to the `subd` input

The component should display:
```
✅ Server running on http://localhost:8888
📦 SubD ready: [N] vertices, [M] faces
🔄 Exact control cage transfer mode
```

<!-- Screenshot: Grasshopper server running -->

### 3.3 Connecting from Desktop Application

**Method 1: Manual Connection**

1. Launch Ceramic Mold Analyzer:
   ```bash
   python3 launch.py
   ```

2. Click **File → Connect to Rhino** (Ctrl+O)

3. If successful, you'll see:
   - Status bar: "Connected to Rhino (manual push mode)"
   - Connection indicator: 🟢 Green dot "● Connected"

**Method 2: Manual Push (Port 8800)**

The application also listens for geometry pushed manually from Grasshopper on port 8800. This avoids conflicts with macOS ControlCenter (which uses port 5000).

In Grasshopper:
1. Create a button component
2. Connect it to trigger the push script
3. Click button to send geometry

<!-- Screenshot: Connection status indicator -->

### 3.4 Sending SubD to Desktop

**Automatic Mode (Live Sync):**

1. Once connected, go to **File → Start Live Sync** (Ctrl+L)

2. The application will now automatically detect changes:
   - Modify your SubD in Rhino (move vertices, add faces, etc.)
   - Desktop app updates within 1 second
   - No need to manually refresh

3. Connection indicator shows: 🟢 "● Live sync active"

**Manual Mode:**

1. If not using live sync, load geometry manually:
   - **File → Load from Rhino** (Ctrl+R)
   - Or press **F5** to force refresh

**What Gets Transferred:**

The system transfers the **control cage** (exact, lossless):
- **Control vertices** - Exact 3D positions
- **Face topology** - Connectivity information
- **Edge creases** - Sharpness values for hard edges
- **Vertex tags** - Corner/smooth/crease classifications

**What Does NOT Happen:**
- ❌ NO conversion to mesh
- ❌ NO approximation or discretization
- ❌ NO loss of precision

<!-- Screenshot: Geometry appearing in viewports after connection -->

### 3.5 Receiving Molds Back in Rhino

After generating molds in the desktop application, you can send them back to Rhino for fabrication:

**Step 1: Generate Molds**
1. Run analysis and pin desired regions
2. Click **🔨 Generate Molds** in Analysis toolbar
3. Application creates NURBS surfaces with draft angles and wall thickness

**Step 2: Send to Rhino**
1. Click **📤 Send to Rhino** in Analysis toolbar
2. Mold geometry is sent back via HTTP bridge
3. Molds appear in Rhino viewport

**Step 3: Export for Fabrication**
1. In Rhino, select mold geometry
2. Export to STL for 3D printing:
   - Type `Export` or `-Export` in command line
   - Choose "STL Files (*.stl)"
   - Set options:
     - File Type: Binary
     - Mesh Density: High
   - Save file

3. Or export G-code directly from your slicer software

<!-- Screenshot: Molds appearing back in Rhino -->

**This is the ONLY approximation step** - SubD to mesh happens at final STL/G-code export, maintaining the lossless principle throughout analysis and design.

---

## 4. Analysis Workflows

### 4.1 Mathematical Lenses Overview

The application uses different mathematical "lenses" to reveal inherent structure in your geometry. Each lens discovers different aspects of the form's mathematical truth.

| Lens | Mathematical Basis | Best For | Implemented |
|------|-------------------|----------|-------------|
| **Differential** | Curvature (Gaussian, Mean, Principal) | Organic forms with clear feature lines | ✅ Yes |
| **Spectral** | Laplace-Beltrami eigenfunctions | Symmetric forms, vibration modes | ✅ Yes |
| **Flow** | Geodesic flow patterns | Complex topologies, drainage basins | 🚧 Future |
| **Topological** | Morse function critical points | Distinct topological features | 🚧 Future |

<!-- Screenshot: Lens selection toolbar -->

### 4.2 Differential Lens (Curvature-Based)

**Mathematical Foundation:**

The Differential Lens analyzes curvature properties computed from the **exact SubD limit surface**:

- **Gaussian curvature** K = κ₁ × κ₂ (intrinsic curvature)
- **Mean curvature** H = (κ₁ + κ₂) / 2 (extrinsic curvature)
- **Principal curvatures** κ₁, κ₂ (max/min normal curvatures)

Faces are classified based on curvature signatures:
- **Elliptic** (K > 0): Bowl-like, convex/concave
- **Hyperbolic** (K < 0): Saddle-like, anticlastic
- **Parabolic** (K ≈ 0, |H| > 0): Cylindrical, developable
- **Planar** (K ≈ 0, H ≈ 0): Flat

<!-- Diagram: Curvature types visualization -->

**When to Use:**
- Forms with clear ridges and valleys
- Organic shapes with varied curvature
- Objects with distinct convex/concave regions
- When you want seams to follow natural feature lines

**Running Differential Analysis:**

1. **Load Geometry**
   - Connect to Rhino and load your SubD
   - Or use test geometry: **View → Show Test SubD Torus**

2. **Select Differential Lens**
   - Click **📐 Curvature** in Analysis toolbar
   - Or go to **Analysis → Curvature Lens**

3. **Adjust Parameters** (in Analysis Panel)
   - **Curvature Threshold**: Sensitivity to curvature changes (default: 0.1)
   - **Min Region Size**: Minimum faces per region (default: 10)
   - **Coherence Tolerance**: How uniform curvature must be (default: 0.3)

4. **Run Analysis**
   - Click **Analyze** button
   - Processing message appears in status bar
   - Debug console shows progress

5. **View Results**
   - Discovered regions appear in Regions panel
   - Each region shows:
     - Classification type (Elliptic/Hyperbolic/etc.)
     - Resonance score (coherence measure)
     - Face count
   - Regions are color-coded in viewport

<!-- Screenshot: Differential analysis results -->

**Interpreting Results:**

**Resonance Score Meaning:**
- **0.8-1.0** (Green) - Excellent: Highly uniform curvature, form "wants" this division
- **0.6-0.8** (Yellow) - Good: Coherent region with some variation
- **0.4-0.6** (Orange) - Moderate: Usable but not ideal
- **0.0-0.4** (Red) - Poor: Try different lens or adjust parameters

**Example: Torus Analysis**

For a torus, differential lens typically discovers:
- **Outer convex region** (top outer surface) - Elliptic, high resonance
- **Inner concave region** (bottom inner surface) - Elliptic, high resonance
- **Saddle regions** (sides) - Hyperbolic, medium resonance
- **Transition zones** - Parabolic, lower resonance

### 4.3 Spectral Lens (Eigenfunction-Based)

**Mathematical Foundation:**

The Spectral Lens uses **Laplace-Beltrami eigenfunctions** - the vibrational modes of the surface:

- Compute discrete Laplace-Beltrami operator on SubD mesh
- Solve eigenvalue problem: Δφ = λφ
- Use eigenfunctions (φ) to segment surface into nodal domains
- Lower eigenfunctions capture global structure
- Higher eigenfunctions capture fine detail

Think of it as: *"How would this surface vibrate like a drum?"*

<!-- Diagram: Eigenfunction visualization -->

**When to Use:**
- Forms with rotational or reflective symmetry
- When differential lens produces too many small regions
- Objects where vibration modes reveal natural structure
- Discovering hidden mathematical symmetries

**Running Spectral Analysis:**

1. **Load Geometry**
   - Connect to Rhino and load your SubD
   - Works best on closed or nearly-closed surfaces

2. **Select Spectral Lens**
   - Click **〰️ Spectral** in Analysis toolbar
   - Or go to **Analysis → Spectral Lens**

3. **Adjust Parameters** (in Analysis Panel)
   - **Number of Eigenmodes**: How many modes to compute (default: 10)
   - **Mode Selection**: Which modes to use for segmentation (default: modes 2-5)
   - **Nodal Threshold**: Sensitivity to zero-crossings (default: 0.01)
   - **Min Region Size**: Minimum faces per region (default: 10)

4. **Run Analysis**
   - Click **Analyze** button
   - Eigenvalue computation may take a few seconds
   - Watch debug console for progress

5. **View Results**
   - Regions correspond to nodal domains
   - Typically produces 2-8 large symmetric regions
   - Good for forms with global structure

<!-- Screenshot: Spectral analysis results on symmetric object -->

**Spectral Visualization Widget:**

The spectral lens includes a special visualization showing:
- **Eigenvalue spectrum** - Plot of eigenvalues
- **Mode selection** - Which modes were used
- **Eigenfunction color map** - Visualization of selected modes

Access via: **View → Spectral Visualization** (when spectral lens is active)

<!-- Screenshot: Spectral visualization widget -->

**Example: Sphere Analysis**

For a sphere, spectral lens discovers regions based on spherical harmonics:
- Mode 2 (first non-trivial): Divides into top/bottom hemispheres
- Mode 3: Divides into front/back/sides
- Combined modes create symmetric multi-region decomposition

### 4.4 Comparing Lenses

**Multi-Lens Workflow:**

The power of the application is trying multiple lenses and comparing results:

1. **Run First Lens** (e.g., Differential)
   - Analyze geometry
   - Review results
   - Pin regions you like (click Pin checkbox)

2. **Run Second Lens** (e.g., Spectral)
   - Switch to different lens
   - Run analysis again
   - **Pinned regions are preserved**
   - Only unpinned areas are re-analyzed

3. **Compare Results**
   - Side-by-side viewport comparison:
     - **Alt+2** for two horizontal viewports
     - Show differential regions in left viewport
     - Show spectral regions in right viewport
   - Look for:
     - Regions that appear in both analyses (high confidence)
     - Complementary insights from different lenses
     - Trade-offs between local detail (differential) and global structure (spectral)

4. **Iterate**
   - Pin best regions from both analyses
   - Try third lens on remaining areas
   - Manually adjust boundaries as needed

<!-- Screenshot: Side-by-side lens comparison -->

**Lens Selection Guidelines:**

| Geometry Type | Primary Lens | Secondary Lens |
|--------------|--------------|----------------|
| Organic vase/bowl | Differential | Spectral |
| Symmetric sculpture | Spectral | Differential |
| Complex topology | Flow (future) | Differential |
| Geometric/architectural | Topological (future) | Differential |

### 4.5 Resonance Scores

**What is Resonance?**

Resonance score (0.0-1.0) measures how well a region aligns with the form's mathematical coherences:

```
Resonance = Mathematical Unity / Internal Variation
```

High resonance = form "wants" this decomposition

**Score Interpretation:**

| Score | Meaning | Action |
|-------|---------|--------|
| **0.9-1.0** | Perfect | Pin immediately, excellent mold boundary |
| **0.8-0.9** | Excellent | Very good, likely pin |
| **0.7-0.8** | Good | Usable, may need minor adjustments |
| **0.6-0.7** | Moderate | Consider re-analyzing or adjusting |
| **0.4-0.6** | Fair | Try different lens or change parameters |
| **0.0-0.4** | Poor | Re-analyze required |

**Factors Affecting Resonance:**

1. **Curvature Uniformity** (Differential Lens)
   - Low standard deviation of Gaussian curvature
   - Consistent mean curvature across region

2. **Eigenfunction Coherence** (Spectral Lens)
   - Clean nodal domain boundaries
   - Minimal noise in eigenfunction values

3. **Region Size**
   - Too small regions typically have lower scores
   - Minimum size parameter helps merge tiny regions

4. **Boundary Quality**
   - Smooth, continuous boundaries score higher
   - Jagged or fragmented boundaries score lower

**Using Resonance for Decision Making:**

- **High-resonance regions**: Pin and preserve
- **Low-resonance regions**: Re-analyze with different lens or parameters
- **Mixed scores**: Pin high-scoring regions, re-analyze low-scoring ones
- **All low scores**: Adjust analysis parameters or try different lens

---

## 5. Region Manipulation

### 5.1 Selecting Regions

**Methods to Select Regions:**

1. **Click in Regions Panel**
   - Click region name or row in list
   - Selected region highlights in yellow in viewports

2. **Click in Viewport** (Panel Mode)
   - Switch to Panel mode (press **P**)
   - Click face in viewport
   - Region containing that face is selected

3. **Keyboard Navigation**
   - **Up/Down arrows** in region list to navigate

<!-- Screenshot: Selected region highlighted -->

**Visual Feedback:**

When region is selected:
- **Viewport**: Region highlighted with yellow outline
- **Regions Panel**: Row highlighted
- **Status Bar**: Shows "Selected: region_id"
- **Constraint Panel**: Updates to show constraints for that region

### 5.2 Pinning and Unpinning Regions

**What is Pinning?**

Pinning **locks** a region from being modified by future analyses:
- Pinned regions remain unchanged when you run analysis again
- Allows iterative refinement: pin good regions, re-analyze bad ones
- Visual indicator: Pinned regions turn gray in viewport

**How to Pin/Unpin:**

1. **Via Regions Panel**
   - Click the **Pin** checkbox next to region
   - ✓ = Pinned (locked)
   - ☐ = Unpinned (can be re-analyzed)

2. **Via Context Menu**
   - Right-click region in list
   - Select **Pin Region** or **Unpin Region**

3. **Via Keyboard**
   - Select region in list
   - Press **P** key to toggle pin state

<!-- Screenshot: Pinned vs unpinned regions -->

**Iterative Refinement Workflow:**

```
1. Run Differential Lens
2. Pin 3 good regions (high resonance)
3. Run Spectral Lens
   → Pinned regions unchanged
   → Only unpinned areas analyzed
4. Pin 2 more good regions from spectral
5. Run Differential again on remaining unpinned area
6. Continue until satisfied
```

**Undo/Redo:**

Pin operations are recorded in undo history:
- **Ctrl+Z** to undo pin/unpin
- **Ctrl+Shift+Z** to redo

### 5.3 Merging Regions

**When to Merge:**

- Two adjacent regions have similar properties
- Analysis over-segmented the form (too many small regions)
- You want a larger, unified mold piece
- Manufacturing constraints require fewer seams

**How to Merge:**

1. **Select First Region**
   - Click in Regions panel

2. **Initiate Merge**
   - Right-click → **Merge with...**
   - A merge dialog appears

3. **Select Second Region**
   - Click target region in list
   - Preview shows combined region in viewport

4. **Confirm Merge**
   - Click **OK** to confirm
   - New merged region appears in list
   - Old regions are removed

<!-- Screenshot: Merge dialog -->

**Merge Options:**

- **Inherit Properties**: Choose which region's properties to keep
  - Unity principle
  - Resonance score (or compute average)
  - Pin state (OR operation - merged is pinned if either was pinned)

- **Smooth Boundary**: Optionally smooth the internal boundary that was removed

**Undo Merge:**

- **Ctrl+Z** immediately after merge to undo
- Restores original two regions

### 5.4 Splitting Regions

**When to Split:**

- One region is too large (manufacturing constraint)
- Region contains distinct sub-features
- Analysis under-segmented the form
- You want to create custom sub-divisions

**How to Split:**

1. **Select Region**
   - Click region in Regions panel

2. **Initiate Split**
   - Right-click → **Split Region**
   - Or go to **Edit → Split Selected Region**

3. **Draw Split Line** (in Viewport)
   - Switch to Edge mode (press **E**)
   - Click edge sequence to define split path
   - Path must cross region from one boundary to another
   - Press **Enter** to confirm

4. **View Split Preview**
   - Two new regions shown in different colors
   - Can adjust split line before confirming

5. **Confirm Split**
   - Click **OK** in dialog
   - New regions appear in list

<!-- Screenshot: Split operation in progress -->

**Split Options:**

- **Split Method**:
  - **Manual Path**: Draw path with edges
  - **Curvature Ridge**: Automatically find curvature ridge line
  - **Geodesic Line**: Shortest path between two points

- **Properties Inheritance**: How to compute properties for new regions
  - Re-analyze each sub-region
  - Copy from parent region

**Undo Split:**

- **Ctrl+Z** to undo split and restore original region

### 5.5 Advanced Region Editing

**Boundary Editing:**

Fine-tune region boundaries face-by-face:

1. **Enable Boundary Edit Mode**
   - Right-click region → **Edit Boundary**
   - Region boundary edges highlight in yellow

2. **Adjust Boundary**
   - Switch to Panel mode (press **P**)
   - **Shift+Click** faces to add to region
   - **Ctrl+Click** faces to remove from region
   - Changes preview in real-time

3. **Confirm Changes**
   - Press **Enter** or click **Apply** in toolbar
   - Region updates with new boundary

4. **Cancel**
   - Press **Esc** or click **Cancel** to discard changes

<!-- Screenshot: Boundary editing mode -->

**Region Properties Dialog:**

Access detailed properties and settings:

1. **Open Dialog**
   - Right-click region → **Properties**
   - Or double-click region in list

2. **Edit Properties**
   - **Name**: Custom region name
   - **Unity Principle**: Description of mathematical coherence
   - **Pin State**: Toggle locked/unlocked
   - **Color**: Custom display color
   - **Notes**: Free-form notes

3. **View Statistics**
   - Face count
   - Surface area
   - Average curvature
   - Boundary length

<!-- Screenshot: Region properties dialog -->

---

## 6. Constraint Validation

### 6.1 Understanding the Three-Tier System

The application validates three levels of constraints, following slip-casting ceramic fabrication requirements:

**Hierarchy:**

```
┌─────────────────────────────────────────────────┐
│  1. PHYSICAL (Must Obey)                        │
│     ❌ Binary Pass/Fail                         │
│     Violations PREVENT casting                  │
├─────────────────────────────────────────────────┤
│  2. MANUFACTURING (Should Obey)                 │
│     ⚠️  Warnings                                │
│     Make production harder but possible         │
├─────────────────────────────────────────────────┤
│  3. MATHEMATICAL (Document)                     │
│     📝 Artistic Choices                         │
│     Departures from mathematical truth          │
└─────────────────────────────────────────────────┘
```

<!-- Diagram: Three-tier constraint pyramid -->

### 6.2 Physical Constraints (Binary)

**Must be satisfied or casting will fail.**

#### 1. Undercuts

**Definition**: Surface areas where the normal vector points away from the draw direction, preventing mold removal.

**Detection**: Application computes normal vectors and compares with pull direction (typically +Z):
```
undercut if: normal · pull_direction < 0
```

**Visualization**:
- Undercut regions shown in RED
- Intensity indicates severity (angle from vertical)

**How to Fix**:
- **Rotate**: Change pull direction (adjust draft vector)
- **Split Region**: Divide region at undercut boundary
- **Adjust Draft**: Increase draft angle to eliminate undercut

<!-- Screenshot: Undercut visualization -->

#### 2. Trapped Volumes

**Definition**: Enclosed volumes that would trap slip or air during casting.

**Detection**: Topological analysis identifies:
- Enclosed cavities with no opening
- Partially enclosed volumes with insufficient vent paths

**Visualization**:
- Trapped volumes shown in DARK RED
- Volume boundaries outlined

**How to Fix**:
- **Add Vent Holes**: Create vent paths in mold design
- **Modify Geometry**: Open trapped regions
- **Split Differently**: Change decomposition to avoid traps

#### 3. Inaccessible Surfaces

**Definition**: Interior surfaces that slip cannot reach during casting.

**Detection**: Ray-casting from pour opening to all surfaces:
```
inaccessible if: no clear path from opening
```

**How to Fix**:
- **Reorient Pour Opening**: Change mold orientation
- **Add Access Channels**: Create flow paths in mold
- **Split Region**: Expose previously hidden surfaces

### 6.3 Manufacturing Constraints (Warnings)

**Should be satisfied for easier production, but violations don't prevent casting.**

#### 1. Draft Angles

**Requirement**: Minimum 0.5° draft on vertical surfaces for easy demolding.

**Detection**: For each face, compute angle from vertical:
```
draft_angle = acos(normal · Z) - 90°
insufficient if: |draft_angle| < 0.5°
```

**Visualization**:
- Faces with insufficient draft shown in ORANGE
- Color intensity indicates how far below 0.5°

<!-- Screenshot: Draft angle visualization -->

**How to Fix**:
- **Increase Global Draft**: Adjust draft parameter (default 2°)
- **Local Draft Adjustment**: Apply extra draft to specific regions
- **Accept Risk**: Very slight draft (<0.5°) may still work with careful demolding

#### 2. Wall Thickness

**Requirements for Translucent Porcelain:**
- **Ceramic wall**: 3-6mm (optimal 4mm)
- **Variation**: <25% across piece
- **Plaster mold walls**: 1.5-2 inches (38-51mm)

**Detection**: Measure thickness at sample points:
```
too_thin if: thickness < 3mm
too_thick if: thickness > 6mm
variable if: std_dev / mean > 0.25
```

**Visualization**:
- Color-coded thickness heat map
- Blue = too thin, Red = too thick, Green = optimal

<!-- Screenshot: Wall thickness heat map -->

**How to Fix**:
- **Adjust Offset Parameter**: Change ceramic wall thickness
- **Add Reinforcement**: Thicken thin areas
- **Smooth Transitions**: Reduce thickness variation

#### 3. Seam Gap

**Requirement**: <0.05 inches (1.27mm) gap between mating surfaces.

**Detection**: Measure distance between adjacent region boundaries at seam.

**Visualization**:
- Excessive gaps shown in YELLOW at seam locations

**How to Fix**:
- **Adjust Region Boundaries**: Move boundaries to reduce gap
- **Merge Regions**: Eliminate problematic seam entirely
- **Add Registration Keys**: Improve mold alignment

### 6.4 Mathematical Constraints (Documentation)

**Not enforced - documents where artistic choices override mathematical truth.**

#### Tracked Departures:

1. **Manual Boundary Edits**
   - When you adjust boundaries by hand (not from analysis)
   - Records which faces were moved

2. **Merged Disparate Regions**
   - Merging regions with different unity principles
   - Different curvature types (elliptic + hyperbolic)

3. **Low Resonance Regions**
   - Regions with score <0.5 that you kept anyway
   - Documents that you're intentionally keeping weak mathematical coherence

4. **Split Forced Regions**
   - Splitting a high-coherence region for manufacturing
   - Form wanted one piece, but you need two

**Purpose**: Not to prevent these actions, but to **acknowledge** them. The seams become a dialogue between mathematical truth and material/manufacturing reality.

<!-- Screenshot: Mathematical constraint log -->

### 6.5 Viewing Violations

**Constraints Panel:**

Shows all detected violations organized by tier:

```
┌─ PHYSICAL ─────────────────────────┐
│ ❌ Region 3: Undercut detected     │
│    Angle: -12° (requires >0°)      │
│ ❌ Region 5: Trapped volume        │
│    Volume: 8.2 cm³                 │
└────────────────────────────────────┘
┌─ MANUFACTURING ────────────────────┐
│ ⚠️  Region 2: Insufficient draft   │
│    0.3° (requires ≥0.5°)           │
│ ⚠️  Region 4: Wall too thin         │
│    2.1mm (requires 3-6mm)          │
└────────────────────────────────────┘
┌─ MATHEMATICAL ─────────────────────┐
│ 📝 Region 1: Manual boundary edit  │
│    14 faces modified               │
│ 📝 Region 6: Low resonance kept    │
│    Score: 0.42 (suggest >0.6)      │
└────────────────────────────────────┘
```

**Clicking a violation:**
- Selects affected region
- Highlights problem area in viewport
- Shows details in properties panel

<!-- Screenshot: Constraints panel with violations -->

### 6.6 Fixing Undercuts

**Interactive Undercut Fixing:**

1. **Identify Undercut**
   - Click undercut violation in Constraints panel
   - Problem area highlights in RED in viewport

2. **Analyze Pull Direction**
   - Current pull direction shown with arrow
   - Undercut normals shown pointing away

3. **Try Fixing Methods** (in order of preference):

**Method A: Adjust Draft Angle**
1. Select region with undercut
2. Right-click → **Properties**
3. Increase **Local Draft Angle**
4. Real-time preview shows if undercut eliminated
5. If successful, click **Apply**

**Method B: Change Pull Direction**
1. Click **Adjust Pull Direction** button
2. Drag arrow in viewport to change direction
3. Watch undercut visualization update in real-time
4. Find direction that eliminates undercut
5. Click **Set Direction**

**Method C: Split Region**
1. Select region with undercut
2. Right-click → **Split Region**
3. Draw split line at undercut boundary
4. Creates two regions:
   - One pulled from top
   - One pulled from different direction
5. Each region can have different pull direction

<!-- Screenshot: Undercut fixing workflow -->

**Automatic Undercut Detection:**

Enable in **Analysis → Validate Constraints** (runs after each analysis):
- Real-time undercut checking
- Suggests optimal pull directions
- Recommends split locations

### 6.7 Adjusting Draft Angles

**Global Draft:**

Sets default draft angle for all regions.

1. **Analysis Panel** → **Mold Parameters**
2. Adjust **Draft Angle** slider (0.5° - 5°)
3. Default: 2° (good for most applications)
4. Preview updates in real-time

**Local Draft Override:**

Set different draft angle for specific region:

1. Select region
2. Right-click → **Properties**
3. Enable **Override Global Draft**
4. Set **Local Draft Angle**
5. Useful for:
   - Problem areas needing extra draft
   - Flat areas that can use minimal draft

<!-- Screenshot: Draft angle adjustment interface -->

**Draft Angle Guidelines:**

| Surface | Recommended Draft |
|---------|-------------------|
| Vertical walls | 2-3° |
| Near-vertical (80-90° from horizontal) | 3-5° |
| Shallow angles (30-60°) | 1-2° |
| Complex undercuts | 5° or split region |

**Visualizing Draft:**

- **View → Show Draft Analysis**
- Color-coded by draft angle:
  - Green: >2° (good)
  - Yellow: 0.5-2° (minimal)
  - Orange: 0.1-0.5° (risky)
  - Red: <0.1° (insufficient)

---

## 7. Mold Generation

### 7.1 Setting Parameters

Before generating molds, configure fabrication parameters:

**Access Mold Parameters:**
- **Analysis Panel** → **Mold Parameters** section
- Or right-click region → **Mold Settings**

<!-- Screenshot: Mold parameters panel -->

**Key Parameters:**

#### Ceramic Wall Thickness
- **Range**: 3-6mm
- **Default**: 4mm (optimal for translucency)
- **Purpose**: Final ceramic piece wall thickness

**Considerations:**
- Thinner (3mm) = more translucent but fragile
- Thicker (6mm) = stronger but less translucent
- Keep variation <25% across piece

#### Draft Angle
- **Range**: 0.5-5°
- **Default**: 2°
- **Purpose**: Taper for demolding

**Guidelines:**
- Minimum 0.5° (absolute requirement)
- 2° = standard for most forms
- 3-5° = complex undercuts or deep cavities

#### Plaster Mold Thickness
- **Range**: 1.5-2 inches (38-51mm)
- **Default**: 2 inches (51mm)
- **Purpose**: Plaster mold walls around ceramic cavity

**Considerations:**
- Thicker = more absorption, longer dry time
- Thinner = less material but may be fragile
- Must have structural integrity

#### Registration Keys
- **Size**: 1/4 inch (6.35mm)
- **Distance from Edge**: 1/4 inch
- **Count**: Automatic based on seam length
- **Purpose**: Alignment between mold pieces

**Options:**
- Enable/disable registration keys
- Auto-place or manual placement
- Key shape: Cylindrical, Conical, or Custom

#### Seam Offset
- **Range**: 0-2mm
- **Default**: 0.5mm
- **Purpose**: Slight overlap/gap at seam for cleanup

<!-- Screenshot: Mold parameters with annotations -->

### 7.2 Generating NURBS Surfaces

**Generation Process:**

The application converts parametric regions to NURBS molds:

```
Parametric Region (face_id, u, v)
    ↓
Exact Limit Surface Evaluation (C++ OpenSubdiv)
    ↓
Point Cloud (high density sampling)
    ↓
NURBS Surface Fitting (C++ OpenCASCADE)
    ↓
Draft Transformation (exact vector math)
    ↓
Boolean Operations (cavity + mold walls)
    ↓
NURBS Mold Solid
```

**Step-by-Step:**

1. **Prepare Regions**
   - Run analysis and refine regions
   - Pin regions you want to generate
   - Validate constraints (no physical violations)

2. **Set Parameters**
   - Review mold parameters (wall thickness, draft, etc.)
   - Adjust as needed

3. **Initiate Generation**
   - Click **🔨 Generate Molds** in Analysis toolbar
   - Or **File → Generate Molds**

4. **Watch Progress**
   - Progress dialog shows:
     - Current region being processed
     - Step (surface fitting, draft, boolean ops)
     - Estimated time remaining

<!-- Screenshot: Mold generation progress dialog -->

5. **Review Results**
   - Generated molds appear in viewport
   - Color-coded by region
   - **Molds Panel** lists all generated molds with:
     - Region source
     - Volume
     - Surface area
     - Validation status

6. **Inspect Quality**
   - Rotate viewports to check:
     - Draft angles applied correctly
     - Registration keys present
     - Wall thickness uniform
     - No self-intersections

**NURBS Surface Quality:**

The application ensures high-quality NURBS:
- **Continuity**: G2 continuous (curvature continuous)
- **Degree**: Cubic (degree 3) or quintic (degree 5)
- **Control Points**: Automatically determined for optimal fit
- **Deviation**: <0.01mm from exact limit surface

<!-- Screenshot: Generated NURBS molds in viewport -->

### 7.3 Exporting to Rhino

**Send Molds Back:**

Once generated, send molds to Rhino for fabrication preparation:

1. **Verify Generation**
   - All desired molds generated successfully
   - No constraint violations
   - Quality inspection passed

2. **Export to Rhino**
   - Click **📤 Send to Rhino** in Analysis toolbar
   - Or **File → Send to Rhino**

3. **Transfer Process**
   - Molds serialized as NURBS Breps
   - Sent via HTTP bridge to Grasshopper
   - Grasshopper receives and instantiates in Rhino

4. **Verify in Rhino**
   - Molds appear in Rhino viewport
   - Each mold is separate Brep object
   - Layer structure:
     - `Molds/Ceramic` - Inner cavity surfaces
     - `Molds/Plaster` - Outer mold shells
     - `Molds/Keys` - Registration features

<!-- Screenshot: Molds appearing in Rhino -->

**What Gets Transferred:**

- **NURBS Surfaces**: Exact Brep geometry
- **Metadata**: Region ID, parameters, validation status
- **Organization**: Proper layer structure
- **Registration Keys**: Positioned correctly

**Not Transferred:**
- Display meshes (only exact NURBS)
- Temporary visualization artifacts
- Analysis data (stays in desktop app)

### 7.4 Fabrication Workflow

**From Molds to Physical Object:**

After exporting to Rhino, follow this workflow for 3D printing and ceramic casting:

#### Phase 1: Rhino Preparation

1. **Verify Mold Geometry**
   - Check alignment between pieces
   - Verify registration keys
   - Measure wall thicknesses

2. **Add Pour Reservoir** (if needed)
   - Extend top opening
   - Add funnel geometry
   - Ensure sufficient capacity

3. **Add Drain Holes** (if needed)
   - For trapped volumes
   - Position at lowest points
   - Typical size: 3-5mm diameter

4. **Inspect Seams**
   - Zoom to seam locations
   - Check gap <1.27mm
   - Smooth transitions if needed

#### Phase 2: STL Export

**THIS IS THE SINGLE APPROXIMATION STEP** (maintaining "Lossless Until Fabrication"):

1. **Select Mold Breps**
   - Select all mold pieces
   - Keep organized by layer

2. **Export to STL**
   - Command: `Export` or `-Export`
   - File type: "STL Files (*.stl)"
   - Settings:
     - **File Type**: Binary (smaller file size)
     - **Tolerance**: 0.01mm (high quality)
     - **Angle Tolerance**: 15°
     - **Min Edge Length**: 0.1mm
     - **Max Edge Length**: 10mm

3. **Verify STL Quality**
   - Import back into Rhino
   - Check mesh density
   - Verify no holes or errors

<!-- Screenshot: STL export dialog -->

#### Phase 3: 3D Printing (Slicer)

1. **Import STL to Slicer** (Cura, PrusaSlicer, etc.)

2. **Orient for Printing**
   - Position for minimum supports
   - Consider registration key orientation

3. **Configure Print Settings**
   - **Material**: ABS or PLA (plaster will be poured onto this)
   - **Layer Height**: 0.2mm (good balance)
   - **Infill**: 20-30% (structural support for plaster)
   - **Walls**: 3-4 perimeters (plaster contact surface)
   - **Support**: Generate for overhangs

4. **Generate G-code and Print**

<!-- Screenshot: Slicer with mold oriented -->

#### Phase 4: Plaster Mold Creation

1. **Prepare 3D Printed Core**
   - Clean support material
   - Smooth surface if needed (light sanding)
   - Seal with spray sealer (optional)

2. **Build Cottle (Mold Box)**
   - Create dam around printed core
   - Leave 1.5-2 inch gap (plaster thickness)
   - Seal bottom with clay

3. **Mix Plaster**
   - Use No. 1 pottery plaster
   - Water:plaster ratio = 70:100 by weight
   - Mix thoroughly, remove air bubbles

4. **Pour Plaster**
   - Pour slowly to avoid air pockets
   - Fill to cover core completely
   - Vibrate to release bubbles

5. **Cure and Demolish**
   - Let set 30-45 minutes
   - Remove cottle
   - Extract 3D printed core
   - Dry plaster mold 5-7 days

#### Phase 5: Slip Casting

1. **Prepare Slip**
   - Translucent porcelain casting slip
   - Proper deflocculation
   - Sieve to remove lumps

2. **First Cast (Test)**
   - Pour slip into mold
   - Monitor wall build-up (check at 15 min)
   - Pour out excess when wall reaches 3-4mm
   - Let dry completely (24+ hours)

3. **Demold**
   - Gently separate mold pieces
   - Remove ceramic carefully
   - Let air dry further

4. **Finishing**
   - Clean seams with knife/sponge
   - Smooth surfaces
   - **The seams remain visible** - they're the mathematical truth inscribed in the form

5. **Fire**
   - Bisque fire: Cone 04 (1945°F / 1063°C)
   - Glaze if desired (transparent to maintain translucency)
   - Glaze fire: Cone 6-10 depending on clay body

<!-- Diagram: Complete fabrication workflow -->

**Resources:**

- **Detailed slip-casting reference**: See [SlipCasting_Ceramics_Technical_Reference.md](reference/SlipCasting_Ceramics_Technical_Reference.md)
- **Technical specifications**: See [technical_implementation_guide_v5.md](reference/technical_implementation_guide_v5.md)

---

## 8. Troubleshooting

### 8.1 Common Issues

#### Application Won't Launch

**Symptom**: `python3 launch.py` fails or shows import errors

**Possible Causes & Solutions:**

1. **PyQt6 Not Installed**
   ```
   Error: ModuleNotFoundError: No module named 'PyQt6'
   ```
   **Solution**:
   ```bash
   pip install PyQt6
   ```

2. **Qt Plugin Path Issues** (macOS)
   ```
   Error: Failed to load platform plugin "cocoa"
   ```
   **Solution**:
   Use `launch.py` instead of `main.py` directly (it auto-configures Qt plugins)

3. **Wrong Python Version**
   ```bash
   python3 --version  # Check version >= 3.11
   ```
   **Solution**: Install Python 3.11+ (see Installation section)

4. **Virtual Environment Not Activated**
   ```bash
   source venv/bin/activate
   ```

#### C++ Core Import Fails

**Symptom**: `import cpp_core` raises ImportError

**Possible Causes & Solutions:**

1. **C++ Module Not Built**
   ```
   Error: ModuleNotFoundError: No module named 'cpp_core'
   ```
   **Solution**:
   ```bash
   cd cpp_core/build
   cmake .. && make -j$(nproc)
   ```

2. **Build Path Not in sys.path**

   The application adds `cpp_core/build` to Python path automatically. If it fails:
   ```python
   import sys
   sys.path.insert(0, '/absolute/path/to/latent/cpp_core/build')
   import cpp_core
   ```

3. **OpenSubdiv Not Found**
   ```
   Error: dyld: Library not loaded: libosdCPU.3.dylib
   ```
   **Solution** (macOS):
   ```bash
   brew install opensubdiv
   ```
   **Solution** (Linux):
   ```bash
   sudo apt-get install libosd-dev
   ```

4. **ABI Mismatch** (pybind11 compiled with different Python)

   **Solution**: Rebuild with current Python interpreter:
   ```bash
   cd cpp_core/build
   rm -rf *
   cmake ..
   make -j$(nproc)
   ```

#### Rhino Connection Fails

**Symptom**: "Could not connect to Rhino HTTP server"

**Possible Causes & Solutions:**

1. **Grasshopper Server Not Running**

   **Check**: Look for "✅ Server running on http://localhost:8888" in Grasshopper Python component output

   **Solution**: Verify server script loaded and SubD connected to input

2. **Port Conflict**

   Another application using port 8888

   **Solution**: Check port availability:
   ```bash
   # macOS/Linux
   lsof -i :8888
   ```
   Kill conflicting process or change port in script

3. **Firewall Blocking**

   **Solution** (macOS):
   - System Preferences → Security & Privacy → Firewall
   - Allow Python to accept incoming connections

4. **Wrong Server Script Version**

   Using old `grasshopper_http_server.py` instead of `grasshopper_http_server_control_cage.py`

   **Solution**: Use the control cage version (exact transfer, not mesh)

5. **SubD Not Valid**

   **Check**: In Rhino, type `What` and click object - should say "subdivision surface"

   **Solution**: Run `SubDRepair` on geometry

#### Geometry Not Appearing

**Symptom**: Connection succeeds but no geometry in viewports

**Possible Causes & Solutions:**

1. **Empty SubD Sent**

   **Check**: Grasshopper output should show vertex count > 0

   **Solution**: Verify SubD connected to `subd` input parameter

2. **Camera Far from Geometry**

   **Solution**: Press **Space** to reset camera, or **View → Reset All Cameras**

3. **Geometry Outside Viewport Clip Planes**

   **Solution**: Check scale - geometry might be extremely small or large

4. **Display Mesh Not Generated**

   **Check**: Debug console for tessellation errors

   **Solution**: Verify SubD evaluator initialized correctly

#### Analysis Produces No Regions

**Symptom**: Click "Analyze" but no regions appear

**Possible Causes & Solutions:**

1. **No Geometry Loaded**

   **Check**: Is SubD displayed in viewport?

   **Solution**: Load from Rhino or use test geometry first

2. **All Faces Below Threshold**

   Analysis parameters too strict

   **Solution**: Adjust parameters in Analysis panel:
   - Lower curvature threshold
   - Reduce minimum region size
   - Increase coherence tolerance

3. **Analysis Engine Error**

   **Check**: Debug console for error messages

   **Solution**: Check traceback, may indicate C++ evaluation issue

4. **All Regions Pinned**

   Re-analysis only affects unpinned regions

   **Solution**: Unpin some regions or unpin all (**Edit → Unpin All Regions**)

### 8.2 Error Messages

#### "Failed to initialize SubD evaluator"

**Cause**: Invalid control cage data

**Solutions**:
- Check SubD topology is valid in Rhino (`SubDRepair`)
- Verify no naked edges or non-manifold vertices
- Try simpler geometry first (test cube/sphere)

#### "Undercut detected - cannot generate mold"

**Cause**: Physical constraint violation

**Solutions**:
- Adjust draft angle (increase to 3-5°)
- Change pull direction
- Split region at undercut boundary
- See [Section 6.6: Fixing Undercuts](#66-fixing-undercuts)

#### "Insufficient memory for eigenvalue computation"

**Cause**: Spectral analysis on very large mesh

**Solutions**:
- Reduce subdivision level (tessellate at lower density)
- Simplify geometry in Rhino before transfer
- Use differential lens instead (less memory intensive)
- Increase system RAM or use machine with more memory

#### "NURBS surface fitting failed"

**Cause**: Point cloud quality issues or complex geometry

**Solutions**:
- Increase sampling density (more points)
- Check for degenerate faces (zero-area faces)
- Simplify region (merge with neighbors, try different lens)
- Manually inspect limit surface evaluation

#### "Registration keys conflict"

**Cause**: Automatic key placement created overlaps

**Solutions**:
- Manually adjust key positions
- Reduce key size parameter
- Disable auto-placement and place manually

### 8.3 Performance Issues

#### Slow Analysis

**Symptom**: Analysis takes >30 seconds on medium geometry

**Optimization Strategies:**

1. **Use Test/Preview Mode**
   - Lower subdivision level for analysis
   - Increase for final generation only

2. **Reduce Sampling Density**
   - In Analysis Panel → Advanced:
   - Curvature samples per face: 9 (3×3) → 4 (2×2)
   - Trade-off: Faster but less accurate

3. **Pin Incrementally**
   - Pin good regions after each analysis
   - Re-analyze only unpinned areas (faster)

4. **Use Appropriate Lens**
   - Differential lens: Fast (seconds)
   - Spectral lens: Slower (tens of seconds, depends on mesh size)
   - Start with differential for quick exploration

5. **Simplify Geometry**
   - In Rhino, reduce SubD control vertex count if possible
   - Fewer faces = faster analysis

#### Slow Viewport Rendering

**Symptom**: Laggy camera movement, low frame rate

**Optimization Strategies:**

1. **Reduce Tessellation Quality**
   - In View → Display Settings:
   - Subdivision level: 3 → 2 (lower quality but faster)

2. **Hide Unnecessary Elements**
   - Hide constraint visualizations when not needed
   - Hide debug overlays
   - Hide unselected regions

3. **Use Single Viewport**
   - **Alt+1** for single viewport (4× faster than four viewports)

4. **Disable Shadows/Lighting Effects**
   - View → Display Mode → Flat Shading (fastest)

5. **Close Other Applications**
   - Free up GPU resources

#### Memory Issues

**Symptom**: Application crashes or system swap usage high

**Optimization Strategies:**

1. **Limit Geometry Complexity**
   - Keep control cage < 5000 faces for desktop analysis
   - Subdivide minimally (level 2-3, not 4-5)

2. **Close Unused Panels**
   - Hide Debug Console if not needed
   - Collapse dockable panels

3. **Clear History Periodically**
   - Undo history consumes memory
   - Edit → Clear History (loses undo capability)

4. **Restart Application**
   - Long sessions accumulate memory
   - Save session and restart periodically

### 8.4 Performance Tips

**Hardware Recommendations:**

| Task | Minimum | Recommended |
|------|---------|-------------|
| **General Use** | 4GB RAM, 2 cores | 8GB RAM, 4 cores |
| **Large Geometry (>2000 faces)** | 8GB RAM, 4 cores | 16GB RAM, 8 cores |
| **Spectral Analysis** | 8GB RAM | 16GB+ RAM |
| **Mold Generation** | 8GB RAM, 4 cores | 16GB RAM, 8 cores, SSD |

**Workflow Optimization:**

1. **Coarse → Fine Approach**
   - Start with low-res geometry for exploration
   - Refine regions with coarse mesh
   - Switch to high-res only for final generation

2. **Batch Processing**
   - Analyze multiple designs in parallel
   - Generate all molds at once (uses multicore efficiently)

3. **Use Test Geometry**
   - Test workflows on simple sphere/torus first
   - Validate settings before applying to complex forms

4. **Incremental Saves**
   - Save session frequently (File → Save Session)
   - Prevents loss of work if crash occurs

**Profiling Analysis Performance:**

For developers, enable profiling:
```python
# In Analysis Panel → Advanced → Enable Profiling
```

Outputs timing breakdown:
- Limit surface evaluation: X ms
- Curvature computation: Y ms
- Region growing: Z ms
- Total: T ms

Helps identify bottlenecks for specific geometry.

---

## Appendix A: Keyboard Shortcuts

**File Operations:**

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Connect to Rhino |
| Ctrl+R | Load from Rhino |
| Ctrl+L | Start Live Sync |
| F5 | Force Refresh |
| Ctrl+S | Save Session |
| Ctrl+Q | Quit |

**Edit Operations:**

| Shortcut | Action |
|----------|--------|
| Ctrl+Z | Undo |
| Ctrl+Shift+Z | Redo |
| Esc | Clear Selection |
| Ctrl+A | Select All |
| Ctrl+I | Invert Selection |
| Ctrl+> | Grow Selection |
| Ctrl+< | Shrink Selection |

**Edit Modes:**

| Shortcut | Mode |
|----------|------|
| S | Solid Mode |
| P | Panel Mode |
| E | Edge Mode |
| V | Vertex Mode |

**View Operations:**

| Shortcut | Action |
|----------|--------|
| Alt+1 | Single Viewport |
| Alt+2 | Two Horizontal Viewports |
| Alt+3 | Two Vertical Viewports |
| Alt+4 | Four Grid Viewports |
| Space | Reset Camera |

**Viewport Navigation:**

| Shortcut | Action |
|----------|--------|
| Left Click | Select |
| Right Drag | Rotate |
| Shift+Right Drag | Pan |
| Mouse Wheel | Zoom |
| Ctrl+Right Drag | Zoom |

---

## Appendix B: Technical Specifications

**Lossless Architecture:**

```
SubD Control Cage (Rhino)
  ↓ (exact transfer)
C++ OpenSubdiv Evaluator
  ↓ (Stam eigenanalysis)
Exact Limit Surface
  ↓ (parametric queries)
Analysis & Region Discovery
  ↓ (parametric regions)
NURBS Surface Generation (OpenCASCADE)
  ↓ (exact Brep operations)
Mold Solids
  ↓ (SINGLE APPROXIMATION)
STL/G-code Export
```

**Technology Stack:**

- **C++ Core**: OpenSubdiv 3.6.0, OpenCASCADE 7.x, pybind11 2.11.0
- **Python**: 3.11+, PyQt6 6.9.1, VTK 9.3.0, NumPy 2.0+
- **Rhino**: Rhino 8+, Grasshopper

**File Formats:**

- **Import**: SubD control cage (JSON via HTTP), .3dm (future)
- **Export**: NURBS Breps to Rhino, STL (final fabrication)

**Precision:**

- Control cage: Exact double-precision
- Limit surface: Exact evaluation via eigenanalysis
- NURBS fitting: <0.01mm deviation from limit surface
- STL export: Configurable tolerance (default 0.01mm)

---

## Appendix C: Additional Resources

**Documentation:**

- [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) - Detailed installation guide
- [API_REFERENCE.md](API_REFERENCE.md) - C++ and Python API documentation
- [RHINO_BRIDGE_SETUP.md](RHINO_BRIDGE_SETUP.md) - Rhino connection setup
- [DIFFERENTIAL_LENS.md](DIFFERENTIAL_LENS.md) - Differential lens details
- [SlipCasting_Ceramics_Technical_Reference.md](reference/SlipCasting_Ceramics_Technical_Reference.md) - Ceramic fabrication specs

**Technical Specifications:**

- [subdivision_surface_ceramic_mold_generation_v5.md](reference/subdivision_surface_ceramic_mold_generation_v5.md) - Complete v5.0 spec
- [technical_implementation_guide_v5.md](reference/technical_implementation_guide_v5.md) - Technical implementation guide

**Project Files:**

- [CLAUDE.md](../CLAUDE.md) - AI collaboration guidance and architectural principles
- [README.md](../README.md) - Project overview and quick start

**Community:**

- GitHub Issues: Bug reports and feature requests
- Discussions: Questions and sharing results

---

## Appendix D: Glossary

**Control Cage**: The coarse polygon mesh defining a SubD surface. Vertices and faces of the cage, not the smooth limit surface.

**Differential Geometry**: Mathematical study of curves and surfaces using calculus. Used for curvature analysis.

**Draft Angle**: Taper applied to vertical surfaces to allow mold removal. Measured in degrees from vertical.

**Eigenfunction**: Solution to Laplace-Beltrami eigenvalue problem. Vibration modes of the surface.

**Gaussian Curvature (K)**: Intrinsic curvature = κ₁ × κ₂. Positive = bowl, negative = saddle, zero = flat or cylindrical.

**Laplace-Beltrami Operator**: Generalization of Laplacian to surfaces. Used in spectral analysis.

**Limit Surface**: The smooth, infinitely-refined surface that a SubD converges to. What you see, not the control cage.

**Lossless**: Exact mathematical representation with no approximation or discretization.

**Mean Curvature (H)**: Extrinsic curvature = (κ₁ + κ₂) / 2. Sign indicates convex/concave.

**NURBS**: Non-Uniform Rational B-Splines. Exact mathematical surface representation used in CAD.

**Parametric Region**: Region defined in (face_id, u, v) parameter space on SubD, not as discrete triangles.

**Principal Curvatures (κ₁, κ₂)**: Maximum and minimum normal curvatures at a point.

**Resonance Score**: 0.0-1.0 measure of mathematical coherence. High = form "wants" this decomposition.

**Slip Casting**: Ceramic forming technique using liquid clay (slip) poured into plaster molds.

**SubD (Subdivision Surface)**: Smooth surface defined by repeatedly subdividing a control cage using Catmull-Clark rules.

**Unity Principle**: Description of mathematical coherence holding a region together (e.g., "uniform Gaussian curvature").

**Undercut**: Surface area preventing mold removal. Normal vector points away from pull direction.

---

**End of User Guide**

*Latent: revealing mathematical truths in ceramic forms*

For questions or support, see GitHub Issues or contact the development team.
