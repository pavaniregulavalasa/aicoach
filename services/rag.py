# Install dependencies
# pip install -qU langchain-community faiss-cpu langchain-openai unstructured[pdf]

import os
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
#from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from tqdm import tqdm
from langchain_community.document_loaders import PyMuPDFLoader  # ✅ No pdfminer!
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
# Configuration
ROOT_DIR = "./knowledge/"  # Your directory
EMBEDDINGS = HuggingFaceBgeEmbeddings(
            model_name="BAAI/bge-base-en-v1.5",
            model_kwargs={"device": "cpu", "trust_remote_code": True},
            encode_kwargs={"normalize_embeddings": True},#True enabling Semantic search
    )

def create_faiss_per_folder(root_dir: str):
    """Create FAISS per folder using PyMuPDF (fixes pdfminer error)"""
    
    root_path = Path(root_dir)
    subfolders = [f for f in root_path.iterdir() if f.is_dir()]
    
    print(f"📁 Found {len(subfolders)} subfolders: {[f.name for f in subfolders]}")
    
    for folder in tqdm(subfolders, desc="Creating FAISS indexes"):
        folder_name = folder.name
        print(f"\n🔄 Processing: {folder_name}")
        
        # ✅ PyMuPDFLoader - No pdfminer dependency, handles scanned PDFs
        loader = DirectoryLoader(
            str(folder),
            glob="**/*.pdf",           # Recursive PDFs
            loader_cls=PyMuPDFLoader,  # Fast & reliable
            show_progress=True,
            silent_errors=False        # Show errors for debugging
        )
        
        try:
            docs = loader.load()
            if not docs:
                print(f"⚠️ No PDFs found in {folder_name}")
                continue
                
            print(f"📄 Loaded {len(docs)} PDFs")
            
            # Add metadata
            for doc in docs:
                doc.metadata.update({
                    "functionality": folder_name,
                    "folder_path": str(folder),
                    "page": doc.metadata.get("page", "unknown")
                })
            
            # Split & index
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1500, chunk_overlap=200
            )
            splits = text_splitter.split_documents(docs)
            
            vectorstore = FAISS.from_documents(splits, EMBEDDINGS)
            
            # Save - match the path expected by ai_coach.py
            index_dir = f"services/faiss_indexes/{folder_name}"
            os.makedirs(index_dir, exist_ok=True)
            vectorstore.save_local(index_dir)
            print(f"✅ {folder_name}: {len(splits)} chunks → {index_dir}/")
            
        except Exception as e:
            print(f"❌ Error in {folder_name}: {e}")
            continue
    
    print("\n🎉 All FAISS indexes created!")

# Run
create_faiss_per_folder(ROOT_DIR)
