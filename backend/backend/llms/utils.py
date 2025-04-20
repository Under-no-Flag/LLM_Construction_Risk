import re, json
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