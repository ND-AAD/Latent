# Latent Interface Wireframes v2.0

## Screen Resolution: 1920×1080 (Full HD)
## Window Size: 1536×864 (80% of screen)

---

## Base Layout Structure

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ≡ Ceramic Mold Analyzer                                                    Min ▭ Max ✕  │ 30px
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [FILE] [ANALYZE] [EDIT] [VALIDATE] [FABRICATE] [VIEW]                     Help | About  │ 40px (Tab bar)
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────┐                       │ 40px
│ │ [Primary Tool 1] [Primary Tool 2] [Primary Tool 3] [Primary Tool 4]  │ (Top toolbar)        │
│ └─────────────────────────────────────────────────────────────────────────────────────────┘   │
├──┬──────────────────────────────────────────────────────────────────────────────────────┬──────┤
│  │                                                                                      │      │
│L │                                                                                      │   R  │
│E │                                                                                      │   I  │
│F │                           VIEWPORT AREA                                             │   G  │
│T │                                                                                      │   H  │
│  │                         (1036×584 pixels)                                           │   T  │
│B │                           67.4% of window                                           │      │
│A │                                                                                      │   P  │
│R │                                                                                      │   A  │
│  │                                                                                      │   N  │
│  │                                                                                      │   E  │
│  │                                                                                      │   L  │
│  │                                                                                      │      │
├──┴──────────────────────────────────────────────────────────────────────────────────────┴──────┤
│ > analyze curvature                                    │ Analysis complete: 6 regions │ ● Rhino│ 120px
│ [Command Input                    ] [History         ] │ [Progress Bar         ] Cancel│Status │ (Bottom)
└────────────────────────────────────────────────────────────────────────────────────────────────┘

Left Bar: 200px (13%) when visible | Right Panel: 300px (19.5%) | Bottom: 120px (13.9%)
```

---

## TAB 1: FILE (Session Management)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ≡ Ceramic Mold Analyzer - untitled.latent *                               Min ▭ Max ✕  │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [FILE] [ANALYZE] [EDIT] [VALIDATE] [FABRICATE] [VIEW]                     Help | About  │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [📄 New] [📁 Open] [💾 Save] [💾 Save As] [⬇ Import] [⬆ Export]                               │
├──┬──────────────────────────────────────────────────────────────────────────────────────┬──────┤
│  │                                                                                      │ TABS │
│S │                                                                                      │ ┌──┐ │
│E │                                                                                      │ │VP│ │
│C │                          VIEWPORT                                                   │ ├──┤ │
│O │                                                                                      │ │RG│ │
│N │                     Shows current model                                             │ ├──┤ │
│D │                      or empty if no file                                            │ │CN│ │
│A │                                                                                      │ ├──┤ │
│R │                                                                                      │ │SL│ │
│Y │                                                                                      │ ├──┤ │
│  │                                                                                      │ │PR│ │
│  │ Recent Files:                                                                       │ └──┘ │
│  │ ├─ project_01.latent                                                                │      │
│  │ ├─ test_mold.latent                                                                 │ VP:  │
│  │ └─ demo.latent                                                                      │View  │
│  │                                                                                      │      │
│  │ Templates:                                                                          │ RG:  │
│  │ ├─ Basic Setup                                                                      │Regio │
│  │ ├─ Complex Form                                                                     │      │
│  │ └─ Production Ready                                                                 │ CN:  │
│  │                                                                                      │Const │
│  │ [Export Report...]                                                                  │      │
│  │ [Batch Export...]                                                                   │ SL:  │
│  │                                                                                      │Selec │
│  │                                                                                      │      │
│  │                                                                                      │ PR:  │
│  │                                                                                      │Param │
├──┴──────────────────────────────────────────────────────────────────────────────────────┴──────┤
│ > _                                                     │ Ready                        │ ● Rhino│
│ [Command: Type to search commands...                 ] │ [Session: untitled.latent  ] │ Connected│
└────────────────────────────────────────────────────────────────────────────────────────────────┘

LEFT: File operations & templates | RIGHT: Properties & current file info
```

---

