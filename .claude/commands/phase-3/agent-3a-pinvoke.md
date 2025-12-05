# Agent 3A: P/Invoke Bindings

## Objective

Create C# managed wrappers for the C bindings, enabling the Rhino plugin to call the C++ core.

## Working Directory

`/Users/NickDuch/.claude-worktrees/Latent/focused-robinson`

## Read First

- `cpp_core/c_bindings/latent_core.h` - C API for evaluator
- `cpp_core/c_bindings/latent_curves.h` - C API for curves
- `cpp_core/c_bindings/latent_analysis.h` - C API for curvature
- `docs/plans/2025-12-04-rhino-plugin-implementation-plan.md` - P/Invoke patterns

## Files to Create

1. `rhino_plugin/Interop/NativeCore.cs` - P/Invoke declarations
2. `rhino_plugin/Interop/SubDEvaluator.cs` - Managed wrapper for evaluator
3. `rhino_plugin/Interop/SurfaceCurve.cs` - Managed wrapper for curves
4. `rhino_plugin/Interop/CurvatureAnalyzer.cs` - Managed wrapper for analysis
5. `rhino_plugin/Tests/InteropTests.cs` - Unit tests

## Tasks

### 1. Create NativeCore.cs

```csharp
// rhino_plugin/Interop/NativeCore.cs
using System;
using System.Runtime.InteropServices;

namespace Latent.Interop
{
    /// <summary>
    /// P/Invoke declarations for the latent_core native library.
    /// </summary>
    public static class NativeCore
    {
        private const string DllName = "latent_core";

        #region Evaluator Lifecycle

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr latent_evaluator_create();

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern void latent_evaluator_destroy(IntPtr handle);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_evaluator_initialize(
            IntPtr handle,
            [MarshalAs(UnmanagedType.LPArray)] float[] vertices, int vertexCount,
            [MarshalAs(UnmanagedType.LPArray)] int[] faces,
            [MarshalAs(UnmanagedType.LPArray)] int[] faceSizes, int faceCount,
            [MarshalAs(UnmanagedType.LPArray)] int[] creaseEdges,
            [MarshalAs(UnmanagedType.LPArray)] float[] creaseSharpness, int creaseCount);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_evaluator_is_initialized(IntPtr handle);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int latent_evaluator_get_face_count(IntPtr handle);

        #endregion

        #region Forward Evaluation

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_evaluate_point(
            IntPtr handle,
            int faceId, float u, float v,
            out float x, out float y, out float z);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_evaluate_normal(
            IntPtr handle,
            int faceId, float u, float v,
            out float nx, out float ny, out float nz);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_evaluate_full(
            IntPtr handle,
            int faceId, float u, float v,
            [MarshalAs(UnmanagedType.LPArray, SizeConst = 3)] float[] point,
            [MarshalAs(UnmanagedType.LPArray, SizeConst = 3)] float[] normal,
            [MarshalAs(UnmanagedType.LPArray, SizeConst = 3)] float[] du,
            [MarshalAs(UnmanagedType.LPArray, SizeConst = 3)] float[] dv);

        #endregion

        #region Inverse Evaluation

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_project_point(
            IntPtr handle,
            float px, float py, float pz,
            out int faceId, out float u, out float v);

        #endregion

        #region Curves

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr latent_curve_create(
            [MarshalAs(UnmanagedType.LPArray)] int[] faceIds,
            [MarshalAs(UnmanagedType.LPArray)] float[] us,
            [MarshalAs(UnmanagedType.LPArray)] float[] vs,
            int pointCount,
            int curveType,
            int degree);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern void latent_curve_destroy(IntPtr handle);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_curve_evaluate(
            IntPtr curveHandle,
            IntPtr evaluatorHandle,
            float t,
            out float x, out float y, out float z);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_curve_evaluate_parametric(
            IntPtr handle,
            float t,
            out int faceId, out float u, out float v);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_curve_sample(
            IntPtr curveHandle,
            IntPtr evaluatorHandle,
            int numSamples,
            [MarshalAs(UnmanagedType.LPArray)] float[] outPoints);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int latent_curve_get_point_count(IntPtr handle);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int latent_curve_get_type(IntPtr handle);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int latent_curve_get_degree(IntPtr handle);

        #endregion

        #region Curvature

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_compute_curvature(
            IntPtr handle,
            int faceId, float u, float v,
            out float k1, out float k2, out float H, out float K);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_compute_curvature_directions(
            IntPtr handle,
            int faceId, float u, float v,
            [MarshalAs(UnmanagedType.LPArray, SizeConst = 3)] float[] dir1,
            [MarshalAs(UnmanagedType.LPArray, SizeConst = 3)] float[] dir2);

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool latent_sample_curvature_grid(
            IntPtr handle,
            int faceId,
            int resolution,
            [MarshalAs(UnmanagedType.LPArray)] float[] outH,
            [MarshalAs(UnmanagedType.LPArray)] float[] outK);

        #endregion

        #region Error Handling

        [DllImport(DllName, CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr latent_get_last_error();

        public static string GetLastError()
        {
            IntPtr ptr = latent_get_last_error();
            return Marshal.PtrToStringAnsi(ptr) ?? "";
        }

        #endregion
    }

    /// <summary>
    /// Curve type enum matching C++ LATENT_CURVE_* constants.
    /// </summary>
    public enum CurveType
    {
        Linear = 0,
        Bezier = 1,
        BSpline = 2
    }
}
```

