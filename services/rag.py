# pdf_indexer_fixed.py - RUN THIS INSTEAD
# pip install -qU langchain-community faiss-cpu "unstructured[pdf-image]" pillow pymupdf sentence-transformers scikit-learn

import os
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader, UnstructuredPDFLoader
from tqdm import tqdm
import json
import fitz  # PyMuPDF for image extraction

# ✅ Configuration
ROOT_DIR = "./knowledge/"
EMBEDDINGS = HuggingFaceBgeEmbeddings(
    model_name="BAAI/bge-base-en-v1.5",
    model_kwargs={"device": "cpu", "trust_remote_code": True},
    encode_kwargs={"normalize_embeddings": True},
)

def extract_images_pymupdf(pdf_path: str, output_dir: str):
    """✅ Extract images using PyMuPDF (works when Unstructured fails)"""
    try:
        doc = fitz.open(pdf_path)
        image_paths = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                if pix.n - pix.alpha < 4:  # Skip transparency
                    img_path = f"{output_dir}/{Path(pdf_path).stem}_page_{page_num+1}_{img_index}.png"
                    pix.save(img_path)
                    image_paths.append(img_path)
                pix = None
        doc.close()
        return image_paths
    except:
        return []

def create_robust_faiss_index(root_dir: str):
    """✅ PyMuPDF + image extraction - NO pdfminer dependency"""
    
    root_path = Path(root_dir)
    subfolders = [f for f in root_path.iterdir() if f.is_dir()]
    
    print(f"📁 Found {len(subfolders)} subfolders")
    
    for folder_idx, folder in enumerate(tqdm(subfolders, desc="Processing subfolders")):
        folder_name = folder.name.replace(" ", "_")  # ✅ Fix spaces
        print(f"\n🔄 [{folder_idx+1}/{len(subfolders)}] Processing: {folder_name}")
        
        # ✅ Create output directories
        index_dir = f"faiss_indexes/{folder_name}"
        img_dir = f"extracted_images/{folder_name}"
        os.makedirs(index_dir, exist_ok=True)
        os.makedirs(img_dir, exist_ok=True)
        
        # ✅ STEP 1: Try Unstructured first (best for complex PDFs)
        pdf_files = list(folder.glob("**/*.pdf"))
        docs = []
        
        for pdf_file in pdf_files:
            try:
                # ✅ Unstructured with minimal deps
                loader = UnstructuredPDFLoader(
                    str(pdf_file),
                    mode="elements",
                    strategy="fast",  # ✅ Avoid pdfminer-heavy hi_res
                    infer_table_structure=True,
                )
                pdf_docs = loader.load()
                if pdf_docs:
                    docs.extend(pdf_docs)
                    print(f"✅ Unstructured: {pdf_file.name}")
                else:
                    raise Exception("No docs")
            except Exception as e:
                print(f"⚠️  Unstructured failed {pdf_file.name}: {e}")
                # ✅ Fallback: PyMuPDF (text + metadata)
                loader = PyMuPDFLoader(str(pdf_file))
                pdf_docs = loader.load()
                # ✅ Add image metadata manually
                for doc in pdf_docs:
                    doc.metadata['element_type'] = 'Text'
                    doc.metadata['has_images'] = True  # Flag potential images
                docs.extend(pdf_docs)
                # ✅ Extract images separately
                img_paths = extract_images_pymupdf(str(pdf_file), img_dir)
                print(f"✅ PyMuPDF + Images: {pdf_file.name} ({len(img_paths)} images)")
        
        if not docs:
            print(f"⚠️ No valid PDFs in {folder_name}")
            continue
            
        print(f"📄 Loaded {len(docs)} elements from {len(pdf_files)} PDFs")
        
        # ✅ Add functionality metadata
        for doc in docs:
            doc.metadata['functionality'] = folder_name
            if doc.metadata.get('category') in ['Image', 'Figure']:
                doc.metadata['element_type'] = 'Image'
            elif doc.metadata.get('category') == 'Table':
                doc.metadata['element_type'] = 'Table'
            else:
                doc.metadata['element_type'] = 'Text'
        
        # ✅ Count element types
        image_docs = [d for d in docs if d.metadata.get('element_type') == 'Image']
        table_docs = [d for d in docs if d.metadata.get('element_type') == 'Table']
        print(f"🖼️  {len(image_docs)} images | 📊 {len(table_docs)} tables | 📄 {len(pdf_files)} PDFs")
        
        # ✅ Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""],
            keep_separator=True
        )
        splits = text_splitter.split_documents(docs)
        
        # ✅ Count chunks by type
        image_chunks = sum(1 for s in splits if s.metadata.get('element_type') == 'Image')
        table_chunks = sum(1 for s in splits if s.metadata.get('element_type') == 'Table')
        print(f"📦 {len(splits)} chunks ({image_chunks} images, {table_chunks} tables)")
        
        # ✅ Create FAISS index
        vectorstore = FAISS.from_documents(splits, EMBEDDINGS)
        vectorstore.save_local(index_dir)
        
        # ✅ Save index info
        index_info = {
            "functionality": folder_name,
            "total_documents": len(pdf_files),
            "total_elements": len(docs),
            "total_chunks": len(splits),
            "image_chunks": image_chunks,
            "table_chunks": table_chunks,
            "extracted_images_path": img_dir,
            "pdf_files": [f.name for f in pdf_files],
            "index_date": "2024-12-20",
            "loader": "PyMuPDF+Unstructured(fast)"
        }
        
        json_path = f"{index_dir}/index_info.json"
        with open(json_path, "w") as f:
            json.dump(index_info, f, indent=2)
        
        print(f"✅ {folder_name}: {len(splits)} chunks → {index_dir}/")
        print(f"🖼️  Images: {img_dir}/")
    
    print("\n🎉 ✅ ROBUST INDEXES CREATED - pdfminer-proof!")

if __name__ == "__main__":
    os.makedirs("faiss_indexes", exist_ok=True)
    os.makedirs("extracted_images", exist_ok=True)
    create_robust_faiss_index(ROOT_DIR)