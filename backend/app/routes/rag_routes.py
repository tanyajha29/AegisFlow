from fastapi import APIRouter, Depends

from ..middleware.auth_middleware import get_current_user
from ..rag.orchestrator import explain_finding
from ..rag.schemas import ExplainRequest, ExplainResponse

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/explain", response_model=ExplainResponse)
def rag_explain(payload: ExplainRequest, current_user=Depends(get_current_user)):
    return explain_finding(payload)
