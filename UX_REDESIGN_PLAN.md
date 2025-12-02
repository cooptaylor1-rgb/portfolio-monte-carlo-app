# Professional Portfolio Analysis Platform - UX Redesign Plan

## Executive Summary
Transform the current Monte Carlo simulation app into a best-in-class professional portfolio analysis platform with clear navigation, enhanced risk visualization, and streamlined workflows for advisors and sophisticated investors.

## Current State Analysis

### Strengths
- Comprehensive Monte Carlo simulation engine
- Multiple stress test scenarios
- Tax-advantaged account modeling
- Healthcare cost projections
- Financial goal tracking
- PDF report generation
- Apple-inspired visual design with Salem branding

### Pain Points
1. **Navigation**: All inputs on single page, no clear workflow progression
2. **Cognitive Load**: Too many inputs visible simultaneously
3. **Risk Clarity**: Success metrics buried, downside scenarios not prominent enough
4. **Workflow**: Linear flow doesn't match advisor use patterns
5. **Comparison**: Difficult to compare multiple scenarios side-by-side
6. **Mobile**: Not optimized for tablet use in client meetings

## Proposed UX Architecture

### 1. **Tab-Based Navigation** (Primary Workflow)
```
┌─────────────────────────────────────────────────────────────┐
│ Salem Investment Counselors                          [Report]│
├─────────────────────────────────────────────────────────────┤
│ [Overview] [Client] [Portfolio] [Analysis] [Reports]        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                    Content Area                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### Tab 1: Overview Dashboard
**Purpose**: At-a-glance risk assessment and plan health

**Layout**:
- **Hero Metrics** (Top): Success Probability (large), Current Age → Horizon, Portfolio Value
- **Risk Summary Cards**: 
  - Downside Protection (P10 ending value, shortfall probability)
  - Sequence Risk (first 5-year returns impact)
  - Cash Flow Coverage (years until depletion scenarios)
- **Quick Actions**: Run Simulation, Compare Scenarios, Export Report
- **Recent Analysis**: Last 3 scenarios with quick access

#### Tab 2: Client & Assumptions
**Purpose**: Rapid data entry with validation

**Sections** (Collapsible Accordions):
1. **Client Information** (Always Visible)
   - Name, Advisor, Report Date
   - Quick Save/Load Client Profile

2. **Time Horizon & Demographics**
   - Current Age, Horizon Age, Longevity Toggle
   - Visual timeline showing current position

3. **Portfolio Details**
   - Starting Value (large, prominent)
   - Asset Allocation (pie chart + sliders)
   - Return Assumptions (expert/simple toggle)
   - Account Types (Taxable/IRA/Roth with visual)

4. **Cash Flows**
   - Spending (fixed vs % with calculator)
   - Income Sources (expandable list)
   - Healthcare Costs
   - One-Time Events (timeline visual)

5. **Tax & Withdrawal Strategy**
   - RMD Settings
   - Tax Rates
   - Withdrawal Sequencing

**Features**:
- Input validation with inline warnings
- Tooltips with industry benchmarks
- "Reasonable?" indicators for outlier inputs
- Quick presets: "Conservative", "Moderate", "Aggressive"

#### Tab 3: Portfolio Analysis
**Purpose**: Run simulations and understand base case

**Layout**:
- **Simulation Controls** (Sticky Top Bar):
  - Number of Scenarios slider
  - Spending Rule toggle
  - [Run Simulation] button (primary, large)
  - Last run timestamp
  
- **Results Display**:
  
  **Section A: Success Metrics** (Cards)
  - Success Probability (gauge with context)
  - Ending Portfolio Values (P10/Median/P90 with delta)
  - Years Sustained (with confidence bars)
  
  **Section B: Time Series Visualization**
  - Fan Chart (P10-P90 shaded regions)
  - Median Path (bold line)
  - Portfolio Value Axis with zoom
  - Age/Year dual axis
  - Hover: specific percentile values
  
  **Section C: Risk Breakdown**
  - Depletion Probability Timeline (line chart)
  - Worst Case Scenarios (table: bottom 10%)
  - Recovery Analysis (from drawdowns)
  
  **Section D: Cash Flow Analysis**
  - Income vs Spending over time
  - Withdrawal sources stacked bar
  - RMD projections
  
  **Section E: Goal Tracking**
  - Financial Goals (if defined)
  - Probability bars for each goal
  - Timeline markers on main chart

#### Tab 4: Scenario Analysis
**Purpose**: Stress testing and comparative analysis

**Layout**:

**Stress Test Builder** (Left Panel, 30%):
- Predefined Scenarios (chips):
  - Market Downturn (-20% Year 1)
  - Sequence Risk (bad early returns)
  - High Inflation (+2-3%)
  - Longevity (live to 100)
  - Healthcare Shock (+50% costs)
  
- Custom Scenario Builder:
  - Name
  - Return adjustment
  - Spending adjustment  
  - Inflation adjustment
  - Duration
  - [Add to Comparison] button

**Comparison View** (Right Panel, 70%):
- **Scenario Cards** (horizontal scroll):
  Each card shows:
  - Scenario name
  - Success probability (color-coded)
  - Ending values (P10/Median/P90)
  - Mini fan chart
  - [Remove] [Details] buttons

- **Detailed Comparison**:
  - Overlay fan charts (different colors)
  - Side-by-side metrics table
  - Delta from base case
  - Traffic light indicators (green/yellow/red)

**Allocation Comparison**:
- Test different portfolio mixes
- Side-by-side allocation viewers
- Efficient frontier overlay
- Risk/return scatter

#### Tab 5: Reports & Export
**Purpose**: Professional deliverables

**Sections**:

1. **Report Builder**
   - Select sections to include (checkboxes):
     - Executive Summary
     - Assumptions
     - Base Case Analysis
     - Stress Tests
     - Recommendations
   - Client-facing vs Internal toggle
   - Branding options

2. **Export Formats**
   - PDF Report (with page preview)
   - PowerPoint Deck
   - Excel Workbook (raw data)
   - Interactive HTML

3. **Saved Reports**
   - History of generated reports
   - Quick regenerate
   - Version comparison

## Design System Enhancements

### Typography Scale
```
H1: 2.5rem / 40px - Page titles
H2: 1.75rem / 28px - Section headers  
H3: 1.25rem / 20px - Subsection headers
H4: 1.125rem / 18px - Card titles
Body: 1rem / 16px - Main text
Small: 0.875rem / 14px - Labels, captions
Tiny: 0.75rem / 12px - Footnotes
```

### Color System
```
Primary: Salem Gold (#C4A053) - Actions, highlights
Secondary: Salem Navy (#1B3B5F) - Headers, emphasis
Success: #10B981 - Positive indicators
Warning: #F59E0B - Caution states
Danger: #EF4444 - Risk, negative scenarios
Neutral Gray Scale: #F9FAFB → #111827 (9 steps)
```

### Component Library

#### Cards
```css
- Elevated: box-shadow, rounded-12px, padding: 20px
- Flat: border: 1px, rounded-8px, padding: 16px  
- Hover: subtle lift animation
- States: default, hover, active, disabled
```

#### Buttons
```css
Primary: Gold gradient, white text, 12px padding
Secondary: White bg, gold border, gold text
Tertiary: Text only, gold on hover
Sizes: small (32px), medium (40px), large (48px)
Icons: left/right positioned, 4px spacing
```

#### Inputs
```css
Text/Number: 40px height, rounded-8px, border-focus animation
Sliders: Gold accent, value tooltip on hover
Dropdowns: Searchable for long lists
Toggle: iOS-style switch
Radio/Checkbox: Custom styled with Salem colors
```

#### Data Tables
```css
Header: Navy background, white text, sticky on scroll
Rows: Alternating subtle gray, hover highlight
Cells: Right-align numbers, formatted (currency/percent)
Actions: Inline icons (edit, delete, duplicate)
Sorting: Arrows in headers
Filtering: Top row with input fields
```

#### Charts (Altair Configuration)
```javascript
{
  axis: {
    labelFont: "Inter",
    titleFont: "Inter",
    labelFontSize: 12,
    titleFontSize: 14,
    gridColor: "#E5E7EB",
    domainColor: "#9CA3AF"
  },
  legend: {
    labelFont: "Inter",
    titleFont: "Inter",
    labelFontSize: 12,
    titleFontSize: 13
  },
  tooltip: {
    background: "white",
    borderColor: SALEM_GOLD,
    fontSize: 13,
    padding: 8
  }
}
```

## Interaction Patterns

### Progressive Disclosure
- Accordion sections start collapsed (except critical inputs)
- "Show Advanced" toggles for expert features
- Inline expansion for details
- Modal overlays for complex configurations

### Feedback & Validation
- Inline validation (red underline + message)
- Warning toasts for unusual values
- Success confirmation after saves
- Loading states with progress indicators
- Optimistic UI updates

### Keyboard Navigation
- Tab through all interactive elements
- Enter to submit forms
- Escape to close modals
- Arrow keys in tables
- Cmd/Ctrl+S to save
- Cmd/Ctrl+E to export

### Responsive Breakpoints
```
Mobile: < 640px (read-only, PDF export)
Tablet: 640px - 1024px (optimized for client meetings)
Desktop: > 1024px (full feature set)
Wide: > 1440px (side-by-side comparisons)
```

## Risk Visualization Enhancements

### 1. Success Probability Gauge
- Large circular gauge (200px)
- Color-coded: Red <60%, Yellow 60-80%, Green >80%
- Context text: "X% of scenarios succeed"
- Benchmark comparison line

### 2. Downside Protection Card
```
┌─────────────────────────────┐
│ DOWNSIDE PROTECTION         │
├─────────────────────────────┤
│ P10 Ending Value:  $X.XXM   │
│ Shortfall Prob:    XX%      │
│ Max Drawdown:      -XX%     │
│ Recovery Time:     X years  │
└─────────────────────────────┘
```

### 3. Sequence Risk Indicator
- First 5-year return distribution
- Impact on final outcome
- "Safe withdrawal" visualization

### 4. Cash Flow Coverage Timeline
```
Years with Positive Balance:
[████████████████░░] 25/30 years
```

### 5. Failure Mode Analysis
- When do failures occur? (histogram)
- What causes failures? (attribution)
- How severe? (depth of shortfall)

## Accessibility Checklist

- [ ] ARIA labels on all interactive elements
- [ ] Sufficient color contrast (WCAG AA minimum)
- [ ] Keyboard navigation throughout
- [ ] Screen reader tested
- [ ] Focus indicators visible
- [ ] Error messages programmatically associated
- [ ] Chart alternatives (data tables)
- [ ] Skip navigation links
- [ ] Semantic HTML structure
- [ ] Alt text on images/icons

## Implementation Phases

### Phase 1: Tab Navigation & Overview (Week 1)
- Implement tab structure with Streamlit
- Build Overview dashboard with key metrics
- Create Risk Summary cards
- Set up session state management

### Phase 2: Reorganize Inputs (Week 1-2)
- Collapsible accordion sections
- Input validation framework
- Preset configurations
- Save/load client profiles

### Phase 3: Enhanced Visualizations (Week 2-3)
- Success probability gauge
- Improved fan charts with better tooltips
- Downside protection cards
- Cash flow visualizations

### Phase 4: Scenario Comparison (Week 3-4)
- Stress test builder UI
- Multi-scenario overlay charts
- Comparison tables
- Allocation analyzer

### Phase 5: Reports & Export (Week 4)
- Report builder interface
- PDF generation improvements
- Export options
- Saved reports management

### Phase 6: Polish & Testing (Week 5)
- Accessibility audit
- Performance optimization
- User testing with advisors
- Documentation

## Success Metrics

### User Experience
- Time to complete full analysis: < 10 minutes
- Clicks to key insights: < 3
- User satisfaction: > 4.5/5
- Error rate: < 2%

### Technical
- Page load: < 2 seconds
- Simulation run: < 5 seconds (1000 scenarios)
- Accessibility score: > 95
- Mobile usability: > 90

### Business
- Report generation time: < 30 seconds
- Client comprehension: > 85%
- Advisor adoption: > 90%

## Next Steps

1. Review and approve this redesign plan
2. Set up component library structure
3. Begin Phase 1 implementation
4. Schedule weekly progress reviews
5. Plan user testing sessions with 3-5 advisors

---

**Prepared by**: AI UX Engineer
**Date**: December 2, 2025
**Version**: 1.0
