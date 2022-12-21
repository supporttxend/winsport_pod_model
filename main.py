from re import T
from fastapi import FastAPI
import uvicorn
import api_pod
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/data", StaticFiles(directory="data"), name="data")

app.include_router(
    api_pod.router, prefix="", tags=["model_prediction"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run("main:app", port=7000, host="0.0.0.0", reload=True)
