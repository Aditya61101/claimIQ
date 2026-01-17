import os
import logging
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
    document_type: str = Form(...), 
    replaces_document_id: int|None = Form(None),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
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
    
    old_doc = None
    if replaces_document_id:
        if len(files)!=1:
            raise HTTPException(status_code=400, detail="Exactly one file must be uploaded when replacing a document")
        
        old_doc = db.query(Document).filter(Document.id==replaces_document_id, Document.claim_id==claim_id, Document.is_active==True).first()

        if not old_doc:
            raise HTTPException(status_code=400, detail="Invalid document to replace")

    claim_dir = os.path.join(CLAIMS_UPLOAD_DIR, str(claim_id), document_type)
    os.makedirs(claim_dir, exist_ok=True)

    new_documents = []
    error_files = []
    try:
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
                claim_id=claim_id,
                is_active=True
            )
            new_documents.append(document)
        
        if not new_documents:
            raise HTTPException(status_code=400, detail='No valid files were uploaded.')

        db.add_all(new_documents)
        db.flush()

        if old_doc:
            old_doc.is_active = False
            old_doc.status = 'REPLACED'
            old_doc.replaced_by_doc_id = new_documents[0].id
            
            claim.processing_status = 'DRAFT'
            claim.action_required = None
            claim.decision_status = 'PENDING'
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(500, detail='Internal Server Error')

    update_claim_processing_status(claim_id, db)

    # TODO: replace this with a task queue
    for doc in new_documents:
        background_tasks.add_task(
            extract_document,
            doc.id
        )

    return APIResponse(
        status=True,
        message='Files uploaded successfully',
        data=new_documents
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