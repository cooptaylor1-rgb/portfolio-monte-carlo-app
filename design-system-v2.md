# Salem Investment Counselors - Design System
## Portfolio Scenario Analysis Platform

---

## 🎨 Brand Identity

### Logo Usage
- **Primary Logo:** Salem Investment Counselors wordmark with tree icon
- **Dimensions:** 458×175px (current), optimized for retina displays
- **Minimum Size:** 200px width for legibility
- **Clear Space:** Minimum 20px padding on all sides
- **Placement:** Top-left header, paired with product title

### Logo Guidelines
- Always maintain aspect ratio (2.6:1)
- Ensure sufficient contrast against backgrounds
- Use PNG format with transparency for flexibility
- Retina optimization: 2x asset size at 0.5x display scale

---

## 🎨 Color Palette

### Primary Colors
```css
/* Salem Navy - Primary Brand Color */
--salem-navy: #1B3B5F
--salem-navy-dark: #0F2540
--salem-navy-light: #2D4D73

/* Salem Gold - Secondary Brand Color */
--salem-gold: #C4A053
--salem-gold-light: #D4B87D
--salem-gold-dark: #B89648
--salem-gold-darker: #A88540
```

### UI Colors
```css
/* Backgrounds */
--bg-primary: #FFFFFF
--bg-secondary: #FAFAFA
--bg-tertiary: #F8F9FA
--bg-surface: rgba(255, 255, 255, 0.95)
--bg-overlay: rgba(255, 255, 255, 0.6)

/* Text */
--text-primary: #1B3B5F (Salem Navy)
--text-secondary: rgba(27, 59, 95, 0.7)
--text-tertiary: rgba(27, 59, 95, 0.5)
--text-inverse: #FFFFFF

/* Borders */
--border-light: rgba(196, 160, 83, 0.15)
--border-medium: rgba(196, 160, 83, 0.3)
--border-strong: rgba(196, 160, 83, 0.5)

/* States */
--hover-gold: rgba(196, 160, 83, 0.1)
--active-gold: rgba(196, 160, 83, 0.2)
--focus-gold: rgba(196, 160, 83, 0.3)
```

### Semantic Colors
```css
/* Success */
--success: #10B981
--success-light: #D1FAE5
--success-dark: #059669

/* Warning */
--warning: #F59E0B
--warning-light: #FEF3C7
--warning-dark: #D97706

/* Error */
--error: #EF4444
--error-light: #FEE2E2
--error-dark: #DC2626

/* Info */
--info: #3B82F6
--info-light: #DBEAFE
--info-dark: #2563EB
```

---

## 📐 Typography

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', 'SF Pro Display', sans-serif;
```

### Type Scale

#### Display
```css
/* H1 - Page Titles */
font-size: 2.25rem (36px)
font-weight: 700 (Bold)
line-height: 1.1
letter-spacing: -0.04em
margin-top: 0.5rem
margin-bottom: 0.5rem
```

#### Headings
```css
/* H2 - Section Headers */
font-size: 1.625rem (26px)
font-weight: 700 (Bold)
line-height: 1.2
letter-spacing: -0.03em
margin-top: 1rem
margin-bottom: 0.5rem

/* H3 - Subsection Headers */
font-size: 1.125rem (18px)
font-weight: 600 (Semibold)
line-height: 1.3
letter-spacing: -0.02em
margin-top: 0.5rem
margin-bottom: 0.25rem

/* H4 - Card Headers */
font-size: 1.0625rem (17px)
font-weight: 600 (Semibold)
line-height: 1.4
letter-spacing: -0.02em
margin-top: 0.375rem
margin-bottom: 0.25rem
```

#### Body Text
```css
/* Body - Default */
font-size: 1rem (16px)
font-weight: 400 (Regular)
line-height: 1.5
letter-spacing: -0.01em
margin-bottom: 0.5rem

/* Body Small */
font-size: 0.9375rem (15px)
font-weight: 400 (Regular)
line-height: 1.5
letter-spacing: -0.01em

