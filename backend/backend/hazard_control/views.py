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


