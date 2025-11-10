# routes/__init__.py
from .upload import upload_bp
from .analysis import analysis_bp
from .filter import filter_bp

__all__ = ['upload_bp', 'analysis_bp', 'filter_bp']