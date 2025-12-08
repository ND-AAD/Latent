// rhino_plugin/Geometry/IGeometryElement.cs
namespace Latent.Geometry
{
    /// <summary>
    /// Common interface for geometry elements (vertices, edges, regions).
    /// </summary>
    public interface IGeometryElement
    {
        /// <summary>
        /// Unique identifier.
        /// </summary>
        string Id { get; }

        /// <summary>
        /// Whether this element is pinned (protected from changes).
        /// </summary>
        bool IsPinned { get; set; }

        /// <summary>
        /// Whether this element is at its implicit (lens-defined) state.
        /// </summary>
        bool IsImplicit { get; }

        /// <summary>
        /// Whether this element is currently selected.
        /// </summary>
        bool IsSelected { get; set; }

        /// <summary>
        /// Whether this element can be reverted to implicit state.
        /// </summary>
        bool CanRevert { get; }
    }
}
