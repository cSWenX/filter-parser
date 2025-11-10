#!/usr/bin/env python3
"""
简化版HTTP服务器 - 用于演示Filter Parser
"""
import http.server
import socketserver
import json
import urllib.parse
import os
import time
import hashlib
import random

class FilterParserHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/Users/cswenx/program/AICoding/Filter-Parser", **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path.startswith('/api/'):
            self.handle_api()
        elif self.path == '/':
            self.path = '/index.html'
            super().do_GET()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/'):
            self.handle_api()
        else:
            self.send_error(404)

    def handle_api(self):
        path = self.path.replace('/api', '')

        try:
            if path == '/health':
                self.send_json({
                    "status": "success",
                    "message": "服务运行正常",
                    "data": {"status": "healthy"}
                })

            elif path == '/upload':
                self.send_json({
                    "status": "success",
                    "message": "上传成功",
                    "data": {
                        "image_id": f"img_{int(time.time())}",
                        "filename": "demo.jpg",
                        "file_size": 102400,
                        "dimensions": [800, 600]
                    }
                })

            elif path.startswith('/analyze/'):
                time.sleep(1)  # 模拟处理时间
                self.send_json({
                    "status": "success",
                    "message": "分析完成",
                    "data": {
                        "image_id": path.split('/')[-1],
                        "parameters": self.get_mock_params(),
                        "analysis_time": 2.1,
                        "confidence_score": 0.85,
                        "suggestions": ["该参数组合适合风景类图片", "可直接用于Lightroom/PS"]
                    }
                })

            else:
                self.send_error(404)

        except Exception as e:
            self.send_json({"status": "error", "message": str(e)}, 500)

    def send_json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def get_mock_params(self):
        return {
            "brightness": {"name": "亮度", "direction": "增加", "value": 15.2, "unit": "%", "reference": "sRGB 标准色彩"},
            "contrast": {"name": "对比度", "direction": "增加", "value": 22.8, "unit": "%", "reference": "灰度阶差分析"},
            "saturation": {"name": "饱和度", "direction": "增加", "value": 18.5, "unit": "%", "reference": "HSV 色彩模型"},
            "sharpness": {"name": "锐化", "direction": "增强", "value": 12.3, "unit": "%", "reference": "边缘清晰度算法"},
            "temperature": {"name": "色温", "direction": "偏暖", "value": 150, "unit": "K", "reference": "标准色温 6500K"},
            "hue": {"name": "色调", "direction": "偏红", "value": 8.2, "unit": "°", "reference": "RGB 通道占比"},
            "shadow": {"name": "阴影", "direction": "提亮", "value": 10.5, "unit": "%", "reference": "暗部像素占比"},
            "highlight": {"name": "高光", "direction": "降低", "value": 5.8, "unit": "%", "reference": "亮部像素占比"}
        }

if __name__ == '__main__':
    PORT = 8080
    os.chdir('/Users/cswenx/program/AICoding/Filter-Parser')

    with socketserver.TCPServer(("", PORT), FilterParserHandler) as httpd:
        print(f"🚀 Filter Parser 服务已启动")
        print(f"📍 访问地址: http://localhost:{PORT}")
        print(f"🔍 健康检查: http://localhost:{PORT}/api/health")
        print("按 Ctrl+C 停止服务")
        httpd.serve_forever()