import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_community.callbacks import get_openai_callback
from langchain_core.messages import HumanMessage
from app.schemas.post import GeneratedPost
from typing import List, Tuple
from fastapi import UploadFile
import time
import uuid
import os
import aiofiles
from app.core.config import get_settings
from langsmith import traceable
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


class PostGenerationService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o",
                              temperature=0.7, verbose=True)
        self.parser = PydanticOutputParser(pydantic_object=GeneratedPost)

    async def generate_post(self, image_paths: List[str], user_input=None) -> Tuple[GeneratedPost, float]:

        logger.info(
            f"Generating post for images: {image_paths}")
        logger.info(f"User input: {user_input}")

        # Convert image paths to base64 encoded strings
        base64_images = []
        for image_path in image_paths:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(
                    image_file.read()).decode('utf-8')
                base64_images.append(f"data:image/png;base64,{encoded_string}")

        # Replace image_paths with base64_images in the chain invocation

        with get_openai_callback() as cb:

            image_dicts = [{"type": "image_url", "image_url": {
                "url": base64_image}} for base64_image in base64_images]

            human_message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text":  "Carefully analyze the following image(s) and optional user input:\n"
                        "User input: {user_input}\n\n"
                        "Based on this information, accurately identify the item(s) present in the image(s) and generate a post for giving them away for free. Your response should be a GeneratedPost object with the following attributes:\n"
                        "1. title: An engaging and concise title that grabs attention and clearly conveys what's being offered, based on your accurate analysis of the image(s).\n"
                        "2. description: A compelling description that provides detailed information about the item(s) you've identified, including their appearance, condition, and any relevant details visible in the image(s). Keep it friendly and appealing to potential takers.\n"
                        "3. hashtags: A list of 3-5 hashtags that will help the post reach interested people. Include general and specific tags related to the item(s) you've identified and free giveaways.\n"
                        "If user input is provided, incorporate it appropriately into the generated content, ensuring it enhances the title, description, or hashtags as needed, while still maintaining accuracy based on what you see in the image(s).\n\n"
                        "Ensure that your analysis of the image(s) is thorough and that you only include items that are clearly visible and intended for giveaway. Do not make assumptions about items that aren't clearly present in the image(s).\n\n"
                        f"Format the output according to these instructions: {self.parser.get_format_instructions()}\n",
                    },
                    *image_dicts
                ]
            )

            template = ChatPromptTemplate.from_messages([human_message])

            chain = template | self.llm | self.parser

            result = await chain.ainvoke(
                input={
                    "user_input": user_input,
                    "images": base64_images
                }
            )

            logger.info(f"Generated post content: {result}")
            logger.info(f"Post generation cost: {cb.total_cost}")

            return result, cb.total_cost

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
