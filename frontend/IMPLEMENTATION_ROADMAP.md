# UI/UX Audit Implementation Roadmap
**Salem Investment Counselors - Portfolio Scenario Analysis Platform**

**Based on:** UI_UX_AUDIT_REPORT.md  
**Created:** December 4, 2025  
**Target Completion:** 6 weeks  
**Effort:** 1 senior frontend engineer

---

## Overview

This roadmap implements all 7 parts of the UI/UX audit in a staged approach, ensuring each phase builds on the previous one without breaking existing functionality.

### Success Criteria
- ✅ Zero inline styles across entire codebase
- ✅ 100% WCAG AA compliance
- ✅ Single unified design system
- ✅ Consistent component patterns
- ✅ Professional, cohesive user experience

---

## Phase 1: Foundation & Design System (Week 1)
**Goal:** Establish single source of truth for all design tokens

### Stage 1.1: Update Core Theme Tokens (Day 1)
**Priority:** 🔴 CRITICAL  
**Effort:** 4 hours  
**Files:**
- `src/theme/tokens.ts`

**Tasks:**
- [ ] Update colors for WCAG AA compliance
  - Change `text.tertiary` from `#6F767D` to `#8B949E`
  - Change `text.secondary` from `#B4B9C2` to `#C9D1D9`
  - Change `brand.gold` from `#B49759` to `#C4A76A`
  - Update all status colors (success, warning, error, info)
- [ ] Add new background colors
  - Update `background.base` from `#0A0C10` to `#0F1419`
  - Update `background.elevated` from `#12141A` to `#1A1F26`
  - Update `background.hover` from `#1A1D24` to `#252B33`
  - Update `background.border` from `#262A33` to `#34393F`
- [ ] Add chart color palette
  - Add equity, fixed, cash colors
  - Add P10-P90 percentile colors
- [ ] Run contrast checker to verify all combinations

**Acceptance Criteria:**
- All color values pass WCAG AA (4.5:1 minimum)
- TypeScript exports remain type-safe
- No breaking changes to existing token structure

### Stage 1.2: Sync Tailwind Configuration (Day 1)
**Priority:** 🔴 CRITICAL  
**Effort:** 2 hours  
**Files:**
- `tailwind.config.js`

**Tasks:**
- [ ] Import tokens directly from `theme/tokens.ts`
- [ ] Map all color tokens to Tailwind utilities
- [ ] Ensure spacing, typography, shadows sync
- [ ] Remove any hardcoded values in config
- [ ] Test Tailwind IntelliSense shows all tokens

**Acceptance Criteria:**
- `tailwind.config.js` imports from single source
- All design tokens accessible as Tailwind classes
- No duplicate value definitions

### Stage 1.3: Create Theme Utility Exports (Day 2)
**Priority:** 🔴 CRITICAL  
**Effort:** 3 hours  
**Files:**
- `src/theme/index.ts` (create)
- `src/utils/chartColors.ts` (create)

**Tasks:**
- [ ] Create `src/theme/index.ts` as central export
- [ ] Create chart color utilities
  - `getPercentileColor(percentile)`
  - `getChartGradients()`
  - `rechartsTheme` object
- [ ] Export formatters from theme
- [ ] Update all imports to use `@/theme`

**Acceptance Criteria:**
- Single import path for all theme values
- Chart utilities tested with all percentiles
- Documentation comments on all exports

### Stage 1.4: Audit & Mark Legacy Code (Day 2-3)
**Priority:** 🟡 MEDIUM  
**Effort:** 6 hours  
**Files:**
- All `.tsx` and `.css` files

**Tasks:**
- [ ] Run grep to find all inline styles: `grep -r "style={{" src/`
- [ ] Run grep to find all CSS variables: `grep -r "var(--salem-" src/`
- [ ] Run grep to find all hex colors: `grep -r "#[0-9A-Fa-f]{6}" src/`
- [ ] Create spreadsheet of all instances by file
- [ ] Add `// TODO: Migrate to design system` comments
- [ ] Prioritize files by impact (user-facing vs internal)

**Acceptance Criteria:**
- Complete inventory of legacy styling (estimate: 300+ instances)
- Files tagged with migration priority
- Baseline metrics established

