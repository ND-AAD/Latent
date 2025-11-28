# Accessibility Guidelines (WCAG 2.2 Level AA)

## Table of Contents
1. [POUR Principles](#pour-principles)
2. [Critical Requirements](#critical-requirements)
3. [Component Patterns](#component-patterns)
4. [Testing Methods](#testing-methods)
5. [ARIA Implementation](#aria-implementation)

## POUR Principles

### Perceivable
Information must be presentable in ways users can perceive

**Requirements**:
- Text alternatives for images
- Captions for videos
- Sufficient color contrast
- Text resizable to 200%
- No information by color alone

### Operable
Interface components must be operable

**Requirements**:
- Keyboard accessible
- No keyboard traps
- Adequate time limits
- No seizure triggers
- Clear focus indicators
- Multiple input methods

### Understandable
Information and UI operation must be understandable

**Requirements**:
- Readable text (8th grade level)
- Predictable navigation
- Consistent identification
- Input assistance
- Error prevention

### Robust
Content must work with assistive technologies

**Requirements**:
- Valid HTML
- Semantic markup
- ARIA when needed
- Progressive enhancement
- Cross-browser support

## Critical Requirements

### Color Contrast
**Minimum Ratios**:
```css
/* Normal text (< 24px) */
.text {
  color: #595959; /* 7:1 on white */
}

/* Large text (≥ 24px or ≥ 18px bold) */
.heading {
  color: #767676; /* 4.5:1 on white */
}

/* Interactive elements */
.button {
  background: #0066cc; /* 4.5:1 */
  color: white;
}
```

**Testing Tool**:
```javascript
function getContrastRatio(color1, color2) {
  const l1 = getLuminance(color1);
  const l2 = getLuminance(color2);
  return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
}
```

### Keyboard Navigation
**Implementation**:
```html
<!-- All interactive elements keyboard accessible -->
<button>Native button (accessible)</button>
<a href="#">Native link (accessible)</a>
<div role="button" tabindex="0" onkeydown="handleKey(event)">
  Custom button (needs work)
</div>
```

**Tab Order**:
- Logical flow (left-to-right, top-to-bottom)
- Skip links for navigation
- No positive tabindex values
- Focus trap for modals

```css
/* Visible focus indicators */
:focus {
  outline: 2px solid #0066cc;
  outline-offset: 2px;
}

/* Don't remove outline without replacement */
:focus:not(:focus-visible) {
  outline: 2px solid #0066cc;
}
```

### Touch Targets
**Minimum Sizes**:
```css
/* WCAG 2.1 Level AAA (recommended) */
.touch-target {
  min-width: 44px;
  min-height: 44px;
}

/* Spacing between targets */
.touch-target + .touch-target {
  margin-left: 8px;
}
```

### Form Accessibility
**Proper Labeling**:
```html
<!-- Explicit label -->
<label for="email">Email Address</label>
<input type="email" id="email" required>

<!-- Implicit label -->
<label>
  <input type="checkbox"> Subscribe
</label>

<!-- Multiple inputs -->
<fieldset>
  <legend>Shipping Address</legend>
  <label for="street">Street</label>
  <input id="street">
</fieldset>
```

**Error Messages**:
```html
<div class="field">
  <label for="password">Password</label>
  <input
    type="password"
    id="password"
    aria-describedby="password-error"
    aria-invalid="true"
  >
  <div id="password-error" role="alert">
    Password must be at least 8 characters
  </div>
</div>
```

## Component Patterns

### Accessible Modal
```html
<div
  role="dialog"
  aria-labelledby="modal-title"
  aria-describedby="modal-desc"
  aria-modal="true"
>
  <h2 id="modal-title">Confirm Action</h2>
  <p id="modal-desc">Are you sure?</p>
  <button>Cancel</button>
  <button>Confirm</button>
</div>
```

```javascript
// Focus management
function openModal() {
  previousFocus = document.activeElement;
  modal.showModal();
  modal.querySelector('button').focus();
  trapFocus(modal);
}

function closeModal() {
  modal.close();
  previousFocus.focus();
}
```

### Accessible Dropdown
```html
<div class="dropdown">
  <button
    aria-expanded="false"
    aria-controls="menu"
    aria-haspopup="menu"
  >
    Options
  </button>
  <ul id="menu" role="menu" hidden>
    <li role="menuitem">Edit</li>
    <li role="menuitem">Delete</li>
  </ul>
</div>
```

### Accessible Tabs
```html
<div class="tabs">
  <div role="tablist">
    <button
      role="tab"
      aria-selected="true"
      aria-controls="panel-1"
      id="tab-1"
    >
      Tab 1
    </button>
    <button
      role="tab"
      aria-selected="false"
      aria-controls="panel-2"
      id="tab-2"
    >
      Tab 2
    </button>
  </div>
  <div
    role="tabpanel"
    id="panel-1"
    aria-labelledby="tab-1"
  >
    Panel 1 content
  </div>
  <div
    role="tabpanel"
    id="panel-2"
    aria-labelledby="tab-2"
    hidden
  >
    Panel 2 content
  </div>
</div>
```

### Loading States
```html
<!-- Announce loading -->
<div aria-live="polite" aria-busy="true">
  <span role="status">Loading results...</span>
</div>

<!-- Announce completion -->
<div aria-live="polite" aria-busy="false">
  <span role="status">10 results found</span>
</div>
```

## Testing Methods

### Manual Testing Checklist
- [ ] Navigate with keyboard only
- [ ] Check all focus indicators visible
- [ ] Verify tab order logical
- [ ] Test with screen reader
- [ ] Zoom to 200% (no horizontal scroll)
- [ ] Check color contrast
- [ ] Verify form labels
- [ ] Test error messages
- [ ] Check heading hierarchy
- [ ] Verify alt text

### Automated Testing
```javascript
// Using axe-core
const results = await axe.run();
results.violations.forEach(violation => {
  console.error(violation.description);
  violation.nodes.forEach(node => {
    console.log(node.html);
  });
});
```

### Screen Reader Testing
**Common Combinations**:
- NVDA + Firefox (Windows)
- JAWS + Chrome (Windows)
- VoiceOver + Safari (macOS/iOS)
- TalkBack + Chrome (Android)

**Key Commands**:
- Navigate headings: H
- Navigate landmarks: D
- Navigate buttons: B
- Navigate links: K
- Read all: Ctrl+A
- Stop reading: Ctrl

## ARIA Implementation

### When to Use ARIA
**Rule 1**: Don't use ARIA if native HTML works
```html
<!-- Good: Native -->
<button>Click me</button>

<!-- Bad: ARIA -->
<div role="button" tabindex="0">Click me</div>
```

**Rule 2**: Don't change native semantics
```html
<!-- Good -->
<h2 role="tab">Tab heading</h2>

<!-- Bad -->
<h2><div role="tab">Tab heading</div></h2>
```

### Common ARIA Attributes
```html
<!-- Labeling -->
<input aria-label="Search">
<div aria-labelledby="heading-id">
<div aria-describedby="help-text">

<!-- States -->
<button aria-pressed="true">
<div aria-expanded="false">
<input aria-invalid="true">
<div aria-hidden="true">

<!-- Live regions -->
<div aria-live="polite">
<div aria-live="assertive">
<div role="alert">
<div role="status">

<!-- Relationships -->
<nav aria-label="Main">
<main role="main">
<aside role="complementary">
<div role="search">
```

### Landmark Roles
```html
<header role="banner">
  <nav role="navigation">
</header>

<main role="main">
  <article role="article">
    <section role="region" aria-label="Introduction">
    </section>
  </article>
  <aside role="complementary">
  </aside>
</main>

<footer role="contentinfo">
</footer>
```

## Best Practices

### Do's
- Test with real assistive technologies
- Use semantic HTML first
- Provide multiple ways to accomplish tasks
- Design with accessibility from the start
- Include users with disabilities in testing
- Document accessibility features

### Don'ts
- Rely on color alone
- Auto-play media with sound
- Use placeholder as label
- Remove focus indicators
- Create keyboard traps
- Assume ARIA fixes everything

## Quick Fixes

### Common Issues & Solutions

**Issue**: Missing alt text
```html
<!-- Fix -->
<img src="chart.png" alt="Sales increased 25% in Q4">
```

**Issue**: Low contrast
```css
/* Fix: Increase contrast */
.text {
  color: #595959; /* Was #999999 */
}
```

**Issue**: Missing focus indicator
```css
/* Fix: Add visible focus */
:focus {
  outline: 2px solid currentColor;
}
```

**Issue**: Inaccessible form
```html
<!-- Fix: Add labels -->
<label for="name">Name</label>
<input id="name" required>
```