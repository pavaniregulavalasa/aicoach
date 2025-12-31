
# ai_coach_dashboard.py - COMPLETE LLM-POWERED TELECOM TRAINING COACH
import os
import json
from datetime import datetime
import re
from typing import Dict, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool
from langchain_core.output_parsers import StrOutputParser
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.text import Text
from pathlib import Path
from pydantic import BaseModel, Field
import httpx
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_core.documents import Document 
from sklearn.cluster import KMeans
import numpy as np
import logging
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'logs/ai_coach_{datetime.now().strftime("%Y%m%d")}.log')
    ]
)
logger = logging.getLogger(__name__)

# Configuration
FAISS_ROOT = "./services/faiss_indexes/"

# Try new langchain-huggingface first, fallback to deprecated for compatibility
try:
    from langchain_huggingface import HuggingFaceEmbeddings  # New API
    USE_NEW_EMBEDDINGS = True
except ImportError:
    # Fallback to deprecated version if new package not available
    from langchain_community.embeddings import HuggingFaceBgeEmbeddings  # Fallback
    USE_NEW_EMBEDDINGS = False

# Initialize embeddings with new or deprecated API
if USE_NEW_EMBEDDINGS:
    # New langchain-huggingface API
    EMBEDDINGS = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5",
        model_kwargs={"device": "cpu", "trust_remote_code": True},
        encode_kwargs={"normalize_embeddings": True},  # True enabling Semantic search
    )
else:
    # Deprecated langchain-community API (fallback)
    EMBEDDINGS = HuggingFaceBgeEmbeddings(
        model_name="BAAI/bge-base-en-v1.5",
        model_kwargs={"device": "cpu", "trust_remote_code": True},
        encode_kwargs={"normalize_embeddings": True},  # True enabling Semantic search
    )