### 2. Create SubDEvaluator.cs

```csharp
// rhino_plugin/Interop/SubDEvaluator.cs
using System;
using System.Collections.Generic;
using Rhino.Geometry;

namespace Latent.Interop
{
    /// <summary>
    /// Parametric point on the SubD limit surface.
    /// </summary>
    public struct ParametricPoint
    {
        public int FaceId;
        public double U;
        public double V;

        public ParametricPoint(int faceId, double u, double v)
        {
            FaceId = faceId;
            U = u;
            V = v;
        }

        public bool IsValid => FaceId >= 0;
    }

    /// <summary>
    /// Managed wrapper for the native SubD evaluator.
    /// </summary>
    public class SubDEvaluator : IDisposable
    {
        private IntPtr _handle;
        private bool _disposed;

        public SubDEvaluator()
        {
            _handle = NativeCore.latent_evaluator_create();
            if (_handle == IntPtr.Zero)
            {
                throw new InvalidOperationException("Failed to create evaluator");
            }
        }

        public bool IsInitialized => NativeCore.latent_evaluator_is_initialized(_handle);
        public int FaceCount => NativeCore.latent_evaluator_get_face_count(_handle);

        /// <summary>
        /// Initialize the evaluator with a Rhino SubD.
        /// </summary>
        public void Initialize(SubD subd)
        {
            var (vertices, faces, faceSizes, creaseEdges, creaseSharpness) = ExtractCage(subd);

            bool success = NativeCore.latent_evaluator_initialize(
                _handle,
                vertices, vertices.Length / 3,
                faces, faceSizes, faceSizes.Length,
                creaseEdges, creaseSharpness, creaseEdges?.Length / 2 ?? 0
            );

            if (!success)
            {
                throw new InvalidOperationException(
                    $"Failed to initialize evaluator: {NativeCore.GetLastError()}"
                );
            }
        }

        /// <summary>
        /// Evaluate a point on the limit surface.
        /// </summary>
        public Point3d EvaluatePoint(int faceId, double u, double v)
        {
            if (!NativeCore.latent_evaluate_point(
                    _handle, faceId, (float)u, (float)v,
                    out float x, out float y, out float z))
            {
                throw new InvalidOperationException(
                    $"Evaluation failed: {NativeCore.GetLastError()}"
                );
            }
            return new Point3d(x, y, z);
        }

        /// <summary>
        /// Evaluate the normal at a point on the limit surface.
        /// </summary>
        public Vector3d EvaluateNormal(int faceId, double u, double v)
        {
            if (!NativeCore.latent_evaluate_normal(
                    _handle, faceId, (float)u, (float)v,
                    out float nx, out float ny, out float nz))
            {
                throw new InvalidOperationException(
                    $"Normal evaluation failed: {NativeCore.GetLastError()}"
                );
            }
            return new Vector3d(nx, ny, nz);
        }

        /// <summary>
        /// Project a 3D point onto the limit surface.
        /// </summary>
        public ParametricPoint ProjectPoint(Point3d point)
        {
            if (!NativeCore.latent_project_point(
                    _handle,
                    (float)point.X, (float)point.Y, (float)point.Z,
                    out int faceId, out float u, out float v))
            {
                return new ParametricPoint(-1, 0, 0);
            }
            return new ParametricPoint(faceId, u, v);
        }

        /// <summary>
        /// Extract control cage from Rhino SubD.
        /// </summary>
        private static (float[] vertices, int[] faces, int[] faceSizes,
                        int[] creaseEdges, float[] creaseSharpness) ExtractCage(SubD subd)
        {
            // Extract vertices
            var vertices = new List<float>();
            var vertexMap = new Dictionary<uint, int>();

            int idx = 0;
            foreach (var v in subd.Vertices)
            {
                vertices.Add((float)v.ControlNetPoint.X);
                vertices.Add((float)v.ControlNetPoint.Y);
                vertices.Add((float)v.ControlNetPoint.Z);
                vertexMap[v.Id] = idx++;
            }

            // Extract faces
            var faces = new List<int>();
            var faceSizes = new List<int>();

            foreach (var f in subd.Faces)
            {
                var corners = f.VertexIds;
                faceSizes.Add(corners.Length);
                foreach (var vid in corners)
                {
                    faces.Add(vertexMap[vid]);
                }
            }

            // Extract creases
            var creaseEdges = new List<int>();
            var creaseSharpness = new List<float>();

            foreach (var e in subd.Edges)
            {
                if (e.IsCrease)
                {
                    creaseEdges.Add(vertexMap[e.Vertex(0).Id]);
                    creaseEdges.Add(vertexMap[e.Vertex(1).Id]);
                    creaseSharpness.Add((float)e.CreaseWeight);
                }
            }

            return (
                vertices.ToArray(),
                faces.ToArray(),
                faceSizes.ToArray(),
                creaseEdges.Count > 0 ? creaseEdges.ToArray() : null,
                creaseSharpness.Count > 0 ? creaseSharpness.ToArray() : null
            );
        }

        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        protected virtual void Dispose(bool disposing)
        {
            if (!_disposed)
            {
                if (_handle != IntPtr.Zero)
                {
                    NativeCore.latent_evaluator_destroy(_handle);
                    _handle = IntPtr.Zero;
                }
                _disposed = true;
            }
        }

        ~SubDEvaluator()
        {
            Dispose(false);
        }

        internal IntPtr Handle => _handle;
    }
}
```

