import uvicorn
from fastapi import FastAPI
from routes import predictions, watermarke #training
from config import settings
from uvicorn.config import LOGGING_CONFIG
# from session import engine, Base
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title=settings.PROJECT_NAME)


app.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
app.include_router(watermarke.router, prefix="/watermarke", tags=["watermarke"])
# app.include_router(training.router, prefix="/training", tags=["auth"])
# app.include_router(users.router, prefix="/users", tags=["users"])



app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)






if __name__ == "__main__":

    # adding datetime in the uvicorn logs of endpoints
    LOGGING_CONFIG["formatters"]["access"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
    LOGGING_CONFIG["formatters"]["access"][
        "fmt"
    ] = "%(levelprefix)s %(asctime)s, %(message)s"

    uvicorn.run(
        "main:app", host="0.0.0.0", port=settings.API_PORT_DOCKER, reload=settings.DEBUG
    )
