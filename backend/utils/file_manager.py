"""
文件管理工具
"""
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import List
from PIL import Image

def generate_image_id() -> str:
    """生成唯一图片ID"""
    return str(uuid.uuid4().hex)

def get_file_path(folder: str, image_id: str, extension: str) -> str:
    """获取文件完整路径"""
    filename = f"{image_id}.{extension.lower()}"
    return os.path.join(folder, filename)

def save_uploaded_image(file, upload_folder: str, max_size: tuple = (2048, 2048)) -> tuple:
    """
    保存上传的图片，返回(image_id, filename, dimensions, file_size)
    """
    image_id = generate_image_id()

    # 打开并处理图片
    image = Image.open(file.stream)

    # 获取原始信息
    original_size = image.size
    file_size = len(file.read())
    file.stream.seek(0)

    # 转换为RGB模式(处理RGBA等)
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # 如果图片过大则压缩
    if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
        image.thumbnail(max_size, Image.Resampling.LANCZOS)

    # 保存图片
    file_path = get_file_path(upload_folder, image_id, 'jpg')
    image.save(file_path, 'JPEG', quality=85, optimize=True)

    return image_id, os.path.basename(file_path), image.size, file_size

def cleanup_old_files(folder: str, max_age_hours: int = 24) -> int:
    """
    清理超过指定时间的文件

    Returns:
        清理的文件数量
    """
    if not os.path.exists(folder):
        return 0

    current_time = time.time()
    cutoff_time = current_time - (max_age_hours * 3600)
    cleaned_count = 0

    for filename in os.listdir(folder):
        if filename.startswith('.'):  # 跳过隐藏文件
            continue

        file_path = os.path.join(folder, filename)

        try:
            # 检查文件修改时间
            if os.path.getmtime(file_path) < cutoff_time:
                os.remove(file_path)
                cleaned_count += 1
        except OSError:
            continue  # 文件可能已被删除或无权限

    return cleaned_count

def get_folder_size(folder: str) -> int:
    """获取文件夹大小(bytes)"""
    total_size = 0
    if os.path.exists(folder):
        for dirpath, dirnames, filenames in os.walk(folder):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except OSError:
                    continue
    return total_size

def list_temp_files(upload_folder: str, output_folder: str) -> dict:
    """列出临时文件信息"""
    def get_files_info(folder: str) -> List[dict]:
        files = []
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                if filename.startswith('.'):
                    continue

                file_path = os.path.join(folder, filename)
                try:
                    stat = os.stat(file_path)
                    files.append({
                        'filename': filename,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except OSError:
                    continue
        return files

    return {
        'uploads': get_files_info(upload_folder),
        'outputs': get_files_info(output_folder),
        'upload_folder_size': get_folder_size(upload_folder),
        'output_folder_size': get_folder_size(output_folder)
    }