### Stage 1.5: Eliminate salem-theme.css (Day 3-4)
**Priority:** 🔴 CRITICAL  
**Effort:** 8 hours  
**Files:**
- `src/styles/salem-theme.css` (delete)
- All components importing CSS variables

**Tasks:**
- [ ] Find all usages: `grep -r "var(--salem-" src/`
- [ ] Replace CSS variables with Tailwind classes
  - `var(--salem-navy-primary)` → `text-brand-navy`
  - `var(--salem-gold)` → `text-brand-gold`
  - `var(--salem-spacing-lg)` → `p-lg`
- [ ] Remove `salem-theme.css` import from `index.css`
- [ ] Delete `src/styles/salem-theme.css`
- [ ] Test all pages still render correctly

**Acceptance Criteria:**
- Zero references to `var(--salem-*)` in codebase
- `salem-theme.css` deleted
- Visual regression tests pass

### Stage 1.6: Create Theme Documentation (Day 4-5)
**Priority:** 🟢 LOW  
**Effort:** 4 hours  
**Files:**
- `src/theme/README.md` (create)

**Tasks:**
- [ ] Document all tokens with usage examples
- [ ] Create visual style guide (Storybook or markdown)
- [ ] Add migration guide for developers
- [ ] Document naming conventions
- [ ] Add accessibility notes (contrast ratios)

**Acceptance Criteria:**
- Comprehensive theme documentation
- Clear examples for all common patterns
- Developer onboarding guide

**Phase 1 Deliverables:**
- ✅ WCAG AA compliant design tokens
- ✅ Single source of truth (`theme/tokens.ts`)
- ✅ Zero CSS variables remaining
- ✅ Complete theme documentation

---

## Phase 2: Component Library (Week 2)
**Goal:** Create consistent, reusable components

### Stage 2.1: AnalysisTable Component (Day 6-7)
**Priority:** 🔴 CRITICAL  
**Effort:** 12 hours  
**Files:**
- `src/components/ui/AnalysisTable.tsx` (create)
- `src/components/ui/AnalysisTable.stories.tsx` (create)

**Tasks:**
- [ ] Create `AnalysisTable` component with props:
  - `columns: Column<T>[]`
  - `data: T[]`
  - `variant: 'default' | 'striped' | 'compact'`
  - `stickyHeader: boolean`
  - `caption?: string`
  - `emptyState?: ReactNode`
  - `loading?: boolean`
- [ ] Implement responsive design (horizontal scroll on mobile)
- [ ] Add loading skeleton state
- [ ] Add empty state handling
- [ ] Add sort functionality (optional)
- [ ] Create comprehensive Storybook stories
- [ ] Write unit tests

**Acceptance Criteria:**
- Component uses only design system tokens
- Fully accessible (ARIA labels, keyboard nav)
- Loading and empty states implemented
- 100% test coverage

### Stage 2.2: FormField Wrapper Component (Day 8)
**Priority:** 🔴 CRITICAL  
**Effort:** 6 hours  
**Files:**
- `src/components/forms/FormField.tsx` (create)
- `src/components/forms/FormField.stories.tsx` (create)

**Tasks:**
- [ ] Create `FormField` wrapper component
  - Label with required indicator
  - Optional help text
  - Error message display
  - Success state (green checkmark)
- [ ] Add proper ARIA attributes
- [ ] Style with design system tokens
- [ ] Create examples for all input types
- [ ] Write unit tests

**Acceptance Criteria:**
- Single component for all form field layouts
- Accessible (ARIA labels, error announcements)
- Works with all existing input components

### Stage 2.3: Chart Utilities & Helpers (Day 9)
**Priority:** 🔴 CRITICAL  
**Effort:** 6 hours  
**Files:**
- `src/utils/chartColors.ts` (expand)
- `src/utils/chartHelpers.ts` (create)

**Tasks:**
- [ ] Expand `chartColors.ts` with all utilities
- [ ] Create `getChartConfig()` for common Recharts props
- [ ] Create responsive chart wrapper
- [ ] Add tooltip styling utilities
- [ ] Add legend styling utilities
- [ ] Document all functions

