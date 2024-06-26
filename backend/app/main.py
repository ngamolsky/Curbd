from fastapi import FastAPI
from app.api.endpoints import generate_post
from app.core.config import get_settings
from fastapi.middleware.cors import CORSMiddleware


settings = get_settings()

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    # Common local development ports
    allow_origins=[settings.FRONTEND_URL or "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(generate_post.router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
