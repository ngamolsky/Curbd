from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage
from app.models.image_analysis import ImageAnalysisResult
import base64
from PIL import Image
from io import BytesIO
import aiofiles
from typing import Tuple, Optional, List, Dict
from langchain_community.callbacks import get_openai_callback
from fastapi import UploadFile
import logging
import time
import os
import asyncio
import uuid
from app.core.config import get_settings

settings = get_settings()

logger = logging.getLogger(__name__)


class OpenAIVisionProcessor:
    def __init__(self):
        self.chat_model = ChatOpenAI(
            model="gpt-4o",
            max_tokens=1000,
            verbose=True
        )
        self.parser = PydanticOutputParser(pydantic_object=ImageAnalysisResult)

    async def encode_image(self, image_path):

        async with aiofiles.open(image_path, mode='rb') as image_file:
            image_data = await image_file.read()
            # Log image size
            logger.info(
                f"Image size: {len(image_data) / (1024 * 1024):.2f} MB")
            image = Image.open(BytesIO(image_data))
            buffered = BytesIO()
            image.save(buffered, format="PNG")

            encoding_start = time.time()
            encoded_image = base64.b64encode(
                buffered.getvalue()).decode('utf-8')
            encoding_duration = time.time() - encoding_start
            logger.info(
                f"Base64 encoding completed in {encoding_duration:.2f} seconds")

        return encoded_image

    async def process_image(self, image_path: str) -> Tuple[ImageAnalysisResult, float]:
        start_time = time.time()

        logger.info(f"Starting image processing for {image_path}")

        encoding_start = time.time()
        base64_image = await self.encode_image(image_path)
        encoding_time = time.time() - encoding_start
        logger.info(
            f"Image encoding completed in {encoding_time:.2f} seconds")

        human_message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": f"Analyze this image in detail. {self.parser.get_format_instructions()}"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                }
            ]
        )

        analysis_start = time.time()
        with get_openai_callback() as callback:
            ai_message = await self.chat_model.ainvoke([human_message])
            result = self.parser.parse(str(ai_message.content))

        analysis_time = time.time() - analysis_start

        total_time = time.time() - start_time
        logger.info(f"Image analysis completed in {analysis_time:.2f} seconds")
        logger.info(f"Total image processing time: {total_time:.2f} seconds")
        logger.info(f"Image processing cost: {callback.total_cost}")
        logger.info(f"Image procesing result: {result}")

        return result, callback.total_cost


class ImageProcessingService:
    def __init__(self, vision_processor):
        self.vision_processor = vision_processor

    async def process_image(self, image_path: str) -> Tuple[ImageAnalysisResult, float]:
        res = await self.vision_processor.process_image(image_path)
        return res

    async def save_uploaded_images(self, images: List[UploadFile]) -> List[str]:
        logger.info(f"Starting to save {len(images)} uploaded images")
        start_time = time.time()
        image_paths = []

        for index, image in enumerate(images):
            # Generate a unique filename for each image
            filename = f"{uuid.uuid4()}.png"
            file_path = os.path.join(settings.TEMP_FILE_DIR, filename)

            # Ensure the temporary directory exists
            os.makedirs(settings.TEMP_FILE_DIR, exist_ok=True)

            # Save the image to the temporary directory
            async with aiofiles.open(file_path, 'wb') as out_file:
                content = await image.read()
                await out_file.write(content)

            image_paths.append(file_path)
            logger.info(
                f"Saved image {index + 1}/{len(images)} to {file_path}")

        end_time = time.time()
        duration = end_time - start_time
        logger.info(
            f"Finished saving {len(images)} images in {duration:.2f} seconds")

        return image_paths

    async def cleanup_temp_files(self, image_paths: List[str]) -> None:
        for path in image_paths:
            os.remove(path)
            logger.info(f"Removed temporary file: {path}")
