# ai_coach_dashboard.py - COMPLETE COMPREHENSIVE TELECOM TRAINING COACH
import os
import logging
import sys
from datetime import datetime
from typing import Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool
from langchain_core.output_parsers import StrOutputParser
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from pathlib import Path
from pydantic import BaseModel, Field
import httpx
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from dotenv import load_dotenv

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

# Load environment variables from .env file
load_dotenv()
logger.info("Environment variables loaded from .env file")

# Configuration
FAISS_ROOT = "./services/faiss_indexes/"
EMBEDDINGS = HuggingFaceBgeEmbeddings(
            model_name="BAAI/bge-base-en-v1.5",
            model_kwargs={"device": "cpu", "trust_remote_code": True},
            encode_kwargs={"normalize_embeddings": True},#True enabling Semantic search
    )
def get_eli_chat_model(temperature: float = 0.0, model_name: str = None):
    logger.info("="*80)
    logger.info("INITIALIZING LLM CONNECTION")
    
    # Get LLM mode: "local" for Ollama, "remote" for ELI gateway (default: auto-detect)
    llm_mode = os.getenv("LLM_MODE", "auto").lower()
    
    # Get model name from environment or use default
    if model_name is None:
        model_name = os.getenv("LLM_MODEL", "qwen2.5-7b")
    
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
    logger.debug(f"Connection parameters: model={model_name}, temperature={temperature}, max_retries=2, ssl_verify={ssl_verify}")
    
    # Create httpx client with SSL verification setting
    # This is needed for Windows machines with certificate issues
    # In newer OpenAI SDK (v1.x) and langchain-openai, we need to pass http_client
    # Note: ChatOpenAI accepts http_client parameter directly in v0.2.0+
    http_client_kwargs = {}
    if not ssl_verify:
        if llm_mode == "local":
            logger.debug("Creating HTTP client for local Ollama (no SSL verification needed)")
        else:
            logger.warning("SSL certificate verification is DISABLED - use only in trusted/internal networks!")
        # Create httpx client with SSL verification disabled
        http_client = httpx.Client(verify=False, timeout=None)
        # Pass http_client to ChatOpenAI - it will use it for the underlying OpenAI client
        http_client_kwargs['http_client'] = http_client
    # If ssl_verify is True, we don't need to pass http_client (uses default with verification)
    
    # Create an instance of ChatOpenAI using latest LangChain OpenAI API (v0.2.0+)
    # Latest API uses api_key and base_url parameters
    # http_client parameter is passed to control SSL verification
    try:
        logger.debug("Creating ChatOpenAI instance with latest API (api_key/base_url)")
        llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=api_key,
            base_url=base_url,
            **http_client_kwargs,  # Only includes http_client if SSL verification is disabled
        )
        logger.info("LLM connection established successfully")
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
    """Get or create the global LLM instance (lazy initialization)"""
    global _LLM
    if _LLM is None:
        try:
            _LLM = get_eli_chat_model()
            logger.info("Global LLM instance created successfully")
        except Exception as e:
            logger.error(f"CRITICAL: Failed to create global LLM instance: {str(e)}")
            logger.exception("Full traceback:")
            raise
    return _LLM

# For backward compatibility - create a proxy that works with LangChain's pipe operator
# The proxy needs to implement __or__ and __ror__ to work with the | operator
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
    
    def __call__(self, *args, **kwargs):
        """Make the proxy callable - ChatOpenAI uses invoke(), not direct call"""
        # ChatOpenAI objects are not directly callable, they use invoke()
        return self._get_llm().invoke(*args, **kwargs)
    
    def invoke(self, *args, **kwargs):
        """Invoke method for LangChain"""
        return self._get_llm().invoke(*args, **kwargs)
    
    def __or__(self, other):
        """Support for LangChain pipe operator: LLM | parser"""
        return self._get_llm() | other
    
    def __ror__(self, other):
        """Support for LangChain pipe operator: prompt | LLM"""
        return other | self._get_llm()
    
    def __getstate__(self):
        """Support for pickling"""
        return {}
    
    def __setstate__(self, state):
        """Support for unpickling"""
        self._llm_instance = None

