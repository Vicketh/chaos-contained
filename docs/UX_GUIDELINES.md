# UX Guidelines

## Design Principles

### ADHD-Friendly Interface

1. **Minimal Visual Clutter**
   - Use clean layouts with plenty of white space
   - Group related items logically
   - Avoid unnecessary decorative elements

2. **Color Scheme**
   - Primary: Light Blue (#A2CFF2)
   - Secondary: Cream (#FFF8E1)
   - Accent: Pastel Green (#C7E8CA)
   - Use colors consistently for specific actions/states

3. **Typography**
   - Primary Font: Poppins
   - Secondary Font: Nunito Sans
   - Ensure readable font sizes (minimum 16px for body text)
   - Use clear hierarchy with headings

### Interaction Design

1. **Navigation**
   - Keep navigation shallow (max 2-3 levels deep)
   - Provide clear back buttons
   - Use bottom navigation for main sections

2. **Task Management**
   - Simple task creation flow
   - Clear visual feedback for completion
   - Easy rescheduling with drag-and-drop

3. **Focus Mode**
   - Minimal UI during focus sessions
   - Clear timer display
   - Gentle transitions between states

## Component Guidelines

### Buttons
- Minimum touch target: 44x44 pixels
- Clear hover/active states
- Use icons with labels for important actions

### Cards
- Rounded corners (12px radius)
- Subtle shadows
- Clear hierarchy of information

### Forms
- Single column layout
- Inline validation
- Clear error messages
- Autofocus on first field

### Notifications
- Non-intrusive design
- Clear but gentle sound cues
- Option to snooze/reschedule

## Animations

### Transitions
- Smooth, natural transitions (300ms duration)
- Avoid flashy or distracting animations
- Use AnimatedContainer for subtle changes

### Feedback
- Subtle scale animation for buttons (1.02x)
- Gentle fade transitions
- Progress indicators for loading states

## Dark Mode

### Colors
- Background: #121212
- Surface: #1E1E1E
- Primary Text: #FFFFFF (87% opacity)
- Secondary Text: #FFFFFF (60% opacity)

### Contrast
- Maintain WCAG AA compliance
- Test all color combinations
- Ensure readability in both modes

## Accessibility

### Touch Targets
- Minimum size: 44x44 pixels
- Adequate spacing between elements
- Clear focus indicators

### Text
- Support dynamic text sizing
- Maintain proper contrast ratios
- Use semantic HTML elements

### Screen Readers
- Meaningful labels for all interactive elements
- Proper heading hierarchy
- Clear navigation structure