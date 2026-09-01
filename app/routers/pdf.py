from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import shutil

from app.database.dependency import get_db
from app.auth.auth import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.chat_session import ChatSession

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


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/pdf",
    tags=["PDF"]
)


UPLOAD_DIR = "uploads"
VECTOR_DIR = "vector_stores"


os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

os.makedirs(
    VECTOR_DIR,
    exist_ok=True
)


# =========================================================
# UPLOAD PDF
# =========================================================

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    session_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # 1. Check file
    # -----------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )


    # -----------------------------------------------------
    # 2. Check PDF extension
    # -----------------------------------------------------

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )


    # -----------------------------------------------------
    # 3. Check chat session
    # -----------------------------------------------------

    chat_session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        )
        .first()
    )

    if not chat_session:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found"
        )


    # -----------------------------------------------------
    # 4. Create user's upload directory
    # -----------------------------------------------------

    user_upload_dir = os.path.join(
        UPLOAD_DIR,
        str(current_user.id)
    )

    os.makedirs(
        user_upload_dir,
        exist_ok=True
    )


    # -----------------------------------------------------
    # 5. Get safe filename
    # -----------------------------------------------------

    filename = os.path.basename(
        file.filename
    )

    file_path = os.path.join(
        user_upload_dir,
        filename
    )


    # -----------------------------------------------------
    # 6. Read uploaded file
    # -----------------------------------------------------

    try:

        file_content = await file.read()

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=f"Could not read uploaded file: {str(e)}"
        )


    if not file_content:

        raise HTTPException(
            status_code=400,
            detail="Uploaded PDF is empty"
        )


    # -----------------------------------------------------
    # 7. Save PDF
    # -----------------------------------------------------

    try:

        with open(
            file_path,
            "wb"
        ) as buffer:

            buffer.write(
                file_content
            )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not save PDF: {str(e)}"
        )


    # -----------------------------------------------------
    # 8. Extract text
    # -----------------------------------------------------

    try:

        extracted_text = extract_text_from_pdf(
            file_path
        )

    except Exception as e:

        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(
            status_code=500,
            detail=f"PDF text extraction failed: {str(e)}"
        )


    if not extracted_text or not extracted_text.strip():

        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(
            status_code=400,
            detail="Could not extract text from PDF"
        )


    # -----------------------------------------------------
    # 9. Split text into chunks
    # -----------------------------------------------------

    try:

        chunks = split_text_into_chunks(
            extracted_text
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Text chunking failed: {str(e)}"
        )


    if not chunks:

        raise HTTPException(
            status_code=400,
            detail="Could not create text chunks"
        )


    # -----------------------------------------------------
    # 10. Create database document
    # -----------------------------------------------------

    document = Document(
        filename=filename,
        file_path=file_path,
        vector_path="",
        chunks_path="",
        user_id=current_user.id
    )

    db.add(document)

    db.commit()

    db.refresh(document)


    # -----------------------------------------------------
    # 11. Create document vector directory
    # -----------------------------------------------------

    document_dir = os.path.join(
        VECTOR_DIR,
        str(current_user.id),
        str(document.id)
    )

    os.makedirs(
        document_dir,
        exist_ok=True
    )


    vector_path = os.path.join(
        document_dir,
        "faiss_index"
    )


    chunks_path = os.path.join(
        document_dir,
        "chunks.pkl"
    )


    # -----------------------------------------------------
    # 12. Create embeddings
    # -----------------------------------------------------

    try:

        vectors = create_embeddings(
            chunks
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Embedding creation failed: {str(e)}"
        )


    # -----------------------------------------------------
    # 13. Create FAISS vector store
    # -----------------------------------------------------

    try:

        index = create_vector_store(
            vectors
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Vector store creation failed: {str(e)}"
        )


    # -----------------------------------------------------
    # 14. Save FAISS index
    # -----------------------------------------------------

    try:

        save_vector_store(
            index,
            vector_path
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not save vector store: {str(e)}"
        )


    # -----------------------------------------------------
    # 15. Save chunks
    # -----------------------------------------------------

    try:

        save_chunks(
            chunks,
            chunks_path
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not save chunks: {str(e)}"
        )


    # -----------------------------------------------------
    # 16. Update document paths
    # -----------------------------------------------------

    document.vector_path = vector_path

    document.chunks_path = chunks_path

    db.commit()

    db.refresh(document)


    # -----------------------------------------------------
    # 17. ATTACH PDF TO CURRENT CHAT SESSION
    # -----------------------------------------------------

    chat_session.document_id = document.id

    db.commit()

    db.refresh(chat_session)


    # -----------------------------------------------------
    # 18. Return response
    # -----------------------------------------------------

    return JSONResponse(
        status_code=200,
        content={
            "message": "PDF uploaded and attached to chat successfully",
            "document_id": document.id,
            "session_id": session_id,
            "filename": filename,
            "characters": len(extracted_text),
            "chunks": len(chunks),
            "vectors": int(index.ntotal),
            "preview": chunks[0][:500] if chunks else ""
        }
    )


# =========================================================
# GET USER DOCUMENTS
# =========================================================

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
        .order_by(
            Document.id.desc()
        )
        .all()
    )

    return [
        {
            "document_id": document.id,
            "filename": document.filename
        }
        for document in documents
    ]


# =========================================================
# DELETE DOCUMENT
# =========================================================

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


    # -----------------------------------------------------
    # Delete uploaded PDF
    # -----------------------------------------------------

    if (
        document.file_path
        and os.path.exists(document.file_path)
    ):

        os.remove(
            document.file_path
        )


    # -----------------------------------------------------
    # Delete vector store
    # -----------------------------------------------------

    if document.vector_path:

        document_dir = os.path.dirname(
            document.vector_path
        )

        if os.path.exists(document_dir):

            shutil.rmtree(
                document_dir
            )


    # -----------------------------------------------------
    # Remove document from sessions
    # -----------------------------------------------------

    sessions = (
        db.query(ChatSession)
        .filter(
            ChatSession.document_id == document_id,
            ChatSession.user_id == current_user.id
        )
        .all()
    )

    for session in sessions:

        session.document_id = None


    # -----------------------------------------------------
    # Delete database record
    # -----------------------------------------------------

    db.delete(
        document
    )

    db.commit()


    return {
        "message": "Document deleted successfully",
        "document_id": document_id
    }

