"""
图像分析参数数据模型
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class ParameterValue:
    """单个参数值"""
    name: str
    direction: str  # 增加/降低/偏暖/偏冷等
    value: float    # 调整幅度
    unit: str       # 单位 %/K/°等
    reference: str  # 参考标准

@dataclass
class AnalysisResult:
    """分析结果数据模型"""
    image_id: str
    parameters: Dict[str, ParameterValue]
    analysis_time: float  # 分析耗时(秒)
    timestamp: datetime
    confidence_score: float  # 分析置信度

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'image_id': self.image_id,
            'parameters': {
                name: {
                    'name': param.name,
                    'direction': param.direction,
                    'value': param.value,
                    'unit': param.unit,
                    'reference': param.reference
                } for name, param in self.parameters.items()
            },
            'analysis_time': self.analysis_time,
            'timestamp': self.timestamp.isoformat(),
            'confidence_score': self.confidence_score
        }

@dataclass
class FilterParameter:
    """滤镜参数模型"""
    brightness: float = 0.0      # 亮度 -100 ~ 100
    contrast: float = 0.0        # 对比度 -100 ~ 100
    saturation: float = 0.0      # 饱和度 -100 ~ 100
    sharpness: float = 0.0       # 锐化 -100 ~ 100
    temperature: float = 0.0     # 色温 -500 ~ 500K
    hue: float = 0.0            # 色调 -180 ~ 180°
    shadow: float = 0.0         # 阴影 -100 ~ 100
    highlight: float = 0.0      # 高光 -100 ~ 100

    def to_dict(self) -> Dict[str, float]:
        """转换为字典"""
        return {
            'brightness': self.brightness,
            'contrast': self.contrast,
            'saturation': self.saturation,
            'sharpness': self.sharpness,
            'temperature': self.temperature,
            'hue': self.hue,
            'shadow': self.shadow,
            'highlight': self.highlight
        }

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'FilterParameter':
        """从字典创建实例"""
        return cls(**data)