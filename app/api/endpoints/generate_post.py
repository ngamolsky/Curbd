from fastapi import APIRouter, UploadFile, File, Depends, Form
from typing import List
from app.schemas.post import PostGenerationResponse
from app.services.post_generation import CurbdService
from app.core.security import get_api_key
import time
from typing import Optional

router = APIRouter()
curbd_service = CurbdService()


@router.post("/generate-post/", response_model=PostGenerationResponse)
async def generate_post(
    images: List[UploadFile] = File(...),
    user_input: Optional[str] = Form(None),
    _: str = Depends(get_api_key)
):

    image_paths = await curbd_service.save_uploaded_images(images)

    start_time = time.time()
    generated_post, total_tokens = await curbd_service.process_images_and_generate_post(image_paths, user_input if user_input else None)
    processing_time = time.time() - start_time

    await curbd_service.cleanup_temp_files(image_paths)

    return PostGenerationResponse(
        post=generated_post,
        processing_time=processing_time,
        image_count=len(images),
        total_tokens=total_tokens
    )
