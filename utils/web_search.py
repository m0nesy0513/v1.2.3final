import re
import requests
import streamlit as st


def _clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def search_tavily(query: str) -> str:
    key = st.secrets.get("TAVILY_API_KEY")
    if not key:
        return ""

    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": key,
                "query": query,
                "max_results": 5
            },
            timeout=20
        )

        if resp.status_code != 200:
            return ""

        data = resp.json()
        results = []

        for item in data.get("results", []):
            content = item.get("content", "").strip()
            if content:
                results.append(content)

        return "\n".join(results)[:1500]
    except Exception:
        return ""


def search_jina(query: str) -> str:
    try:
        resp = requests.get(f"https://search.jina.ai?q={query}", timeout=20)
        if resp.status_code != 200:
            return ""

        return _clean_text(resp.text)[:1500]
    except Exception:
        return ""


def search_web(query: str) -> str:
    res = search_tavily(query)
    if res:
        return res
    return search_jina(query)
