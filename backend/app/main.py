from fastapi import FastAPI, UploadFile, File
import shutil
import os

from app.services.extraction import extract_and_detect
from app.services.scheduler_service import update_alerts

app = FastAPI()

UPLOAD_FOLDER = "uploads"

# create uploads folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def home():
    return {"message": "Rental Agreement AI Analyzer API Running"}


@app.post("/upload/")
async def upload(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    # save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # extract clauses and alerts
    result = extract_and_detect(file_path)

    # send alerts to scheduler
    update_alerts(result["alerts"])

    return {
        "message": "File processed successfully",
        "clauses": result["clauses"],
        "alerts": result["alerts"]
    }