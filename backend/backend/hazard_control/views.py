import os, uuid
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def submit_hazard(hazard_info):
    return JsonResponse({
        'code':0,
        'msg': 'success'
    }
    )


