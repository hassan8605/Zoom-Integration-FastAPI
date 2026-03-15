from fastapi import FastAPI, status
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from src.settings import settings
from src.logging_config import setup_logging
from src import api_router






app = FastAPI(**settings.fastapi_kwargs)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
       '*'
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
setup_logging()


@app.get("/", response_model=dict, status_code=status.HTTP_200_OK)
async def root() -> dict:
    """
    Root endpoint to check service availability.
    """
    return {"message": f"Welcome to the {settings.PROJECT_NAME}"}


if __name__ == "__main__":
    uvicorn.run(app, host=settings.SERVER_HOST, port=settings.SERVER_PORT)