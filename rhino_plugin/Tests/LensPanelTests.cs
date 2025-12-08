// rhino_plugin/Tests/LensPanelTests.cs
using System.Collections.Generic;
using NUnit.Framework;
using Latent.UI;

namespace Latent.Tests
{
    [TestFixture]
    public class LensParameterRegistryTests
    {
        [Test]
        public void GetParameters_Differential_ReturnsCurvatureTolerance()
        {
            var parameters = LensParameterRegistry.GetParameters(LensType.Differential);

            Assert.That(parameters, Has.Count.GreaterThan(0));
            Assert.That(parameters[0].Name, Is.EqualTo("curvature_tolerance"));
        }

        [Test]
        public void GetParameters_Spectral_ReturnsNumEigenfunctions()
        {
            var parameters = LensParameterRegistry.GetParameters(LensType.Spectral);

            Assert.That(parameters, Has.Count.GreaterThan(0));
            Assert.That(parameters[0].Name, Is.EqualTo("num_eigenfunctions"));
        }

        [Test]
        public void CurvatureTolerance_HasValidRange()
        {
            var parameters = LensParameterRegistry.GetParameters(LensType.Differential);
            var param = parameters.Find(p => p.Name == "curvature_tolerance");

            Assert.That(param, Is.Not.Null);
            Assert.That(param!.MinValue, Is.GreaterThan(0));
            Assert.That(param.MaxValue, Is.LessThanOrEqualTo(1.0));
            Assert.That(param.DefaultValue, Is.InRange(param.MinValue, param.MaxValue));
        }

        [Test]
        public void NumEigenfunctions_IsInteger()
        {
            var parameters = LensParameterRegistry.GetParameters(LensType.Spectral);
            var param = parameters.Find(p => p.Name == "num_eigenfunctions");

            Assert.That(param, Is.Not.Null);
            Assert.That(param!.IsInteger, Is.True);
        }

        [Test]
        public void NumEigenfunctions_HasValidRange()
        {
            var parameters = LensParameterRegistry.GetParameters(LensType.Spectral);
            var param = parameters.Find(p => p.Name == "num_eigenfunctions");

            Assert.That(param, Is.Not.Null);
            Assert.That(param!.MinValue, Is.GreaterThanOrEqualTo(1));
            Assert.That(param.MaxValue, Is.GreaterThan(param.MinValue));
            Assert.That(param.DefaultValue, Is.InRange(param.MinValue, param.MaxValue));
        }
    }

    [TestFixture]
    public class LensParameterTests
    {
        [Test]
        public void LensParameter_DefaultValues()
        {
            var param = new LensParameter();

            Assert.That(param.Name, Is.EqualTo(""));
            Assert.That(param.Step, Is.EqualTo(0.1));
            Assert.That(param.IsInteger, Is.False);
        }

        [Test]
        public void LensParameter_CanSetAllProperties()
        {
            var param = new LensParameter
            {
                Name = "test_param",
                DisplayName = "Test Parameter",
                Description = "A test parameter",
                DefaultValue = 5.0,
                MinValue = 0.0,
                MaxValue = 10.0,
                Step = 0.5,
                IsInteger = false
            };

            Assert.That(param.Name, Is.EqualTo("test_param"));
            Assert.That(param.DisplayName, Is.EqualTo("Test Parameter"));
            Assert.That(param.Description, Is.EqualTo("A test parameter"));
            Assert.That(param.DefaultValue, Is.EqualTo(5.0));
            Assert.That(param.MinValue, Is.EqualTo(0.0));
            Assert.That(param.MaxValue, Is.EqualTo(10.0));
            Assert.That(param.Step, Is.EqualTo(0.5));
        }
    }

    [TestFixture]
    public class LensTypeTests
    {
        [Test]
        public void LensType_HasExpectedValues()
        {
            Assert.That(LensType.Differential, Is.EqualTo((LensType)0));
            Assert.That(LensType.Spectral, Is.EqualTo((LensType)1));
        }

        [Test]
        public void AllLensTypes_HaveParameters()
        {
            foreach (LensType lens in System.Enum.GetValues(typeof(LensType)))
            {
                var parameters = LensParameterRegistry.GetParameters(lens);
                Assert.That(parameters, Is.Not.Null,
                    $"LensType.{lens} should have parameters defined");
            }
        }

        [Test]
        public void AllParameters_HaveValidDefaults()
        {
            foreach (LensType lens in System.Enum.GetValues(typeof(LensType)))
            {
                var parameters = LensParameterRegistry.GetParameters(lens);
                foreach (var param in parameters)
                {
                    Assert.That(param.DefaultValue, Is.InRange(param.MinValue, param.MaxValue),
                        $"{lens}.{param.Name} default value out of range");
                }
            }
        }
    }
}
