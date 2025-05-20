from django.db import models

class Hazard(models.Model):
    title = models.CharField("标题", max_length=255)
    risk_description = models.TextField("风险描述")
    # 如果你的 Django ≥3.1，SQLite 也支持 JSONField，前端以字符串形式提交的 regulations
    # 可以直接存为 JSON：
    regulations = models.JSONField("相关法规", default=list, blank=True)
    uploader = models.CharField("上传人", max_length=100)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    STATUS_CHOICES = [
        ("待处理", "待处理"),
        ("整改中", "整改中"),
        ("已完成", "已完成"),
    ]
    status = models.CharField("状态", max_length=10,
                              choices=STATUS_CHOICES,
                              default="待处理")
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    def __str__(self):
        return self.title

class Attachment(models.Model):
    hazard = models.ForeignKey(Hazard, related_name="attachments", on_delete=models.CASCADE)
    file = models.FileField("附件", upload_to="hazard_files/%Y/%m/%d/")

    def __str__(self):
        return f"{self.hazard.title} - {self.file.name}"
