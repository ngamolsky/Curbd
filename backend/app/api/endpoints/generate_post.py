from fastapi import APIRouter, UploadFile, File, Depends, Form
from typing import List
from app.schemas.post import PostGenerationResponse
from app.services.post_generation import PostGenerationService
from app.services.image_processing import ImageProcessingService, OpenAIVisionProcessor
from app.core.security import get_api_key
from typing import Annotated
import time
import asyncio

router = APIRouter()
post_generation_service = PostGenerationService()
image_processing_service = ImageProcessingService(OpenAIVisionProcessor())


@router.post("/generate-post/", response_model=PostGenerationResponse, operation_id="GeneratePost")
async def generate_post(
    images: Annotated[List[UploadFile], File()],
    user_input: Annotated[str | None, Form()] = None,
    _: str = Depends(get_api_key)
):
    timing_info = {}
    start_time = time.time()
    image_paths = await image_processing_service.save_uploaded_images(images)
    image_uploading_time = time.time() - start_time
    timing_info['image_uploading'] = image_uploading_time

    start_time = time.time()
    image_analyses_with_cost = await asyncio.gather(*[image_processing_service.process_image(path) for path in image_paths])
    image_analyses = [analysis[0] for analysis in image_analyses_with_cost]
    image_processing_cost = sum([analysis[1]
                                for analysis in image_analyses_with_cost])
    image_processing_time = time.time() - start_time
    timing_info['image_processing'] = image_processing_time

    start_time = time.time()
    final_post, post_generation_cost = await post_generation_service.generate_post(
        image_analyses, user_input)
    post_generation_time = time.time() - start_time
    timing_info['post_generation'] = post_generation_time

    await image_processing_service.cleanup_temp_files(image_paths)

    return PostGenerationResponse(
        post=final_post,
        image_count=len(images),
        image_processing_cost=image_processing_cost,
        post_generation_cost=post_generation_cost,
        total_cost=image_processing_cost + post_generation_cost,
        timing_info=timing_info
    )
