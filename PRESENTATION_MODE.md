# Presentation Mode - Financial Advisor Client Presentations

## Overview

Presentation Mode is a full-screen, client-facing presentation layer designed specifically for financial advisors to deliver professional portfolio analysis presentations during client meetings, whether in-person, via Zoom, or on iPads.

## Features

### ✨ Core Capabilities

- **Full-Screen Presentation**: Immersive, distraction-free presentation environment
- **Professional Dark Theme**: High-contrast Salem-branded theme optimized for projectors and screen sharing
- **Keyboard Navigation**: Arrow keys, spacebar, Home/End, and ESC for seamless control
- **8 Modular Slides**:
  1. **Overview** - Client introduction and meeting agenda
  2. **Plan Summary** - Current portfolio and planning parameters
  3. **Portfolio Projection** - Monte Carlo simulation results
  4. **Stress Tests** - Historical scenario analysis
  5. **Asset Allocation** - Investment mix breakdown
  6. **Cash Flows** - Income and spending timeline
  7. **Key Considerations** - Risk factors and mitigation
  8. **Next Steps** - Action items and follow-up

### 🎯 Advisor Features

- **Speaker Notes Panel** (Ctrl+N): Private advisor notes not visible to clients
- **Compliance Mode Toggle**: Hide performance history and restricted analytics
- **Auto-Hide Controls**: UI controls fade after 3 seconds of inactivity
- **Export Options**: PDF, PowerPoint, and high-resolution PNG exports
- **Live Data Integration**: All metrics auto-update from latest simulation results

### 🎨 Design System

