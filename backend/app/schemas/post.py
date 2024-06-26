from fastapi import UploadFile
from pydantic import BaseModel
from typing import List, Optional, Dict


class GeneratedPost(BaseModel):
    title: str
    description: str
    hashtags: List[str]


class ImageMetadata(BaseModel):
    filename: str
    size: int
    content_type: str


class PostGenerationRequest(BaseModel):
    user_input: Optional[str] = None
    images: List[UploadFile]


class PostGenerationResponse(BaseModel):
    post: GeneratedPost
    image_count: int
    total_cost: float
    image_processing_cost: float
    post_generation_cost: float
    timing_info: Dict[str, float]
