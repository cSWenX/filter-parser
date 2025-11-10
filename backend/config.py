# Flask Config
import os
from datetime import timedelta

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
    OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

    # 处理配置
    ANALYSIS_TIMEOUT = 30  # 30秒超时
    GENERATION_TIMEOUT = 20  # 20秒超时
    AUTO_CLEANUP_HOURS = 24  # 24小时后自动清理

    # CORS配置
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']

    # 图像处理配置
    MAX_IMAGE_SIZE = (2048, 2048)  # 最大处理尺寸
    QUALITY_COMPRESSION = 85  # JPEG压缩质量

    @staticmethod
    def init_app(app):
        # 确保上传和输出目录存在
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)