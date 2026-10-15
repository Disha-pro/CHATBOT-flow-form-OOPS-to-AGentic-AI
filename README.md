AI ENGINEERING LEARNING ROADMAP
FROM PYTHON OOP TO LANGGRAPH
==============================================

START
  |
  v
+------------------------------------------------------+
| STAGE 1: PYTHON PROGRAMMING FOUNDATION               |
+------------------------------------------------------+
  |
  +-- Python execution and syntax
  |
  +-- Variables and data types
  |
  +-- Strings, Lists, Tuples, Sets, Dictionaries
  |
  +-- Conditional statements
  |      |-- if / elif / else
  |
  +-- Loops
  |      |-- for / while
  |
  +-- Functions
  |      |-- def
  |      |-- parameters / arguments
  |      |-- return
  |      |-- scope
  |
  +-- List comprehensions
  |
  +-- Exception handling
  |      |-- try / except / finally
  |      |-- raise
  |
  +-- File handling
  |      |-- open / read / write
  |      |-- with statement
  |
  +-- JSON
  |      |-- dumps / loads
  |      |-- dump / load
  |
  +-- Modules and packages
  |      |-- import
  |      |-- pip
  |      |-- virtual environments
  |
  v
+------------------------------------------------------+
| STAGE 2: OBJECT-ORIENTED PROGRAMMING (OOP)           |
+------------------------------------------------------+
  |
  +-- Class
  +-- Object
  +-- Attributes
  +-- Methods
  +-- self
  +-- __init__
  +-- Inheritance
  +-- Encapsulation
  +-- Abstraction
  +-- Polymorphism
  |
  +-- Why OOP matters
  |      |
  |      +-- SDK clients are objects
  |      +-- Document is a class
  |      +-- ChatGroq is a class
  |      +-- StateGraph is a class
  |      +-- Vector stores expose methods
  |
  v
+------------------------------------------------------+
| STAGE 3: APIs AND LLM FOUNDATIONS                    |
+------------------------------------------------------+
  |
  +-- HTTP requests and responses
  |      |-- GET / POST
  |      |-- headers / body
  |      |-- status codes
  |
  +-- API keys and environment variables
  |
  +-- Groq SDK
  |      |-- client
  |      |-- chat completions
  |      |-- model
  |      |-- temperature
  |      |-- messages
  |
  +-- LLM basics
  |      |-- tokens
  |      |-- context window
  |      |-- system / user / assistant messages
  |      |-- hallucination
  |
  +-- Prompt engineering
  |      |-- instructions
  |      |-- context
  |      |-- output format
  |
  +-- Pydantic
  |      |-- BaseModel
  |      |-- Field
  |      |-- Literal
  |      |-- structured output
  |
  v
+------------------------------------------------------+
| STAGE 4: LANGCHAIN                                   |
+------------------------------------------------------+
  |
  +-- LangChain framework
  |
  +-- ChatGroq model wrapper
  |
  +-- ChatPromptTemplate
  |
  +-- LCEL
  |      |-- prompt | llm
  |      |-- chain.invoke()
  |
  +-- Document
  |      |-- page_content
  |      |-- metadata
  |
  +-- Document loaders
  |      |-- TextLoader
  |      |-- PyMuPDFLoader
  |      |-- UnstructuredPDFLoader
  |
  +-- Text splitters
  |      |-- RecursiveCharacterTextSplitter
  |      |-- chunk_size
  |      |-- chunk_overlap
  |
  +-- Embeddings
  |      |-- HuggingFaceEmbeddings
  |      |-- sentence-transformers
  |
  +-- Vector stores
  |      |-- InMemoryVectorStore
  |      |-- Pinecone
  |
  +-- Retrievers
  |      |-- similarity search
  |      |-- retriever.invoke()
  |
  v
+------------------------------------------------------+
| STAGE 5: VECTOR SEARCH AND TEXT RAG                  |
+------------------------------------------------------+
  |
  +-- Document ingestion
  |
  +-- Text extraction
  |
  +-- Chunking
  |
  +-- Embedding generation
  |
  +-- Vector storage
  |
  +-- Similarity search
  |      |-- cosine similarity
  |      |-- nearest neighbors
  |      |-- ANN
  |      |-- HNSW / IVF / PQ (conceptual)
  |
  +-- Context construction
  |
  +-- Prompt + retrieved context
  |
  +-- Groq answer generation
  |
  +-- Source metadata
  |
  +-- Missing-information handling
  |
  v
