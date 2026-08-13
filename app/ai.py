import requests
from . import config


def chat(messages, temperature=0.3, max_tokens=2048):
    if not config.API_KEY or not config.BASE_URL:
        raise RuntimeError("缺少 .env 配置（API_KEY / BASE_URL）")

    payload = {
        "model": config.MODEL_NAME,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {config.API_KEY}",
        "Content-Type": "application/json",
    }
    resp = requests.post(config.BASE_URL, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def ask_path_and_tags(content):
    system = (
        "你是知識庫整理助手。根據網頁內容，輸出兩個部分：\n"
        "1. 標籤：3-5 個簡短標籤，用逗號分隔。\n"
        "2. 路徑：在 VuePress 知識庫中的 md 路徑，用「/」分層，"
        "例如「Linux/發行版/Fedora」或「化學/繪製工具/ketcher」。"
        "不要把檔案堆在根目錄，路徑要分層合理。\n"
        "只輸出以下格式，不要多餘內容：\n"
        "標籤：xxx, xxx\n"
        "路徑：xxx/xxx/xxx"
    )
    content = content[:6000]
    return chat([
        {"role": "system", "content": system},
        {"role": "user", "content": content},
    ])


def ask_summary(content, feedback=None):
    system = (
        "你是簡潔的內容總結助手。用繁體中文，用 2-4 句話簡單總結網頁內容，"
        "不要過於複雜，不要羅列細節，平實易懂。只輸出總結文字本身。"
    )
    if feedback:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": content[:6000]},
            {"role": "assistant", "content": "（已生成的總結）"},
            {"role": "user", "content": f"請根據以下意見修改總結：{feedback}"},
        ]
    else:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": content[:6000]},
        ]
    return chat(messages)