## TAB 2: ANALYZE (Mathematical Analysis)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ≡ Ceramic Mold Analyzer - project.latent                                   Min ▭ Max ✕  │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [FILE] [ANALYZE] [EDIT] [VALIDATE] [FABRICATE] [VIEW]                     Help | About  │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [📐 Curvature] [〰️ Spectral] [🌊 Flow] [🔷 Topological] │ [▶ ANALYZE] [⏹ Stop]              │
├──┬──────────────────────────────────────────────────────────────────────────────────────┬──────┤
│  │                                                                                      │ ▼VP  │
│C │                                                                                      │┌────┐│
│O │                                                                                      ││4-G ││
│M │                                                                                      │├────┤│
│P │                    3D VIEWPORT                                                      ││Sha ││
│A │                                                                                      ││ded ││
│R │              Shows model with analysis                                              │├────┤│
│E │                  overlay (colormap)                                                 ││Edg ││
│  │                                                                                      ││On  ││
│⎯ │                                                                                      │├────┤│
│D │                  Green = High resonance                                             ││BG: ││
│I │                  Yellow = Medium                                                    ││Gray││
│F │                  Red = Low resonance                                                │└────┘│
│F │                                                                                      │      │
│⎯ │                                                                                      │ ▶RG  │
│B │                                                                                      │ 12   │
│A │                                                                                      │region│
│T │                                                                                      │      │
│C │                                                                                      │ ▶CN  │
│H │                                                                                      │ Not  │
│  │                                                                                      │ run  │
│⎯ │                                                                                      │      │
│H │                                                                                      │ ▶SL  │
│I │                                                                                      │ None │
│S │                                                                                      │      │
│T │                                                                                      │ ▼PR  │
│O │                                                                                      │┌────┐│
│R │                                                                                      ││Res:││
│Y │                                                                                      ││Med ││
│  │                                                                                      │├────┤│
│⎯ │                                                                                      ││Map:││
│P │                                                                                      ││Cool││
│R │                                                                                      │├────┤│
│E │                                                                                      ││Auto││
│S │                                                                                      ││☑   ││
│E │                                                                                      │├────┤│
│T │                                                                                      ││Min:││
│S │                                                                                      ││0.0 ││
│  │                                                                                      │├────┤│
│  │                                                                                      ││Max:││
│  │                                                                                      ││1.0 ││
│  │                                                                                      │└────┘│
├──┴──────────────────────────────────────────────────────────────────────────────────────┴──────┤
│ > analyze curvature                                    │ Analyzing... 45%              │ ● Rhino│
│ [Command                                            ]  │ [██████████░░░░░░░░        ] │Connected│
└────────────────────────────────────────────────────────────────────────────────────────────────┘

LEFT: Advanced analysis tools | RIGHT: Parameters and results
```

---

## TAB 3: EDIT (Region Manipulation)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ≡ Ceramic Mold Analyzer - project.latent                                   Min ▭ Max ✕  │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [FILE] [ANALYZE] [EDIT] [VALIDATE] [FABRICATE] [VIEW]                     Help | About  │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [S|P|E|V] [Select All] [Clear] [Invert] [📌 Pin] [🗑️ Delete]                                 │
├──┬──────────────────────────────────────────────────────────────────────────────────────┬──────┤
│  │                                                                                      │ ▶VP  │
│G │                                                                                      │      │
│R │                                                                                      │ ▼RG  │
│O │                                                                                      │ 12(3)│
│W │                     3D VIEWPORT                                                     │┌────┐│
│  │                                                                                      ││🔍  ││
│S │                 Shows model with selected                                           │├────┤│
│H │                    regions highlighted                                              ││Sort││
│R │                      in yellow                                                      ││Name││
│I │                                                                                      │├────┤│
│N │                                                                                      ││📌R1││
│K │                  Panel mode active                                                  ││ 0.9││
│  │                   Click to select                                                   │├────┤│
│⎯ │                                                                                      ││📌R2││
│  │                                                                                      ││ 0.8││
│E │                                                                                      │├────┤│
│D │                                                                                      ││ R3 ││
│I │                                                                                      ││ 0.7││
│T │                                                                                      │├────┤│
│  │                                                                                      ││ R4 ││
│B │                                                                                      ││ 0.6││
│O │                                                                                      │├────┤│
│U │                                                                                      ││ R5 ││
│N │                                                                                      ││ 0.5││
│D │                                                                                      │└────┘│
│A │                                                                                      │[Pin ]│
│R │                                                                                      │[All ]│
│Y │                                                                                      │      │
│  │                                                                                      │ ▶CN  │
│⎯ │                                                                                      │      │
│  │                                                                                      │ ▼SL  │
│M │                                                                                      │Panel │
│E │                                                                                      │F: 42 │
│R │                                                                                      │E: 0  │
│G │                                                                                      │V: 0  │
│E │                                                                                      │┌────┐│
│  │                                                                                      ││42, ││
│S │                                                                                      ││43, ││
│P │                                                                                      ││44, ││
│L │                                                                                      ││... ││
│I │                                                                                      │└────┘│
│T │                                                                                      │[Copy]│
│  │                                                                                      │      │
│⎯ │                                                                                      │ ▶PR  │
│  │                                                                                      │      │
│B │                                                                                      │      │
│A │                                                                                      │      │
│T │                                                                                      │      │
│C │                                                                                      │      │
│H │                                                                                      │      │
├──┴──────────────────────────────────────────────────────────────────────────────────────┴──────┤
│ > select panel 42                                      │ 42 faces selected            │ ● Rhino│
│ [Command                                            ]  │ Panel mode - 3 regions pinned│Connected│
└────────────────────────────────────────────────────────────────────────────────────────────────┘

LEFT: Selection tools | RIGHT: Region list and selection info
```

