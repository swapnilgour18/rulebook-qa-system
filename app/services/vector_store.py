import os
from langchain_chroma import Chroma
from app.services.embeddings import get_embeddings

CHROMA_PERSIST_DIR = os.path.join("data", "chroma")
COLLECTION_NAME = "rulebook_collection"

def get_vector_store():
    """
    Initializes and returns the Chroma vector store.
    Reopens it if it already exists, or creates it if it doesn't.
    """
    embeddings = get_embeddings()
    
    # In langchain-chroma, specifying persist_directory automatically persists data to disk.
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )
    
    return vector_store

import hashlib

def add_documents_to_store(chunks):
    """
    Adds chunks to the persistent ChromaDB vector store using deterministic IDs
    to avoid duplication on multiple runs.
    """
    vector_store = get_vector_store()
    
    ids = []
    for chunk in chunks:
        # Create a deterministic ID using MD5 hash of source and content
        source = chunk.metadata.get("source", "unknown")
        content_hash = hashlib.md5(chunk.page_content.encode("utf-8")).hexdigest()
        ids.append(f"{source}_{content_hash}")
        
    vector_store.add_documents(chunks, ids=ids)
    return vector_store
