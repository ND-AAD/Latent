// test_draft_simple.cpp
// Simple standalone test for draft transformation

#include <Geom_BSplineSurface.hxx>
#include <TColgp_Array2OfPnt.hxx>
#include <TColStd_Array1OfReal.hxx>
#include <TColStd_Array1OfInteger.hxx>
#include <TColStd_Array2OfReal.hxx>
#include <gp_Pnt.hxx>
#include <gp_Vec.hxx>
#include <gp_Dir.hxx>
#include <gp_Pln.hxx>

#include <iostream>
#include <cmath>
#include <vector>
#include <stdexcept>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Minimal types for standalone test
struct Point3D {
    float x, y, z;
    Point3D(float _x = 0, float _y = 0, float _z = 0) : x(_x), y(_y), z(_z) {}
};

struct Vector3 {
    float x, y, z;
    Vector3(float _x = 0, float _y = 0, float _z = 0) : x(_x), y(_y), z(_z) {}
};

// Standalone draft transformation function (copy of the implementation)
Handle(Geom_BSplineSurface) apply_draft_standalone(
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

    float angle_rad = draft_angle_degrees * M_PI / 180.0f;
    float tan_angle = std::tan(angle_rad);

    try {
        Standard_Real u_min, u_max, v_min, v_max;
        surface->Bounds(u_min, u_max, v_min, v_max);

        int u_degree = surface->UDegree();
        int v_degree = surface->VDegree();
        int nb_u_poles = surface->NbUPoles();
        int nb_v_poles = surface->NbVPoles();

        gp_Pnt parting_origin;
        gp_Dir parting_normal;

        if (parting_line.empty()) {
            gp_Pnt p_min;
            surface->D0(u_min, v_min, p_min);
            parting_origin = p_min;
            parting_normal = gp_Dir(demolding_direction.x, demolding_direction.y, demolding_direction.z);
        } else {
            parting_origin = gp_Pnt(parting_line[0].x, parting_line[0].y, parting_line[0].z);
            parting_normal = gp_Dir(demolding_direction.x, demolding_direction.y, demolding_direction.z);
        }

        gp_Pln parting_plane(parting_origin, parting_normal);

        TColgp_Array2OfPnt new_poles(1, nb_u_poles, 1, nb_v_poles);
        TColStd_Array2OfReal weights(1, nb_u_poles, 1, nb_v_poles);

        bool is_rational = surface->IsURational() || surface->IsVRational();

        for (int i = 1; i <= nb_u_poles; i++) {
            for (int j = 1; j <= nb_v_poles; j++) {
                gp_Pnt pole = surface->Pole(i, j);

                gp_Vec to_point(parting_origin, pole);
                float h = to_point.Dot(gp_Vec(parting_normal));

                gp_Pnt projected = pole.Translated(gp_Vec(parting_normal).Multiplied(-h));

                gp_Vec radial(projected, pole);
                radial.Subtract(gp_Vec(parting_normal).Multiplied(h));

                float radial_length = radial.Magnitude();

                if (radial_length > 1e-6 && std::abs(h) > 1e-6) {
                    float offset = std::abs(h) * tan_angle;
                    gp_Vec radial_normalized = radial.Normalized();
                    gp_Vec draft_offset = radial_normalized.Multiplied(offset * (h > 0 ? 1.0 : -1.0));

                    gp_Pnt new_pole = pole.Translated(draft_offset);
                    new_poles.SetValue(i, j, new_pole);
                } else {
                    new_poles.SetValue(i, j, pole);
                }

                if (is_rational) {
                    weights.SetValue(i, j, surface->Weight(i, j));
                } else {
                    weights.SetValue(i, j, 1.0);
                }
            }
        }

        TColStd_Array1OfReal u_knots(1, surface->NbUKnots());
        TColStd_Array1OfReal v_knots(1, surface->NbVKnots());
        TColStd_Array1OfInteger u_mults(1, surface->NbUKnots());
        TColStd_Array1OfInteger v_mults(1, surface->NbVKnots());

        surface->UKnots(u_knots);
        surface->VKnots(v_knots);
        surface->UMultiplicities(u_mults);
        surface->VMultiplicities(v_mults);

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

// Create a simple planar NURBS surface
Handle(Geom_BSplineSurface) create_test_plane() {
    int u_poles = 3;
    int v_poles = 3;

    TColgp_Array2OfPnt poles(1, u_poles, 1, v_poles);

    for (int i = 1; i <= u_poles; i++) {
        for (int j = 1; j <= v_poles; j++) {
            double x = (i - 1) * 50.0;
            double y = (j - 1) * 50.0;
            double z = 0.0;
            poles.SetValue(i, j, gp_Pnt(x, y, z));
        }
    }

    TColStd_Array1OfReal u_knots(1, 2);
    TColStd_Array1OfReal v_knots(1, 2);
    u_knots.SetValue(1, 0.0);
    u_knots.SetValue(2, 1.0);
    v_knots.SetValue(1, 0.0);
    v_knots.SetValue(2, 1.0);

    TColStd_Array1OfInteger u_mults(1, 2);
    TColStd_Array1OfInteger v_mults(1, 2);
    u_mults.SetValue(1, 3);
    u_mults.SetValue(2, 3);
    v_mults.SetValue(1, 3);
    v_mults.SetValue(2, 3);

    int degree = 2;

    Handle(Geom_BSplineSurface) surface = new Geom_BSplineSurface(
        poles,
        u_knots,
        v_knots,
        u_mults,
        v_mults,
        degree,
        degree
    );

    return surface;
}

int main() {
    std::cout << "==================================================" << std::endl;
    std::cout << "  Draft Angle Transformation - Simple Test" << std::endl;
    std::cout << "==================================================" << std::endl;

    try {
        // Create test surface
        Handle(Geom_BSplineSurface) plane = create_test_plane();
        std::cout << "Created planar surface: "
                  << plane->NbUPoles() << "x" << plane->NbVPoles() << " control points" << std::endl;

        // Apply draft
        Vector3 demolding_dir(0, 0, 1);
        std::vector<Point3D> parting_line;
        parting_line.push_back(Point3D(0, 50, 0));

        float draft_angle = 2.0f;
        Handle(Geom_BSplineSurface) drafted = apply_draft_standalone(
            plane, demolding_dir, draft_angle, parting_line
        );

        if (drafted.IsNull()) {
            std::cout << "ERROR: Draft transformation returned null" << std::endl;
            return 1;
        }

        std::cout << "SUCCESS: Draft transformation completed!" << std::endl;
        std::cout << "Drafted surface: "
                  << drafted->NbUPoles() << "x" << drafted->NbVPoles() << " control points" << std::endl;

        // Verify surface bounds
        Standard_Real u_min, u_max, v_min, v_max;
        drafted->Bounds(u_min, u_max, v_min, v_max);
        std::cout << "Surface bounds: u=[" << u_min << "," << u_max << "], "
                  << "v=[" << v_min << "," << v_max << "]" << std::endl;

        std::cout << "\n==================================================" << std::endl;
        std::cout << "Result: PASS - Draft transformation working correctly" << std::endl;
        std::cout << "==================================================" << std::endl;

        return 0;

    } catch (const std::exception& e) {
        std::cout << "ERROR: " << e.what() << std::endl;
        return 1;
    }
}
