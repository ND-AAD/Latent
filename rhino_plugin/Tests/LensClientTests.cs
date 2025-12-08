// rhino_plugin/Tests/LensClientTests.cs
using System.Collections.Generic;
using System.Threading.Tasks;
using NUnit.Framework;
using Rhino.Geometry;
using Latent.Analysis;

namespace Latent.Tests
{
    [TestFixture]
    public class LensClientTests
    {
        private ServiceManager _serviceManager;
        private LensClient _client;

        [OneTimeSetUp]
        public async Task SetUp()
        {
            // Start analysis service for tests
            try
            {
                _serviceManager = new ServiceManager();
                await _serviceManager.StartAsync();
                _client = new LensClient(serviceManager: _serviceManager);
            }
            catch
            {
                // Service may not be available in CI
            }
        }

        [OneTimeTearDown]
        public void TearDown()
        {
            _client?.Dispose();
            _serviceManager?.Dispose();
        }

        [Test]
        public async Task Ping_ReturnsOk()
        {
            if (_client == null)
            {
                Assert.Ignore("Analysis service not available");
            }

            var result = await _client.PingAsync();
            Assert.IsTrue(result);
        }

        [Test]
        public async Task Initialize_Succeeds()
        {
            if (_client == null)
            {
                Assert.Ignore("Analysis service not available");
            }

            // Create a simple SubD
            var box = new Box(
                Plane.WorldXY,
                new Interval(-1, 1),
                new Interval(-1, 1),
                new Interval(-1, 1)
            );
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            var subd = SubD.CreateFromMesh(mesh);

            await _client.InitializeAsync(subd);
            // No exception = success
        }

        [Test]
        public async Task AnalyzeDifferential_ReturnsResult()
        {
            if (_client == null)
            {
                Assert.Ignore("Analysis service not available");
            }

            // Initialize first
            var box = new Box(
                Plane.WorldXY,
                new Interval(-1, 1),
                new Interval(-1, 1),
                new Interval(-1, 1)
            );
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            var subd = SubD.CreateFromMesh(mesh);
            await _client.InitializeAsync(subd);

            // Run analysis
            var result = await _client.AnalyzeDifferentialAsync(0.3);

            Assert.IsNotNull(result);
            // Result may be empty if lens not fully implemented yet
        }

        [Test]
        public void ControlCage_ExtractsCorrectly()
        {
            var box = new Box(
                Plane.WorldXY,
                new Interval(-1, 1),
                new Interval(-1, 1),
                new Interval(-1, 1)
            );
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            var subd = SubD.CreateFromMesh(mesh);

            // Use reflection to test private method
            var method = typeof(LensClient).GetMethod(
                "ExtractControlCage",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static
            );

            var cage = (ControlCage)method.Invoke(null, new object[] { subd });

            Assert.AreEqual(8, cage.Vertices.Count); // Box has 8 vertices
            Assert.AreEqual(6, cage.Faces.Count);    // Box has 6 faces
        }
    }
}
