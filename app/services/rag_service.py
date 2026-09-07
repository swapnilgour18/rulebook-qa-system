from typing import Dict, Any
from app.services.retrieval import retrieve_relevant_chunks
from app.services.conflict_detector import detect_conflicts
from app.services.answer_generator import generate_answer

def answer_query(query: str) -> Dict[str, Any]:
    """
    Orchestrates the RAG pipeline: Retrieval -> Conflict Detection -> Answer Generation.
    """
    if not query or not query.strip():
        return {
            "status": "NOT_COVERED",
            "answer": "The query is empty. Please ask a valid question.",
            "sources": []
        }
        
    # 1. Retrieve relevant chunks from ChromaDB
    chunks = retrieve_relevant_chunks(query, k=5)
    if not chunks:
        return {
            "status": "NOT_COVERED",
            "answer": "The rulebook does not provide the requested information.",
            "sources": []
        }
        
    # 2. Detect explicit known contradictions
    conflict_result = detect_conflicts(chunks)
    
    if conflict_result.get("has_conflict"):
        # Format the conflict explanation
        conflicts = conflict_result.get("conflicts", [])
        answer_text = "The corpus contains conflicting provisions regarding your query.\n\n"
        
        for i, c in enumerate(conflicts):
            answer_text += f"Conflict {i+1}: {c['topic']}\n"
            answer_text += f"{c['description']}\n\n"
            
            # Format Section A
            sec_a_section = f" — §{c['section_a'].get('section')}" if c['section_a'].get('section') else ""
            score_a = f"\nSimilarity Score: {c['section_a']['similarity_score']:.4f}" if c['section_a'].get('similarity_score') is not None else ""
            answer_text += f"Section A:\n{c['section_a']['document']}{sec_a_section}{score_a}\n\n"
            answer_text += f"Statement:\n{c['section_a']['rule']}\n\n"
            
            # Format Section B
            sec_b_section = f" — §{c['section_b'].get('section')}" if c['section_b'].get('section') else ""
            score_b = f"\nSimilarity Score: {c['section_b']['similarity_score']:.4f}" if c['section_b'].get('similarity_score') is not None else ""
            answer_text += f"Section B:\n{c['section_b']['document']}{sec_b_section}{score_b}\n\n"
            answer_text += f"Statement:\n{c['section_b']['rule']}\n\n"
            
        return {
            "status": "CONFLICT",
            "answer": answer_text.strip(),
            "sources": chunks
        }
        
    # 3. Generate grounded answer if no conflict
    generation_result = generate_answer(query, chunks)
    
    if generation_result.get("status") == "NOT_COVERED":
        return {
            "status": "NOT_COVERED",
            "answer": "The rulebook does not provide the requested information.",
            "sources": []
        }
    elif generation_result.get("status") == "ERROR":
        return {
            "status": "ERROR",
            "answer": generation_result.get("answer", "Unknown error"),
            "sources": []
        }
        
    # 4. Successfully Answered
    return {
        "status": "ANSWERED",
        "answer": generation_result.get("answer", ""),
        "sources": generation_result.get("sources", [])
    }