---

## TAB 4: VALIDATE (Constraint Checking)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ≡ Ceramic Mold Analyzer - project.latent                                   Min ▭ Max ✕  │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [FILE] [ANALYZE] [EDIT] [VALIDATE] [FABRICATE] [VIEW]                     Help | About  │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [✓ Check All] [❌ Errors] [⚠️ Warnings] [ℹ️ Info] [Clear] [Re-validate]                      │
├──┬──────────────────────────────────────────────────────────────────────────────────────┬──────┤
│  │                                                                                      │ ▶VP  │
│F │                                                                                      │      │
│I │                                                                                      │ ▶RG  │
│X │                                                                                      │      │
│  │                     3D VIEWPORT                                                     │ ▼CN  │
│U │                                                                                      │3E 2W │
│N │                Shows model with constraint                                          │┌────┐│
│D │                  violations highlighted                                             ││▼ E ││
│E │                                                                                      ││────││
│R │                   Red = Errors                                                      ││UC1 ││
│C │                   Yellow = Warnings                                                 ││ F42││
│U │                   Green = Passed                                                    ││0.8 ││
│T │                                                                                      │├────┤│
│S │                                                                                      ││UC2 ││
│  │                                                                                      ││ F51││
│⎯ │                                                                                      ││0.6 ││
│  │                                                                                      │├────┤│
│A │                                                                                      ││TV1 ││
│D │                                                                                      ││ F12││
│J │                                                                                      ││0.9 ││
│U │                                                                                      │├────┤│
│S │                                                                                      ││▼ W ││
│T │                                                                                      ││────││
│  │                                                                                      ││DR1 ││
│P │                                                                                      ││ F8 ││
│U │                                                                                      ││0.3°││
│L │                                                                                      │├────┤│
│L │                                                                                      ││WT1 ││
│  │                                                                                      ││ F15││
│⎯ │                                                                                      ││2.5 ││
│  │                                                                                      │└────┘│
│A │                                                                                      │[Fix ]│
│U │                                                                                      │[All ]│
│T │                                                                                      │      │
│O │                                                                                      │ ▶SL  │
│  │                                                                                      │      │
│F │                                                                                      │ ▼PR  │
│I │                                                                                      │┌────┐│
│X │                                                                                      ││Drft││
│  │                                                                                      ││3.0°││
│⎯ │                                                                                      │├────┤│
│  │                                                                                      ││Wall││
│T │                                                                                      ││3-6 ││
│O │                                                                                      │├────┤│
│L │                                                                                      ││Seam││
│E │                                                                                      ││1.5 ││
│R │                                                                                      │└────┘│
│A │                                                                                      │      │
│N │                                                                                      │      │
│C │                                                                                      │      │
│E │                                                                                      │      │
├──┴──────────────────────────────────────────────────────────────────────────────────────┴──────┤
│ > fix undercut F42                                     │ 3 errors, 2 warnings         │ ● Rhino│
│ [Command                                            ]  │ Adjusting pull direction...  │Connected│
└────────────────────────────────────────────────────────────────────────────────────────────────┘

