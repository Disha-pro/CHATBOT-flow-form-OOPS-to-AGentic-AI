#Multimodal RAG
Uses multiple modalities such as text, tables and images.
PDF → Extraction → Multimodal representation → Retrieval

One important distinction: extracting text from a PDF is not automatically multimodal RAG. A genuinely multimodal pipeline must preserve and use non-text information, such as images, diagrams or visual table structure, when that information is needed.

  #PDF loaders you must know
*Loader / library                   	*Primary use	Key                                                         * limitation
PyPDFLoader	                        General PDF text extraction and page metadata	                           Scanned content requires OCR
PyMuPDFLoader                      	Fast PDF text extraction with page-aware handling                       	Visual content needs additional processing
UnstructuredPDFLoader              	Layout-aware extraction of document elements	                            More dependencies and processing overhead
PyMuPDF (fitz)                     	Direct PDF processing, page rendering, image extraction, geometry	        Lower-level API requires more coding
OCR tools	                          Extract text from scanned pages/images	                                  Recognition errors and layout loss

!pip install -q langchain-community pymupdf

#Upload a sample PDF:
from google.colab import files
uploaded = files.upload()

#Then load it:
from langchain_community.document_loaders import PyMuPDFLoader
pdf_path = next(iter(uploaded))
loader = PyMuPDFLoader(pdf_path)
documents = loader.load() 

#What does .load() return?
#Usually, in its default page-oriented
print("Total page documents:", len(documents))

#Inspect the first page:
first_page = documents[0]

print("CONTENT:")
print(first_page.page_content[:500])

print("\nMETADATA:")
print(first_page.metadata)

#PyMuPDF vs PyMuPDFLoader — an important difference
PyMuPDFLoader is a LangChain integration that converts PDF content into LangChain Document objects.
PyMuPDF is the underlying PDF-processing library that gives you more direct control.

#Example:

import pymupdf

pdf = pymupdf.open(pdf_path) #opens the PDF.

print("Total pages:", len(pdf))  

page = pdf[0] #accesses the first page.

text = page.get_text() #extracts text from that page.

print(text[:500])

pdf.close() #releases the document.

***************************OCR (Optical Character Recognition) converts visible characters in an image or scan into machine-readable text.

print("Pages:", len(documents))

for i, doc in enumerate(documents):
    print(f"\nPAGE {i + 1}")
    print("Characters:", len(doc.page_content))
    print("Source:", doc.metadata.get("source"))
    print("PDF page index:", doc.metadata.get("page"))

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**********************************UnstructuredPDFLoader, Layout Detection & OCR***********************************

Our goal today: Understand how to preserve document structure before converting content into embeddings.


PyMuPDFLoader                            vs                                              UnstructuredPDFLoader
Feature                              	PyMuPDFLoader	                                     UnstructuredPDFLoader
Primary strength                    	Fast, page-oriented PDF extraction                	Layout-aware document partitioning
Text extraction                      	Yes	                                                Yes
Headings and element types	          Limited by default                                 	Can identify titles and other elements
Tables	                              Requires additional handling	                      Supports table extraction with appropriate strategy/settings
Scanned PDFs	                        Requires OCR configuration or separate OCR	        Can use OCR-based processing
Images	                              Extraction support depends on configuration        	Can extract image elements with appropriate settings
Dependencies	                        Relatively  lightweight                            	Heavier
Best fit                             	Straightforward digital PDFs                      	Complex document layouts

#Neither loader is universally superior.
#. What is Unstructured?
Unstructured is a document-processing ecosystem that partitions files into meaningful elements.
Instead of treating an entire PDF page as one large text block, it can identify elements such as:
PDF
 ├── Title
 ├── NarrativeText
 ├── Table
 ├── ListItem
 └── Image


!pip install -q "unstructured[pdf]" langchain-community
#The Unstructured PDF stack may require system dependencies such as Poppler and Tesseract, depending on the strategy and runtime.
!apt-get update -qq
!apt-get install -y -qq poppler-utils tesseract-ocr

from google.colab import files
uploaded=files.upload()
#load the pdf
pdf_path = next(iter(uploaded))

#Now:
from langchain_community.document_loaders import UnstructuredPDFLoader

loader = UnstructuredPDFLoader(
    pdf_path,
    mode="elements", #requests separate LangChain Document objects for detected elements, rather than combining the document into one text object.
    strategy="fast" #prioritizes faster processing of PDFs with extractable text. It is not the appropriate choice when you need full layout-aware table/image extraction.
) #For complex layouts, we'll examine strategy="hi_res".

documents = loader.load()

print("Total elements:", len(documents))

