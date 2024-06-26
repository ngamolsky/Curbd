from pydantic import BaseModel
from typing import List, Optional


class ImageFeature(BaseModel):
    name: str
    confidence: float


class ObjectDetection(BaseModel):
    object_name: str
    confidence: float
    bounding_box: Optional[List[float]] = None


class ImageAnalysisResult(BaseModel):
    image_path: str
    features: List[ImageFeature]
    objects: List[ObjectDetection]
    dominant_colors: List[str]
    image_description: str
    additional_attributes: Optional[dict] = None
    brand: Optional[str] = None
    main_object: Optional[str] = None


class CombinedAnalysisResult(BaseModel):
    individual_results: List[ImageAnalysisResult]
    overall_description: str
    common_themes: List[str]
    suggested_hashtags: List[str]
