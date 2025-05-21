import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files import File
from backend.hazard_control.models import Hazard, Attachment

class Command(BaseCommand):
    help = "Seed the database with fictional Hazard and Attachment data"

    def handle(self, *args, **options):
        # 1) 清空已有数据
        self.stdout.write("Clearing existing Hazard and Attachment data...")
        Attachment.objects.all().delete()
        Hazard.objects.all().delete()

        # 2) 示例数据列表，新增 image_path 字段
        sample_data = [
            {
                "title": "混凝土搅拌车作业风险",
                "risk_description": "1. 工人未佩戴安全帽，存在头部受伤的风险；2. 施工现场没有明显的安全警示标志，可能导致工人和路人忽视潜在的危险；3. 混凝土搅拌车周围有散落的建筑材料，可能造成绊倒或滑倒事故；4. 施工区域没有设置有效的隔离措施，可能导致非施工人员误入施工现场。",
                "regulations": ["国务院令第393号"],
                "uploader": "李四",
                "status": "待处理",
                "image_path": "media/demo_images/3.png",
            },
            {
                "title": "夜间高空作业风险",
                "risk_description": "图片中的建筑施工存在以下安全风险：1. 施工人员未佩戴安全帽；2. 施工现场缺乏防护措施，如护栏或安全网；3. 施工人员站在不稳定的平台上工作，存在跌落风险。",
                "regulations": ["JGJ59-2011 3.13.3(3)"],
                "uploader": "王五",
                "status": "待处理",
                "image_path": "media/demo_images/1.png",
            },
            {
                "title": "脚手架搭设不规范",
                "risk_description": "脚手架连接松动，缺少必要的横杆支撑，存在坠落风险。",
                "regulations": ["JGJ59-2011 3.13.3(1)", "JGJ80-2016 4.1.3"],
                "uploader": "张三",
                "status": "待处理",
                "image_path": "media/demo_images/2.png",
            },
            {
                "title": "配电箱门未关闭",
                "risk_description": "配电箱门开启，电气元件裸露，存在触电风险。",
                "regulations": ["GB50303-2015 5.1.2"],
                "uploader": "李四",
                "status": "整改中",
                "image_path": "media/demo_images/1.png",
            },
            {
                "title": "裸露钢筋未做防护",
                "risk_description": "施工现场裸露钢筋突出，未采取防护措施，存在刺伤风险。",
                "regulations": ["JGJ59-2011 3.13.3(3)"],
                "uploader": "王五",
                "status": "已完成",
                "image_path": "media/demo_images/2.png",
            },


        ]

        # 3) 插入数据并创建附件（优先图片，否则回退文本附件）
        for item in sample_data:
            hazard = Hazard.objects.create(
                title=item["title"],
                risk_description=item["risk_description"],
                regulations=item["regulations"],
                uploader=item["uploader"],
                status=item["status"]
            )
            img_path = item.get("image_path")
            if img_path:
                abs_path = os.path.join(settings.BASE_DIR, img_path)
                if os.path.exists(abs_path):
                    with open(abs_path, "rb") as f:
                        django_file = File(f, name=os.path.basename(abs_path))
                        Attachment.objects.create(hazard=hazard, file=django_file)
                    self.stdout.write(self.style.SUCCESS(f"Attached image: {abs_path}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Image not found: {abs_path}, creating text attachment instead."))
            if not hazard.attachments.exists():
                dummy_content = ContentFile(
                    f"附件说明：针对隐患 '{item['title']}' 的示例文件内容。".encode("utf-8"),
                    name=f"hazard_{hazard.id}_example.txt"
                )
                Attachment.objects.create(hazard=hazard, file=dummy_content)
                self.stdout.write(self.style.SUCCESS(f"Created dummy text attachment for Hazard(id={hazard.id})"))

        self.stdout.write(self.style.SUCCESS("Database seeding completed."))
