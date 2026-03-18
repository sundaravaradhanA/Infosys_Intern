from fastapi import APIRouter, UploadFile, File, Form
import os
from datetime import datetime

router = APIRouter()

UPLOAD_FOLDER = "kyc_uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@router.post("/kyc/upload")
async def upload_kyc(
    user_id: int = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...)
):

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return {
        "message": "KYC document uploaded successfully",
        "file_name": file.filename,
        "document_type": document_type,
        "uploaded_at": datetime.now()
    }