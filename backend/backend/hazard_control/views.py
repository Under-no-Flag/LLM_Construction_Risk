import os, uuid
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Hazard, Attachment
import json


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
    graph = [
        { 'data': { 'id': 'risk_helmet', 'label': '未佩戴安全帽' } },
        { 'data': { 'id': 'risk_edge', 'label': '临边无防护' } },
        { 'data': { 'id': 'risk_harness', 'label': '未系安全带' } },

        # 措施节点
        { 'data': { 'id': 'measure_helmet', 'label': '全员佩戴安全帽' } },
        { 'data': { 'id': 'measure_edge', 'label': '设防护栏杆/安全网' } },
        { 'data': { 'id': 'measure_harness', 'label': '系挂安全带+生命线' } },

        # // 法规节点
        {
            'data': {
                'id': 'spec_59_hat',
                'label': 'JGJ59-2011 3.13.3(1)',
            },
        },
        {
            'data': {
                'id': 'spec_80_edge',
                'label': 'JGJ80-2016 4.1.3',
            },
        },
        {
            'data': {
                'id': 'spec_59_harness',
                'label': 'JGJ59-2011 3.13.3(3)',
            },
        },

        # // 风险→措施 边
        { 'data': { 'source': 'risk_helmet', 'target': 'measure_helmet', 'label': '治理' } },
        { 'data': { 'source': 'risk_edge', 'target': 'measure_edge', 'label': '治理' } },
        { 'data': { 'source': 'risk_harness', 'target': 'measure_harness', 'label': '治理' } },
        # // 措施→法规 边
        { 'data': { 'source': 'measure_helmet', 'target': 'spec_59_hat', 'label': '依据' } },
        { 'data': { 'source': 'measure_edge', 'target': 'spec_80_edge', 'label': '依据' } },
        { 'data': { 'source': 'measure_harness', 'target': 'spec_59_harness', 'label': '依据' } },
    ]


    suggestions = [
        # … 从 DB 或按关联逻辑生成 …
        '现场所有作业人员进入施工区域前必须正确佩戴合格安全帽，并由安全员现场巡查抽检。',
        '在作业临边处安装 1.2 m 高双道防护栏杆，并加挂密目式安全网，夜间作业区加装照明。',
        '设置水平生命线，高处作业人员全程系挂安全带并定期检查挂点牢固性。',
        '以 JGJ59‑2011 3.13.3 与 JGJ80‑2016 4.1.3 为依据，完成整改后填写隐患关闭单并归档。',
    ]

    return JsonResponse({
        "hazard": {
            "id": hazard.id,
            "title": hazard.title,
            "uploader": hazard.uploader,
            "riskDescription": hazard.risk_description,
            "image": img_url,
        },
        "graph": graph,
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
            # 假设你模型里有个 status 字段，或你可以动态计算
            # "status": h.status,
            "status": "未处理",
            "updatedAt": h.updated_at.strftime("%Y-%m-%d %H:%M"),
        })
    return JsonResponse({"data": data})


