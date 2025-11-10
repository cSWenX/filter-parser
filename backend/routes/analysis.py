"""
参数分析路由
"""
from flask import Blueprint, request, jsonify, current_app
import os
import traceback

from ..models.response import APIResponse, ResponseStatus, AnalysisResponse
from ..services.image_analyzer import ImageAnalyzer
from ..utils.constants import SUCCESS_MESSAGES, ERROR_MESSAGES, ANALYSIS_THRESHOLDS

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/analyze/<image_id>', methods=['POST'])
def analyze_image(image_id):
    """
    分析图片滤镜参数

    Args:
        image_id: 图片ID

    Returns:
        分析结果包含8类参数信息
    """
    try:
        # 检查图片文件是否存在
        upload_folder = current_app.config['UPLOAD_FOLDER']
        image_path = os.path.join(upload_folder, f"{image_id}.jpg")

        if not os.path.exists(image_path):
            return jsonify(APIResponse(
                status=ResponseStatus.ERROR,
                message=ERROR_MESSAGES['file_not_found'],
                error_code="FILE_NOT_FOUND"
            ).to_dict()), 404

        # 初始化分析器
        analyzer = ImageAnalyzer()

        try:
            # 执行分析
            analysis_result = analyzer.analyze_image(image_path)

            # 检查是否有显著变化
            significant_changes = []
            all_parameters = {}

            for param_name, param_value in analysis_result.parameters.items():
                param_dict = {
                    'name': param_value.name,
                    'direction': param_value.direction,
                    'value': round(param_value.value, 1),
                    'unit': param_value.unit,
                    'reference': param_value.reference
                }
                all_parameters[param_name] = param_dict

                # 检查是否为显著变化
                if param_value.value >= ANALYSIS_THRESHOLDS['min_change_threshold']:
                    significant_changes.append(param_name)

            # 生成建议
            suggestions = _generate_suggestions(analysis_result, significant_changes)

            # 如果没有显著变化
            if len(significant_changes) == 0:
                message = "该图片接近原始效果，未检测到显著滤镜参数调整"
            else:
                message = SUCCESS_MESSAGES['analysis_complete']

            # 构造响应数据
            analysis_data = AnalysisResponse(
                image_id=image_id,
                parameters=all_parameters,
                analysis_time=round(analysis_result.analysis_time, 2),
                confidence_score=analysis_result.confidence_score,
                suggestions=suggestions,
                message=message
            )

            return jsonify(APIResponse(
                status=ResponseStatus.SUCCESS,
                message=message,
                data=analysis_data.__dict__
            ).to_dict()), 200

        except Exception as e:
            current_app.logger.error(f"图像分析失败: {str(e)}")
            return jsonify(APIResponse(
                status=ResponseStatus.ERROR,
                message=ERROR_MESSAGES['analysis_failed'],
                error_code="ANALYSIS_ERROR"
            ).to_dict()), 500

    except Exception as e:
        current_app.logger.error(f"分析请求处理异常: {str(e)}")
        current_app.logger.error(traceback.format_exc())

        return jsonify(APIResponse(
            status=ResponseStatus.ERROR,
            message="服务器内部错误",
            error_code="INTERNAL_ERROR"
        ).to_dict()), 500

@analysis_bp.route('/analyze/batch', methods=['POST'])
def analyze_batch():
    """
    批量分析多张图片 (可选功能)

    Request body:
        {
            "image_ids": ["id1", "id2", "id3"]
        }

    Returns:
        批量分析结果
    """
    try:
        data = request.get_json()
        if not data or 'image_ids' not in data:
            return jsonify(APIResponse(
                status=ResponseStatus.ERROR,
                message="缺少图片ID列表",
                error_code="MISSING_IMAGE_IDS"
            ).to_dict()), 400

        image_ids = data['image_ids']
        if len(image_ids) > 10:  # 限制批量处理数量
            return jsonify(APIResponse(
                status=ResponseStatus.ERROR,
                message="批量处理最多支持10张图片",
                error_code="TOO_MANY_IMAGES"
            ).to_dict()), 400

        upload_folder = current_app.config['UPLOAD_FOLDER']
        analyzer = ImageAnalyzer()

        results = []
        failed_images = []

        for image_id in image_ids:
            try:
                image_path = os.path.join(upload_folder, f"{image_id}.jpg")

                if not os.path.exists(image_path):
                    failed_images.append({
                        'image_id': image_id,
                        'error': 'file_not_found'
                    })
                    continue

                # 分析图片
                analysis_result = analyzer.analyze_image(image_path)

                # 简化输出格式
                parameters = {}
                for param_name, param_value in analysis_result.parameters.items():
                    parameters[param_name] = {
                        'direction': param_value.direction,
                        'value': round(param_value.value, 1)
                    }

                results.append({
                    'image_id': image_id,
                    'parameters': parameters,
                    'confidence_score': analysis_result.confidence_score
                })

            except Exception as e:
                failed_images.append({
                    'image_id': image_id,
                    'error': str(e)
                })

        response_data = {
            'successful_count': len(results),
            'failed_count': len(failed_images),
            'results': results,
            'failed_images': failed_images
        }

        return jsonify(APIResponse(
            status=ResponseStatus.SUCCESS,
            message=f"批量分析完成: 成功 {len(results)} 张，失败 {len(failed_images)} 张",
            data=response_data
        ).to_dict()), 200

    except Exception as e:
        current_app.logger.error(f"批量分析异常: {str(e)}")

        return jsonify(APIResponse(
            status=ResponseStatus.ERROR,
            message="批量分析失败",
            error_code="BATCH_ANALYSIS_ERROR"
        ).to_dict()), 500

def _generate_suggestions(analysis_result, significant_changes):
    """生成参数应用建议"""
    suggestions = []

    # 基于显著变化的参数数量给出建议
    if len(significant_changes) >= 5:
        suggestions.append("该图片经过较多滤镜调整，参数组合较复杂")

    if 'temperature' in significant_changes:
        if analysis_result.parameters['temperature'].direction == '偏暖':
            suggestions.append("适合用于秋季、黄昏类场景图片")
        else:
            suggestions.append("适合用于冬季、清晨类场景图片")

    if 'saturation' in significant_changes:
        if analysis_result.parameters['saturation'].direction == '增加':
            suggestions.append("适合风景、花卉等需要鲜艳色彩的图片")
        else:
            suggestions.append("适合人像、复古风格图片")

    if 'contrast' in significant_changes:
        if analysis_result.parameters['contrast'].direction == '增加':
            suggestions.append("适合缺乏层次感的平淡图片")

    # 默认建议
    if not suggestions:
        suggestions.append("该参数组合可直接用于Lightroom、Photoshop等修图软件")

    return suggestions