**Acceptance Criteria:**
- All chart colors from design system
- Reusable configuration objects
- Documentation with examples

### Stage 2.4: Additional UI Components (Day 10)
**Priority:** 🟡 MEDIUM  
**Effort:** 8 hours  
**Files:**
- `src/components/ui/Tooltip.tsx` (create)
- `src/components/ui/LoadingSkeleton.tsx` (create)
- `src/components/ui/Modal.tsx` (create)
- `src/components/ui/Alert.tsx` (create)

**Tasks:**
- [ ] Create `Tooltip` component with proper positioning
- [ ] Create `LoadingSkeleton` for loading states
- [ ] Create `Modal` component (accessible, ESC to close)
- [ ] Create `Alert` component for notifications
- [ ] Create Storybook stories for all
- [ ] Write unit tests

**Acceptance Criteria:**
- All components use design system
- Fully accessible (keyboard nav, ARIA)
- Responsive on mobile

### Stage 2.5: Update Existing UI Components (Day 10)
**Priority:** 🟡 MEDIUM  
**Effort:** 4 hours  
**Files:**
- `src/components/ui/Button.tsx`
- `src/components/ui/Card.tsx`
- `src/components/ui/Badge.tsx`

**Tasks:**
- [ ] Review existing components for design system compliance
- [ ] Update focus states to match new tokens
- [ ] Ensure consistent sizing/spacing
- [ ] Add missing variants if needed
- [ ] Update tests

**Acceptance Criteria:**
- All UI components consistent
- No hardcoded values
- Focus states meet WCAG standards

**Phase 2 Deliverables:**
- ✅ AnalysisTable component ready
- ✅ FormField wrapper ready
- ✅ Chart utilities ready
- ✅ Full UI component library
- ✅ 100% design system compliance

---

## Phase 3: Table Migration (Week 3)
**Goal:** Migrate all tables to AnalysisTable component

### Stage 3.1: Monte Carlo Analytics Tables (Day 11-12)
**Priority:** 🔴 CRITICAL  
**Effort:** 12 hours  
**Files:**
- `src/components/monte-carlo/tables/OutcomeSummaryTable.tsx` (✅ already done)
- `src/components/monte-carlo/tables/LongevityStressTable.tsx` (✅ already done)
- `src/components/monte-carlo/tables/AnnualProbabilityRuinTable.tsx` (✅ already done)

**Tasks:**
- [ ] Verify existing refactored tables use design system
- [ ] Update any remaining inline styles
- [ ] Ensure consistent with AnalysisTable patterns
- [ ] Add loading states
- [ ] Add empty states

**Acceptance Criteria:**
- All Monte Carlo tables use design system
- Consistent styling across all three
- Loading and empty states working

### Stage 3.2: Salem Report Tables (Day 12-14)
**Priority:** 🔴 CRITICAL  
**Effort:** 16 hours  
**Files:**
- `src/components/salem-reports/CashFlowTable.tsx`
- `src/components/salem-reports/AssumptionsTable.tsx`
- `src/components/salem-reports/SummaryTable.tsx`
- All other Salem report table components

**Tasks:**
- [ ] Identify all Salem report tables
- [ ] Convert each to use `AnalysisTable` component
- [ ] Remove all inline styles and CSS variables
- [ ] Update column definitions
- [ ] Add proper formatting functions
- [ ] Test print styling
- [ ] Verify PDF export still works

**Acceptance Criteria:**
- All Salem tables use AnalysisTable
- Print/PDF export maintains quality
- No visual regressions

### Stage 3.3: Scenario & Input Tables (Day 15)
**Priority:** 🟡 MEDIUM  
**Effort:** 6 hours  
**Files:**
- Any tables in scenarios or inputs pages

**Tasks:**
- [ ] Audit all pages for table usage
- [ ] Migrate to AnalysisTable
- [ ] Ensure responsive behavior
- [ ] Test with various data sizes

**Acceptance Criteria:**
- 100% of tables use AnalysisTable
- Responsive on all screen sizes

