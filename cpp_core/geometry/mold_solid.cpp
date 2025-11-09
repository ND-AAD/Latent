// cpp_core/geometry/mold_solid.cpp

#include "nurbs_generator.h"
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepOffsetAPI_ThruSections.hxx>
#include <BRepOffsetAPI_MakeThickSolid.hxx>
#include <BRepPrimAPI_MakeCylinder.hxx>
#include <BRepAlgoAPI_Fuse.hxx>
#include <BRepCheck_Analyzer.hxx>
#include <TopTools_ListOfShape.hxx>
#include <TopoDS_Solid.hxx>
#include <gp_Ax2.hxx>
#include <gp_Pnt.hxx>
#include <gp_Dir.hxx>
#include <cmath>
#include <stdexcept>

namespace latent {

TopoDS_Shape NURBSMoldGenerator::create_mold_solid(
    Handle(Geom_BSplineSurface) surface,
    float wall_thickness) {

    if (surface.IsNull()) {
        throw std::runtime_error("Cannot create mold solid from null surface");
    }

    if (wall_thickness <= 0.0f) {
        throw std::runtime_error("Wall thickness must be positive");
    }

    try {
        // Step 1: Create face from NURBS surface
        BRepBuilderAPI_MakeFace face_maker(surface, 1e-6);
        
        if (!face_maker.IsDone()) {
            throw std::runtime_error("Failed to create face from NURBS surface");
        }
        
        TopoDS_Face face = face_maker.Face();

        // Step 2: Thicken the face to create a solid
        // Note: BRepOffsetAPI_MakeThickSolid removes specified faces and offsets the rest
        // Since we want to thicken a single face, we need a different approach
        
        // Alternative approach: Use offset surface to create top and bottom faces,
        // then create solid by lofting/stitching
        
        // For now, use a simpler approach with BRepOffsetAPI_MakeThickSolid
        // by converting the face to a thin shell first
        
        TopTools_ListOfShape faces_to_remove;
        // Empty list means offset all faces
        
        BRepOffsetAPI_MakeThickSolid solid_maker;
        
        // Method: offset the face inward and outward to create thickness
        // We'll create the solid by offsetting
        solid_maker.MakeThickSolidByJoin(
            face,
            faces_to_remove,
            wall_thickness,
            1e-6  // tolerance
        );

        if (!solid_maker.IsDone()) {
            throw std::runtime_error("Solid creation failed - thickening operation unsuccessful");
        }

        TopoDS_Shape result = solid_maker.Shape();

        // Step 3: Validate the resulting solid
        BRepCheck_Analyzer analyzer(result);
        if (!analyzer.IsValid()) {
            throw std::runtime_error("Created solid is not valid");
        }

        return result;

    } catch (const Standard_Failure& e) {
        throw std::runtime_error(
            std::string("OpenCASCADE error during solid creation: ") + 
            e.GetMessageString()
        );
    }
}

TopoDS_Shape NURBSMoldGenerator::add_registration_keys(
    TopoDS_Shape mold,
    const std::vector<Point3D>& key_positions) {

    if (mold.IsNull()) {
        throw std::runtime_error("Cannot add keys to null mold shape");
    }

    if (key_positions.empty()) {
        // No keys to add, return original mold
        return mold;
    }

    try {
        TopoDS_Shape result = mold;

        // Registration key parameters
        const float key_radius = 5.0f;      // mm - radius of cylindrical key
        const float key_height = 10.0f;     // mm - height of key protrusion
        const gp_Dir key_direction(0, 0, 1); // Keys extend upward in Z

        // Create and add each registration key
        for (const Point3D& pos : key_positions) {
            // Create axis for cylinder at key position
            gp_Pnt origin(pos.x, pos.y, pos.z);
            gp_Ax2 axis(origin, key_direction);

            // Create cylindrical key
            BRepPrimAPI_MakeCylinder cylinder_maker(axis, key_radius, key_height);
            
            if (!cylinder_maker.IsDone()) {
                throw std::runtime_error("Failed to create registration key cylinder");
            }

            TopoDS_Shape key = cylinder_maker.Shape();

            // Boolean union with mold
            BRepAlgoAPI_Fuse fuse_op(result, key);
            
            if (!fuse_op.IsDone()) {
                throw std::runtime_error("Failed to fuse registration key with mold");
            }

            result = fuse_op.Shape();

            // Validate after each fusion
            BRepCheck_Analyzer analyzer(result);
            if (!analyzer.IsValid()) {
                throw std::runtime_error("Mold shape became invalid after adding registration key");
            }
        }

        return result;

    } catch (const Standard_Failure& e) {
        throw std::runtime_error(
            std::string("OpenCASCADE error during key addition: ") + 
            e.GetMessageString()
        );
    }
}

} // namespace latent
