"""
Frontend & Static Assets Foundation Tests for [STUDIO_NAME]
"""

import pytest


@pytest.mark.asyncio
async def test_home_page_renders_base_template(async_client):
    """Verifies that the root landing page renders Jinja2 layout with proper brand assets."""
    response = await async_client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    text = response.text
    assert "[STUDIO_NAME]" in text
    assert "/static/css/main.css" in text
    assert "/static/vendor/htmx.min.js" in text
    assert "/static/vendor/alpine.min.js" in text


@pytest.mark.asyncio
async def test_vendored_static_assets_served(async_client):
    """Verifies that vendored static assets are directly served via FastAPI."""
    r_htmx = await async_client.get("/static/vendor/htmx.min.js")
    assert r_htmx.status_code == 200
    assert len(r_htmx.content) > 40000

    r_alpine = await async_client.get("/static/vendor/alpine.min.js")
    assert r_alpine.status_code == 200
    assert len(r_alpine.content) > 40000

    r_css = await async_client.get("/static/css/main.css")
    assert r_css.status_code == 200
    assert len(r_css.content) > 1000