#RUN
for i, doc in enumerate(documents[:10]):
    print(f"\nELEMENT {i + 1}")
    print("Type:", doc.metadata.get("category"))
    print("Page:", doc.metadata.get("page_number"))
    print("Content:", doc.page_content[:200])

#The actual categories depend on the PDF, extraction strategy and installed Unstructured version.
Notice an important difference:
PyMuPDFLoader commonly uses a zero-based page index, while Unstructured element metadata commonly uses a one-based page_number.
Always normalize page references before generating user-facing citations.

#What changes with high-resolution extraction?
For complex PDF documents, Unstructured provides a hi_res strategy that uses document-layout analysis.

loader = UnstructuredPDFLoader(
    pdf_path,
    mode="elements",
    strategy="hi_res",
    infer_table_structure=True
)

elements = loader.load()

#This may be substantially slower and can require downloading layout-analysis models.
With suitable configuration, detected tables can include an HTML representation in metadata, which is useful for preserving rows and columns.

#for example:
tables = [
    doc for doc in elements
    if doc.metadata.get("category") == "Table"
]

print("Tables detected:", len(tables))

for table in tables[:2]:
    print("TEXT:", table.page_content[:500])
    print("HTML:", table.metadata.get("text_as_html"))

#A structured table representation can preserve relationships that plain text may flatten.
However, table detection is not guaranteed, and HTML metadata availability depends on the extraction configuration.

*****************************OCR*********************************************
OCR stands for Optical Character Recognition.
It converts visible characters in scanned pages or images into machine-readable text.

 loader = UnstructuredPDFLoader(
    pdf_path,
    mode="elements",
    strategy="ocr_only"
)

ocr_documents = loader.load() 

Use this when OCR-based text extraction is appropriate. OCR does not necessarily preserve complex layout, table structure or mathematical notation accurately.


  Incoming PDF
     ↓
Inspect text and layout
     ↓
Digital text available?
     ├── Yes → PyMuPDF / fast extraction
     │
     └── No → OCR
                  ↓
          Complex tables/images?
                  ↓
          Layout / vision processing
                  ↓
          Normalize content + metadata
                  ↓
          Embeddings + Vector Database

#how to connect to your multimodel rag
{
    "source": "attention_paper.pdf",
    "page": 3,
    "content_type": "table",
    "section": "Model Architecture"
}

#For visual content, we'll also learn how to generate a vision-model description and associate it with the original image.
That will allow queries such as:
"Explain the Transformer architecture shown in the diagram."

A text-only retriever might miss visual information. A multimodal pipeline can retrieve a representation of the figure and use the original visual evidence during answer generation

#EXAMPLE
from collections import Counter

categories = Counter(
    doc.metadata.get("category", "Unknown")
    for doc in documents
)

for category, count in categories.items():
    print(category, ":", count)

loader = UnstructuredPDFLoader(
    pdf_path,
    mode="elements",
    strategy="fast"
)
fast_stra = loader.load()
#inspect
for i, doc in enumerate(documents[:10]):
    print(f"\nELEMENT {i + 1}")
    print("Type:", doc.metadata.get("category"))
    print("Page:", doc.metadata.get("page_number"))
    print("Content:", doc.page_content[:200])

---------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
*****************************************TABLE & IMAGE EXTRACTION*********************************************

  #load
  from google.colab import files

uploaded = files.upload()
pdf_path = next(iter(uploaded))

import pymupdf

pdf = pymupdf.open(pdf_path)#opens the pdf
page = pdf[0] # selects the first page

print(page.get_text()[:1000]) extracts machine relatable text.

#Extract the table
tables = page.find_tables() #detects table structures and extract() returns rows and cells. You should look for the Personal Loan, Vehicle Loan and Home Loan rows.

print("Tables found:", len(tables.tables))

for table in tables.tables:
    for row in table.extract():
        print(row)


#Extract Visual content
A critical distinction: embedded images and vector-drawn diagrams are different PDF objects. The workflow diagram in this practice PDF is vector-drawn, so it may not appear in page.get_images().
For a robust approach, render the whole page:

pix = page.get_pixmap(dpi=150)

pix.save("page_1.png")

This converts the page into an image, including the diagram, tables and text.
You can then provide the rendered image to a vision-capable model to describe the workflow. That is a foundation of multimodal document understanding.

#Line 1: pix = page.get_pixmap(dpi=150)
- page is the first PDF page, selected earlier using pdf[0].
- get_pixmap() renders the PDF page into a raster image (pixels).
- dpi means dots per inch, which controls the rendering resolution.
- 150 means 150 pixels per inch at the PDF page's physical scale.
- pix is a variable holding the resulting PyMuPDF Pixmap object.

Higher DPI generally improves the visibility of small text, but increases memory, image size and processing cost. It does not automatically guarantee better OCR accuracy.