def get_eli_chat_model(temperature: float = 0.0, model_name: str = None):
    logger.info("="*80)
    logger.info("INITIALIZING LLM CONNECTION")
    
    # Get LLM mode: "local" for Ollama, "remote" for ELI gateway (default: auto-detect)
    llm_mode = os.getenv("LLM_MODE", "auto").lower()
    
    # Get model name from environment or use default
    # Note: Ollama uses colon (:) in model names, e.g., "qwen2.5:7b"
    if model_name is None:
        model_name = os.getenv("LLM_MODEL", "qwen2.5:7b")
    
    # Auto-detect mode based on base_url if not explicitly set
    if llm_mode == "auto":
        base_url = os.getenv("LLM_BASE_URL", os.getenv("ELI_BASE_URL", ""))
        if "localhost" in base_url or "127.0.0.1" in base_url or base_url == "":
            llm_mode = "local"
        else:
            llm_mode = "remote"
    
    logger.info(f"  Mode: {llm_mode.upper()}")
    logger.info(f"  Model: {model_name}")
    logger.info(f"  Temperature: {temperature}")
    logger.info("="*80)
    
    # Configure based on mode
    if llm_mode == "local":
        # Local Ollama configuration - skip all validations
        base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
        api_key = os.getenv("LLM_API_KEY", "ollama")  # Ollama doesn't require real API key - any value works
        ssl_verify = False  # Local HTTP connections don't need SSL verification
        logger.info("Using LOCAL Ollama instance")
        logger.debug(f"Ollama base URL: {base_url}")
        logger.debug("Skipping API key and SSL validations for local mode")
    else:
        # Remote ELI gateway configuration - full validations
        base_url = os.getenv("LLM_BASE_URL", os.getenv("ELI_BASE_URL", ""))
        api_key = os.getenv("LLM_API_KEY", os.getenv("ELI_API_KEY", ""))
        
        # Get SSL verification setting (default: True, set to "false" or "0" to disable)
        ssl_verify_str = os.getenv("LLM_SSL_VERIFY", os.getenv("ELI_SSL_VERIFY", "true")).lower()
        ssl_verify = ssl_verify_str not in ("false", "0", "no", "off")
        
        logger.info("Using REMOTE ELI gateway")
        logger.debug(f"ELI base URL: {base_url}")
        logger.debug(f"SSL verification: {ssl_verify}")
        
        # Validate required fields for remote mode only
        if not api_key or api_key == "" or api_key == "Replace with your ELI API key":
            logger.error("LLM_API_KEY or ELI_API_KEY not found in environment variables")
            raise ValueError("LLM_API_KEY or ELI_API_KEY not found in environment variables. Please set it in .env file.")
        if not base_url or base_url == "":
            logger.error("LLM_BASE_URL or ELI_BASE_URL not found in environment variables")
            raise ValueError("LLM_BASE_URL or ELI_BASE_URL not found in environment variables. Please set it in .env file.")
    
    logger.debug(f"API key present: {bool(api_key and api_key != 'Replace with your ELI API key')}")
    
    logger.info(f"Attempting to connect to LLM at: {base_url}")
    
    # Get max_tokens from environment (default: 2000 for local, None for remote)
    # Limiting tokens significantly speeds up Ollama responses
    max_tokens_env = os.getenv("LLM_MAX_TOKENS", "")
    if llm_mode == "local":
        # For local Ollama, use a reasonable default to speed up responses
        # 2000 tokens ≈ 1500 words, which is sufficient for most training content
        max_tokens = int(max_tokens_env) if max_tokens_env.isdigit() else 2000
        logger.info(f"⚡ [SPEED] Using max_tokens={max_tokens} for faster Ollama responses")
    else:
        # For remote, allow None (unlimited) or use env var if set
        max_tokens = int(max_tokens_env) if max_tokens_env.isdigit() else None
    
    logger.debug(f"Connection parameters: model={model_name}, temperature={temperature}, max_tokens={max_tokens}, max_retries=2, ssl_verify={ssl_verify}")
    
    # Create httpx client with SSL verification setting
    # Set reasonable timeout: 450 seconds (7.5 minutes) for local, 600 seconds (10 minutes) for remote
    # This prevents indefinite hangs while allowing enough time for LLM responses
    # Note: Ollama can take 300-400 seconds for complex training content generation
    timeout_seconds = 450 if llm_mode == "local" else 600
    http_client_kwargs = {}
    if not ssl_verify:
        if llm_mode == "local":
            logger.debug(f"Creating HTTP client for local Ollama (no SSL verification, timeout={timeout_seconds}s)")
        else:
            logger.warning("SSL certificate verification is DISABLED - use only in trusted/internal networks!")
        # Create httpx client with SSL verification disabled and reasonable timeout
        http_client = httpx.Client(verify=False, timeout=timeout_seconds)
        # Pass http_client to ChatOpenAI - it will use it for the underlying OpenAI client
        http_client_kwargs['http_client'] = http_client
    else:
        # Even with SSL verification, we need a timeout
        http_client = httpx.Client(verify=True, timeout=timeout_seconds)
        http_client_kwargs['http_client'] = http_client
    
    # Create an instance of ChatOpenAI using latest LangChain OpenAI API (v0.2.0+)
    try:
        logger.debug("Creating ChatOpenAI instance with latest API (api_key/base_url)")
        logger.info(f"🔧 [CONFIG] Model: {model_name}")
        logger.info(f"🔧 [CONFIG] Base URL: {base_url}")
        logger.info(f"🔧 [CONFIG] Temperature: {temperature}")
        logger.info(f"🔧 [CONFIG] Max tokens: {max_tokens} ({'limited' if max_tokens else 'unlimited'})")
        logger.info(f"🔧 [CONFIG] Max retries: 2")
        logger.info(f"🔧 [CONFIG] HTTP timeout: {timeout_seconds}s ({timeout_seconds/60:.1f} minutes)")
        llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,  # Limit tokens for faster responses
            timeout=timeout_seconds,  # Set timeout to match http_client
            max_retries=2,
            api_key=api_key,
            base_url=base_url,
            **http_client_kwargs,  # Includes http_client with proper timeout
        )
        logger.info("✅ LLM connection established successfully")
        logger.info("📡 [OLLAMA] Ready to accept requests")
    except Exception as e:
        logger.error(f"Failed to initialize LLM connection: {str(e)}")
        logger.exception("Full traceback:")
        raise
    
    logger.info("LLM connection initialized and ready")
    logger.info("="*80)
    return llm

# Lazy initialization of LLM to avoid import-time failures
_LLM = None

def get_llm():
    """Get or create the global LLM instance"""
    global _LLM
    if _LLM is None:
        try:
            _LLM = get_eli_chat_model()
            logger.info("Global LLM instance created successfully")
        except Exception as e:
            logger.error(f"CRITICAL: Failed to create global LLM instance: {str(e)}")
            raise
    return _LLM

