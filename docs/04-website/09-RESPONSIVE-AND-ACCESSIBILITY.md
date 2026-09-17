# Website Responsive Architecture & Accessibility Standards (WCAG 2.1 AA)

**Document ID:** `DOC-WEB-009`  
**Classification:** Website Architecture / Phase 3 Ergonomics & Accessibility  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-012](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-012), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [Design System Spec](file:///d:/Project_website/docs/04-website/08-DESIGN-SYSTEM-SPEC.md) | [Page Specifications](file:///d:/Project_website/docs/04-website/04-PAGE-SPECIFICATIONS.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Executive Mandate: Universal Usability & Inclusivity

The digital presence of `[STUDIO_NAME]` must be completely accessible and responsive to every founder, operator, and executive regardless of their device, screen size, assistive technology, or network environment.

The system targets strict compliance with **WCAG 2.1 Level AA** standards across all public and interactive surfaces.

---

## 2. Responsive Breakpoint Matrix & Layout Adaptation

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              VIEWPORT BREAKPOINT MATRIX                                │
├─────────────────┬──────────────┬───────────────────────────────────────────────────────┤
│ BREAKPOINT ID   │ VIEWPORT (px)│ PRIMARY LAYOUT & NAVIGATION BEHAVIOR                  │
├─────────────────┼──────────────┼───────────────────────────────────────────────────────┤
│ Mobile Small    │ 320px–480px  │ Single-column vertical flow. Persistent bottom CTA    │
│                 │              │ bar. Slide-over drawer navigation. 100% card width.   │
├─────────────────┼──────────────┼───────────────────────────────────────────────────────┤
│ Mobile Large /  │ 481px–768px  │ 1-to-2 column adaptive grid. Drawer navigation.       │
│ Tablet Portrait │              │ Opportunity Map cards switch to stacked dual-column.  │
├─────────────────┼──────────────┼───────────────────────────────────────────────────────┤
│ Tablet Landscape│ 769px–1024px │ Multi-column grid. Standard header navigation.        │
│ / Small Laptop  │              │ Stepper displays side-by-side question/preview.       │
├─────────────────┼──────────────┼───────────────────────────────────────────────────────┤
│ Desktop Standard│ 1025px–1440px│ Canonical 12-column container (max 1280px width).     │
│                 │              │ Full mega-menus. Persistent progress sidebar.         │
├─────────────────┼──────────────┼───────────────────────────────────────────────────────┤
│ Ultra-Wide      │ > 1440px     │ Centered content box (max-width bounded to 1440px)    │
│                 │              │ with balanced ambient background margins.             │
└─────────────────┴──────────────┴───────────────────────────────────────────────────────┘
```

### A. Mobile Interaction Ergonomics (320px–480px)
* **Persistent Bottom Conversion Bar**: Positioned above browser system controls with a high z-index, containing the universal trigger: **"Start With Your Problem"** (`BD-012`).
* **Zero Horizontal Scroll**: All containers use fluid percentage widths (`width: 100%; max-width: 100%`) with strict `box-sizing: border-box`.
* **Touch Target Sizing**: All interactive buttons, radio options, dropdown triggers, and links possess a minimum touch surface of **48px $\times$ 48px** to prevent tapping errors.
* **Virtual Keyboard Optimization**: Inputs use appropriate HTML5 `inputmode` and `autocomplete` attributes (`inputmode="email"`, `type="text"`) to present optimal mobile keyboards without layout distortion.

---

## 3. Web Accessibility Standards (WCAG 2.1 Level AA)

### A. Semantic HTML5 Hierarchy & Landmark Structure
* Every page enforces a single, authoritative `<h1>` tag containing the primary page subject.
* Strict heading hierarchy (`<h1>` $\rightarrow$ `<h2>` $\rightarrow$ `<h3>`) without skipped heading levels.
* Structural HTML5 landmarks across all templates:
  - `<header role="banner">`
  - `<nav role="navigation" aria-label="Primary">`
  - `<main role="main" id="main-content">`
  - `<footer role="contentinfo">`
* A **"Skip to Main Content"** link is placed as the first focusable element in the DOM, allowing screen-reader and keyboard users to bypass header navigation immediately.

### B. Contrast Ratios & Visual Ergonomics
* **Normal Text**: Minimum contrast ratio of **4.5:1** against underlying dark surface tokens.
* **Large Text (Display / H1 / H2 $\ge$ 24px)**: Minimum contrast ratio of **3:1**.
* **UI Components & Graphical Objects**: Form borders, interactive indicators, and status badges maintain at least **3:1** contrast against adjacent canvas surfaces.
* **Color Independence**: Color is never used as the sole indicator of state or validation. Error states include both an amber/red border and an explicit text explanation with an icon.

### C. Keyboard Navigation & Focus Management
* All interactive elements (buttons, inputs, links, modal triggers) are 100% navigable via `Tab`, `Shift+Tab`, `Enter`, and `Spacebar`.
* **Visible Focus Indicator**: A high-contrast, dual-layer focus ring (`2px solid color-brand-primary` with a `2px offset`) illuminates cleanly around currently focused elements. The system never applies `outline: none` without a custom focus indicator.
* **Focus Trap in Modals**: When the Lead Capture modal or mobile drawer navigation opens, keyboard focus is strictly trapped within the active dialog until closed via `Escape` or the close button.

### D. Screen Reader & Dynamic Content Accessibility (`aria-live`)
* **AI Stepper Streaming**: When the AI Discovery engine processes problem text or renders the Opportunity Map via HTMX, updates are broadcast to assistive technologies using:
  ```html
  <div role="status" aria-live="polite" class="sr-only">
    Synthesizing business problem into Opportunity Map...
  </div>
  ```
* **Icon Ergonomics**: Decorative icons and SVG glyphs are explicitly hidden from screen readers using `aria-hidden="true"`. Functional icon-only buttons include descriptive `aria-label` tags (e.g. `aria-label="Close discovery modal"`).

### E. Motion Sensitivity (`prefers-reduced-motion`)
* The entire platform respects operating system motion preferences:
  - When reduced motion is requested, all CSS transitions, spring transforms, and ambient pulses are disabled or converted to instantaneous opacity fades ($\le 50$ms).