**Phase 3 Deliverables:**
- ✅ All tables migrated to AnalysisTable
- ✅ Consistent table styling app-wide
- ✅ Zero inline table styles

---

## Phase 4: Form Migration (Week 4)
**Goal:** Migrate all forms to use FormField wrapper

### Stage 4.1: InputsPage Main Form (Day 16-17)
**Priority:** 🔴 CRITICAL  
**Effort:** 12 hours  
**Files:**
- `src/pages/InputsPage.tsx`

**Tasks:**
- [ ] Wrap all form inputs with `FormField` component
- [ ] Add proper labels, help text, error messages
- [ ] Implement field-level validation feedback
- [ ] Add success indicators (green checkmarks)
- [ ] Test form submission
- [ ] Ensure accessibility (keyboard nav, screen reader)

**Acceptance Criteria:**
- All inputs use FormField wrapper
- Validation feedback immediate and clear
- Accessible form flow

### Stage 4.2: Scenario Configuration Forms (Day 18)
**Priority:** 🟡 MEDIUM  
**Effort:** 6 hours  
**Files:**
- `src/pages/ScenariosPage.tsx`
- Any modal forms

**Tasks:**
- [ ] Migrate scenario forms to FormField
- [ ] Add validation
- [ ] Update styling
- [ ] Test edge cases

**Acceptance Criteria:**
- Consistent form patterns
- Proper validation

### Stage 4.3: Form Input Components (Day 19)
**Priority:** 🟡 MEDIUM  
**Effort:** 6 hours  
**Files:**
- `src/components/forms/NumberInput.tsx`
- `src/components/forms/DollarInput.tsx`
- `src/components/forms/PercentInput.tsx`
- All other form inputs

**Tasks:**
- [ ] Ensure all inputs have consistent styling
- [ ] Add focus states using design tokens
- [ ] Add disabled states
- [ ] Test accessibility

**Acceptance Criteria:**
- All inputs follow design system
- Consistent focus/disabled states

**Phase 4 Deliverables:**
- ✅ All forms use FormField
- ✅ Consistent form patterns
- ✅ Improved validation UX

---

## Phase 5: Chart Migration (Week 4-5)
**Goal:** Migrate all charts to use design system colors

### Stage 5.1: Core Monte Carlo Charts (Day 19-20)
**Priority:** 🔴 CRITICAL  
**Effort:** 10 hours  
**Files:**
- `src/components/monte-carlo/visualizations/EnhancedFanChart.tsx`
- `src/components/monte-carlo/visualizations/MonteCarloChart.tsx`
- `src/components/charts/FanChart.tsx`

**Tasks:**
- [ ] Replace all hardcoded colors with `getPercentileColor()`
- [ ] Use `rechartsTheme` for consistent styling
- [ ] Update gradients to use design system
- [ ] Ensure tooltips use theme colors
- [ ] Test chart responsiveness

**Acceptance Criteria:**
- No hardcoded hex colors
- Charts use percentile colors correctly
- Tooltips styled consistently

### Stage 5.2: Distribution & Histogram Charts (Day 21)
**Priority:** 🔴 CRITICAL  
**Effort:** 6 hours  
**Files:**
- `src/components/charts/TerminalWealthHistogram.tsx`
- `src/components/charts/DistributionChart.tsx`
- `src/components/charts/SuccessProbabilityChart.tsx`

**Tasks:**
- [ ] Update color schemes
- [ ] Use chart utilities
- [ ] Ensure accessibility (labels, contrast)
- [ ] Test with various data ranges

**Acceptance Criteria:**
- Design system colors throughout
- Accessible color contrasts

### Stage 5.3: Stress Test & Income Charts (Day 22)
**Priority:** 🟡 MEDIUM  
**Effort:** 6 hours  
**Files:**
- `src/components/charts/StressTestChart.tsx`
- `src/components/charts/IncomeTimelineChart.tsx`
- Any other chart components

**Tasks:**
- [ ] Migrate to design system colors
- [ ] Update legends and axes
- [ ] Test print/export quality

**Acceptance Criteria:**
- All charts using design system
- Print quality maintained

