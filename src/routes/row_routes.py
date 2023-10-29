from fastapi import HTTPException, APIRouter
from uuid import UUID as PyUUID
from src.database.database_manager import SessionLocal
from src.database.schemas.row_schema import Row, RowSchema, RowCreateUpdate, RowList

router = APIRouter()


@router.get("/rows", response_model=list[Row])
def list_rows(request_data: RowList):
    cabinet_ids = request_data.cabinet_ids

    db = SessionLocal()
    if cabinet_ids:
        rows = db.query(RowSchema).filter(RowSchema.cabinet_id.in_(cabinet_ids)).all()
    else:
        rows = db.query(RowSchema).all()
    db.close()
    return rows


@router.get("/rows/{row_id}", response_model=Row)
def get_row(row_id: PyUUID):
    db = SessionLocal()
    row = db.query(RowSchema).filter(RowSchema.id == row_id).first()
    db.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Row not found")
    return row


@router.post("/rows", response_model=Row)
def create_row(row: RowCreateUpdate):
    db = SessionLocal()
    try:
        db_row = RowSchema(**row.model_dump())
        db.add(db_row)
        db.commit()
        db.refresh(db_row)
        return db_row
    finally:
        db.close()


@router.put("/rows/{row_id}", response_model=Row)
def update_row(row_id: PyUUID, updated_row: RowCreateUpdate):
    db = SessionLocal()
    try:
        existing_row = db.query(RowSchema).filter(RowSchema.id == row_id).first()
        if existing_row is None:
            raise HTTPException(status_code=404, detail="Row not found")

        for attr, value in updated_row.model_dump().items():
            setattr(existing_row, attr, value)

        db.commit()
        db.refresh(existing_row)
        return existing_row
    finally:
        db.close()


@router.delete("/rows/{row_id}", response_model=Row)
def delete_row(row_id: PyUUID):
    db = SessionLocal()
    row = db.query(RowSchema).filter(RowSchema.id == row_id).first()
    if row is None:
        db.close()
        raise HTTPException(status_code=404, detail="Row not found")
    db.delete(row)
    db.commit()
    db.close()
    return row