/* Caption */
font-size: 0.8125rem (13px)
font-weight: 500 (Medium)
line-height: 1.4
letter-spacing: 0.05em
text-transform: uppercase
opacity: 0.7
```

### Typography Best Practices
- Use negative letter-spacing (-0.01em to -0.04em) for modern feel
- Apply antialiasing for crisp rendering
- Maintain consistent line-height for readability
- Use uppercase sparingly (labels, captions only)

---

## 📏 Spacing System

### Base Unit: 4px

#### Spacing Scale
```css
--space-1: 4px    /* 0.25rem */
--space-2: 8px    /* 0.5rem */
--space-3: 12px   /* 0.75rem */
--space-4: 16px   /* 1rem */
--space-5: 20px   /* 1.25rem */
--space-6: 24px   /* 1.5rem */
--space-8: 32px   /* 2rem */
--space-10: 40px  /* 2.5rem */
--space-12: 48px  /* 3rem */
--space-16: 64px  /* 4rem */
--space-20: 80px  /* 5rem */
```

#### Component Spacing
```css
/* Cards & Containers */
padding: 16px (--space-4)
margin-bottom: 12px (--space-3)

/* Metrics */
padding: 14px 16px
margin-bottom: 8px

/* Buttons */
padding: 10px 24px
margin: 4px

/* Input Fields */
padding: 8px 12px
margin-bottom: 4px

/* Sections */
margin-top: 16px
margin-bottom: 12px

/* Element Groups */
gap: 8px to 16px
```

---

## 🎯 Components

### Buttons

#### Primary Button
```css
background: linear-gradient(180deg, #C4A053 0%, #B89648 100%)
color: #FFFFFF
font-weight: 600
padding: 10px 24px
border-radius: 12px
font-size: 1rem
box-shadow: 0 2px 12px rgba(196, 160, 83, 0.3)
transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1)

/* Hover */
background: linear-gradient(180deg, #D4B87D 0%, #C4A053 100%)
box-shadow: 0 4px 20px rgba(196, 160, 83, 0.4)
transform: translateY(-1px)

/* Active */
background: linear-gradient(180deg, #B89648 0%, #A88540 100%)
box-shadow: 0 2px 8px rgba(196, 160, 83, 0.3)
transform: translateY(0px)
```

#### Secondary Button
```css
background: #FFFFFF
color: #C4A053
font-weight: 600
border: 2px solid #C4A053
padding: 10px 24px
border-radius: 12px
font-size: 1rem
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08)
transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1)

/* Hover */
background: rgba(196, 160, 83, 0.1)
box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12)
transform: translateY(-1px)

/* Active */
background: rgba(196, 160, 83, 0.2)
transform: translateY(0px)
```

#### Button States
- **Disabled:** opacity: 0.5, cursor: not-allowed
- **Loading:** add spinner animation
- **Focus:** outline with gold color

### Cards

#### Standard Card
```css
background: rgba(255, 255, 255, 0.95)
border: 1px solid rgba(196, 160, 83, 0.2)
border-radius: 12px
padding: 16px
box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0, 0, 0, 0.02)
backdrop-filter: blur(20px)
transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1)

/* Hover */
box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12)
transform: translateY(-2px)
```

#### Metric Card
```css
background: rgba(255, 255, 255, 0.95)
border: 1px solid rgba(196, 160, 83, 0.2)
border-radius: 12px
padding: 14px 16px
box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0, 0, 0, 0.02)
backdrop-filter: blur(20px)

/* Label */
font-size: 0.8125rem
font-weight: 600
text-transform: uppercase
letter-spacing: 0.05em
opacity: 0.7
color: #1B3B5F

/* Value */
font-size: 1.875rem
font-weight: 700
letter-spacing: -0.03em
color: #1B3B5F

/* Delta */
font-size: 0.9375rem
font-weight: 600
color: #C4A053
```

### Input Fields

#### Text Input
```css
background: rgba(255, 255, 255, 0.9)
border: 1px solid rgba(196, 160, 83, 0.3)
border-radius: 10px
padding: 8px 12px
font-size: 1rem
font-weight: 500
color: #1B3B5F
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06)
transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1)

