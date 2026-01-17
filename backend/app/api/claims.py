from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_roles, assert_claim_access
# Schemas
from app.schemas.claims import ClaimCreate, ClaimResponse, ClaimWithDocumentsResponse
from app.schemas.api_response import APIResponse
# Models
from app.models.users import User
from app.models.claims import Claim
from app.models.documents import Document
from app.models.policies import Policy
from app.models.insured_persons import InsuredPerson
# helpers
from app.utils.constants import UserRoles

from app.orchestration.document.document_executor import invoke_document_graph

router = APIRouter(prefix='/claims', tags=['Claims'])

@router.post('/', response_model = APIResponse[ClaimResponse])
def create_claim(
    payload:ClaimCreate, 
    db:Session = Depends(get_db),
    current_user:User = Depends(require_roles("POLICY_HOLDER", "HOSPITAL"))
):

    # validating policy
    policy = (
        db.query(Policy).filter(
            Policy.id==payload.policy_id,
        ).first()
    )
    if not policy:
        raise HTTPException(404, detail="Policy doesn't exists")

    if current_user.role == UserRoles.POLICY_HOLDER:
        if policy.owner_user_id != current_user.id:
            raise HTTPException(403, detail="You are not authorized to create claim for this policy")

    insured_person = (
        db.query(InsuredPerson)
        .filter(
            InsuredPerson.id == payload.insured_person_id,
            InsuredPerson.policy_id==policy.id
        ).first()
    )

    if not insured_person:
        raise HTTPException(400, detail='No insured person found for the given policy')
        # insured_person = InsuredPerson(
        #     user_id=current_user.id,
        #     full_name=payload.insured_person.full_name,
        #     date_of_birth=payload.insured_person.date_of_birth,
        #     gender=payload.insured_person.gender
        # )
        # db.add(insured_person)
        # db.commit()
        # db.refresh(insured_person)
    
    new_claim = Claim(
        policy_id=payload.policy_id,
        insured_person_id=insured_person.id,
        created_by_id=current_user.id,
        claim_type=payload.claim_type,
        claim_amount=payload.claim_amount,
        diagnosis=payload.diagnosis,
        treatment_date=payload.treatment_date if payload.claim_type=='domiciliary' else None,
        admission_date=payload.admission_date if payload.claim_type=='hospitalization' else None,
        discharge_date=payload.discharge_date if payload.claim_type=='hospitalization' else None,
        hospital_id=payload.hospital_id if payload.claim_type=='hospitalization' else None
    )

    db.add(new_claim) # Stage object for insert
    db.commit() # actually writes to the DB
    db.refresh(new_claim) # pull DB generated values

    return APIResponse(
        status=True,
        message='Claim created successfully',
        data=new_claim
    )

@router.get('/{id}', response_model=APIResponse[ClaimWithDocumentsResponse])
def get_claim_by_id(
    id:int, 
    db:Session = Depends(get_db),
    current_user:User = Depends(require_roles("POLICY_HOLDER", "INSURER", "HOSPITAL"))
):
    claim = db.query(Claim).filter(Claim.id==id).first()

    if not claim:
        raise HTTPException(status_code=404, detail='No claim exists for the given claim id')
    
    # for authorization purpose, raises exception if claim is not owned by current user
    assert_claim_access(claim, current_user)

    documents = db.query(Document).filter(Document.claim_id==id).all()

    response = ClaimWithDocumentsResponse(
        id=claim.id,
        claim_type=claim.claim_type,
        policy_id=claim.policy_id,
        claim_amount=claim.claim_amount,
        processing_status=claim.processing_status,
        decision_status=claim.decision_status,
        created_at=claim.created_at,
        documents=documents
    )
    
    return APIResponse(
        status=True,
        message=f'Claim fetched for {id}',
        data=response
    )

@router.get('/', response_model=APIResponse[list[ClaimResponse]])
def get_claims(
    db:Session = Depends(get_db),
    current_user:User = Depends(require_roles("POLICY_HOLDER", "INSURER", "HOSPITAL"))
):
    role = current_user.role
    
    if role == UserRoles.INSURER:
        claims = db.query(Claim).all()
    else:
        claims = db.query(Claim).filter(Claim.created_by_id==current_user.id).all()

    return APIResponse(
        status=True,
        message='Claims fetched successfully',
        data=claims
    )

# TODO: make it idempotent
@router.post("/{claim_id}/process")
def claim_processing(
    claim_id:int, 
    background_tasks: BackgroundTasks,
    db:Session = Depends(get_db),
    current_user:User = Depends(require_roles("POLICY_HOLDER", "HOSPITAL"))
):

    claim = db.query(Claim).get(claim_id)
    if not claim:
        raise HTTPException(404, "Claim not found")
    
    # for authorization purpose, raises exception if claim is not owned by current user
    assert_claim_access(claim, current_user)
    
    if claim.processing_status not in {"DRAFT", "ACTION_REQUIRED"}:
        raise HTTPException(400, detail=f'Claim cannot be processed in state: {claim.processing_status}')
    
    # fetching documents for the given claim id
    document_ids = db.query(Document.id).filter(Document.claim_id==claim_id, Document.status.in_(['UPLOADED', 'EXTRACTED'])).all()

    if not document_ids:
        raise HTTPException(400, "No documents uploaded")
    
    claim.processing_status = 'DOCUMENT_PROCESSING'
    db.commit()

    # parallel document graph execution for each document available
    # TODO: replace this with a task queue
    for (document_id, ) in document_ids:
        background_tasks.add_task(
            invoke_document_graph,
            document_id,
            claim_id
        )

    return APIResponse(
        status=True,
        message='Claim sent for processing',
    )