---
name: ux-design-system
description: "Systematic UX design and evaluation framework for creating human-centered, accessible, and coherent digital interfaces. Activates when: (1) Designing new user interfaces or experiences, (2) Evaluating existing designs for usability issues, (3) Creating design systems or component libraries, (4) Solving UX/UI problems or improving user flows, (5) Implementing accessibility standards, (6) Applying visual hierarchy and information architecture, (7) Conducting design reviews or heuristic evaluations, (8) Creating wireframes, prototypes, or design specifications, (9) Optimizing cognitive load and user comprehension, (10) Building responsive and mobile-first designs"
---

# UX Design System Framework

## Core Design Process

### 1. Discovery & Definition
Understand the problem space before designing solutions:
```
1. Define user needs and goals
2. Identify constraints (technical, business, user)
3. Map user journeys and task flows
4. Establish success metrics (HEART framework)
5. Create problem statements
```

### 2. Design Principles Application

Apply these fundamental principles to every design decision:

**Visual Hierarchy**
- Size: Larger elements for importance
- Color: Strategic contrast to guide attention
- Position: Top-left for primary content (Western)
- Spacing: White space creates emphasis
- Typography: Clear heading structure

**Cognitive Load Management**
- Chunk information (7±2 items max)
- Progressive disclosure for complexity
- Recognition over recall
- Consistent patterns reduce learning
- Clear conceptual models

**Interaction Design**
- Touch targets: 48px minimum (44px iOS)
- Fitts's Law: Larger, closer targets
- Hick's Law: Minimize choices
- Immediate feedback for all actions
- Reversible actions (undo capability)

### 3. Component-Based Architecture

Build interfaces using atomic design hierarchy:

```
Atoms → Molecules → Organisms → Templates → Pages

Example:
- Atom: Button, Input, Label
- Molecule: Search form (input + button)
- Organism: Header (logo + nav + search)
- Template: Page layout structure
- Page: Specific instance with content
```

Use design tokens for consistency:
```css
/* Primitive tokens */
--color-blue-500: #3b82f6;
--spacing-4: 16px;

/* Semantic tokens */
--color-primary: var(--color-blue-500);
--spacing-section: var(--spacing-4);

/* Component tokens */
--button-bg-primary: var(--color-primary);
--card-padding: var(--spacing-section);
```

### 4. Evaluation Framework

#### Nielsen's 10 Heuristics Checklist
Run `scripts/heuristic_evaluation.py` to systematically evaluate:
1. Visibility of system status
2. Match between system and real world
3. User control and freedom
4. Consistency and standards
5. Error prevention
6. Recognition rather than recall
7. Flexibility and efficiency
8. Aesthetic and minimalist design
9. Error recovery
10. Help and documentation

#### WCAG Accessibility (Level AA)
Run `scripts/accessibility_check.py` to verify:
- Color contrast (4.5:1 minimum)
- Keyboard navigation
- Screen reader compatibility
- Focus indicators
- Alternative text
- Semantic HTML

### 5. Design System Implementation

#### Component Structure
```
ComponentName/
├── ComponentName.jsx     # React/Vue/etc
├── ComponentName.css      # Styles
├── ComponentName.test.js  # Tests
├── ComponentName.docs.md  # Documentation
└── ComponentName.stories.js # Storybook
```

#### Responsive Patterns
Apply mobile-first approach:
1. Design for smallest screen first
2. Enhance progressively for larger screens
3. Use fluid grids: target ÷ context = result
4. Implement common patterns:
   - Mostly Fluid
   - Column Drop
   - Layout Shifter
   - Off Canvas

### 6. Error Prevention & Recovery

**Prevention Strategies**
- Inline validation (onBlur, not while typing)
- Clear constraints and limits
- Confirmation for destructive actions
- Disabled states with explanations
- Smart defaults

**Error Message Format**
```
[What went wrong] + [Why] + [How to fix]
Example: "Email format invalid. Please include @ symbol.
Format: name@example.com"
```

## Design Workflow

### For New Interfaces
1. **Understand**: Review requirements and user research
2. **Ideate**: Sketch multiple solutions (see `references/ideation_methods.md`)
3. **Prototype**: Create low-fidelity wireframes
4. **Test**: Validate with heuristic evaluation
5. **Refine**: Apply visual design and polish
6. **Implement**: Build with component system
7. **Measure**: Track success metrics

### For Design Reviews
1. Run `scripts/design_audit.py` for systematic evaluation
2. Check against `references/design_principles.md`
3. Verify accessibility compliance
4. Test responsive behavior
5. Document findings with severity ratings
6. Prioritize fixes by impact

### For Component Creation
1. Check existing components first
2. Design all states (default, hover, active, disabled, error)
3. Create design tokens for theming
4. Build with accessibility defaults
5. Document usage patterns
6. Add to component library

## Quick Reference

### Color Usage
- **Primary**: Main actions, brand
- **Secondary**: Supporting elements
- **Success**: Positive feedback (#10b981)
- **Warning**: Caution states (#f59e0b)
- **Error**: Problems, destructive (#ef4444)
- **Neutral**: Text, backgrounds (grays)

### Spacing Scale
```
--spacing-1: 4px   (tight)
--spacing-2: 8px   (compact)
--spacing-3: 12px  (default)
--spacing-4: 16px  (comfortable)
--spacing-6: 24px  (relaxed)
--spacing-8: 32px  (spacious)
--spacing-12: 48px (generous)
```

### Typography Scale
```
--text-xs: 12px/16px
--text-sm: 14px/20px
--text-base: 16px/24px
--text-lg: 18px/28px
--text-xl: 20px/28px
--text-2xl: 24px/32px
--text-3xl: 30px/36px
```

## Advanced Topics

For detailed guidance, see references:
- `references/gestalt_principles.md` - Perception and visual design
- `references/information_architecture.md` - Content organization
- `references/design_systems.md` - Building scalable systems
- `references/accessibility_guidelines.md` - WCAG compliance
- `references/usability_testing.md` - User research methods

## Scripts & Tools

**Analysis Scripts**
- `scripts/heuristic_evaluation.py` - Systematic usability review
- `scripts/accessibility_check.py` - WCAG compliance validation
- `scripts/design_audit.py` - Comprehensive design assessment
- `scripts/contrast_checker.py` - Color contrast validation

**Generation Scripts**
- `scripts/generate_component.py` - Component boilerplate
- `scripts/create_tokens.py` - Design token generation
- `scripts/build_styleguide.py` - Documentation builder

## Assets & Templates

- `assets/wireframe_kit.svg` - Low-fidelity components
- `assets/grid_templates.css` - Responsive grid systems
- `assets/component_template.jsx` - React component starter
- `assets/design_brief_template.md` - Project documentation

## Key Reminders

1. **Users don't read, they scan** - Use clear visual hierarchy
2. **Consistency reduces cognitive load** - Follow established patterns
3. **Accessibility is not optional** - Design for all users
4. **Performance impacts UX** - Optimize for speed
5. **Mobile-first prevents problems** - Start with constraints
6. **Test early and often** - Validate assumptions
7. **Document decisions** - Future you will thank you

When designing, always ask:
- Is it learnable?
- Is it efficient?
- Is it memorable?
- Does it prevent errors?
- Is it delightful?