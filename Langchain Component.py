1#Documents in Langchain 
A Document is LangChain's standard data structure for representing a piece of
text together with metadata describing that text.

  from langchain_core.documents import Document

                External knowledge
                       ↓
User → Retrieval → Context → Prompt → LLM

#Create one
document = Document(
    page_content="RAG combines retrieval with language model generation.", #That's the knowledge we eventually embed and retrieve.
    metadata={ #Metadata tells us where the information came from.
#This becomes extremely important for citations.
        "source": "rag_notes.txt",
        "page": 1
    }
)

Document
│
├── page_content
│      ↓
│   actual textual information
│
└── metadata
       ↓
    information ABOUT that text

#Real-life analogy
Imagine a page from a textbook.
The actual paragraph is:
"Embeddings are numerical vector representations..."

That's:
page_content


But attached to it you know:
Book: AI Engineering
Chapter: Vector Search
Page: 124

That's:
metadata


So:
Document
│
├── CONTENT
│   "Embeddings are numerical..."
│
└── METADATA
    source = AI Engineering
    chapter = Vector Search
    page = 124

#EXERCISE

from langchain_core.documents import Document
document = Document(
    page_content= "RAG is Retrival augumeted generation mainly have multiple types",
    metadata={
        "source":"rag_notes_txt",
        "page":11
    }
)

document1= Document(
    page_content="Agentic AI is autonous ai which have components with langaraph,cew ai,autogen",
    metadata={
        "source":"agentic_notes.txt",
        "page":23}
)

documents = [document, document1]

for doc in documents:   #IN LOOP 
    print("Content:", doc.page_content)
    print("Source:", doc.metadata["source"])
    print("Page:", doc.metadata["page"])
    print()

---------------------------------------------------------------------------------------------------------------------------
2#******************************************DOCUMENT LOADERS**************************************************
A Document Loader is a component that reads data from an external source and 
converts it into LangChain Document objects.

#But imagine a real PDF containing 100 pages.
Obviously we won't type:
Document(...)Document(...)Document(...)


100 times.
That's where a Document Loader comes in.

#source 
TXT
PDF
HTML/web page
DOCX
CSV
...

External file
     ↓
Document Loader
     ↓
LangChain Document objects
     ↓
page_content + metadata

This is an important distinction:
Document = data structure
Document Loader = mechanism that creates/populates those Document objects from a source.

#Real-life analogy
Think of an airport.
Your raw documents are passengers arriving from different places:
PDF ──────┐
TXT ──────┤
HTML ─────┤
DOCX ─────┘
          ↓
        LOADER
          ↓
standard LangChain Documents

The inputs may have different formats, but downstream RAG components want a standardized representation.

#start with .txt file
  #Suppose we have:
rag_notes.txt

#containing:
Retrieval-Augmented Generation combines retrieval
with language model generation.

A retriever searches an external knowledge base
for information relevant to the user's query.

The retrieved context is then provided to the LLM.

#For many community integrations, we'll use:
  !pip install -q langchain-community

from langchain_community.document_loaders import TextLoader

#create the loader:
loader = TextLoader("rag_notes.txt")

TextLoader → class
loader → object

"rag_notes.txt" → file the object should load

#then:
documents = loader.load()   #.load()-It normally returns a list of Document objects.
print(type(documents))

loader.load()
     ↓

[
   Document(...)
]
#therefore
documents[0].page_content  #accesses the text.
documents[0].metadata #access the metadata

#Why a list?
Because some loaders can produce multiple documents.
For example, a PDF loader may represent pages separately:
PDF
 │
 ├── Page 1 → Document
 ├── Page 2 → Document
 ├── Page 3 → Document
 └── Page 4 → Document


