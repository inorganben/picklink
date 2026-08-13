from pathlib import Path
from playwright.sync_api import sync_playwright

from . import config


def screenshot(url, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(url, wait_until="networkidle", timeout=60000)
        page.screenshot(path=str(out_path), type="jpeg", quality=60, full_page=False)
        browser.close()
