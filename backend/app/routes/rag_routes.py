from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..middleware.auth_middleware import get_current_user
from ..rag.rag_orchestrator import run_explain, run_fix
from ..rag.retriever_service import search_chunks
from ..rag.schemas import ExplainRequest, ExplainResponse, FixResponse, SearchRequest, SearchResponse

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/search", response_model=SearchResponse)
def rag_search(payload: SearchRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    results = search_chunks(
        db,
        query=payload.query,
        vulnerability_type=payload.vulnerability_type,
        language=payload.language,
        framework=payload.framework,
        top_k=payload.top_k,
    )
    return SearchResponse(results=results)


@router.post("/explain", response_model=ExplainResponse)
def rag_explain(payload: ExplainRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return run_explain(db, payload)


@router.post("/fix", response_model=FixResponse)
def rag_fix(payload: ExplainRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return run_fix(db, payload)
