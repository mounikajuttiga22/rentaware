from fastapi import FastAPI, UploadFile, File
from dotenv import load_dotenv
import shutil
import os

from app.services.extraction import extract_and_detect
from app.services.scheduler_service import update_alerts

# Load environment variables (.env)
load_dotenv()

app = FastAPI(title="RentAware API")

UPLOAD_FOLDER = "uploads"

# Create uploads folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def home():
    return {"message": "Rental Agreement AI Analyzer API Running 🚀"}


@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    try:

        # Save uploaded file
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print("File uploaded:", file.filename)

        # Extract clauses
        result = extract_and_detect(file_path)

        print("Clauses extracted")

        # Update alerts for scheduler
        update_alerts(result.get("alerts", []))

        print("Alerts updated")

        return {
            "message": "File processed successfully",
            "clauses": result.get("clauses", {}),
            "alerts": result.get("alerts", [])
        }

    except Exception as e:
        return {
            "error": str(e)
        }