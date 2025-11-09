# UX/UI Design Specification
## Ceramic Mold Analyzer Desktop Application
### Version 1.0 - January 2025

---

## 1. PROJECT OVERVIEW

### 1.1 Product Vision
A desktop application that discovers natural mathematical decompositions of 3D forms for ceramic slip-casting molds. The software reveals inherent mathematical structures within forms through various analytical "lenses," treating the resulting seam lines not as manufacturing necessities to hide, but as intentional aesthetic features that celebrate the dialogue between mathematics and material.

### 1.2 Target Users

**Primary User: Artist-Technologist**
- Ceramic artists with digital fabrication experience
- Comfortable with 3D modeling (Rhino) and computational design
- Values both mathematical elegance and craft tradition
- Seeks to push boundaries of slip-casting techniques
- Age: 25-55, Design/Art education background

**Secondary Users:**
- Industrial designers exploring ceramic production
- Architecture students working with ceramic components
- Research institutions investigating computational fabrication

### 1.3 Core Values
- **Mathematical Truth**: Reveal, don't impose, the form's inherent structure
- **Craft Respect**: Honor traditional ceramic knowledge while embracing computation
- **Transparent Process**: Make the mathematical analysis understandable and adjustable
- **Aesthetic Intent**: Seams are features, not flaws

---

## 2. USER EXPERIENCE GOALS

### 2.1 Primary Experience Objectives

1. **Immediate Understanding**: Users should grasp what mathematical decomposition means within 30 seconds of seeing the interface
2. **Progressive Disclosure**: Complex features reveal themselves as users gain expertise
3. **Direct Manipulation**: All adjustments should provide immediate visual feedback
4. **Confidence Building**: Clear validation helps users trust the system's recommendations
5. **Creative Control**: Mathematical analysis serves the artist, not vice versa

### 2.2 Emotional Journey

**Discovery Phase** → Curiosity and wonder at seeing mathematical structures
**Exploration Phase** → Confidence through experimentation and comparison
**Refinement Phase** → Satisfaction from precise control and adjustment
**Production Phase** → Trust in the system's technical validation

### 2.3 Key Differentiators
- Unlike CAD: Focus on discovering natural boundaries, not drawing them
- Unlike simulation: Real-time interaction, not batch processing
- Unlike generative design: Artist retains full control over aesthetic decisions

---

## 3. FUNCTIONAL REQUIREMENTS

### 3.1 Core Workflow

```
Connect to 3D Model → Select Analysis Method → Discover Regions → 
Refine Boundaries → Validate Constraints → Generate Molds → Export
```

### 3.2 Essential Features

**3D Visualization**
- Display SubD surface from Rhino
- Show discovered regions with distinct visualization
- Highlight seam lines as primary features
- Interactive camera control (orbit, pan, zoom)
- Multiple viewport modes (solid, wireframe, x-ray)

**Mathematical Analysis**
- Multiple "lenses" for analysis (minimum 4 types)
- Resonance scoring (how well the method fits the form)
- Comparative analysis (see multiple decompositions)
- Analysis parameters adjustment

**Region Management**
- List all discovered regions
- Pin regions to lock from reanalysis
- Edit boundaries manually
- Merge multiple regions
- Split single regions
- Track modification history

**Constraint Validation**
- Three-tier system (Physical/Manufacturing/Mathematical)
- Real-time feedback during editing
- Clear visual indication of issues
- Contextual suggestions for fixes

**Mold Generation**
- Apply draft angles
- Set wall thickness
- Add registration features
- Preview final mold pieces

### 3.3 Connection & Communication
- Live link with Rhino/Grasshopper
- Automatic geometry updates
- Bidirectional data flow
- Clear connection status

---

## 4. INFORMATION ARCHITECTURE

### 4.1 Primary Interface Zones

**Zone A: 3D Viewport (Primary Focus)**
- Largest area (60-70% of interface)
- Central position
- Minimal UI overlay
- Context-sensitive tools

**Zone B: Analysis Control (Secondary)**
- Mathematical lens selection
- Analysis parameters
- Comparison tools

**Zone C: Region Management (Secondary)**
- Region list/tree
- Properties panel
- Action buttons

