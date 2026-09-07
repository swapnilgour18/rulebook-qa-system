from typing import List, Dict, Any
from app.services.vector_store import get_vector_store

def retrieve_relevant_chunks(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieves the most relevant chunks for a given query using semantic similarity search.
    
    Args:
        query: The search query string.
        k: The number of chunks to retrieve.
        
    Returns:
        A list of dictionaries containing the content, source, score, and all existing metadata.
    """
    if not query or not query.strip():
        return []
        
    vector_store = get_vector_store()
    relevance_fn = vector_store._select_relevance_score_fn()
    
    # Use similarity_search_with_score to get distance scores
    results = vector_store.similarity_search_with_score(query, k=k)
    
    formatted_results = []
    for doc, distance in results:
        # Calculate user-facing similarity score
        try:
            similarity_score = relevance_fn(distance)
        except Exception:
            similarity_score = 0.0
            
        meta = doc.metadata
        
        # Derive section/reference based on source type
        source = meta.get("source", "Unknown")
        section = None
        
        if source.endswith(".md"):
            # Markdown: try to build a hierarchical section name from headers
            headers = []
            for i in range(1, 7):
                header_val = meta.get(f"Header {i}")
                if header_val:
                    headers.append(header_val)
            if headers:
                section = " > ".join(headers)
        elif source.endswith(".pdf"):
            # PDF: check if 'section' exists, otherwise None
            section = meta.get("section")
        
        # Extract row/page
        page = meta.get("page")
        row = meta.get("row")
            
        result_dict = {
            "content": doc.page_content,
            "score": distance,  # raw distance (legacy, keep for backward compatibility)
            "distance_score": distance,
            "similarity_score": similarity_score,
            "source": source,
            "section": section,
            "page": page,
            "row": row,
            "metadata": meta
        }
        formatted_results.append(result_dict)
        
    return formatted_results