**Theme Configuration** (`presentationTheme.ts`):
- Salem brand colors (Navy #0F3B63, Gold #B49759)
- Typography scale optimized for readability from distance
- 8px spacing system for consistent layout
- High-contrast chart colors with accessibility in mind

**Client-Friendly Language**:
- "Monte Carlo" → "Portfolio Projection"
- "Volatility" → "Market Fluctuation"
- "Depletion" → "Portfolio Exhaustion"
- All technical terms translated to advisor-appropriate language

## Usage

### Entering Presentation Mode

1. Run a Monte Carlo simulation from the Inputs page
2. Click the **"Presentation Mode"** button in the header (gold button with Presentation icon)
3. Full-screen presentation will launch automatically

### Navigation

| Action | Keys |
|--------|------|
| Next Slide | `→` `Space` `Page Down` |
| Previous Slide | `←` `Page Up` |
| First Slide | `Home` |
| Last Slide | `End` |
| Exit Presentation | `ESC` |
| Toggle Speaker Notes | `Ctrl+N` |

### Controls

- **Slide Indicators**: Click any dot to jump to specific slide
- **Slide Counter**: Shows current position (e.g., "3 / 8")
- **Compliance Mode**: Eye icon toggles restricted content visibility
- **Speaker Notes**: File icon shows/hides advisor-only notes
- **Export Menu**: Download icon provides export options
- **Exit**: X button returns to main application

## Technical Architecture

### File Structure

```
frontend/src/presentation/
├── PresentationMode.tsx          # Main container component
├── presentationTheme.ts          # Theme configuration
└── slides/
    ├── OverviewSlide.tsx         # Opening slide
    ├── PlanSummarySlide.tsx      # Plan overview
    ├── MonteCarloSlide.tsx       # Simulation results
    ├── StressTestsSlide.tsx      # Scenario analysis
    ├── AssetAllocationSlide.tsx  # Investment mix
    ├── CashFlowsSlide.tsx        # Income/spending
    ├── KeyRisksSlide.tsx         # Risk factors
    └── NextStepsSlide.tsx        # Action items
```

### Performance Optimizations

- **Lazy Loading**: Slides load on-demand using React.lazy()
- **Suspense Boundaries**: Smooth loading states between slides
- **Auto-Hide Controls**: Reduces UI distraction during presentation
- **Optimized Re-renders**: Memoized components and callbacks
- **Lightweight Bundle**: Minimal dependencies for fast load times

### State Management

Presentation Mode integrates with the existing Zustand store:
- `clientInfo`: Client demographic data
- `simulationResults`: Monte Carlo output
- `hasRunSimulation`: Controls Presentation Mode access

### Responsive Design

- **Conference Rooms**: Optimized for 1920x1080 projectors
- **Zoom Sharing**: High contrast for screen compression
- **iPads**: Touch-friendly controls and readable text
- **Adaptive Scaling**: Content scales to viewport dimensions

## Customization

### Adding New Slides

1. Create new slide component in `slides/` directory:
```tsx
import React from 'react';
import { presentationTheme } from '../presentationTheme';

const MyCustomSlide: React.FC<any> = ({ clientInfo, simulationResults, complianceMode }) => {
  return (
    <div style={{ padding: '5vh 5vw' }}>
      <h1 style={{ ...presentationTheme.typography.slideTitle, color: presentationTheme.colors.gold }}>
        My Custom Slide
      </h1>
      {/* Slide content */}
    </div>
  );
};

export default MyCustomSlide;
```

2. Add to slides array in `PresentationMode.tsx`:
```tsx
const slides = [
  // ... existing slides
  { id: 'custom', title: 'Custom Analysis', Component: MyCustomSlide },
];
```

### Customizing Theme

Edit `presentationTheme.ts` to modify:
- **Colors**: Update `colors` object for branding
- **Typography**: Adjust `typography` scales for readability
- **Spacing**: Modify `spacing` system for layout
- **Charts**: Configure `charts` object for visual styling

### Speaker Notes

Update speaker notes templates in `presentationTheme.ts`:
```typescript
export const speakerNotes = {
  myCustomSlide: [
    'Key talking point 1',
    'Key talking point 2',
    'Transition to next topic',
  ],
};
```

## Export Functionality

### PDF Export (Planned)
- Generates multi-page PDF with all slides
- Includes client branding and footer
- Preserves charts and formatting

### PowerPoint Export (Planned)
- Creates `.pptx` file with editable slides
- Maintains theme consistency
- Allows post-meeting customization

### PNG Export (Planned)
- High-resolution images of each slide
- Suitable for email attachments
- 1920x1080 or custom dimensions

## Accessibility

- **Keyboard Navigation**: Full control without mouse
- **High Contrast**: WCAG AA compliant color ratios
- **Screen Reader Support**: Semantic HTML and ARIA labels
- **Focus Management**: Clear focus indicators for navigation

## Best Practices

### Before the Meeting
1. Run simulation and review results
2. Customize speaker notes for client specifics
3. Test presentation mode on target device
4. Have backup PDF export ready

### During the Meeting
1. Start with Overview slide to set context
2. Use speaker notes panel for talking points
3. Enable Compliance Mode if required
4. Allow time for questions on each slide

### After the Meeting
1. Export presentation for client records
2. Note any required follow-ups
3. Schedule next review meeting

## Troubleshooting

### Presentation Mode Button Not Visible
- Ensure a simulation has been run successfully
- Check that `hasRunSimulation` is true in store

### Slides Not Loading
- Check browser console for errors
- Verify all slide components are properly exported
- Ensure simulation data is available

### Controls Not Auto-Hiding
- Move mouse to trigger timer reset
- Check for console errors blocking event listeners

### Export Not Working
- Export functionality is placeholder (implementation pending)
- Check future updates for full export support

## Future Enhancements

- [ ] Advanced chart animations and reveals
- [ ] PDF/PowerPoint/PNG export implementation
- [ ] Custom branding per advisor
- [ ] Client-specific slide templates
- [ ] Video recording capability
- [ ] Interactive chart drill-downs
- [ ] Multi-presenter mode
- [ ] Presentation analytics tracking

## Development

### Running in Development
```bash
cd frontend
npm run dev
```

### Building for Production
```bash
npm run build
```

### Testing
- Navigate to `/presentation` after running simulation
- Test keyboard shortcuts
- Verify speaker notes panel
- Check compliance mode toggle
- Test export menu interactions

## Support

For technical support or feature requests:
- Review inline code comments
- Check component documentation
- Contact development team

---

**Version**: 1.0.0  
**Last Updated**: December 2025  
**Developed for**: Salem Investment Counselors  
**Framework**: React 18 + TypeScript + Vite
