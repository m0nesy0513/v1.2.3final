import json
from typing import Optional

from utils.deepseek_client import ask_deepseek
from utils.vector_store import search_similar
from utils.web_search import search_web

RULES_PATH = "rules/genealogy_rules.json"


def load_rules_text(max_rules: int = 20) -> str:
    try:
        with open(RULES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        rules = data.get("rules", [])[:max_rules]
        lines = []

        for rule in rules:
            rule_id = rule.get("id", "")
            name = rule.get("name", "")
            desc = rule.get("description", "")
            suggestion = rule.get("suggestion", "")
            lines.append(f"{rule_id} | {name} | {desc} | 建议：{suggestion}")

        return "\n".join(lines)[:1200]
    except Exception:
        return ""


def rag_answer(question: str, index, texts, current_genealogy_text: Optional[str] = "") -> str:
    rag_hits = search_similar(question, index, texts, top_k=3)

    rag_context = "\n\n".join(rag_hits)[:1500]
    rules_context = load_rules_text()
    web_context = search_web(question)
    current_context = (current_genealogy_text or "")[:2000]

    prompt = f"""
你是一个族谱校勘助手。请结合以下资料回答问题。

【规则库】
{rules_context}

【审查案例知识库】
{rag_context}

【联网资料】
{web_context}

【当前族谱】
{current_context}

【问题】
{question}

请用中文回答，并尽量清晰、简洁、分点。
"""

    messages = [{"role": "user", "content": prompt}]
    return ask_deepseek(messages)


def analyze_genealogy(text: str, index, texts) -> str:
    query = "请分析这份族谱，指出结构问题、关系冲突、迁徙问题与修改建议。"

    rag_hits = search_similar(query, index, texts, top_k=3)

    rag_context = "\n\n".join(rag_hits)[:1500]
    rules_context = load_rules_text()
    web_context = search_web(query)
    current_context = text[:20000]

    prompt = f"""
你是一个专业的族谱校勘专家。

请结合以下资料，分析用户上传的族谱，并输出结构化校勘报告。

【规则库】
{rules_context}

【审查案例知识库】
{rag_context}

【联网资料】
{web_context}

【当前族谱】
{current_context}

请输出：
1. 总体判断
2. 发现的问题
3. 修改建议
4. 优先处理项

要求：中文输出，清晰、简洁、适合普通用户阅读。
"""

    messages = [{"role": "user", "content": prompt}]
    return ask_deepseek(messages)
