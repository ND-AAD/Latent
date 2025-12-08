// rhino_plugin/Interaction/SurfaceConstrainedGetPoint.cs
using System;
using Rhino;
using Rhino.Display;
using Rhino.Geometry;
using Rhino.Input;
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
        private ParametricPoint _currentParam;
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
        public System.Drawing.Color NormalArrowColor { get; set; } = System.Drawing.Color.Blue;

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

            // Note: GetPoint.Constrain doesn't support SubD directly in RhinoCommon.
            // Surface constraint is achieved through projection in OnMouseMove.
            // The SubD is stored for reference and potential future use.

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
            e.Display.DrawPoint(_currentPoint3d, PointStyle.RoundControlPoint, 5, System.Drawing.Color.Yellow);

            // Draw normal if enabled
            if (ShowNormal && _currentNormal.IsValid)
            {
                var endPoint = _currentPoint3d + _currentNormal * NormalArrowLength;
                e.Display.DrawArrow(
                    new Line(_currentPoint3d, endPoint),
                    NormalArrowColor,
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
