
import re
import json
from typing import Dict, List
def _split_analysis(raw: str):
    """
    将 Qwen‑VL 返回的文本切成
      ① 风险列表      ② 依据列表
    形如：
        1. **缺乏防护措施**：
           - xxx
           - xxx
    """
    # 先用 “依据” 分成两段
    if "依据" in raw:
        risk_txt, law_txt = raw.split("依据", 1)
    else:                               # 容错：万一没写“依据”
        risk_txt, law_txt = raw, ""

    # ---- 解析风险 ----
    risk_items = []
    # 找 1. 2. 3. 或 “- ” 开头的行
    for line in risk_txt.splitlines():
        line = line.strip()
        m = re.match(r"^\d+\.\s*\*\*(.*?)\*\*", line)  # **标题**
        if m:
            current = {"title": m.group(1), "details": []}
            risk_items.append(current)
        elif line.startswith("-") and risk_items:
            risk_items[-1]["details"].append(line.lstrip("-• ").strip())

    # ---- 解析依据 ----
    law_items = []
    for line in law_txt.splitlines():
        line = line.strip(" -")
        if not line:
            continue
        # 《xxx》 或 ISO 45001 之类
        m = re.match(r"^《?(.*?)》?\s*(.*)", line)
        if m:
            title, rest = m.groups()
            law_items.append({"title": title, "content": rest})

    return risk_items, law_items




risk_re = re.compile(
    r'"?riskDescription"?\s*:\s*"(?P<risk>[^"]+)"', re.S)

# 抓取 {...} 内部字段三元组；容忍空格/换行
reg_re = re.compile(
    r'{"?\s*title"?\s*:\s*"(?P<title>[^"]+)"\s*,\s*'
    r'"?code"?\s*:\s*"(?P<code>[^"]+)"\s*,\s*'
    r'"?content"?\s*:\s*"(?P<content>[^"]+?)"\s*}',  # 非贪婪
    re.S
)

def llm_str2json_regex(raw: str) -> Dict[str, object]:
    """
    将大模型返回的“伪 JSON”整理成 {'riskDescription': str, 'regulations': [ {...}, ... ]}
    若字段找不到，返回空字符串/空列表，而不是抛异常。
    """
    if not raw:
        return {"riskDescription": "", "regulations": []}

    # 0) 统一引号 & 去掉换行导致的 JSON 断行
    txt = raw.replace("“", "\"").replace("”", "\"").replace("\n", "")

    # 1) riskDescription – 取第一个匹配
    risk_match = risk_re.search(txt)
    risk_desc = risk_match.group("risk").strip() if risk_match else ""

    # 2) regulations – 抓所有完整 {...}
    regulations: List[Dict[str, str]] = []
    for m in reg_re.finditer(txt):
        reg = {
            "title": m.group("title").strip(),
            "code": m.group("code").strip(),
            "content": m.group("content").strip()
        }
        # 去重（有时大模型会重复同一段对象）
        if reg not in regulations:
            regulations.append(reg)

    return {"riskDescription": risk_desc, "regulations": regulations}


def llm_str2json(text: str) -> Dict:
    """
    把大模型返回的字符串解析成 Python 字典。
    常见格式问题（markdown 代码块、换行、尾逗号等）都会顺带处理。
    """
    if not text:
        raise ValueError("空字符串，无法解析")

    # 1去掉 markdown 代码围栏 ```json ... ```
    text = text.strip()
    if text.startswith("```"):
        # 把第一行 ```xxx 和最后一行 ``` 去掉
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()

    # 2用正则抓取第一个 { … }，支持跨行
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        raise ValueError("未找到 JSON 对象")
    json_str = m.group(0)

    # 清理常见语法瑕疵：尾逗号、Windows 回车
    json_str = re.sub(r",\s*}", "}", json_str)   # 尾逗号 + }
    json_str = re.sub(r",\s*]", "]", json_str)   # 尾逗号 + ]
    json_str = json_str.replace("\r\n", "\n")

    # 反序列化
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失败: {e}\n原始文本:\n{json_str}")