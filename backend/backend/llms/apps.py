from django.apps import AppConfig


class llmsConfig(AppConfig):
    """
    把所有大模型相关的初始化放到 ready()
    Django 进程启动时只会执行一次。
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.llms"          # ← 注意用完整包路径

    def ready(self):
        # 触发 deepseek_config 的 import
        # 里面的 LLM / embedding / Neo4j index 会立即加载到内存
        from . import deepseek_config  # noqa: F401
