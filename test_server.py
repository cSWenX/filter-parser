#!/usr/bin/env python3
"""
简化的测试服务器 - 专门用于调试上传问题
"""
import http.server
import socketserver
import json
import os
import time
from datetime import datetime

class TestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/Users/cswenx/program/AICoding/Filter-Parser", **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        print("Received OPTIONS request")
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        print(f"POST: {self.path}")
        if self.path.startswith('/api/'):
            self.handle_api_post()
        else:
            self.send_error(404)

    def do_GET(self):
        print(f"GET: {self.path}")
        if self.path.startswith('/api/'):
            self.handle_api_get()
        else:
            super().do_GET()

    def handle_api_post(self):
        api_path = self.path.replace('/api', '')
        if '?' in api_path:
            api_path = api_path.split('?')[0]

        print(f"API POST Path: {api_path}")
        print(f"Content-Type: {self.headers.get('Content-Type', 'None')}")
        print(f"Content-Length: {self.headers.get('Content-Length', 'None')}")

        if api_path == '/upload':
            self.handle_upload_post()
        elif api_path.startswith('/analyze/'):
            self.handle_analyze_post(api_path)
        elif api_path == '/health':
            self.handle_health()
        else:
            self.send_json_error(404, "API endpoint not found")

    def handle_api_get(self):
        api_path = self.path.replace('/api', '')
        if '?' in api_path:
            api_path = api_path.split('?')[0]

        print(f"API GET Path: {api_path}")

        if api_path == '/health':
            self.handle_health()
        else:
            self.send_json_error(404, "API endpoint not found")

    def handle_upload_post(self):
        print("=== UPLOAD REQUEST ===")
        print(f"Method: {self.command}")
        print(f"Headers: {dict(self.headers)}")

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            print(f"Content Length: {content_length}")

            if content_length > 0:
                post_data = self.rfile.read(content_length)
                print(f"Data received: {len(post_data)} bytes")

            # 生成成功响应
            image_id = f"img_{int(time.time() * 1000)}"
            response_data = {
                "status": "success",
                "message": "上传成功",
                "data": {
                    "image_id": image_id,
                    "filename": "test_image.jpg",
                    "file_size": 1024,
                    "dimensions": [800, 600]
                }
            }
            print("Sending success response")
            self.send_json_response(response_data)

        except Exception as e:
            print(f"Upload error: {e}")
            self.send_json_error(500, f"Upload failed: {str(e)}")

    def handle_analyze_post(self, api_path):
        print("=== ANALYZE REQUEST ===")
        image_id = api_path.split('/')[-1]
        print(f"Analyzing image: {image_id}")

        # 模拟分析延迟
        import time
        time.sleep(1)

        # 生成模拟分析结果
        response_data = {
            "status": "success",
            "message": "分析完成",
            "data": {
                "image_id": image_id,
                "parameters": {
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
                    }
                },
                "analysis_time": 2.1,
                "confidence_score": 0.85,
                "suggestions": [
                    "该参数组合适合风景类图片",
                    "建议在秋季、暖色调场景中使用",
                    "适合需要增强色彩饱和度的图片"
                ]
            }
        }
        print("Sending analysis response")
        self.send_json_response(response_data)

    def handle_health(self):
        response_data = {
            "status": "success",
            "message": "Test server running",
            "data": {
                "timestamp": datetime.now().isoformat()
            }
        }
        self.send_json_response(response_data)

    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(json_str.encode('utf-8'))

    def send_json_error(self, status_code, message):
        error_data = {
            "status": "error",
            "message": message,
            "error_code": f"HTTP_{status_code}"
        }
        self.send_json_response(error_data, status_code)

def main():
    PORT = 8081  # 使用不同端口避免冲突
    os.chdir('/Users/cswenx/program/AICoding/Filter-Parser')

    with socketserver.TCPServer(("", PORT), TestHandler) as httpd:
        print(f"🧪 Test server running on http://localhost:{PORT}")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nTest server stopped")

if __name__ == '__main__':
    main()