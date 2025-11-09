# Agent 43: Constraint Python Bindings

**Day**: 6
**Duration**: 2-3 hours
**Cost**: $2-4 (40K tokens)

---

## Mission

Expose C++ constraint validators to Python via pybind11.

---

## Deliverables

**File**: `cpp_core/python_bindings/py_constraints.cpp`

---

## Requirements

```cpp
// Add to py_bindings.cpp

py::enum_<ConstraintLevel>(m, "ConstraintLevel")
    .value("ERROR", ConstraintLevel::ERROR)
    .value("WARNING", ConstraintLevel::WARNING)
    .value("FEATURE", ConstraintLevel::FEATURE);

py::class_<ConstraintViolation>(m, "ConstraintViolation")
    .def_readonly("level", &ConstraintViolation::level)
    .def_readonly("description", &ConstraintViolation::description)
    .def_readonly("face_id", &ConstraintViolation::face_id)
    .def_readonly("severity", &ConstraintViolation::severity);

py::class_<ConstraintValidator>(m, "ConstraintValidator")
    .def(py::init<const SubDEvaluator&>())
    .def("validate_region", &ConstraintValidator::validate_region);
```

---

## Success Criteria

- [ ] Bindings compile
- [ ] Python can import ConstraintValidator
- [ ] Tests call from Python

---

**Ready to begin!**
