from pydantic import BaseModel, Field
from typing import List, Optional


class UserInput(BaseModel):
    prompt_modification: Optional[str] = Field(
        None, description="Modifications to the prompt")


class GeneratedPost(BaseModel):
    title: str
    description: str
    hashtags: List[str]


class ImageMetadata(BaseModel):
    filename: str
    size: int
    content_type: str


class PostGenerationRequest(BaseModel):
    user_input: Optional[UserInput] = None
    images: List[ImageMetadata]


class PostGenerationResponse(BaseModel):
    post: GeneratedPost
    processing_time: float
    image_count: int
    total_tokens: int
