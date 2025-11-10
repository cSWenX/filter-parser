"""
核心图像分析算法
基于OpenCV和PIL实现8类滤镜参数的自动识别
"""
import cv2
import numpy as np
from PIL import Image, ImageStat
from typing import Dict, Tuple
import time
from datetime import datetime

from ..models.parameter import ParameterValue, AnalysisResult, FilterParameter
from ..utils.constants import (
    PARAMETER_NAMES, PARAMETER_UNITS, PARAMETER_REFERENCES,
    DIRECTION_MAPPING, ANALYSIS_THRESHOLDS
)

class ImageAnalyzer:
    def __init__(self):
        self.reference_values = {
            'brightness': 128,    # RGB中值
            'contrast': 50,       # 标准对比度
            'saturation': 50,     # 标准饱和度
            'temperature': 6500,  # 标准色温K
            'hue': 0,            # 色调中值
        }

    def analyze_image(self, image_path: str) -> AnalysisResult:
        """
        分析图片并提取滤镜参数

        Args:
            image_path: 图片路径

        Returns:
            AnalysisResult: 分析结果
        """
        start_time = time.time()

        # 加载图片
        image_cv = cv2.imread(image_path)
        image_pil = Image.open(image_path)

        if image_cv is None:
            raise ValueError("无法加载图片")

        # 执行各项分析
        parameters = {}

        # 1. 亮度分析
        brightness_param = self._analyze_brightness(image_cv)
        parameters['brightness'] = brightness_param

        # 2. 对比度分析
        contrast_param = self._analyze_contrast(image_cv)
        parameters['contrast'] = contrast_param

        # 3. 饱和度分析
        saturation_param = self._analyze_saturation(image_cv)
        parameters['saturation'] = saturation_param

        # 4. 锐化分析
        sharpness_param = self._analyze_sharpness(image_cv)
        parameters['sharpness'] = sharpness_param

        # 5. 色温分析
        temperature_param = self._analyze_temperature(image_cv)
        parameters['temperature'] = temperature_param

        # 6. 色调分析
        hue_param = self._analyze_hue(image_cv)
        parameters['hue'] = hue_param

        # 7. 阴影分析
        shadow_param = self._analyze_shadow(image_cv)
        parameters['shadow'] = shadow_param

        # 8. 高光分析
        highlight_param = self._analyze_highlight(image_cv)
        parameters['highlight'] = highlight_param

        analysis_time = time.time() - start_time

        # 计算置信度
        confidence_score = self._calculate_confidence(parameters)

        # 生成图片ID
        from ..utils.file_manager import generate_image_id
        image_id = generate_image_id()

        return AnalysisResult(
            image_id=image_id,
            parameters=parameters,
            analysis_time=analysis_time,
            timestamp=datetime.now(),
            confidence_score=confidence_score
        )

    def _analyze_brightness(self, image: np.ndarray) -> ParameterValue:
        """分析亮度"""
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)

        # 计算相对于标准值的偏差
        reference = self.reference_values['brightness']
        diff_percent = ((mean_brightness - reference) / reference) * 100

        direction = '增加' if diff_percent > 0 else '降低'

        return ParameterValue(
            name=PARAMETER_NAMES['brightness'],
            direction=direction,
            value=abs(diff_percent),
            unit=PARAMETER_UNITS['brightness'],
            reference=PARAMETER_REFERENCES['brightness']
        )

    def _analyze_contrast(self, image: np.ndarray) -> ParameterValue:
        """分析对比度"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 使用标准差计算对比度
        contrast_value = np.std(gray)

        # 标准对比度值约为50，根据这个计算偏差
        reference = 50
        diff_percent = ((contrast_value - reference) / reference) * 100

        direction = '增加' if diff_percent > 0 else '降低'

        return ParameterValue(
            name=PARAMETER_NAMES['contrast'],
            direction=direction,
            value=abs(diff_percent),
            unit=PARAMETER_UNITS['contrast'],
            reference=PARAMETER_REFERENCES['contrast']
        )

    def _analyze_saturation(self, image: np.ndarray) -> ParameterValue:
        """分析饱和度"""
        # 转换为HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        saturation_channel = hsv[:, :, 1]

        mean_saturation = np.mean(saturation_channel)

        # HSV中S通道范围0-255，标准值约127
        reference = 127
        diff_percent = ((mean_saturation - reference) / reference) * 100

        direction = '增加' if diff_percent > 0 else '降低'

        return ParameterValue(
            name=PARAMETER_NAMES['saturation'],
            direction=direction,
            value=abs(diff_percent),
            unit=PARAMETER_UNITS['saturation'],
            reference=PARAMETER_REFERENCES['saturation']
        )

    def _analyze_sharpness(self, image: np.ndarray) -> ParameterValue:
        """分析锐化程度"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 使用Sobel算子计算边缘强度
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)

        sharpness_score = np.mean(sobel_magnitude)

        # 经验值：标准锐化值约为15
        reference = 15
        diff_percent = ((sharpness_score - reference) / reference) * 100

        direction = '增强' if diff_percent > 0 else '减弱'

        return ParameterValue(
            name=PARAMETER_NAMES['sharpness'],
            direction=direction,
            value=abs(diff_percent),
            unit=PARAMETER_UNITS['sharpness'],
            reference=PARAMETER_REFERENCES['sharpness']
        )

    def _analyze_temperature(self, image: np.ndarray) -> ParameterValue:
        """分析色温"""
        # 计算RGB通道平均值
        b, g, r = cv2.split(image)

        mean_r = np.mean(r)
        mean_g = np.mean(g)
        mean_b = np.mean(b)

        # 计算色温偏向 (简化算法)
        # 暖色调：红色分量高，蓝色分量低
        # 冷色调：蓝色分量高，红色分量低
        temperature_ratio = (mean_r - mean_b) / (mean_r + mean_b + 1e-6)

        # 转换为K值偏差 (-500 to +500)
        temperature_offset = temperature_ratio * 300  # 调整系数

        direction = '偏暖' if temperature_offset > 0 else '偏冷'

        return ParameterValue(
            name=PARAMETER_NAMES['temperature'],
            direction=direction,
            value=abs(temperature_offset),
            unit=PARAMETER_UNITS['temperature'],
            reference=PARAMETER_REFERENCES['temperature']
        )

    def _analyze_hue(self, image: np.ndarray) -> ParameterValue:
        """分析色调"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hue_channel = hsv[:, :, 0]

        # HSV中H通道范围0-179 (OpenCV)
        mean_hue = np.mean(hue_channel)

        # 转换为标准色调角度 (0-360°)
        hue_angle = (mean_hue / 179) * 360

        # 判断主要色调偏向
        if hue_angle < 60 or hue_angle > 300:
            direction = '偏红'
            hue_offset = min(hue_angle, 360 - hue_angle)
        elif 60 <= hue_angle < 180:
            direction = '偏绿'
            hue_offset = abs(120 - hue_angle)
        else:
            direction = '偏蓝'
            hue_offset = abs(240 - hue_angle)

        return ParameterValue(
            name=PARAMETER_NAMES['hue'],
            direction=direction,
            value=hue_offset,
            unit=PARAMETER_UNITS['hue'],
            reference=PARAMETER_REFERENCES['hue']
        )

    def _analyze_shadow(self, image: np.ndarray) -> ParameterValue:
        """分析阴影"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 定义阴影区域 (亮度 < 85)
        shadow_mask = gray < 85
        shadow_pixels = gray[shadow_mask]

        if len(shadow_pixels) == 0:
            shadow_brightness = 85
        else:
            shadow_brightness = np.mean(shadow_pixels)

        # 标准阴影亮度约为60
        reference = 60
        diff_percent = ((shadow_brightness - reference) / reference) * 100

        direction = '提亮' if diff_percent > 0 else '压暗'

        return ParameterValue(
            name=PARAMETER_NAMES['shadow'],
            direction=direction,
            value=abs(diff_percent),
            unit=PARAMETER_UNITS['shadow'],
            reference=PARAMETER_REFERENCES['shadow']
        )

    def _analyze_highlight(self, image: np.ndarray) -> ParameterValue:
        """分析高光"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 定义高光区域 (亮度 > 170)
        highlight_mask = gray > 170
        highlight_pixels = gray[highlight_mask]

        if len(highlight_pixels) == 0:
            highlight_brightness = 170
        else:
            highlight_brightness = np.mean(highlight_pixels)

        # 标准高光亮度约为200
        reference = 200
        diff_percent = ((highlight_brightness - reference) / reference) * 100

        direction = '提升' if diff_percent > 0 else '降低'

        return ParameterValue(
            name=PARAMETER_NAMES['highlight'],
            direction=direction,
            value=abs(diff_percent),
            unit=PARAMETER_UNITS['highlight'],
            reference=PARAMETER_REFERENCES['highlight']
        )

    def _calculate_confidence(self, parameters: Dict[str, ParameterValue]) -> float:
        """计算分析置信度"""
        # 基于参数变化幅度计算置信度
        significant_changes = 0
        total_params = len(parameters)

        for param in parameters.values():
            if param.value >= ANALYSIS_THRESHOLDS['min_change_threshold']:
                significant_changes += 1

        # 置信度 = 有显著变化的参数比例
        base_confidence = significant_changes / total_params

        # 添加一些随机性模拟算法不确定性
        confidence = min(0.95, base_confidence + 0.1)

        return round(confidence, 2)

    def extract_filter_parameters(self, analysis_result: AnalysisResult) -> FilterParameter:
        """从分析结果提取标准化滤镜参数"""
        params = FilterParameter()

        for param_name, param_value in analysis_result.parameters.items():
            # 转换方向为数值
            direction_sign = 1 if param_value.direction in ['增加', '增强', '偏暖', '偏红', '提亮', '提升'] else -1

            # 限制参数范围
            if param_name == 'temperature':
                # 色温范围 -500 to +500
                value = min(500, param_value.value) * direction_sign
            elif param_name == 'hue':
                # 色调范围 -180 to +180
                value = min(180, param_value.value) * direction_sign
            else:
                # 其他参数范围 -100 to +100
                value = min(100, param_value.value) * direction_sign

            setattr(params, param_name, round(value, 1))

        return params