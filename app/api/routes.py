from fastapi import APIRouter
from app.models.schemas import AskRequest, AskResponse
from app.services.rag_service import answer_query

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    """
    Submits a question to the Rulebook QA System.
    Returns the generated answer, conflict status, and supporting sources.
    """
    result = answer_query(request.question)
    
    return AskResponse(
        status=result["status"],
        answer=result["answer"],
        sources=result.get("sources", [])
    )
