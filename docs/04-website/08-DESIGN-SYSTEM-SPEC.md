# Website Design System Specifications (Conceptual System Architecture)

**Document ID:** `DOC-WEB-008`  
**Classification:** Website Architecture / Phase 3 Design System Specification  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-006](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-006), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010), [BD-012](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-012), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [Visual Identity Direction](file:///d:/Project_website/docs/02-brand/06-VISUAL-IDENTITY-DIRECTION.md) | [Brand Guidelines](file:///d:/Project_website/docs/02-brand/07-BRAND-GUIDELINES.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Design System Philosophy: Calm, Intelligent Craftsmanship

The design system of `[STUDIO_NAME]` embodies **technical authority, intellectual calm, and radical clarity**. It avoids the juvenile tropes of AI consumer apps (garish neon gradients, floating 3D spheres, confetti micro-interactions) and the cold sterility of legacy enterprise portals.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               CORE DESIGN SYSTEM PILLARS                               │
├───────────────────────────────┬───────────────────────────────┬────────────────────────┤
│ 1. OBSIDIAN FOUNDATION        │ 2. RESTRAINED AMBIENT LIGHT   │ 3. RIGOROUS TYPOGRAPHY │
│ Deep charcoal/black canvases  │ Subtle radial indigo & violet │ High-legibility modern │
│ that reduce eye strain.       │ accents that focus attention. │ geometric/mono scales. │
├───────────────────────────────┼───────────────────────────────┼────────────────────────┤
│ 4. HUMAN-AI BADGING CLARITY   │ 5. INTENTIONAL MOTION         │ 6. ACCESSIBLE CONTRAST │
│ Unmistakable visual borders   │ Fast, spring-damped micro-    │ Strict WCAG 2.1 AA     │
│ between AI drafts and humans. │ transitions (150–250ms).      │ compliance across all. │
└───────────────────────────────┴───────────────────────────────┴────────────────────────┘
```

---

## 2. Conceptual Design Token Architecture

*(Note: Tokens are defined conceptually and structurally. Exact hex values and CSS classes remain implementation details to be bound in Phase 4 / CSS files).*

### A. Semantic Surface & Canvas Roles
* **`surface-canvas-base`**: The darkest foundational background (deep void / obsidian).
* **`surface-card-subtle`**: Layer 1 container elevation for content blocks, cards, and section containers.
* **`surface-card-elevated`**: Layer 2 container elevation for interactive popovers, dropdowns, and modals.
* **`border-hairline`**: Ultra-subtle divider border (10–15% opacity) providing structural separation without visual clutter.
* **`border-interactive`**: Active border state illuminating on hover or input focus.

### B. Functional Color Roles
* **`color-brand-primary`**: Deep electric indigo / royal purple anchoring the primary CTA: **"Start With Your Problem"** (`BD-012`).
* **`color-brand-glow`**: Low-opacity ambient back-glow used sparingly behind hero headers and spotlight cards.
* **`color-text-primary`**: Pristine off-white (high contrast, WCAG AAA compliant against dark canvases).
* **`color-text-secondary`**: Cool muted slate for supporting copy, explanations, and metadata.
* **`color-text-tertiary`**: Low-emphasis gray for labels, timestamps, and breadcrumbs.
* **`color-status-quickwin`**: Emerald green denoting immediate, high-impact ROI opportunities.
* **`color-status-strategic`**: Deep cyan denoting long-term core architectural builds.
* **`color-status-uncertainty`**: Warm amber denoting assumptions, unverified data, or system risks.

### C. Conceptual Typography Scale & Hierarchy
* **Display / Hero Headline**: Bold geometric display weight (3rem to 4.5rem fluid desktop), tight negative letter spacing (-0.02em) to convey executive authority.
* **Section Headlines (H2)**: Balanced semi-bold weight (2rem to 2.5rem), high legibility.
* **Subsection Titles (H3)**: Clean medium weight (1.25rem to 1.5rem).
* **Body Primary**: Balanced regular weight (1rem / 16px to 1.125rem / 18px), relaxed line-height (1.6 to 1.7) for fatigue-free long-form reading.
* **Technical Monospace**: Clean monospace family for schema properties, data types, architecture tokens, and code snippets.

### D. Spacing & Rhythm Grid (8-Point Base System)
* All paddings, margins, and gaps adhere to a uniform 8-point geometric scale:
  - `space-1` (4px), `space-2` (8px), `space-3` (12px), `space-4` (16px), `space-6` (24px), `space-8` (32px), `space-12` (48px), `space-16` (64px), `space-24` (96px).

---

## 3. Core Component Contracts

### A. Button Hierarchy
1. **Primary Action Button (Hero & Discovery CTA)**:
   - *Label*: **"Start With Your Problem"**
   - *Styling*: High-contrast `color-brand-primary` fill, crisp typography, subtle hover glow, generous padding (14px 28px).
2. **Secondary Ghost Button (Exploratory)**:
   - *Label*: *"Explore What We Build"* / *"How We Work"*
   - *Styling*: Transparent background with `border-hairline`, transitioning to subtle surface fill on hover.
3. **Tertiary Text Anchor**:
   - *Styling*: Understated link with directional arrow glyph (`➔`), illuminating on hover.

### B. Input & Form Fields (Discovery Stepper)
* **Textarea (Problem Input)**: Large, generous canvas with subtle placeholder text, gentle border focus ring, no jarring browser defaults.
* **Selection Radio Cards**: Large selectable cards with distinct active borders, accessible keyboard focus rings, and clear radio/checkbox icons.
* **Touch Targets**: Minimum **48px $\times$ 48px** bounding box on touch devices.

---

## 4. Distinctive Status Indicators: AI vs. Human Oversight (`BD-010`)

To enforce the studio's operating doctrine (*"AI handles leverage. Humans handle judgement"*), the design system specifies **two distinct, unmissable visual badges**:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        MANDATORY STATUS BADGE CONTRACTS                                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│   [✦ AI-GENERATED PRELIMINARY SPECIFICATION]                                           │
│   • Visual: Subtle dashed violet border, spark icon, muted ambient background.         │
│   • Meaning: Output generated by automated synthesis; subject to human review.         │
│                                                                                        │
│   [🛡️ ARCHITECT-VERIFIED & SIGNED SPECIFICATION]                                       │
│   • Visual: Solid emerald/cyan border, verified shield icon, crisp badge fill.         │
│   • Meaning: Reviewed, stress-tested, and commercially endorsed by a senior architect. │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Micro-Interactions, State Indicators & Motion Laws

1. **Duration Law**: All transitions, hover states, and dropdown reveals must execute within **150ms to 250ms**. Zero sluggish animations that slow down user navigation.
2. **Easing Law**: Use natural, decelerating cubic-bezier curves (e.g. ease-out) that mimic physical mass coming smoothly to rest.
3. **Skeleton Loading States**: During server-side HTMX requests or AI synthesis, show calm pulsing skeleton wireframes rather than chaotic spinning wheels.
4. **Accessible Motion Compliance**: The entire system strictly respects `@media (prefers-reduced-motion: reduce)` by immediately disabling all transform animations and fading smoothly instead.
