# Core Design Principles

## Table of Contents
1. [Fundamental Principles](#fundamental-principles)
2. [Visual Design Laws](#visual-design-laws)
3. [Interaction Principles](#interaction-principles)
4. [System Design Principles](#system-design-principles)

## Fundamental Principles

### 1. Human-Centered Design
**Definition**: Design for actual human needs, capabilities, and limitations.
- Observe real behavior, not idealized usage
- Design for how people DO behave, not how they SHOULD
- Consider physical, cognitive, and emotional needs
- Account for diverse abilities and contexts

### 2. Form Follows Function
**Origin**: Bauhaus principle - aesthetics emerge from purpose
- Every element must serve a purpose
- Remove decoration that doesn't enhance function
- Beauty emerges from proper execution
- Material honesty - don't disguise the nature of elements

### 3. Consistency
**Types**:
- **Internal**: Within the product
- **External**: With platform conventions
- **Conceptual**: Mental models remain stable
- **Visual**: Similar elements look similar
- **Behavioral**: Similar actions produce similar results

### 4. Constraints as Catalysts
**Application**: Limitations drive better solutions
- Limited color palette forces hierarchy through other means
- Small screens force prioritization
- Performance constraints demand optimization
- Accessibility requirements improve clarity for all

## Visual Design Laws

### Fitts's Law
**Formula**: MT = a + b × log₂(D/W + 1)
- Movement time increases with distance
- Movement time decreases with target size
- Screen edges are "infinite" targets
- Implications:
  - Make important buttons larger
  - Place frequent actions closer
  - Use screen edges for critical controls
  - Group related actions

### Hick's Law
**Formula**: RT = a + b × log₂(n)
- Decision time increases logarithmically with choices
- Applications:
  - Limit menu items to 7±2
  - Use progressive disclosure
  - Categorize long lists
  - Highlight recommended options
  - Provide smart defaults

### Miller's Law
**Principle**: Working memory holds 7±2 items
- Chunk information into groups
- Use recognition over recall
- Limit simultaneous options
- Build on existing schemas
- Progressive complexity

### Von Restorff Effect
**Principle**: Distinctive items are more memorable
- Use sparingly for emphasis
- One focal point per screen
- Contrast draws attention
- Consistency makes outliers stand out

## Interaction Principles

### Direct Manipulation
**Characteristics**:
- Continuous representation of objects
- Physical actions instead of syntax
- Immediate feedback
- Reversible actions
- Incremental operations

### Affordances & Signifiers
**Affordances**: What actions are possible
**Signifiers**: How to perform actions
- Buttons look pressable (shadows, borders)
- Links look clickable (underline, color)
- Sliders show drag handles
- Text fields show input cursors

### Feedback Loops
**Requirements**:
- Immediate (< 100ms for direct manipulation)
- Appropriate (match action significance)
- Clear (unambiguous meaning)
- Informative (show progress/completion)

### Error Tolerance
**Strategies**:
- Prevention > Recovery > Error messages
- Undo/Redo for all actions
- Confirmation for destructive operations
- Auto-save to prevent data loss
- Forgiving formats (accept variations)

## System Design Principles

### Modularity
**Benefits**:
- Reusability across contexts
- Consistent behavior
- Easier maintenance
- Scalable complexity
- Independent testing

**Implementation**:
- Single responsibility per component
- Clear interfaces between modules
- Loose coupling, high cohesion
- Standardized communication patterns

### Progressive Enhancement
**Layers**:
1. **Content** (HTML): Works without CSS/JS
2. **Presentation** (CSS): Visual enhancement
3. **Behavior** (JS): Interactive enhancement

**Benefits**:
- Universal access
- Resilient to failure
- Performance optimization
- Future-proof

### Separation of Concerns
**Divisions**:
- Structure vs. Presentation vs. Behavior
- Data vs. Logic vs. Interface
- Content vs. Chrome
- Core vs. Enhancement

### Design Tokens
**Hierarchy**:
```
Primitive → Semantic → Component
#0066CC → color.link → button.primary.bg
```

**Benefits**:
- Single source of truth
- Platform agnostic
- Systematic updates
- Brand consistency
- Theme capability

## Application Guidelines

### When Starting a Project
1. Define constraints first
2. Establish design principles
3. Create component inventory
4. Build systematic hierarchy
5. Test with real content

### When Evaluating Designs
1. Check against principles
2. Verify consistency
3. Test accessibility
4. Measure performance
5. Validate assumptions

### When Problem-Solving
1. Identify root cause
2. Consider multiple solutions
3. Test with users
4. Measure impact
5. Document decisions

## Key Takeaways

1. **Principles > Rules**: Understand why, not just what
2. **Systems > Instances**: Build reusable solutions
3. **Users > Aesthetics**: Function drives form
4. **Clarity > Cleverness**: Obvious is better than smart
5. **Consistency > Novelty**: Familiarity reduces friction