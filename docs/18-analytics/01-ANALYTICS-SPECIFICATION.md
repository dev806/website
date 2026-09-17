# PHASE 6 — PRIVACY-FIRST TELEMETRY & ANALYTICS SPECIFICATION

**Document ID:** `DOC-ANA-001`  
**Classification:** Telemetry Architecture & Privacy Specification  
**Parent Horizon:** Phase 6 (Rigor, Security & Reliability)  
**Status:** CANONICAL SPECIFICATION — RECONCILED & CORRECTED — AWAITING OWNER APPROVAL  

---

## 1. TELEMETRY PHILOSOPHY: PRIVACY-FIRST & ZERO-PII

The analytics model of `[STUDIO_NAME]` is engineered around a fundamental privacy law: **capture only anonymous operational event telemetry required to understand funnel drop-offs and system health, while strictly prohibiting the ingestion or storage of personal data, business problem text, or confidential prompts**.

We reject third-party cross-site tracking pixels, cookie banners, and invasive ad-tech scripts.

---

## 2. ANALYTICS STORAGE ARCHITECTURE EVALUATION

Comparing storage options for operational event telemetry:

| Option | Privacy Compliance | Database Overhead | Queryability | Cost | Maintenance Burden | Recommendation Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Option A: Structured Application Log Stream (stdout/log file)** | 100% Privacy-First | **Zero DB Overhead** | Excellent (grep/Loki) | **₹0 / $0** | Zero | **RECOMMENDED FOR MVP** |
| **Option B: SQL Server Telemetry Table (`dbo.telemetry_events`)** | 100% Privacy-First | High Write Load | Excellent (SQL) | ₹0 / $0 | Low | **NOT RECOMMENDED** (Adds DB write bloat) |
| **Option C: Plausible Analytics (Self-Hosted / Cloud)** | High (Cookie-less) | Zero DB Overhead | High (Dashboard) | $9/mo | Low | **ALTERNATIVE OPTION C** |
| **Option D: PostHog / Google Analytics** | Low / Medium | Zero DB Overhead | High | $0 - $20/mo| Medium | **REJECTED FOR MVP** |

- **Recommendation**: Implement **Option A (Structured Application Log Stream)** for MVP. Anonymous event JSON strings are written directly to Uvicorn structured application logs via FastAPI middleware. Incurs **₹0 cost**, requires **zero database write overhead**, and **zero third-party tracking scripts**.

---

## 3. STRICT PRIVACY BOUNDARIES & PROHIBITIONS

### Permitted Telemetry (Anonymous Event Metadata)
- Anonymous Session UUID (SHA-256 hashed)
- Stage transition events (`discovery_started`, `stage_completed`, `blueprint_viewed`)
- Button click counts (CTA interactions)
- Request latency & HTTP status codes

### Strictly Prohibited Data (Never Logged or Tracked)
- ✕ Raw business problem statement text
- ✕ User names, emails, or phone numbers
- ✕ AI prompts or model completion text
- ✕ Blueprint contents or financial figures
- ✕ Cross-site tracking cookies or ad pixels
