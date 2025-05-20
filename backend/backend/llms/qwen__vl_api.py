# # utils.py
# import os
# from pathlib import Path
# os.environ['DASHSCOPE_API_KEY']='sk-854797802db342189c61fff60950715d'

# from llama_index.multi_modal_llms.dashscope import (
#     DashScopeMultiModal,
#     DashScopeMultiModalModels,
# )
# from llama_index.core.base.llms.types import (
#     ChatMessage, MessageRole,
#     ImageBlock, TextBlock,
# )
# from llama_index.core.multi_modal_llms.generic_utils import load_image_urls

# # 单例：避免每次创建模型带来的额外时延
# _mm_llm = DashScopeMultiModal(model_name=DashScopeMultiModalModels.QWEN_VL_MAX)

# # PROMPT = "图片中的建筑施工安全风险有哪些？不合规之处有吗？请给出依据。返回格式json格式{'riskDescription':'......安全隐患描述','regulations':[{\
# #     'title':'...安全法规或标准名称','code':'法规或标准的代码，如JGJ59-2011)','content':'法规的具体内容'},{...}]}。请用中文回答，不要用英文。"
# PROMPT = "图片中的建筑施工安全风险有哪些?"

# def analyse_risk(image_path: str) -> str:
#     """
#     调用 Qwen‑VL Max 返回一段中文分析文本
#     """
#     # 1. 构造 blocks 列表（先图后文本）
#     blocks = [
#         ImageBlock(url=str(Path(image_path).absolute())),  # 本地文件自动 base64
#         TextBlock(text=PROMPT),
#     ]

#     # 2. 封装成 ChatMessage 并调用 .chat
#     msg = ChatMessage(role=MessageRole.USER, blocks=blocks)
#     resp = _mm_llm.chat(messages=[msg])
#     print(resp.message)
#     return resp.message  # .message 等价于 .text

# if __name__=="__main__":
#     # test_analyse_risk()
#     analyse_risk(r"D:\LLM_Construction_Risk\backend\media\uploads\bad36013a71844a5b0793fd01d0457e6.png")


# utils_raw.py
import os
from pathlib import Path
import dashscope
from dashscope import MultiModalConversation    # 核心类

# ① 设置 API-Key（也可以提前 export DASHSCOPE_API_KEY=xxx）
os.environ['DASHSCOPE_API_KEY']='sk-854797802db342189c61fff60950715d'
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY", "sk-854797802db342189c61fff60950715d")

# PROMPT = "图片中的建筑施工安全风险有哪些？"
# PROMPT = "图片中的建筑施工安全风险有哪些？不合规之处有吗？请给出依据。返回格式json，格式如下：{'riskDescription':'......安全隐患描述','regulations':[{\
#     'title':'...安全法规或标准名称','code':'法规或标准的代码，如JGJ59-2011)','content':'法规的具体内容'},{...}]}。请用中文回答，不要用英文。"

PROMPT = "图片中的建筑施工安全风险有哪些？不合规之处有吗？请给出依据。请用中文回答，不要用英文。返回格式json，格式如下：{'riskDescription':'......','regulations':[{\
    'title':'安全法规或标准名称','code':'法规或标准的代码，如JGJ59-2011)','content':'法规的具体内容'},{...}]}。请用中文回答，不要用英文。"

def analyse_risk(image_path: str) -> str:
    abs_path = Path(image_path).expanduser().resolve()

    messages = [
        {
            "role": "user",
            "content": [
                {"image": f"file://{abs_path}"},
                {"text": PROMPT},
            ],
        }
    ]

    # ② 直接调用，多模态模型名固定写字符串
    resp = MultiModalConversation.call(
        model="qwen-vl-max",          # 也可换成 qwen-vl-plus 等
        messages=messages,
        # vl_high_resolution_images=True   # 需要超清时再打开
    )

    # ③ 错误处理：非 200 均返回 .status_code != 200
    if resp.status_code != 200:
        raise RuntimeError(f"DashScope error: {resp.message}")

    # ④ 拿文本：content 是列表 ⇒ 第 0 个元素 ⇒ "text"
    return resp.output["choices"][0]["message"]["content"][0]["text"]

if __name__ == "__main__":

    result=analyse_risk(
            r"D:\LLM_Construction_Risk\backend\media\uploads\bad36013a71844a5b0793fd01d0457e6.png"
    )
    from utils import llm_str2json
    print(llm_str2json(result))

