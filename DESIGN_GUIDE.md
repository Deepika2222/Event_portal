# 🎨 UI Preview & Design Guide

## Color Scheme

```
Primary Blue:    #007bff  (Main brand color)
Dark Blue:       #0056b3  (Hover/Active states)
Success Green:   #28a745  (Positive actions)
Danger Red:      #dc3545  (Errors/Warnings)
Warning Yellow:  #ffc107  (Alerts)
Light Gray:      #f8f9fa  (Background)
Dark Gray:       #6c757d  (Secondary text)
Dark Text:       #212529  (Main text)
```

---

## Typography

- **Font Family**: Segoe UI, Tahoma, Geneva, Verdana, sans-serif
- **Headings**: Bold, larger size, primary blue color
- **Body Text**: Regular weight, dark gray
- **Labels**: Medium weight, dark text
- **Helper Text**: Small, secondary gray

---

## Components

### Navigation Bar
```
┌─────────────────────────────────────────────────────────────┐
│ 📅 Event Portal    Home | Events | Register | Feedback     │
└─────────────────────────────────────────────────────────────┘
```
- Gradient blue background
- White text
- Fixed on all pages
- Responsive hamburger menu on mobile

### Page Headers
```
┌─────────────────────────────────────────────────────────────┐
│ 📅 All Events                                               │
│ Explore all available events and find something you're     │
│ interested in                                               │
└─────────────────────────────────────────────────────────────┘
```

### Forms
```
┌─────────────────────────────────────────────────────────────┐
│ ✍️ Register for an Event                                    │
│                                                              │
│ Registration ID *                                            │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Enter your registration ID (numbers only)              │ │
│ └────────────────────────────────────────────────────────┘ │
│ Must contain only numbers                                   │
│                                                              │
│ Select Event *                                               │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ -- Choose an event --                              ▼  │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                              │
│ [Register Now]  [View All Events]                          │
└─────────────────────────────────────────────────────────────┘
```
- White background with subtle shadow
- Clear labels with helper text
- Consistent spacing between fields
- Prominent call-to-action buttons

### Tables
```
┌───────────────────────────────────────────────────────────────┐
│ Event ID │ Event Name │ Date │ Venue │ Capacity               │
├───────────────────────────────────────────────────────────────┤
│ #001     │ Tech Talk  │ ...  │ ...   │ 150                    │
│ #002     │ Workshop   │ ...  │ ...   │ 80                     │
└───────────────────────────────────────────────────────────────┘
```
- Blue header background
- Hover effects on rows
- Proper spacing and alignment
- Responsive on mobile

### Buttons
```
Primary:    [Register Now]  (Blue background, white text)
Success:    [Submit]        (Green background, white text)
Secondary:  [Cancel]        (Gray background, white text)
Link:       View Events     (Transparent with blue border)
```
- Smooth hover animations
- Elevation effect on hover
- Touch-friendly size
- Clear labels

### Alerts
```
Success: ✓ Registration Successful!
Error:   ⚠ Invalid Registration ID
Warning: ! Please select an event
Info:    ℹ No events available
```
- Colored backgrounds
- Icon indicators
- Clear messaging
- Dismissible or auto-hide

### Success Page
```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│                              ✓                              │
│                         Success!                            │
│                                                              │
│              Registration Successful!                       │
│                                                              │
│       [View Events]  [Back to Home]                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```
- Large checkmark icon
- Centered layout
- Clear success message
- Navigation options

### Error Page
```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│                              ⚠                              │
│                  Oops! Something went wrong                 │
│                                                              │
│              Database connection failed                     │
│                                                              │
│       [Back to Home]  [View Events]                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```
- Large warning icon
- Clear error description
- Recovery options

---

## Responsive Breakpoints

### Desktop (1200px+)
- Full width layouts
- Multi-column grids
- Sidebar navigation
- Large buttons and text

### Tablet (768px - 1199px)
- Adjusted spacing
- 2-column grids
- Optimized navigation
- Medium-sized buttons

### Mobile (< 768px)
- Single column
- Stacked buttons
- Full-width inputs
- Touch-friendly sizing
- Collapsible navigation

---

## Interactive Elements

### Form Inputs
- **Default**: Gray border, white background
- **Focus**: Blue border, subtle blue shadow
- **Error**: Red border, light red background
- **Success**: Green border (optional)

### Buttons
- **Default**: Blue background, white text
- **Hover**: Darker blue, lifted effect
- **Active**: Pressed effect
- **Disabled**: Gray, cursor not-allowed

### Links
- **Default**: Blue text, no underline
- **Hover**: Underline appears
- **Visited**: Can be styled (currently inherits)

---

## Spacing System

- **Extra Small**: 0.5rem (8px)
- **Small**: 1rem (16px)
- **Medium**: 1.5rem (24px)
- **Large**: 2rem (32px)
- **Extra Large**: 3rem+ (48px+)

---

## Shadow Effects

- **Subtle**: `0 0.125rem 0.25rem rgba(0, 0, 0, 0.075)`
- **Medium**: `0 1rem 3rem rgba(0, 0, 0, 0.175)`

---

## Animation & Transitions

- **Default Duration**: 0.3s
- **Easing**: ease (cubic-bezier(0.25, 0.46, 0.45, 0.94))
- **Properties**: color, background-color, border-color, box-shadow, transform

---

## Accessibility Features

- ✅ Semantic HTML (proper heading hierarchy)
- ✅ Form labels associated with inputs
- ✅ Color contrast ratios meet WCAG standards
- ✅ Focus states clearly visible
- ✅ Helper text for form fields
- ✅ Error messages associated with fields
- ✅ Mobile touch targets 44x44px minimum

---

## Icon Usage

- 📅 Calendar/Event related pages
- ✍️ Registration/Form pages
- ⭐ Feedback/Rating pages
- ✓ Success state
- ⚠ Error/Warning state
- ℹ Info/Details state
- 🏠 Home

---

## CSS Classes Available

```css
/* Typography */
.text-center
.text-muted

/* Spacing */
.mt-1, .mt-2, .mt-3, .mt-4  /* Margin top */
.mb-1, .mb-2, .mb-3, .mb-4  /* Margin bottom */

/* Buttons */
.btn
.btn-primary
.btn-success
.btn-secondary
.btn-link
.btn-block

/* Alerts */
.alert
.alert-success
.alert-danger
.alert-warning
.alert-info

/* Utilities */
.hidden
.container
.form-group
```

---

## Dark Mode (Future Enhancement)

Current design uses light theme. To implement dark mode:
1. Duplicate CSS variables with `@media (prefers-color-scheme: dark)`
2. Adjust colors for readability
3. Test contrast ratios
4. Add theme toggle button

---

**Design Guide Version**: 1.0
**Last Updated**: November 25, 2024
