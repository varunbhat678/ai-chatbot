from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import os

from app.database.dependency import get_db
from app.auth.auth import get_current_user
from app.models.user import User
from app.models.document import Document

from app.services.pdf_service import (
    extract_text_from_pdf,
    split_text_into_chunks
)

from app.services.embedding_service import create_embeddings

from app.services.vector_store import (
    create_vector_store,
    save_vector_store,
    save_chunks
)


router = APIRouter(
    prefix="/pdf",
    tags=["PDF"]
)

UPLOAD_DIR = "uploads"
VECTOR_DIR = "vector_stores"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTOR_DIR, exist_ok=True)


@router.post("/upload")
def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # 1. Check file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # 2. Save uploaded PDF
    user_upload_dir = os.path.join(
        UPLOAD_DIR,
        str(current_user.id)
    )

    os.makedirs(user_upload_dir, exist_ok=True)

    file_path = os.path.join(
        user_upload_dir,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    # 3. Extract text
    extracted_text = extract_text_from_pdf(file_path)

    if not extracted_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from PDF"
        )

    # 4. Split text into chunks
    chunks = split_text_into_chunks(extracted_text)

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="Could not create text chunks"
        )

    # 5. Create document record
    document = Document(
        filename=file.filename,
        file_path=file_path,
        vector_path="",
        chunks_path="",
        user_id=current_user.id
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # 6. Create document-specific folder
    document_dir = os.path.join(
        VECTOR_DIR,
        str(current_user.id),
        str(document.id)
    )

    os.makedirs(document_dir, exist_ok=True)

    vector_path = os.path.join(
        document_dir,
        "faiss_index"
    )

    chunks_path = os.path.join(
        document_dir,
        "chunks.pkl"
    )

    # 7. Convert chunks into embeddings
    vectors = create_embeddings(chunks)

    # 8. Create FAISS vector store
    index = create_vector_store(vectors)

    # 9. Save FAISS index
    save_vector_store(
        index,
        vector_path
    )

    # 10. Save original chunks
    save_chunks(
        chunks,
        chunks_path
    )

    # 11. Update document paths
    document.vector_path = vector_path
    document.chunks_path = chunks_path

    db.commit()
    db.refresh(document)

    return {
        "message": "PDF uploaded and vectorized successfully",
        "document_id": document.id,
        "filename": file.filename,
        "characters": len(extracted_text),
        "chunks": len(chunks),
        "vectors": index.ntotal,
        "preview": chunks[0][:500] if chunks else ""
    }

@router.get("/")
def get_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    documents = (
        db.query(Document)
        .filter(
            Document.user_id == current_user.id
        )
        .order_by(Document.id.desc())
        .all()
    )

    return [
        {
            "document_id": document.id,
            "filename": document.filename
        }
        for document in documents
    ]

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # Delete uploaded PDF
    if document.file_path and os.path.exists(document.file_path):
        os.remove(document.file_path)

    # Delete vector store folder
    if document.vector_path:
        document_dir = os.path.dirname(document.vector_path)

        if os.path.exists(document_dir):
            import shutil
            shutil.rmtree(document_dir)

    # Delete database record
    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully",
        "document_id": document_id
    }