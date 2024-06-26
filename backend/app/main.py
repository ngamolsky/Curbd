from fastapi import FastAPI
from app.api.endpoints import generate_post
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(generate_post.router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