# Create module-level LLM proxy
LLM = LLMProxy()

console = Console()

class TrainingContentInput(BaseModel):
    """Input schema for comprehensive training content"""
    knowledge_base: str = Field(description="'mml' or 'alarm_handling'")
    level: str = Field(description="'beginner', 'intermediate', 'advanced', 'architecture'")
    topic: str = Field(default="", description="Specific topic for doubt clearing")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "knowledge_base": "mml",
                "level": "beginner",
                "topic": ""
            }
        }
    }

@tool(args_schema=TrainingContentInput)
def retrieve_training_content(knowledge_base: str, level: str, topic: str = "") -> str:
    """Retrieve comprehensive training content from specific knowledge base"""
    logger.info("="*80)
    logger.info("RETRIEVING TRAINING CONTENT FROM FAISS")
    logger.info(f"  Knowledge Base: {knowledge_base}")
    logger.info(f"  Level: {level}")
    logger.info(f"  Topic: {topic}")
    logger.info("="*80)
    
    index_path = Path(f"{FAISS_ROOT}/{knowledge_base}")
    logger.debug(f"FAISS index path: {index_path}")
    
    if not index_path.exists():
        logger.error(f"FAISS index not found at: {index_path}")
        return f"❌ No {knowledge_base} knowledge base available"
    
    try:
        logger.info(f"Loading FAISS vectorstore from: {index_path}")
        vectorstore = FAISS.load_local(
            str(index_path),
            EMBEDDINGS,
            allow_dangerous_deserialization=True
        )
        logger.info("FAISS vectorstore loaded successfully")
    except Exception as e:
        logger.error(f"Error loading FAISS vectorstore: {str(e)}")
        logger.exception("Full traceback:")
        return f"❌ Error loading {knowledge_base}: {str(e)}"
    
    # Enhanced query for comprehensive retrieval
    query = f"{knowledge_base} {level} training {topic} fundamentals concepts design details architecture commands ".strip()
    logger.info(f"Performing similarity search with query: {query[:100]}...")
    logger.debug(f"Search parameters: k=10 (top 10 documents)")
    
    try:
        docs = vectorstore.similarity_search(query, k=10)  # Maximum relevant docs
        logger.info(f"Similarity search completed: found {len(docs)} documents")
    except Exception as e:
        logger.error(f"Error during similarity search: {str(e)}")
        logger.exception("Full traceback:")
        return f"❌ Error searching {knowledge_base}: {str(e)}"
    
    content = []
    for i, doc in enumerate(docs, 1):
        doc_source = Path(doc.metadata.get('source', 'N/A')).name
        doc_page = doc.metadata.get('page', 'N/A')
        doc_length = len(doc.page_content)
        logger.debug(f"Document {i}: source={doc_source}, page={doc_page}, length={doc_length} chars")
        
        content.append(
            f"=== 📄 DOCUMENT {i} ===\n"
            f"📁 Source: {doc_source}\n"
            f"📍 Page: {doc_page}\n"
            f"📝 Extracted Content:\n{doc.page_content}\n{'='*80}"
        )
    
    result = "\n\n".join(content)
    logger.info(f"Retrieved content assembled: {len(result)} total characters from {len(docs)} documents")
    logger.info("="*80)
    return result