LEFT: Fixing tools | RIGHT: Constraint list and tolerances
```

---

## TAB 5: FABRICATE (Mold Generation)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ≡ Ceramic Mold Analyzer - project.latent                                   Min ▭ Max ✕  │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [FILE] [ANALYZE] [EDIT] [VALIDATE] [FABRICATE] [VIEW]                     Help | About  │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [🔨 Generate] [🔑 Keys] [💍 Bands] [🚰 Spouts] [📊 Volume] [📤 Export]                       │
├──┬──────────────────────────────────────────────────────────────────────────────────────┬──────┤
│  │                                                                                      │ ▶VP  │
│K │                                                                                      │      │
│E │                                                                                      │ ▶RG  │
│Y │                                                                                      │      │
│  │                     3D VIEWPORT                                                     │ ▶CN  │
│P │                                                                                      │      │
│R │                 Shows generated molds with                                          │ ▶SL  │
│O │                   registration features                                             │      │
│F │                                                                                      │ ▼PR  │
│I │                                                                                      │┌────┐│
│L │                  Keys shown in blue                                                 ││Wall││
│E │                  Bands shown in green                                               ││4mm ││
│S │                  Spouts shown in cyan                                               │├────┤│
│  │                                                                                      ││Key ││
│⎯ │                                                                                      ││Ball││
│  │                                                                                      │├────┤│
│S │                                                                                      ││Size││
│E │                                                                                      ││10mm││
│A │                                                                                      │├────┤│
│M │                                                                                      ││Band││
│  │                                                                                      ││6mm ││
│O │                                                                                      │├────┤│
│P │                                                                                      ││Gap ││
│T │                                                                                      ││1mm ││
│I │                                                                                      │├────┤│
│M │                                                                                      ││Pour││
│I │                                                                                      ││15mm││
│Z │                                                                                      │├────┤│
│E │                                                                                      ││Vent││
│  │                                                                                      ││3mm ││
│⎯ │                                                                                      │├────┤│
│  │                                                                                      ││────││
│A │                                                                                      ││Vol:││
│S │                                                                                      ││450 ││
│S │                                                                                      ││ml  ││
│E │                                                                                      │├────┤│
│M │                                                                                      ││Time││
│B │                                                                                      ││12m ││
│L │                                                                                      │├────┤│
│Y │                                                                                      ││Cast││
│  │                                                                                      ││2x  ││
│⎯ │                                                                                      │└────┘│
│  │                                                                                      │      │
│D │                                                                                      │[Gen ]│
│R │                                                                                      │[QC  ]│
│Y │                                                                                      │      │
│I │                                                                                      │      │
│N │                                                                                      │      │
│G │                                                                                      │      │
├──┴──────────────────────────────────────────────────────────────────────────────────────┴──────┤
│ > generate molds                                       │ 6 mold pieces generated      │ ● Rhino│
│ [Command                                            ]  │ Ready for export             │Connected│
└────────────────────────────────────────────────────────────────────────────────────────────────┘

LEFT: Advanced mold tools | RIGHT: Mold parameters
```

---

