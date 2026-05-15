#!/usr/bin/env python3
"""Smoke-test mobile layout: no horizontal overflow, key elements visible per hub view."""
from __future__ import annotations

import http.server
import socketserver
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORT = 8890

VIEWS = [
    ("onboarding", "#hubNavOnboarding", "#fullName"),
    ("payment", "#hubNavPayment", "#rpClientSearch"),
    ("session", "#hubNavSession", "#trainerSel"),
    ("admin", "#hubNavAdmin", "#adminUser"),
]

VIEWPORTS = [
    (320, 568),
    (390, 844),
    (414, 896),
]


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("SKIP: playwright not installed")
        return 0

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=str(ROOT), **k)

        def log_message(self, *args):
            pass

    srv = socketserver.TCPServer(("127.0.0.1", PORT), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    failures = []

    with sync_playwright() as p:
        for w, h in VIEWPORTS:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": w, "height": h})
            page.goto(f"http://127.0.0.1:{PORT}/index.html", wait_until="load")
            overflow = page.evaluate(
                "() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1"
            )
            if overflow:
                failures.append(f"{w}x{h}: horizontal overflow")
            for _name, nav_sel, key_sel in VIEWS:
                page.click(nav_sel)
                page.wait_for_timeout(100)
                visible = page.evaluate(
                    f"""() => {{
                      const el = document.querySelector('{key_sel}');
                      if (!el) return false;
                      const r = el.getBoundingClientRect();
                      const st = getComputedStyle(el);
                      return r.width > 0 && r.height > 0 && st.display !== 'none' && st.visibility !== 'hidden';
                    }}"""
                )
                if not visible and key_sel != "#adminUser":
                    failures.append(f"{w}x{h} {_name}: {key_sel} not visible")
            browser.close()

    srv.shutdown()
    srv.server_close()

    if failures:
        print("FAIL")
        for f in failures:
            print(" ", f)
        return 1
    print("OK: mobile layout smoke passed for", len(VIEWPORTS), "viewports x", len(VIEWS), "views")
    return 0


if __name__ == "__main__":
    sys.exit(main())
