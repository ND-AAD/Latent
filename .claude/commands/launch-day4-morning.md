---
description: Launch Day 4 morning agents (26-31) - Curvature analysis
---

Launch 6 agents IN PARALLEL for Day 4 curvature analysis foundation:

Agent 26: docs/reference/api_sprint/DAYS_4_10_AGENT_SUMMARY.md (Curvature Analyzer Header)
Agent 27: docs/reference/api_sprint/DAYS_4_10_AGENT_SUMMARY.md (Curvature Implementation) 
Agent 28: docs/reference/api_sprint/DAYS_4_10_AGENT_SUMMARY.md (Curvature Python Bindings)
Agent 29: docs/reference/api_sprint/DAYS_4_10_AGENT_SUMMARY.md (Curvature Visualization)
Agent 30: docs/reference/api_sprint/DAYS_4_10_AGENT_SUMMARY.md (Curvature Tests)
Agent 31: docs/reference/api_sprint/DAYS_4_10_AGENT_SUMMARY.md (Analysis Panel UI)

**Key Details from Summary**:
- Agent 27 is longest (6-7h) - implements differential geometry from second derivatives
- All use cpp_core module (not latent_core)
- Tests must validate sphere (K=1/r², H=1/r), plane (K=0, H=0)
- Performance target: >1000 curvature evaluations/sec

Use ONE message with 6 Task tool calls. Each agent reads summary and works autonomously.