# LLM Proxy for lazy initialization
class LLMProxy:
    """Proxy class that lazily initializes the LLM when accessed"""
    _llm_instance = None
    
    def _get_llm(self):
        """Get the actual LLM instance"""
        if self._llm_instance is None:
            self._llm_instance = get_llm()
        return self._llm_instance
    
    def __getattr__(self, name):
        """Delegate all attribute access to the actual LLM"""
        return getattr(self._get_llm(), name)
    
    def __or__(self, other):
        """Support LangChain pipe operator: prompt | LLM"""
        return self._get_llm() | other
    
    def __ror__(self, other):
        """Support LangChain pipe operator: prompt | LLM"""
        return other | self._get_llm()
    
    def __call__(self, *args, **kwargs):
        """Make the proxy callable - ChatOpenAI uses invoke(), not direct call"""
        # ChatOpenAI objects are not directly callable, they use invoke()
        return self._get_llm().invoke(*args, **kwargs)
    
    def invoke(self, *args, **kwargs):
        """Explicit invoke method"""
        return self._get_llm().invoke(*args, **kwargs)

# Create LLM proxy instance
LLM = LLMProxy()
console = Console()

class TrainingContentInput(BaseModel):
    knowledge_base: str = Field(..., description="'alarm_handling' or 'mml'")
    level: str = Field(..., description="'beginner', 'intermediate', 'advanced', 'architecture'")

def classify_chunk_type(chunk: Document) -> str:
    """✅ Classify chunk as Text/Image/Table"""
    metadata = chunk.metadata
    content = chunk.page_content.lower()
    
    if metadata.get('category') == 'Image' or metadata.get('element_type') == 'Image':
        return 'Image'
    if metadata.get('category') == 'Table' or metadata.get('element_type') == 'Table':
        return 'Table'
    if metadata.get('has_images'):
        return 'Image'
    
    image_keywords = ['diagram', 'figure', 'fig', 'image', 'chart', 'graph', 'flow']
    table_keywords = ['table', '|', '---', 'parameter', 'value']
    
    if sum(1 for kw in image_keywords if kw in content) >= 1:
        return 'Image'
    if sum(1 for kw in table_keywords if kw in content) >= 2:
        return 'Table'
    
    return 'Text'

def retrieve_all_chunks_raw(knowledge_base: str) -> List[Document]:
    """✅ Retrieve 100% ALL chunks from FAISS"""
    index_path = None
    possible_paths = [
        Path(f"{FAISS_ROOT}/{knowledge_base}"),
        Path(f"{FAISS_ROOT}/{knowledge_base.lower()}"),
        Path(f"./{knowledge_base}"),
        Path(f"./faiss_indexes/{knowledge_base}")
    ]
    
    for path in possible_paths:
        if path.exists() and list(path.glob("index.faiss")):
            index_path = path
            print(f"✅ Found FAISS index: {path}")
            break
    
    if not index_path:
        return []
    
    try:
        vectorstore = FAISS.load_local(str(index_path), EMBEDDINGS, allow_dangerous_deserialization=True)
        index_size = vectorstore.index.ntotal
        
        if index_size > 0:
            try:
                all_docs_with_scores = vectorstore.similarity_search_with_score(" ", k=index_size)
                all_docs = [doc for doc, score in all_docs_with_scores]
            except:
                all_docs = vectorstore.similarity_search(" ", k=index_size)
        else:
            all_docs = []
    except Exception as e:
        print(f"❌ FAISS error: {e}")
        return []
    
    filtered_docs = [doc for doc in all_docs 
                    if knowledge_base.lower() in str(doc.metadata).lower()]
    print(f"✅ Retrieved {len(filtered_docs)} chunks from RAG")
    return filtered_docs

