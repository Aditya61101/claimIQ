from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.core.database import get_db
# Schemas
from app.schemas.claims import ClaimCreate, ClaimResponse, ClaimWithDocumentsResponse
from app.schemas.api_response import APIResponse
# Models
from app.models.claims import Claim
from app.models.documents import Document

router = APIRouter(prefix='/claims', tags=['Claims'])

@router.post('/', response_model = APIResponse[ClaimResponse])
def create_claim(claim:ClaimCreate, db:Session = Depends(get_db)):
    print("entered post claims")
    new_claim = Claim(
        policy_id=claim.policy_id,
        claim_type=claim.claim_type,
        amount=claim.amount
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
def get_claim_by_id(id:int, db:Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id==id).first()

    if not claim:
        raise HTTPException(status_code=404, detail='No claim exists for the given claim id')

    documents = db.query(Document).filter(Document.claim_id==id).all()

    response = ClaimWithDocumentsResponse(
        id=claim.id,
        claim_type=claim.claim_type,
        policy_id=claim.policy_id,
        amount=claim.amount,
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
def get_claims(db:Session = Depends(get_db)):
    print("entered post claims")
    claims = db.query(Claim).all()

    return APIResponse(
        status=True,
        message='Claims fetched successfully',
        data=claims
    )