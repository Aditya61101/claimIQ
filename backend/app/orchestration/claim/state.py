from typing import TypedDict, Optional, List, Dict, Any

class AgentIssue(TypedDict):
    code:str
    message:str
    severity:str
    evidence: Optional[Dict[str, any]]

class ClaimGraphState(TypedDict):
    claim_id:int

    # core inputs
    claim_data: Dict[str,Any]
    documents: List[Dict[str, any]]
    insured_person: Dict[str, any]
    policy_data: Dict[str, any]

    # agent outputs
    consistency_issues: Optional[List[AgentIssue]]
    policy_issues: Optional[List[AgentIssue]]
    fraud_signals: Optional[List[AgentIssue]]

    # deep extraction
    enriched_claim_facts: Optional[Dict[str, any]]

    # final decision
    recommendation: Optional[str]
    reasoning: Optional[str]
    confidence: Optional[float]
