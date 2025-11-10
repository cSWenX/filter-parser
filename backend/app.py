"""
Flask主应用
"""
from flask import Flask, jsonify
from flask_cors import CORS
import os
import atexit
import threading
import time

from config import Config
from routes import upload_bp, analysis_bp, filter_bp
from models.response import APIResponse, ResponseStatus
from utils.file_manager import cleanup_old_files

def create_app(config_class=Config):
    """Flask应用工厂"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化配置
    config_class.init_app(app)

    # 配置CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # 注册蓝图
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(analysis_bp, url_prefix='/api')
    app.register_blueprint(filter_bp, url_prefix='/api')

    # 注册错误处理器
    register_error_handlers(app)

    # 启动后台清理任务
    setup_cleanup_task(app)

    return app

def register_error_handlers(app):
    """注册全局错误处理器"""

    @app.errorhandler(404)
    def not_found(error):
        return jsonify(APIResponse(
            status=ResponseStatus.ERROR,
            message="接口不存在",
            error_code="ENDPOINT_NOT_FOUND"
        ).to_dict()), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify(APIResponse(
            status=ResponseStatus.ERROR,
            message="请求方法不允许",
            error_code="METHOD_NOT_ALLOWED"
        ).to_dict()), 405

    @app.errorhandler(413)
    def payload_too_large(error):
        return jsonify(APIResponse(
            status=ResponseStatus.ERROR,
            message="请求体过大",
            error_code="PAYLOAD_TOO_LARGE"
        ).to_dict()), 413

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify(APIResponse(
            status=ResponseStatus.ERROR,
            message="服务器内部错误",
            error_code="INTERNAL_ERROR"
        ).to_dict()), 500

def setup_cleanup_task(app):
    """设置文件清理任务"""
    cleanup_interval = 3600  # 每小时清理一次

    def cleanup_worker():
        """后台清理工作线程"""
        while True:
            try:
                with app.app_context():
                    upload_count = cleanup_old_files(
                        app.config['UPLOAD_FOLDER'],
                        app.config['AUTO_CLEANUP_HOURS']
                    )
                    output_count = cleanup_old_files(
                        app.config['OUTPUT_FOLDER'],
                        app.config['AUTO_CLEANUP_HOURS']
                    )

                    if upload_count > 0 or output_count > 0:
                        app.logger.info(f"自动清理完成: 上传文件 {upload_count} 个，输出文件 {output_count} 个")

            except Exception as e:
                app.logger.error(f"文件清理异常: {str(e)}")

            time.sleep(cleanup_interval)

    # 启动后台线程
    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()

    # 注册退出时清理
    def cleanup_on_exit():
        try:
            cleanup_old_files(app.config['UPLOAD_FOLDER'], 0)  # 清理所有临时文件
            cleanup_old_files(app.config['OUTPUT_FOLDER'], 0)
        except:
            pass

    atexit.register(cleanup_on_exit)

# 添加健康检查和系统信息接口
def add_system_routes(app):
    """添加系统路由"""

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """健康检查"""
        from utils.file_manager import list_temp_files

        try:
            file_info = list_temp_files(
                app.config['UPLOAD_FOLDER'],
                app.config['OUTPUT_FOLDER']
            )

            health_data = {
                'status': 'healthy',
                'upload_folder_size_mb': round(file_info['upload_folder_size'] / 1024 / 1024, 2),
                'output_folder_size_mb': round(file_info['output_folder_size'] / 1024 / 1024, 2),
                'upload_files_count': len(file_info['uploads']),
                'output_files_count': len(file_info['outputs'])
            }

            return jsonify(APIResponse(
                status=ResponseStatus.SUCCESS,
                message="服务运行正常",
                data=health_data
            ).to_dict()), 200

        except Exception as e:
            return jsonify(APIResponse(
                status=ResponseStatus.ERROR,
                message=f"健康检查失败: {str(e)}",
                error_code="HEALTH_CHECK_ERROR"
            ).to_dict()), 500

    @app.route('/api/cleanup', methods=['POST'])
    def manual_cleanup():
        """手动触发文件清理"""
        try:
            upload_count = cleanup_old_files(
                app.config['UPLOAD_FOLDER'],
                app.config['AUTO_CLEANUP_HOURS']
            )
            output_count = cleanup_old_files(
                app.config['OUTPUT_FOLDER'],
                app.config['AUTO_CLEANUP_HOURS']
            )

            cleanup_data = {
                'upload_files_cleaned': upload_count,
                'output_files_cleaned': output_count,
                'total_cleaned': upload_count + output_count
            }

            return jsonify(APIResponse(
                status=ResponseStatus.SUCCESS,
                message=f"清理完成: 共清理 {upload_count + output_count} 个文件",
                data=cleanup_data
            ).to_dict()), 200

        except Exception as e:
            app.logger.error(f"手动清理失败: {str(e)}")
            return jsonify(APIResponse(
                status=ResponseStatus.ERROR,
                message="清理失败",
                error_code="CLEANUP_ERROR"
            ).to_dict()), 500

# 创建应用实例
app = create_app()
add_system_routes(app)

if __name__ == '__main__':
    # 开发模式运行
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )