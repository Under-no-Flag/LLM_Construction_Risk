# utils.py
import os
from pathlib import Path
os.environ['DASHSCOPE_API_KEY']='sk-854797802db342189c61fff60950715d'

from llama_index.multi_modal_llms.dashscope import (
    DashScopeMultiModal,
    DashScopeMultiModalModels,
)
from llama_index.core.multi_modal_llms.generic_utils import load_image_urls

# 单例：避免每次创建模型带来的额外时延
_mm_llm = DashScopeMultiModal(model_name=DashScopeMultiModalModels.QWEN_VL_MAX)

PROMPT = "图片中的建筑施工安全风险有哪些？不合规之处有吗？请给出依据。"

def analyse_risk(image_path: str) -> str:
    """
    调用 Qwen‑VL Max 返回一段中文分析文本
    """
    docs = load_image_urls([image_path])
    print(image_path)
    resp = _mm_llm.complete(prompt=PROMPT, image_documents=docs)
    print(resp.text)
    return resp.text  # llama‑index >= 0.10 把内容存在 .text
