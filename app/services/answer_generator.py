import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

class AnswerResponse(BaseModel):
    status: str = Field(description="Return 'ANSWERED' ONLY if the exact information is explicitly in the text without concept substitution. Return 'NOT_COVERED' otherwise.")
    answer: str = Field(description="The concise answer to the question based ONLY on explicit context. Empty string if NOT_COVERED.")
    passages_used: List[int] = Field(description="List of PASSAGE numbers (1-indexed) used. Empty list if NOT_COVERED.")

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

CRITICAL INSTRUCTION: ONLY answer a question when the retrieved rulebook context explicitly contains enough information to answer exactly what was asked.

CRITICAL DECISION RULE:
Before returning ANSWERED, ask:
"Does the provided context explicitly state the exact information requested by the user, without any derivation, inference, or concept substitution?"
If the answer is not a direct "yes", you MUST return NOT_COVERED.

RULES:
1. Do not invent facts or use outside knowledge.
2. Use only the supplied context.
3. If the context does not answer the question explicitly, return status="NOT_COVERED" and an empty answer.
4. Do not substitute a related concept for the requested concept. If the specific concept requested is not explicitly discussed in the text, return NOT_COVERED.


EXAMPLES:

Question: "What is the minimum attendance requirement?"
Context: "All students must maintain a minimum attendance of 75%..."
Output: {{"status": "ANSWERED", "answer": "The minimum attendance requirement is 75%.", "passages_used": [1]}}

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
