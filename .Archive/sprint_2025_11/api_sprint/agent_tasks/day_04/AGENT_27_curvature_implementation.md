# Agent 27: Curvature Implementation

**Day**: 4 | **Duration**: 6-7h | **Cost**: $7-12

## Mission
Implement differential geometry curvature computations from exact SubD limit surface second derivatives.

## Deliverables
- `cpp_core/analysis/curvature_analyzer.cpp` - Full implementation
- Uses Agent 10's second derivative evaluation
- `cpp_core/test_curvature.cpp` - Curvature tests

## Requirements
**Algorithms**:
- First fundamental form (I): E, F, G coefficients
- Second fundamental form (II): L, M, N coefficients  
- Shape operator: S = I^(-1) * II
- Eigenvalues of S → principal curvatures
- Eigenvectors of S → principal directions

**Performance**: >1000 curvature evaluations/sec

## Success Criteria
- [ ] All curvature types computed
- [ ] Sphere test: K=1/r², H=1/r
- [ ] Plane test: K=0, H=0
- [ ] Tests pass