**Zone D: Validation Feedback (Tertiary)**
- Constraint status
- Warnings and errors
- Suggestions

**Zone E: Global Controls (Persistent)**
- File operations
- View controls
- Settings access
- Help/documentation

### 4.2 Information Hierarchy

1. **Level 1 (Always Visible)**: Current form, discovered regions, active lens
2. **Level 2 (One Click)**: Region properties, basic constraints, view options
3. **Level 3 (On Demand)**: Advanced settings, detailed analysis, history

### 4.3 Navigation Patterns
- **Direct manipulation** in viewport (primary)
- **List selection** for regions (secondary)
- **Modal dialogs** for complex operations (sparingly)
- **Contextual menus** for quick actions

---

## 5. INTERACTION DESIGN PRINCIPLES

### 5.1 Direct Manipulation
- Click regions in 3D to select
- Drag boundary points to adjust
- Hover for information reveal
- Right-click for context menus

### 5.2 Immediate Feedback
- <100ms response for selection
- <500ms for analysis preview
- Progress indication for >1 second operations
- Intermediate results during long processes

### 5.3 Reversibility
- Comprehensive undo/redo
- Non-destructive editing
- Version comparison
- "Reset to discovered" option

### 5.4 State Clarity
- Clear indication of:
  - What's selected
  - What's being edited
  - What's locked/pinned
  - What's valid/invalid
  - Connection status

---

## 6. VISUAL DESIGN DIRECTION

### 6.1 Design Philosophy
The interface should reflect the dialogue between mathematical precision and ceramic craft. Clean, modern aesthetics that don't overshadow the 3D content, with subtle references to both computational design and traditional pottery.

### 6.2 Visual Metaphors to Explore
- **Seams as Signatures**: Celebrate rather than hide boundaries
- **Lenses as Perspectives**: Different ways of seeing the same form
- **Pinning as Commitment**: Locked decisions in the creative process
- **Resonance as Harmony**: Natural fit between form and decomposition

### 6.3 Key Visual Decisions Needed

**Color Strategy**
- How to differentiate regions clearly without overwhelming
- Indicating state (selected, pinned, invalid) through color
- Balancing visibility against 3D model
- Accessibility considerations

**Typography**
- Technical precision vs. approachability
- Hierarchy for complex information
- Legibility at various sizes

**Iconography**
- Mathematical concepts made visual
- Ceramic process references
- Action clarity

**Depth & Dimensionality**
- Relationship between 2D UI and 3D viewport
- Shadow and elevation usage
- Panel overlays vs. embedded UI

### 6.4 Mood & Tone
- **Professional** but not intimidating
- **Precise** but not rigid
- **Innovative** but respectful of tradition
- **Calm** workspace for concentration

---

## 7. RESPONSIVE BEHAVIOR

### 7.1 Window Scaling
- Minimum window size: 1280x720
- Optimal size: 1920x1080 or larger
- Panels should reflow intelligently
- Maintain viewport aspect ratio

### 7.2 Panel Management
- Collapsible panels for maximum viewport
- Dockable/floating panel options
- Saved layout presets
- Quick maximize viewport mode

### 7.3 Display Scenarios
- Single monitor setup (most common)
- Dual monitor (viewport on one, controls on other)
- High DPI/Retina displays
- Different aspect ratios

---

## 8. SPECIFIC UI COMPONENTS

### 8.1 Region List Item
**Requirements:**
- Show region identifier
- Indicate unity strength (mathematical coherence)
- Show pinned/unlocked state
- Indicate if constraints are violated
- Enable selection
- Provide quick actions (pin, edit, delete)

**Design Considerations:**
- How to show mathematical "confidence" visually?
- Compact vs. detailed view modes?
- Grouping or hierarchy?

### 8.2 Mathematical Lens Selector
**Requirements:**
- Present 4+ analysis methods
- Show current selection clearly
- Indicate "resonance" with current form
- Allow parameter adjustment
- Enable comparison mode

**Design Considerations:**
- Radio buttons, dropdown, or visual selector?
- How to explain what each lens does?
- Preview of what each would generate?

