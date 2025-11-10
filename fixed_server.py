#!/usr/bin/env python3
"""
Filter Parser 完整服务器
修复API接口问题，确保前后端通信正常
"""
import http.server
import socketserver
import json
import os
import time
import urllib.parse
import sqlite3
import uuid
from datetime import datetime

class FilterParserHandler(http.server.SimpleHTTPRequestHandler):
    # 类级别的数据库路径，所有实例共享
    db_path = "/Users/cswenx/program/AICoding/Filter-Parser/filters.db"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/Users/cswenx/program/AICoding/Filter-Parser", **kwargs)
        self.init_database()

    def end_headers(self):
        # 添加CORS头
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        """处理OPTIONS预检请求"""
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        """处理GET请求"""
        print(f"GET: {self.path}")

        if self.path.startswith('/api/'):
            self.handle_api_request()
        elif self.path == '/':
            # 重定向到主页
            self.send_response(302)
            self.send_header('Location', '/index.html')
            self.end_headers()
        else:
            # 处理静态文件
            super().do_GET()

    def do_POST(self):
        """处理POST请求"""
        print(f"POST: {self.path}")

        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            self.send_error(404, "API endpoint not found")

    def do_PUT(self):
        """处理PUT请求"""
        print(f"PUT: {self.path}")

        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            self.send_error(404, "API endpoint not found")

    def do_DELETE(self):
        """处理DELETE请求"""
        print(f"DELETE: {self.path}")

        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            self.send_error(404, "API endpoint not found")

    def handle_api_request(self):
        """处理API请求"""
        try:
            # 移除/api前缀
            api_path = self.path.replace('/api', '')

            # 解析查询参数
            if '?' in api_path:
                api_path = api_path.split('?')[0]

            print(f"API Path: {api_path}")

            # 路由处理
            if api_path == '/health':
                self.handle_health()
            elif api_path == '/upload':
                self.handle_upload()
            elif api_path.startswith('/analyze/'):
                self.handle_analyze(api_path)
            elif api_path == '/generate':
                self.handle_generate()
            elif api_path == '/filters':
                self.handle_filters()
            elif api_path.startswith('/filters/'):
                self.handle_filter_operations(api_path)
            elif api_path == '/apply-filter':
                self.handle_apply_filter()
            elif api_path.startswith('/download/'):
                self.handle_download(api_path)
            else:
                self.send_json_error(404, "API接口不存在")

        except Exception as e:
            print(f"API Error: {e}")
            self.send_json_error(500, f"服务器错误: {str(e)}")

    def handle_health(self):
        """健康检查"""
        response_data = {
            "status": "success",
            "message": "服务运行正常",
            "data": {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "upload_folder_size_mb": 0,
                "output_folder_size_mb": 0,
                "upload_files_count": 0,
                "output_files_count": 0
            }
        }
        self.send_json_response(response_data)

    def handle_upload(self):
        """处理图片上传"""
        print(f"Upload request method: {self.command}")
        print(f"Upload request headers: {dict(self.headers)}")

        if self.command != 'POST':
            print(f"ERROR: Expected POST, got {self.command}")
            self.send_json_error(405, "仅支持POST方法")
            return

        print("Processing upload request...")
        # 生成模拟的上传响应
        image_id = f"img_{int(time.time() * 1000)}"

        response_data = {
            "status": "success",
            "message": "上传成功，正在分析参数",
            "data": {
                "image_id": image_id,
                "filename": "demo_image.jpg",
                "file_size": 1024000,
                "dimensions": [800, 600]
            }
        }
        self.send_json_response(response_data)

    def handle_analyze(self, api_path):
        """处理参数分析"""
        if self.command != 'POST':
            self.send_json_error(405, "仅支持POST方法")
            return

        # 提取图片ID
        image_id = api_path.split('/')[-1]

        # 模拟分析时间
        time.sleep(1)

        # 生成模拟分析结果
        response_data = {
            "status": "success",
            "message": "分析完成",
            "data": {
                "image_id": image_id,
                "parameters": self.generate_mock_parameters(),
                "analysis_time": 2.1,
                "confidence_score": 0.85,
                "suggestions": [
                    "该参数组合适合风景类图片，可直接用于 Lightroom/PS",
                    "建议在秋季、暖色调场景中使用",
                    "适合需要增强色彩饱和度的图片"
                ]
            }
        }
        self.send_json_response(response_data)

    def handle_generate(self):
        """处理滤镜生成"""
        if self.command != 'POST':
            self.send_json_error(405, "仅支持POST方法")
            return

        # 模拟滤镜生成
        output_id = f"output_{int(time.time() * 1000)}"

        response_data = {
            "status": "success",
            "message": "滤镜生成完成",
            "data": {
                "output_image_id": output_id,
                "output_filename": f"{output_id}.jpg",
                "processing_time": 1.8,
                "download_url": f"/api/download/{output_id}"
            }
        }
        self.send_json_response(response_data)

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

    def init_database(self):
        """初始化SQLite数据库"""
        try:
            # 确保使用类级别的数据库路径
            if not hasattr(self.__class__, 'db_initialized'):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # 创建滤镜表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS filters (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        parameters TEXT NOT NULL,
                        analysis_result TEXT,
                        saved_time TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                ''')

                # 创建图片表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS images (
                        id TEXT PRIMARY KEY,
                        filename TEXT NOT NULL,
                        file_path TEXT,
                        file_size INTEGER,
                        dimensions TEXT,
                        upload_time TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                ''')

                conn.commit()
                conn.close()
                self.__class__.db_initialized = True
                print(f"Database initialized at: {self.db_path}")
        except Exception as e:
            print(f"Database init error: {e}")

    def get_db_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

    def handle_filters(self):
        """处理滤镜列表请求 GET /api/filters"""
        if self.command == 'GET':
            self.handle_get_filters()
        elif self.command == 'POST':
            self.handle_save_filter()
        else:
            self.send_json_error(405, "不支持的HTTP方法")

    def handle_get_filters(self):
        """获取所有保存的滤镜"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, name, parameters, analysis_result, saved_time, created_at
                FROM filters
                ORDER BY created_at DESC
            ''')

            filters = []
            for row in cursor.fetchall():
                filters.append({
                    "id": row[0],
                    "name": row[1],
                    "parameters": json.loads(row[2]),
                    "analysis_result": json.loads(row[3]) if row[3] else None,
                    "saved_time": row[4],
                    "created_at": row[5]
                })

            conn.close()

            response_data = {
                "status": "success",
                "message": "获取滤镜列表成功",
                "data": {
                    "filters": filters,
                    "total": len(filters)
                }
            }
            self.send_json_response(response_data)

        except Exception as e:
            print(f"Get filters error: {e}")
            self.send_json_error(500, f"获取滤镜失败: {str(e)}")

    def handle_save_filter(self):
        """保存新滤镜"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # 验证必需字段
            required_fields = ['name', 'parameters']
            for field in required_fields:
                if field not in data:
                    self.send_json_error(400, f"缺少必需字段: {field}")
                    return

            # 生成滤镜ID
            filter_id = str(uuid.uuid4())
            current_time = datetime.now().isoformat()

            # 保存到数据库
            conn = self.get_db_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO filters (id, name, parameters, analysis_result, saved_time, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                filter_id,
                data['name'],
                json.dumps(data['parameters']),
                json.dumps(data.get('analysis_result')) if data.get('analysis_result') else None,
                current_time,
                current_time
            ))

            conn.commit()
            conn.close()

            response_data = {
                "status": "success",
                "message": "滤镜保存成功",
                "data": {
                    "filter_id": filter_id,
                    "name": data['name'],
                    "saved_time": current_time
                }
            }
            self.send_json_response(response_data)

        except Exception as e:
            print(f"Save filter error: {e}")
            self.send_json_error(500, f"保存滤镜失败: {str(e)}")

    def handle_filter_operations(self, api_path):
        """处理单个滤镜的操作 GET/PUT/DELETE /api/filters/{id}"""
        filter_id = api_path.split('/')[-1]

        if self.command == 'GET':
            self.handle_get_filter(filter_id)
        elif self.command == 'PUT':
            self.handle_update_filter(filter_id)
        elif self.command == 'DELETE':
            self.handle_delete_filter(filter_id)
        else:
            self.send_json_error(405, "不支持的HTTP方法")

    def handle_get_filter(self, filter_id):
        """获取单个滤镜详情"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, name, parameters, analysis_result, saved_time, created_at
                FROM filters
                WHERE id = ?
            ''', (filter_id,))

            row = cursor.fetchone()
            conn.close()

            if not row:
                self.send_json_error(404, "滤镜不存在")
                return

            filter_data = {
                "id": row[0],
                "name": row[1],
                "parameters": json.loads(row[2]),
                "analysis_result": json.loads(row[3]) if row[3] else None,
                "saved_time": row[4],
                "created_at": row[5]
            }

            response_data = {
                "status": "success",
                "message": "获取滤镜详情成功",
                "data": filter_data
            }
            self.send_json_response(response_data)

        except Exception as e:
            print(f"Get filter error: {e}")
            self.send_json_error(500, f"获取滤镜详情失败: {str(e)}")

    def handle_update_filter(self, filter_id):
        """更新滤镜信息"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            conn = self.get_db_connection()
            cursor = conn.cursor()

            # 检查滤镜是否存在
            cursor.execute('SELECT id FROM filters WHERE id = ?', (filter_id,))
            if not cursor.fetchone():
                conn.close()
                self.send_json_error(404, "滤镜不存在")
                return

            # 更新滤镜
            updates = []
            params = []

            if 'name' in data:
                updates.append('name = ?')
                params.append(data['name'])

            if 'parameters' in data:
                updates.append('parameters = ?')
                params.append(json.dumps(data['parameters']))

            if 'analysis_result' in data:
                updates.append('analysis_result = ?')
                params.append(json.dumps(data['analysis_result']))

            if not updates:
                conn.close()
                self.send_json_error(400, "没有提供更新字段")
                return

            params.append(filter_id)
            query = f"UPDATE filters SET {', '.join(updates)} WHERE id = ?"

            cursor.execute(query, params)
            conn.commit()
            conn.close()

            response_data = {
                "status": "success",
                "message": "滤镜更新成功",
                "data": {
                    "filter_id": filter_id,
                    "updated_time": datetime.now().isoformat()
                }
            }
            self.send_json_response(response_data)

        except Exception as e:
            print(f"Update filter error: {e}")
            self.send_json_error(500, f"更新滤镜失败: {str(e)}")

    def handle_delete_filter(self, filter_id):
        """删除滤镜"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # 检查滤镜是否存在
            cursor.execute('SELECT name FROM filters WHERE id = ?', (filter_id,))
            row = cursor.fetchone()

            if not row:
                conn.close()
                self.send_json_error(404, "滤镜不存在")
                return

            filter_name = row[0]

            # 删除滤镜
            cursor.execute('DELETE FROM filters WHERE id = ?', (filter_id,))
            conn.commit()
            conn.close()

            response_data = {
                "status": "success",
                "message": f"滤镜 \"{filter_name}\" 删除成功",
                "data": {
                    "filter_id": filter_id,
                    "deleted_time": datetime.now().isoformat()
                }
            }
            self.send_json_response(response_data)

        except Exception as e:
            print(f"Delete filter error: {e}")
            self.send_json_error(500, f"删除滤镜失败: {str(e)}")

    def handle_apply_filter(self):
        """应用滤镜到图片"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # 验证必需字段
            required_fields = ['image_id', 'parameters']
            for field in required_fields:
                if field not in data:
                    self.send_json_error(400, f"缺少必需字段: {field}")
                    return

            # 模拟处理时间
            time.sleep(1.5)

            # 生成输出文件名
            output_id = f"filtered_{int(time.time() * 1000)}"
            output_filename = f"{output_id}.jpg"

            response_data = {
                "status": "success",
                "message": "滤镜应用成功",
                "data": {
                    "output_image_id": output_id,
                    "output_filename": output_filename,
                    "processing_time": 1.5,
                    "download_url": f"/api/download/{output_filename}",
                    "applied_parameters": data['parameters']
                }
            }
            self.send_json_response(response_data)

        except Exception as e:
            print(f"Apply filter error: {e}")
            self.send_json_error(500, f"应用滤镜失败: {str(e)}")

    def handle_download(self, api_path):
        """处理文件下载"""
        try:
            filename = api_path.split('/')[-1]

            # 模拟文件下载
            response_data = {
                "status": "success",
                "message": "下载链接生成成功",
                "data": {
                    "download_url": f"http://localhost:8080/static/downloads/{filename}",
                    "filename": filename,
                    "expires_at": datetime.now().isoformat()
                }
            }
            self.send_json_response(response_data)

        except Exception as e:
            print(f"Download error: {e}")
            self.send_json_error(500, f"下载失败: {str(e)}")

    def send_json_response(self, data, status_code=200):
        """发送JSON响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()

        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(json_str.encode('utf-8'))

    def send_json_error(self, status_code, message):
        """发送JSON错误响应"""
        error_data = {
            "status": "error",
            "message": message,
            "error_code": f"HTTP_{status_code}"
        }
        self.send_json_response(error_data, status_code)

    def log_message(self, format, *args):
        """重写日志方法，显示更清晰的日志"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

def main():
    PORT = 8080

    # 确保在正确的目录
    os.chdir('/Users/cswenx/program/AICoding/Filter-Parser')

    # 创建服务器
    with socketserver.TCPServer(("", PORT), FilterParserHandler) as httpd:
        print("=" * 60)
        print("🚀 Filter Parser 服务器已启动")
        print("=" * 60)
        print(f"📍 主页地址: http://localhost:{PORT}")
        print(f"🔍 健康检查: http://localhost:{PORT}/api/health")
        print(f"📁 项目目录: {os.getcwd()}")
        print("=" * 60)
        print("💡 使用说明:")
        print("   1. 打开浏览器访问主页地址")
        print("   2. 上传图片开始分析")
        print("   3. 查看参数分析结果")
        print("=" * 60)
        print("按 Ctrl+C 停止服务")
        print()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 服务已停止")

if __name__ == '__main__':
    main()