"""
Public Web Router for [STUDIO_NAME]
Implements Phase 5.4 public routes, contact intake with PII scrubbing, 
dynamic capability pillar rendering, and unified legal/trust documentation.
Conforms strictly to Phase 5.4 specifications and project governance.
"""

import json
import re
from typing import Any, Dict
import urllib.parse
from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, PlainTextResponse

from fastapi.templating import Jinja2Templates
from app.shared.logging import get_logger
from app.shared.security import scrub_pii

logger = get_logger(__name__)

router = APIRouter(tags=["Public Website Views"])
templates = Jinja2Templates(directory="templates")

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Capability Pillars Dataset
PILLARS_DATA: Dict[str, Dict[str, Any]] = {
    "software": {
        "slug": "software",
        "title": "Software & Websites",
        "tagline": "Business websites, web applications, internal tools, and custom software designed around your business.",
        "icon": "code-bracket",
        "description": "We build custom business websites, web applications, internal operational tools, and tailored software systems designed specifically around your business workflows and operational realities.",
        "capabilities": [
            "Custom Business Websites & Web Applications",
            "Internal Operational Tools & Portals",
            "Domain-Driven Backend Architecture",
            "Database Schema Design & Query Optimization",
            "Automated Testing & Continuous Integration"
        ],
        "deliverables": [
            "Production-Ready Source Code & Web Assets",
            "Comprehensive Architecture & API Documentation",
            "Automated Test Coverage & Performance Benchmarks",
            "Deployment Playbooks & Infrastructure Configurations"
        ]
    },
    "ai": {
        "slug": "ai",
        "title": "AI Solutions",
        "tagline": "AI-powered workflows, assistants, knowledge systems, and business-specific AI solutions.",
        "icon": "cpu-chip",
        "description": "We construct enterprise AI-powered workflows, domain-grounded knowledge systems, custom AI assistants, and provider-neutral AI gateways with strict pre-transit PII sanitization.",
        "capabilities": [
            "Business-Specific AI Workflows & Assistants",
            "Domain-Grounded Knowledge Systems (RAG)",
            "Provider-Neutral LLM Gateway Architecture",
            "Pre-Transit PII & Credential Sanitization",
            "Autonomous Multi-Agent Task Orchestration"
        ],
        "deliverables": [
            "Isolated AI Gateway Service & Routing Middleware",
            "Vector Database Indexing & Retrieval Pipelines",
            "Prompt Engineering & Output Validation Models",
            "Real-Time Latency & Cost Monitoring Dashboard"
        ]
    },
    "automation": {
        "slug": "automation",
        "title": "Automation",
        "tagline": "Replace repetitive manual work with reliable automated workflows and processes.",
        "icon": "bolt",
        "description": "We eliminate manual bottlenecks and repetitive human effort by building robust, event-driven automated workflows, document extraction pipelines, and process orchestration.",
        "capabilities": [
            "Repetitive Task & Process Automation",
            "Asynchronous Event-Driven Orchestration",
            "Deterministic State Machine Workflows",
            "Document Extraction & Processing Pipelines",
            "Automated Failure Alerting & Audit Logging"
        ],
        "deliverables": [
            "Event Queue Infrastructure & Consumer Services",
            "Workflow State Visualization & Management Tools",
            "Automated Failure Alerting & Monitoring Integration",
            "End-to-End Workflow Verification Test Suites"
        ]
    },
    "integrations": {
        "slug": "integrations",
        "title": "Integrations",
        "tagline": "Connect existing tools, APIs, and business systems so information moves where it should.",
        "icon": "link",
        "description": "We seamlessly connect your existing SaaS platforms, databases, APIs, and legacy systems so information flows automatically across your business without manual data entry.",
        "capabilities": [
            "SaaS, API & Database System Connections",
            "RESTful & GraphQL API Gateway Design",
            "Legacy Platform Data Synchronization",
            "OAuth2, SAML & Enterprise Security Authentication",
            "Bidirectional Webhook & Streaming Synchronization"
        ],
        "deliverables": [
            "Secure Integration Gateway & Middleware Services",
            "Comprehensive API Schema Specifications (OpenAPI)",
            "Data Mapping & Transformation Libraries",
            "Integration Test Suites & Mock Services"
        ]
    },
    "scale": {
        "slug": "scale",
        "title": "Scale & Improve",
        "tagline": "Improve, optimize, and scale existing software, workflows, and technology as your business grows.",
        "icon": "chart-bar",
        "description": "We optimize, modernize, and scale existing applications, cloud infrastructure, and database layers so your technology performs reliably as your operations expand.",
        "capabilities": [
            "Performance Optimization & Refactoring",
            "Cloud Infrastructure Scaling & Cost Tuning",
            "Database Index Tuning & High Availability",
            "Zero-Downtime Deployment & Containerization",
            "Security Hardening & Technical Governance"
        ],
        "deliverables": [
            "Modular Infrastructure as Code Repositories",
            "Performance Benchmark & Load Test Diagnostics",
            "Container Orchestration & Scaling Policies",
            "Disaster Recovery & Backup Automation Protocols"
        ]
    }
}


