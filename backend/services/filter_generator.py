"""
滤镜生成服务
基于分析参数对新图片应用滤镜效果
"""
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from typing import Tuple
import time
import os

from ..models.parameter import FilterParameter
from ..utils.file_manager import generate_image_id, get_file_path
from ..utils.constants import IMAGE_PROCESSING

class FilterGenerator:
    def __init__(self):
        self.processing_methods = {
            'brightness': self._adjust_brightness,
            'contrast': self._adjust_contrast,
            'saturation': self._adjust_saturation,
            'sharpness': self._adjust_sharpness,
            'temperature': self._adjust_temperature,
            'hue': self._adjust_hue,
            'shadow': self._adjust_shadow,
            'highlight': self._adjust_highlight
        }

    def generate_filter_image(self, original_image_path: str, parameters: FilterParameter,
                            output_folder: str) -> Tuple[str, str, float]:
        """
        基于参数生成滤镜图片

        Args:
            original_image_path: 原始图片路径
            parameters: 滤镜参数
            output_folder: 输出文件夹

        Returns:
            (output_image_id, output_filename, processing_time)
        """
        start_time = time.time()

        # 加载原始图片
        image = Image.open(original_image_path)

        # 确保图片为RGB模式
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # 按顺序应用各种滤镜效果
        processed_image = self._apply_all_filters(image, parameters)

        # 生成输出文件信息
        output_image_id = generate_image_id()
        output_filename = f"{output_image_id}.jpg"
        output_path = get_file_path(output_folder, output_image_id, 'jpg')

        # 保存处理后的图片
        processed_image.save(
            output_path,
            'JPEG',
            quality=IMAGE_PROCESSING['default_quality'],
            optimize=True
        )

        processing_time = time.time() - start_time

        return output_image_id, output_filename, processing_time

    def _apply_all_filters(self, image: Image.Image, parameters: FilterParameter) -> Image.Image:
        """应用所有滤镜效果"""
        result_image = image.copy()

        # 1. 亮度调整
        if abs(parameters.brightness) > 1:
            result_image = self._adjust_brightness(result_image, parameters.brightness)

        # 2. 对比度调整
        if abs(parameters.contrast) > 1:
            result_image = self._adjust_contrast(result_image, parameters.contrast)

        # 3. 饱和度调整
        if abs(parameters.saturation) > 1:
            result_image = self._adjust_saturation(result_image, parameters.saturation)

        # 4. 色温调整
        if abs(parameters.temperature) > 10:
            result_image = self._adjust_temperature(result_image, parameters.temperature)

        # 5. 色调调整
        if abs(parameters.hue) > 5:
            result_image = self._adjust_hue(result_image, parameters.hue)

        # 6. 阴影/高光调整
        if abs(parameters.shadow) > 1 or abs(parameters.highlight) > 1:
            result_image = self._adjust_shadow_highlight(result_image, parameters.shadow, parameters.highlight)

        # 7. 锐化调整 (最后应用)
        if abs(parameters.sharpness) > 1:
            result_image = self._adjust_sharpness(result_image, parameters.sharpness)

        return result_image

    def _adjust_brightness(self, image: Image.Image, value: float) -> Image.Image:
        """调整亮度 (-100 to +100)"""
        # 转换为增强因子 (0.5 to 1.5)
        factor = 1.0 + (value / 100.0)
        factor = max(0.1, min(2.0, factor))  # 限制范围

        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)

    def _adjust_contrast(self, image: Image.Image, value: float) -> Image.Image:
        """调整对比度 (-100 to +100)"""
        factor = 1.0 + (value / 100.0)
        factor = max(0.1, min(2.0, factor))

        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)

    def _adjust_saturation(self, image: Image.Image, value: float) -> Image.Image:
        """调整饱和度 (-100 to +100)"""
        factor = 1.0 + (value / 100.0)
        factor = max(0.0, min(2.0, factor))

        enhancer = ImageEnhance.Color(image)
        return enhancer.enhance(factor)

    def _adjust_sharpness(self, image: Image.Image, value: float) -> Image.Image:
        """调整锐化 (-100 to +100)"""
        if value > 0:
            # 增强锐化
            factor = 1.0 + (value / 100.0)
            enhancer = ImageEnhance.Sharpness(image)
            return enhancer.enhance(factor)
        else:
            # 模糊处理
            blur_radius = abs(value) / 50.0  # 0-2的模糊半径
            return image.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    def _adjust_temperature(self, image: Image.Image, value: float) -> Image.Image:
        """调整色温 (-500K to +500K)"""
        # 转换PIL图像为numpy数组
        img_array = np.array(image, dtype=np.float32)

        # 色温调整系数
        temp_factor = value / 500.0  # -1 to +1

        if temp_factor > 0:
            # 偏暖：增加红色，减少蓝色
            img_array[:, :, 0] *= (1.0 + temp_factor * 0.3)  # R
            img_array[:, :, 2] *= (1.0 - temp_factor * 0.3)  # B
        else:
            # 偏冷：减少红色，增加蓝色
            img_array[:, :, 0] *= (1.0 + temp_factor * 0.3)  # R
            img_array[:, :, 2] *= (1.0 - temp_factor * 0.3)  # B

        # 限制像素值范围
        img_array = np.clip(img_array, 0, 255)

        return Image.fromarray(img_array.astype(np.uint8))

    def _adjust_hue(self, image: Image.Image, value: float) -> Image.Image:
        """调整色调 (-180° to +180°)"""
        # 转换为HSV
        img_array = np.array(image)
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV).astype(np.float32)

        # 调整色调 (H通道)
        hue_shift = (value / 180.0) * 90  # 转换为OpenCV范围
        hsv[:, :, 0] = (hsv[:, :, 0] + hue_shift) % 180

        # 转换回RGB
        rgb = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
        return Image.fromarray(rgb)

    def _adjust_shadow_highlight(self, image: Image.Image, shadow: float, highlight: float) -> Image.Image:
        """调整阴影和高光"""
        img_array = np.array(image, dtype=np.float32) / 255.0

        # 计算亮度
        luminance = 0.299 * img_array[:, :, 0] + 0.587 * img_array[:, :, 1] + 0.114 * img_array[:, :, 2]

        # 阴影调整 (暗部)
        if abs(shadow) > 1:
            shadow_factor = 1.0 + (shadow / 100.0)
            shadow_mask = luminance < 0.3
            for c in range(3):
                img_array[:, :, c][shadow_mask] *= shadow_factor

        # 高光调整 (亮部)
        if abs(highlight) > 1:
            highlight_factor = 1.0 + (highlight / 100.0)
            highlight_mask = luminance > 0.7
            for c in range(3):
                img_array[:, :, c][highlight_mask] *= highlight_factor

        # 限制像素值范围
        img_array = np.clip(img_array * 255, 0, 255)

        return Image.fromarray(img_array.astype(np.uint8))

    def preview_filter_effect(self, original_image_path: str, parameters: FilterParameter,
                            max_size: Tuple[int, int] = (400, 400)) -> Image.Image:
        """
        生成滤镜效果预览图 (不保存到文件)

        Args:
            original_image_path: 原始图片路径
            parameters: 滤镜参数
            max_size: 预览图最大尺寸

        Returns:
            处理后的预览图
        """
        # 加载并缩放图片
        image = Image.open(original_image_path)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)

        if image.mode != 'RGB':
            image = image.convert('RGB')

        # 应用滤镜效果
        return self._apply_all_filters(image, parameters)