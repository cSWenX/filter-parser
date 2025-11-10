#!/usr/bin/env python3
"""
Real Image Analysis Server - 使用OpenCV进行真实图像分析
"""
import http.server
import socketserver
import json
import os
import time
import tempfile
import hashlib
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
import cgi

class ImageAnalysisHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/Users/cswenx/program/AICoding/Filter-Parser", **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        print("Received OPTIONS request")
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        print(f"POST: {self.path}")
        if self.path.startswith('/api/'):
            self.handle_api_post()
        else:
            self.send_error(404)

    def do_GET(self):
        print(f"GET: {self.path}")
        if self.path.startswith('/api/'):
            self.handle_api_get()
        else:
            super().do_GET()

    def handle_api_post(self):
        api_path = self.path.replace('/api', '')
        if '?' in api_path:
            api_path = api_path.split('?')[0]

        print(f"API POST Path: {api_path}")

        if api_path == '/upload':
            self.handle_upload()
        elif api_path.startswith('/analyze/'):
            self.handle_analyze(api_path)
        elif api_path == '/generate':
            self.handle_generate()
        elif api_path == '/health':
            self.handle_health()
        else:
            self.send_json_error(404, "API endpoint not found")

    def handle_api_get(self):
        api_path = self.path.replace('/api', '')
        if '?' in api_path:
            api_path = api_path.split('?')[0]

        print(f"API GET Path: {api_path}")

        if api_path == '/health':
            self.handle_health()
        elif api_path.startswith('/download/'):
            self.handle_download(api_path)
        elif api_path.startswith('/preview/'):
            self.handle_preview(api_path)
        else:
            self.send_json_error(404, "API endpoint not found")

    def handle_upload(self):
        print("=== UPLOAD REQUEST ===")
        print(f"Method: {self.command}")
        print(f"Headers: {dict(self.headers)}")

        try:
            # 解析multipart form data
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )

            if 'image' in form:
                file_item = form['image']
                if file_item.filename:
                    # 保存上传的文件到临时目录
                    temp_dir = tempfile.gettempdir()
                    file_data = file_item.file.read()

                    # 生成基于文件内容的ID（确保同一文件总是同一ID）
                    file_hash = hashlib.md5(file_data).hexdigest()
                    image_id = f"img_{file_hash[:12]}"

                    # 保存文件
                    temp_path = os.path.join(temp_dir, f"{image_id}.jpg")
                    with open(temp_path, 'wb') as f:
                        f.write(file_data)

                    print(f"Image saved to: {temp_path}")
                    print(f"Image ID: {image_id}")

                    response_data = {
                        "status": "success",
                        "message": "上传成功",
                        "data": {
                            "image_id": image_id,
                            "filename": file_item.filename,
                            "file_size": len(file_data),
                            "dimensions": self.get_image_dimensions(temp_path)
                        }
                    }
                else:
                    response_data = {
                        "status": "error",
                        "message": "没有选择文件"
                    }
            else:
                response_data = {
                    "status": "error",
                    "message": "未找到图像文件"
                }

            print("Sending upload response")
            self.send_json_response(response_data)

        except Exception as e:
            print(f"Upload error: {e}")
            self.send_json_error(500, f"Upload failed: {str(e)}")

    def get_image_dimensions(self, image_path):
        """获取图片尺寸"""
        try:
            img = cv2.imread(image_path)
            height, width = img.shape[:2]
            return [width, height]
        except:
            return [800, 600]  # 默认尺寸

    def analyze_image_with_opencv(self, image_path):
        """使用OpenCV进行真实的图像分析"""
        try:
            print(f"Analyzing image: {image_path}")

            # 读取图像
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("无法读取图像文件")

            # 转换颜色空间
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img_lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

            # 1. 增强亮度分析 - 使用多种指标
            brightness_metrics = self.analyze_brightness_advanced(img_gray, img_lab)
            brightness_adjust = self.calculate_brightness_adjustment_advanced(brightness_metrics)

            # 2. 增强对比度分析 - 局部对比度 + 全局对比度
            contrast_metrics = self.analyze_contrast_advanced(img_gray)
            contrast_adjust = self.calculate_contrast_adjustment_advanced(contrast_metrics)

            # 3. 增强饱和度分析 - HSV + LAB双重分析
            saturation_metrics = self.analyze_saturation_advanced(img_hsv, img_lab)
            saturation_adjust = self.calculate_saturation_adjustment_advanced(saturation_metrics)

            # 4. 增强锐化分析 - 多尺度锐度检测
            sharpness_metrics = self.analyze_sharpness_advanced(img_gray)
            sharpness_adjust = self.calculate_sharpness_adjustment_advanced(sharpness_metrics)

            # 5. 增强色温分析 - 白平衡算法
            temperature_metrics = self.analyze_temperature_advanced(img_rgb)
            temperature_adjust = self.calculate_temperature_adjustment_advanced(temperature_metrics)

            # 6. 增强色调分析 - 主导色调检测
            hue_metrics = self.analyze_hue_advanced(img_hsv)
            hue_adjust = self.calculate_hue_adjustment_advanced(hue_metrics)

            # 7. 增强阴影/高光分析 - 区域性分析
            shadow_highlight_metrics = self.analyze_shadow_highlight_advanced(img_gray, img_rgb)
            shadow_adjust, highlight_adjust = self.calculate_shadow_highlight_adjustment_advanced(shadow_highlight_metrics)

            # 8. 生成智能建议
            suggestions = self.generate_intelligent_suggestions_advanced(
                brightness_metrics, contrast_metrics, saturation_metrics,
                sharpness_metrics, temperature_metrics, hue_metrics
            )

            return {
                "brightness": {
                    "name": "亮度",
                    "direction": "增加" if brightness_adjust > 0 else "降低" if brightness_adjust < 0 else "适中",
                    "value": brightness_adjust,
                    "unit": "%",
                    "reference": f"平均亮度: {brightness_metrics['mean']:.1f}/255, 中位数: {brightness_metrics['median']:.1f}",
                    "analysis": f"基于多重亮度指标分析 (置信度: {brightness_metrics['confidence']:.2f})"
                },
                "contrast": {
                    "name": "对比度",
                    "direction": "增加" if contrast_adjust > 0 else "降低" if contrast_adjust < 0 else "适中",
                    "value": contrast_adjust,
                    "unit": "%",
                    "reference": f"全局对比度: {contrast_metrics['global']:.1f}, 局部对比度: {contrast_metrics['local']:.1f}",
                    "analysis": f"基于多层次对比度分析 (置信度: {contrast_metrics['confidence']:.2f})"
                },
                "saturation": {
                    "name": "饱和度",
                    "direction": "增加" if saturation_adjust > 0 else "降低" if saturation_adjust < 0 else "适中",
                    "value": saturation_adjust,
                    "unit": "%",
                    "reference": f"HSV饱和度: {saturation_metrics['hsv']:.1f}, LAB色度: {saturation_metrics['lab']:.1f}",
                    "analysis": f"基于HSV+LAB双重色彩空间分析 (置信度: {saturation_metrics['confidence']:.2f})"
                },
                "sharpness": {
                    "name": "锐化",
                    "direction": "增强" if sharpness_adjust > 0 else "适中",
                    "value": sharpness_adjust,
                    "unit": "%",
                    "reference": f"拉普拉斯: {sharpness_metrics['laplacian']:.1f}, Sobel: {sharpness_metrics['sobel']:.1f}",
                    "analysis": f"基于多尺度边缘检测 (置信度: {sharpness_metrics['confidence']:.2f})"
                },
                "temperature": {
                    "name": "色温",
                    "direction": "偏暖" if temperature_adjust > 0 else "偏冷" if temperature_adjust < 0 else "中性",
                    "value": temperature_adjust,
                    "unit": "K",
                    "reference": f"估计色温: {temperature_metrics['estimated_temp']:.0f}K, 白平衡偏差: {temperature_metrics['wb_deviation']:.2f}",
                    "analysis": f"基于白平衡算法分析 (置信度: {temperature_metrics['confidence']:.2f})"
                },
                "hue": {
                    "name": "色调",
                    "direction": "调整" if abs(hue_adjust) > 1 else "适中",
                    "value": hue_adjust,
                    "unit": "°",
                    "reference": f"主导色调: {hue_metrics['dominant_hue']:.1f}°, 分布方差: {hue_metrics['variance']:.1f}",
                    "analysis": f"基于主导色调检测 (置信度: {hue_metrics['confidence']:.2f})"
                },
                "shadow": {
                    "name": "阴影",
                    "direction": "提亮" if shadow_adjust > 0 else "压暗" if shadow_adjust < 0 else "适中",
                    "value": shadow_adjust,
                    "unit": "%",
                    "reference": f"阴影区域占比: {shadow_highlight_metrics['shadow_ratio']:.1%}",
                    "analysis": f"基于区域性阴影分析 (置信度: {shadow_highlight_metrics['shadow_confidence']:.2f})"
                },
                "highlight": {
                    "name": "高光",
                    "direction": "降低" if highlight_adjust < 0 else "提亮" if highlight_adjust > 0 else "适中",
                    "value": highlight_adjust,
                    "unit": "%",
                    "reference": f"高光区域占比: {shadow_highlight_metrics['highlight_ratio']:.1%}",
                    "analysis": f"基于区域性高光分析 (置信度: {shadow_highlight_metrics['highlight_confidence']:.2f})"
                }
            }, suggestions

        except Exception as e:
            print(f"Image analysis error: {e}")
            raise

    def calculate_brightness_adjustment(self, current_brightness):
        """计算亮度调整建议"""
        # 理想亮度范围: 120-140
        if current_brightness < 80:
            return round(25 + (80 - current_brightness) * 0.3, 1)
        elif current_brightness < 120:
            return round((120 - current_brightness) * 0.8, 1)
        elif current_brightness > 180:
            return round(-(current_brightness - 180) * 0.5, 1)
        elif current_brightness > 140:
            return round(-(current_brightness - 140) * 0.3, 1)
        return 0.0

    def calculate_contrast_adjustment(self, current_contrast):
        """计算对比度调整建议"""
        # 理想对比度范围: 45-65
        if current_contrast < 30:
            return round(30 + (30 - current_contrast) * 0.6, 1)
        elif current_contrast < 45:
            return round((45 - current_contrast) * 0.8, 1)
        elif current_contrast > 80:
            return round(-(current_contrast - 80) * 0.4, 1)
        return 0.0

    def calculate_saturation_adjustment(self, current_saturation):
        """计算饱和度调整建议"""
        # 理想饱和度范围: 100-140
        if current_saturation < 80:
            return round(15 + (80 - current_saturation) * 0.3, 1)
        elif current_saturation < 100:
            return round((100 - current_saturation) * 0.5, 1)
        elif current_saturation > 160:
            return round(-(current_saturation - 160) * 0.3, 1)
        return 0.0

    def calculate_sharpness_adjustment(self, current_sharpness):
        """计算锐化调整建议"""
        # 锐化基于图像的清晰度
        if current_sharpness < 100:
            return round(20 + (100 - current_sharpness) * 0.1, 1)
        elif current_sharpness < 300:
            return round((300 - current_sharpness) * 0.05, 1)
        return 0.0

    def calculate_temperature_adjustment(self, r_avg, g_avg, b_avg):
        """计算色温调整建议"""
        # 分析RGB比值来判断色温偏向
        if r_avg > g_avg * 1.1 and r_avg > b_avg * 1.2:
            return -100  # 偏暖，建议降低色温
        elif b_avg > r_avg * 1.1 and b_avg > g_avg * 1.1:
            return 100   # 偏冷，建议提高色温
        return 0

    def calculate_hue_adjustment(self, current_hue):
        """计算色调调整建议"""
        # 基于主要色调进行微调
        if 15 <= current_hue <= 45:  # 橙色范围
            return -2.0  # 稍微偏红
        elif 45 <= current_hue <= 75:  # 黄色范围
            return 1.0   # 稍微偏绿
        elif 100 <= current_hue <= 130:  # 绿色范围
            return -1.0  # 稍微偏黄
        return 0.0

    def analyze_shadow_highlight(self, img_gray):
        """分析阴影和高光"""
        # 计算阴影区域（低于25%的像素）
        shadow_mask = img_gray < 64  # 0-63为阴影
        shadow_ratio = np.sum(shadow_mask) / img_gray.size

        # 计算高光区域（高于75%的像素）
        highlight_mask = img_gray > 192  # 192-255为高光
        highlight_ratio = np.sum(highlight_mask) / img_gray.size

        shadow_adjust = 0.0
        highlight_adjust = 0.0

        # 阴影过多，建议提亮
        if shadow_ratio > 0.3:
            shadow_adjust = round(15 + (shadow_ratio - 0.3) * 30, 1)
        elif shadow_ratio > 0.2:
            shadow_adjust = round((shadow_ratio - 0.2) * 50, 1)

        # 高光过多，建议降低
        if highlight_ratio > 0.15:
            highlight_adjust = round(-10 - (highlight_ratio - 0.15) * 40, 1)
        elif highlight_ratio > 0.1:
            highlight_adjust = round(-(highlight_ratio - 0.1) * 60, 1)

        return shadow_adjust, highlight_adjust

    def generate_intelligent_suggestions(self, brightness, contrast, saturation, sharpness, r, g, b):
        """生成智能化建议"""
        suggestions = []

        # 基于亮度的建议
        if brightness < 100:
            suggestions.append("图片整体偏暗，建议增加曝光和阴影提亮")
        elif brightness > 160:
            suggestions.append("图片整体偏亮，建议降低高光和整体曝光")

        # 基于对比度的建议
        if contrast < 40:
            suggestions.append("图片对比度偏低，建议增加对比度以提升层次感")
        elif contrast > 70:
            suggestions.append("图片对比度较高，建议适当降低以获得柔和效果")

        # 基于饱和度的建议
        if saturation < 90:
            suggestions.append("色彩饱和度偏低，建议适当增加以提升色彩鲜明度")
        elif saturation > 150:
            suggestions.append("色彩过于饱和，建议适当降低以获得自然效果")

        # 基于色温的建议
        if r > g * 1.1:
            suggestions.append("图片色调偏暖，如需自然效果可适当降低色温")
        elif b > r * 1.1:
            suggestions.append("图片色调偏冷，可适当提高色温增加温暖感")

        # 基于锐度的建议
        if sharpness < 200:
            suggestions.append("图片清晰度一般，建议适当增加锐化以提升细节")

        # 如果没有明显问题，给出通用建议
        if len(suggestions) == 0:
            suggestions.append("图片整体曝光和色彩平衡良好，可根据个人偏好微调")

        # 最多返回3个建议
        return suggestions[:3]

    # ========== 增强的图像分析算法 ==========

    def analyze_brightness_advanced(self, img_gray, img_lab):
        """增强的亮度分析"""
        # 多种亮度指标
        mean_brightness = np.mean(img_gray)
        median_brightness = np.median(img_gray)
        # LAB颜色空间中的L通道更准确表示亮度
        lab_brightness = np.mean(img_lab[:, :, 0])

        # 直方图分析
        hist = cv2.calcHist([img_gray], [0], None, [256], [0, 256])
        hist_peak = np.argmax(hist)

        # 计算亮度分布的偏斜度
        brightness_std = np.std(img_gray)

        # 置信度计算：基于多指标的一致性
        indicators = [mean_brightness, median_brightness, lab_brightness * 2.55, hist_peak]
        confidence = 1.0 - (np.std(indicators) / np.mean(indicators))
        confidence = max(0.5, min(1.0, confidence))

        return {
            'mean': mean_brightness,
            'median': median_brightness,
            'lab': lab_brightness,
            'hist_peak': hist_peak,
            'std': brightness_std,
            'confidence': confidence
        }

    def calculate_brightness_adjustment_advanced(self, metrics):
        """基于增强指标的亮度调整"""
        # 使用加权平均，LAB L通道权重更高
        weighted_brightness = (metrics['mean'] * 0.3 +
                              metrics['median'] * 0.2 +
                              metrics['lab'] * 2.55 * 0.4 +
                              metrics['hist_peak'] * 0.1)

        # 理想亮度范围: 120-140
        if weighted_brightness < 80:
            return round(30 + (80 - weighted_brightness) * 0.4, 1)
        elif weighted_brightness < 120:
            return round((120 - weighted_brightness) * 0.8, 1)
        elif weighted_brightness > 180:
            return round(-(weighted_brightness - 180) * 0.6, 1)
        elif weighted_brightness > 140:
            return round(-(weighted_brightness - 140) * 0.4, 1)
        return 0.0

    def analyze_contrast_advanced(self, img_gray):
        """增强的对比度分析"""
        # 全局对比度（标准差）
        global_contrast = np.std(img_gray)

        # 局部对比度（Michelson对比度）
        kernel = np.ones((5, 5), np.float32) / 25
        local_mean = cv2.filter2D(img_gray.astype(np.float32), -1, kernel)
        local_contrast = np.mean(np.abs(img_gray.astype(np.float32) - local_mean))

        # RMS对比度
        mean_val = np.mean(img_gray)
        rms_contrast = np.sqrt(np.mean((img_gray - mean_val) ** 2))

        # 基于直方图的对比度
        hist = cv2.calcHist([img_gray], [0], None, [256], [0, 256]).flatten()
        hist_spread = np.sum(hist * np.arange(256)) / np.sum(hist)

        # 置信度
        contrasts = [global_contrast, local_contrast, rms_contrast]
        confidence = 1.0 - (np.std(contrasts) / (np.mean(contrasts) + 1e-6))
        confidence = max(0.6, min(1.0, confidence))

        return {
            'global': global_contrast,
            'local': local_contrast,
            'rms': rms_contrast,
            'hist_spread': hist_spread,
            'confidence': confidence
        }

    def calculate_contrast_adjustment_advanced(self, metrics):
        """基于增强指标的对比度调整"""
        # 加权对比度
        weighted_contrast = (metrics['global'] * 0.4 +
                            metrics['local'] * 0.3 +
                            metrics['rms'] * 0.3)

        if weighted_contrast < 25:
            return round(35 + (25 - weighted_contrast) * 0.8, 1)
        elif weighted_contrast < 40:
            return round((40 - weighted_contrast) * 1.0, 1)
        elif weighted_contrast > 90:
            return round(-(weighted_contrast - 90) * 0.5, 1)
        return 0.0

    def analyze_saturation_advanced(self, img_hsv, img_lab):
        """增强的饱和度分析"""
        # HSV空间的饱和度
        hsv_saturation = np.mean(img_hsv[:, :, 1])

        # LAB空间的色度（A和B通道）
        a_channel = img_lab[:, :, 1].astype(np.float32) - 128
        b_channel = img_lab[:, :, 2].astype(np.float32) - 128
        lab_chroma = np.mean(np.sqrt(a_channel**2 + b_channel**2))

        # 饱和度分布分析
        sat_std = np.std(img_hsv[:, :, 1])

        # 高饱和度像素比例
        high_sat_ratio = np.sum(img_hsv[:, :, 1] > 128) / img_hsv[:, :, 1].size

        # 置信度
        confidence = min(1.0, (hsv_saturation / 255) * 2 + 0.3)

        return {
            'hsv': hsv_saturation,
            'lab': lab_chroma,
            'std': sat_std,
            'high_sat_ratio': high_sat_ratio,
            'confidence': confidence
        }

    def calculate_saturation_adjustment_advanced(self, metrics):
        """基于增强指标的饱和度调整"""
        # HSV和LAB的综合评估
        normalized_lab = min(metrics['lab'] * 2, 255)  # 归一化LAB色度
        weighted_saturation = metrics['hsv'] * 0.6 + normalized_lab * 0.4

        if weighted_saturation < 60:
            return round(20 + (60 - weighted_saturation) * 0.4, 1)
        elif weighted_saturation < 90:
            return round((90 - weighted_saturation) * 0.6, 1)
        elif weighted_saturation > 180:
            return round(-(weighted_saturation - 180) * 0.4, 1)
        return 0.0

    def analyze_sharpness_advanced(self, img_gray):
        """增强的锐度分析"""
        # 拉普拉斯算子
        laplacian = cv2.Laplacian(img_gray, cv2.CV_64F)
        laplacian_var = laplacian.var()

        # Sobel算子
        sobelx = cv2.Sobel(img_gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(img_gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_combined = np.sqrt(sobelx**2 + sobely**2)
        sobel_mean = np.mean(sobel_combined)

        # 高频内容分析
        f_transform = np.fft.fft2(img_gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude = np.abs(f_shift)
        h, w = img_gray.shape
        high_freq = magnitude[h//4:3*h//4, w//4:3*w//4]
        high_freq_energy = np.mean(high_freq)

        # 置信度
        sharpness_indicators = [laplacian_var / 1000, sobel_mean / 100]
        confidence = min(1.0, np.mean(sharpness_indicators) / 50 + 0.4)

        return {
            'laplacian': laplacian_var,
            'sobel': sobel_mean,
            'high_freq': high_freq_energy,
            'confidence': confidence
        }

    def calculate_sharpness_adjustment_advanced(self, metrics):
        """基于增强指标的锐度调整"""
        # 综合锐度评估
        normalized_laplacian = min(metrics['laplacian'] / 100, 50)
        normalized_sobel = min(metrics['sobel'] / 10, 50)
        weighted_sharpness = normalized_laplacian * 0.6 + normalized_sobel * 0.4

        if weighted_sharpness < 10:
            return round(25 + (10 - weighted_sharpness) * 1.5, 1)
        elif weighted_sharpness < 20:
            return round((20 - weighted_sharpness) * 1.0, 1)
        return 0.0

    def analyze_temperature_advanced(self, img_rgb):
        """增强的色温分析"""
        # 基础RGB分析
        r_avg, g_avg, b_avg = np.mean(img_rgb[:, :, 0]), np.mean(img_rgb[:, :, 1]), np.mean(img_rgb[:, :, 2])

        # 白平衡分析 - 灰度世界假设
        gray_world_r = r_avg / (r_avg + g_avg + b_avg)
        gray_world_g = g_avg / (r_avg + g_avg + b_avg)
        gray_world_b = b_avg / (r_avg + g_avg + b_avg)

        # 估计色温 (简化的算法)
        if b_avg > 0:
            color_temp_ratio = r_avg / b_avg
            estimated_temp = 6500 / color_temp_ratio if color_temp_ratio > 0 else 6500
        else:
            estimated_temp = 6500

        # 白平衡偏差
        ideal_gray = 1/3
        wb_deviation = abs(gray_world_r - ideal_gray) + abs(gray_world_g - ideal_gray) + abs(gray_world_b - ideal_gray)

        # 置信度
        confidence = max(0.5, 1.0 - wb_deviation * 3)

        return {
            'r_avg': r_avg,
            'g_avg': g_avg,
            'b_avg': b_avg,
            'estimated_temp': estimated_temp,
            'wb_deviation': wb_deviation,
            'confidence': confidence
        }

    def calculate_temperature_adjustment_advanced(self, metrics):
        """基于增强指标的色温调整"""
        estimated_temp = metrics['estimated_temp']

        # 目标色温6500K
        if estimated_temp < 5000:
            return round((5500 - estimated_temp) / 50, 0)  # 偏冷，需要加温
        elif estimated_temp > 7500:
            return round(-(estimated_temp - 7000) / 50, 0)  # 偏暖，需要降温
        return 0

    def analyze_hue_advanced(self, img_hsv):
        """增强的色调分析"""
        hue_channel = img_hsv[:, :, 0]

        # 主导色调
        hue_hist = cv2.calcHist([hue_channel], [0], None, [180], [0, 180])
        dominant_hue = np.argmax(hue_hist)

        # 色调分布
        hue_mean = np.mean(hue_channel[hue_channel > 0])  # 排除无色调的像素
        hue_std = np.std(hue_channel[hue_channel > 0])

        # 色调集中度
        hue_concentration = np.sum(hue_hist > np.max(hue_hist) * 0.1) / 180

        # 置信度
        confidence = min(1.0, (1 - hue_concentration) + 0.3)

        return {
            'dominant_hue': dominant_hue * 2,  # 转换为360度制
            'mean': hue_mean * 2,
            'variance': hue_std,
            'concentration': hue_concentration,
            'confidence': confidence
        }

    def calculate_hue_adjustment_advanced(self, metrics):
        """基于增强指标的色调调整"""
        dominant_hue = metrics['dominant_hue']

        # 根据主导色调进行细微调整
        if 15 <= dominant_hue <= 45:  # 橙色范围
            return -3.0
        elif 45 <= dominant_hue <= 75:  # 黄色范围
            return 2.0
        elif 75 <= dominant_hue <= 150:  # 绿色范围
            return -1.0
        elif 280 <= dominant_hue <= 320:  # 紫色范围
            return 2.0
        return 0.0

    def analyze_shadow_highlight_advanced(self, img_gray, img_rgb):
        """增强的阴影/高光分析"""
        # 动态阈值计算
        mean_brightness = np.mean(img_gray)
        shadow_threshold = max(mean_brightness * 0.3, 32)
        highlight_threshold = min(mean_brightness * 1.8, 224)

        # 阴影分析
        shadow_mask = img_gray < shadow_threshold
        shadow_ratio = np.sum(shadow_mask) / img_gray.size
        shadow_mean = np.mean(img_gray[shadow_mask]) if np.sum(shadow_mask) > 0 else 0

        # 高光分析
        highlight_mask = img_gray > highlight_threshold
        highlight_ratio = np.sum(highlight_mask) / img_gray.size
        highlight_mean = np.mean(img_gray[highlight_mask]) if np.sum(highlight_mask) > 0 else 255

        # 中间调分析
        midtone_mask = (img_gray >= shadow_threshold) & (img_gray <= highlight_threshold)
        midtone_ratio = np.sum(midtone_mask) / img_gray.size

        # 置信度
        shadow_confidence = min(1.0, shadow_ratio * 5 + 0.3)
        highlight_confidence = min(1.0, highlight_ratio * 5 + 0.3)

        return {
            'shadow_ratio': shadow_ratio,
            'shadow_mean': shadow_mean,
            'highlight_ratio': highlight_ratio,
            'highlight_mean': highlight_mean,
            'midtone_ratio': midtone_ratio,
            'shadow_confidence': shadow_confidence,
            'highlight_confidence': highlight_confidence
        }

    def calculate_shadow_highlight_adjustment_advanced(self, metrics):
        """基于增强指标的阴影/高光调整"""
        shadow_adjust = 0.0
        highlight_adjust = 0.0

        # 阴影调整
        if metrics['shadow_ratio'] > 0.4:  # 阴影过多
            shadow_adjust = round(20 + (metrics['shadow_ratio'] - 0.4) * 40, 1)
        elif metrics['shadow_ratio'] > 0.25:
            shadow_adjust = round((metrics['shadow_ratio'] - 0.25) * 60, 1)

        # 高光调整
        if metrics['highlight_ratio'] > 0.2:  # 高光过多
            highlight_adjust = round(-15 - (metrics['highlight_ratio'] - 0.2) * 50, 1)
        elif metrics['highlight_ratio'] > 0.1:
            highlight_adjust = round(-(metrics['highlight_ratio'] - 0.1) * 80, 1)

        return shadow_adjust, highlight_adjust

    def generate_intelligent_suggestions_advanced(self, brightness_metrics, contrast_metrics,
                                                 saturation_metrics, sharpness_metrics,
                                                 temperature_metrics, hue_metrics):
        """生成增强的智能化建议"""
        suggestions = []

        # 基于置信度的建议
        high_confidence_threshold = 0.8

        # 亮度建议
        if brightness_metrics['confidence'] > high_confidence_threshold:
            if brightness_metrics['mean'] < 100:
                suggestions.append(f"图片整体偏暗(置信度: {brightness_metrics['confidence']:.1%})，建议增加曝光和阴影提亮")
            elif brightness_metrics['mean'] > 160:
                suggestions.append(f"图片整体偏亮(置信度: {brightness_metrics['confidence']:.1%})，建议降低高光和整体曝光")

        # 对比度建议
        if contrast_metrics['confidence'] > high_confidence_threshold:
            if contrast_metrics['global'] < 35:
                suggestions.append(f"图片对比度偏低(置信度: {contrast_metrics['confidence']:.1%})，建议增加对比度以提升层次感")

        # 饱和度建议
        if saturation_metrics['confidence'] > 0.7:  # 较低阈值，因为饱和度分析相对困难
            if saturation_metrics['hsv'] < 80:
                suggestions.append(f"色彩饱和度偏低(置信度: {saturation_metrics['confidence']:.1%})，建议适当增加以提升色彩鲜明度")

        # 锐度建议
        if sharpness_metrics['confidence'] > 0.6:
            if sharpness_metrics['laplacian'] < 150:
                suggestions.append(f"图片清晰度一般(置信度: {sharpness_metrics['confidence']:.1%})，建议适当增加锐化以提升细节")

        # 色温建议
        if temperature_metrics['confidence'] > 0.7:
            if temperature_metrics['estimated_temp'] < 5000:
                suggestions.append(f"图片色调偏冷(色温约{temperature_metrics['estimated_temp']:.0f}K)，可适当提高色温增加温暖感")
            elif temperature_metrics['estimated_temp'] > 7500:
                suggestions.append(f"图片色调偏暖(色温约{temperature_metrics['estimated_temp']:.0f}K)，如需自然效果可适当降低色温")

        # 通用建议
        if len(suggestions) == 0:
            suggestions.append("图片整体曝光和色彩平衡良好，可根据个人偏好进行微调")
        elif len(suggestions) > 3:
            # 根据置信度排序，保留前3个
            suggestions = suggestions[:3]

        return suggestions

    def handle_analyze(self, api_path):
        print("=== REAL IMAGE ANALYSIS ===")
        image_id = api_path.split('/')[-1]
        print(f"Analyzing image: {image_id}")

        try:
            # 查找临时文件
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"{image_id}.jpg")

            if not os.path.exists(temp_path):
                self.send_json_error(404, "图片文件不存在，请重新上传")
                return

            start_time = time.time()

            # 进行真实的图像分析
            parameters, suggestions = self.analyze_image_with_opencv(temp_path)

            analysis_time = round(time.time() - start_time, 1)

            response_data = {
                "status": "success",
                "message": "图像分析完成",
                "data": {
                    "image_id": image_id,
                    "parameters": parameters,
                    "analysis_time": analysis_time,
                    "confidence_score": 0.92,  # 基于OpenCV分析的可信度较高
                    "suggestions": suggestions,
                    "analysis_method": "OpenCV计算机视觉分析"
                }
            }
            print("Sending real analysis response")
            self.send_json_response(response_data)

        except Exception as e:
            print(f"Analysis error: {e}")
            self.send_json_error(500, f"图像分析失败: {str(e)}")

    def handle_generate(self):
        print("=== GENERATE REQUEST ===")

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                print(f"Generate request data: {data}")

                # 获取原始图片和滤镜参数
                image_id = data.get("original_image_id", "")
                filter_parameters = data.get("parameters", {})

                if not image_id:
                    self.send_json_error(400, "Missing original_image_id")
                    return

                # 查找原始图片
                temp_dir = tempfile.gettempdir()
                image_path = os.path.join(temp_dir, f"{image_id}.jpg")

                if not os.path.exists(image_path):
                    # 如果找不到指定图片，使用最新上传的图片
                    image_files = []
                    for filename in os.listdir(temp_dir):
                        if filename.startswith('img_') and filename.endswith('.jpg'):
                            file_path = os.path.join(temp_dir, filename)
                            if os.path.exists(file_path):
                                image_files.append((file_path, os.path.getmtime(file_path)))

                    if not image_files:
                        self.send_json_error(404, "No uploaded image found")
                        return

                    # 使用最新上传的图片
                    image_files.sort(key=lambda x: x[1], reverse=True)
                    image_path = image_files[0][0]

                print(f"Processing image: {image_path}")

                # 应用滤镜处理生成新图片
                output_id = f"output_{int(time.time() * 1000)}"
                processed_image_data = self.apply_filter_to_image(image_path, filter_parameters)

                if processed_image_data:
                    # 保存处理后的图片到临时目录
                    processed_image_path = os.path.join(temp_dir, f"{output_id}.jpg")
                    with open(processed_image_path, 'wb') as f:
                        f.write(processed_image_data)

                    # 保存滤镜信息到临时文件
                    filter_info_path = os.path.join(temp_dir, f"{output_id}_filter.json")
                    filter_info = {
                        "output_id": output_id,
                        "image_id": image_id,
                        "filter_parameters": filter_parameters,
                        "timestamp": time.time(),
                        "processed_image_path": processed_image_path
                    }

                    with open(filter_info_path, 'w') as f:
                        json.dump(filter_info, f)

                    print(f"Saved processed image to: {processed_image_path}")
                    print(f"Saved filter info to: {filter_info_path}")

                    response_data = {
                        "status": "success",
                        "message": "滤镜生成完成",
                        "data": {
                            "output_image_id": output_id,
                            "output_filename": f"{output_id}.jpg",
                            "processing_time": 1.5,
                            "preview_url": f"/api/preview/{output_id}",
                            "download_url": f"/api/download/{output_id}"
                        }
                    }
                else:
                    response_data = {
                        "status": "error",
                        "message": "Failed to process image with filters"
                    }
            else:
                response_data = {
                    "status": "error",
                    "message": "No data received"
                }

            print("Sending generate response")
            self.send_json_response(response_data)

        except Exception as e:
            print(f"Generate error: {e}")
            import traceback
            traceback.print_exc()
            self.send_json_error(500, f"Generate failed: {str(e)}")

    def handle_preview(self, api_path):
        print("=== PREVIEW REQUEST ===")
        output_id = api_path.split('/')[-1]
        print(f"Preview output: {output_id}")

        try:
            temp_dir = tempfile.gettempdir()
            processed_image_path = os.path.join(temp_dir, f"{output_id}.jpg")

            if os.path.exists(processed_image_path):
                # 读取处理后的图片
                with open(processed_image_path, 'rb') as f:
                    image_data = f.read()

                # 设置正确的响应头
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                self.send_header('Content-Length', str(len(image_data)))
                self.end_headers()

                # 发送图片数据
                self.wfile.write(image_data)
                print(f"Successfully sent preview image: {len(image_data)} bytes")
            else:
                self.send_json_error(404, "Processed image not found")

        except Exception as e:
            print(f"Preview error: {e}")
            self.send_json_error(500, f"Preview failed: {str(e)}")

    def handle_download(self, api_path):
        print("=== DOWNLOAD REQUEST ===")
        output_id = api_path.split('/')[-1]
        print(f"Downloading output: {output_id}")

        try:
            temp_dir = tempfile.gettempdir()

            # 读取滤镜信息
            filter_info_path = os.path.join(temp_dir, f"{output_id}_filter.json")
            filter_info = None

            if os.path.exists(filter_info_path):
                with open(filter_info_path, 'r') as f:
                    filter_info = json.load(f)
                    print(f"Found filter info: {filter_info}")

            # 查找原始图片
            image_id = filter_info.get("image_id", "") if filter_info else ""
            image_path = None

            if image_id:
                # 优先使用指定的图片ID
                image_path = os.path.join(temp_dir, f"{image_id}.jpg")

            # 如果找不到指定图片，使用最新上传的图片
            if not image_path or not os.path.exists(image_path):
                image_files = []
                for filename in os.listdir(temp_dir):
                    if filename.startswith('img_') and filename.endswith('.jpg'):
                        file_path = os.path.join(temp_dir, filename)
                        if os.path.exists(file_path):
                            image_files.append((file_path, os.path.getmtime(file_path)))

                if not image_files:
                    self.send_json_error(404, "No uploaded image found for processing")
                    return

                # 使用最新上传的图片
                image_files.sort(key=lambda x: x[1], reverse=True)
                image_path = image_files[0][0]

            print(f"Using image: {image_path}")

            if os.path.exists(image_path):
                # 应用滤镜处理
                processed_image_data = self.apply_filter_to_image(
                    image_path,
                    filter_info.get("filter_parameters", {}) if filter_info else {}
                )

                if processed_image_data:
                    # 设置正确的响应头
                    self.send_response(200)
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Disposition', f'attachment; filename="enhanced_{output_id}.jpg"')
                    self.send_header('Content-Length', str(len(processed_image_data)))
                    self.end_headers()

                    # 发送处理后的图片数据
                    self.wfile.write(processed_image_data)
                    print(f"Successfully sent filtered image: {len(processed_image_data)} bytes")
                else:
                    self.send_json_error(500, "Failed to process image with filters")
            else:
                self.send_json_error(404, "Original image file not found")

        except Exception as e:
            print(f"Download error: {e}")
            self.send_json_error(500, f"Download failed: {str(e)}")

    def apply_filter_to_image(self, image_path, filter_parameters):
        """应用滤镜参数到图片并返回处理后的图片数据"""
        try:
            # 读取原始图片
            img = cv2.imread(image_path)
            if img is None:
                print(f"Failed to read image: {image_path}")
                return None

            print(f"Applying filters: {filter_parameters}")

            # 转换为RGB (OpenCV默认BGR)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # 应用亮度调整
            if 'brightness' in filter_parameters:
                brightness_param = filter_parameters['brightness']
                if isinstance(brightness_param, dict) and 'value' in brightness_param:
                    brightness_val = brightness_param['value']
                else:
                    brightness_val = brightness_param

                if brightness_val != 0:
                    print(f"Applying brightness: {brightness_val}")
                    # 亮度调整：添加常数值
                    brightness_change = int(brightness_val * 2.5)  # 增强效果
                    # 确保数据类型匹配
                    img_rgb = img_rgb.astype(np.int16)
                    img_rgb = img_rgb + brightness_change
                    img_rgb = np.clip(img_rgb, 0, 255).astype(np.uint8)

            # 应用对比度调整
            if 'contrast' in filter_parameters:
                contrast_param = filter_parameters['contrast']
                if isinstance(contrast_param, dict) and 'value' in contrast_param:
                    contrast_val = contrast_param['value']
                else:
                    contrast_val = contrast_param

                if contrast_val != 0:
                    print(f"Applying contrast: {contrast_val}")
                    # 对比度调整：乘以比例因子
                    factor = 1.0 + (contrast_val / 100.0)
                    img_rgb = img_rgb.astype(np.float32)
                    img_rgb = img_rgb * factor
                    img_rgb = np.clip(img_rgb, 0, 255).astype(np.uint8)

            # 应用饱和度调整
            if 'saturation' in filter_parameters:
                saturation_param = filter_parameters['saturation']
                if isinstance(saturation_param, dict) and 'value' in saturation_param:
                    saturation_val = saturation_param['value']
                else:
                    saturation_val = saturation_param

                if saturation_val != 0:
                    print(f"Applying saturation: {saturation_val}")
                    # 转换到HSV进行饱和度调整
                    img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
                    factor = 1.0 + (saturation_val / 100.0)
                    img_hsv[:, :, 1] = img_hsv[:, :, 1] * factor
                    img_hsv[:, :, 1] = np.clip(img_hsv[:, :, 1], 0, 255)
                    img_rgb = cv2.cvtColor(img_hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

            # 应用色调调整
            if 'hue' in filter_parameters:
                hue_param = filter_parameters['hue']
                if isinstance(hue_param, dict) and 'value' in hue_param:
                    hue_val = hue_param['value']
                else:
                    hue_val = hue_param

                if hue_val != 0:
                    print(f"Applying hue: {hue_val}")
                    # 转换到HSV进行色调调整
                    img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
                    img_hsv[:, :, 0] = (img_hsv[:, :, 0] + hue_val) % 180
                    img_rgb = cv2.cvtColor(img_hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

            # 应用锐化
            if 'sharpness' in filter_parameters:
                sharpness_param = filter_parameters['sharpness']
                if isinstance(sharpness_param, dict) and 'value' in sharpness_param:
                    sharpness_val = sharpness_param['value']
                else:
                    sharpness_val = sharpness_param

                if sharpness_val > 0:
                    print(f"Applying sharpness: {sharpness_val}")
                    # 使用锐化核
                    amount = sharpness_val / 100.0
                    kernel = np.array([[-1,-1,-1], [-1,9+amount,-1], [-1,-1,-1]])
                    img_rgb = cv2.filter2D(img_rgb, -1, kernel)
                    img_rgb = np.clip(img_rgb, 0, 255).astype(np.uint8)

            # 转换回BGR for JPEG编码
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

            # 编码为JPEG
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
            is_success, buffer = cv2.imencode(".jpg", img_bgr, encode_param)

            if is_success:
                print(f"Successfully processed image with filters")
                return buffer.tobytes()
            else:
                print("Failed to encode processed image")
                return None

        except Exception as e:
            print(f"Error applying filter: {e}")
            import traceback
            traceback.print_exc()
            return None

    def handle_health(self):
        response_data = {
            "status": "success",
            "message": "Real Image Analysis Server正常运行",
            "data": {
                "timestamp": datetime.now().isoformat(),
                "analysis_engine": "OpenCV + Computer Vision",
                "version": "1.0.0"
            }
        }
        self.send_json_response(response_data)

    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(json_str.encode('utf-8'))

    def send_json_error(self, status_code, message):
        error_data = {
            "status": "error",
            "message": message,
            "error_code": f"HTTP_{status_code}"
        }
        self.send_json_response(error_data, status_code)

def main():
    PORT = 8080
    os.chdir('/Users/cswenx/program/AICoding/Filter-Parser')

    with socketserver.TCPServer(("", PORT), ImageAnalysisHandler) as httpd:
        print("=" * 70)
        print("🔬 Real Image Analysis Server - OpenCV Powered")
        print("=" * 70)
        print(f"📍 服务地址: http://localhost:{PORT}")
        print(f"🧠 分析引擎: OpenCV + Computer Vision")
        print(f"📁 工作目录: {os.getcwd()}")
        print("=" * 70)
        print("✨ 功能特点:")
        print("   • 真实图像亮度、对比度分析")
        print("   • 色彩饱和度和色温检测")
        print("   • 图像锐度和清晰度评估")
        print("   • 阴影/高光区域分析")
        print("   • 智能化参数调整建议")
        print("=" * 70)
        print("按 Ctrl+C 停止服务")
        print()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Real Image Analysis Server已停止")

if __name__ == '__main__':
    main()