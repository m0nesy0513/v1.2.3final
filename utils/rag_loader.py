import os
from typing import List, Dict

from utils.docx_parser import parse_docx


def load_knowledge_base(folder: str) -> List[Dict]:
    documents = []

    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        return documents

    for file_name in sorted(os.listdir(folder)):
        if not file_name.lower().endswith(".docx"):
            continue

        path = os.path.join(folder, file_name)

        if not os.path.isfile(path):
            continue

        try:
            text = parse_docx(path)
            if text.strip():
                documents.append({
                    "file_name": file_name,
                    "text": text
                })
        except Exception:
            continue

    return documents
