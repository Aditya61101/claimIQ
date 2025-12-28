import os
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, BackgroundTasks
from werkzeug.utils import secure_filename

from sqlalchemy.orm import Session
# core
from app.core.database import get_db
from app.core.security import require_roles, assert_claim_access
# Schemas
from app.schemas.documents import DocumentResponse
from app.schemas.api_response import APIResponse
# Models
from app.models.claims import Claim
from app.models.documents import Document
# services
from app.services.document_extraction import extract_document
from app.services.claim_status import update_claim_processing_status

UPLOAD_DIR = os.getenv("UPLOAD_DIR") # UPLOAD_DIR="uploads" in .env
CLAIMS_UPLOAD_DIR = f"{UPLOAD_DIR}/claims"

router = APIRouter(prefix='/claims', tags=['Documents'])

@router.post("/{claim_id}/documents", response_model=APIResponse[list[DocumentResponse]])
async def upload_files(
    claim_id: int, 
    background_tasks: BackgroundTasks,
    current_user = Depends(require_roles("POLICY_HOLDER", "HOSPITAL")),
    document_type: str=Form(...), 
    files: list[UploadFile]=File(...),
    db: Session=Depends(get_db)
):

    claim = db.query(Claim).filter(Claim.id==claim_id).first()

    if not claim:
        raise HTTPException(status_code=404, detail='Claim not found')
    
    if not document_type or document_type not in ['bills', 'prescriptions', 'reports']:
        raise HTTPException(status_code=400, detail='Document type not provided or not supported.')
    
    if not files:
        raise HTTPException(status_code=400, detail='No files provided.')
    
    # for authorization purpose, raises exception if claim is not owned by current user
    assert_claim_access(claim, current_user)

    claim_dir = os.path.join(CLAIMS_UPLOAD_DIR, str(claim_id), document_type)
    os.makedirs(claim_dir, exist_ok=True)

    saved_files = []
    error_files = []
    for file in files:
        if not file.filename:
            continue
        filename = secure_filename(file.filename)
        file_path = os.path.join(claim_dir, filename)
        try:
            with open(file_path, 'wb') as f:
                while chunk:= await file.read(1024*1024):
                    f.write(chunk)    
        except Exception as e:
            error_files.append({
                'file_name': filename,
                'error': str(e)
            })
            continue
            # raise HTTPException(status_code=500, detail='Failed to upload file')
        document = Document(
            file_name=filename,
            original_file_name=file.filename,
            file_path=file_path,
            content_type=file.content_type,
            document_type=document_type,
            claim_id=claim_id
        )
        saved_files.append(document)
    
    if not saved_files:
        raise HTTPException(status_code=400, detail='No valid files were uploaded.')

    db.add_all(saved_files)
    db.commit()

    update_claim_processing_status(claim_id, db)

    for doc in saved_files:
        db.refresh(doc)

        background_tasks.add_task(
            extract_document,
            doc.id
        )

    return APIResponse(
        status=True,
        message='Files uploaded successfully',
        data=saved_files
    )

@router.get("/{claim_id}/documents", response_model=APIResponse[list[DocumentResponse]])
def get_documents_for_claim_id(
    claim_id:int,
    current_user = Depends(require_roles("POLICY_HOLDER", "HOSPITAL")), 
    db:Session=Depends(get_db)
):

    claim = db.query(Claim).filter(Claim.id==claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail='Claim not found')

    # for authorization purpose, raises exception if claim is not owned by current user
    assert_claim_access(claim, current_user)

    doc_list = db.query(Document).filter(Document.claim_id==claim_id).order_by(Document.uploaded_at.asc()).all()

    if not doc_list:
        raise HTTPException(204, detail='No documents found')
    
    return APIResponse(
        status=True,
        message=f'Documents fetched for claim id: {claim_id}',
        data=doc_list
    )