## TAB 6: VIEW (Display Control)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ≡ Ceramic Mold Analyzer - project.latent                                   Min ▭ Max ✕  │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [FILE] [ANALYZE] [EDIT] [VALIDATE] [FABRICATE] [VIEW]                     Help | About  │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [🏠 Reset All] [🎯 Frame All] [📷 Frame Sel] [⊞ Grid] [→| Axes] [🎨 Style]                  │
├──┬──────────────────────────────────────────────────────────────────────────────────────┬──────┤
│  │                                                                                      │ ▼VP  │
│S │                                                                                      │┌────┐│
│A │                                                                                      ││Lyt:││
│V │                                                                                      ││4-G ││
│E │                     VIEWPORT(S)                                                    │├────┤│
│  │                                                                                      ││Mode││
│V │                   Can show 1, 2H, 2V,                                              ││Shad││
│I │                    or 4-grid layout                                                │├────┤│
│E │                                                                                      ││Edge││
│W │                                                                                      ││ On ││
│  │              ┌──────────┬──────────┐                                              │├────┤│
│⎯ │              │   Top    │  Persp   │                                              ││BG: ││
│  │              │          │          │                                              ││Gray││
│R │              │          │          │                                              │├────┤│
│E │              ├──────────┼──────────┤                                              ││Grid││
│S │              │  Front   │  Right   │                                              ││10mm││
│T │              │          │          │                                              │├────┤│
│O │              │          │          │                                              ││Snap││
│R │              └──────────┴──────────┘                                              ││ Off││
│E │                                                                                      │├────┤│
│  │                                                                                      ││Sync││
│⎯ │                                                                                      ││Cam ││
│  │                                                                                      ││ On ││
│L │                                                                                      │├────┤│
│O │                                                                                      ││Mat:││
│C │                                                                                      ││Prev││
│K │                                                                                      │├────┤│
│  │                                                                                      ││Lght││
│⎯ │                                                                                      ││3pt ││
│  │                                                                                      │└────┘│
│C │                                                                                      │      │
│A │                                                                                      │ ▶RG  │
│M │                                                                                      │      │
│E │                                                                                      │ ▶CN  │
│R │                                                                                      │      │
│A │                                                                                      │ ▶SL  │
│  │                                                                                      │      │
│⎯ │                                                                                      │ ▶PR  │
│  │                                                                                      │      │
│R │                                                                                      │      │
│E │                                                                                      │      │
│S │                                                                                      │      │
│E │                                                                                      │      │
│T │                                                                                      │      │
│  │                                                                                      │      │
│P │                                                                                      │      │
│A │                                                                                      │      │
│N │                                                                                      │      │
│E │                                                                                      │      │
│L │                                                                                      │      │
├──┴──────────────────────────────────────────────────────────────────────────────────────┴──────┤
│ > view set 4-grid                                      │ Viewport layout: 4-Grid     │ ● Rhino│
│ [Command                                            ]  │ All cameras synchronized     │Connected│
└────────────────────────────────────────────────────────────────────────────────────────────────┘

LEFT: View management | RIGHT: Viewport properties
```

---

## Responsive Behavior

### Collapsed State (F7 - Focus Mode)
```
All panels hidden, only viewport visible:

┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [FILE] [ANALYZE] [EDIT] [VALIDATE] [FABRICATE] [VIEW]                 F7:Exit Focus    │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [Current Tab Tools Here                                                              ] │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                │
│                                                                                                │
│                                     FULL VIEWPORT                                             │
│                                   (1536×704 pixels)                                           │
│                                    81.5% of window                                            │
│                                                                                                │
│                                                                                                │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│ > _                                                     │ Focus Mode Active (F7)       │ ● Rhino│
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Right Panel Collapsed States

```
Collapsed sections (only headers visible):

│ ▶ Viewport     │
│ ▼ Regions (12) │ <- Expanded
│ ▶ Constraints  │
│ ▶ Selection    │
│ ▶ Parameters   │

Each collapsed section = 28px
Expanded content varies by section
```

---

## Design Specifications

### Colors
- Primary: #007AFF
- Success: #34C759
- Warning: #FF9500
- Error: #FF3B30
- Background: #FFFFFF
- Panel BG: #F5F5F5
- Borders: #D1D1D6

### Typography
- Headers: 12px bold
- Body: 11px regular
- Monospace: 10px
- Small: 10px

### Spacing
- Panel padding: 8px
- Section spacing: 16px
- Button spacing: 8px
- List items: 28px height

### Component Heights
- Window title bar: 30px
- Tab bar: 40px
- Toolbars: 40px
- Bottom panel: 120px
- Collapsed section: 28px

### Responsive Breakpoints
- <1600px: Compact mode (icons only left bar)
- 1600-2400px: Standard mode
- >2400px: Comfortable mode (larger panels)

---

## Interaction States

### Hover Effects
- Buttons: Lighten 10%
- Tabs: Underline appears
- List items: Background #E8E8E8

### Active States
- Active tab: Bold + underline
- Selected tool: Blue background
- Selected region: Yellow highlight

### Disabled States
- Opacity: 0.5
- Cursor: not-allowed

---

## Keyboard Navigation

### Tab Switching
- F1-F6: Direct tab access
- Ctrl+Tab: Next tab
- Ctrl+Shift+Tab: Previous tab

### Panel Management
- Ctrl+1-5: Toggle right panels
- F7: Focus mode
- Ctrl+0: Collapse all

### Common Actions
- Space: Reset camera
- Esc: Clear selection
- Ctrl+Z/Y: Undo/Redo

---

## Implementation Priority

### Phase 1: Core Structure
1. Tab system
2. Four-sided layout
3. Basic tool placement

### Phase 2: Functionality
1. Tool connections
2. Command palette
3. Keyboard shortcuts

### Phase 3: Polish
1. Animations
2. Preferences
3. Help system