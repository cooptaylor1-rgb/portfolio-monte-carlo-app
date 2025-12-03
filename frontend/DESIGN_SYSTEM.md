# Design System - Portfolio Monte Carlo App

## Overview
A professional design system for retirement and portfolio scenario analysis software. Built for advisor-facing applications with emphasis on data clarity, trustworthiness, and efficiency.

---

## 1. Color System

### Brand Colors
```typescript
primary: {
  navy: '#0F3B63',      // Salem navy - primary brand
  navyLight: '#1F4F7C', // Lighter navy for hover states
  navyDark: '#082539',  // Darker navy for depth
}

accent: {
  gold: '#B49759',      // Salem gold - accent, CTAs
  goldLight: '#C4A76A', // Lighter gold for hover
  goldDark: '#9A834D',  // Darker gold for active
}
```

### Neutral Palette (Dark Mode)
```typescript
background: {
  base: '#0A0C10',      // App background
  elevated: '#12141A',  // Cards, elevated surfaces
  hover: '#1A1D24',     // Hover states
  border: '#262A33',    // Subtle borders
}

text: {
  primary: '#FFFFFF',   // Headings, primary text
  secondary: '#B4B9C2', // Body text, labels
  tertiary: '#6F767D',  // Helper text, captions
  disabled: '#4A5057',  // Disabled states
}
```

### Semantic Colors
```typescript
status: {
  success: {
    base: '#10B981',    // Success actions, positive metrics
    light: '#34D399',   // Light variant
    dark: '#059669',    // Dark variant
  },
  warning: {
    base: '#F59E0B',    // Warning states, moderate risk
    light: '#FBBF24',   // Light variant
    dark: '#D97706',    // Dark variant
  },
  error: {
    base: '#EF4444',    // Errors, high risk, danger actions
    light: '#F87171',   // Light variant
    dark: '#DC2626',    // Dark variant
  },
  info: {
    base: '#3B82F6',    // Info states, neutral highlights
    light: '#60A5FA',   // Light variant
    dark: '#2563EB',    // Dark variant
  },
}
```

### Chart Colors
```typescript
charts: {
  equity: '#4CA6E8',    // Equity allocation
  fixed: '#7AC18D',     // Fixed income
  cash: '#D7B46A',      // Cash
  projection: '#7AA6C4', // Projections
  percentiles: [
    '#059669',          // P90 (best case)
    '#10B981',          // P75
    '#B49759',          // P50 (median) - GOLD
    '#F59E0B',          // P25
    '#DC2626',          // P10 (worst case)
  ],
}
```

---

## 2. Typography

### Font Families
- **Primary**: Inter (body text, labels, data)
- **Display**: Nunito Sans (headings, titles)
- **Mono**: JetBrains Mono (code, numbers with precision)

### Type Scale
```typescript
// Page Titles
h1: {
  fontSize: '32px',
  lineHeight: '40px',
  fontWeight: 700,
  letterSpacing: '-0.02em',
  fontFamily: 'Nunito Sans',
}

// Section Headings
h2: {
  fontSize: '24px',
  lineHeight: '32px',
  fontWeight: 600,
  letterSpacing: '-0.01em',
  fontFamily: 'Nunito Sans',
}

// Subsection Headings
h3: {
  fontSize: '18px',
  lineHeight: '28px',
  fontWeight: 600,
  letterSpacing: '0',
  fontFamily: 'Nunito Sans',
}

// Card Titles, Labels
h4: {
  fontSize: '16px',
  lineHeight: '24px',
  fontWeight: 600,
  letterSpacing: '0',
  fontFamily: 'Inter',
}

// Body Text
body: {
  fontSize: '14px',
  lineHeight: '20px',
  fontWeight: 400,
  letterSpacing: '0',
  fontFamily: 'Inter',
}

// Small Text (helper, captions)
small: {
  fontSize: '12px',
  lineHeight: '16px',
  fontWeight: 400,
  letterSpacing: '0',
  fontFamily: 'Inter',
}

// Micro Text (legal, timestamps)
micro: {
  fontSize: '11px',
  lineHeight: '14px',
  fontWeight: 400,
  letterSpacing: '0',
  fontFamily: 'Inter',
}

// Large Numbers (metrics)
display: {
  fontSize: '36px',
  lineHeight: '44px',
  fontWeight: 700,
  letterSpacing: '-0.02em',
  fontFamily: 'Nunito Sans',
}
```

---

## 3. Spacing Scale

Use consistent 4px base unit with specific multipliers:

```typescript
spacing: {
  xs: '4px',   // 1x - Tight spacing within components
  sm: '8px',   // 2x - Small gaps, padding
  md: '16px',  // 4x - Default spacing between elements
  lg: '24px',  // 6x - Section spacing
  xl: '32px',  // 8x - Major section dividers
  '2xl': '48px', // 12x - Page-level spacing
  '3xl': '64px', // 16x - Hero sections
}

// Common Patterns:
// - Card padding: 24px (lg)
// - Section gap: 32px (xl)
// - Form field gap: 16px (md)
// - Button padding: 12px 24px
// - Input padding: 12px 16px
```

---

## 4. Border & Radius

