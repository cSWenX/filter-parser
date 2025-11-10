"""
图片上传路由
"""
from flask import Blueprint, request, jsonify, current_app
from werkzeug.exceptions import RequestEntityTooLarge
import os
import traceback

from ..models.response import APIResponse, ResponseStatus, UploadResponse
from ..utils.validation import validate_image_file, ValidationError
from ..utils.file_manager import save_uploaded_image
from ..utils.constants import SUCCESS_MESSAGES, ERROR_MESSAGES

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['POST'])
def upload_image():
    """
    上传图片接口

    Returns:
        JSON响应包含图片ID、文件名、尺寸等信息
    """
    try:
        # 检查是否有文件
        if 'image' not in request.files:
            return jsonify(APIResponse(
                status=ResponseStatus.ERROR,
                message="未选择文件",
                error_code="NO_FILE"
            ).to_dict()), 400

        file = request.files['image']

        # 验证文件
        try:
            filename, _ = validate_image_file(file, current_app.config['ALLOWED_EXTENSIONS'])
        except ValidationError as e:
            return jsonify(APIResponse(
                status=ResponseStatus.ERROR,
                message=str(e),
                error_code="VALIDATION_ERROR"
            ).to_dict()), 400

        # 保存文件
        try:
            image_id, saved_filename, dimensions, file_size = save_uploaded_image(
                file,
                current_app.config['UPLOAD_FOLDER'],
                current_app.config['MAX_IMAGE_SIZE']
            )

            # 构造响应数据
            upload_data = UploadResponse(
                image_id=image_id,
                filename=saved_filename,
                file_size=file_size,
                dimensions=dimensions
            )

            return jsonify(APIResponse(
                status=ResponseStatus.SUCCESS,
                message=SUCCESS_MESSAGES['upload_success'],
                data=upload_data.__dict__
            ).to_dict()), 200

        except Exception as e:
            current_app.logger.error(f"文件保存失败: {str(e)}")
            return jsonify(APIResponse(
                status=ResponseStatus.ERROR,
                message="文件保存失败",
                error_code="SAVE_ERROR"
            ).to_dict()), 500

    except RequestEntityTooLarge:
        return jsonify(APIResponse(
            status=ResponseStatus.ERROR,
            message=ERROR_MESSAGES['file_too_large'],
            error_code="FILE_TOO_LARGE"
        ).to_dict()), 413

    except Exception as e:
        current_app.logger.error(f"上传处理异常: {str(e)}")
        current_app.logger.error(traceback.format_exc())

        return jsonify(APIResponse(
            status=ResponseStatus.ERROR,
            message="服务器内部错误",
            error_code="INTERNAL_ERROR"
        ).to_dict()), 500

@upload_bp.route('/upload/status/<image_id>', methods=['GET'])
def get_upload_status(image_id):
    """
    获取上传文件状态

    Args:
        image_id: 图片ID

    Returns:
        文件状态信息
    """
    try:
        # 检查文件是否存在
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, f"{image_id}.jpg")

        if not os.path.exists(file_path):
            return jsonify(APIResponse(
                status=ResponseStatus.ERROR,
                message="文件不存在",
                error_code="FILE_NOT_FOUND"
            ).to_dict()), 404

        # 获取文件信息
        file_stat = os.stat(file_path)
        file_info = {
            'image_id': image_id,
            'file_size': file_stat.st_size,
            'upload_time': file_stat.st_mtime,
            'exists': True
        }

        return jsonify(APIResponse(
            status=ResponseStatus.SUCCESS,
            message="文件状态获取成功",
            data=file_info
        ).to_dict()), 200

    except Exception as e:
        current_app.logger.error(f"状态查询异常: {str(e)}")

        return jsonify(APIResponse(
            status=ResponseStatus.ERROR,
            message="状态查询失败",
            error_code="STATUS_ERROR"
        ).to_dict()), 500