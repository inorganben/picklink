import trafilatura


def fetch_and_clean(url):
    downloaded = trafilatura.fetch_url(url)
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
    return text.strip()
