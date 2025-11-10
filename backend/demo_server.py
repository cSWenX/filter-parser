"""
简化版Flask应用 - 用于演示
只使用基础功能，不依赖OpenCV等复杂库
"""
import json
import os
import time
from datetime import datetime
import hashlib
import random

# 简单的HTTP服务器
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
import mimetypes

class FilterParserHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/Users/cswenx/program/AICoding/Filter-Parser", **kwargs)

    def do_POST(self):
        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            self.send_error(404)

    def do_GET(self):
        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            # 处理静态文件
            if self.path == '/':
                self.path = '/frontend/public/index.html'
            super().do_GET()

    def handle_api_request(self):
        try:
            # 解析路径
            path = self.path.replace('/api', '')

            if path == '/health':
                self.send_json_response({
                    "status": "success",
                    "message": "服务运行正常",
                    "data": {
                        "status": "healthy",
                        "upload_folder_size_mb": 0,
                        "output_folder_size_mb": 0,
                        "upload_files_count": 0,
                        "output_files_count": 0
                    }
                })

            elif path == '/upload' and self.command == 'POST':
                # 模拟图片上传
                image_id = self.generate_id()
                self.send_json_response({
                    "status": "success",
                    "message": "上传成功",
                    "data": {
                        "image_id": image_id,
                        "filename": "demo_image.jpg",
                        "file_size": 1024000,
                        "dimensions": [800, 600]
                    }
                })

            elif path.startswith('/analyze/') and self.command == 'POST':
                # 模拟参数分析
                image_id = path.split('/')[-1]
                time.sleep(1)  # 模拟处理时间

                # 生成模拟参数
                params = self.generate_mock_parameters()

                self.send_json_response({
                    "status": "success",
                    "message": "分析完成",
                    "data": {
                        "image_id": image_id,
                        "parameters": params,
                        "analysis_time": 2.1,
                        "confidence_score": 0.85,
                        "suggestions": [
                            "该参数组合适合风景类图片",
                            "可直接用于Lightroom/PS"
                        ]
                    }
                })

            else:
                self.send_error(404, "API接口不存在")

        except Exception as e:
            self.send_json_response({
                "status": "error",
                "message": f"服务器错误: {str(e)}"
            }, 500)

    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(json_data.encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def generate_id(self):
        return hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:16]

    def generate_mock_parameters(self):
        """生成模拟的分析参数"""
        return {
            "brightness": {
                "name": "亮度",
                "direction": "增加",
                "value": 15.2,
                "unit": "%",
                "reference": "sRGB 标准色彩"
            },
            "contrast": {
                "name": "对比度",
                "direction": "增加",
                "value": 22.8,
                "unit": "%",
                "reference": "灰度阶差分析"
            },
            "saturation": {
                "name": "饱和度",
                "direction": "增加",
                "value": 18.5,
                "unit": "%",
                "reference": "HSV 色彩模型"
            },
            "sharpness": {
                "name": "锐化",
                "direction": "增强",
                "value": 12.3,
                "unit": "%",
                "reference": "边缘清晰度算法"
            },
            "temperature": {
                "name": "色温",
                "direction": "偏暖",
                "value": 150,
                "unit": "K",
                "reference": "标准色温 6500K"
            },
            "hue": {
                "name": "色调",
                "direction": "偏红",
                "value": 8.2,
                "unit": "°",
                "reference": "RGB 通道占比"
            },
            "shadow": {
                "name": "阴影",
                "direction": "提亮",
                "value": 10.5,
                "unit": "%",
                "reference": "暗部像素占比"
            },
            "highlight": {
                "name": "高光",
                "direction": "降低",
                "value": 5.8,
                "unit": "%",
                "reference": "亮部像素占比"
            }
        }

if __name__ == '__main__':
    port = 5000
    server = HTTPServer(('localhost', port), FilterParserHandler)
    print(f"🚀 Filter Parser 后端服务已启动")
    print(f"📍 地址: http://localhost:{port}")
    print(f"🔍 健康检查: http://localhost:{port}/api/health")
    print(f"💡 这是一个演示版本，使用模拟数据")
    print("按 Ctrl+C 停止服务")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
        server.shutdown()