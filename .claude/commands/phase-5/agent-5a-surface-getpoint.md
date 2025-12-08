# Agent 5A: Surface-Constrained GetPoint

## Objective

Implement a custom GetPoint class that constrains picking to the SubD limit surface and tracks parametric coordinates (faceId, u, v).

## Working Directory

`/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent`

## Read First

- `docs/plans/2025-12-04-rhino-plugin-implementation-plan.md` - GetPoint examples
- `rhino_plugin/Interop/SubDEvaluator.cs` - evaluator with ProjectPoint method
- `rhino_plugin/Geometry/Vertex.cs` - uses ParametricPoint for positions

## Dependencies

**From Phase 3:**
- `SubDEvaluator` - provides `ProjectPoint(Point3d)` → (faceId, u, v)
- `SubDEvaluator` - provides `EvaluatePoint(faceId, u, v)` → Point3d

**RhinoCommon:**
- `Rhino.Input.Custom.GetPoint` - base class for point picking
- `Rhino.Geometry.SubD` - the surface to constrain to

## Files to Create

1. `rhino_plugin/Interaction/SurfaceConstrainedGetPoint.cs` - constrained GetPoint
2. `rhino_plugin/Tests/SurfaceGetPointTests.cs` - unit tests

**IMPORTANT**: Do NOT create a new `ParametricPoint` class. Use the existing `Latent.Interop.ParametricPoint` struct from Phase 3.

## Tasks

### 1. Create SurfaceConstrainedGetPoint.cs

