from app.core.database import SessionLocal
from app.models.claims import Claim
from app.models.documents import Document
from app.models.insured_persons import InsuredPerson
from app.models.policies import Policy
from .claim_graph import claim_graph
from .state import ClaimGraphState

def invoke_claim_graph(claim_id:int):
    """
        Entry point to evaluate a claim using agentic graph.
    """
    db = SessionLocal()
    try:
        claim:Claim|None = db.query(Claim).filter(Claim.id==claim_id).first()
        if not claim:
            return
        
        documents:list[Document]|None = db.query(Document).filter(Document.claim_id==claim_id, Document.status=='VERIFIED').all()

        insured_person:InsuredPerson|None = db.query(InsuredPerson).filter(InsuredPerson.id==claim.insured_person_id).first()
        if not insured_person:
            return

        policy:Policy|None = db.query(Policy).filter(Policy.id==claim.policy_id).first()
        if not policy:
            return

        state:ClaimGraphState = {
            "claim_id":claim.id,
            "claim_data": {
                "claim_type": claim.claim_type,
                "diagnosis": claim.diagnosis,
                "claim_amount": claim.claim_amount,
                "treatment_date": claim.treatment_date,
                "admission_date": claim.admission_date,
                "discharge_date": claim.discharge_date,
                "hospital_id": claim.hospital_id
            },
            "documents": [
                {
                    "id": d.id,
                    "document_type": d.document_type,
                    "extracted_data": d.extracted_data
                } for d in documents
            ],
            "insured_person": {
                "id": insured_person.id,
                "full_name": insured_person.full_name,
                "date_of_birth": insured_person.date_of_birth,
                "gender": insured_person.gender,
            },
            "policy_data": {
                "id": policy.id,
                "policy_number": policy.policy_number,
                "total_sum_insured": policy.total_sum_insured,
                "approved_claim_amount": policy.approved_claim_amount,
                "policy_start_date": policy.policy_start_date,
                "policy_end_date": policy.policy_end_date,
            },
            "consistency_issues":None,
            "confidence":None,
            "enriched_claim_facts":None,
            "fraud_signals":None,
            "policy_issues":None,
            "reasoning":None,
            "recommendation":None
        }

        result = claim_graph.invoke(state)
    except Exception as e:
        pass
    finally:
        db.close()