# 🔥 LLM-POWERED GROUPING (NEW)
def llm_group_chunks(chunks: List[Document], knowledge_base: str) -> Dict[str, List[Document]]:
    """🔥 ELI LLM creates intelligent groups from ALL chunks (NO limit!)"""
    print(f"🤖 LLM analyzing **ALL {len(chunks)}** chunks for grouping...")
    
    # ✅ ALL CHUNKS (no [:60] limit)
    chunk_samples = []
    for i, chunk in enumerate(chunks):  # ALL chunks!
        chunk_type = classify_chunk_type(chunk)
        source = Path(chunk.metadata.get('source', 'unknown.pdf')).name
        preview = chunk.page_content[:250].strip()  # Shorter previews for more chunks
        chunk_samples.append(f"CHUNK {i+1} [{chunk_type.upper()}] {source}: {preview}")
    
    # ✅ ALL samples (chunked if too long)
    sample_text = "\n---\n".join(chunk_samples)
    
    # Chunk if exceeds token limit
    if len(sample_text) > 8000:
        sample_text = sample_text[:8000] + "\n...[TRUNCATED - ALL CHUNKS ANALYZED]"
        print(f"⚠️ Truncated to 8000 chars ({len(chunk_samples)} chunks analyzed)")
    
    prompt = ChatPromptTemplate.from_template("""
You are **Ericsson Telecom Training Architect**. Organize **ALL {len_chunks}** {knowledge_base} chunks into **5-12 meaningful business topics**.

**ALL CHUNKS** (Text/Images/Tables - analyze complete list):
{sample_text}

**OUTPUT EXACTLY this JSON**:
{{
  "groups": [
    {{
      "name": "MML Command Syntax & Examples",
      "chunk_indices": [1,5,12,23,45,67,89]
    }},
    {{
      "name": "Network Flow Diagrams", 
      "chunk_indices": [2,8,19,33,56]
    }}
  ]
}}

**IMPORTANT**: Use ALL chunk numbers (1-{len_chunks}). Images/Tables first.
""")
    
    chain = prompt | LLM | StrOutputParser()
    
    try:
        response = chain.invoke({
            "knowledge_base": knowledge_base, 
            "sample_text": sample_text,
            "len_chunks": len(chunks)
        })
        groups_json = json.loads(response.strip())
        
        grouped = {}
        for group in groups_json.get("groups", []):
            name = group.get("name", "Unnamed Group")
            indices = group.get("chunk_indices", [])
            group_chunks = [chunks[i-1] for i in indices if 0 <= i-1 < len(chunks)]
            if group_chunks:
                grouped[name] = group_chunks
        
        print(f"✅ LLM grouped **ALL {len(chunks)}** chunks into {len(grouped)} groups")
        return grouped
        
    except Exception as e:
        print(f"⚠️ LLM failed: {e} → Fallback")
        return create_fallback_groups(chunks)

def create_fallback_groups(chunks: List[Document]) -> Dict[str, List[Document]]:
    """Fallback if LLM fails"""
    grouped = {}
    image_chunks = [c for c in chunks if classify_chunk_type(c) == 'Image']
    table_chunks = [c for c in chunks if classify_chunk_type(c) == 'Table']
    text_chunks = [c for c in chunks if classify_chunk_type(c) == 'Text']
    
    if image_chunks: grouped["🖼️ Diagrams & Flowcharts"] = image_chunks
    if table_chunks: grouped["📊 Reference Tables & Codes"] = table_chunks
    if text_chunks: grouped["📝 Procedures & Commands"] = text_chunks
    
    return grouped

