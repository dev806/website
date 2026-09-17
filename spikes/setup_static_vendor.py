"""
Spike SP-07: Static Asset Vendoring and Local Serving Spike
Downloads or vendors HTMX 2.x and Alpine.js 3.x into static/vendor/,
serves them via FastAPI StaticFiles, and verifies offline availability.
"""
import os
import sys
sys.path.insert(0, os.path.abspath("."))
from pathlib import Path
import httpx
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from httpx import AsyncClient, ASGITransport

print("=" * 70)
print("SP-07: STATIC ASSET VENDORS & LOCAL SERVING SPIKE")
print("=" * 70)

VENDOR_DIR = Path("static/vendor")
VENDOR_DIR.mkdir(parents=True, exist_ok=True)

HTMX_URL = "https://unpkg.com/htmx.org@2.0.4/dist/htmx.min.js"
ALPINE_URL = "https://unpkg.com/alpinejs@3.14.8/dist/cdn.min.js"

htmx_path = VENDOR_DIR / "htmx.min.js"
alpine_path = VENDOR_DIR / "alpine.min.js"

# 1. Download official vendor assets if not already cached locally
with httpx.Client(timeout=10.0, follow_redirects=True) as client:
    if not htmx_path.exists() or htmx_path.stat().st_size == 0:
        print(f"Downloading HTMX 2.x from {HTMX_URL}...")
        resp = client.get(HTMX_URL)
        if resp.status_code == 200:
            htmx_path.write_bytes(resp.content)
            print(f"  --> Saved HTMX 2.x ({len(resp.content)} bytes) to {htmx_path}")
        else:
            print(f"  --> Failed to download HTMX: {resp.status_code}")

    if not alpine_path.exists() or alpine_path.stat().st_size == 0:
        print(f"Downloading Alpine.js 3.x from {ALPINE_URL}...")
        resp = client.get(ALPINE_URL)
        if resp.status_code == 200:
            alpine_path.write_bytes(resp.content)
            print(f"  --> Saved Alpine.js 3.x ({len(resp.content)} bytes) to {alpine_path}")
        else:
            print(f"  --> Failed to download Alpine.js: {resp.status_code}")

# Verify files exist on disk
assert htmx_path.exists() and htmx_path.stat().st_size > 10000, "HTMX asset missing or corrupted"
assert alpine_path.exists() and alpine_path.stat().st_size > 10000, "Alpine asset missing or corrupted"
print(f"[PASS] Static files vendored locally: htmx ({htmx_path.stat().st_size} bytes), alpine ({alpine_path.stat().st_size} bytes)")

# 2. Test Serving via FastAPI StaticFiles
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

async def test_static_serving():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test HTMX
        r_htmx = await client.get("/static/vendor/htmx.min.js")
        assert r_htmx.status_code == 200
        assert "javascript" in r_htmx.headers.get("content-type", "")
        assert len(r_htmx.content) == htmx_path.stat().st_size
        print(f"[PASS] GET /static/vendor/htmx.min.js returned HTTP 200 ({len(r_htmx.content)} bytes, Content-Type: {r_htmx.headers.get('content-type')})")

        # Test Alpine.js
        r_alpine = await client.get("/static/vendor/alpine.min.js")
        assert r_alpine.status_code == 200
        assert "javascript" in r_alpine.headers.get("content-type", "")
        assert len(r_alpine.content) == alpine_path.stat().st_size
        print(f"[PASS] GET /static/vendor/alpine.min.js returned HTTP 200 ({len(r_alpine.content)} bytes, Content-Type: {r_alpine.headers.get('content-type')})")

        # Test non-existent file returns 404
        r_404 = await client.get("/static/vendor/non_existent.js")
        assert r_404.status_code == 404
        print("[PASS] Non-existent static asset returns HTTP 404 cleanly.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_static_serving())
    print("\n[PASS] All Static Asset Vending tests passed successfully.")
    print("=" * 70)
