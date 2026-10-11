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

Upload a sample PDF:
from google.colab import filesuploaded = files.upload()

Then load it:
from langchain_community.document_loaders import PyMuPDFLoader
pdf_path = next(iter(uploaded))
loader = PyMuPDFLoader(pdf_path)
documents = loader.load() #What does .load() return?
Usually, in its default page-oriented
print("Total page documents:", len(documents))

#Inspect the first page:
first_page = documents[0]

print("CONTENT:")
print(first_page.page_content[:500])

print("\nMETADATA:")
print(first_page.metadata)

