import logging
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

from . import config

log = logging.getLogger("screenshot")


def screenshot(url, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    log.info("啟動 Chrome 截圖 %s", url)
    start = time.time()
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        log.info("Chrome 已啟動，耗時 %.1fs", time.time() - start)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        log.info("載入頁面（domcontentloaded，最長 30s）…")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1500)
        log.info("頁面載入完成，耗時 %.1fs，開始截圖", time.time() - start)
        page.screenshot(path=str(out_path), type="jpeg", quality=60, full_page=False)
        log.info("截圖完成，總耗時 %.1fs", time.time() - start)
        browser.close()
