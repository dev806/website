"""
Automated Test Suite for Phase 5.5 — Public Website Completion & Hardening
Conforms to DOC-TEST-001 and Phase 5.5 Implementation Authorization.
Tests all 17 concrete GET paths, solutions index, robots.txt, sitemap.xml,
canonical & Open Graph metadata, SVG icon standardization, and accessibility landmarks.
"""

import xml.etree.ElementTree as ET
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

CONCRETE_GET_PATHS = [
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
    "/robots.txt",
    "/sitemap.xml",
]

HTML_PUBLIC_PATHS = [
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


@pytest.mark.parametrize("path", CONCRETE_GET_PATHS)
def test_public_get_paths_return_200(path: str):
    """Verifies that all 17 concrete public GET paths respond with HTTP 200 OK."""
    response = client.get(path)
    assert response.status_code == 200, f"Expected 200 for {path}, got {response.status_code}"
    if path == "/robots.txt":
        assert "text/plain" in response.headers.get("content-type", "")
    elif path == "/sitemap.xml":
        assert "xml" in response.headers.get("content-type", "")
    else:
        assert "text/html" in response.headers.get("content-type", "")


def test_invalid_service_pillar_returns_404():
    """Verifies that invalid capability pillar slugs return HTTP 404 Not Found."""
    response = client.get("/services/invalid-pillar-slug")
    assert response.status_code == 404
    assert "detail" in response.json() or "404" in response.text


def test_robots_txt_content_and_directives():
    """Verifies that /robots.txt returns valid plain text directives referencing sitemap.xml."""
    response = client.get("/robots.txt")
    assert response.status_code == 200
    text = response.text
    assert "User-agent: *" in text
    assert "Allow: /" in text
    assert "sitemap.xml" in text


def test_sitemap_xml_validity_and_routes():
    """Verifies that /sitemap.xml returns valid XML containing all 15 public HTML URLs and zero internal/POST routes."""
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert "xml" in response.headers.get("content-type", "")

    root = ET.fromstring(response.text)
    assert root.tag.endswith("urlset")

    # Extract all <loc> values
    namespaces = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [elem.text for elem in root.findall("s:url/s:loc", namespaces)]
    
    # If namespaces failed, fallback without NS
    if not locs:
        locs = [elem.text for elem in root.findall(".//loc")]

    assert len(locs) == len(HTML_PUBLIC_PATHS), f"Expected {len(HTML_PUBLIC_PATHS)} URLs in sitemap, found {len(locs)}"

    for path in HTML_PUBLIC_PATHS:
        assert any(path in loc for loc in locs), f"Path {path} missing from sitemap"

    # Ensure no internal/health/POST endpoints in sitemap
    assert not any("/health" in loc for loc in locs)
    assert not any("/contact/submit" in loc for loc in locs)


def test_seo_metadata_canonical_and_open_graph():
    """Verifies canonical URL, Open Graph metadata presence, and absence of speculative og:image."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    assert '<link rel="canonical"' in html
    assert 'property="og:title"' in html
    assert 'property="og:description"' in html
    assert 'property="og:type"' in html
    assert 'property="og:url"' in html

    # Strict check: og:image must NOT be present as no approved image asset exists
    assert 'property="og:image"' not in html


def test_service_pages_svg_icon_standardization():
    """Verifies that service pages render clean SVG icons and zero emoji icons."""
    # Overview page
    res_services = client.get("/services")
    assert res_services.status_code == 200
    html_services = res_services.text
    assert "<svg" in html_services
    for emoji in ["💻", "🤖", "⚡", "🔗", "📊"]:
        assert emoji not in html_services, f"Emoji {emoji} found in /services"

    # Detail page
    res_detail = client.get("/services/software")
    assert res_detail.status_code == 200
    html_detail = res_detail.text
    assert "<svg" in html_detail
    assert "⚡" not in html_detail


def test_contact_post_valid_payload():
    """Verifies that submitting a valid contact form returns HTTP 200 and renders success message."""
    payload = {
        "full_name": "Jane Doe",
        "corporate_email": "jane.doe@enterprise.com",
        "company_name": "Acme Corp",
        "project_scope": "Bespoke Software Architecture",
        "message": "We need to modernize our legacy system architecture and scale backend services.",
    }
    response = client.post("/contact", data=payload)
    assert response.status_code == 200
    assert "Inquiry Received" in response.text or "Thank you for reaching out" in response.text


def test_contact_post_invalid_payload_returns_422():
    """Verifies that empty or invalid contact payloads return HTTP 422 Unprocessable Entity."""
    response_empty = client.post("/contact", data={})
    assert response_empty.status_code == 422

    response_bad_email = client.post(
        "/contact",
        data={
            "full_name": "Jane Doe",
            "corporate_email": "invalid-email-format",
            "message": "Project description text",
        },
    )
    assert response_bad_email.status_code == 422
    assert "valid email" in response_bad_email.text.lower()


def test_accessibility_landmarks():
    """Verifies that semantic accessibility landmarks (banner, main, contentinfo, skip-link) are present on homepage."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    assert 'role="banner"' in html or '<header' in html
    assert 'id="main-content"' in html
    assert 'role="main"' in html
    assert 'role="contentinfo"' in html or '<footer' in html
    assert 'class="skip-link"' in html


def test_navigation_mega_menu_markup_and_css_guards():
    """Verifies that navigation markup, Alpine reactivity handlers, and CSS guards prevent stuck mega-menus."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    # Verify Alpine component data and escape handler on body
    assert 'x-data="{ mobileOpen: false, dropdownOpen: false }"' in html
    assert '@keydown.escape="dropdownOpen = false; mobileOpen = false"' in html

    # Verify desktop dropdown has click.outside dismissal and click handlers on sibling links
    assert '@click.outside="dropdownOpen = false"' in html
    assert 'href="/how-we-work" class="nav-link" @click="dropdownOpen = false"' in html
    assert 'href="/about" class="nav-link" @click="dropdownOpen = false"' in html
    assert 'href="/contact" class="nav-link" @click="dropdownOpen = false"' in html

    # Verify mobile drawer links dismiss mobile drawer
    assert 'class="mobile-drawer"' in html
    assert 'x-show="mobileOpen"' in html
    assert '@click="mobileOpen = false"' in html

    # Verify CSS contains desktop exclusion guard for mobile-drawer
    css_res = client.get("/static/css/main.css")
    assert css_res.status_code == 200
    assert "@media (min-width: 901px)" in css_res.text
    assert ".mobile-drawer" in css_res.text
    assert "display: none !important" in css_res.text
