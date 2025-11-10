"""
API响应数据模型
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional, List
from enum import Enum

class ResponseStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

@dataclass
class APIResponse:
    """统一API响应格式"""
    status: ResponseStatus
    message: str
    data: Optional[Any] = None
    error_code: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'status': self.status.value,
            'message': self.message
        }
        if self.data is not None:
            result['data'] = self.data
        if self.error_code:
            result['error_code'] = self.error_code
        return result

@dataclass
class UploadResponse:
    """文件上传响应"""
    image_id: str
    filename: str
    file_size: int
    dimensions: tuple
    message: str = "上传成功"

@dataclass
class AnalysisResponse:
    """参数分析响应"""
    image_id: str
    parameters: Dict[str, Any]
    analysis_time: float
    confidence_score: float
    suggestions: List[str]
    message: str = "分析完成"

@dataclass
class GenerationResponse:
    """滤镜生成响应"""
    output_image_id: str
    output_filename: str
    processing_time: float
    original_image_id: str
    applied_parameters: Dict[str, Any]
    message: str = "滤镜生成完成"