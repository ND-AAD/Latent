# Agent 0B: Project Structure Setup

## Objective

Create directory structure and placeholder files for the Rhino plugin and Python analysis service.

## Working Directory

`/Users/NickDuch/.claude-worktrees/Latent/focused-robinson`

## Read First

- `CLAUDE.md` - project principles
- `docs/plans/2025-12-04-rhino-plugin-architecture-design.md` - architecture overview

## Files to Create

### Rhino Plugin Structure

```
rhino_plugin/
├── LatentPlugin.csproj
├── Properties/
│   └── AssemblyInfo.cs
├── Interop/
│   └── .gitkeep
├── Commands/
│   └── .gitkeep
├── Display/
│   └── .gitkeep
├── Geometry/
│   └── .gitkeep
├── Analysis/
│   └── .gitkeep
├── UI/
│   └── .gitkeep
├── Interaction/
│   └── .gitkeep
└── Tests/
    └── .gitkeep
```

### Analysis Service Structure

```
analysis_service/
├── __init__.py
├── __main__.py
├── requirements.txt
└── .gitkeep
```

## Tasks

### 1. Create Rhino Plugin .csproj

```xml
<!-- rhino_plugin/LatentPlugin.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net48</TargetFramework>
    <RootNamespace>Latent</RootNamespace>
    <AssemblyName>LatentPlugin</AssemblyName>
    <OutputType>Library</OutputType>
    <LangVersion>latest</LangVersion>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="RhinoCommon" Version="8.0.23304.9001" />
    <PackageReference Include="Eto.Forms" Version="2.8.0" />
  </ItemGroup>

  <ItemGroup>
    <Reference Include="Eto">
      <HintPath>$(RhinoSystemDir)\Eto.dll</HintPath>
      <Private>False</Private>
    </Reference>
    <Reference Include="Rhino.UI">
      <HintPath>$(RhinoSystemDir)\Rhino.UI.dll</HintPath>
      <Private>False</Private>
    </Reference>
  </ItemGroup>
</Project>
```

### 2. Create AssemblyInfo.cs

```csharp
// rhino_plugin/Properties/AssemblyInfo.cs
using System.Runtime.InteropServices;
using Rhino.PlugIns;

[assembly: PlugInDescription(DescriptionType.Organization, "Latent")]
[assembly: PlugInDescription(DescriptionType.Email, "")]
[assembly: PlugInDescription(DescriptionType.Phone, "")]
[assembly: PlugInDescription(DescriptionType.Address, "")]
[assembly: PlugInDescription(DescriptionType.Country, "")]
[assembly: PlugInDescription(DescriptionType.WebSite, "")]
[assembly: PlugInDescription(DescriptionType.UpdateUrl, "")]

[assembly: Guid("F1A2B3C4-D5E6-7890-ABCD-EF1234567890")]
```

### 3. Create Analysis Service Files

```python
# analysis_service/__init__.py
"""
Latent Analysis Service

JSON-RPC server providing lens analysis for the Rhino plugin.
Runs as a subprocess, communicates via HTTP on port 5555.
"""

__version__ = "0.1.0"
```

```python
# analysis_service/__main__.py
"""
Entry point for running the analysis service.

Usage: python -m analysis_service
"""

import logging

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.info("Analysis service starting...")

    # Server implementation will be added in Phase 2
    logger.info("Service ready (placeholder)")

if __name__ == "__main__":
    main()
```

```text
# analysis_service/requirements.txt
numpy>=1.21.0
scipy>=1.7.0
```

### 4. Create Directory Structure

Use mkdir and touch commands to create all directories with .gitkeep files.

## Success Criteria

- [ ] All directories exist as specified
- [ ] `rhino_plugin/LatentPlugin.csproj` is valid XML (no syntax errors)
- [ ] `python3 -c "import analysis_service"` succeeds without errors
- [ ] `python3 -m analysis_service` runs and prints startup message

## Verification Commands

```bash
# Verify directories exist
test -d rhino_plugin/Interop && echo "✓ Interop"
test -d rhino_plugin/Commands && echo "✓ Commands"
test -d rhino_plugin/Display && echo "✓ Display"
test -d rhino_plugin/Geometry && echo "✓ Geometry"
test -d rhino_plugin/Analysis && echo "✓ Analysis"
test -d rhino_plugin/UI && echo "✓ UI"
test -d rhino_plugin/Interaction && echo "✓ Interaction"
test -d rhino_plugin/Tests && echo "✓ Tests"
test -d analysis_service && echo "✓ analysis_service"

# Verify Python package
python3 -c "import analysis_service; print(analysis_service.__version__)"

# Verify csproj is valid XML
python3 -c "import xml.etree.ElementTree as ET; ET.parse('rhino_plugin/LatentPlugin.csproj'); print('✓ Valid XML')"
```

## Do Not Modify

- Any files in `cpp_core/` (Agent 0A's domain)
- Any files in `app/` (existing Python application)
- Any files in `docs/`

## Skills to Use

- `superpowers:verification-before-completion` - verify structure before reporting done

## Report

When complete, provide:
1. Directory tree output showing created structure
2. Python import verification result
3. Any issues encountered