@router.get("/", response_class=HTMLResponse, summary="Homepage — 7-Section Anchor")
async def home_view(request: Request) -> HTMLResponse:
    """Renders the approved 7-section homepage narrative."""
    return templates.TemplateResponse(
        request=request,
        name="pages/index.html",
        context={
            "page_title": "[STUDIO_NAME] — Turning Business Problems Into Technology",
            "pillars": list(PILLARS_DATA.values()),
        },
    )


@router.get("/services", response_class=HTMLResponse, summary="Services Index")
async def services_index_view(request: Request) -> HTMLResponse:
    """Renders the overview page listing the five capability pillars."""
    return templates.TemplateResponse(
        request=request,
        name="pages/services.html",
        context={
            "page_title": "Capability Pillars & Services — [STUDIO_NAME]",
            "pillars": list(PILLARS_DATA.values()),
        },
    )


@router.get("/services/{pillar_slug}", response_class=HTMLResponse, summary="Service Detail")
async def service_detail_view(request: Request, pillar_slug: str) -> HTMLResponse:
    """Renders detailed breakdown for one of the five capability pillars. Returns HTTP 404 for invalid slugs."""
    pillar = PILLARS_DATA.get(pillar_slug.lower())
    if not pillar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service pillar '{pillar_slug}' not found."
        )

    return templates.TemplateResponse(
        request=request,
        name="pages/service_detail.html",
        context={
            "page_title": f"{pillar['title']} — [STUDIO_NAME]",
            "pillar": pillar,
            "all_pillars": list(PILLARS_DATA.values()),
        },
    )


@router.get("/how-we-work", response_class=HTMLResponse, summary="How We Work — Methodology")
async def how_we_work_view(request: Request) -> HTMLResponse:
    """Renders methodology, engineering laws, and Human+AI collaboration principles."""
    return templates.TemplateResponse(
        request=request,
        name="pages/how_we_work.html",
        context={
            "page_title": "How We Work — Methodology & Engineering Principles — [STUDIO_NAME]",
        },
    )


@router.get("/about", response_class=HTMLResponse, summary="About Studio")
async def about_view(request: Request) -> HTMLResponse:
    """Renders studio philosophy, technical ethos, and architectural values."""
    return templates.TemplateResponse(
        request=request,
        name="pages/about.html",
        context={
            "page_title": "About — [STUDIO_NAME] Technology Studio",
        },
    )


@router.get("/contact", response_class=HTMLResponse, summary="Direct Advisory Contact Form")
async def contact_get_view(request: Request) -> HTMLResponse:
    """Renders the direct architect inquiry intake form."""
    return templates.TemplateResponse(
        request=request,
        name="pages/contact.html",
        context={
            "page_title": "Contact Senior Architects — [STUDIO_NAME]",
            "submitted": False,
            "errors": {},
            "form_data": {},
        },
    )



async def _parse_form_data(request: Request) -> Dict[str, Any]:
    """Parses form data from application/x-www-form-urlencoded or application/json without python-multipart dependency."""
    content_type = request.headers.get("content-type", "")
    body = await request.body()
    text_body = body.decode("utf-8", errors="replace")
    if "application/json" in content_type:
        try:
            return json.loads(text_body)
        except Exception:
            return {}
    parsed = urllib.parse.parse_qs(text_body, keep_blank_values=True)
    return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}


