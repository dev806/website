# Website Analytics & Conversion Telemetry Dictionary

**Document ID:** `DOC-WEB-013`  
**Classification:** Website Architecture / Phase 3 Telemetry & Analytics Specification  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-004](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-004), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-006](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-006), [BD-012](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-012), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [Website Strategy](file:///d:/Project_website/docs/04-website/01-WEBSITE-STRATEGY.md) | [AI Discovery UX Flow](file:///d:/Project_website/docs/04-website/06-AI-DISCOVERY-UX-FLOW.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Analytics Principles & Privacy-by-Design Posture

The analytics architecture of `[STUDIO_NAME]` is engineered to understand **user intent, diagnostic friction, and conversion velocity** while upholding the highest standards of data privacy:

1. **Vendor Agnosticism (Phase 4 Evaluation)**: In adherence to governance rules, no specific proprietary analytics vendor (e.g. Google Analytics 4, PostHog, Plausible, Mixpanel) is hard-coded at this stage. Vendor selection remains a technical evaluation item for Phase 4.
2. **Strict Zero-PII Policy in Telemetry**: Names, email addresses, phone numbers, and raw confidential problem text are **never sent to client-side analytics trackers**. Telemetry records only categorical identifiers, step counts, and duration metrics.
3. **Cookie-Free Top-of-Funnel Tracking**: Event tracking operates without tracking cookies or cross-site fingerprinting scripts.

---

## 2. Universal Telemetry Event Dictionary

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              DISCOVERY FUNNEL EVENT PIPELINE                           │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  [page_view] ➔ [cta_clicked] ➔ [discovery_started] ➔ [discovery_stage_completed]      │
│                                                                │                       │
│                                                                ▼                       │
│  [lead_captured]  [lead_capture_started]  [opportunity_map_viewed]                   │
│         │                                                                              │
│         ▼                                                                              │
│  [blueprint_viewed] ➔ [estimate_viewed] ➔ [review_requested] / [sprint_inquired]      │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Event Specifications

| Event Name | Trigger Condition | Analytical Purpose | Event Properties (Payload) | Privacy Safeguard |
| :--- | :--- | :--- | :--- | :--- |
| **`page_view`** | Client loads any canonical route. | Measures traffic distribution and entry point velocity. | `page_path`, `referrer_domain`, `viewport_category` (`mobile`/`desktop`). | No URL query params containing sensitive tokens are tracked. |
| **`cta_clicked`** | User clicks any primary or secondary conversion button. | Identifies which conversion copy drives the highest click-through rate. | `cta_label` (e.g. `"Start With Your Problem"`), `cta_location` (`hero`, `nav`, `footer`). | Purely categorical; zero user input captured. |
| **`discovery_started`** | User focuses on Stage 1 input or clicks prompt chip. | Benchmarks initial diagnostic intent. | `entry_point` (`homepage_hero`, `nav_button`, `service_page`), `preseed_topic`. | Raw input text is excluded. |
| **`discovery_stage_completed`**| User advances from one discovery stage to the next. | Analyzes funnel drop-off and friction points across the 7 stages. | `stage_number` (1–7), `stage_name` (e.g. `"questions"`), `time_spent_seconds`. | Only tracks step completion timestamp and index. |
| **`opportunity_map_viewed`**| Stage 4 Opportunity Map renders in the viewport. | Verifies delivery of free, ungated diagnostic value (`BD-005`). | `opportunity_count`, `quick_win_count`, `top_category`. | Summarized count only; no client business details sent. |
| **`lead_capture_started`** | Progressive reveal modal or gate opens. | Measures conversion intent for deep architectural outputs. | `trigger_stage` (`5`), `time_to_gate_seconds`. | Tracks form initialization event only. |
| **`lead_captured`** | User successfully submits valid name and email. | Key conversion milestone (`BD-005`). | `has_company_name` (Boolean: `true`/`false`), `consent_given` (Boolean). | **Zero PII**: Email and name are sent only to the secure backend DB; never to analytics trackers. |
| **`blueprint_viewed`** | Full 18-section Solution Blueprint renders after gating. | Measures post-gating content consumption. | `session_token_hash`, `recommended_stack_category`. | Uses hashed pseudonymized session token. |
| **`estimate_viewed`** | Stage 6 Indicative Budget & Timeline bands render. | Assesses client engagement with pricing transparency (`BD-006`). | `timeline_band_weeks`, `complexity_tier` (`Low`/`Med`/`High`), `confidence_level`. | Tracks high-level tiering; no proprietary commercial data. |
| **`review_requested`** | User clicks **"Request Human Architect Review"**. | Measures transition into human-led discovery (`BD-010`). | `session_token_hash`, `request_type` (`standard_review`). | Notifies backend event bus securely. |
| **`discovery_sprint_interest`**| User clicks **"Inquire About Discovery Sprint"** (`BD-004`). | Validates commercial demand for the Paid Discovery Sprint hypothesis (`BA-002`). | `session_token_hash`, `urgency_preference`. | Crucial business hypothesis validation signal. |
| **`contact_form_submitted`**| User submits the direct architect contact form (`/contact`). | Tracks inbound RFP and enterprise direct advisory volume. | `inquiry_type`, `has_project_timeline` (Boolean). | PII restricted strictly to encrypted database persistence. |

---

## 3. Funnel Drop-off Analysis & Instrumentation Rules

To maintain high analytical fidelity without degrading website performance:
1. **Lightweight Event Dispatcher**: All events are queued and dispatched via non-blocking `navigator.sendBeacon` or asynchronous `fetch` during browser idle time.
2. **Zero DOM Bloat**: Events are bound cleanly using HTML data attributes (e.g. `data-analytics-event="cta_clicked"` `data-analytics-cta="start-problem"`) processed by a tiny 1KB Alpine.js helper.
3. **Session Replay Exclusion**: Third-party session recording tools that capture user keystrokes (e.g. Hotjar, FullStory) are **strictly forbidden** on the discovery textarea to protect confidential client operational disclosures.