### 8.3 Constraint Status Panel
**Requirements:**
- Three-tier hierarchy (Physical/Manufacturing/Mathematical)
- Traffic light metaphor (Pass/Warning/Fail)
- Detailed information on demand
- Actionable suggestions

**Design Considerations:**
- Persistent visibility vs. on-demand?
- How much detail to show by default?
- Visual weight relative to importance?

### 8.4 3D Viewport Controls

**Navigation Controls (Rhino 8 Standard):**

The application uses Rhino 8-compatible viewport navigation for immediate familiarity:

**Mouse Controls:**
- **Right-drag**: Rotate/orbit view around model
- **Shift + Right-drag**: Pan view (slide camera)
- **Ctrl + Right-drag** or **Mouse wheel**: Zoom in/out
- **Left-click**: Select object (no camera movement)

**Keyboard Shortcuts:**
- **Space**: Reset camera to default view
- **Home**: Undo view change
- **End**: Redo view change

**Implementation Note:**
Viewport navigation is implemented directly in `app/ui/viewport_3d.py` using the `RhinoInteractorStyle` class, which extends VTK's `vtkInteractorStyleTrackballCamera` to match Rhino's behavior exactly.

**Display Mode Features:**
- Region visibility toggles
- Seam line emphasis control
- View presets (top, front, right, perspective, isometric)
- Measurement tools (future enhancement)

**Design Principles:**
- Direct manipulation: No mode switching required for navigation
- Muscle memory: Users familiar with Rhino can work immediately
- No gesture conflicts: Left-click reserved exclusively for selection
- Momentum-free: Direct 1:1 control without inertia/spin effects

---

## 9. STATES & FEEDBACK

### 9.1 Application States
1. **Disconnected**: No Rhino connection
2. **Connected**: Awaiting geometry
3. **Loaded**: Geometry present, no analysis
4. **Analyzed**: Regions discovered
5. **Editing**: Boundary adjustment mode
6. **Generating**: Creating mold geometry
7. **Error**: Various error states

### 9.2 Loading & Progress
- Skeleton screens for initial load
- Determinate progress bars when possible
- Indeterminate with meaningful messages
- Ability to cancel long operations

### 9.3 Error Handling
- Inline validation for parameters
- Non-blocking warnings
- Clear error messages with solutions
- Recovery options

### 9.4 Empty States
- Helpful guidance when no geometry
- Sample/demo option
- Clear next actions

---

## 10. ACCESSIBILITY & USABILITY

### 10.1 Accessibility Requirements
- Keyboard navigation throughout
- Screen reader compatibility for critical functions
- Color-blind safe palettes
- Adjustable text size
- High contrast mode option

### 10.2 Tooltips & Help
- Progressive tooltip detail (brief → detailed)
- Contextual help panels
- Video tutorials accessible in-app
- Glossary for mathematical terms

### 10.3 Keyboard Shortcuts
- Industry-standard where applicable
- Customizable for power users
- Visual cheat sheet available
- Consistent with Rhino where logical

---

## 11. TECHNICAL CONSTRAINTS

### 11.1 Platform
- macOS 12+ (primary)
- Windows 11 (future)
- Native desktop application
- PyQt6 framework

### 11.2 Performance Targets
- 60 FPS viewport interaction
- <2 second analysis for typical form
- <100ms UI response
- Smooth with 10,000 polygon models

### 11.3 Integration Requirements
- Must communicate with Rhino 8+
- Support SubD and NURBS geometry
- Export standard CAD formats

---

## 12. DESIGN DELIVERABLES NEEDED

### 12.1 Discovery Phase
1. **Mood boards** exploring visual direction
2. **Conceptual sketches** of key interactions
3. **User journey maps** for primary workflows
4. **Competitive analysis** of similar tools

### 12.2 Design Phase
1. **Wireframes** for all major screens
2. **Interactive prototype** of core workflow
3. **Visual design system**:
   - Color palette
   - Typography scale
   - Icon set
   - Component library
4. **High-fidelity mockups** of key states

### 12.3 Specification Phase
1. **Component specifications** with all states
2. **Animation and transition specs**
3. **Responsive behavior documentation**
4. **Design-to-development handoff files**

### 12.4 Optional Explorations
1. **Alternative layout concepts**
2. **Dark mode variation**
3. **Compact/expanded view modes**
4. **Touch/tablet interface (future)**

