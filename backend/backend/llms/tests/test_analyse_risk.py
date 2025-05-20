import io
from django.test import TestCase
from django.urls import reverse
import os
print(os.getcwd())
import pytest
from llms.qwen__vl_api import analyse_risk


# class UploadDetectAPITest(TestCase):
#     def _fake_image(self):
#         img = Image.new("RGB", (100, 100), color="red")
#         buf = io.BytesIO()
#         img.save(buf, format="PNG")
#         buf.seek(0)
#         return buf

#     def test_upload_success(self):
#         url = reverse("upload_and_detect")
#         resp = self.client.post(
#             url,
#             data={"file": self._fake_image()},
#             format="multipart"
#         )
#         self.assertEqual(resp.status_code, 200)
#         self.assertIn("url", resp.json())
#         self.assertIn("riskList", resp.json())
#         self.assertIn("regulations", resp.json())


def test_analyse_risk():
    result = analyse_risk(r"D:\LLM_Construction_Risk\backend\media\uploads\bad36013a71844a5b0793fd01d0457e6.png")
    assert isinstance(result, str), "Result should be a string"
    print(result)