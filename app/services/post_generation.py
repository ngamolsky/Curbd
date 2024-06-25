import asyncio
import aiofiles
from fastapi import UploadFile
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.models.image_analysis import ImageAnalysisResult
from langchain_core.output_parsers import PydanticOutputParser
from langchain_community.callbacks import get_openai_callback

from app.schemas.post import GeneratedPost
from app.services.image_processing import ImageProcessingModule, OpenAIVisionProcessor
from typing import List, Tuple, Optional
import os


class PostGenerationService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
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

    def generate_post(self, image_analysis_results: List[ImageAnalysisResult], user_input=None) -> Tuple[GeneratedPost, float]:
        # Combine image descriptions from all ImageAnalysisResult objects
        image_descriptions = "\n".join(
            [result.image_description for result in image_analysis_results])

        with get_openai_callback() as cb:
            result = self.post_generation_chain.invoke({
                "image_descriptions": image_descriptions,
                "user_input": user_input
            })

            return self.parser.parse(str(result.content)), cb.total_cost


class CurbdService:
    def __init__(self):
        self.image_processor = ImageProcessingModule(OpenAIVisionProcessor())
        self.post_generator = PostGenerationService()

    async def save_uploaded_images(self, images: List[UploadFile]) -> List[str]:
        image_paths = []
        for image in images:
            temp_path = f"/tmp/{image.filename}"
            async with aiofiles.open(temp_path, "wb") as buffer:
                await buffer.write(await image.read())
            image_paths.append(temp_path)
        return image_paths

    async def process_images_and_generate_post(self, image_paths: List[str], user_input: Optional[str] = None) -> Tuple[GeneratedPost, float]:
        image_analyses = await asyncio.gather(*[self.image_processor.process_image(path) for path in image_paths])
        final_post, total_cost = self.post_generator.generate_post(
            image_analyses, user_input)
        return final_post, total_cost

    async def cleanup_temp_files(self, image_paths: List[str]) -> None:
        for path in image_paths:
            os.remove(path)
