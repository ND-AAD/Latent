// cpp_core/geometry/nurbs_generator.h

#pragma once

#include "types.h"
#include "subd_evaluator.h"

// OpenCASCADE includes
#include <TopoDS_Shape.hxx>
#include <TopoDS_Face.hxx>
#include <Geom_BSplineSurface.hxx>

#include <vector>

namespace latent {

// NURBS mold generator
class NURBSMoldGenerator {
public:
    NURBSMoldGenerator(const SubDEvaluator& evaluator);

    // 1. Sample exact limit surface and fit NURBS
    Handle(Geom_BSplineSurface) fit_nurbs_surface(
        const std::vector<int>& face_indices,
        int sample_density = 50  // Samples per face dimension
    );

    // 2. Apply draft angle transformation
    Handle(Geom_BSplineSurface) apply_draft_angle(
        Handle(Geom_BSplineSurface) surface,
        const Vector3& demolding_direction,
        float draft_angle_degrees,
        const std::vector<Point3D>& parting_line  // Fixed base curve
    );

    // 3. Create solid mold cavity
    TopoDS_Shape create_mold_solid(
        Handle(Geom_BSplineSurface) surface,
        float wall_thickness = 40.0f  // mm
    );

    // 4. Add registration features (keys/notches)
    TopoDS_Shape add_registration_keys(
        TopoDS_Shape mold,
        const std::vector<Point3D>& key_positions
    );

    // Quality control
    struct FittingQuality {
        float max_deviation;     // mm
        float mean_deviation;    // mm
        float rms_deviation;     // mm
        int num_samples;
        bool passes_tolerance;   // True if max_deviation < 0.1mm
    };

    FittingQuality check_fitting_quality(
        Handle(Geom_BSplineSurface) nurbs,
        const std::vector<int>& face_indices
    );

private:
    const SubDEvaluator& evaluator_;

    // Sample limit surface at regular grid
    std::vector<Point3D> sample_limit_surface(
        const std::vector<int>& face_indices,
        int density
    );
};

} // namespace latent