```csharp
// rhino_plugin/Interaction/SurfaceConstrainedGetPoint.cs
using System;
using System.Drawing;
using Rhino;
using Rhino.Display;
using Rhino.Geometry;
using Rhino.Input.Custom;
using Latent.Interop;

namespace Latent.Interaction
{
    /// <summary>
    /// GetPoint that constrains picking to a SubD surface and tracks parametric coordinates.
    /// Uses Latent.Interop.ParametricPoint from Phase 3.
    /// </summary>
    public class SurfaceConstrainedGetPoint : GetPoint
    {
        private readonly SubD _subd;
        private readonly SubDEvaluator _evaluator;
        private ParametricPoint _currentParam;  // Uses Latent.Interop.ParametricPoint
        private Point3d _currentPoint3d = Point3d.Unset;
        private Vector3d _currentNormal = Vector3d.Unset;

        /// <summary>
        /// The current parametric position on the surface.
        /// Updated during mouse move. Check IsValid before using.
        /// </summary>
        public ParametricPoint CurrentParametricPosition => _currentParam;

        /// <summary>
        /// Whether the current parametric position is valid.
        /// </summary>
        public bool HasValidPosition => _currentParam.IsValid;

        /// <summary>
        /// The current 3D point on the surface.
        /// </summary>
        public Point3d CurrentSurfacePoint => _currentPoint3d;

        /// <summary>
        /// The surface normal at the current point.
        /// </summary>
        public Vector3d CurrentNormal => _currentNormal;

        /// <summary>
        /// Whether to show the surface normal during picking.
        /// </summary>
        public bool ShowNormal { get; set; } = false;

        /// <summary>
        /// Length of normal arrow when ShowNormal is true.
        /// </summary>
        public double NormalArrowLength { get; set; } = 1.0;

        /// <summary>
        /// Color for the normal arrow.
        /// </summary>
        public Color NormalColor { get; set; } = Color.Blue;

        /// <summary>
        /// Whether to show parametric coordinates in status bar.
        /// </summary>
        public bool ShowParametricCoords { get; set; } = true;

        /// <summary>
        /// Create a surface-constrained GetPoint.
        /// </summary>
        /// <param name="subd">The SubD surface to constrain to</param>
        /// <param name="evaluator">Evaluator for the SubD</param>
        public SurfaceConstrainedGetPoint(SubD subd, SubDEvaluator evaluator)
        {
            _subd = subd ?? throw new ArgumentNullException(nameof(subd));
            _evaluator = evaluator ?? throw new ArgumentNullException(nameof(evaluator));

            // Constrain picking to the SubD surface
            Constrain(_subd, allowPickingPointOffObject: false);

            // Enable dynamic drawing for visual feedback
            DynamicDraw += OnDynamicDraw;
        }

        /// <summary>
        /// Called when mouse moves during point picking.
        /// </summary>
        protected override void OnMouseMove(GetPointMouseEventArgs e)
        {
            base.OnMouseMove(e);

            // Project the current point to parametric space
            var point3d = e.Point;

            if (_evaluator.ProjectPoint(point3d, out int faceId, out float u, out float v))
            {
                _currentParam = new ParametricPoint(faceId, u, v);
                _currentPoint3d = _evaluator.EvaluatePoint(faceId, u, v);

                // Get normal if needed
                if (ShowNormal)
                {
                    var normal = _evaluator.GetNormal(faceId, u, v);
                    _currentNormal = normal ?? Vector3d.Unset;
                }

                // Update status bar
                if (ShowParametricCoords)
                {
                    RhinoApp.SetCommandPromptMessage($"Face {faceId} ({u:F3}, {v:F3})");
                }
            }
            else
            {
                _currentParam = ParametricPoint.Unset;
                _currentPoint3d = Point3d.Unset;
                _currentNormal = Vector3d.Unset;
            }
        }

        /// <summary>
        /// Dynamic draw callback for visual feedback.
        /// </summary>
        private void OnDynamicDraw(object sender, GetPointDrawEventArgs e)
        {
            if (!HasValidPosition)
                return;

            // Draw a point marker at current position
            e.Display.DrawPoint(_currentPoint3d, PointStyle.RoundControlPoint, 5, Color.Yellow);

            // Draw normal if enabled
            if (ShowNormal && _currentNormal.IsValid)
            {
                var endPoint = _currentPoint3d + _currentNormal * NormalArrowLength;
                e.Display.DrawArrow(
                    new Line(_currentPoint3d, endPoint),
                    NormalColor,
                    0.0,   // screen size
                    0.2);  // arrow head size ratio
            }
        }

        /// <summary>
        /// Get a point with full parametric information.
        /// </summary>
        /// <returns>Result including parametric coordinates</returns>
        public SurfacePickResult GetSurfacePoint()
        {
            var result = Get();

            return new SurfacePickResult
            {
                Result = result,
                Point3d = _currentPoint3d,
                ParametricPoint = _currentParam,
                Normal = _currentNormal
            };
        }

        /// <summary>
        /// Set the base point for distance display.
        /// </summary>
        public void SetBasePointFromParametric(ParametricPoint param)
        {
            if (!param.IsValid) return;

            var point3d = _evaluator.EvaluatePoint(param.FaceId, (float)param.U, (float)param.V);
            SetBasePoint(point3d, showDistanceInStatusBar: true);
        }
    }

    /// <summary>
    /// Result from a surface pick operation.
    /// </summary>
    public class SurfacePickResult
    {
        /// <summary>
        /// The GetResult from the pick operation.
        /// </summary>
        public GetResult Result { get; set; }

        /// <summary>
        /// The 3D point on the surface.
        /// </summary>
        public Point3d Point3d { get; set; }

        /// <summary>
        /// The parametric coordinates on the surface.
        /// </summary>
        public ParametricPoint ParametricPoint { get; set; }

        /// <summary>
        /// The surface normal at the pick point.
        /// </summary>
        public Vector3d Normal { get; set; }

        /// <summary>
        /// Whether the pick was successful.
        /// </summary>
        public bool Success => Result == GetResult.Point && ParametricPoint.IsValid;
    }
}
```

### 2. Create Unit Tests

**NOTE**: The `Latent.Interop.ParametricPoint` struct from Phase 3 is a simple struct. These tests verify the SurfaceConstrainedGetPoint class behavior, not the ParametricPoint (already tested in Phase 3).

