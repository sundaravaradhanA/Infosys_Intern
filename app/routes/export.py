from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
import csv
import io

from app.database import get_db
from app.models import Transaction

router = APIRouter(prefix="/export", tags=["Export"])

print("🔥 EXPORT FILE LOADED 🔥")


@router.get("/transactions")
def export_transactions(db: Session = Depends(get_db)):

    transactions = db.query(Transaction).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["ID", "Amount", "Category", "Date"])

    for t in transactions:
        writer.writerow([
            t.id,
            float(t.amount),
            t.category,
            t.created_at
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"}
    )