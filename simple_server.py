#!/usr/bin/env python3
"""
Simple test server for debugging API issues
"""
import http.server
import socketserver
import json
import os
import time
import random
from datetime import datetime

class SimpleHandler(http.server.SimpleHTTPRequestHandler):
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

        if api_path == '/upload':
            self.handle_upload()
        elif api_path.startswith('/analyze/'):
            self.handle_analyze(api_path)
        elif api_path == '/generate':
            self.handle_generate()
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

    def handle_upload(self):
        print("=== UPLOAD REQUEST ===")
        print(f"Method: {self.command}")
        print(f"Headers: {dict(self.headers)}")

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                print(f"Data received: {len(post_data)} bytes")

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
            print("Sending upload success response")
            self.send_json_response(response_data)

        except Exception as e:
            print(f"Upload error: {e}")
            self.send_json_error(500, f"Upload failed: {str(e)}")

    def handle_analyze(self, api_path):
        print("=== ANALYZE REQUEST ===")
        image_id = api_path.split('/')[-1]
        print(f"Analyzing image: {image_id}")

        time.sleep(1)

        # 为每个图片生成不同的随机参数
        # 设置种子为图片ID的hash，确保同一图片总是得到相同结果，但不同图片有不同结果
        random.seed(hash(image_id) % 10000)

        # 生成随机参数值
        brightness_val = round(random.uniform(-30, 30), 1)
        contrast_val = round(random.uniform(-25, 35), 1)
        saturation_val = round(random.uniform(-20, 40), 1)
        sharpness_val = round(random.uniform(0, 25), 1)
        temperature_val = random.randint(-300, 300)
        hue_val = round(random.uniform(-15, 15), 1)
        shadow_val = round(random.uniform(-20, 30), 1)
        highlight_val = round(random.uniform(-30, 20), 1)

        # 生成方向描述
        def get_direction(value, positive="增加", negative="减少", zero="不变"):
            if value > 5:
                return positive
            elif value < -5:
                return negative
            else:
                return "轻微调整"

        # 生成随机建议
        suggestions_pool = [
            "该参数组合适合风景类图片，可直接用于 Lightroom/PS",
            "建议在秋季、暖色调场景中使用",
            "适合需要增强色彩饱和度的图片",
            "适合人像摄影后期处理",
            "建议在夜景拍摄中使用",
            "适合提升图片整体明亮感",
            "建议用于增强画面对比度",
            "适合处理曝光不足的图片",
            "建议用于营造温暖氛围",
            "适合处理偏暗的室内照片",
            "建议用于突出主体层次感",
            "适合处理逆光拍摄的照片"
        ]

        selected_suggestions = random.sample(suggestions_pool, 3)

        response_data = {
            "status": "success",
            "message": "分析完成",
            "data": {
                "image_id": image_id,
                "parameters": {
                    "brightness": {
                        "name": "亮度",
                        "direction": get_direction(brightness_val, "增加", "降低"),
                        "value": brightness_val,
                        "unit": "%",
                        "reference": "sRGB 标准色彩"
                    },
                    "contrast": {
                        "name": "对比度",
                        "direction": get_direction(contrast_val, "增加", "降低"),
                        "value": contrast_val,
                        "unit": "%",
                        "reference": "灰度阶差分析"
                    },
                    "saturation": {
                        "name": "饱和度",
                        "direction": get_direction(saturation_val, "增加", "降低"),
                        "value": saturation_val,
                        "unit": "%",
                        "reference": "HSV 色彩模型"
                    },
                    "sharpness": {
                        "name": "锐化",
                        "direction": "增强" if sharpness_val > 0 else "不变",
                        "value": sharpness_val,
                        "unit": "%",
                        "reference": "边缘清晰度算法"
                    },
                    "temperature": {
                        "name": "色温",
                        "direction": "偏暖" if temperature_val > 0 else "偏冷" if temperature_val < 0 else "中性",
                        "value": temperature_val,
                        "unit": "K",
                        "reference": "标准色温 6500K"
                    },
                    "hue": {
                        "name": "色调",
                        "direction": "偏红" if hue_val > 0 else "偏绿" if hue_val < 0 else "中性",
                        "value": hue_val,
                        "unit": "°",
                        "reference": "RGB 通道占比"
                    },
                    "shadow": {
                        "name": "阴影",
                        "direction": get_direction(shadow_val, "提亮", "压暗"),
                        "value": shadow_val,
                        "unit": "%",
                        "reference": "暗部像素占比"
                    },
                    "highlight": {
                        "name": "高光",
                        "direction": get_direction(highlight_val, "提亮", "降低"),
                        "value": highlight_val,
                        "unit": "%",
                        "reference": "亮部像素占比"
                    }
                },
                "analysis_time": round(random.uniform(1.5, 3.2), 1),
                "confidence_score": round(random.uniform(0.75, 0.95), 2),
                "suggestions": selected_suggestions
            }
        }
        print("Sending analysis response")
        self.send_json_response(response_data)

    def handle_generate(self):
        print("=== GENERATE REQUEST ===")

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                print(f"Generate request data: {data}")

            # 模拟处理时间
            time.sleep(1.5)

            # 生成输出文件ID
            output_id = f"output_{int(time.time() * 1000)}"

            response_data = {
                "status": "success",
                "message": "滤镜生成完成",
                "data": {
                    "output_image_id": output_id,
                    "output_filename": f"{output_id}.jpg",
                    "processing_time": 1.5,
                    "download_url": f"/api/download/{output_id}"
                }
            }
            print("Sending generate success response")
            self.send_json_response(response_data)

        except Exception as e:
            print(f"Generate error: {e}")
            self.send_json_error(500, f"Generate failed: {str(e)}")

    def handle_health(self):
        response_data = {
            "status": "success",
            "message": "服务运行正常",
            "data": {
                "timestamp": datetime.now().isoformat(),
                "server": "simple_test_server"
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
    PORT = 8080
    os.chdir('/Users/cswenx/program/AICoding/Filter-Parser')

    with socketserver.TCPServer(("", PORT), SimpleHandler) as httpd:
        print(f"🧪 Simple test server running on http://localhost:{PORT}")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nSimple test server stopped")

if __name__ == '__main__':
    main()