```csharp
// rhino_plugin/Tests/SurfaceGetPointTests.cs
using System;
using NUnit.Framework;
using Rhino.Geometry;
using Latent.Interaction;
using Latent.Interop;

namespace Latent.Tests
{
    [TestFixture]
    public class SurfaceConstrainedGetPointTests
    {
        [Test]
        public void Constructor_WithNullSubD_ThrowsArgumentNull()
        {
            var evaluator = new SubDEvaluator();
            Assert.Throws<ArgumentNullException>(() =>
                new SurfaceConstrainedGetPoint(null, evaluator));
        }

        [Test]
        public void Constructor_WithNullEvaluator_ThrowsArgumentNull()
        {
            var subd = SubD.CreateFromMesh(Mesh.CreateFromBox(new BoundingBox(Point3d.Origin, new Point3d(1, 1, 1)), 1, 1, 1), SubDCreationOptions.FromNgons);
            Assert.Throws<ArgumentNullException>(() =>
                new SurfaceConstrainedGetPoint(subd, null));
        }

        [Test]
        public void ShowNormal_DefaultsFalse()
        {
            var subd = CreateTestSubD();
            var evaluator = new SubDEvaluator();
            var gp = new SurfaceConstrainedGetPoint(subd, evaluator);

            Assert.That(gp.ShowNormal, Is.False);
        }

        [Test]
        public void ShowParametricCoords_DefaultsTrue()
        {
            var subd = CreateTestSubD();
            var evaluator = new SubDEvaluator();
            var gp = new SurfaceConstrainedGetPoint(subd, evaluator);

            Assert.That(gp.ShowParametricCoords, Is.True);
        }

        [Test]
        public void HasValidPosition_InitiallyFalse()
        {
            var subd = CreateTestSubD();
            var evaluator = new SubDEvaluator();
            var gp = new SurfaceConstrainedGetPoint(subd, evaluator);

            Assert.That(gp.HasValidPosition, Is.False);
        }

        [Test]
        public void CurrentParametricPosition_InitiallyInvalid()
        {
            var subd = CreateTestSubD();
            var evaluator = new SubDEvaluator();
            var gp = new SurfaceConstrainedGetPoint(subd, evaluator);

            // FaceId of 0 (default int) with no projection done = check IsValid
            Assert.That(gp.CurrentParametricPosition.IsValid, Is.False);
        }

        private SubD CreateTestSubD()
        {
            // Create a simple box mesh and convert to SubD
            var mesh = Mesh.CreateFromBox(
                new BoundingBox(Point3d.Origin, new Point3d(1, 1, 1)),
                1, 1, 1);
            return SubD.CreateFromMesh(mesh, SubDCreationOptions.FromNgons);
        }
    }

    [TestFixture]
    public class SurfacePickResultTests
    {
        [Test]
        public void Success_WhenPointAndValidParam_ReturnsTrue()
        {
            var result = new SurfacePickResult
            {
                Result = Rhino.Input.GetResult.Point,
                ParametricPoint = new ParametricPoint(0, 0.5, 0.5)
            };

            Assert.That(result.Success, Is.True);
        }

        [Test]
        public void Success_WhenCanceled_ReturnsFalse()
        {
            var result = new SurfacePickResult
            {
                Result = Rhino.Input.GetResult.Cancel,
                ParametricPoint = new ParametricPoint(0, 0.5, 0.5)
            };

            Assert.That(result.Success, Is.False);
        }

        [Test]
        public void Success_WhenInvalidParam_ReturnsFalse()
        {
            var result = new SurfacePickResult
            {
                Result = Rhino.Input.GetResult.Point,
                ParametricPoint = ParametricPoint.Unset  // Invalid point
            };

            Assert.That(result.Success, Is.False);
        }
    }
}
```

## Success Criteria

- [ ] Uses `Latent.Interop.ParametricPoint` from Phase 3 (no duplicate struct)
- [ ] `SurfaceConstrainedGetPoint` constrains picking to SubD surface
- [ ] `OnMouseMove` updates parametric coordinates via projection
- [ ] Visual feedback shows current point during picking
- [ ] Optional normal display works when enabled
- [ ] `GetSurfacePoint()` returns full pick information
- [ ] All unit tests pass

## Verification Commands

```bash
cd /Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/rhino_plugin
dotnet build
dotnet test --filter "FullyQualifiedName~SurfaceConstrainedGetPointTests|FullyQualifiedName~SurfacePickResultTests"
```

## Do Not Modify

- Files in `Geometry/` (Phase 3 domain)
- Files in `Interop/` (Phase 3 domain)
- Files in `Display/` (Phase 4 domain)
- `VertexDragHandler.cs` (Agent 5B's domain)
- `RegionPicker.cs` (Agent 5C's domain)

## Skills to Use

- `superpowers:test-driven-development` - write tests first
- `superpowers:verification-before-completion` - run tests before reporting

## Notes

- `GetPoint.Constrain(SubD, false)` is the key for surface-locking
- `OnMouseMove` is called continuously during picking
- `DynamicDraw` event allows custom drawing during interaction
- Parametric coordinates are essential for the rest of the system
- Projection uses the C++ Newton-Raphson implementation via P/Invoke

## Report

When complete, provide:
1. Test output showing all tests pass
2. Build output showing no errors
3. Notes on projection accuracy
4. Any edge cases for face boundaries