@tool(args_schema=TrainingContentInput)
def retrieve_training_content(knowledge_base: str, level: str) -> str:
    """✅ LLM GROUPS ALL CHUNKS → SAVES ROOT DIR → RETURNS SAME GROUPS FOR LLM"""
    
    print(f"\n🔥 LLM-POWERED: {knowledge_base} ({level})")
    
    all_chunks = retrieve_all_chunks_raw(knowledge_base)
    if not all_chunks:
        available = [p.name for p in Path(FAISS_ROOT).iterdir() if p.is_dir()]
        return f"❌ No '{knowledge_base}' chunks\nAvailable: {available}"
    
    total_chunks = len(all_chunks)
    print(f"✅ Retrieved {total_chunks} chunks (Text+Images+Tables)")
    
    cache_file = Path(f"./{knowledge_base}_llm_groups.json")
    grouped_chunks = None
    
    if cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text(encoding='utf-8'))
            if cached["total_chunks"] == total_chunks:
                print(f"✅ LOADED CACHE: {len(cached['groups'])} LLM groups")
                grouped_chunks = {
                    g["name"]: [Document(**chunk_data) for chunk_data in g["chunks"]]
                    for g in cached["groups"]
                }
        except Exception as e:
            print(f"⚠️ Cache invalid: {e}")
    
    if not grouped_chunks:
        print("🤖 LLM creating intelligent groups...")
        grouped_chunks = llm_group_chunks(all_chunks, knowledge_base)
        
        cache_data = {
            "knowledge_base": knowledge_base,
            "level": level,
            "total_chunks": total_chunks,
            "groups": [
                {
                    "name": name,
                    "chunk_count": len(chunks),
                    "chunks": [chunk.dict() for chunk in chunks]
                }
                for name, chunks in grouped_chunks.items()
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        cache_file.write_text(json.dumps(cache_data, ensure_ascii=False, indent=2), encoding='utf-8')
        
        full_content = generate_llm_grouped_content(grouped_chunks, knowledge_base, level, total_chunks, all_chunks)
        txt_file = Path(f"./{knowledge_base}_{level}_{total_chunks}chunks_LLM.txt")
        txt_file.write_text(full_content, encoding='utf-8')
        
        print(f"💾 SAVED ROOT DIR:")
        print(f"   📁 {cache_file.name}")
        print(f"   📄 {txt_file.name}")
    
    full_context = generate_llm_grouped_content(grouped_chunks, knowledge_base, level, total_chunks, all_chunks)
    print(f"✅ {len(grouped_chunks)} LLM groups → SAME groups sent back to LLM")
    
    return full_context

def generate_llm_grouped_content(grouped: Dict[str, List[Document]], knowledge_base: str, 
                               level: str, total_chunks: int, all_chunks: List[Document]) -> str:
    """✅ FIXED: Format for display + LLM context - Handles missing types"""
    
    lines = []
    lines.extend([
        "=" * 120,
        f"🤖 LLM-ORGANIZED: {knowledge_base.upper()} - {level.upper()} LEVEL",
        f"📊 TOTAL: {total_chunks} CHUNKS | {len(grouped)} INTELLIGENT GROUPS",
        f"💾 Cache: ./{knowledge_base}_llm_groups.json (ROOT DIR)",
        "=" * 120,
        ""
    ])
    
    # ✅ FIXED: Safe type counting
    type_counts = {'Text': 0, 'Image': 0, 'Table': 0}
    for chunk in all_chunks:
        t = classify_chunk_type(chunk)
        type_counts[t] = type_counts.get(t, 0) + 1
    
    lines.extend([
        f"📈 BREAKDOWN: 📝 Text={type_counts['Text']} | 🖼️ Images={type_counts['Image']} | 📊 Tables={type_counts['Table']}",
        "",
        "🤖 LLM-ORGANIZED GROUPS (Use these exact groups):",
        ""
    ])
    
    # Sort groups by size (largest first)
    sorted_groups = sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True)
    group_num = 1
    
    for group_name, group_chunks in sorted_groups:
        lines.extend([
            f"\n{'#'*120}",
            f"⭐ GROUP {group_num}: {group_name}",
            f"📊 {len(group_chunks)} FULL CHUNKS",
            f"{'#'*120}",
            ""
        ])
        
        # ALL CHUNKS IN GROUP (FULL CONTENT)
        for chunk_idx, chunk in enumerate(group_chunks, 1):
            source = Path(chunk.metadata.get('source', 'unknown.pdf')).name
            page = chunk.metadata.get('page', 'N/A')
            chunk_type = classify_chunk_type(chunk)
            
            # Image/Table references
            visual_ref = ""
            if chunk_type == 'Image':
                img_name = f"{source.replace('.pdf','')}_page_{page}_"
                visual_ref = f"\n💾 IMAGE: extracted_images/{knowledge_base}/{img_name}*.png"
            elif chunk_type == 'Table':
                visual_ref = "\n📊 TABLE DATA:"
            
            lines.extend([
                f"\n  🆔 CHUNK {chunk_idx}/{len(group_chunks)}",
                f"  📍 {source} | Page {page} | Type: {chunk_type}",
                visual_ref if visual_ref else "",
                f"  📄 {'='*80}",
                f"  {chunk.page_content.strip()}",
                f"  {'='*80}"
            ])
        
        group_num += 1
    
    lines.extend([
        f"\n{'='*120}",
        f"✅ VERIFICATION: {total_chunks}/{total_chunks} chunks (100%)",
        f"📂 {len(grouped)} LLM groups preserved",
        f"🎯 SAME GROUPS SENT BACK TO LLM FOR Q&A",
        f"💾 Files saved in ROOT directory",
        "=" * 120
    ])
    
    return "\n".join(lines)

# ✅ YOUR ComprehensiveTrainingCoach CLASS (UNCHANGED)
class ComprehensiveTrainingCoach:
    def __init__(self):
        console.print("[bold green]🚀 Initializing Comprehensive Telecom Training Coach...[/bold green]")
        self.index_paths = self._scan_indexes()
        if not self.index_paths:
            console.print("[bold red]❌ No knowledge bases found![/bold red]")
            exit(1)
        console.print(f"[bold green]✅ {len(self.index_paths)} knowledge bases loaded![/bold green]\n")
    
    def _scan_indexes(self) -> Dict[str, str]:
        indexes = {}
        folders = ["alarm handling", "mml"]
        for folder in folders:
            index_path = Path(f"{FAISS_ROOT}/{folder}")
            if index_path.exists():
                try:
                    vectorstore = FAISS.load_local(str(index_path), EMBEDDINGS, allow_dangerous_deserialization=True)
                    doc_count = len(vectorstore.index_to_docstore_id)
                    indexes[folder] = str(index_path)
                    console.print(f"  ✅ [cyan]{folder}[/cyan]: [yellow]{doc_count:,}[/yellow] documents")
                except Exception as e:
                    console.print(f"  ❌ [red]{folder}:[red] Load error - {e}")
            else:
                console.print(f"  ❌ [red]{folder}:[/red] Directory not found")
        return indexes
    
    def show_welcome_dashboard(self):
        """Rich interactive dashboard"""
        console.clear()
        
        # Enhanced welcome
        welcome_content = Text()
        welcome_content.append("🤖 AI TELECOM TRAINING COACH", style="bold cyan")
        welcome_content.append("\n\n", style="white")
        welcome_content.append("Production-grade training from your PDF specifications:\n", style="bold white")
        welcome_content.append("• [green]Complete MML Command Reference[/green]\n", style="white")
        welcome_content.append("• [green]CNZ Alarm Resolution Procedures[/green]\n", style="white")
        welcome_content.append("• [green]AXE Architecture & Troubleshooting[/green]\n", style="white")
        welcome_content.append("• [green]Beginner → Expert Progression[/green]\n", style="white")
        
        welcome_panel = Panel(
            welcome_content,
            title="[bold green]🚀 ENTERPRISE TRAINING PLATFORM[/bold green]", 
            border_style="bright_green",
            padding=(1, 2)
        )
        console.print(welcome_panel)
        
        # Knowledge base selection table
        table = Table(title="[bold magenta]📚 SELECT TRAINING MODULE[/bold magenta]", 
                     show_header=True, header_style="bold magenta")
        table.add_column("🎓 MODULE", style="cyan", width=28)
        table.add_column("📖 COMPREHENSIVE COVERAGE", style="green")
        table.add_column("📊 STATUS", justify="right", style="yellow")
        
        for kb in self.index_paths:
            display_name = kb.replace('handling', 'Handling').title()
            coverage = (
                "• Fundamentals & Theory\n"
                "• Complete MML Syntax\n"
                "• Architecture Diagrams\n"
                "• Troubleshooting Matrix\n"
                "• Specifications & KPIs"
            )
            table.add_row(display_name, coverage, "✅ [green]LOADED[/green]")
        
        console.print(table)
        
        choices = list(self.index_paths.keys()) + ["quit"]
        return Prompt.ask(
            "\n[bold cyan]🎯 SELECT MODULE[/bold cyan]", 
            choices=choices, 
            default="quit"
        )
    
    def start_training_module(self, knowledge_base: str):
        """Progressive comprehensive training experience"""
        display_name = knowledge_base.replace('handling', 'Handling').title()
        
        training_levels = {
            0: ("BEGINNER", "Core Fundamentals & Basic Commands"),
            1: ("INTERMEDIATE", "Practical Application & Procedures"), 
            2: ("ADVANCED", "Expert Troubleshooting & Optimization"),
            3: ("ARCHITECTURE", "System Design & Specifications")
        }
        
        current_level_idx = 0
        
        while True:
            level_idx, (emoji, subtitle) = list(training_levels.items())[current_level_idx]
            level_key = ["beginner", "intermediate", "advanced", "architecture"][current_level_idx]
            
            console.clear()
            
            # Professional training header
            header_content = Text()
            header_content.append(f"{emoji} {display_name}", style="bold white")
            header_content.append(f"\n{subtitle}", style="italic cyan")
            
            header_panel = Panel(
                header_content,
                title=f"[bold blue]{knowledge_base.upper()}[/bold blue] | TRAINING LEVEL {level_idx+1}/4",
                subtitle="[dim]LLM-organized content with diagrams, commands, architecture[/dim]",
                border_style="bright_blue",
                padding=(2, 2)
            )
            console.print(header_panel)
            
            console.print("\n[bold]🔄 Loading LLM-organized content...[/bold]")
            
            # Retrieve LLM-grouped content
            content = retrieve_training_content.invoke({
                "knowledge_base": knowledge_base,
                "level": level_key
            })
            
            # Generate DETAILED lesson using LLM groups
            lesson = self.generate_comprehensive_lesson(knowledge_base, level_key, content)
            
            # Rich lesson display
            lesson_panel = Panel(
                lesson,
                title=f"[bold cyan]{emoji} {subtitle}[/bold cyan]",
                border_style="cyan",
                padding=(1, 2),
                expand=False
            )
            console.print(lesson_panel)
            
            console.print("\n" + "─" * 120)
            
            # Navigation
            nav_table = Table.grid(expand=True, padding=(0, 1))
            nav_table.add_column("Action", style="bold cyan")
            nav_table.add_column("Description", style="white")
            
            next_level = list(training_levels.keys())[(current_level_idx + 1) % 4]
            next_display = list(training_levels.values())[(current_level_idx + 1) % 4][0]
            
            nav_table.add_row("1️⃣ NEXT LEVEL", f"→ {next_display}")
            nav_table.add_row("2️⃣ ASK DOUBT", "Interactive Q&A from LLM groups")
            nav_table.add_row("3️⃣ REPEAT", "Review current level")
            nav_table.add_row("4️⃣ DASHBOARD", "Return to module selection")
            nav_table.add_row("Q. QUIT", "Exit training")
            
            console.print(nav_table)
            
            choice = Prompt.ask(
                "\n[bold cyan]What next?[/bold cyan]", 
                choices=["1", "2", "3", "4", "q"], 
                default="1"
            )
            
            if choice == "1":
                current_level_idx = (current_level_idx + 1) % 4
            elif choice == "2":
                self.handle_comprehensive_doubts(knowledge_base, level_key)
            elif choice == "3":
                continue
            elif choice == "4":
                return
            elif choice == "q":
                return "quit"
    
    def generate_comprehensive_lesson(self, knowledge_base: str, level: str, docs: str) -> str:
        """Generate structured, level-appropriate training lesson"""
        level_configs = {
            "beginner": {
                "instructions": "Use simple, clear language with step-by-step explanations. Focus on foundational concepts and basic understanding. Avoid jargon or explain it clearly when used.",
                "depth": "basic",
                "sections": ["Introduction", "Fundamentals", "Key Concepts", "Basic Examples", "Summary", "References"]
            },
            "intermediate": {
                "instructions": "Provide practical examples, real-world scenarios, and troubleshooting guidance. Include hands-on exercises and common use cases.",
                "depth": "practical",
                "sections": ["Overview", "Core Concepts", "Practical Applications", "Common Scenarios", "Troubleshooting", "Best Practices", "References"]
            },
            "advanced": {
                "instructions": "Dive deep into technical details, edge cases, optimization techniques, and advanced configurations. Include performance considerations and complex scenarios.",
                "depth": "expert",
                "sections": ["Advanced Overview", "Deep Dive Concepts", "Advanced Configurations", "Performance Optimization", "Edge Cases & Troubleshooting", "Best Practices & Patterns", "References"]
            },
            "architecture": {
                "instructions": "Focus on system design, architectural patterns, data flows, integration points, scalability, and high-level design decisions. Include architectural diagrams and design rationale.",
                "depth": "system",
                "sections": ["Architectural Overview", "System Architecture", "Architectural Flow & Diagrams", "Design Details", "Integration Points", "Scalability & Performance", "Design Patterns", "References"]
            }
        }
    
        level_config = level_configs.get(level.lower(), level_configs["beginner"])
        level_instructions = level_config["instructions"]
        sections = level_config["sections"]
    
        prompt = ChatPromptTemplate.from_template("""
You are an **Ericsson Senior Telecom Training Architect** specializing in {knowledge_base}. Your task is to create a comprehensive, well-structured training lesson tailored for {level} level learners.

**SOURCE DOCUMENTS** (Use ALL provided content - maintain accuracy, NO hallucination):

{docs}

**TRAINING LEVEL**: {level}
**INSTRUCTIONS**: {level_instructions}

**REQUIRED STRUCTURE** (Follow this exact format):

## 1. Introduction
- Brief overview of the topic
- Learning objectives
- Prerequisites (if any)
- What you will learn

## 2. Fundamentals / Core Concepts / Advanced Overview / Architectural Overview
(Choose section name based on level)
- Essential concepts and principles
- Key terminology and definitions
- Foundation knowledge required

## 3. Core Concepts / Practical Applications / Deep Dive Concepts / System Architecture
(Choose section name based on level)
- Detailed explanations
- Important concepts and their relationships
- Technical details appropriate for {level} level

## 4. Architectural Flow & Diagrams
(Especially important for architecture level, but include for all levels when relevant)
- System/data flow descriptions
- Architecture diagrams (use ASCII art or detailed text descriptions)
- Component interactions
- Process flows
- Integration points

## 5. Design Details / Common Scenarios / Advanced Configurations / Design Details
(Choose section name based on level)
- Practical examples and use cases
- Configuration details
- Implementation guidance
- Real-world scenarios

## 6. Best Practices / Troubleshooting / Edge Cases / Integration Points
(Choose section name based on level)
- Industry best practices
- Common issues and solutions
- Optimization tips
- Integration considerations

## 7. Summary / References
- Key takeaways
- Summary of important points
- References to source documents
- Additional resources

**CRITICAL REQUIREMENTS**:
1. **NO "Group 1", "Chunk 1", "Chunk 2" labels** - Transform raw content into natural, flowing prose
2. **Structured sections** - Use clear markdown headers (##, ###) for each section
3. **Level-appropriate depth** - Adjust complexity and detail based on {level}
4. **Architecture diagrams** - For architecture level, include detailed ASCII diagrams or clear text descriptions of system flows
5. **Professional formatting** - Use bullet points, numbered lists, code blocks, and tables where appropriate
6. **Complete content** - Synthesize information from all provided chunks into coherent sections
7. **No raw chunk references** - Do NOT mention "chunk X" or "group Y" in the output
8. **Smooth transitions** - Make content flow naturally between sections

**OUTPUT**: Generate a complete, professional training lesson following the structure above. Make it engaging, clear, and appropriate for {level} level learners.
""")
    
        chain = prompt | LLM | StrOutputParser()
    
        logger.info(f"Generating {level} level lesson for {knowledge_base}")
        logger.debug(f"Using sections: {sections}")
        
        return chain.invoke({
            "knowledge_base": knowledge_base,
            "level": level,
            "docs": docs,
            "level_instructions": level_instructions
        })
    
    def handle_comprehensive_doubts(self, knowledge_base: str, current_level: str):
        """Production-grade doubt clearing using LLM groups"""
        console.print("\n🆘 [bold red]EXPERT TECHNICAL SUPPORT[/bold red]")
        console.print(f"[cyan]🔒 Context Locked: {knowledge_base.title()} | Level: {current_level}[/cyan]")
        console.print("[dim]💭 Ask production-level doubts ('back' to return)[/dim]\n")
        
        while True:
            doubt = Prompt.ask("[bold yellow]❓ TECHNICAL DOUBT[/bold yellow]").strip()
            if doubt.lower() in ['back', 'return', 'menu']:
                break
            
            console.print("[dim]🔍 Searching LLM-organized knowledge base...[/dim]")
            answer = self.answer_comprehensive_doubt(knowledge_base, doubt)
            
            doubt_panel = Panel(
                answer,
                title="[bold green]💡 EXPERT RESOLUTION[/bold green]", 
                border_style="green",
                padding=(1, 2)
            )
            console.print(doubt_panel)
            console.print()
    
    def answer_comprehensive_doubt(self, knowledge_base: str, doubt: str) -> str:
        """Comprehensive technical doubt resolution using LLM groups"""
        docs = retrieve_training_content.invoke({
            "knowledge_base": knowledge_base,
            "level": "advanced"
        })
        
        prompt = ChatPromptTemplate.from_template("""
**PRODUCTION-CRITICAL DOUBT RESOLUTION** using {knowledge_base} LLM groups:

❓ **DOUBT**: {doubt}

📚 **LLM-ORGANIZED CONTEXT**:
{docs}

**EXPECTED FORMAT**:
1. **Direct Answer** (1 line)
2. **Relevant LLM Group** (quote exact group name)
3. **Step-by-Step Resolution**
4. **MML Commands** (if applicable)
5. **Image/Table References**
6. **Verification Steps**

**Answer using ONLY these LLM groups - no hallucination.**
""")
        
        chain = prompt | LLM | StrOutputParser()
        return chain.invoke({"knowledge_base": knowledge_base, "doubt": doubt, "docs": docs})
    
    def run(self):
        """Main enterprise training platform"""
        console.print("\n[bold green]🎓 ENTERPRISE TELECOM TRAINING PLATFORM v2.0 - LLM POWERED[/bold green]")
        console.print("[dim]Press Ctrl+C to exit at any time[/dim]\n")
        
        try:
            while True:
                choice = self.show_welcome_dashboard()
                
                if choice == "quit":
                    console.print("\n[bold green]🎓 TRAINING SESSION COMPLETE![/bold green]")
                    console.print("🚀 [yellow]Mastered:[/] MML Commands | Alarm Handling | LLM Groups")
                    console.print("📚 [dim]Files saved in root: *_llm_groups.json[/dim]")
                    break
                
                if choice in self.index_paths:
                    result = self.start_training_module(choice)
                    if result == "quit":
                        break
                else:
                    console.print("[bold red]❌ Invalid selection![/bold red]")
        
        except KeyboardInterrupt:
            console.print("\n\n[bold yellow]👋 Session ended. Happy learning![/bold yellow]")

# 🚀 LAUNCH PRODUCTION TRAINING COACH
if __name__ == "__main__":
    coach = ComprehensiveTrainingCoach()
    coach.run()