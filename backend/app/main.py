from fastapi import FastAPI, UploadFile, File
import shutil
import os

from app.services.extraction import extract_and_detect
from app.services.scheduler_service import update_alerts

app = FastAPI()

# Folder to store uploaded agreements
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def home():
    return {"message": "Rental Agreement AI Analyzer API Running"}


@app.post("/upload/")
async def upload(file: UploadFile = File(...)):

    # Save uploaded file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run extraction and risk detection
    result = extract_and_detect(file_path)

    # Send alerts to scheduler (this triggers SMS later)
    update_alerts(result["alerts"])

    return {
        "message": "File processed successfully",
        "clauses": result["clauses"],
        "alerts": result["alerts"]
    }