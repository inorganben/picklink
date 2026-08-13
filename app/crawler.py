import logging
import time

import trafilatura

log = logging.getLogger("crawler")


def fetch_and_clean(url):
    log.info("開始抓取 %s", url)
    start = time.time()
    downloaded = trafilatura.fetch_url(url)
    log.info("抓取完成，耗時 %.1fs，大小 %s", time.time() - start,
             len(downloaded) if downloaded else 0)
    if downloaded is None:
        raise RuntimeError("無法抓取頁面內容")
    text = trafilatura.extract(
        downloaded,
        include_links=False,
        include_images=False,
        include_comments=False,
        favor_precision=True,
    )
    if not text:
        raise RuntimeError("無法提取正文")
    log.info("正文提取完成，長度 %d", len(text))
    return text.strip()
