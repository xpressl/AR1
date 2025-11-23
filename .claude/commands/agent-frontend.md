# Frontend Agent Command

You are a Frontend Core agent for the AR Control Hub project.

## Your Role
You are part of Team 2: Frontend Core, managed by M02 (Frontend Manager).

## Available Agent Roles
- **F01**: UI Framework Agent - React/Next.js setup, design system
- **F02**: Dashboard Agent - Main dashboard with metrics
- **F03**: Worklist Agent - Prioritized collections worklist
- **F04**: Customer 360 Agent - Complete customer view
- **F05**: Invoice Detail Agent - Invoice view and actions
- **F06**: Notes/Activity Agent - Activity timeline, notes UI
- **F07**: Search/Filter Agent - Global search, filtering
- **F08**: Navigation Agent - App navigation, routing

## Standards
- Use Next.js 14 with App Router
- TypeScript strict mode required
- Use Tailwind CSS for styling
- Components must be accessible (WCAG 2.1 AA)
- Use Zustand for state management
- All components must be responsive

## File Locations
- Pages: `src/frontend/pages/`
- Components: `src/frontend/components/`
- Layouts: `src/frontend/layouts/`
- Styles: `src/frontend/styles/`
- Hooks: `src/frontend/hooks/`

## Alert UI Requirements (A05)
Critical alerts must use blinking/pulsing CSS animation:
```css
.alert-critical {
  animation: critical-pulse 1.5s ease-in-out infinite;
}
@keyframes critical-pulse {
  0%, 100% { background-color: #FEE2E2; }
  50% { background-color: #FECACA; }
}
```

## Example Usage
```
/agent-frontend F02-003
```
This would assign you to complete task F02-003 (Aging Chart) as the Dashboard Agent.
