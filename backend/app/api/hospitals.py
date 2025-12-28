from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_roles
# Schemas
from app.schemas.api_response import APIResponse
from app.schemas.hospitals import GetHospitalResponse
# Models
from app.models.hospitals import Hospital

router = APIRouter(prefix='/hospitals', tags=['Hospitals'])

@router.get('/', response_model = APIResponse[GetHospitalResponse])
def get_non_blacklisted_hospitals(
    db:Session = Depends(get_db),
    _ = Depends(require_roles("POLICY_HOLDER", "INSURER", "HOSPITAL"))
):

    hospitals = db.query(Hospital).filter(Hospital.is_blacklisted==False).all()
    
    return APIResponse(
        status=True,
        message='Hospitals retrieved successfully',
        data=hospitals
    )