### 3. Create SurfaceCurve.cs

```csharp
// rhino_plugin/Interop/SurfaceCurve.cs
using System;
using System.Collections.Generic;
using Rhino.Geometry;

namespace Latent.Interop
{
    /// <summary>
    /// Managed wrapper for a curve on the SubD limit surface.
    /// </summary>
    public class SurfaceCurve : IDisposable
    {
        private IntPtr _handle;
        private bool _disposed;
        private readonly List<ParametricPoint> _controlPoints;
        private readonly CurveType _type;
        private readonly int _degree;

        public SurfaceCurve(
            List<ParametricPoint> controlPoints,
            CurveType type = CurveType.Bezier,
            int degree = 3)
        {
            _controlPoints = controlPoints;
            _type = type;
            _degree = degree;

            // Convert to native arrays
            var faceIds = new int[controlPoints.Count];
            var us = new float[controlPoints.Count];
            var vs = new float[controlPoints.Count];

            for (int i = 0; i < controlPoints.Count; i++)
            {
                faceIds[i] = controlPoints[i].FaceId;
                us[i] = (float)controlPoints[i].U;
                vs[i] = (float)controlPoints[i].V;
            }

            _handle = NativeCore.latent_curve_create(
                faceIds, us, vs, controlPoints.Count,
                (int)type, degree
            );

            if (_handle == IntPtr.Zero)
            {
                throw new InvalidOperationException("Failed to create surface curve");
            }
        }

        public IReadOnlyList<ParametricPoint> ControlPoints => _controlPoints;
        public CurveType Type => _type;
        public int Degree => _degree;
        public int PointCount => NativeCore.latent_curve_get_point_count(_handle);

        /// <summary>
        /// Evaluate the curve at parameter t.
        /// </summary>
        public Point3d Evaluate(double t, SubDEvaluator evaluator)
        {
            if (!NativeCore.latent_curve_evaluate(
                    _handle, evaluator.Handle, (float)t,
                    out float x, out float y, out float z))
            {
                throw new InvalidOperationException("Curve evaluation failed");
            }
            return new Point3d(x, y, z);
        }

        /// <summary>
        /// Evaluate the parametric position at parameter t.
        /// </summary>
        public ParametricPoint EvaluateParametric(double t)
        {
            if (!NativeCore.latent_curve_evaluate_parametric(
                    _handle, (float)t,
                    out int faceId, out float u, out float v))
            {
                return new ParametricPoint(-1, 0, 0);
            }
            return new ParametricPoint(faceId, u, v);
        }

        /// <summary>
        /// Sample the curve for display.
        /// </summary>
        public List<Point3d> Sample(int numSamples, SubDEvaluator evaluator)
        {
            var points = new float[numSamples * 3];

            if (!NativeCore.latent_curve_sample(_handle, evaluator.Handle, numSamples, points))
            {
                throw new InvalidOperationException("Curve sampling failed");
            }

            var result = new List<Point3d>(numSamples);
            for (int i = 0; i < numSamples; i++)
            {
                result.Add(new Point3d(
                    points[i * 3],
                    points[i * 3 + 1],
                    points[i * 3 + 2]
                ));
            }
            return result;
        }

        /// <summary>
        /// Convert sampled curve to a Rhino polyline curve.
        /// </summary>
        public PolylineCurve ToPolylineCurve(int numSamples, SubDEvaluator evaluator)
        {
            var points = Sample(numSamples, evaluator);
            return new PolylineCurve(points);
        }

        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        protected virtual void Dispose(bool disposing)
        {
            if (!_disposed)
            {
                if (_handle != IntPtr.Zero)
                {
                    NativeCore.latent_curve_destroy(_handle);
                    _handle = IntPtr.Zero;
                }
                _disposed = true;
            }
        }

        ~SurfaceCurve()
        {
            Dispose(false);
        }
    }
}
```

