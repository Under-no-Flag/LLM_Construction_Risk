import os, uuid
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from backend.llms.qwen__vl_api import analyse_risk

from backend.llms.utils import _split_analysis
@csrf_exempt                     # 演示用；生产环境请改成带 CSRF 的 APIView
def upload_and_detect(request):
    """
    接收 Element‑Plus el‑upload 提交的文件并返回可访问 URL
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    f = request.FILES.get("file")             # el‑upload 默认字段名就是 file
    if not f:
        return JsonResponse({"error": "No file"}, status=400)

    # 随机文件名防止冲突
    ext = os.path.splitext(f.name)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(settings.MEDIA_ROOT, "uploads", filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with open(save_path, "wb+") as dst:
        for chunk in f.chunks():
            dst.write(chunk)
        # === 调用 Qwen‑VL 做风险识别 ===
    try:
        analysis_text = analyse_risk(save_path)
    except Exception as e:
        return JsonResponse({"error": f"LLM error: {e}"}, status=500)

    risks, laws = _split_analysis(analysis_text)
    return JsonResponse(
        {
            "url": settings.MEDIA_URL + "uploads/" + filename,  # 让前端能显示图片
            "riskList": risks,                          # 识别结果
            "regulations": laws,
        }
    )
