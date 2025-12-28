from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_roles
# Schemas
from app.schemas.api_response import APIResponse
from app.schemas.policies import GetPoliciesResponse
from app.schemas.insured_persons import InsuredPersonResponse
# Models
from app.models.users import User
from app.models.policies import Policy
from app.models.insured_persons import InsuredPerson
# helpers
from app.utils.constants import UserRoles

router = APIRouter(prefix='/policies', tags=['Policies'])

@router.get('/', response_model = APIResponse[GetPoliciesResponse])
def get_policies_for_user(
    db:Session = Depends(get_db),
    current_user:User = Depends(require_roles("POLICY_HOLDER", "INSURER", "HOSPITAL"))
):
    role = current_user.role
    
    if role in {UserRoles.POLICY_HOLDER, UserRoles.HOSPITAL}:
        policies = db.query(Policy).filter(Policy.owner_user_id==current_user.id).all()
    elif role == UserRoles.INSURER:
        policies = db.query(Policy).all()
    
    return APIResponse(
        status=True,
        message='Policies retrieved successfully',
        data=policies
    )

@router.get("/{policy_id}/insured-persons", response_model=APIResponse[InsuredPersonResponse])
def get_insured_persons(
    policy_id:int,
    db:Session = Depends(get_db),
    _:User = Depends(require_roles("POLICY_HOLDER", "INSURER", "HOSPITAL"))
):
    policy = db.query(Policy).filter(Policy.id==policy_id).first()

    if not policy:
        raise HTTPException(404, detail='Policy not found')

    insured_people = db.query(InsuredPerson).filter(InsuredPerson.policy_id==policy_id).all()

    return APIResponse(
        status=True,
        message='Insured person list',
        data=insured_people
    )