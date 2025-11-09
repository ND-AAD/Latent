// cpp_core/constraints/constraint_validator.cpp

#include "validator.h"

namespace latent {

ConstraintValidator::ConstraintValidator(const SubDEvaluator& evaluator)
    : evaluator_(evaluator),
      undercut_detector_(evaluator),
      draft_checker_(evaluator) {}

ConstraintReport ConstraintValidator::validate_region(
    const std::vector<int>& face_indices,
    const Vector3& demolding_direction,
    float min_wall_thickness) {

    ConstraintReport report;

    // 1. Check for undercuts
    auto undercut_map = undercut_detector_.detect_undercuts(face_indices, demolding_direction);
    for (const auto& [face_id, severity] : undercut_map) {
        report.add_error(
            "Undercut detected - requires additional mold piece",
            face_id,
            severity
        );
    }

    // 2. Check draft angles
    auto draft_map = draft_checker_.compute_draft_angles(face_indices, demolding_direction);
    for (const auto& [face_id, draft_angle] : draft_map) {
        if (draft_angle < DraftChecker::MIN_DRAFT_ANGLE) {
            // Below minimum - ERROR
            float severity = 1.0f - (draft_angle / DraftChecker::MIN_DRAFT_ANGLE);
            report.add_error(
                "Draft angle below minimum (" + std::to_string(draft_angle) + "° < " + 
                std::to_string(DraftChecker::MIN_DRAFT_ANGLE) + "°)",
                face_id,
                severity
            );
        } else if (draft_angle < DraftChecker::RECOMMENDED_DRAFT_ANGLE) {
            // Below recommended - WARNING
            float severity = 1.0f - (draft_angle / DraftChecker::RECOMMENDED_DRAFT_ANGLE);
            report.add_warning(
                "Draft angle below recommended (" + std::to_string(draft_angle) + "° < " + 
                std::to_string(DraftChecker::RECOMMENDED_DRAFT_ANGLE) + "°)",
                face_id,
                severity
            );
        }
    }

    // 3. Wall thickness check would go here
    // This is a simplified implementation - full thickness analysis would require
    // more sophisticated geometry queries

    return report;
}

} // namespace latent
