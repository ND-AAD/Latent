// cpp_core/geometry/draft_transform.cpp

#include "nurbs_generator.h"
#include <BRepOffsetAPI_DraftAngle.hxx>
#include <gp_Pln.hxx>
#include <gp_Ax1.hxx>
#include <gp_Dir.hxx>
#include <gp_Pnt.hxx>
#include <gp_Vec.hxx>
#include <TColgp_Array2OfPnt.hxx>
#include <TColStd_Array2OfReal.hxx>
#include <TColStd_Array1OfReal.hxx>
#include <TColStd_Array1OfInteger.hxx>
#include <cmath>
#include <stdexcept>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace latent {

Handle(Geom_BSplineSurface) NURBSMoldGenerator::apply_draft_angle(
    Handle(Geom_BSplineSurface) surface,
    const Vector3& demolding_direction,
    float draft_angle_degrees,
    const std::vector<Point3D>& parting_line) {

    if (surface.IsNull()) {
        throw std::runtime_error("Cannot apply draft angle to null surface");
    }

    if (draft_angle_degrees < 0.0f || draft_angle_degrees > 45.0f) {
        throw std::runtime_error("Draft angle must be between 0 and 45 degrees");
    }

    // Convert draft angle to radians
    float angle_rad = draft_angle_degrees * M_PI / 180.0f;
    float tan_angle = std::tan(angle_rad);

    try {
        // Get surface parameters
        Standard_Real u_min, u_max, v_min, v_max;
        surface->Bounds(u_min, u_max, v_min, v_max);

        // Get surface degree and control points
        int u_degree = surface->UDegree();
        int v_degree = surface->VDegree();
        int nb_u_poles = surface->NbUPoles();
        int nb_v_poles = surface->NbVPoles();

        // Calculate parting plane from parting line
        // Use first point as origin and demolding direction as normal
        gp_Pnt parting_origin;
        gp_Dir parting_normal;

        if (parting_line.empty()) {
            // If no parting line provided, use surface minimum bound as reference
            gp_Pnt p_min;
            surface->D0(u_min, v_min, p_min);
            parting_origin = p_min;
            parting_normal = gp_Dir(demolding_direction.x, demolding_direction.y, demolding_direction.z);
        } else {
            // Use parting line to define parting plane
            parting_origin = gp_Pnt(parting_line[0].x, parting_line[0].y, parting_line[0].z);
            parting_normal = gp_Dir(demolding_direction.x, demolding_direction.y, demolding_direction.z);
        }

        gp_Pln parting_plane(parting_origin, parting_normal);

        // Create new control point array
        TColgp_Array2OfPnt new_poles(1, nb_u_poles, 1, nb_v_poles);
        TColStd_Array2OfReal weights(1, nb_u_poles, 1, nb_v_poles);

        // Get original weights if rational
        bool is_rational = surface->IsURational() || surface->IsVRational();

        // Transform each control point
        for (int i = 1; i <= nb_u_poles; i++) {
            for (int j = 1; j <= nb_v_poles; j++) {
                gp_Pnt pole = surface->Pole(i, j);

                // Calculate signed distance from parting plane along demolding direction
                gp_Vec to_point(parting_origin, pole);
                float h = to_point.Dot(gp_Vec(parting_normal)) ;

                // Project point onto parting plane
                gp_Pnt projected = pole.Translated(gp_Vec(parting_normal).Multiplied(-h));

                // Calculate radial vector (perpendicular to demolding direction)
                gp_Vec radial(projected, pole);
                radial.Subtract(gp_Vec(parting_normal).Multiplied(h));

                float radial_length = radial.Magnitude();

                if (radial_length > 1e-6 && std::abs(h) > 1e-6) {
                    // Apply draft: offset = h * tan(draft_angle)
                    float offset = std::abs(h) * tan_angle;

                    // Normalize radial vector and apply offset
                    gp_Vec radial_normalized = radial.Normalized();
                    gp_Vec draft_offset = radial_normalized.Multiplied(offset * (h > 0 ? 1.0 : -1.0));

                    // Apply transformation
                    gp_Pnt new_pole = pole.Translated(draft_offset);
                    new_poles.SetValue(i, j, new_pole);
                } else {
                    // Point is on or very close to parting plane or parting line - keep unchanged
                    new_poles.SetValue(i, j, pole);
                }

                // Preserve weights
                if (is_rational) {
                    weights.SetValue(i, j, surface->Weight(i, j));
                } else {
                    weights.SetValue(i, j, 1.0);
                }
            }
        }

        // Get knot vectors
        TColStd_Array1OfReal u_knots(1, surface->NbUKnots());
        TColStd_Array1OfReal v_knots(1, surface->NbVKnots());
        TColStd_Array1OfInteger u_mults(1, surface->NbUKnots());
        TColStd_Array1OfInteger v_mults(1, surface->NbVKnots());

        surface->UKnots(u_knots);
        surface->VKnots(v_knots);
        surface->UMultiplicities(u_mults);
        surface->VMultiplicities(v_mults);

        // Create new NURBS surface with transformed control points
        Handle(Geom_BSplineSurface) drafted_surface = new Geom_BSplineSurface(
            new_poles,
            weights,
            u_knots,
            v_knots,
            u_mults,
            v_mults,
            u_degree,
            v_degree,
            surface->IsUPeriodic(),
            surface->IsVPeriodic()
        );

        return drafted_surface;

    } catch (const Standard_Failure& e) {
        throw std::runtime_error(
            std::string("OpenCASCADE error during draft transformation: ") +
            e.GetMessageString()
        );
    }
}

} // namespace latent