class ComprehensiveTrainingCoach:
    def __init__(self):
        console.print("[bold green]🚀 Initializing Comprehensive Telecom Training Coach...[/bold green]")
        self.index_paths = self._scan_indexes()
        if not self.index_paths:
            error_msg = "❌ No knowledge bases found! Run rag.py first to create FAISS indexes.\n📁 Expected: faiss_indexes/alarm_handling/ & faiss_indexes/mml/"
            console.print(f"[bold red]{error_msg}[/bold red]")
            raise FileNotFoundError(error_msg)
        console.print(f"[bold green]✅ {len(self.index_paths)} knowledge bases loaded![/bold green]\n")
    
    def _scan_indexes(self) -> Dict[str, str]:
        """Scan and validate FAISS indexes"""
        indexes = {}
        folders = ["alarm_handling", "mml"]
        for folder in folders:
            index_path = Path(f"{FAISS_ROOT}/{folder}")
            if index_path.exists():
                try:
                    # Quick validation
                    vectorstore = FAISS.load_local(
                        str(index_path), EMBEDDINGS, 
                        allow_dangerous_deserialization=True
                    )
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
            display_name = kb.replace('_', ' ').replace('handling', 'Handling').title()
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
        display_name = knowledge_base.replace('_', ' ').replace('handling', 'Handling').title()
        
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
                subtitle="[dim]Comprehensive lesson with diagrams, commands, architecture[/dim]",
                border_style="bright_blue",
                padding=(2, 2)
            )
            console.print(header_panel)
            
            console.print("\n[bold]🔄 Generating comprehensive lesson from PDFs...[/bold]")
            
            # Retrieve comprehensive content
            content = retrieve_training_content.invoke({
                "knowledge_base": knowledge_base,
                "level": level_key
            })
            
            # Generate DETAILED lesson
            lesson = self.generate_comprehensive_lesson(knowledge_base, level_key, content)
            
            # Rich lesson display with scrollable content
            lesson_panel = Panel(
                lesson,
                title=f"[bold cyan]{emoji} {subtitle}[/bold cyan]",
                border_style="cyan",
                padding=(1, 2),
                expand=False
            )
            console.print(lesson_panel)
            
            console.print("\n" + "─" * 120)
            
            # Professional navigation
            nav_table = Table.grid(expand=True, padding=(0, 1))
            nav_table.add_column("Action", style="bold cyan")
            nav_table.add_column("Description", style="white")
            
            next_level = list(training_levels.keys())[(current_level_idx + 1) % 4]
            next_display = list(training_levels.values())[(current_level_idx + 1) % 4][0]
            
            nav_table.add_row(
                "1️⃣ NEXT LEVEL", 
                f"→ {next_display}"
            )
            nav_table.add_row("2️⃣ ASK DOUBT", "Interactive Q&A from this knowledge base")
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
                continue  # Repeat current level
            elif choice == "4":
                return
            elif choice == "q":
                return "quit"
    
    def generate_comprehensive_lesson(self, knowledge_base: str, level: str, docs: str) -> str:
        """Generate LEVEL-SPECIFIC training lesson from knowledge base ONLY"""
        logger.info("="*80)
        logger.info("GENERATING COMPREHENSIVE LESSON")
        logger.info(f"  Knowledge Base: {knowledge_base}")
        logger.info(f"  Level: {level}")
        logger.info(f"  Input docs length: {len(docs)} characters")
        logger.info("="*80)
    
        # Level-specific depth instructions
        level_configs = {
        "beginner": {
            "instructions": "Use simple language, basic concepts, step-by-step explanations. Avoid advanced terminology unless explained.",
            "depth": "basic"
        },
        "intermediate": {
            "instructions": "Include practical examples, common scenarios, basic troubleshooting. Explain WHY commands work with examples.",
            "depth": "practical"
        },
        "advanced": {
            "instructions": "Deep technical details, edge cases, performance optimization, advanced MML commands, configuration parameters.",
            "depth": "expert"
        },
        "architecture": {
            "instructions": "System design, data flows, component interactions, configuration parameters, scalability considerations.",
            "depth": "system"
        }
        }
    
        # ✅ EXTRACT VALUES BEFORE TEMPLATE (FIXES [] indexing)
        level_config = level_configs.get(level.lower(), level_configs["beginner"])
        level_depth = level_config["depth"]           # ✅ Pre-compute
        level_instructions = level_config["instructions"]  # ✅ Pre-compute
        level_upper = level.upper()
        
        logger.debug(f"Level config: depth={level_depth}, instructions={level_instructions[:50]}...")
    
        prompt = ChatPromptTemplate.from_template("""
You are **Ericsson Senior Telecom Architect** specializing in {knowledge_base}.

**SOURCE DOCUMENTS ONLY** (Use ONLY this content - NO external knowledge):
{docs}

**{level_upper} LEVEL TRAINING ({level_depth} depth)**:
{level_instructions}

**EXACT REQUIRED STRUCTURE** (Content STRICTLY from documents):

## TRAINING OBJECTIVE (2 sentences)
1. What learner masters from these documents
2. Prerequisites mentioned in source materials

### **1. FUNDAMENTALS EXPLAINED** (Minimum 250 words):
Provide a detailed explanation of the basic concepts.
- **Avoid bullet points**.
- Use **full paragraphs** with clear, well-explained fundamentals.

### **2. CORE CONCEPTS** (Each concept requires 4+ sentences):
Explain each core concept comprehensively:
- Break down each concept and provide explanations for the learner to understand it fully.

### **3. DETAILED ARCHITECTURE DIAGRAM** (Minimum 12 lines):
Provide an ASCII diagram of the architecture:
- Include **legend, data flow**, and **all components**.
- Ensure the diagram is understandable and clearly conveys the structure.

### **4. FURTHER RECOMMENDATIONS**:
- Suggest **additional resources** for self-learning, practice exercises, or areas for improvement.
- Provide a **learning path** for progressing to the next level.

## **5. TECHNICAL REFERENCES**
List exact references from **training documents**:
Get heading of document and provide page number if possibe. Don't provide document number
Don't hallucinate.


**STRICT RULES**:
• 100% FROM DOCUMENTS 
• {level_upper} complexity matching instructions above
• Clear, concise, technically accurate
• Commands EXACTLY as in source
• If info missing: "Not covered in provided documents"

GENERATE LESSON:
    """)
    
        logger.info("Building prompt chain (prompt | LLM | StrOutputParser)")
        chain = prompt | LLM | StrOutputParser()
    
        # Prepare prompt variables
        prompt_vars = {
            "knowledge_base": knowledge_base,
            "level": level,
            "docs": docs,
            "level_upper": level_upper,
            "level_depth": level_depth,
            "level_instructions": level_instructions
        }
        
        logger.info("="*80)
        logger.info("SENDING PROMPT TO LLM")
        logger.info(f"  Knowledge Base: {knowledge_base}")
        logger.info(f"  Level: {level} ({level_upper})")
        logger.info(f"  Depth: {level_depth}")
        logger.info(f"  Docs length: {len(docs)} characters")
        logger.debug(f"  Full prompt variables: {list(prompt_vars.keys())}")
        logger.info("="*80)
        
        try:
            logger.info("Invoking LLM chain...")
            result = chain.invoke(prompt_vars)
            logger.info("="*80)
            logger.info("LLM RESPONSE RECEIVED")
            logger.info(f"  Response length: {len(result)} characters")
            logger.debug(f"  Response preview (first 200 chars): {result[:200]}...")
            logger.info("="*80)
            return result
        except Exception as e:
            logger.error("="*80)
            logger.error("LLM INVOCATION FAILED")
            logger.error(f"  Error: {str(e)}")
            logger.error(f"  Knowledge Base: {knowledge_base}")
            logger.error(f"  Level: {level}")
            logger.exception("Full traceback:")
            logger.error("="*80)
            raise
    def handle_comprehensive_doubts(self, knowledge_base: str, current_level: str):
        """Production-grade doubt clearing"""
        console.print("\n🆘 [bold red]EXPERT TECHNICAL SUPPORT[/bold red]")
        console.print(f"[cyan]🔒 Context Locked: {knowledge_base.title()} | Level: {current_level}[/cyan]")
        console.print("[dim]💭 Ask production-level doubts ('back' to return)[/dim]\n")
        
        while True:
            doubt = Prompt.ask("[bold yellow]❓ TECHNICAL DOUBT[/bold yellow]").strip()
            if doubt.lower() in ['back', 'return', 'menu']:
                break
            
            console.print("[dim]🔍 Searching knowledge base...[/dim]")
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
        """Comprehensive technical doubt resolution"""
        logger.info("="*80)
        logger.info("ANSWERING COMPREHENSIVE DOUBT")
        logger.info(f"  Knowledge Base: {knowledge_base}")
        logger.info(f"  Doubt: {doubt[:100]}..." if len(doubt) > 100 else f"  Doubt: {doubt}")
        logger.info("="*80)
        
        logger.info("Retrieving relevant content for doubt resolution...")
        docs = retrieve_training_content.invoke({
            "knowledge_base": knowledge_base,
            "level": "advanced",
            "topic": doubt
        })
        logger.info(f"Retrieved {len(docs)} characters of context documents")
        
        prompt = ChatPromptTemplate.from_template("""
        Resolve **production-critical doubt** using ONLY {knowledge_base}:
        
        ❓ **CRITICAL ISSUE**: {doubt}
        📚 **ENTERPRISE CONTEXT** (10 docs): {docs}
        
        **PRODUCTION RESOLUTION FORMAT**:
        1. **Immediate Answer** (1 sentence)
        2. **Root Cause Analysis** (technical mechanism)
        3. **COMPLETE MML WORKFLOW**
           ```
           Diagnostic → Fix → Verify → Rollback
           ```
        4. **KPI IMPACT ASSESSMENT**
        5. **ESCALATION MATRIX** (if unresolvable)
        6. **PREVENTION MEASURES**
        7. **PDF REFERENCE** (exact page)
        8. **Follow-up question**

        RESPONSE:""")
        
        logger.info("Building prompt chain for doubt resolution")
        chain = prompt | LLM | StrOutputParser()
        
        prompt_vars = {"knowledge_base": knowledge_base, "doubt": doubt, "docs": docs}
        logger.info("="*80)
        logger.info("SENDING DOUBT RESOLUTION PROMPT TO LLM")
        logger.info(f"  Knowledge Base: {knowledge_base}")
        logger.info(f"  Doubt length: {len(doubt)} characters")
        logger.info(f"  Context docs length: {len(docs)} characters")
        logger.info("="*80)
        
        try:
            logger.info("Invoking LLM chain for doubt resolution...")
            result = chain.invoke(prompt_vars)
            logger.info("="*80)
            logger.info("DOUBT RESOLUTION RESPONSE RECEIVED")
            logger.info(f"  Response length: {len(result)} characters")
            logger.debug(f"  Response preview (first 200 chars): {result[:200]}...")
            logger.info("="*80)
            return result
        except Exception as e:
            logger.error("="*80)
            logger.error("DOUBT RESOLUTION LLM INVOCATION FAILED")
            logger.error(f"  Error: {str(e)}")
            logger.error(f"  Knowledge Base: {knowledge_base}")
            logger.error(f"  Doubt: {doubt}")
            logger.exception("Full traceback:")
            logger.error("="*80)
            raise
    
    def run(self):
        """Main enterprise training platform"""
        console.print("\n[bold green]🎓 ENTERPRISE TELECOM TRAINING PLATFORM v2.0[/bold green]")
        console.print("[dim]Press Ctrl+C to exit at any time[/dim]\n")
        
        try:
            while True:
                choice = self.show_welcome_dashboard()
                
                if choice == "quit":
                    console.print("\n[bold green]🎓 TRAINING SESSION COMPLETE![/bold green]")
                    console.print("🚀 [yellow]Mastered:[/] MML Commands | Alarm Handling")
                    console.print("📚 [dim]Bookmark this coach for ongoing reference![/dim]")
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