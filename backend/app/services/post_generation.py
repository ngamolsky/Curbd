import asyncio
import aiofiles
import logging
from fastapi import UploadFile
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.models.image_analysis import ImageAnalysisResult
from langchain_core.output_parsers import PydanticOutputParser
from langchain_community.callbacks import get_openai_callback

from app.schemas.post import GeneratedPost
from app.services.image_processing import ImageProcessingModule, OpenAIVisionProcessor
from typing import List, Tuple, Optional, Dict
import os
from PIL import Image
from io import BytesIO
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostGenerationService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo",
                              temperature=0.7, verbose=True)
        self.parser = PydanticOutputParser(pydantic_object=GeneratedPost)

        self.post_prompt = PromptTemplate.from_template(
            "Analyze the following image descriptions and optional user input:\n"
            "Image descriptions: {image_descriptions}\n"
            "User input: {user_input}\n\n"
            "Based on this information, generate a post for giving away the item(s) for free. Follow these steps:\n"
            "1. Create an engaging and concise title that will grab attention and clearly convey what's being offered.\n"
            "2. Write a compelling description that provides more information about the item(s), their condition, and any relevant details. Keep it friendly and appealing to potential takers.\n"
            "3. Generate 3-5 hashtags that will help the post reach interested people. Include general and specific tags related to the item(s) and free giveaways.\n"
            "4. If user input is provided, incorporate it appropriately into the generated content, ensuring it enhances the title, description, or hashtags as needed.\n\n"
            "Format the output according to these instructions: {format_instructions}\n",
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            }
        )

        self.post_generation_chain = self.post_prompt | self.llm

    async def generate_post(self, image_analysis_results: List[ImageAnalysisResult], user_input=None) -> Tuple[GeneratedPost, float]:
        # Combine image descriptions from all ImageAnalysisResult objects
        image_descriptions = "\n".join(
            [result.image_description for result in image_analysis_results])

        logger.info(
            f"Generating post with image descriptions: {image_descriptions}")
        logger.info(f"User input: {user_input}")

        with get_openai_callback() as cb:
            result = await self.post_generation_chain.ainvoke({
                "image_descriptions": image_descriptions,
                "user_input": user_input
            })

            logger.info(f"Generated post content: {result.content}")
            logger.info(f"Post generation cost: {cb.total_cost}")

            return self.parser.parse(str(result.content)), cb.total_cost


class CurbdService:
    def __init__(self):
        self.image_processor = ImageProcessingModule(OpenAIVisionProcessor())
        self.post_generator = PostGenerationService()

    async def save_uploaded_images(self, images: List[UploadFile]) -> List[str]:
        image_paths = []
        for image in images:
            content = await image.read()
            img = Image.open(BytesIO(content))

            logger.info(f"Processing image: {image.filename}")
            logger.info(f"Initial image format: {image.content_type}")
            # Check and convert file type if necessary
            if image.content_type not in ["image/png", "image/webp"]:
                img = img.convert("RGB")
                output_format = "PNG"
            else:
                output_format = image.content_type.split("/")[1].upper()

            # Compress if larger than 20MB
            output = BytesIO()
            img.save(output, format=output_format, optimize=True, quality=85)
            compressed_content = output.getvalue()

            # Log the initial file size
            initial_size = len(compressed_content)
            logger.info(
                f"Initial file size: {initial_size / (1024 * 1024):.2f} MB")
            logger.info(f"Initial image size: {img.size}")

            while len(compressed_content) > 4 * 1024 * 1024:  # 20MB in bytes
                output = BytesIO()
                img = img.resize((int(img.width * 0.9), int(img.height * 0.9)))
                img.save(output, format=output_format,
                         optimize=True, quality=85)
                compressed_content = output.getvalue()

            logger.info(f"Final image size: {img.size}")
            logger.info(
                f"Final file size: {len(compressed_content) / (1024 * 1024):.2f} MB")

            # Save the image
            temp_path = f"/tmp/{image.filename}"
            async with aiofiles.open(temp_path, "wb") as buffer:
                await buffer.write(compressed_content)
            image_paths.append(temp_path)
        return image_paths

    async def process_images_and_generate_post(self, image_paths: List[str], user_input: Optional[str] = None) -> Tuple[GeneratedPost, float, float, Dict[str, float]]:

        timing_info = {}

        start_time = time.time()
        image_analyses = await asyncio.gather(*[self.image_processor.process_image(path) for path in image_paths])
        image_processing_time = time.time() - start_time
        timing_info['image_processing'] = image_processing_time

        image_processing_cost = sum([cost for _, cost in image_analyses])
        image_analyses = [result for result, _ in image_analyses]

        logger.info(
            f"Image processing completed in {image_processing_time:.2f} seconds")
        logger.info(f"Image processing cost: {image_processing_cost}")
        for i, analysis in enumerate(image_analyses):
            logger.info(f"Image {i+1} analysis result: {analysis}")

        start_time = time.time()
        final_post, post_generation_cost = await self.post_generator.generate_post(
            image_analyses, user_input)
        post_generation_time = time.time() - start_time
        timing_info['post_generation'] = post_generation_time

        timing_info['total'] = image_processing_time + post_generation_time

        logger.info(
            f"Post generation completed in {post_generation_time:.2f} seconds")
        logger.info(f"Post generation cost: {post_generation_cost}")
        logger.info(f"Generated post: {final_post}")

        return final_post, image_processing_cost, post_generation_cost, timing_info

    async def cleanup_temp_files(self, image_paths: List[str]) -> None:
        for path in image_paths:
            os.remove(path)
            logger.info(f"Removed temporary file: {path}")
