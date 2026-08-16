# Implementation Plan - Gemini Style Redesign and Progress Pacing Fix

## Goal Description
We will pivot the application's layout from the previous iOS Liquid Glass design to a **Google Gemini-style aesthetic** featuring soft, drifting multi-color background blobs, clean Material 3-like rounded controls, and soft shadows instead of blurred/frosted panels. Additionally, we will fix the simulated progress pacing by making it highly irregular in timing and steps, matching a more organic feeling while still respecting the ease-out deceleration curve and finishing exactly on API response completion.

---

## User Review Required

> [!IMPORTANT]
> The iOS glassmorphism elements (`backdrop-filter`, `.glass`, `.glass-card`, `.glass-btn-*`, etc.) will be completely removed from `index.css` and replaced with Gemini-style UI tokens.

---

## Proposed Changes

### Component: Frontend Styling & Layout

#### [MODIFY] [index.css](file:///d:/Desktop/Projects/Research%20Assistant/frontend/src/index.css)
- Remove all `backdrop-filter`, liquid-glass color/blur tokens, and deprecated `.glass-card`, `.glass-btn-primary`, `.glass-btn-secondary`, `.glass-input`, and `.glass-slider` classes.
- Introduce a Gemini-style design token system under `@theme`:
  - A signature multi-color gradient (`--gradient-gemini`) for buttons, active tracks, and highlight states (using Gemini's purple/blue/pink/orange blend).
  - Background surface variables (`--color-surface-bg`) utilizing soft white for light mode and deep charcoal (e.g., `#121214` / `#1e1e24`) for dark mode.
  - Very generous border-radii: Fully rounded pill-shapes (`border-radius: 9999px`) for buttons/inputs, and moderate card rounding (`border-radius: 20px` to `24px`).
- Style the `body` with a beautiful CSS-based floating color blobs animation (soft, slowly moving radial gradient blobs that drift and scale) to provide a fluid, alive background.
- Build clean, solid components with soft elevation (`box-shadow: 0 4px 30px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02)`) instead of frosted glass.
- Define a beautiful loading shimmer state using an animated gradient shimmer for progress/assembling screens.
- Revamp the sliders: custom-styled track with signature gradient active portions, and larger touch thumbs that smoothly scale up on hover/interaction.

#### [MODIFY] [Header.tsx](file:///d:/Desktop/Projects/Research%20Assistant/frontend/src/components/Header.tsx)
- Restyle the header container to sit on a clean, solid, soft elevation background with pill-like styling to blend with the Gemini design language.

#### [MODIFY] [ResearchSetup.tsx](file:///d:/Desktop/Projects/Research%20Assistant/frontend/src/components/ResearchSetup.tsx)
- Update inputs, textarea, sliders, cards, and buttons to use the new pill-shaped layout and Gemini gradient styling.

#### [MODIFY] [AnalystReview.tsx](file:///d:/Desktop/Projects/Research%20Assistant/frontend/src/components/AnalystReview.tsx)
- Restyle the review panel, cards, and guidance text area.

#### [MODIFY] [AnalystCard.tsx](file:///d:/Desktop/Projects/Research%20Assistant/frontend/src/components/AnalystCard.tsx)
- Restyle cards to have Material 3 rounding, soft shadows, and clean borders.

#### [MODIFY] [ResearchProgress.tsx](file:///d:/Desktop/Projects/Research%20Assistant/frontend/src/components/ResearchProgress.tsx)
- Adjust the layout and step indicators, adding a soft animated gradient shimmer instead of a plain spinner where applicable.

#### [MODIFY] [FinalReport.tsx](file:///d:/Desktop/Projects/Research%20Assistant/frontend/src/components/FinalReport.tsx)
- Style surrounding chrome, action buttons, metadata blocks, and collapsible detail disclosures. Ensure that the markdown text body remains clear and readable without gradients.

### Component: Progress Pacing Logic

#### [MODIFY] [useSimulatedProgress.ts](file:///d:/Desktop/Projects/Research%20Assistant/frontend/src/hooks/useSimulatedProgress.ts)
- Refactor the simulated progress loop:
  - Replace the frame-by-frame increment with a random scheduling interval using `setTimeout`.
  - The interval between progress updates will randomly vary between **200ms - 400ms** (fast ticks) and **1.5s - 3.0s** (long pauses).
  - The percentage increment per update will vary randomly too (e.g. between **0.5%** and **8.0%**), while still conforming to an eased/decelerating curve so it slows down as it approaches the 90% cap.
  - Keep the completion animation (fast sweep from current progress to 100% when API finishes).

---

## Verification Plan

### Automated Tests
We will verify TypeScript and build compilation:
- `npm run build` inside `frontend/`

### Manual Verification
- We will start the backend server (`start_api.sh` or Python command) and the Vite frontend dev server.
- We will load the app via the `browser_subagent` and step through all 5 screens:
  1. Input form
  2. Assembling Analyst Panel
  3. Analyst Panel Review
  4. Research in Progress (observing the irregular pacing and capturing snapshots at ~10%, ~50%, and ~95%)
  5. Final Report
- We will capture real screenshots of all these states using the browser tool and place them in the walkthrough.