```typescript
borders: {
  width: {
    thin: '1px',
    medium: '2px',
    thick: '3px',
  },
  radius: {
    sm: '6px',   // Buttons, inputs, small elements
    md: '8px',   // Cards, containers
    lg: '12px',  // Large cards, modals
    xl: '16px',  // Feature cards
    full: '9999px', // Pills, avatars
  },
}
```

---

## 5. Shadows & Elevation

```typescript
shadows: {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.3)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.3), 0 2px 4px -2px rgb(0 0 0 / 0.2)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.4), 0 4px 6px -4px rgb(0 0 0 / 0.3)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.4), 0 8px 10px -6px rgb(0 0 0 / 0.3)',
  glow: '0 0 20px rgb(180 151 89 / 0.3)', // Gold glow for emphasis
}

// Elevation levels:
// Base: no shadow
// Raised (cards): sm
// Floating (dropdowns): md
// Modal: lg
// Emphasized: glow
```

---

## 6. Component Specifications

### Button Variants

**Primary** (CTAs, main actions)
- Background: `accent.gold`
- Text: `text.primary`
- Hover: `accent.goldLight`
- Active: `accent.goldDark`
- Padding: `12px 24px`
- Border radius: `sm`
- Font weight: 600

**Secondary** (Alternative actions)
- Background: `transparent`
- Border: `1px solid accent.gold`
- Text: `accent.gold`
- Hover: `background.hover`
- Padding: `12px 24px`
- Border radius: `sm`
- Font weight: 600

**Tertiary** (Low priority)
- Background: `background.hover`
- Text: `text.secondary`
- Hover: `background.border`
- Padding: `12px 24px`
- Border radius: `sm`
- Font weight: 500

**Danger** (Destructive actions)
- Background: `status.error.base`
- Text: `text.primary`
- Hover: `status.error.dark`
- Padding: `12px 24px`
- Border radius: `sm`
- Font weight: 600

### Input Fields

**Default**
- Background: `background.elevated`
- Border: `1px solid background.border`
- Text: `text.primary`
- Padding: `12px 16px`
- Border radius: `sm`
- Focus: `border accent.gold`, `ring 0 0 0 3px accent.gold/20`

**Error State**
- Border: `status.error.base`
- Ring: `status.error.base/20`

**Disabled**
- Background: `background.hover`
- Text: `text.disabled`
- Cursor: `not-allowed`

### Card Component

**Default**
- Background: `background.elevated`
- Border: `1px solid background.border`
- Padding: `24px`
- Border radius: `md`
- Shadow: `sm`

**Interactive** (clickable)
- Hover: `border accent.gold`, `shadow md`
- Cursor: `pointer`

**Highlighted**
- Border: `2px solid accent.gold`
- Shadow: `glow`

### Stat Tile

**Structure:**
- Background: `background.elevated`
- Padding: `20px`
- Border radius: `md`
- Border: `1px solid background.border`

**Elements:**
- Label: `text.tertiary`, `small`
- Value: `display`, `text.primary`
- Change: `body`, with status color
- Icon: `24px`, status color

---

## 7. Iconography

**Size Scale:**
- Micro: `12px` (inline with text)
- Small: `16px` (labels, small buttons)
- Default: `20px` (standard buttons, nav)
- Large: `24px` (stat tiles, feature icons)
- XL: `32px` (empty states)
- Hero: `48px` (large empty states)

**Usage:**
- Use Lucide React icons consistently
- Pair icons with text for clarity
- Use semantic colors (success/warning/error icons)

---

## 8. Layout Grid

**Container:**
- Max width: `1440px`
- Padding: `32px` (desktop), `16px` (mobile)
- Margin: `auto`

**Sidebar:**
- Width: `240px` (desktop)
- Collapsible on tablet
- Hidden on mobile (show hamburger menu)

**Content Grid:**
- Gap: `24px` (default)
- Columns: 12-column grid
- Breakpoints:
  - Mobile: `< 640px` (1 column)
  - Tablet: `640px - 1024px` (2 columns)
  - Desktop: `> 1024px` (3-4 columns)
  - Wide: `> 1440px` (4+ columns)

---

## 9. Animation & Transitions

**Duration:**
- Fast: `150ms` (hover, focus)
- Default: `200ms` (most transitions)
- Slow: `300ms` (complex animations, page transitions)

**Easing:**
- `ease-out`: For entrances
- `ease-in-out`: For state changes
- `ease-in`: For exits

**Common Patterns:**
```css
/* Hover */
transition: all 150ms ease-out;

/* Focus rings */
transition: box-shadow 200ms ease-out;

/* Height animations */
transition: height 300ms ease-in-out;
```

---

## 10. Accessibility Standards

**Minimum Requirements:**
- Color contrast: WCAG AA (4.5:1 for body text, 3:1 for large text)
- Focus indicators: Visible 2px outline or ring
- Keyboard navigation: All interactive elements accessible
- ARIA labels: All icons and controls properly labeled
- Form validation: Clear error messages, associated with inputs

**Color Usage:**
- Never rely on color alone for meaning
- Pair colors with icons or text labels
- Provide alternative text for all visual information

---

## Implementation Notes

1. **Tailwind Config**: Extend theme with these tokens
2. **CSS Variables**: Define core values as CSS custom properties
3. **Component Library**: Build reusable React components using these specs
4. **Documentation**: Keep this design system as single source of truth
5. **Version**: v1.0 - Portfolio Monte Carlo Redesign (Dec 2025)