### Stage 5.4: Salem Report Charts (Day 23)
**Priority:** 🔴 CRITICAL  
**Effort:** 8 hours  
**Files:**
- All chart components in `src/components/salem-reports/`

**Tasks:**
- [ ] Replace all legacy colors
- [ ] Ensure charts match new design
- [ ] Test PDF export
- [ ] Verify print styling

**Acceptance Criteria:**
- Salem charts match modern design
- PDF export quality maintained

**Phase 5 Deliverables:**
- ✅ All charts use design system colors
- ✅ Color blind friendly palettes
- ✅ Consistent chart styling

---

## Phase 6: Page-Level Improvements (Week 5)
**Goal:** Improve page layouts, UX flows, accessibility

### Stage 6.1: Dashboard Page Refinement (Day 24)
**Priority:** 🔴 CRITICAL  
**Effort:** 6 hours  
**Files:**
- `src/pages/Dashboard.tsx`

**Tasks:**
- [ ] Improve empty state with clearer CTAs
- [ ] Add executive summary section
- [ ] Reorganize chart hierarchy
- [ ] Add "Key Takeaways" callout
- [ ] Improve microcopy
- [ ] Test mobile layout

**Acceptance Criteria:**
- Clear visual hierarchy
- Intuitive empty state
- Mobile responsive

### Stage 6.2: Analytics Page Reorganization (Day 24-25)
**Priority:** 🔴 CRITICAL  
**Effort:** 8 hours  
**Files:**
- `src/pages/MonteCarloAnalyticsPage.tsx`

**Tasks:**
- [ ] Add executive summary card at top
- [ ] Organize charts into tabs
  - Overview
  - Risk Analysis
  - Cash Flow
  - Detailed Tables
- [ ] Add "Key Takeaway" for each chart
- [ ] Improve loading states
- [ ] Test with various data sizes

**Acceptance Criteria:**
- Clear tab organization
- Executive summary prominent
- Better UX flow

### Stage 6.3: Navigation & Layout (Day 25)
**Priority:** 🟡 MEDIUM  
**Effort:** 6 hours  
**Files:**
- `src/components/layout/Sidebar.tsx`
- `src/components/layout/AppHeader.tsx`
- `src/components/layout/AppLayout.tsx`

**Tasks:**
- [ ] Add progress indicators to sidebar
- [ ] Improve mobile sidebar (drawer pattern)
- [ ] Ensure keyboard navigation works
- [ ] Add skip links for accessibility
- [ ] Test focus management

**Acceptance Criteria:**
- Mobile navigation functional
- Keyboard accessible
- Focus states visible

### Stage 6.4: Accessibility Audit & Fixes (Day 26-27)
**Priority:** 🔴 CRITICAL  
**Effort:** 12 hours  
**Files:**
- All pages and components

**Tasks:**
- [ ] Run axe DevTools on all pages
- [ ] Fix all WCAG AA violations
- [ ] Add ARIA labels where missing
- [ ] Test with screen reader (NVDA/JAWS)
- [ ] Test keyboard-only navigation
- [ ] Ensure proper heading hierarchy
- [ ] Add alt text to all images/charts
- [ ] Test color contrast with tools

**Acceptance Criteria:**
- Zero WCAG AA violations
- Screen reader compatible
- Keyboard accessible throughout

### Stage 6.5: Mobile Responsiveness (Day 27-28)
**Priority:** 🔴 CRITICAL  
**Effort:** 10 hours  
**Files:**
- All pages and components

**Tasks:**
- [ ] Test all pages on mobile devices
- [ ] Fix chart overflow issues
- [ ] Implement horizontal scroll indicators for tables
- [ ] Optimize form layouts for mobile
- [ ] Test touch interactions
- [ ] Ensure proper viewport settings
- [ ] Test on various screen sizes (320px to 1920px)

**Acceptance Criteria:**
- All pages usable on mobile
- Charts readable on small screens
- Tables scrollable with indicators
- Touch targets 44x44px minimum

**Phase 6 Deliverables:**
- ✅ Improved page layouts
- ✅ 100% WCAG AA compliance
- ✅ Full mobile responsiveness
- ✅ Better UX flows

---

