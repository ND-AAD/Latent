# API Sprint Documentation

**10-Day Sprint to Build Latent MVP**

---

## Document Structure

```
api_sprint/
├── README.md                          # This file
├── QUICK_START.md                     # Daily launch commands (START HERE!)
├── MASTER_ORCHESTRATION.md            # Detailed agent management
├── 10_DAY_SPRINT_STRATEGY.md          # Overall strategy
├── IMPLEMENTATION_ROADMAP.md          # Complete technical roadmap
└── agent_tasks/                       # Individual agent task files
    ├── day_01/ (9 agents)
    ├── day_02/ (8 agents)
    ├── day_03/ (8 agents)
    ├── day_04/ (8 agents)
    ├── day_05/ (6 agents)
    ├── day_06/ (6 agents)
    ├── day_07/ (6 agents)
    ├── day_08/ (6 agents)
    ├── day_09/ (6 agents)
    └── day_10/ (4 agents)
```

---

## How to Use This System

### Step 1: Read QUICK_START.md
Contains minimum viable instructions for each day.

### Step 2: Complete Day 0 Preparation
Install all dependencies before launching any agents.

### Step 3: Launch Agents Daily
Use the templates in QUICK_START.md to launch agents in parallel.

### Step 4: Integrate Outputs
Follow integration checklists after each batch.

---

## Agent Task File Format

Each agent has a dedicated markdown file with:

**Standard Sections**:
1. **Mission** - What the agent will accomplish
2. **Context** - Background and dependencies
3. **Deliverables** - Specific files to create
4. **Requirements** - Detailed specifications
5. **Code Template** - Starting point
6. **Success Criteria** - How to verify completion
7. **Testing** - Validation steps
8. **Integration Notes** - How it fits with other agents
9. **Output Format** - What to provide

**Benefits**:
- ✅ Agents work completely autonomously
- ✅ Minimal orchestrator input needed
- ✅ Clear success criteria
- ✅ Built-in testing
- ✅ Reduced back-and-forth

---

## Current Status

### Completed Task Files

**Day 1** (3/9 files created):
- [x] AGENT_01_types_data_structures.md
- [x] AGENT_02_subd_evaluator_header.md
- [x] AGENT_03_cmakelists.md
- [ ] AGENT_04_subd_evaluator_impl.md (NEEDED)
- [ ] AGENT_05_pybind11_bindings.md (NEEDED)
- [ ] AGENT_06_grasshopper_server.md (NEEDED)
- [ ] AGENT_07_tessellation.md (NEEDED)
- [ ] AGENT_08_desktop_bridge.md (NEEDED)
- [ ] AGENT_09_basic_tests.md (NEEDED)

**Days 2-10**: Template files need to be generated

---

## Generating Remaining Task Files

You have two options:

### Option 1: Generate On-Demand
Create task files as needed before each day's launch. This is flexible but requires more work during the sprint.

### Option 2: Pre-Generate All Files
Create all 67 agent task files upfront (recommended). This front-loads the work but makes the sprint run smoother.

**Recommendation**: Generate Day 1-3 files immediately (critical path), then generate remaining days as you progress.

---

## Task File Template

```markdown
# Agent X: [Name]

**Day**: X
**Phase**: [Phase Name]
**Duration**: X hours
**Estimated Cost**: $X-Y (XXK tokens, Sonnet/Haiku)

---

## Mission
[Clear one-sentence goal]

---

## Context
[Background, dependencies, architectural context]

---

## Deliverables
[Specific files to create with paths]

---

## Requirements
[Detailed specifications, interfaces, algorithms]

---

## Code Template
[Starting code structure]

---

## Success Criteria
[Checklist of completion requirements]

---

## Testing
[How to validate the work]

---

## Integration Notes
[Dependencies on other agents, integration steps]

---

## Output Format
[What to provide in response]

---

**Ready to begin!**
```

---

## Next Steps

### Immediate (Before Day 1)

1. **Complete Day 0 Preparation** (~4 hours)
   - Install all dependencies
   - Verify OpenSubdiv builds
   - Set up project structure

2. **Generate Remaining Day 1 Task Files** (~30 minutes)
   - Agents 4-9 (6 files)
   - Critical for tomorrow's launch

3. **Review QUICK_START.md**
   - Understand daily pattern
   - Prepare launch commands

### During Sprint

1. **Generate next day's files** evening before
2. **Launch agents** using QUICK_START templates
3. **Integrate outputs** following checklists
4. **Track progress** in MASTER_ORCHESTRATION.md

---

## Budget & Timeline

**Total Budget**: $1000
**Expected Cost**: $242-412
**Reserve**: $588-758

**Timeline**: 10 days (67 agents)
**Parallelism**: 6-8 agents simultaneously
**Your Time**: 8-12 hours/day

---

## Questions?

Refer to:
- **Quick daily instructions**: QUICK_START.md
- **Agent management**: MASTER_ORCHESTRATION.md
- **Strategy rationale**: 10_DAY_SPRINT_STRATEGY.md
- **Technical details**: IMPLEMENTATION_ROADMAP.md

---

## File Status Summary

| Category | Status | Location |
|----------|--------|----------|
| Strategy docs | ✅ Complete | api_sprint/ |
| Day 1 tasks | ⏳ 3/9 created | agent_tasks/day_01/ |
| Day 2-10 tasks | ❌ Not created | agent_tasks/day_XX/ |
| Quick start | ✅ Complete | QUICK_START.md |
| Orchestration | ✅ Complete | MASTER_ORCHESTRATION.md |

---

**System is ready! Generate remaining task files before launch.**
