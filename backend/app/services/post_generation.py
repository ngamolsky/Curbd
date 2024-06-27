import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_community.callbacks import get_openai_callback

from app.schemas.post import GeneratedPost
from typing import List, Tuple
from fastapi import UploadFile
import time
import uuid
import os
import aiofiles
from app.core.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


class PostGenerationService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o",
                              temperature=0.7, verbose=True)
        self.parser = PydanticOutputParser(pydantic_object=GeneratedPost)

        self.post_prompt = PromptTemplate.from_template(
            "Analyze the following image(s) and optional user input:\n"
            "Image(s): {images}\n"
            "User input: {user_input}\n\n"
            "Based on this information, generate a post for giving away the item(s) for free. Your response should be a GeneratedPost object with the following attributes:\n"
            "1. title: An engaging and concise title that grabs attention and clearly conveys what's being offered.\n"
            "2. description: A compelling description that provides more information about the item(s), their condition, and any relevant details. Keep it friendly and appealing to potential takers.\n"
            "3. hashtags: A list of 3-5 hashtags that will help the post reach interested people. Include general and specific tags related to the item(s) and free giveaways.\n"
            "If user input is provided, incorporate it appropriately into the generated content, ensuring it enhances the title, description, or hashtags as needed.\n\n"
            "Format the output according to these instructions: {format_instructions}\n",
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            }
        )

        self.post_generation_chain = self.post_prompt | self.llm

    async def generate_post(self, image_paths: List[str], user_input=None) -> Tuple[GeneratedPost, float]:

        logger.info(
            f"Generating post for images: {image_paths}")
        logger.info(f"User input: {user_input}")

        with get_openai_callback() as cb:
            result = await self.post_generation_chain.ainvoke({
                "images": image_paths,
                "user_input": user_input
            })

            logger.info(f"Generated post content: {result.content}")
            logger.info(f"Post generation cost: {cb.total_cost}")

            return self.parser.parse(str(result.content)), cb.total_cost

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