## Phase 7: Salem Reports Overhaul (Week 6)
**Goal:** Replace legacy Salem reports with modern system

### Stage 7.1: Design New Report Template (Day 29)
**Priority:** 🔴 CRITICAL  
**Effort:** 6 hours  
**Files:**
- `src/components/reports/ReportTemplate.tsx` (create)

**Tasks:**
- [ ] Design modern report layout
- [ ] Create header/footer components
- [ ] Design section layouts
- [ ] Ensure print-friendly styling
- [ ] Add branding elements
- [ ] Test PDF generation

**Acceptance Criteria:**
- Professional, modern design
- Print/PDF optimized
- Consistent with main app

### Stage 7.2: Build ReportBuilder Component (Day 29-30)
**Priority:** 🔴 CRITICAL  
**Effort:** 10 hours  
**Files:**
- `src/components/reports/ReportBuilder.tsx` (create)
- `src/components/reports/ReportSection.tsx` (create)
- `src/components/reports/ReportChart.tsx` (create)

**Tasks:**
- [ ] Create `ReportBuilder` component
- [ ] Create `ReportSection` component
- [ ] Create chart wrapper for reports
- [ ] Add page break handling
- [ ] Add export functionality (PDF, PowerPoint, Excel)
- [ ] Test with various content lengths

**Acceptance Criteria:**
- Flexible report composition
- Multi-format export working
- Page breaks handled properly

### Stage 7.3: Migrate Salem Report Sections (Day 31-32)
**Priority:** 🔴 CRITICAL  
**Effort:** 12 hours  
**Files:**
- All files in `src/components/salem-reports/`
- `src/pages/SalemReportPage.tsx`

**Tasks:**
- [ ] Identify all Salem report sections
- [ ] Rebuild each section with new components
  - Executive Summary
  - Portfolio Projections
  - Risk Analysis
  - Cash Flow Analysis
  - Assumptions
- [ ] Remove all legacy components
- [ ] Test report generation
- [ ] Verify PDF export quality
- [ ] Test print styling

**Acceptance Criteria:**
- All Salem report sections modernized
- Legacy components deleted
- Export quality maintained

### Stage 7.4: Report Customization & Templates (Day 33)
**Priority:** 🟡 MEDIUM  
**Effort:** 6 hours  
**Files:**
- `src/components/reports/ReportTemplates.ts` (create)

**Tasks:**
- [ ] Create template system
  - Client-facing (minimal jargon)
  - Advisor-facing (full detail)
  - Executive summary only
- [ ] Add customization options
- [ ] Save custom templates
- [ ] Test all template variations

**Acceptance Criteria:**
- Multiple template options
- Customizable sections
- Templates saved/loaded

### Stage 7.5: Final Testing & Polish (Day 34)
**Priority:** 🔴 CRITICAL  
**Effort:** 8 hours  
**Files:**
- All report components

**Tasks:**
- [ ] Full regression testing
- [ ] Test all export formats
- [ ] Test with edge case data
- [ ] Verify branding consistency
- [ ] Get stakeholder approval
- [ ] Update documentation

**Acceptance Criteria:**
- All exports working
- Professional quality
- Stakeholder approved

**Phase 7 Deliverables:**
- ✅ Modern report system
- ✅ Legacy Salem reports deleted
- ✅ Multi-format export
- ✅ Professional quality reports

---

## Post-Implementation (Ongoing)

### Performance Optimization
- [ ] Run Lighthouse audits
- [ ] Optimize bundle size
- [ ] Implement code splitting
- [ ] Optimize chart rendering
- [ ] Add performance monitoring

### Documentation
- [ ] Update component documentation
- [ ] Create developer onboarding guide
- [ ] Document design system usage
- [ ] Create troubleshooting guide
- [ ] Record video tutorials

### Monitoring & Metrics
- [ ] Track design system adoption
- [ ] Monitor WCAG compliance
- [ ] Track component reuse
- [ ] Monitor load times
- [ ] Collect user feedback

---

## Risk Mitigation

### High-Risk Items
1. **Breaking Changes:** Each phase includes regression testing
2. **User Disruption:** Deploy behind feature flags when possible
3. **PDF Export Quality:** Dedicated testing for report generation
4. **Mobile Usability:** Test on real devices, not just simulators

