import time
import requests
import streamlit as st

API_URL = "https://api.deepseek.com/v1/chat/completions"


def ask_deepseek(messages, model: str = "deepseek-chat") -> str:
    api_key = st.secrets.get("DEEPSEEK_API_KEY")

    if not api_key:
        return "未配置 DeepSeek API Key。"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2
    }

    last_error = "AI请求失败"

    for attempt in range(3):
        try:
            resp = requests.post(API_URL, headers=headers, json=payload, timeout=60)

            if resp.status_code != 200:
                try:
                    data = resp.json()
                    last_error = data.get("error", {}).get("message", f"HTTP {resp.status_code}")
                except Exception:
                    last_error = f"HTTP {resp.status_code}"
                time.sleep(2 ** attempt)
                continue

            data = resp.json()

            if "choices" in data and data["choices"]:
                return data["choices"][0]["message"]["content"]

            last_error = "DeepSeek 返回数据格式异常。"

        except requests.RequestException as e:
            last_error = f"网络请求失败：{e}"
            time.sleep(2 ** attempt)
        except Exception as e:
            last_error = f"请求失败：{e}"
            time.sleep(2 ** attempt)

    return f"AI请求失败：{last_error}"
