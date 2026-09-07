import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

class AnswerResponse(BaseModel):
    status: str = Field(description="Must be 'ANSWERED' if the context provides the answer, or 'NOT_COVERED' if the context does not contain enough information.")
    answer: str = Field(description="The concise answer to the question based ONLY on the provided context. Empty string if NOT_COVERED.")
    passages_used: List[int] = Field(description="List of PASSAGE numbers (1-indexed) that were actually used to formulate the answer. Empty list if NOT_COVERED.")

def get_llm():
    """Initializes and returns the Gemini text-generation model."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
    load_dotenv(dotenv_path=env_path)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not found.")
        
    return ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature=0,
        google_api_key=api_key
    )

def generate_answer(query: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generates an answer to the query based strictly on the retrieved chunks.
    
    Args:
        query: The user's question.
        retrieved_chunks: A list of dictionaries representing the retrieved context.
        
    Returns:
        A dictionary containing the status, answer, and the specific sources used.
    """
    if not retrieved_chunks:
        return {
            "status": "NOT_COVERED",
            "answer": "",
            "sources": []
        }
        
    llm = get_llm()
    structured_llm = llm.with_structured_output(AnswerResponse)
    
    context_text = ""
    for i, chunk in enumerate(retrieved_chunks):
        context_text += f"\n--- PASSAGE {i+1} ---\n"
        context_text += f"Source: {chunk.get('source', 'Unknown')}\n"
        context_text += f"Content: {chunk.get('content', '')}\n"
        
    prompt = f"""
You are a strict, precise answering assistant for a university rulebook.
You must answer the user's question based ONLY on the provided passages.

RULES:
1. Do not invent facts.
2. Do not use outside knowledge.
3. Do not make assumptions.
4. Use only the supplied context.
5. If the context does not answer the question, return status="NOT_COVERED" and an empty answer.
6. If multiple passages contain relevant information, consider all of them. Provide the answer based on the evidence.

QUESTION: {query}

CONTEXT PASSAGES:
{context_text}
"""
    
    try:
        response: AnswerResponse = structured_llm.invoke(prompt)
    except Exception as e:
        return {
            "status": "ERROR",
            "answer": f"An error occurred during generation: {str(e)}",
            "sources": []
        }
    
    # Map the passages_used indices back to the actual chunks
    sources_used = []
    if response.status == "ANSWERED":
        for p_num in response.passages_used:
            idx = p_num - 1
            if 0 <= idx < len(retrieved_chunks):
                sources_used.append(retrieved_chunks[idx])
    
    return {
        "status": response.status,
        "answer": response.answer,
        "sources": sources_used
    }
