# backend/hazard_control/apps.py
from django.apps import AppConfig

class HazardControlConfig(AppConfig):
    name = 'backend.hazard_control'
    verbose_name = '隐患管理'

    def ready(self):
        """应用启动时初始化知识图谱服务"""
        try:
            from .kg_service import kg_service
            print("知识图谱服务初始化成功")
        except Exception as e:
            print(f"知识图谱服务初始化失败: {str(e)}")
            raise