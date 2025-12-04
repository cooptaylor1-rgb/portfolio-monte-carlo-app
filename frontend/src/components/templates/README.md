# Page Templates

Reusable page layout templates that provide consistent structure, styling, and behavior across the application.

## AnalyticsPageTemplate

A comprehensive template for analytics and dashboard pages with built-in section navigation and export functionality.

### Features

- **Consistent Header**: Uses `SectionHeader` component with title, description, icon, and action buttons
- **Section Navigation**: Optional tabbed navigation between different content sections
- **Export Footer**: Built-in support for export actions (PDF, PNG, etc.)
- **Responsive Layout**: Adapts to different screen sizes with configurable max-width
- **Design System Integration**: Fully styled with theme tokens and Tailwind classes

### Usage Example

```tsx
import { AnalyticsPageTemplate } from '@/components/templates';
import { BarChart3, FileText, Image } from 'lucide-react';

function MyAnalyticsPage() {
  const [activeSection, setActiveSection] = useState('overview');

  return (
    <AnalyticsPageTemplate
      // Header
      title="Portfolio Analytics"
      description="Comprehensive analysis of your investment portfolio"
      icon={<BarChart3 size={28} />}
      
      // Section Navigation
      sections={[
        { id: 'overview', label: 'Overview' },
        { id: 'performance', label: 'Performance' },
        { id: 'risk', label: 'Risk Analysis' },
      ]}
      activeSection={activeSection}
      onSectionChange={setActiveSection}
      
      // Export Options
      exportActions={[
        {
          label: 'Export PDF',
          onClick: handleExportPDF,
          icon: <FileText size={20} />,
          variant: 'primary',
        },
        {
          label: 'Export Images',
          onClick: handleExportImages,
          icon: <Image size={20} />,
          variant: 'secondary',
        },
      ]}
      
      // Layout
      maxWidth="container"
      spacing="xl"
    >
      {/* Your content sections */}
      {activeSection === 'overview' && (
        <div className="space-y-lg">
          <h2 className="text-h2 font-display font-semibold text-accent-gold">
            Overview
          </h2>
          {/* Overview content */}
        </div>
      )}
      
      {activeSection === 'performance' && (
        <div className="space-y-lg">
          <h2 className="text-h2 font-display font-semibold text-accent-gold">
            Performance
          </h2>
          {/* Performance content */}
        </div>
      )}
    </AnalyticsPageTemplate>
  );
}
```

### Props

#### Header Configuration

- **title** (required): Main page title
- **description** (optional): Subtitle or description text
- **icon** (optional): Icon component (from lucide-react)
- **headerActions** (optional): Custom action buttons in header

#### Section Navigation

- **sections** (optional): Array of section objects with `id` and `label`
- **activeSection** (optional): Currently active section ID
- **onSectionChange** (optional): Callback when section changes

#### Export Options

- **exportActions** (optional): Array of export action objects
  - `label`: Button text
  - `onClick`: Click handler
  - `icon`: Optional icon
  - `variant`: Button style ('primary' | 'secondary' | 'tertiary')
  - `loading`: Show loading state
  - `disabled`: Disable button
- **showExportFooter** (optional): Show/hide export footer (default: true)

#### Layout Options

- **maxWidth** (optional): Maximum content width
  - `'container'`: 1440px (default)
  - `'content'`: 1200px
  - `'narrow'`: 800px
- **spacing** (optional): Vertical spacing between elements
  - `'sm'`: 16px
  - `'md'`: 24px
  - `'lg'`: 32px
  - `'xl'`: 48px (default)
- **className** (optional): Additional CSS classes

### Content Structure

Content within the template should follow this pattern:

```tsx
<div className="space-y-lg">
  {/* Section Header */}
  <div>
    <h2 className="text-h2 font-display font-semibold text-accent-gold mb-2">
      Section Title
    </h2>
    <p className="text-body text-text-secondary">
      Section description
    </p>
  </div>

  {/* Charts/Content */}
  <div id="chart-1" data-chart-export>
    <YourChartComponent />
  </div>

  <div id="chart-2" data-chart-export>
    <AnotherChartComponent />
  </div>
</div>
```

### Best Practices

1. **Use Design System Components**: Always use components from `@/components/ui` for consistency
2. **Follow Typography Scale**: Use Tailwind typography classes (text-h1, text-h2, text-body, etc.)
3. **Consistent Spacing**: Use spacing scale classes (space-y-lg, mb-4, etc.)
4. **Semantic HTML**: Use proper heading hierarchy (h1 → h2 → h3)
5. **Accessibility**: Include proper ARIA labels and keyboard navigation
6. **Export IDs**: Add `id` and `data-chart-export` to elements you want to export

### Design Tokens Reference

#### Colors
- **Background**: `bg-background-base`, `bg-background-elevated`
- **Text**: `text-text-primary`, `text-text-secondary`, `text-text-tertiary`
- **Accent**: `text-accent-gold`, `bg-accent-gold`
- **Status**: `text-status-success-base`, `text-status-warning-base`, `text-status-error-base`

#### Typography
- **Headings**: `text-h1`, `text-h2`, `text-h3`, `text-h4`
- **Body**: `text-body`, `text-small`, `text-micro`
- **Font**: `font-display` (headings), `font-sans` (body)
- **Weight**: `font-normal`, `font-medium`, `font-semibold`, `font-bold`

#### Spacing
- **Vertical**: `space-y-xs`, `space-y-sm`, `space-y-md`, `space-y-lg`, `space-y-xl`, `space-y-2xl`
- **Margin**: `mb-2`, `mb-4`, `mb-6`, `mb-8`
- **Padding**: `p-4`, `p-6`, `p-lg`

## Future Templates

Consider creating additional templates for:

- **DashboardTemplate**: Grid-based dashboard with metric cards
- **ReportTemplate**: Long-form report with print styling
- **FormPageTemplate**: Multi-step form with validation
- **ComparisonTemplate**: Side-by-side comparison views