### 4. Create CurvatureAnalyzer.cs

```csharp
// rhino_plugin/Interop/CurvatureAnalyzer.cs
using System;
using Rhino.Geometry;

namespace Latent.Interop
{
    /// <summary>
    /// Curvature data at a surface point.
    /// </summary>
    public struct CurvatureData
    {
        public double K1;          // Maximum principal curvature
        public double K2;          // Minimum principal curvature
        public double MeanH;       // Mean curvature (K1 + K2) / 2
        public double GaussianK;   // Gaussian curvature (K1 * K2)
        public Vector3d Dir1;      // Direction of maximum curvature
        public Vector3d Dir2;      // Direction of minimum curvature
    }

    /// <summary>
    /// Managed wrapper for curvature analysis functions.
    /// </summary>
    public class CurvatureAnalyzer
    {
        private readonly SubDEvaluator _evaluator;

        public CurvatureAnalyzer(SubDEvaluator evaluator)
        {
            _evaluator = evaluator ?? throw new ArgumentNullException(nameof(evaluator));
        }

        /// <summary>
        /// Compute curvature at a parametric point.
        /// </summary>
        public CurvatureData ComputeCurvature(int faceId, double u, double v)
        {
            if (!NativeCore.latent_compute_curvature(
                    _evaluator.Handle, faceId, (float)u, (float)v,
                    out float k1, out float k2, out float H, out float K))
            {
                throw new InvalidOperationException("Curvature computation failed");
            }

            return new CurvatureData
            {
                K1 = k1,
                K2 = k2,
                MeanH = H,
                GaussianK = K
            };
        }

        /// <summary>
        /// Compute curvature including principal directions.
        /// </summary>
        public CurvatureData ComputeCurvatureWithDirections(int faceId, double u, double v)
        {
            var data = ComputeCurvature(faceId, u, v);

            var dir1 = new float[3];
            var dir2 = new float[3];

            if (NativeCore.latent_compute_curvature_directions(
                    _evaluator.Handle, faceId, (float)u, (float)v, dir1, dir2))
            {
                data.Dir1 = new Vector3d(dir1[0], dir1[1], dir1[2]);
                data.Dir2 = new Vector3d(dir2[0], dir2[1], dir2[2]);
            }

            return data;
        }

        /// <summary>
        /// Sample curvature across a grid on one face.
        /// </summary>
        public (double[,] MeanH, double[,] GaussianK) SampleCurvatureGrid(
            int faceId, int resolution)
        {
            var outH = new float[resolution * resolution];
            var outK = new float[resolution * resolution];

            if (!NativeCore.latent_sample_curvature_grid(
                    _evaluator.Handle, faceId, resolution, outH, outK))
            {
                throw new InvalidOperationException("Curvature grid sampling failed");
            }

            var meanH = new double[resolution, resolution];
            var gaussianK = new double[resolution, resolution];

            for (int j = 0; j < resolution; j++)
            {
                for (int i = 0; i < resolution; i++)
                {
                    int idx = j * resolution + i;
                    meanH[i, j] = outH[idx];
                    gaussianK[i, j] = outK[idx];
                }
            }

            return (meanH, gaussianK);
        }
    }
}
```

