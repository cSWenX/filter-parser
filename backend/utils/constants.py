"""
常量定义
"""

# 参数分析相关常量
PARAMETER_NAMES = {
    'brightness': '亮度',
    'contrast': '对比度',
    'saturation': '饱和度',
    'sharpness': '锐化',
    'temperature': '色温',
    'hue': '色调',
    'shadow': '阴影',
    'highlight': '高光'
}

PARAMETER_UNITS = {
    'brightness': '%',
    'contrast': '%',
    'saturation': '%',
    'sharpness': '%',
    'temperature': 'K',
    'hue': '°',
    'shadow': '%',
    'highlight': '%'
}

PARAMETER_REFERENCES = {
    'brightness': 'sRGB 标准色彩',
    'contrast': '灰度阶差分析',
    'saturation': 'HSV 色彩模型',
    'sharpness': '边缘清晰度算法',
    'temperature': '标准色温 6500K',
    'hue': 'RGB 通道占比',
    'shadow': '暗部像素占比',
    'highlight': '亮部像素占比'
}

# 方向描述
DIRECTION_MAPPING = {
    'brightness': {1: '增加', -1: '降低'},
    'contrast': {1: '增加', -1: '降低'},
    'saturation': {1: '增加', -1: '降低'},
    'sharpness': {1: '增强', -1: '减弱'},
    'temperature': {1: '偏暖', -1: '偏冷'},
    'hue': {1: '偏红', 0: '偏绿', -1: '偏蓝'},
    'shadow': {1: '提亮', -1: '压暗'},
    'highlight': {1: '提升', -1: '降低'}
}

# 分析阈值
ANALYSIS_THRESHOLDS = {
    'min_change_threshold': 5,  # 最小变化阈值(%)
    'confidence_threshold': 0.7,  # 置信度阈值
    'max_analysis_time': 30,  # 最大分析时间(秒)
}

# 图像处理常量
IMAGE_PROCESSING = {
    'default_quality': 85,
    'max_dimension': 2048,
    'supported_formats': ['JPEG', 'PNG', 'WEBP'],
    'default_format': 'JPEG'
}

# 错误消息
ERROR_MESSAGES = {
    'file_too_large': '文件大小超过限制',
    'invalid_format': '不支持的文件格式',
    'analysis_failed': '图像分析失败',
    'generation_failed': '滤镜生成失败',
    'file_not_found': '文件未找到',
    'invalid_parameters': '无效的参数',
    'processing_timeout': '处理超时'
}

# 成功消息
SUCCESS_MESSAGES = {
    'upload_success': '图片上传成功',
    'analysis_complete': '参数分析完成',
    'generation_complete': '滤镜生成完成',
    'cleanup_complete': '文件清理完成'
}