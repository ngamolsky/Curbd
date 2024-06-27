from fastapi import APIRouter, UploadFile, File, Depends, Form
from typing import List
from app.schemas.post import PostGenerationResponse
from app.services.post_generation import PostGenerationService
from app.core.security import get_api_key
from typing import Annotated
import time
from langsmith import traceable

router = APIRouter()
post_generation_service = PostGenerationService()


@traceable
@router.post("/generate-post/", response_model=PostGenerationResponse, operation_id="GeneratePost")
async def generate_post(
    images: Annotated[List[UploadFile], File()],
    user_input: Annotated[str | None, Form()] = None,
    _: str = Depends(get_api_key)
):
    timing_info = {}
    start_time = time.time()
    image_paths = await post_generation_service.save_uploaded_images(images)
    image_uploading_time = time.time() - start_time
    timing_info['image_uploading'] = image_uploading_time

    start_time = time.time()
    final_post, post_generation_cost = await post_generation_service.generate_post(
        image_paths, user_input)
    post_generation_time = time.time() - start_time
    timing_info['post_generation'] = post_generation_time

    await post_generation_service.cleanup_temp_files(image_paths)

    return PostGenerationResponse(
        post=final_post,
        image_count=len(images),
        post_generation_cost=post_generation_cost,
        timing_info=timing_info
    )
