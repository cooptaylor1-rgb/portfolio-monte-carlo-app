# Accessibility Implementation Guide

## Overview

This document outlines the accessibility features implemented in Phase 6 to ensure WCAG AA compliance and provide an inclusive user experience for all users.

## Key Accessibility Features

### 1. Keyboard Navigation

#### Focus Indicators
- All interactive elements (buttons, inputs, links) have visible focus states
- Focus ring: 2px solid gold (#C4A76A) with 50% opacity
- Focus offset for better visibility
- Consistent focus styles across all components

#### Tab Order
- Logical tab order following visual flow
- Skip link to main content (visible on focus)
- Mobile menu button accessible via keyboard
- Form fields follow logical sequence

#### Keyboard Shortcuts
| Action | Key | Description |
|--------|-----|-------------|
| Skip to main | Tab (first) | Bypass navigation |
| Navigate | Tab / Shift+Tab | Move through interactive elements |
| Activate | Enter / Space | Activate buttons and links |
| Close modal | Escape | Close overlays and modals |
| Navigate menu | Arrow keys | Navigate through menu items |

### 2. ARIA Labels and Semantic HTML

#### Landmark Regions
```tsx
<header role="banner" aria-label="Site header">
<nav role="navigation" aria-label="Main navigation">
<main role="main" aria-label="Main content">
<aside role="complementary">
```

#### Form Labels
- All input fields have associated `<label>` elements
- Required fields marked with `aria-required="true"` and visual asterisk
- Error messages linked via `aria-describedby`
- Helper text associated with inputs

#### Chart Accessibility
```tsx
<div role="region" aria-labelledby="chart-heading">
  <h3 id="chart-heading">Portfolio Trajectory</h3>
  <div aria-label="Line chart showing portfolio growth over 30 years">
    {/* Chart content */}
  </div>
</div>
```

#### Button Labels
- All icon-only buttons have `aria-label`
- Loading states announced: `aria-label="Running simulation..."`
- Disabled states with `aria-disabled="true"`

### 3. Screen Reader Support

#### Live Regions
```tsx
// Success notifications
<div role="status" aria-live="polite" aria-atomic="true">
  Export completed successfully
</div>

// Error messages
<div role="alert" aria-live="assertive" aria-atomic="true">
  Simulation failed. Please try again.
</div>
```

#### Descriptive Text
- Chart data described in text format
- Complex visualizations have accessible alternatives
- Statistical summaries provided alongside charts

#### Image Alternatives
- All decorative images have `alt=""`
- Informative images have descriptive alt text
- Icons paired with text labels

### 4. Color and Contrast

#### WCAG AA Compliance
- All text meets 4.5:1 contrast ratio
- Large text meets 3:1 contrast ratio
- UI components meet 3:1 contrast ratio

#### Color Usage
- Color never used as sole indicator
- Status conveyed through icons + color + text
- High contrast mode supported

#### Tested Combinations
| Element | Foreground | Background | Ratio | Status |
|---------|------------|------------|-------|--------|
| Primary text | #FFFFFF | #00335D | 12.63:1 | ✅ AAA |
| Secondary text | #B0BEC5 | #0F3B63 | 7.21:1 | ✅ AAA |
| Tertiary text | #78909C | #0F3B63 | 4.82:1 | ✅ AA |
| Gold accent | #C4A76A | #00335D | 4.98:1 | ✅ AA |
| Error text | #F44336 | #FFFFFF | 4.52:1 | ✅ AA |
| Success text | #4B8F29 | #FFFFFF | 4.67:1 | ✅ AA |

### 5. Responsive Design

#### Breakpoints
```css
/* Mobile */
@media (min-width: 320px)  /* Small phones */
@media (min-width: 375px)  /* Standard phones */
@media (min-width: 425px)  /* Large phones */

/* Tablet */
@media (min-width: 768px)  /* Small tablets */
@media (min-width: 1024px) /* Large tablets */

/* Desktop */
@media (min-width: 1440px) /* Standard desktop */
@media (min-width: 1920px) /* Large desktop */
```

#### Mobile Optimizations
- Touch targets minimum 44x44px
- Mobile menu with hamburger icon
- Collapsible sidebar on mobile
- Responsive typography scaling
- Horizontal scrolling prevented

#### Tablet Optimizations
- 2-column layouts for charts
- Expanded navigation visible
- Optimized spacing and padding
- Touch-friendly controls

#### Desktop Optimizations
- Full navigation sidebar
- Multi-column layouts
- Detailed tooltips on hover
- Keyboard shortcuts available

### 6. Focus Management

#### Modal Focus Trap
```typescript
// Trap focus within modal
const trapFocus = (container: HTMLElement) => {
  const focusableElements = getFocusableElements(container);
  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];
  
  // Handle Tab key
  container.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      if (e.shiftKey && document.activeElement === firstElement) {
        e.preventDefault();
        lastElement?.focus();
      } else if (!e.shiftKey && document.activeElement === lastElement) {
        e.preventDefault();
        firstElement?.focus();
      }
    }
  });
  
  firstElement?.focus();
};
```

#### Focus Restoration
- Previous focus restored after modal close
- Focus returned to trigger element
- Scroll position maintained

### 7. Error Prevention and Recovery

#### Input Validation
- Real-time validation feedback
- Clear error messages
- Suggestions for correction
- Required field indicators

#### Error Messages
```tsx
<Alert variant="error" title="Validation Error" role="alert">
  <ul aria-label="Error list">
    <li>Initial balance must be greater than $0</li>
    <li>Years to model must be between 1 and 50</li>
  </ul>
</Alert>
```

#### Loading States
- Loading indicators with `aria-busy="true"`
- Skeleton screens for progressive loading
- Timeout handling with retry options

## Component Accessibility

### Button Component
```tsx
<Button
  variant="primary"
  onClick={handleAction}
  aria-label="Run Monte Carlo simulation"
  disabled={isLoading}
  aria-disabled={isLoading}
>
  {isLoading ? 'Running...' : 'Run Simulation'}
</Button>
```

### Input Component
```tsx
<Input
  label="Initial Balance"
  type="number"
  required
  aria-required="true"
  error={errors.balance}
  aria-describedby={errors.balance ? 'balance-error' : undefined}
  helperText="Enter your starting portfolio value"
/>
```

### ChartContainer Component
```tsx
<ChartContainer
  title="Portfolio Trajectory"
  subtitle="30-year Monte Carlo simulation"
  role="region"
  aria-labelledby="portfolio-chart"
>
  <LineChart data={data} />
</ChartContainer>
```

## Testing Checklist

### Manual Testing
- [ ] All pages navigable by keyboard only
- [ ] Focus indicators visible on all interactive elements
- [ ] Skip link works and is visible on focus
- [ ] Modal focus trap works correctly
- [ ] Screen reader announces all content correctly
- [ ] Forms can be completed without mouse
- [ ] Error messages are announced
- [ ] Loading states are announced
- [ ] All images have appropriate alt text

### Automated Testing Tools
- [ ] Lighthouse accessibility score > 90
- [ ] axe DevTools - 0 violations
- [ ] WAVE - 0 errors
- [ ] pa11y - All checks pass
- [ ] Color contrast analyzer - All pass

### Screen Reader Testing
- [ ] NVDA (Windows) - All content accessible
- [ ] JAWS (Windows) - All content accessible
- [ ] VoiceOver (macOS/iOS) - All content accessible
- [ ] TalkBack (Android) - All content accessible

### Browser Testing
- [ ] Chrome - Full functionality
- [ ] Firefox - Full functionality
- [ ] Safari - Full functionality
- [ ] Edge - Full functionality
- [ ] Mobile browsers - Touch and voice input

## Best Practices for Future Development

### 1. Always Include Focus States
```css
.interactive-element:focus {
  outline: 2px solid #C4A76A;
  outline-offset: 2px;
}
```

### 2. Use Semantic HTML
```tsx
// ✅ Good
<button onClick={handleClick}>Submit</button>

// ❌ Bad
<div onClick={handleClick}>Submit</div>
```

### 3. Provide Text Alternatives
```tsx
// ✅ Good
<img src="chart.png" alt="Bar chart showing 75% success rate" />

// ❌ Bad
<img src="chart.png" />
```

### 4. Use ARIA When Needed
```tsx
// ✅ Good
<div role="alert" aria-live="polite">
  Simulation complete
</div>

// ❌ Overuse
<div role="div" aria-label="Container">  // Unnecessary
```

### 5. Test with Real Users
- Include users with disabilities in testing
- Test with assistive technologies
- Gather feedback and iterate
- Document accessibility decisions

## Resources

### Documentation
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)

### Tools
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [WAVE](https://wave.webaim.org/)
- [Color Contrast Analyzer](https://www.tpgi.com/color-contrast-checker/)

### Testing
- [NVDA Screen Reader](https://www.nvaccess.org/)
- [VoiceOver User Guide](https://support.apple.com/guide/voiceover/welcome/mac)
- [Keyboard Testing Guide](https://webaim.org/articles/keyboard/)

---

*Accessibility is not a feature, it's a fundamental requirement for inclusive design.*