#Line 2: pix.save("page_1.png")
- pix.save() writes the rendered image to a file.
- "page_1.png" is the output filename.
- The file is saved in your Colab working directory.
  
#To display img
  from IPython.display import Image, display

display(Image(filename="page_1.png"))

------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------
***********************************Convert Tables and Images into RAG Knowledge***********************************************

PDF
 ├── Text extraction
 ├── Table extraction
 └── Image rendering
          ↓
   Vision model description
          ↓
   Normalize into Documents
          ↓
   Hugging Face Embeddings
          ↓
       Vector Store
          ↓
   Retriever → Groq LLM

1#Convert your extracted tbale into readable text
table = tables.tables[0] #selects the first detected table

rows = table.extract()#returns its content as a list of rows

headers = rows[0] #selects the header row.

data_rows = rows[1:]

#rows[1:] selects every row after the header.
Now convert the table into searchable sentences:

table_texts = []

for row in data_rows:
    record = dict(zip(headers, row))#pairs each column name with its corresponding cell.
#dict converts those pairs into a dictionary.
    text = (
        f"Product: {record['Product']}. "
        f"Minimum income: {record['Minimum income']}. "
        f"Minimum score: {record['Minimum score']}. "
        f"Maximum tenure: {record['Maximum tenure']}."
    )

    table_texts.append(text)
#adds each product's structured description to a list.
for text in table_texts:
    print(text)

#convert table records into Langchian document
from langchain_core.documents import Document

table_documents = []

for text in table_texts:
    doc = Document(
        page_content=text,
        metadata={
            "source": pdf_path,
            "page": 1,
            "content_type": "table"
        }
    )

    table_documents.append(doc)
  #Here, page_content stores the text that will be embedded, while metadata stores information about its origin.

3#Generate a description of the diageam using a vison model
import os
import base64#Some vision APIs accept images as Base64 data URLs rather than local file paths.
from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

with open("page_1.png", "rb") as image_file:
    image_bytes = image_file.read()

image_base64 = base64.b64encode(image_bytes).decode("utf-8")

What does this mean?
- rb opens the image in read-binary mode.
- .read() loads the image bytes.
- base64.b64encode() converts binary data into Base64-encoded bytes.
- .decode("utf-8") converts those encoded bytes into a Python string.

#Now call a vision capable model
  vision_response = client.chat.completions.create(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Describe the workflow diagram in this image. "
                        "Identify the stages and their sequence. "
                        "Do not invent missing details."
                    )
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": (
                            "data:image/png;base64,"
                            + image_base64
                        )
                    }
                }
            ]
        }
    ],
    temperature=0
)

image_description = vision_response.choices[0].message.content

print(image_description)

4#store the visual description as Document
image_document = Document(
    page_content=image_description,
    metadata={
        "source": pdf_path,
        "page": 1,
        "content_type": "image_description",
        "image_path": "page_1.png"
    }
)

This creates a searchable textual representation of visual content.
It is a vision-to-text multimodal RAG approach: the image is interpreted by a vision model, and the resulting description is embedded as text. This differs from a system that stores native image embeddings and performs cross-modal image retrieval.


  #Combine and index the knowledge
  all_documents = table_documents + [image_document]

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = InMemoryVectorStore(
    embedding=embeddings
)

vector_store.add_documents(all_documents)

retriever = vector_store.as_retriever(
    search_kwargs={"k": 3}
)

#Test multimodel retrival
questions = [
    "What is the minimum credit score for a vehicle loan?",
    "Which loan product has the longest maximum tenure?",
    "Explain the five-stage workflow shown in the diagram."
]

for question in questions:
    print("\nQUESTION:", question)

    docs = retriever.invoke(question)

    for doc in docs:
        print("Type:", doc.metadata["content_type"])
        print("Content:", doc.page_content[:300])
        print("---")

--------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------
***********************************OCR FALLBACK AND COMPLETE MULTIMODEL RAG*******************************************************

1#why OCR fallback matters
Suppose a bank uploads 100 loan documents. Some are digital PDFs, some are scanned forms, and others contain a mixture of both.
                  PDF Page
                     ↓
            Extract digital text
                     ↓
             Enough usable text?
                /          \
              Yes           No
               ↓             ↓
          Keep text       Render page
                             ↓
                            OCR
                             ↓
                   Extracted page text
                \           /
                 ↓         ↓
                  Normalize
                     ↓
             Document + Metadata
                     ↓
              RAG Retrieval

We will use PyMuPDF + Tesseract OCR.

2#install OCR dependencies
!apt-get install -y -qq tesseract-ocr
!pip install -q pytesseract pillow pymupdf

3#build an OCR fallback funtion

import pymupdf
import pytesseract

from PIL import Image
from io import BytesIO

