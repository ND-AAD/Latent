# Information Architecture Guide

## Table of Contents
1. [Core Components](#core-components)
2. [Organization Schemes](#organization-schemes)
3. [Navigation Systems](#navigation-systems)
4. [Search & Discovery](#search--discovery)
5. [Content Strategy](#content-strategy)
6. [IA Validation](#ia-validation)

## Core Components

### 1. Organization Systems
How information is categorized and structured

**Exact Schemes** (Objective):
- Alphabetical (A-Z listings)
- Chronological (timelines, date-based)
- Geographical (location-based)
- Numerical (ranked, ordered)

**Ambiguous Schemes** (Subjective):
- Topic (subject categories)
- Task (user goals: "Buy", "Learn", "Support")
- Audience (user types: "Students", "Teachers")
- Metaphor (desktop, shopping cart)

### 2. Labeling Systems
How information is represented

**Types**:
- Navigation labels (main menu items)
- Headings (page and section titles)
- Link text (descriptive, action-oriented)
- Index terms (tags, categories)
- Icons (visual representation)

**Best Practices**:
- Use user vocabulary, not jargon
- Be specific, not clever
- Maintain consistency
- Front-load important words
- Keep labels concise (2-3 words ideal)

### 3. Navigation Systems
How users move through information

**Global Navigation**:
- Present on all pages
- Primary sections/features
- Consistent placement
- 5-7 items maximum

**Local Navigation**:
- Section-specific options
- Contextual to current location
- Secondary priority
- Can be more extensive

**Contextual Navigation**:
- Inline links
- Related content
- "See also" sections
- Next/previous

### 4. Search Systems
How users query and find information

**Components**:
- Search interface (box, filters)
- Query processing (autocomplete, suggestions)
- Results presentation (ranking, snippets)
- Refinement tools (facets, sorting)
- No results handling

## Organization Schemes

### Hierarchical Structure
```
Home
├── Products
│   ├── Category A
│   │   ├── Product 1
│   │   └── Product 2
│   └── Category B
├── Services
└── About
```

**Best Practices**:
- 3-5 levels deep maximum
- 7±2 items per level
- Balanced breadth and depth
- Clear parent-child relationships

### Sequential Structure
```
Step 1 → Step 2 → Step 3 → Complete
```

**Use Cases**:
- Onboarding flows
- Checkout processes
- Tutorials
- Wizards

### Matrix Structure
```
        Feature A  Feature B  Feature C
Type 1     ✓         ✓         ✗
Type 2     ✓         ✗         ✓
Type 3     ✗         ✓         ✓
```

**Applications**:
- Product comparisons
- Feature matrices
- Faceted search
- Multi-dimensional filtering

### Organic Structure
No consistent pattern, exploratory

**Examples**:
- Knowledge graphs
- Tag clouds
- Social networks
- Wiki-style linking

## Navigation Systems

### Primary Navigation Patterns

**Horizontal Navigation Bar**:
```css
.nav-bar {
  display: flex;
  justify-content: space-between;
  padding: 16px 24px;
}
```
- Best for 5-7 items
- Clear hierarchy
- Always visible

**Vertical Sidebar**:
```css
.sidebar {
  width: 240px;
  height: 100vh;
  overflow-y: auto;
}
```
- Accommodates more items
- Good for nested structures
- Can be collapsed

**Tab Navigation**:
```css
.tabs {
  border-bottom: 1px solid #e5e5e5;
}
.tab.active {
  border-bottom: 2px solid var(--primary);
}
```
- Peer sections
- Mutually exclusive
- Clear active state

### Mobile Navigation

**Bottom Navigation**:
- 3-5 items maximum
- Most important features
- Thumb-friendly zone
- Persistent access

**Hamburger Menu**:
- Secondary options
- Reduces clutter
- Requires discovery
- Extra tap to access

**Priority+ Pattern**:
- Shows what fits
- "More" for overflow
- Responsive to space
- Maintains visibility

## Search & Discovery

### Search Interface Design

**Search Box**:
```html
<div class="search">
  <input
    type="search"
    placeholder="Search products, docs, help..."
    aria-label="Search"
  />
  <button type="submit">
    <Icon name="search" />
  </button>
</div>
```

**Enhancements**:
- Autocomplete
- Recent searches
- Popular searches
- Scoped search
- Voice input

### Results Presentation

**Result Card**:
```html
<article class="result">
  <h3>Title with <mark>keyword</mark></h3>
  <p class="snippet">
    Context showing matched <mark>keyword</mark>...
  </p>
  <div class="meta">
    <span class="type">Article</span>
    <time>2 days ago</time>
  </div>
</article>
```

### Faceted Search
```
Results (247)

Category
□ Documentation (89)
□ Tutorials (67)
□ API Reference (45)

Date
○ Last 24 hours
○ Last week
● Last month
○ All time

Sort by: Relevance ▼
```

## Content Strategy

### Content Audit Process
1. **Inventory**: List all content
2. **Evaluate**: Assess quality/relevance
3. **Organize**: Group and categorize
4. **Prioritize**: Identify critical content
5. **Plan**: Migration/improvement strategy

### Writing for Findability

**Page Titles**:
- Descriptive and unique
- Front-load keywords
- 60 characters max
- Include context

**Headings**:
- Clear hierarchy (h1 → h2 → h3)
- Scannable structure
- Parallel construction
- Keywords in headings

**Link Text**:
- Descriptive, not "click here"
- Indicate destination
- Match target page title
- Action-oriented

### Metadata Structure
```yaml
title: "Component Design Guidelines"
description: "Best practices for building reusable UI components"
category: "Design System"
tags: ["components", "guidelines", "design-system"]
author: "Design Team"
date: 2024-01-15
related: ["atomic-design", "component-testing"]
```

## IA Validation

### Card Sorting
**Process**:
1. Create cards with content/features
2. Users group cards logically
3. Users name groups
4. Analyze patterns
5. Refine structure

**Types**:
- Open: Users create categories
- Closed: Predefined categories
- Hybrid: Both options

### Tree Testing
**Process**:
1. Create text-only site structure
2. Give users tasks
3. Track paths taken
4. Measure success/failure
5. Identify problem areas

**Metrics**:
- Success rate
- Directness
- Time taken
- First click
- Backtrack rate

### Analytics Validation
**Track**:
- Search queries
- Navigation paths
- Exit pages
- 404 errors
- Time on site

**Look For**:
- Common search terms → Missing navigation?
- High bounce rates → Wrong page?
- Long paths → Poor structure?
- Dead ends → Missing links?

## Best Practices

### Do's
- Start with user needs
- Use familiar patterns
- Test with real users
- Maintain consistency
- Provide multiple paths
- Design for growth
- Document decisions

### Don'ts
- Over-categorize
- Use internal jargon
- Hide important content
- Create dead ends
- Forget mobile users
- Ignore search
- Make assumptions

## IA Checklist

- [ ] Clear organization scheme
- [ ] Consistent labeling
- [ ] Intuitive navigation
- [ ] Effective search
- [ ] Logical URL structure
- [ ] Helpful error pages
- [ ] Clear breadcrumbs
- [ ] Accessible structure
- [ ] Scalable architecture
- [ ] Documented patterns