# Icon Color Standardization Guide

## Overview
This guide documents the standardized color scheme for all icons in the Model Management System application to ensure consistency across all components.

## Icon Color Standards

### Action Icons

| Action | Icon | Color | Class | Usage |
|--------|------|-------|-------|-------|
| **Download** | `<Download />` | Green | `text-green-600 hover:text-green-900` | Downloading files, models, data |
| **Share** | `<Share />` | Blue | `text-blue-600 hover:text-blue-900` | Sharing content with others |
| **Edit/Settings** | `<Sliders />`, `<Settings />` | Purple | `text-purple-600 hover:text-purple-900` | Opening settings, calibration interface |
| **Report/Analytics** | `<FileBarChart />` | Orange | `text-orange-600 hover:text-orange-900` | Viewing reports, analytics |
| **Delete** | `<Trash2 />` | Red | `text-red-600 hover:text-red-900` | Deleting items |
| **View/File** | `<FileText />`, `<Eye />` | Blue | `text-blue-600 hover:text-blue-900` | Viewing files, documents |
| **Report Issue** | `<AlertTriangle />` | Orange | `text-orange-600 hover:text-orange-700` | Reporting problems |

### Status Icons

| Status | Icon | Color | Class | Usage |
|--------|------|-------|-------|-------|
| **Success/Completed** | `<CheckCircle />` | Green | `text-green-500/600` | Successful operations, completed tasks |
| **In Progress** | `<RefreshCw />`, `<Activity />` | Blue | `text-blue-500/600` | Ongoing operations |
| **Error/Failed** | `<AlertCircle />`, `<XCircle />` | Red | `text-red-500/600` | Errors, failures |
| **Warning/Pending** | `<AlertCircle />` | Yellow | `text-yellow-500/600` | Warnings, pending items |

## Implementation

### Using Theme Constants

Always use the centralized theme constants for icon colors:

```tsx
import { theme } from '../theme';

// For action icons
<button className={theme.iconColors.download}>
  <Download className="w-4 h-4" />
</button>

// For status icons
<CheckCircle className={theme.iconColors.success} />
```

### Available Theme Icon Colors

```typescript
theme.iconColors = {
  download: 'text-green-600 hover:text-green-900',
  share: 'text-blue-600 hover:text-blue-900',
  edit: 'text-purple-600 hover:text-purple-900',
  report: 'text-orange-600 hover:text-orange-900',
  delete: 'text-red-600 hover:text-red-900',
  view: 'text-blue-600 hover:text-blue-900',
  issue: 'text-orange-600 hover:text-orange-700',
  primary: 'text-purple-600 hover:text-purple-900',
  // Status colors
  success: 'text-green-600',
  info: 'text-blue-600',
  warning: 'text-yellow-600',
  error: 'text-red-600',
  neutral: 'text-gray-600',
}
```

## Component-Specific Usage

### MyModels.tsx
- ✅ Download: Green (correct)
- ✅ Share: Blue (correct)
- ✅ Edit (Sliders): Purple (correct)
- ✅ Report (FileBarChart): Orange (correct)
- ✅ Delete: Red (correct)

### ModelLibrary.tsx
- ✅ Download: Green (fixed from purple)
- ✅ Report Issue: Orange (correct)

### ReferenceDataLibrary.tsx
- ✅ Download: Green (correct)
- ✅ View (FileText): Blue (correct)
- ✅ Report Issue: Orange (correct)

### TestbenchLibrary.tsx
- ✅ Download: Green (correct)
- ✅ View (FileText): Blue (correct)
- ✅ Report Issue: Orange (correct)

### Reports.tsx
- ✅ Download: Green (correct)
- ✅ Report (FileBarChart): Orange (fixed from purple)

## Migration Checklist

When adding new icons or updating existing ones:

1. ✅ Check if the action type exists in `theme.iconColors`
2. ✅ Use the theme constant instead of hardcoding colors
3. ✅ Ensure hover states are included
4. ✅ Test that colors are consistent across all views (table/card/detail)
5. ✅ Verify the color makes semantic sense for the action

## Rationale

### Color Choices

- **Green for Download**: Positive action, getting something
- **Blue for Share/View**: Informational, non-destructive
- **Purple for Edit**: Primary brand color, important actions
- **Orange for Reports**: Attention-grabbing but not alarming
- **Red for Delete**: Destructive action, requires caution
- **Status colors**: Follow standard UI conventions (green=good, red=bad, etc.)

## Notes

- Always prefer theme constants over inline color classes
- When in doubt, check this guide or existing implementations
- Consistency is more important than perfect color choice
- Test hover states to ensure they're working properly