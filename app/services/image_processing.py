from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage
from app.models.image_analysis import ImageAnalysisResult
import base64
from PIL import Image
from io import BytesIO
import aiofiles


class OpenAIVisionProcessor:
    def __init__(self):
        self.chat_model = ChatOpenAI(
            model="gpt-4o",
            max_tokens=1000
        )
        self.parser = PydanticOutputParser(pydantic_object=ImageAnalysisResult)

    async def encode_image(self, image_path):
        async with aiofiles.open(image_path, mode='rb') as image_file:
            image_data = await image_file.read()
            image = Image.open(BytesIO(image_data))
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')

    async def process_image(self, image_path: str) -> ImageAnalysisResult:
        base64_image = await self.encode_image(image_path)

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
        ai_message = await self.chat_model.ainvoke([human_message])
        return self.parser.parse(str(ai_message.content))


class ImageProcessingModule:
    def __init__(self, vision_processor):
        self.vision_processor = vision_processor

    async def process_image(self, image_path: str) -> ImageAnalysisResult:
        return await self.vision_processor.process_image(image_path)
