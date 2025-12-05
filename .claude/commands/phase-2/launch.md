# Launch Phase 2: Python Analysis Service

Launch 3 parallel agents to create the JSON-RPC analysis service with boundary extraction.

## Pre-Launch Checklist

- [ ] Phase 1 gate tests passed
- [ ] C++ core builds and tests pass
- [ ] Python environment has numpy, scipy, pytest installed
- [ ] Working directory is `/Users/NickDuch/.claude-worktrees/Latent/focused-robinson`

## Agent Overview

| Agent | File | Objective |
|-------|------|-----------|
| 2A | `phase-2/agent-2a-jsonrpc-server.md` | JSON-RPC 2.0 server infrastructure |
| 2B | `phase-2/agent-2b-differential-boundary.md` | Curvature contour extraction (marching squares) |
| 2C | `phase-2/agent-2c-spectral-boundary.md` | Nodal line extraction (zero-crossing) |

## Dependencies

```
Agent 2A (Server) ─────────────────────────┐
                                           ├──► Phase 2 Complete
Agent 2B (Differential Boundary) ──────────┤
                                           │
Agent 2C (Spectral Boundary) ──────────────┘
```

**Parallel execution strategy:**
- All agents can start immediately (independent)
- Agent 2A creates server infrastructure with stub handlers
- Agents 2B and 2C create boundary extraction that plugs into handlers
- Agent 2B's `boundary_extraction.py` is used by Agent 2C's nodal extraction

**File isolation:**
- 2A: `analysis_service/` directory
- 2B: `app/analysis/boundary_extraction.py`, `app/analysis/differential_lens.py`
- 2C: `app/analysis/nodal_extraction.py`, `app/analysis/spectral_lens.py`

## Launch Instructions

Launch 3 agents in parallel using the Task tool:

### Agent 2A
- **Subagent Type**: `general-purpose`
- **Prompt**: Read and execute `/Users/NickDuch/.claude-worktrees/Latent/focused-robinson/.claude/commands/phase-2/agent-2a-jsonrpc-server.md`

### Agent 2B
- **Subagent Type**: `general-purpose`
- **Prompt**: Read and execute `/Users/NickDuch/.claude-worktrees/Latent/focused-robinson/.claude/commands/phase-2/agent-2b-differential-boundary.md`

### Agent 2C
- **Subagent Type**: `general-purpose`
- **Prompt**: Read and execute `/Users/NickDuch/.claude-worktrees/Latent/focused-robinson/.claude/commands/phase-2/agent-2c-spectral-boundary.md`

## Post-Phase Consolidation

After all agents complete:

```bash
cd /Users/NickDuch/.claude-worktrees/Latent/focused-robinson

# Install dependencies
pip install -r analysis_service/requirements.txt

# Run all tests
python -m pytest tests/test_analysis_protocol.py -v
python -m pytest tests/test_boundary_extraction.py -v
python -m pytest tests/test_nodal_extraction.py -v

# Integration test: start server and test endpoints
python -m analysis_service --debug &
SERVER_PID=$!
sleep 2

curl -s http://localhost:5555 -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"ping","params":{},"id":"1"}' | python -m json.tool

curl -s http://localhost:5555 -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"cage":{"vertices":[[0,0,0],[1,0,0],[1,1,0],[0,1,0]],"faces":[[0,1,2,3]],"creases":[]}},"id":"2"}' | python -m json.tool

kill $SERVER_PID

# If all pass, commit
git add -A
git commit -m "feat: Phase 2 - Python analysis service

- Add JSON-RPC 2.0 server infrastructure
- Add marching squares boundary extraction
- Add nodal line extraction from eigenfunctions
- Integrate boundary curves with differential lens
- Integrate nodal lines with spectral lens
- Comprehensive unit tests"
```

## Phase 2 Gate Tests

All must pass before proceeding to Phase 3:

```bash
#!/bin/bash
set -e

echo "=== Phase 2 Gate Tests ==="

cd /Users/NickDuch/.claude-worktrees/Latent/focused-robinson

# Test 2.1: Protocol tests pass
python -m pytest tests/test_analysis_protocol.py -v
echo "✓ Protocol tests passed"

# Test 2.2: Boundary extraction tests pass
python -m pytest tests/test_boundary_extraction.py -v
echo "✓ Boundary extraction tests passed"

# Test 2.3: Nodal extraction tests pass
python -m pytest tests/test_nodal_extraction.py -v
echo "✓ Nodal extraction tests passed"

# Test 2.4: Server starts and responds to ping
python -m analysis_service &
SERVER_PID=$!
sleep 3

PING_RESULT=$(curl -s http://localhost:5555 -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"ping","params":{},"id":"1"}')

kill $SERVER_PID 2>/dev/null || true

if echo "$PING_RESULT" | grep -q '"status".*"ok"'; then
    echo "✓ Server ping successful"
else
    echo "✗ Server ping failed"
    echo "Response: $PING_RESULT"
    exit 1
fi

# Test 2.5: Initialize endpoint works
python -m analysis_service &
SERVER_PID=$!
sleep 3

INIT_RESULT=$(curl -s http://localhost:5555 -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "method":"initialize",
    "params":{
      "cage":{
        "vertices":[[0,0,0],[1,0,0],[1,1,0],[0,1,0]],
        "faces":[[0,1,2,3]],
        "creases":[]
      }
    },
    "id":"2"
  }')

kill $SERVER_PID 2>/dev/null || true

if echo "$INIT_RESULT" | grep -q '"initialized"'; then
    echo "✓ Initialize endpoint works"
else
    echo "✗ Initialize endpoint failed"
    echo "Response: $INIT_RESULT"
    exit 1
fi

echo ""
echo "=== Phase 2 PASSED - Ready for Phase 3 ==="
```

## Troubleshooting

### Agent 2B/2C need existing lens files
- Both agents modify existing files in `app/analysis/`
- If files don't exist, agents should create minimal stubs
- Integration will verify the full flow

### Server fails to start
- Check port 5555 is not in use
- Check all imports resolve correctly
- Run `python -c "from analysis_service import server"` to debug

### Marching squares produces no segments
- Check that threshold value is within the range of grid values
- Verify grid is not uniform (all same value)

### Nodal extraction produces no curves
- Check that eigenfunction has zero-crossings
- Verify tessellation has proper connectivity
