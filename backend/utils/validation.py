"""
输入验证工具
"""
import os
from werkzeug.utils import secure_filename
from PIL import Image
from typing import Tuple, Optional

class ValidationError(Exception):
    """验证错误异常"""
    pass

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def validate_image_file(file, allowed_extensions: set) -> Tuple[str, str]:
    """
    验证上传的图片文件

    Returns:
        (secure_filename, error_message)
    """
    if not file:
        raise ValidationError("未选择文件")

    if file.filename == '':
        raise ValidationError("文件名为空")

    if not allowed_file(file.filename, allowed_extensions):
        raise ValidationError(f"不支持的文件格式，仅支持: {', '.join(allowed_extensions)}")

    # 检查文件是否为有效图片
    try:
        image = Image.open(file.stream)
        image.verify()  # 验证图片完整性
        file.stream.seek(0)  # 重置文件指针

        # 检查图片尺寸
        if image.size[0] * image.size[1] > 25000000:  # 25MP limit
            raise ValidationError("图片尺寸过大，请选择25MP以下的图片")

    except Exception as e:
        raise ValidationError(f"无效的图片文件: {str(e)}")

    return secure_filename(file.filename), ""

def validate_parameter_name(name: str) -> bool:
    """验证参数名称"""
    if not name or len(name.strip()) == 0:
        return False

    if len(name) > 20:
        return False

    # 只允许中英文、数字、下划线
    import re
    pattern = r'^[\u4e00-\u9fa5a-zA-Z0-9_]+$'
    return bool(re.match(pattern, name.strip()))

def validate_filter_parameters(params: dict) -> bool:
    """验证滤镜参数范围"""
    valid_ranges = {
        'brightness': (-100, 100),
        'contrast': (-100, 100),
        'saturation': (-100, 100),
        'sharpness': (-100, 100),
        'temperature': (-500, 500),
        'hue': (-180, 180),
        'shadow': (-100, 100),
        'highlight': (-100, 100)
    }

    for param_name, value in params.items():
        if param_name not in valid_ranges:
            return False

        min_val, max_val = valid_ranges[param_name]
        if not isinstance(value, (int, float)) or value < min_val or value > max_val:
            return False

    return True