### 5. Create InteropTests.cs

```csharp
// rhino_plugin/Tests/InteropTests.cs
using System;
using System.Collections.Generic;
using NUnit.Framework;
using Rhino.Geometry;
using Latent.Interop;

namespace Latent.Tests
{
    [TestFixture]
    public class InteropTests
    {
        // Note: These tests require the native library to be available.
        // They may be skipped in CI if the library isn't built.

        private static bool NativeLibraryAvailable()
        {
            try
            {
                var handle = NativeCore.latent_evaluator_create();
                if (handle != IntPtr.Zero)
                {
                    NativeCore.latent_evaluator_destroy(handle);
                    return true;
                }
            }
            catch (DllNotFoundException)
            {
            }
            return false;
        }

        [Test]
        public void Evaluator_CreateAndDestroy()
        {
            if (!NativeLibraryAvailable())
            {
                Assert.Ignore("Native library not available");
            }

            using var evaluator = new SubDEvaluator();
            Assert.IsFalse(evaluator.IsInitialized);
        }

        [Test]
        public void Evaluator_Initialize_WithTestSubD()
        {
            if (!NativeLibraryAvailable())
            {
                Assert.Ignore("Native library not available");
            }

            // Create a simple box SubD
            var box = new Box(Plane.WorldXY, new Interval(-1, 1), new Interval(-1, 1), new Interval(-1, 1));
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            var subd = SubD.CreateFromMesh(mesh);

            using var evaluator = new SubDEvaluator();
            evaluator.Initialize(subd);

            Assert.IsTrue(evaluator.IsInitialized);
            Assert.AreEqual(6, evaluator.FaceCount);
        }

        [Test]
        public void Evaluator_EvaluatePoint()
        {
            if (!NativeLibraryAvailable())
            {
                Assert.Ignore("Native library not available");
            }

            var box = new Box(Plane.WorldXY, new Interval(-1, 1), new Interval(-1, 1), new Interval(-1, 1));
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            var subd = SubD.CreateFromMesh(mesh);

            using var evaluator = new SubDEvaluator();
            evaluator.Initialize(subd);

            var point = evaluator.EvaluatePoint(0, 0.5, 0.5);

            Assert.IsFalse(double.IsNaN(point.X));
            Assert.IsFalse(double.IsNaN(point.Y));
            Assert.IsFalse(double.IsNaN(point.Z));
        }

        [Test]
        public void Evaluator_ProjectPoint_RoundTrip()
        {
            if (!NativeLibraryAvailable())
            {
                Assert.Ignore("Native library not available");
            }

            var box = new Box(Plane.WorldXY, new Interval(-1, 1), new Interval(-1, 1), new Interval(-1, 1));
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            var subd = SubD.CreateFromMesh(mesh);

            using var evaluator = new SubDEvaluator();
            evaluator.Initialize(subd);

            // Evaluate a known point
            var point = evaluator.EvaluatePoint(0, 0.5, 0.5);

            // Project it back
            var param = evaluator.ProjectPoint(point);

            Assert.IsTrue(param.IsValid);
            Assert.AreEqual(0, param.FaceId);
            Assert.AreEqual(0.5, param.U, 0.01);
            Assert.AreEqual(0.5, param.V, 0.01);
        }

        [Test]
        public void SurfaceCurve_Sample()
        {
            if (!NativeLibraryAvailable())
            {
                Assert.Ignore("Native library not available");
            }

            var box = new Box(Plane.WorldXY, new Interval(-1, 1), new Interval(-1, 1), new Interval(-1, 1));
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            var subd = SubD.CreateFromMesh(mesh);

            using var evaluator = new SubDEvaluator();
            evaluator.Initialize(subd);

            var controlPoints = new List<ParametricPoint>
            {
                new ParametricPoint(0, 0.0, 0.5),
                new ParametricPoint(0, 1.0, 0.5)
            };

            using var curve = new SurfaceCurve(controlPoints, CurveType.Linear, 1);

            var samples = curve.Sample(10, evaluator);

            Assert.AreEqual(10, samples.Count);
            foreach (var pt in samples)
            {
                Assert.IsFalse(double.IsNaN(pt.X));
            }
        }

        [Test]
        public void CurvatureAnalyzer_ComputeCurvature()
        {
            if (!NativeLibraryAvailable())
            {
                Assert.Ignore("Native library not available");
            }

            var box = new Box(Plane.WorldXY, new Interval(-1, 1), new Interval(-1, 1), new Interval(-1, 1));
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            var subd = SubD.CreateFromMesh(mesh);

            using var evaluator = new SubDEvaluator();
            evaluator.Initialize(subd);

            var analyzer = new CurvatureAnalyzer(evaluator);
            var data = analyzer.ComputeCurvature(0, 0.5, 0.5);

            Assert.IsFalse(double.IsNaN(data.K1));
            Assert.IsFalse(double.IsNaN(data.K2));
            Assert.AreEqual((data.K1 + data.K2) / 2, data.MeanH, 0.001);
            Assert.AreEqual(data.K1 * data.K2, data.GaussianK, 0.001);
        }
    }
}
```

