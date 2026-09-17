"""
Exception Architecture & Standard Error Envelope Tests for [STUDIO_NAME]
"""

import pytest


@pytest.mark.asyncio
async def test_not_found_error_envelope(async_client):
    """Verifies that 404 errors return the standardized error envelope."""
    custom_corr_id = "test-correlation-id-12345"
    response = await async_client.get(
        "/non-existent-endpoint-path",
        headers={"X-Correlation-ID": custom_corr_id},
    )
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert data["error"]["code"] == "HTTP_404"
    assert "meta" in data
    assert data["meta"]["request_id"] == custom_corr_id
    assert "timestamp" in data["meta"]
    assert response.headers["X-Correlation-ID"] == custom_corr_id
