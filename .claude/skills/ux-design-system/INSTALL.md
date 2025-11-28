# Installing the UX Design System Skill

## Installation Methods

### Method 1: Local Project Installation

1. **Create a skills directory in your project** (if it doesn't exist):
```bash
mkdir -p your-project/.claude/skills/
```

2. **Copy the skill directory**:
```bash
cp -r ux-design-system/ your-project/.claude/skills/
```

3. **Verify installation**:
```bash
ls -la your-project/.claude/skills/ux-design-system/
# Should show SKILL.md and subdirectories
```

### Method 2: Global Installation

1. **Create global Claude skills directory**:
```bash
mkdir -p ~/.claude/skills/
```

2. **Move the skill to global location**:
```bash
cp -r ux-design-system/ ~/.claude/skills/
```

3. **The skill will be available to all projects**

### Method 3: Package and Install

1. **Package the skill** (from the skill directory):
```bash
cd ux-design-system/
python package_skill.py
# This creates ux-design-system.skill file
```

2. **Install the packaged skill**:
```bash
# Copy to your project's skills directory
cp ux-design-system.skill your-project/.claude/skills/
```

## Activating the Skill

### Automatic Activation

The skill automatically activates when Claude detects relevant tasks based on the description in the frontmatter:

```yaml
description: "Systematic UX design and evaluation framework for creating
  human-centered, accessible, and coherent digital interfaces. Activates when:
  (1) Designing new user interfaces or experiences,
  (2) Evaluating existing designs for usability issues,
  (3) Creating design systems or component libraries..."
```

Claude will load this skill when you ask about:
- "Help me design a dashboard"
- "Review this interface for accessibility"
- "Create a component library"
- "Evaluate the UX of this page"
- "Build a responsive layout"

### Manual Activation

You can explicitly request the skill:
```
"Use the ux-design-system skill to help me design a mobile app"
```

### Project Configuration (Optional)

You can add skill preferences to your project's Claude configuration:

**your-project/.claude/config.yaml** (create if doesn't exist):
```yaml
skills:
  enabled:
    - ux-design-system
  auto_load:
    - ux-design-system  # Always load for this project
```

## Verifying Installation

### Check if skill is recognized:
1. Ask Claude: "What UX skills do you have available?"
2. Or: "List available design skills"

### Test the skill:
```
"Using UX best practices, help me create a login form"
```

Claude should respond using the systematic framework from the skill.

## Using the Skill Effectively

### Trigger Examples

**For Design Tasks:**
- "Design a user-friendly checkout flow"
- "Create wireframes for a mobile app"
- "Build a design system for my startup"

**For Evaluation:**
- "Evaluate this interface using Nielsen's heuristics"
- "Check if this design meets WCAG standards"
- "Review the information architecture of this site"

**For Implementation:**
- "Generate an accessible React component"
- "Create a responsive grid layout"
- "Build a component with proper ARIA labels"

### Accessing Scripts

When the skill is loaded, you can use its scripts:
```
"Run the heuristic evaluation script on my interface"
"Check color contrast between #333333 and #ffffff"
"Generate a Button component with accessibility"
```

### Using References

The skill uses progressive disclosure. When you need detailed information:
```
"Explain Gestalt principles for this design"
"Show me WCAG guidelines for forms"
"What are the information architecture best practices?"
```

## Troubleshooting

### Skill Not Loading?

1. **Check installation path**:
```bash
# For project-specific
ls -la .claude/skills/ux-design-system/SKILL.md

# For global
ls -la ~/.claude/skills/ux-design-system/SKILL.md
```

2. **Validate skill structure**:
```bash
cd ux-design-system/
python validate_skill.py
```

3. **Check frontmatter**:
```bash
head -20 ux-design-system/SKILL.md
# Should show proper YAML frontmatter
```

### Skill Not Triggering?

- Use more specific UX/design keywords
- Explicitly mention "design", "UX", "interface", or "accessibility"
- Reference specific methodologies: "Nielsen heuristics", "WCAG", "atomic design"

## Integration with Claude Agents

When working with Claude agents in your codebase:

1. **The skill enhances Claude's capabilities** automatically when relevant
2. **No need to modify system prompts** - the skill description handles triggering
3. **Skills are additive** - they don't override Claude's base knowledge

## Best Practices

1. **Keep skills organized**: One skill per directory
2. **Update regularly**: Pull latest versions of skills
3. **Test after installation**: Verify skill loads and works
4. **Use progressive disclosure**: Start with general requests, get specific as needed
5. **Leverage bundled tools**: Use the scripts and templates included

## Support

If you encounter issues:
1. Run `validate_skill.py` to check structure
2. Ensure SKILL.md has proper frontmatter
3. Check that all referenced files exist
4. Verify permissions on script files

The skill is now ready to transform Claude into a UX design expert!