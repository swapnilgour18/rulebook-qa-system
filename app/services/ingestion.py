import os
import glob
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, CSVLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_core.documents import Document

def ingest_corpus(data_dir: str):
    """
    Loads Markdown, CSV, and PDF files from data_dir.
    Chunks them into LangChain Document objects and preserves metadata.
    """
    all_chunks = []
    
    # Text splitter config
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    
    # Headers to split on for Markdown
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

    files = glob.glob(os.path.join(data_dir, "*"))
    
    for file_path in files:
        filename = os.path.basename(file_path)
        
        # Skip conflicts.json
        if filename == "conflicts.json":
            continue
            
        file_type = Path(filename).suffix.lower()
        
        if file_type == ".md":
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Split by markdown headers
            md_docs = markdown_splitter.split_text(content)
            
            # Add metadata and further split if necessary
            for doc in md_docs:
                doc.metadata["source"] = filename
                doc.metadata["file_type"] = "markdown"
                
            chunks = text_splitter.split_documents(md_docs)
            all_chunks.extend(chunks)
            
        elif file_type == ".pdf":
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = filename
                doc.metadata["file_type"] = "pdf"
                # PyPDFLoader adds 'page' metadata automatically
            chunks = text_splitter.split_documents(docs)
            all_chunks.extend(chunks)
            
        elif file_type == ".csv":
            loader = CSVLoader(file_path)
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = filename
                doc.metadata["file_type"] = "csv"
                # CSVLoader adds 'row' metadata automatically
            
            # CSV rows are usually small, but run them through the splitter just in case
            chunks = text_splitter.split_documents(docs)
            all_chunks.extend(chunks)

    return all_chunks
