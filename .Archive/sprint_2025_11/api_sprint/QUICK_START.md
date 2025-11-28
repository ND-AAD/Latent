# Quick Start Guide - 10-Day Sprint

**For**: Nick (Orchestrator)
**Purpose**: Minimum viable instructions to launch and manage agents

---

## Day 0: Preparation (DO THIS FIRST!)

```bash
# Install dependencies (3-4 hours)
brew install cmake pybind11 tbb

# Build OpenSubdiv
cd ~/Downloads
git clone https://github.com/PixarAnimationStudios/OpenSubdiv.git
cd OpenSubdiv && git checkout v3_6_0
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local \
         -DNO_EXAMPLES=ON -DNO_TUTORIALS=ON -DNO_REGRESSION=ON \
         -DNO_DOC=ON -DNO_TESTS=ON -DOSD_ENABLE_METAL=ON
make -j$(sysctl -n hw.ncpu) && sudo make install

# Verify
pkg-config --modversion opensubdiv  # Should show 3.6.0

# Create project dirs
cd "/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent"
mkdir -p cpp_core/{geometry,analysis,constraints,python_bindings,utils}
mkdir -p ceramic_mold_analyzer/app/{bridge,ui,state,analysis}
mkdir -p rhino tests
```

---

## Day 1: Launch First 6 Agents

### Morning (9am)

**Copy/paste this into Claude**:

```markdown
I need to launch 6 agents in parallel for Day 1. Each agent should read their task file and work autonomously.

Agent 1: Read and complete: docs/reference/api_sprint/agent_tasks/day_01/AGENT_01_types_data_structures.md

Agent 2: Read and complete: docs/reference/api_sprint/agent_tasks/day_01/AGENT_02_subd_evaluator_header.md

Agent 3: Read and complete: docs/reference/api_sprint/agent_tasks/day_01/AGENT_03_cmakelists.md

Agent 4: Read and complete: docs/reference/api_sprint/agent_tasks/day_01/AGENT_04_subd_evaluator_impl.md

Agent 5: Read and complete: docs/reference/api_sprint/agent_tasks/day_01/AGENT_05_pybind11_bindings.md

Agent 6: Read and complete: docs/reference/api_sprint/agent_tasks/day_01/AGENT_06_grasshopper_server.md

Launch all in parallel using Task tool.
```

### Afternoon (2pm)

**Integrate morning agents**:

```bash
# Copy files to correct locations (agents will tell you where)
# For C++ files:
cd cpp_core/build
cmake ..
make -j$(sysctl -n hw.ncpu)

# Test Python bindings:
cd ..
python3 test_bindings.py

# Test Grasshopper server:
# (Start server in Grasshopper, then)
curl http://localhost:8888/status
```

### Evening (6pm)

**Launch Agents 7-9**:

```markdown
Launch 3 agents in parallel:

Agent 7: docs/reference/api_sprint/agent_tasks/day_01/AGENT_07_tessellation.md
Agent 8: docs/reference/api_sprint/agent_tasks/day_01/AGENT_08_desktop_bridge.md
Agent 9: docs/reference/api_sprint/agent_tasks/day_01/AGENT_09_basic_tests.md

Use Task tool for parallel execution.
```

---

## Daily Pattern

**Morning**: Launch 6-8 agents
**Afternoon**: Integrate and test
**Evening**: Launch 2-4 more agents
**Night**: Agents work while you sleep

---

## Integration Checklist (After Each Batch)

- [ ] Copy files to correct locations
- [ ] Build C++: `cd cpp_core/build && cmake .. && make`
- [ ] Test Python: `python3 test_*.py`
- [ ] Commit: `git add . && git commit -m "feat: Day X batch Y"`
- [ ] Mark agents complete in MASTER_ORCHESTRATION.md

---

## If Something Breaks

**Agent failed?**
```markdown
Agent X produced this error: [paste error]

Please re-read task file and fix:
docs/reference/api_sprint/agent_tasks/day_XX/AGENT_XX_name.md

Previous attempt: [paste code]
Error: [paste error]

Provide corrected version.
```

**Can't figure it out?**
- Skip for now
- Continue with other agents
- Come back later
- Budget +$50-100 for manual fixes

---

## Progress Tracking

Update this table daily:

| Day | Agents Done | Cost | Notes |
|-----|-------------|------|-------|
| 1   | /9          | $    |       |
| 2   | /8          | $    |       |
| 3   | /8          | $    |       |
| 4   | /8          | $    |       |
| 5   | /6          | $    |       |
| 6   | /6          | $    |       |
| 7   | /6          | $    |       |
| 8   | /6          | $    |       |
| 9   | /6          | $    |       |
| 10  | /4          | $    |       |

---

## Where Are the Task Files?

All agent tasks are in:
```
docs/reference/api_sprint/agent_tasks/day_XX/AGENT_XX_name.md
```

**NOTE**: I'm creating these task files now. Check the `agent_tasks/` folder - they're being generated as we speak!

---

## Key Documents

- **This file**: Quick daily instructions
- **MASTER_ORCHESTRATION.md**: Detailed agent-by-agent breakdown
- **10_DAY_SPRINT_STRATEGY.md**: Overall strategy and rationale
- **IMPLEMENTATION_ROADMAP.md**: Complete technical roadmap

---

**Ready? Start with Day 0 preparation!**
