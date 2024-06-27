from pydantic import BaseModel
from typing import List, Dict


class GeneratedPost(BaseModel):
    title: str
    description: str
    hashtags: List[str]


class PostGenerationResponse(BaseModel):
    post: GeneratedPost
    image_count: int
    post_generation_cost: float
    timing_info: Dict[str, float]
