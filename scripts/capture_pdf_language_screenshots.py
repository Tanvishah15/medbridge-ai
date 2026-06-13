"""Capture PDF upload + multilingual explanation screenshots for README."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS = ROOT / "docs" / "screenshots"
PDF_PATH = ROOT / "data" / "synthetic_reports" / "medbridge_demo_upload_liver.pdf"
DEFAULT_URL = "https://medbridge-ai.streamlit.app"

# Complete symptoms to reduce clarification rounds on cloud demo
SYMPTOMS = (
    "Please explain this liver lab report in simple language. "
    "No abdominal pain or jaundice. I only take vitamins. Very little alcohol."
)

CAPTURES = [
    ("Chinese", "streamlit-ui-pdf-chinese-liver.png"),
    ("French", "streamlit-ui-pdf-french-liver.png"),
    ("German", "streamlit-ui-pdf-german-liver.png"),
]


def _app_locator(page):
    iframe = page.locator('iframe[title="streamlitApp"]')
    if iframe.count():
        return iframe.first.content_frame
    return page


def _select_language(app, language: str) -> None:
    selects = app.locator('[data-testid="stSelectbox"]')
    lang_select = selects.nth(1)
    lang_select.click()
    app.get_by_text(language, exact=True).click()
    app.wait_for_timeout(1500)


def _run_pdf_demo(app) -> None:
    app.locator('[data-testid="stFileUploader"] input[type="file"]').set_input_files(
        str(PDF_PATH)
    )
    app.wait_for_timeout(1000)
    symptoms = app.locator('[data-testid="stTextArea"] textarea').first
    symptoms.fill(SYMPTOMS)
    app.wait_for_timeout(500)
    app.get_by_role("button", name="Understand My Report").click()
    app.get_by_text("Your explanation").or_(app.get_by_text("Clarification needed")).wait_for(
        timeout=180_000
    )
    if app.get_by_text("Clarification needed").count():
        inputs = app.locator('[data-testid="stTextInput"] input')
        for index in range(1, min(inputs.count(), 4)):
            inputs.nth(index).fill("No.")
        app.get_by_role("button", name="Submit answers & explain").click()
        app.get_by_text("Your explanation").wait_for(timeout=180_000)
    app.wait_for_timeout(2000)


def capture(url: str) -> None:
    from playwright.sync_api import sync_playwright

    if not PDF_PATH.exists():
        raise FileNotFoundError(f"Missing demo PDF: {PDF_PATH}")

    SCREENSHOTS.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 1200})
        page.goto(url, wait_until="networkidle", timeout=120_000)
        page.wait_for_timeout(4000)

        app = _app_locator(page)
        if app is None:
            raise RuntimeError("Could not locate Streamlit app frame")
        app.wait_for_selector('[data-testid="stApp"]', timeout=60_000)

        for language, filename in CAPTURES:
            print(f"Capturing {language}...")
            page.goto(url, wait_until="networkidle", timeout=120_000)
            page.wait_for_timeout(3000)
            app = _app_locator(page)
            _select_language(app, language)
            _run_pdf_demo(app)
            page.screenshot(path=str(SCREENSHOTS / filename), full_page=True)
            print(f"Saved {SCREENSHOTS / filename}")

        browser.close()


def main() -> None:
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    capture(url.rstrip("/"))


if __name__ == "__main__":
    main()