def extract_page_text(page):

    # First attempt: extract digital text
    text = page.get_text().strip()

    # Heuristic: sufficiently long text
    if len(text) >= 50:
        return text, "digital"

    # Fallback: render the page
    pix = page.get_pixmap(dpi=200)

    # Convert Pixmap to PIL Image
    image = Image.open(
        BytesIO(pix.tobytes("png"))
    )

    # Apply OCR
    ocr_text = pytesseract.image_to_string(
        image,
        lang="eng"
    )

    return ocr_text.strip(), "ocr"


Code                                                    	Meaning
page.get_text()	                                         Extracts machine-readable PDF text
.strip()	                                                Removes leading/trailing whitespace
len(text) >= 50                                          	A simple heuristic for deciding whether to skip OCR
page.get_pixmap(dpi=200)	                                Renders the PDF page at 200 DPI
pix.tobytes("png")	                                      Converts the rendered image to PNG bytes
BytesIO(...)	                                            Treats those bytes like an in-memory file
Image.open(...)                                          	Opens the image using Pillow
pytesseract.image_to_string()                            	Recognizes text from the image
return text, digital	                                  Returns extracted text and the extraction method


Production warning: The 50-character threshold is only a learning heuristic. A page may contain 200 extractable characters and still have an important scanned table or figure. Production systems need page-layout inspection and content-quality checks.


  4#Process the whole pdf with OCR fallback
from langchain_core.documents import Document

pdf = pymupdf.open(pdf_path)

ocr_documents = []

for page_index, page in enumerate(pdf): #enumerate() gives you both the index and the item.

    text, method = extract_page_text(page)

    if not text:
        continue

    doc = Document(
        page_content=text,
        metadata={
            "source": pdf_path,
            "page": page_index + 1,
            "content_type": "text",
            "extraction_method": method
        }
    )

    ocr_documents.append(doc)

pdf.close()

print("Extracted pages:", len(ocr_documents))

#for index, value in enumerate(["A", "B", "C"]): #for enumerte
    print(index, value)

5#Combine OCR,table and visual document
table_documents — structured banking loan records.
image_document — a vision-generated description of the diagram.

all_documents = (
    ocr_documents
    + table_documents
    + [image_document]
)

print("Total documents:", len(all_documents))

Production note: This approach may duplicate information because the page text also contains table labels and values. Later, we can remove duplicated table regions, preserve bounding boxes and apply content-aware chunking.

6#Chunk and index the documents
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=80
)

chunks = splitter.split_documents(all_documents)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = InMemoryVectorStore(
    embedding=embeddings
)

vector_store.add_documents(chunks)

retriever = vector_store.as_retriever(
    search_kwargs={"k": 4}
)

#Why 500 and 80?
- chunk_size=500: targets chunks of approximately 500 characters.
- chunk_overlap=80: preserves up to approximately 80 characters of context between adjacent chunks.
These are starting values, not production-optimized settings.
Also note that RecursiveCharacterTextSplitter uses character counts by default, not token counts.


7#Connect the multimodel retriver to Groq
  from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are a document question-answering assistant.

        Answer using only the supplied context.
        If the answer is not supported, say you don't know.

        Preserve numerical values accurately.
        Do not invent information.

        Context:
        {context}
        """
    ),
    ("human", "{question}")
])

#Build the final multimodel RAG funtion
def ask_multimodal_rag(question):

    # Retrieve relevant chunks
    docs = retriever.invoke(question)

    # Prepare context with source references
    context = "\n\n".join(
        f"Source: {doc.metadata.get('source')}\n"
        f"Page: {doc.metadata.get('page')}\n"
        f"Type: {doc.metadata.get('content_type')}\n"
        f"Content: {doc.page_content}"
        for doc in docs
    )

    # Generate answer
    chain = prompt | llm

    response = chain.invoke({
        "context": context,
        "question": question
    })

    return {
        "answer": response.content,
        "sources": [
            doc.metadata for doc in docs
        ],
        "retrieved_count": len(docs)
    }

#Test the complete pipeline
questions = [
    "What is the minimum credit score for a vehicle loan?",
    "Which loan product has the longest tenure?",
    "Explain the five stages shown in the workflow diagram."
]

for question in questions:

    result = ask_multimodal_rag(question)

    print("\nQUESTION:", question)
    print("ANSWER:", result["answer"])
    print("RETRIEVED:", result["retrieved_count"])
    print("SOURCES:", result["sources"])




******************************************************Multimodal RAG milestone
Ready for testing

- Digital PDF text extraction and OCR fallback
- Table-to-text serialization
- Vision-generated image descriptions
- Content-type and page metadata
- Embedding, retrieval and Groq answer generation
This is a learning implementation, not yet a production-hardened system. We still need evaluation, error handling, deduplication and verified citations.
