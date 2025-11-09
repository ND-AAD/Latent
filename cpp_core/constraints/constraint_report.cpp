// cpp_core/constraints/constraint_report.cpp

#include "validator.h"

namespace latent {

void ConstraintReport::add_error(const std::string& desc, int face_id, float severity) {
    ConstraintViolation violation;
    violation.level = ConstraintLevel::ERROR;
    violation.description = desc;
    violation.face_id = face_id;
    violation.severity = severity;
    violation.suggestion = "This region requires revision to eliminate physical impossibility";
    violations.push_back(violation);
}

void ConstraintReport::add_warning(const std::string& desc, int face_id, float severity) {
    ConstraintViolation violation;
    violation.level = ConstraintLevel::WARNING;
    violation.description = desc;
    violation.face_id = face_id;
    violation.severity = severity;
    violation.suggestion = "Consider adjusting geometry for better manufacturability";
    violations.push_back(violation);
}

void ConstraintReport::add_feature(const std::string& desc, int face_id) {
    ConstraintViolation violation;
    violation.level = ConstraintLevel::FEATURE;
    violation.description = desc;
    violation.face_id = face_id;
    violation.severity = 0.0f;
    violation.suggestion = "This is an aesthetic feature - mathematical tension";
    violations.push_back(violation);
}

bool ConstraintReport::has_errors() const {
    for (const auto& v : violations) {
        if (v.level == ConstraintLevel::ERROR) return true;
    }
    return false;
}

bool ConstraintReport::has_warnings() const {
    for (const auto& v : violations) {
        if (v.level == ConstraintLevel::WARNING) return true;
    }
    return false;
}

int ConstraintReport::error_count() const {
    int count = 0;
    for (const auto& v : violations) {
        if (v.level == ConstraintLevel::ERROR) count++;
    }
    return count;
}

int ConstraintReport::warning_count() const {
    int count = 0;
    for (const auto& v : violations) {
        if (v.level == ConstraintLevel::WARNING) count++;
    }
    return count;
}

} // namespace latent
