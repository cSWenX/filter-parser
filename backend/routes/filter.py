"""
滤镜生成路由
"""
from flask import Blueprint, request, jsonify, current_app, send_file
import os
import traceback

from ..models.response import APIResponse, ResponseStatus, GenerationResponse
from ..models.parameter import FilterParameter
from ..services.filter_generator import FilterGenerator
from ..utils.validation import validate_filter_parameters
from ..utils.constants import SUCCESS_MESSAGES, ERROR_MESSAGES

filter_bp = Blueprint('filter', __name__)

@filter_bp.route('/generate', methods=['POST'])
def generate_filter():
    """
    基于参数生成滤镜图片

    Request body:
        {
            "original_image_id": "图片ID",
            "parameters": {
                "brightness": 20,
                "contrast": -10,
                ...
            }
        }

    Returns:
        生成的滤镜图片信息
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify(APIResponse(
                status=ResponseStatus.ERROR,
                message="缺少请求数据",
                error_code="MISSING_DATA"
            ).to_dict()), 400

        # 验证必需字段
        if 'original_image_id' not in data or 'parameters' not in data:
            return jsonify(APIResponse(
                status=ResponseStatus.ERROR,
                message="缺少原始图片ID或参数",
                error_code="MISSING_REQUIRED_FIELDS"
            ).to_dict()), 400

        original_image_id = data['original_image_id']
        parameters_dict = data['parameters']

        # 验证参数
        if not validate_filter_parameters(parameters_dict):
            return jsonify(APIResponse(
                status=ResponseStatus.ERROR,
                message="参数值超出有效范围",
                error_code="INVALID_PARAMETERS"
            ).to_dict()), 400

        # 检查原始图片是否存在
        upload_folder = current_app.config['UPLOAD_FOLDER']
        original_image_path = os.path.join(upload_folder, f"{original_image_id}.jpg")

        if not os.path.exists(original_image_path):
            return jsonify(APIResponse(
                status=ResponseStatus.ERROR,
                message="原始图片不存在",
                error_code="ORIGINAL_IMAGE_NOT_FOUND"
            ).to_dict()), 404

        try:
            # 创建滤镜参数对象
            filter_params = FilterParameter.from_dict(parameters_dict)

            # 初始化滤镜生成器
            generator = FilterGenerator()

            # 生成滤镜图片
            output_image_id, output_filename, processing_time = generator.generate_filter_image(
                original_image_path,
                filter_params,
                current_app.config['OUTPUT_FOLDER']
            )

            # 构造响应数据
            generation_data = GenerationResponse(
                output_image_id=output_image_id,
                output_filename=output_filename,
                processing_time=round(processing_time, 2),
                original_image_id=original_image_id,
                applied_parameters=parameters_dict
            )

            return jsonify(APIResponse(
                status=ResponseStatus.SUCCESS,
                message=SUCCESS_MESSAGES['generation_complete'],
                data=generation_data.__dict__
            ).to_dict()), 200

        except Exception as e:
            current_app.logger.error(f"滤镜生成失败: {str(e)}")
            return jsonify(APIResponse(
                status=ResponseStatus.ERROR,
                message=ERROR_MESSAGES['generation_failed'],
                error_code="GENERATION_ERROR"
            ).to_dict()), 500

    except Exception as e:
        current_app.logger.error(f"滤镜生成请求处理异常: {str(e)}")
        current_app.logger.error(traceback.format_exc())

        return jsonify(APIResponse(
            status=ResponseStatus.ERROR,
            message="服务器内部错误",
            error_code="INTERNAL_ERROR"
        ).to_dict()), 500

@filter_bp.route('/download/<output_image_id>', methods=['GET'])
def download_filter_image(output_image_id):
    """
    下载生成的滤镜图片

    Args:
        output_image_id: 输出图片ID

    Returns:
        图片文件流
    """
    try:
        output_folder = current_app.config['OUTPUT_FOLDER']
        output_path = os.path.join(output_folder, f"{output_image_id}.jpg")

        if not os.path.exists(output_path):
            return jsonify(APIResponse(
                status=ResponseStatus.ERROR,
                message="输出图片不存在",
                error_code="OUTPUT_IMAGE_NOT_FOUND"
            ).to_dict()), 404

        # 返回文件
        return send_file(
            output_path,
            mimetype='image/jpeg',
            as_attachment=True,
            download_name=f"filter_{output_image_id}.jpg"
        )

    except Exception as e:
        current_app.logger.error(f"图片下载异常: {str(e)}")

        return jsonify(APIResponse(
            status=ResponseStatus.ERROR,
            message="下载失败",
            error_code="DOWNLOAD_ERROR"
        ).to_dict()), 500

@filter_bp.route('/preview', methods=['POST'])
def preview_filter():
    """
    生成滤镜效果预览 (不保存文件)

    Request body:
        {
            "original_image_id": "图片ID",
            "parameters": {...}
        }

    Returns:
        Base64编码的预览图片
    """
    try:
        data = request.get_json()
        if not data or 'original_image_id' not in data or 'parameters' not in data:
            return jsonify(APIResponse(
                status=ResponseStatus.ERROR,
                message="缺少必需参数",
                error_code="MISSING_REQUIRED_FIELDS"
            ).to_dict()), 400

        original_image_id = data['original_image_id']
        parameters_dict = data['parameters']

        # 验证参数
        if not validate_filter_parameters(parameters_dict):
            return jsonify(APIResponse(
                status=ResponseStatus.ERROR,
                message="参数值超出有效范围",
                error_code="INVALID_PARAMETERS"
            ).to_dict()), 400

        # 检查原始图片
        upload_folder = current_app.config['UPLOAD_FOLDER']
        original_image_path = os.path.join(upload_folder, f"{original_image_id}.jpg")

        if not os.path.exists(original_image_path):
            return jsonify(APIResponse(
                status=ResponseStatus.ERROR,
                message="原始图片不存在",
                error_code="ORIGINAL_IMAGE_NOT_FOUND"
            ).to_dict()), 404

        try:
            # 生成预览
            filter_params = FilterParameter.from_dict(parameters_dict)
            generator = FilterGenerator()

            preview_image = generator.preview_filter_effect(
                original_image_path,
                filter_params,
                max_size=(400, 400)
            )

            # 转换为Base64
            import io
            import base64

            buffer = io.BytesIO()
            preview_image.save(buffer, format='JPEG', quality=80)
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            preview_data = {
                'preview_base64': f"data:image/jpeg;base64,{img_base64}",
                'original_image_id': original_image_id,
                'preview_size': preview_image.size
            }

            return jsonify(APIResponse(
                status=ResponseStatus.SUCCESS,
                message="预览生成成功",
                data=preview_data
            ).to_dict()), 200

        except Exception as e:
            current_app.logger.error(f"预览生成失败: {str(e)}")
            return jsonify(APIResponse(
                status=ResponseStatus.ERROR,
                message="预览生成失败",
                error_code="PREVIEW_ERROR"
            ).to_dict()), 500

    except Exception as e:
        current_app.logger.error(f"预览请求处理异常: {str(e)}")

        return jsonify(APIResponse(
            status=ResponseStatus.ERROR,
            message="服务器内部错误",
            error_code="INTERNAL_ERROR"
        ).to_dict()), 500