# Website SEO Strategy & Search Architecture

**Document ID:** `DOC-WEB-012`  
**Classification:** Website Architecture / Phase 3 SEO Strategy  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-002](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-002), [BD-003](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-003), [BD-009](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-009), [BD-011](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-011), [BD-012](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-012), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [Website Strategy](file:///d:/Project_website/docs/04-website/01-WEBSITE-STRATEGY.md) | [Sitemap](file:///d:/Project_website/docs/04-website/02-SITEMAP.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. SEO Strategic Objectives & Governance

The search engine optimization strategy of `[STUDIO_NAME]` targets **high-intent commercial and problem-led search traffic** rather than generic consumer volume. 

### Core SEO Mandates
1. **Zero Fabricated Search Metrics**: In strict compliance with claim governance (`BR-GDL-003`), **zero search volumes, keyword difficulty scores, or traffic forecasts are invented**. Where quantitative search volume data is needed for campaign planning, it is formally labeled `RESEARCH REQUIRED`.
2. **Problem-Led Search Capture**: Position the studio as the destination for founders and operators searching for solutions to acute operational pain (e.g. *"how to automate manual invoice data entry"*, *"integrating custom CRM with legacy ERP"*).
3. **Flawless Technical Hygiene**: Leverage the server-rendered FastAPI + Jinja2 stack (`BD-015`) to achieve near-instantaneous First Contentful Paint (FCP) and 100% crawlability with zero client-side JavaScript rendering penalties.

---

## 2. Search Intent Taxonomy & Keyword Topic Clusters

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              SEARCH INTENT CLUSTER MATRIX                              │
├───────────────────────┬────────────────────────────┬───────────────────────────────────┤
│ CLUSTER ID            │ SEARCH INTENT & THEME      │ TARGET CANONICAL URL              │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Cluster 1: Category   │ "AI technology studio",    │ `/` (Home)                        │
│ & Studio Positioning  │ "AI systems partner",      │                                   │
│                       │ "AI software engineering"  │                                   │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Cluster 2: Custom     │ "custom software studio",  │ `/services/software`              │
│ Software Engineering  │ "Python web app build",    │                                   │
│                       │ "startup MVP development"  │                                   │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Cluster 3: Applied AI │ "applied AI for business", │ `/services/ai`                    │
│ & Document Extraction │ "LLM workflow integration",│                                   │
│                       │ "enterprise AI automation" │                                   │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Cluster 4: Workflow   │ "process automation tools",│ `/services/automation`            │
│ & Task Automation     │ "eliminate manual entry",  │                                   │
│                       │ "event-driven automation"  │                                   │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Cluster 5: Systems &  │ "ERP CRM integration",     │ `/services/integrations`          │
│ API Integrations      │ "custom API connector",    │                                   │
│                       │ "database synchronization" │                                   │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Cluster 6: Problem    │ "turn business problem     │ `/discovery`                      │
│ Translation & Scoping │ into software",            │ (*"Start With Your Problem"*)     │
│                       │ "software project scope"   │                                   │
└───────────────────────┴────────────────────────────┴───────────────────────────────────┘
```

---

## 3. Metadata Architecture & Tagging Conventions

Every page in the system dynamically injects an optimized metadata envelope adhering to strict character length boundaries:

* **Title Tag Formula**: `<Page Specific Title> | [STUDIO_NAME] — AI-Native Technology Studio` (Total length $\le 60$ characters).
* **Meta Description Formula**: Actionable summary of page value, mentioning target segments and ending with a clear conversion verb (Total length 140–155 characters).
* **Canonical URL**: Strict self-referential canonical tag without query parameters or trailing slashes (e.g. `<link rel="canonical" href="https://domain.com/services/software">`).

### Metadata Matrix (MVP Pages)
| Page Route | Optimized Title Tag Candidate | Meta Description Candidate |
| :--- | :--- | :--- |
| `/` | `[STUDIO_NAME] — Turn Business Problems Into Technology` | We build custom software, deploy applied AI, and automate workflows for startups and growing businesses. Start with your problem today. |
| `/discovery` | `AI Project Discovery Engine | [STUDIO_NAME]` | Translate your operational friction into an actionable technology blueprint and indicative estimate in minutes. Free and confidential. |
| `/services` | `Engineering Capabilities & Pillars | [STUDIO_NAME]` | Explore our 5 capability pillars: Custom Software, Applied AI, Workflow Automation, Systems Integration, and Scale Engineering. |
| `/services/software`| `Custom Software Engineering | [STUDIO_NAME]` | High-craft full-stack web applications, internal tools, and modular architectures engineered in modern Python and FastAPI. |
| `/services/ai` | `Applied AI & Document Intelligence | [STUDIO_NAME]` | Enterprise AI integration with zero model training on client data. Structured LLM workflows, extraction pipelines, and deterministic logic. |
| `/services/automation`| `Workflow & Operations Automation | [STUDIO_NAME]` | Eliminate manual copy-pasting and repetitive tasks with resilient, event-driven background queues and automation pipelines. |
| `/services/integrations`| `API & Enterprise Systems Integration | [STUDIO_NAME]` | Connect fragmented CRMs, ERPs, billing platforms, and legacy databases into unified, synchronized operational workflows. |
| `/services/scale` | `System Scale & Modernization | [STUDIO_NAME]` | Refactor technical debt, optimize database performance, and modernize legacy software for high-volume enterprise stability. |
| `/how-we-work` | `Our Methodology & North Star | [STUDIO_NAME]` | Discover how we work: Understand, Translate, Build, Automate, Scale. Senior human architects owning judgement, AI handling leverage. |
| `/about` | `About the Studio & Philosophy | [STUDIO_NAME]` | An AI-native technology studio built on craftsmanship, transparent estimation, and business-aligned software engineering. |
| `/contact` | `Contact Senior Architects | [STUDIO_NAME]` | Direct architectural advisory for enterprise founders and operators. Triage and response within 1 business day. |

---

## 4. Structured Data Specifications (Schema.org JSON-LD)

The application automatically renders validated JSON-LD schema blocks in the `<head>` of HTML templates:

### A. Universal Organization Schema (Injected on `/` and `/about`)
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "[STUDIO_NAME]",
  "url": "https://domain.com",
  "logo": "https://domain.com/static/assets/logo.png",
  "description": "AI-Native Technology Studio and Systems Partner turning business problems into custom software, automation, and scale.",
  "knowsAbout": [
    "Custom Software Engineering",
    "Applied Artificial Intelligence",
    "Workflow Automation",
    "Enterprise Systems Integration"
  ]
}
```

### B. SoftwareApplication Schema (Injected on `/discovery`)
```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "AI Project Discovery Engine",
  "operatingSystem": "All modern web browsers",
  "applicationCategory": "BusinessApplication",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "description": "Interactive diagnostic tool translating business problems into Opportunity Maps, Solution Blueprints, and indicative project estimates."
}
```

---

## 5. Technical Indexation & Crawl Discipline

1. **Server-Rendered HTML**: Because templates are rendered server-side via FastAPI and Jinja2 (`BD-015`), search engine bots receive 100% complete HTML text on the initial HTTP response without waiting for client-side JavaScript execution.
2. **Robots.txt Architecture**:
   - `Allow: /`
   - `Allow: /services/`
   - `Allow: /solutions`
   - `Allow: /how-we-work`
   - `Allow: /about`
   - `Allow: /discovery`
   - `Disallow: /discovery/review` *(Protects private client session tokens)*
   - `Disallow: /api/` *(Protects internal API endpoints)*
   - `Sitemap: https://domain.com/sitemap.xml`
3. **Automated XML Sitemap**: A dynamic XML sitemap is generated by FastAPI at `/sitemap.xml`, containing all canonical URLs, last-modified dates, and strict `<loc>` tags.