## Success Criteria

- [ ] All P/Invoke signatures match C header declarations
- [ ] Managed wrappers implement IDisposable correctly
- [ ] No memory leaks in create/destroy cycle
- [ ] SubDEvaluator.Initialize works with Rhino SubD
- [ ] Forward evaluation returns valid points
- [ ] Inverse evaluation round-trips accurately
- [ ] SurfaceCurve sampling produces valid points
- [ ] CurvatureAnalyzer returns valid curvature data

## Verification Commands

```bash
cd /Users/NickDuch/.claude-worktrees/Latent/focused-robinson/rhino_plugin

# Build the plugin
dotnet build

# Run tests (if NUnit test adapter is configured)
dotnet test
```

## Do Not Modify

- Files in `cpp_core/` (Phase 1)
- Files in `analysis_service/` (Agent 3B's domain)
- Other files in `rhino_plugin/` (other agents' domains)

## Skills to Use

- `superpowers:verification-before-completion` - verify all P/Invoke calls work

## Notes

**Library loading**: The native library must be in the correct location for P/Invoke to find it:
- Windows: Same directory as the .dll, or in PATH
- macOS: Set DYLD_LIBRARY_PATH or use @rpath

**SubD creation**: Test code uses `SubD.CreateFromMesh` which creates a box-derived SubD. This is not a "true" SubD but is sufficient for testing the P/Invoke layer.

## Report

When complete, provide:
1. Build output showing successful compilation
2. Test results (if tests run)
3. Any P/Invoke marshaling issues encountered
