import os, uuid
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from backend.llms.qwen__vl_api import analyse_risk

from backend.llms.utils import _split_analysis,llm_str2json
@csrf_exempt                     # 演示用；生产环境请改成带 CSRF 的 APIView
def upload_and_detect(request):
    """
    接收 Element‑Plus el‑upload 提交的文件并返回可访问 URL
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    f = request.FILES.get("image")             # el‑upload 默认字段名就是 file
    if not f:
        return JsonResponse({"error": "No image"}, status=400)

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

    data= llm_str2json(analysis_text)
    return JsonResponse(
        {
            "url": settings.MEDIA_URL + "uploads/" + filename,  # 让前端能显示图片
            "data": data,                          # 识别结果
        }
    )


#     return JsonResponse(
#         {
#             "url": settings.MEDIA_URL + "uploads/" + "test",  # 让前端能显示图片
#             "data": {'riskDescription': '图片中的建筑施工存在以下安全风险：1. 施工人员未佩戴安全帽；2. 施工现场缺乏防护措施，如护栏或安全网；3. 施工人员站在不稳定的平台上工作，存在跌落风 \
# 险。', 'regulations': [{'title': '《建设工程安全生产管理条例》', 'code': '国务院令第393号', 'content': '第二十八条 施工单位应当根据不同施工阶段和周围环境及季节、气候的 \
# 变化，在施工现场采取相应的安全施工措施。施工单位应当对因建设工程施工可能造成损害的毗邻建筑物、构筑物和地下管线等，采取专项防护措施。'}, {'title': '《建筑施工高处作业安 \
# 全技术规范》', 'code': 'JGJ80-2016', 'content': '4.2.1 高处作业人员必须按规定正确使用安全带（绳）。安全带（绳）应挂在牢固的构件上，并不得低挂高用。作业中严禁用手抓住棱 \
# 角处系挂安全带。'}]},                          # 识别结果
#         }
#     )
