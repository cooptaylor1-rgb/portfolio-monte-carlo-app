# UX/UI Audit - Portfolio Monte Carlo App

## Executive Summary
The current React app is a functional port from Streamlit but lacks polish, visual hierarchy, and professional UX patterns expected in advisor-facing financial software. Key issues span navigation, forms, visual design, and user flows.

---

## Critical Issues by Category

### 1. Navigation & Information Architecture
**Problems:**
- ❌ Navigation labels are unclear ("Inputs & Assumptions" is vague)
- ❌ No clear workflow guidance (what to do first, second, third)
- ❌ Sidebar is always visible but provides no context of progress
- ❌ No breadcrumbs or "where am I?" indicators beyond active state
- ❌ Missing quick actions in header (Run Simulation, Export, etc.)

**Impact:** Users don't know where to start or what the logical flow is.

### 2. Forms & Input Experience (InputsPage)
**Problems:**
- ❌ 80+ fields presented as a flat wall of inputs with minimal grouping
- ❌ Inconsistent input widths and alignment (some full-width, some not)
- ❌ No visual hierarchy between sections (all use basic card)
- ❌ Expander components hide important context, making it unclear what's configured
- ❌ Labels and helper text are too similar in visual weight
- ❌ No validation feedback until after submit
- ❌ Preset dropdown is disconnected from the flow
- ❌ Action buttons ("Validate", "Run Simulation") buried at bottom with equal visual weight

**Impact:** Overwhelming experience, high error rates, unclear required vs. optional fields.

### 3. Dashboard & Data Visualization
**Problems:**
- ❌ Charts lack context (no titles, minimal legends)
- ❌ Empty state is generic ("Run a simulation first" with no guidance)
- ❌ Metric cards are uniform - no emphasis on most important metric (success probability)
- ❌ No quick comparison or trend indicators
- ❌ Loading states are basic spinners with no progress indication
- ❌ Charts use inconsistent sizing and spacing

**Impact:** Hard to interpret results, unclear what actions to take.

### 4. Scenarios & Comparison
**Problems:**
- ❌ Adding scenarios requires multiple clicks with unclear purpose
- ❌ Sliders for adjustments have no quick presets (e.g., "Optimistic", "Pessimistic")
- ❌ Results table is dense and hard to scan
- ❌ No visual comparison (charts showing scenarios side-by-side)
- ❌ Sensitivity analysis is buried and disconnected from scenario builder

**Impact:** Time-consuming to build and compare scenarios, unclear insights.

### 5. Design System & Visual Consistency
**Problems:**
- ❌ Inconsistent spacing (some 4px, some 6px, some 8px with no pattern)
- ❌ Button styles vary across pages (some use bg-brand-gold, others don't)
- ❌ Card component lacks consistent padding/shadow/border
- ❌ Typography hierarchy is weak (H1/H2/H3 barely differentiated)
- ❌ Color usage is inconsistent (success/warning/danger not systematically applied)
- ❌ Form inputs use .input class but definition is unclear
- ❌ No hover states or micro-interactions

**Impact:** App feels amateurish and hard to navigate.

### 6. Responsiveness & Layout
**Problems:**
- ❌ Fixed sidebar takes up 256px on all screens (no collapse)
- ❌ Content area has inconsistent max-width (some pages full-width, others not)
- ❌ Forms don't stack properly on smaller screens
- ❌ Charts break or become unreadable at smaller widths
- ❌ No consideration for 1366x768 (common laptop resolution)

**Impact:** Poor experience on common laptop screens.

---

## Workflow Issues

### Primary User Flow: "Run an Analysis"
**Current Experience:**
1. Land on Dashboard (empty, unclear where to start)
2. Navigate to "Inputs & Assumptions" (vague label)
3. Fill 80+ fields with minimal guidance
4. Scroll to bottom, find "Run Simulation" button
5. Wait (no progress indicator)
6. Navigate back to Dashboard to see results

**Problems:**
- No onboarding or first-time user guidance
- Unclear which fields are critical vs. optional
- No inline validation or smart defaults
- No success confirmation or "next steps" after running

### Secondary Flow: "Compare Scenarios"
**Current Experience:**
1. Navigate to "Scenarios & Analysis"
2. Click "Add Scenario" (unclear what this does)
3. Adjust 4 sliders per scenario
4. Click "Run Scenarios" (separate from main simulation)
5. Review table (hard to interpret differences)

**Problems:**
- Disconnected from main simulation workflow
- No templates or quick presets
- Results lack visual comparison
- Unclear how to export or act on insights

---

## Design System Gaps

### Missing Components:
- ✗ Consistent Button variants (primary, secondary, tertiary, danger)
- ✗ Input validation states (error, success, warning)
- ✗ Loading skeletons (currently just spinners)
- ✗ Toast notifications for actions
- ✗ Empty state illustrations
- ✗ Stat tiles with trends
- ✗ Progress indicators
- ✗ Section headers with descriptions
- ✗ Card variants (default, highlighted, interactive)

### Inconsistent Patterns:
- Link styling (sometimes underlined, sometimes not)
- Icon usage (sizes vary: 16/20/24px)
- Spacing between sections (sometimes 24px, sometimes 32px)
- Border radius (some components 4px, others 8px, cards 12px)

---

## Recommendations Priority

### P0 (Critical - Must Fix):
1. **Create proper design system** (tokens, components, spacing scale)
2. **Redesign InputsPage** with clear sections, better hierarchy, inline validation
3. **Add workflow guidance** (stepper, progress, "what's next")
4. **Improve Dashboard** with clear CTAs and result interpretation

### P1 (High - Should Fix):
5. **Standardize all components** (Button, Card, Input, etc.)
6. **Add quick actions to header** (Run, Export, Save)
7. **Improve scenario builder** with templates and visual comparison
8. **Better empty states** with clear guidance

### P2 (Medium - Nice to Have):
9. **Add onboarding flow** for first-time users
10. **Improve chart readability** (titles, legends, highlights)
11. **Add keyboard shortcuts** for power users
12. **Responsive optimizations**

---

## Next Steps

1. Create design system foundation (theme tokens)
2. Build core component library
3. Redesign page layouts with clear hierarchy
4. Implement improved workflows
5. Polish with micro-interactions and animations
