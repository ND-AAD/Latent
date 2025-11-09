# Agent 50: NURBS Python Bindings

**Day**: 7
**Duration**: 2-3 hours
**Cost**: $3-5 (50K tokens)

---

## Mission

Expose NURBS mold generator to Python via pybind11.

---

## Deliverables

**File**: Update `cpp_core/python_bindings/py_bindings.cpp`

---

## Requirements

```cpp
// Add to py_bindings.cpp

py::class_<NURBSMoldGenerator>(m, "NURBSMoldGenerator")
    .def(py::init<const SubDEvaluator&>())
    .def("fit_nurbs_surface", &NURBSMoldGenerator::fit_nurbs_surface,
         py::arg("face_indices"), py::arg("sample_density") = 50)
    .def("create_mold_solid", &NURBSMoldGenerator::create_mold_solid,
         py::arg("surface"), py::arg("wall_thickness") = 40.0f);

// Note: OpenCASCADE Handle types need special handling
// May need custom conversion or serialization
```

---

## Success Criteria

- [ ] Bindings compile
- [ ] Python can call NURBS generator
- [ ] Tests import and execute

---

**Ready to begin!**
