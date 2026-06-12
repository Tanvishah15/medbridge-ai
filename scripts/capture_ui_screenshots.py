"""Capture Streamlit UI screenshots for README / hackathon submission (Step 230)."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS = ROOT / "docs" / "screenshots"
DEFAULT_URL = "https://medbridge-ai.streamlit.app"
DEMO_LABEL = "ENT — Otitis Media (rpt_ent_001)"
CLARIFICATION_ANSWERS = [
    "Haan, halka bukhar hai.",
    "Dard halka hai, 3 din se.",
    "Kaam sunai deta hai.",
]


def _submit_demo_run(app) -> None:
    app.get_by_role("button", name="Understand My Report").click()
    app.get_by_text("Your explanation").or_(app.get_by_text("Clarification needed")).wait_for(
        timeout=180_000
    )

    if app.get_by_text("Clarification needed").count():
        inputs = app.locator('[data-testid="stTextInput"] input')
        count = inputs.count()
        for index in range(1, count):
            inputs.nth(index).fill(CLARIFICATION_ANSWERS[(index - 1) % len(CLARIFICATION_ANSWERS)])
        app.get_by_role("button", name="Submit answers & explain").click()
        app.get_by_text("Your explanation").wait_for(timeout=180_000)

    app.wait_for_timeout(2000)


def _wait_for_server(url: str, timeout: float = 60.0) -> None:
    import urllib.error
    import urllib.request

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(1)
    raise RuntimeError(f"Server not ready at {url}")


def _start_local_streamlit(port: int) -> subprocess.Popen:
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(ROOT / "ui" / "app.py"),
            "--server.headless",
            "true",
            "--server.port",
            str(port),
            "--browser.gatherUsageStats",
            "false",
        ],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _app_locator(page):
    """Streamlit Community Cloud embeds the app in an iframe."""
    iframe = page.locator('iframe[title="streamlitApp"]')
    if iframe.count():
        return iframe.first.content_frame
    return page


def capture_screenshots(base_url: str) -> None:
    from playwright.sync_api import sync_playwright

    SCREENSHOTS.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.goto(base_url, wait_until="networkidle", timeout=120_000)
        page.wait_for_timeout(4000)

        app = _app_locator(page)
        if app is None:
            raise RuntimeError("Could not locate Streamlit app frame")

        app.wait_for_selector('[data-testid="stApp"]', timeout=60_000)

        page.screenshot(
            path=str(SCREENSHOTS / "streamlit-ui-home.png"),
            full_page=True,
        )
        print(f"Saved {SCREENSHOTS / 'streamlit-ui-home.png'}")

        demo_select = app.locator('[data-testid="stSelectbox"]').first
        demo_select.click()
        app.get_by_text(DEMO_LABEL, exact=True).click()
        app.wait_for_timeout(5000)

        page.screenshot(
            path=str(SCREENSHOTS / "streamlit-ui-demo-loaded.png"),
            full_page=True,
        )
        print(f"Saved {SCREENSHOTS / 'streamlit-ui-demo-loaded.png'}")

        _submit_demo_run(app)

        page.screenshot(
            path=str(SCREENSHOTS / "streamlit-ui-demo-ent.png"),
            full_page=True,
        )
        print(f"Saved {SCREENSHOTS / 'streamlit-ui-demo-ent.png'}")

        trace = app.get_by_text("See how agents reasoned")
        if trace.count():
            trace.click()
            app.wait_for_timeout(1000)
            page.screenshot(
                path=str(SCREENSHOTS / "streamlit-ui-trace.png"),
                full_page=True,
            )
            print(f"Saved {SCREENSHOTS / 'streamlit-ui-trace.png'}")

        browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture MedBridge Streamlit UI screenshots.")
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help=f"Streamlit app URL (default: {DEFAULT_URL})",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Start local Streamlit instead of using cloud URL",
    )
    parser.add_argument("--port", type=int, default=8502)
    args = parser.parse_args()

    process: subprocess.Popen | None = None
    base_url = args.url.rstrip("/")

    try:
        if args.local:
            process = _start_local_streamlit(args.port)
            base_url = f"http://localhost:{args.port}"
            _wait_for_server(base_url)

        capture_screenshots(base_url)
    finally:
        if process is not None:
            process.terminate()
            process.wait(timeout=10)


if __name__ == "__main__":
    main()