/* Focus */
border-color: #C4A053
box-shadow: 0 4px 16px rgba(196, 160, 83, 0.2)
background: #FFFFFF
outline: none
```

#### Select Dropdown
```css
background: rgba(255, 255, 255, 0.9)
border: 1px solid rgba(196, 160, 83, 0.3)
border-radius: 10px
padding: 8px 12px
font-size: 1rem
font-weight: 500
color: #1B3B5F
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06)

/* Hover */
border-color: rgba(196, 160, 83, 0.5)
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08)
```

#### Slider
```css
/* Track */
background: rgba(196, 160, 83, 0.15)
height: 4px
border-radius: 2px

/* Fill */
background: linear-gradient(90deg, #C4A053 0%, rgba(196, 160, 83, 0.3) 100%)
height: 4px
border-radius: 2px

/* Thumb */
background: linear-gradient(135deg, #C4A053 0%, #B89648 100%)
width: 18px
height: 18px
border-radius: 50%
box-shadow: 0 2px 8px rgba(196, 160, 83, 0.3)

/* Thumb Hover */
transform: scale(1.1)
box-shadow: 0 4px 12px rgba(196, 160, 83, 0.4)
```

### Data Tables

```css
/* Container */
border: 1px solid rgba(196, 160, 83, 0.2)
border-radius: 12px
overflow: hidden
box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08)

/* Header */
background: linear-gradient(180deg, #1B3B5F 0%, #152D4A 100%)
color: #FFFFFF
font-size: 0.85rem
font-weight: 600
text-transform: uppercase
letter-spacing: 0.05em
padding: 12px 16px

/* Cell */
padding: 10px 16px
border-bottom: 1px solid rgba(196, 160, 83, 0.1)
color: #1B3B5F

/* Row Hover */
background: rgba(196, 160, 83, 0.05)
```

### Tabs

```css
/* Tab Container */
background: rgba(255, 255, 255, 0.6)
padding: 8px
border-radius: 16px
gap: 8px
box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08)
backdrop-filter: blur(20px)

/* Tab Inactive */
background: transparent
padding: 12px 24px
border-radius: 12px
color: #1B3B5F
font-weight: 500
font-size: 0.95rem

/* Tab Hover */
background: rgba(196, 160, 83, 0.1)
color: #C4A053

/* Tab Active */
background: linear-gradient(180deg, #C4A053 0%, #B89648 100%)
color: #FFFFFF
box-shadow: 0 2px 8px rgba(196, 160, 83, 0.3)
```

---

## 🎭 Effects & Interactions

### Shadows
```css
/* Elevation 1 - Cards, Inputs */
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06)

/* Elevation 2 - Raised Cards */
box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0, 0, 0, 0.02)

/* Elevation 3 - Hover States */
box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12)

/* Elevation Gold - Gold Accents */
box-shadow: 0 2px 12px rgba(196, 160, 83, 0.3)
box-shadow: 0 4px 20px rgba(196, 160, 83, 0.4) /* Hover */
```

### Border Radius
```css
--radius-sm: 8px   /* Small elements */
--radius-md: 10px  /* Inputs */
--radius-lg: 12px  /* Cards, buttons */
--radius-xl: 16px  /* Containers */
--radius-full: 50% /* Circular */
```

### Transitions
```css
/* Standard */
transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1)

/* Smooth (for larger movements) */
transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1)

/* Snappy (for micro-interactions) */
transition: all 0.15s cubic-bezier(0.4, 0.0, 0.2, 1)
```

### Hover Transforms
```css
/* Lift */
transform: translateY(-1px) to translateY(-2px)

/* Scale */
transform: scale(1.05) to scale(1.1)

/* Glow (via box-shadow) */
box-shadow: 0 4px 20px rgba(196, 160, 83, 0.4)
```

---

## 📱 Responsive Design

### Breakpoints
```css
/* Mobile */
max-width: 640px