### Rollback Plan
- Each phase can be rolled back independently
- Feature flags for major changes
- Comprehensive automated tests
- Staged rollout to users

### Communication Plan
- Weekly status updates to stakeholders
- Demo sessions at end of each phase
- Documentation updates with each phase
- Training sessions before final release

---

## Success Metrics

### Technical Metrics
| Metric | Baseline | Target | Phase |
|--------|----------|--------|-------|
| Inline styles | ~300 | 0 | 1-5 |
| CSS variables | ~150 | 0 | 1 |
| Hardcoded colors | ~200 | 0 | 1-5 |
| WCAG violations | ~40 | 0 | 6 |
| Component reuse | 30% | 80% | 2-7 |
| Bundle size | TBD | -20% | Post |
| Load time | ~2.5s | <1.5s | Post |
| Lighthouse score | TBD | >90 | Post |

### User Experience Metrics
- User satisfaction surveys (before/after)
- Task completion time (input → report)
- Error rate reduction
- Mobile usage increase
- Support ticket reduction

### Developer Experience Metrics
- Time to implement new feature (reduction)
- Design decision time (reduction)
- Code review comments (reduction)
- New developer onboarding time (reduction)

---

## Resource Requirements

### Personnel
- **1 Senior Frontend Engineer** (primary implementer)
- **1 Designer** (consultation, 4 hours/week)
- **1 QA Engineer** (testing support, 8 hours/week)
- **Product Owner** (approval, 2 hours/week)

### Tools
- Figma (design system documentation)
- Storybook (component library)
- axe DevTools (accessibility testing)
- Lighthouse (performance)
- BrowserStack (cross-browser testing)

### Environment
- Development environment
- Staging environment (for demos)
- Feature flags system
- Automated testing pipeline

---

## Timeline Summary

| Phase | Duration | Focus | Deliverable |
|-------|----------|-------|-------------|
| **Phase 1** | Week 1 | Foundation | Unified design system |
| **Phase 2** | Week 2 | Components | Component library |
| **Phase 3** | Week 3 | Tables | Consistent tables |
| **Phase 4** | Week 4 | Forms | Consistent forms |
| **Phase 5** | Week 4-5 | Charts | Consistent charts |
| **Phase 6** | Week 5 | Pages | Polish & accessibility |
| **Phase 7** | Week 6 | Reports | Modern reports |
| **Post** | Ongoing | Optimization | Performance & docs |

**Total Timeline:** 6 weeks + ongoing optimization

---

## Next Steps

### Immediate Actions (This Week)
1. [ ] Review and approve this roadmap
2. [ ] Set up project tracking (Jira/GitHub Projects)
3. [ ] Create feature flag system
4. [ ] Schedule kickoff meeting
5. [ ] Set up automated testing

### Phase 1 Kickoff (Week 1)
1. [ ] Create branch: `feat/design-system-foundation`
2. [ ] Begin Stage 1.1: Update core theme tokens
3. [ ] Schedule daily standups
4. [ ] Set up progress tracking

### Communication
- **Daily:** Quick standup (15 min)
- **Weekly:** Demo to stakeholders (30 min)
- **End of Phase:** Retrospective (1 hour)

---

## Appendix

### Useful Commands

**Find inline styles:**
```bash
grep -r "style={{" src/ | wc -l
```

**Find CSS variables:**
```bash
grep -r "var(--salem-" src/ | wc -l
```

**Find hardcoded colors:**
```bash
grep -rE "#[0-9A-Fa-f]{6}" src/ | wc -l
```

**Run accessibility audit:**
```bash
npm run test:a11y
```

**Run visual regression tests:**
```bash
npm run test:visual
```

### References
- [UI/UX Audit Report](./UI_UX_AUDIT_REPORT.md)
- [Design System Documentation](./src/theme/README.md)
- [WCAG 2.1 AA Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Recharts Documentation](https://recharts.org/)

---

**Document Version:** 1.0  
**Last Updated:** December 4, 2025  
**Owner:** Frontend Team  
**Status:** 📋 Ready for Implementation
