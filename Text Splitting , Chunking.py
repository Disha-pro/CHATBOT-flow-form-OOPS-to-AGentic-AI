Chunking is the process of splitting a large document into smaller pieces of text called chunks ,
so they can be embedded, stored, searched, and retrieved efficiently.

  #Suppose you have a 100-page PDF.
We generally don't create just one embedding for the entire PDF:
100-page PDF
      ↓
ONE embedding ❌

Instead:
100-page PDF
      ↓
Text Splitter
      ↓
Chunk 1
Chunk 2
Chunk 3
Chunk 4
...
      ↓
Embedding for each chunk

Then the retriever can find the specific pieces relevant to the user's question.

#Why not embed the entire document?
Imagine a banking policy document contains:
Page 1–10    → Introduction
Page 11–20   → Personal Loans
Page 21–30   → Credit Cards
Page 31–40   → Home Loans
Page 41–50   → Risk Policy

User asks:
"What is the home loan eligibility policy?"

We don't need the entire document.
Ideally retrieval gives us something like:
Chunk 31
Chunk 32
Chunk 33

containing the home-loan information.
#So:
Question
   ↓
Find relevant chunks
   ↓
Give chunks to LLM
   ↓
Generate grounded answer

#Two extremely important parameters
chunk_size
chunk_overlap

1#Chunk size
Chunk size controls approximately how much text goes into each chunk, according to the splitters length function.

#Suppose we simplify it to words and have:
RAG retrieves relevant information before generating an answer.

#Imagine:
chunk_size = 4

#Conceptually:
Chunk 1:
RAG retrieves relevant information

Chunk 2:
before generating an answer

Real splitters may count characters or tokens rather than words, so always know what your splitter length function measures.

2#chunk_overlap
#Now consider this sentence:
Chunk overlap repeats a portion of neighboring chunks to reduce context loss at chunk boundaries.

Agentic RAG retrieves documents and evaluates their relevance before generation.

Suppose a split occurs badly:
Chunk 1:
Agentic RAG retrieves documents and evaluates

Chunk 2:
their relevance before generation
------
Some semantic context crosses the boundary.
Overlap lets part of one chunk appear again in the next.
Conceptually:
Chunk 1:
Agentic RAG retrieves documents and evaluates
                                  ↑
                                  │ overlap

Chunk 2:
documents and evaluates their relevance before generation

#Why not use huge overlap?
Because then you duplicate lots of information.
For example:
chunk_size = 1000
chunk_overlap = 900

would make neighboring chunks extremely similar.
Consequences can include:
- unnecessary storage,
- redundant embeddings,
- repetitive retrieval results,
- wasted tokens.
So overlap should be useful, not excessive.

  **************************IMP*************************************
RecursiveCharacterTextSplitter
  #A very common LangChain splitter is:
from langchain_text_splitters import RecursiveCharacterTextSplitter

#If needed:
!pip install -q langchain-text-splitters

Then:
text_splitter = RecursiveCharacterTextSplitter(   
  chunk_size=1000,   
  chunk_overlap=150)
#You may recognize those numbers: theyre also close to what youve used in your larger Agentic RAG project.


#Why "recursive"?
The splitter tries to preserve sensible text boundaries where possible, typically preferring larger separators before falling back to smaller ones.
Conceptually it tries boundaries such as:
paragraph
    ↓
newline
    ↓
space
    ↓
character

rather than blindly cutting every piece in the middle of text.

#Splitting Langchain Documents

documents = loader.load()
chunks = text_splitter.split_documents(documents)
#Now:
documents
    ↓
Text Splitter
    ↓
chunks
#And importantly, each chunk is itself typically a:
Document

#So:
chunks[0].page_content  #contains the chunk text.

chunks[0].metadata     #contains metadata inherited from the source document. That's important for citations later.

#FLOW
rag_notes.txt
      ↓
 TextLoader
      ↓
documents
[List of Document objects]
      ↓
RecursiveCharacterTextSplitter
      ↓
chunks
[List of smaller Document objects]
