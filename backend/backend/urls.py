"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from backend.llms.views import upload_and_detect
from backend.hazard_control.views import submit_hazard,hazard_detail,hazard_list

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/upload_and_detect/", upload_and_detect, name="api-upload"),
    path("api/submit_hazard/", submit_hazard, name="submit-hazard"),
    path('hazard/<int:pk>/', hazard_detail,name='hazard-detail'),
    path("api/hazards/", hazard_list),
]

# 让 runserver 能直接回媒体文件（生产请交给 Nginx）
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

