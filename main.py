import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from core.config import settings

main_app = FastAPI(default_response_class=ORJSONResponse)
if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
    )