+------------------------------------------------------+
| STAGE 6: MULTIMODAL RAG                              |
+------------------------------------------------------+
  |
  +-- PDF processing
  |      |-- PyMuPDF
  |      |-- PyMuPDFLoader
  |      |-- UnstructuredPDFLoader
  |
  +-- Text extraction
  |
  +-- Table extraction
  |      |-- page.find_tables()
  |
  +-- Page rendering
  |      |-- page.get_pixmap()
  |
  +-- Image processing
  |      |-- PNG
  |      |-- Base64
  |
  +-- Vision-language models
  |      |-- image -> description
  |
  +-- OCR
  |      |-- pytesseract
  |      |-- scanned PDF fallback
  |
  +-- Metadata
  |      |-- page
  |      |-- source
  |      |-- content_type
  |
  +-- Unified document collection
  |      |-- text chunks
  |      |-- table descriptions
  |      |-- image descriptions
  |
  +-- Embed -> Retrieve -> Answer
  |
  v
+------------------------------------------------------+
| STAGE 7: GRAPHRAG                                    |
+------------------------------------------------------+
  |
  +-- Knowledge graphs
  |
  +-- Entities / Nodes
  |
  +-- Relationships / Edges
  |
  +-- Properties
  |
  +-- Graph triples
  |      |-- Subject / Predicate / Object
  |
  +-- NetworkX
  |      |-- DiGraph
  |      |-- add_node
  |      |-- add_edge
  |      |-- edges(data=True)
  |
  +-- Neo4j fundamentals
  |      |-- graph database
  |      |-- Cypher
  |      |-- CREATE / MERGE
  |      |-- MATCH / WHERE / RETURN
  |
  +-- Graph traversal
  |
  +-- Multi-hop retrieval
  |
  +-- Graph evidence -> LLM
  |
  v
+------------------------------------------------------+
| STAGE 8: RAG AND GRAPHRAG EVALUATION                 |
+------------------------------------------------------+
  |
  +-- Retrieval metrics
  |      |-- Precision@k
  |      |-- Recall@k
  |      |-- Contextual Precision
  |      |-- Contextual Recall
  |      |-- Contextual Relevancy
  |
  +-- Generation metrics
  |      |-- Faithfulness
  |      |-- Groundedness
  |      |-- Answer Relevancy
  |      |-- Hallucination
  |
  +-- LLM-as-a-Judge
  |
  +-- DeepEval
  |
  +-- RAGAS
  |
  +-- G-Eval
  |
  +-- GraphRAG metrics
  |      |-- Entity Precision / Recall / F1
  |      |-- Relationship Precision / Recall / F1
  |      |-- Graph Retrieval Recall
  |      |-- Multi-hop Accuracy
  |
  v
+------------------------------------------------------+
| STAGE 9: OBSERVABILITY                               |
+------------------------------------------------------+
  |
  +-- Python logging
  |
  +-- Request IDs
  |
  +-- Latency measurement
  |      |-- time.perf_counter()
  |
  +-- Retrieval and generation timings
  |
  +-- Token usage
  |
  +-- Logs / Traces / Metrics
  |
  +-- LangSmith
  +-- Langfuse
  +-- Arize Phoenix
  |
  v
+------------------------------------------------------+
| STAGE 10: LANGGRAPH                                  |
+------------------------------------------------------+
  |
  +-- TypedDict state
  |
  +-- StateGraph
  |
  +-- Nodes
  |
  +-- START / END
  |
  +-- add_node()
  |
  +-- add_edge()
  |
  +-- add_conditional_edges()
  |
  +-- compile()
  |
  +-- invoke()
  |
  +-- Conditional routing
  |
  +-- Loops
  |
  +-- Query rewriting
  |
  +-- Retry limits
  |
  +-- Tool calling
  |      |-- @tool
  |      |-- bind_tools()
  |      |-- ToolNode
  |      |-- tools_condition
  |
  +-- MessagesState
  |
  +-- Checkpointing
  |      |-- InMemorySaver
  |      |-- thread_id
  |      |-- get_state()
  |      |-- get_state_history()
  |
  +-- Human-in-the-loop
         |-- interrupt()
         |-- Command(resume=...)
  |
  v
+------------------------------------------------------+
| CURRENT POSITION                                     |
| LangGraph fundamentals covered                      |
| Independent implementation still developing         |
+------------------------------------------------------+
  |
  v
+------------------------------------------------------+
| NEXT: AGENTIC AI + CORTEXRAG PROJECT                 |
+------------------------------------------------------+
  |
  +-- Agent architecture
  +-- Tool selection and execution
  +-- Evidence grading
  +-- Self-correction
  +-- Query rewriting
  +-- Grounding verification
  +-- Failure recovery
  +-- Evaluation and tracing
  +-- FastAPI
  +-- Docker
  +-- Deployment
  |
  v
PORTFOLIO-READY APPLICATION
