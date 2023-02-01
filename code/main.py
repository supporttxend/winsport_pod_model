from re import T

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import api_pod

app = FastAPI()
app.mount("/data", StaticFiles(directory="data"), name="data")

app.include_router(api_pod.router, prefix="", tags=["model_prediction"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run("main:app", port=7000, host="0.0.0.0", reload=True)
