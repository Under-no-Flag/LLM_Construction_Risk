import os, uuid
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Hazard, Attachment
import json
from django.views.decorators.http import require_http_methods
from backend.hazard_control.kg_service import kg_service

@csrf_exempt
def submit_hazard(request):
    if request.method != "POST":
        return JsonResponse({"code": 1, "msg": "只支持 POST"}, status=400)

    # 1) 读取表单字段
    title = request.POST.get("title", "").strip()
    risk_desc = request.POST.get("riskDescription", "").strip()
    regs_raw = request.POST.get("regulations", "[]")
    uploader = request.POST.get("uploader", "").strip()

    # 2) 简单校验
    if not title or not uploader:
        return JsonResponse({"code": 2, "msg": "标题和上传人必填"}, status=400)

    # 3) regulations 字段解析（如果是 JSON 字符串）
    try:
        regulations = json.loads(regs_raw)
    except json.JSONDecodeError:
        # 如果你用的是 TextField，也可以直接存原字符串
        regulations = regs_raw

    # 4) 新建 Hazard 记录
    hazard = Hazard.objects.create(
        title=title,
        risk_description=risk_desc,
        regulations=regulations,
        uploader=uploader
    )

    # 5) 处理上传的文件列表
    for f in request.FILES.getlist("files"):
        Attachment.objects.create(hazard=hazard, file=f)

    return JsonResponse({"code": 0, "msg": "success"})




def hazard_detail(request, pk):
    # 1. 拿到 Hazard
    hazard = Hazard.objects.get(pk=pk)
    # 2. 附件（假设只有一张主图）
    img_url = None
    att = hazard.attachments.first()
    if att:
        img_url = request.build_absolute_uri(att.file.url)
    # 3. 子图 & 建议：实际中可能存到另一个表，这里示例硬编码或从模型拿
    # try:
    #     graph = kg_service.query_graph(
    #         f"施工现场的风险隐患描述为：{hazard.risk_description}。根据风险隐患描述,拆分隐患描述中各类要素。查找各要素对应有关的法律法规、建筑施工标准和事故报告 。"
    #     )
    #     print(graph)
    # except Exception as e:
    #     graph = []
    #     print(f"知识图谱生成异常: {str(e)}")


    # suggestions = [
    #     # … 从 DB 或按关联逻辑生成 …
    #     '现场所有作业人员进入施工区域前必须正确佩戴合格安全帽，并由安全员现场巡查抽检。',
    #     '在作业临边处安装 1.2 m 高双道防护栏杆，并加挂密目式安全网，夜间作业区加装照明。',
    #     '设置水平生命线，高处作业人员全程系挂安全带并定期检查挂点牢固性。',
    #     '以 JGJ59‑2011 3.13.3 与 JGJ80‑2016 4.1.3 为依据，完成整改后填写隐患关闭单并归档。',
    # ]
    suggestions=[]

    return JsonResponse({
        "hazard": {
            "id": hazard.id,
            "title": hazard.title,
            "uploader": hazard.uploader,
            "riskDescription": hazard.risk_description,
            "image": img_url,
        },
        "graph": None,
        "suggestions": suggestions,
    })

def hazard_list(request):
    """
    返回所有 Hazard 的列表，字段包括：
      - id, title, uploader, status, updated_at
    """
    qs = Hazard.objects.order_by("-updated_at")
    data = []
    for h in qs:
        data.append({
            "id": h.id,
            "title": h.title,
            "uploader": h.uploader,
            "description": h.risk_description,
            # 假设你模型里有个 status 字段，或你可以动态计算
            # "status": h.status,
            "status": h.status,
            "updatedAt": h.updated_at.strftime("%Y-%m-%d %H:%M"),
        })
    return JsonResponse({"data": data})

from backend.llms.query_kg import query_kg_for_suggestion   # ← 刚写好的函数

# 新视图
@csrf_exempt
@require_http_methods(["POST"])
def generate_hazard_suggestion(request, pk: int):
    """
    根据 hazard.risk_description 调用 LLM+KG 生成治理意见
    """
    try:
        hazard = Hazard.objects.get(pk=pk)
    except Hazard.DoesNotExist:
        return JsonResponse({"error": "Hazard not found"}, status=404)

    suggestions = query_kg_for_suggestion(hazard.risk_description)
    return JsonResponse({"suggestions": suggestions["suggestions"]})



@csrf_exempt
@require_http_methods(["POST"])
def retrieve_subgraph(request, pk: int):
    try:
        hazard = Hazard.objects.get(pk=pk)
    except Hazard.DoesNotExist:
        return JsonResponse({"error": "Hazard not found"}, status=404)
    try:
        graph = kg_service.query_graph(
            # f"施工现场的风险隐患描述为：{hazard.risk_description} 根据风险隐患描述,拆分隐患描述中各要素。各要素对应有关的法律法规、建筑施工标准和事故报告有哪些？。"
            f"施工现场的风险隐患描述为：{hazard.risk_description} 根据风险隐患描述、相关安全法规、事故报告、建筑施工标准和条例，指出违反了哪些法律法规和标准？"
        )
        print(graph)
    except Exception as e:
        graph = []
        print(f"知识图谱生成异常: {str(e)}")


    return JsonResponse({"graph": graph})




