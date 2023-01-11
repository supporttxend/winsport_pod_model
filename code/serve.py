from fastapi import FastAPI, Response, Request
import uvicorn
from joblib import dump, load
from helper_funcitons.custom_functions import load_model, get_path
from pathlib import Path

try:
    BASE_DIR = Path(__file__).resolve().parent
    print("Try BASE", BASE_DIR)

except Exception as e:

    BASE_DIR = Path(".").parent.absolute()
    print("Except BASE", BASE_DIR)

app = FastAPI()





@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/invocations")
def predict():

    return Response(
        response="Yes this is model response",
        status=200
    )







if __name__ == "__main__":
    uvicorn.run("serve:app", host="0.0.0.0", port=81122, reload=True)