---

## 13. SUCCESS METRICS

### 13.1 Usability Goals
- New user can discover regions within 5 minutes
- Complete mold generation in under 10 minutes
- Zero critical errors in typical session
- 80% of features discoverable without documentation

### 13.2 Experience Goals
- Users describe interface as "intuitive"
- Mathematical concepts become understandable
- Seam placement feels intentional, not arbitrary
- Confidence in generated molds

---

## 14. INSPIRATION & REFERENCES

### 14.1 Visual Inspiration
- **Computational Design Tools**: Grasshopper, Houdini
- **3D Software**: Fusion 360, Blender (geometry nodes)
- **Scientific Visualization**: ParaView, VMD
- **Craft/Making**: Ceramics glazing charts, kiln controllers

### 14.2 Interaction Patterns
- **Direct manipulation**: Origami Simulator
- **Progressive disclosure**: Figma's property panels
- **Constraint feedback**: Fusion 360's sketch constraints
- **Mathematical visualization**: 3Blue1Brown's Manim

### 14.3 Avoid
- Overwhelming "cockpit" interfaces
- Over-skeuomorphic ceramic references
- Purely technical/engineering aesthetic
- Hidden critical functions

---

## 15. OPEN QUESTIONS FOR DESIGNER

### 15.1 Conceptual Questions
1. How might we visualize "mathematical resonance" in an intuitive way?
2. Should seam lines be celebrated through explicit visualization or subtle emphasis?
3. How can the interface reflect both computational precision and craft sensibility?
4. What visual metaphors best explain different mathematical lenses?

### 15.2 Practical Questions
1. Fixed panels vs. floating windows vs. docked but adjustable?
2. How much mathematical detail should be visible by default?
3. Should region colors be semantic (meaningful) or just distinctive?
4. Dark interface with bright 3D or light interface with contrast control?

### 15.3 Future Considerations
1. How should the design scale for 20+ region pieces (Peter Pincus level)?
2. Multi-monitor setup as primary or secondary use case?
3. Should we plan for collaborative features (shared sessions)?
4. How to handle library/preset systems in the future?

---

## 16. DESIGN PHILOSOPHY SUMMARY

This tool sits at the intersection of:
- **Mathematics** (truth, precision, logic)
- **Ceramics** (tradition, material, craft)
- **Computation** (possibility, automation, analysis)
- **Art** (expression, intention, beauty)

The interface should honor all four domains while making the complex feel approachable. Every design decision should ask: "Does this help the artist understand and control the mathematical decomposition of their form?"

Remember: **The seams are not flaws to hide but truths to celebrate.**

---

## APPENDIX A: CURRENT IMPLEMENTATION

The existing PyQt6 application provides a functional foundation with:
- Main window with menu system
- 3D viewport placeholder (70% of window)
- Control panel (30% of window)
- Region list with pin/edit controls
- Constraint status panel
- Mathematical lens selector

This can serve as a wireframe for design exploration, but should not constrain creative solutions.

---

## APPENDIX B: GLOSSARY

**SubD**: Subdivision surface - smooth 3D form defined by a coarse control mesh
**Region**: A continuous area of the surface that will become one mold piece
**Mathematical Lens**: An analytical method for discovering natural boundaries
**Unity Strength**: Measure of how coherently a region belongs together
**Pinning**: Locking a region to prevent reanalysis
**Resonance**: How well a mathematical method "fits" a particular form
**Draft Angle**: Taper required for removing cast piece from mold
**Registration Keys**: Alignment features ensuring mold pieces fit together
**Slip-casting**: Ceramic forming technique using liquid clay in plaster molds

---

## APPENDIX C: CONTACT & COLLABORATION

**Design Process:**
- Initial concepts can be rough/exploratory
- Prefer iterative refinement over perfect first attempt
- Questions and clarifications welcome throughout
- Design critique sessions encouraged

**Deliverable Formats:**
- Figma preferred for collaborative editing
- Sketch, XD, or other tools acceptable
- Export specifications as needed for development

---

*This specification is a living document. The designer is encouraged to challenge assumptions, propose alternatives, and help evolve the vision.*