/* Tablet */
min-width: 641px, max-width: 1024px

/* Desktop */
min-width: 1025px

/* Large Desktop */
min-width: 1440px
```

### Layout Guidelines
- **Mobile:** Single column, full-width components, larger touch targets
- **Tablet:** 2-column grid for metrics, adjusted spacing
- **Desktop:** 3-4 column grid, optimal spacing
- **Large Desktop:** Max content width 1400px, centered

---

## ♿ Accessibility

### Contrast Ratios
- **Normal Text:** Minimum 4.5:1 (WCAG AA)
- **Large Text:** Minimum 3:1 (WCAG AA)
- **UI Components:** Minimum 3:1 (WCAG AA)

### Focus States
- Always provide visible focus indicators
- Use gold color (#C4A053) for focus rings
- Minimum 2px outline width

### Interactive Elements
- Minimum 44×44px touch target
- Clear hover/active states
- Descriptive labels and ARIA attributes

---

## 🎨 Design Patterns

### Header Layout
```
[Logo (280px width)] [Spacer (24px)] [Title (H1)]
```

### Metric Grid
```
[Metric 1] [Metric 2] [Metric 3] [Metric 4]
(Equal width, 12-16px gap)
```

### Form Layout
```
[Label (uppercase, small)]
[Input Field (full width)]
[Helper Text (optional, small)]
(8px vertical spacing)
```

### Card Layout
```
[Card Header (H3)]
[Divider (1px, optional)]
[Content Area]
[Actions (bottom-aligned)]
```

---

## 📊 Chart Styling

### Chart Container
```css
background: rgba(255, 255, 255, 0.95)
border: 1px solid rgba(196, 160, 83, 0.15)
border-radius: 12px
padding: 10px
box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08)
```

### Chart Colors (Institutional)
```css
--chart-navy: #1B3B5F
--chart-gold: #C4A053
--chart-blue: #3B82F6
--chart-green: #10B981
--chart-red: #EF4444
--chart-purple: #8B5CF6
--chart-orange: #F59E0B
```

---

## 🚀 Performance Guidelines

### Image Optimization
- Use WebP format where supported
- Provide 2x assets for retina displays
- Lazy load below-the-fold images
- Compress images to <100KB where possible

### CSS Best Practices
- Use CSS custom properties for theming
- Minimize use of `!important`
- Leverage CSS containment for performance
- Use `will-change` sparingly

### Animation Performance
- Prefer `transform` and `opacity` for animations
- Use `cubic-bezier(0.4, 0.0, 0.2, 1)` for smooth easing
- Keep animations under 300ms
- Use `requestAnimationFrame` for JavaScript animations

---

## 📝 Usage Guidelines

### Do's
✅ Maintain consistent spacing using the 4px scale  
✅ Use Salem colors for all brand touchpoints  
✅ Apply proper typography hierarchy  
✅ Ensure sufficient contrast for readability  
✅ Test on multiple screen sizes  
✅ Provide hover/focus states for interactive elements  
✅ Use the design system tokens  

### Don'ts
❌ Don't use colors outside the defined palette  
❌ Don't mix font weights inconsistently  
❌ Don't ignore spacing guidelines  
❌ Don't create custom components without system review  
❌ Don't use different shadow styles  
❌ Don't override border-radius arbitrarily  
❌ Don't forget accessibility considerations  

---

## 🔄 Changelog

### Version 2.0 (December 2025)
- Comprehensive design system documentation
- Refined color palette with semantic tokens
- Updated typography scale for better hierarchy
- Improved component specifications
- Added accessibility guidelines
- Enhanced spacing system
- Performance optimization guidelines

### Version 1.0 (November 2025)
- Initial Salem Investment Counselors branding
- Basic component library
- Apple-inspired styling foundation

---

## 📞 Support

For questions about this design system or proposed changes, contact:
- **Design Lead:** Salem Investment Counselors Design Team
- **Technical Lead:** Development Team

---

*Last Updated: December 2, 2025*
