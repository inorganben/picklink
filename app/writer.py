import subprocess
from datetime import datetime
from pathlib import Path

from . import config


def build_md(url, summary, tags, path):
    title = path.split("/")[-1]
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    tag_line = " ".join(f"#{t.strip()}" for t in tags.split(",") if t.strip())
    return (
        f"---\n"
        f"title: {title}\n"
        f"date: {date}\n"
        f"tags: [{', '.join(repr(t.strip()) for t in tags.split(',') if t.strip())}]\n"
        f"url: {url}\n"
        f"---\n\n"
        f"{summary}\n\n"
        f"![截圖](/images/{title}.jpg)\n\n"
        f"原文連結：{url}\n"
    )


def save(url, summary, tags, path, image_path):
    docs_dir = config.ROOT / "docs"
    md_dir = docs_dir / Path(path)
    md_dir.mkdir(parents=True, exist_ok=True)

    title = path.split("/")[-1]
    img_dir = docs_dir / ".vuepress" / "public" / "images"
    img_dir.mkdir(parents=True, exist_ok=True)
    final_img = img_dir / f"{title}.jpg"
    if image_path and image_path.exists() and image_path != final_img:
        final_img.write_bytes(image_path.read_bytes())

    md_path = md_dir / f"{title}.md"
    md_path.write_text(build_md(url, summary, tags, path), encoding="utf-8")
    return md_path


def commit(message):
    repo = config.ROOT
    try:
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", message], cwd=repo, check=True)
    except subprocess.CalledProcessError:
        return False
    return True


def push():
    repo = config.ROOT
    try:
        subprocess.run(["git", "push"], cwd=repo, check=True)
    except subprocess.CalledProcessError:
        return False
    return True