@router.post("/contact", response_class=HTMLResponse, summary="Process Contact Inquiry")
async def contact_post_view(request: Request) -> HTMLResponse:
    """
    Validates direct inquiry payload, performs PII scrubbing, 
    and logs request without claiming unconfigured email dispatch.
    Returns HTTP 422 on validation failure.
    """
    form = await _parse_form_data(request)
    full_name = str(form.get("full_name", "")).strip()
    corporate_email = str(form.get("corporate_email", "")).strip().lower()
    company_name = str(form.get("company_name", "")).strip()
    project_scope = str(form.get("project_scope", "")).strip()
    message = str(form.get("message", "")).strip()

    errors: Dict[str, str] = {}
    if not full_name:
        errors["full_name"] = "Full name is required."
    if not corporate_email:
        errors["corporate_email"] = "Corporate email is required."
    elif not EMAIL_REGEX.match(corporate_email):
        errors["corporate_email"] = "Please enter a valid email address (e.g. name@company.com)."
    if not message:
        errors["message"] = "Project description / message is required."

    form_data = {
        "full_name": full_name,
        "corporate_email": corporate_email,
        "company_name": company_name,
        "project_scope": project_scope,
        "message": message,
    }

    if errors:
        logger.info(f"Contact form validation failed: {errors}")
        return templates.TemplateResponse(
            request=request,
            name="pages/contact.html",
            context={
                "page_title": "Contact Senior Architects — [STUDIO_NAME]",
                "submitted": False,
                "errors": errors,
                "form_data": form_data,
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    # Sanitize message before logging
    sanitized_message = scrub_pii(message)
    sanitized_name = scrub_pii(full_name)

    logger.info(
        f"Inquiry received from {sanitized_name} ({corporate_email}) | "
        f"Company: {company_name or 'N/A'} | Scope: {project_scope or 'General'} | "
        f"Message length: {len(sanitized_message)}"
    )

    # Safe success response (no fake claims of email dispatch)
    return templates.TemplateResponse(
        request=request,
        name="pages/contact.html",
        context={
            "page_title": "Inquiry Received — [STUDIO_NAME]",
            "submitted": True,
            "errors": {},
            "form_data": {},
        },
        status_code=status.HTTP_200_OK,
    )


@router.get("/privacy", response_class=HTMLResponse, summary="Privacy Policy")
async def privacy_view(request: Request) -> HTMLResponse:
    """Renders Privacy Policy using unified trust/legal template."""
    return templates.TemplateResponse(
        request=request,
        name="pages/trust_legal.html",
        context={
            "page_title": "Privacy Policy — [STUDIO_NAME]",
            "document_type": "privacy",
            "document_title": "Privacy Policy & Data Protection",
            "last_updated": "September 2026",
        },
    )


@router.get("/terms", response_class=HTMLResponse, summary="Terms of Service")
async def terms_view(request: Request) -> HTMLResponse:
    """Renders Terms of Service using unified trust/legal template."""
    return templates.TemplateResponse(
        request=request,
        name="pages/trust_legal.html",
        context={
            "page_title": "Terms of Service — [STUDIO_NAME]",
            "document_type": "terms",
            "document_title": "Terms of Service & Commercial Terms",
            "last_updated": "September 2026",
        },
    )


@router.get("/security", response_class=HTMLResponse, summary="Security & Governance")
async def security_view(request: Request) -> HTMLResponse:
    """Renders Security & Technical Governance using unified trust/legal template."""
    return templates.TemplateResponse(
        request=request,
        name="pages/trust_legal.html",
        context={
            "page_title": "Security & Governance — [STUDIO_NAME]",
            "document_type": "security",
            "document_title": "Security & Technical Governance",
            "last_updated": "September 2026",
        },
    )


@router.get("/solutions", response_class=HTMLResponse, summary="Solution Blueprints Index")
async def solutions_view(request: Request) -> HTMLResponse:
    """Renders outcome-driven solution blueprints index mapping enterprise problems to technical capabilities."""
    return templates.TemplateResponse(
        request=request,
        name="pages/solutions.html",
        context={
            "page_title": "Solution Blueprints & Enterprise Outcomes — [STUDIO_NAME]",
        },
    )


@router.get("/robots.txt", response_class=PlainTextResponse, summary="Search Engine Directives")
async def robots_txt_view(request: Request) -> PlainTextResponse:
    """Returns minimal plain-text search crawler directives."""
    base_url = str(request.base_url).rstrip("/")
    content = f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n"
    return PlainTextResponse(content=content)


@router.get("/sitemap.xml", summary="XML Sitemap Index")
async def sitemap_xml_view(request: Request) -> Response:
    """Generates dynamic XML sitemap of all canonical public paths."""
    base_url = str(request.base_url).rstrip("/")
    paths = [
        "/",
        "/discovery",
        "/services",
        "/services/software",
        "/services/ai",
        "/services/automation",
        "/services/integrations",
        "/services/scale",
        "/solutions",
        "/how-we-work",
        "/about",
        "/contact",
        "/privacy",
        "/terms",
        "/security",
    ]
    xml_items = []
    for path in paths:
        loc = f"{base_url}{path}"
        priority = "1.0" if path == "/" else "0.8"
        xml_items.append(f"  <url>\n    <loc>{loc}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>{priority}</priority>\n  </url>")

    xml_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(xml_items) +
        "\n</urlset>"
    )
    return Response(content=xml_content, media_type="application/xml")

