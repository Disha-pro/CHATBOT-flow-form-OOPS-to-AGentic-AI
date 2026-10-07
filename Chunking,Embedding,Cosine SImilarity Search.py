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

#EXERCISE

from langchain_community.document_loaders import TextLoader

# Create a sample rag_notes.txt file first so that it exists in the filesystem
with open("rag_notes.txt", "w", encoding="utf-8") as f:
    f.write("RAG is Retrieval-Augmented Generation. It enhances Large Language Models by retrieving relevant information from an external knowledge base.")

# Now load the file using TextLoader
loader = TextLoader("rag_notes.txt")
documents = loader.load()
print(documents)

from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=80,
    chunk_overlap=20
)

chunks=text_splitter.split_documents(documents)
print(chunks)
len(chunks)

#To print every chunk cleanly:
for i, chunk in enumerate(chunks):
    print(f"CHUNK {i + 1}")
    print("Content:", chunk.page_content)
    print("Metadata:", chunk.metadata)
    print()

#enumerate(chunks)

lets us get both:
i       → 0, 1, 2
chunk   → actual Document object

and i + 1 makes the display start at 1 instead of 0

#output will be:
CHUNK 1
RAG is Retrieval-Augmented Generation. It enhances Large Language Models by

CHUNK 2
Large Language Models by retrieving relevant information from an external

CHUNK 3
from an external knowledge base.


  -------------------------------------------------------------------------------------------------------------------------
********************************************🧠 → 🔢 Embeddings 🧠 → 🔢 **********************************
  An embedding is a numerical vector representation of data—such as text—designed so that 
semantically similar content is represented near each other in the embedding space.

Embedding converts meaning into numbers that a computer can compare mathematically.

#For example:
"I love machine learning"

could become something conceptually like:
[0.18, -0.42, 0.73, 0.11, ...]


That list of numbers is a vector.
Real embedding vectors usually contain hundreds or thousands of dimensions depending on the model.

#Why can't we just store text?
A computer can store:
What is RAG?

But for semantic retrieval, we want to answer questions like:
#Which stored chunk has a meaning closest to this question?

Embeddings make that comparison possible.

#Consider
  Sentence A:
How do I reset my password?

Sentence B:
I forgot my login password.

Sentence C:
Today the weather is hot.

#A normal keyword comparison may have limitations.
But semantically:
A ↔ B   VERY SIMILAR

A ↔ C   NOT SIMILAR

An embedding model tries to represent this **relationship numerically***.

  "reset my password"
        ↓
Embedding Model
        ↓
[0.82, 0.14, -0.37, ...]

forgot login password"
        ↓
Embedding Model
        ↓
[0.79, 0.18, -0.32, ...]

weather is hot
        ↓
Embedding Model
        ↓
[-0.11, 0.84, 0.51, ...]  #The first two vectors should be closer in the model's embedding space.


#Real-life analogy: coordinates
Think about locations:
Mumbai       → (coordinates)
Pune         → (coordinates)
London       → (coordinates)

Mumbai and Pune are geographically closer than Mumbai and London.
Embedding space is somewhat analogous, except the coordinates represent learned semantic features, not latitude and longitude.

#How embeddings work in RAG

  #suppose your chunks are :
  Chunk 1:
RAG retrieves external information.

Chunk 2:
Python is a programming language.

Chunk 3:
Agentic RAG can evaluate retrieved evidence.

  #We create an embedding for each chunk:
  Chunk 1
 ↓
Embedding
 ↓
Vector 1

Chunk 2
 ↓
Embedding
 ↓
Vector 2

Chunk 3
 ↓
Embedding
 ↓
Vector 3

#Store those vectors in a vector database.
Later user asks:
What happens when Agentic RAG retrieves information?

#We also embed the question:
  User question
     ↓
Embedding Model
     ↓
Query Vector

  #Then Compare:
  Query Vector

   ↕ similarity

Vector 1
Vector 2
Vector 3

  The most similar vectors identify the most relevant chunks.
That's semantic search.******************IMP


*********************************CRITICAL DOSTINCTION********************************************8

  #There are two embedding operations you'll encounter frequently:

  1.embed_documents()
  2.embed_query()

  DOCUMENT CHUNKS
      ↓
embed_documents()
      ↓
vectors stored in vector DB
  ------------

  USER QUESTION
      ↓
embed_query()
      ↓
query vector used for search

#Install it 
!pip install -q langchain-huggingface sentence-transformers

#THEN
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
#Now:
vector = embeddings.embed_query("What is RAG?")
print(type(vector))
print(len(vector))
print(vector[:10])

#For this model, you should see a vector with 384 dimensions.
Something conceptually like:
<class 'list'>
384
[-0.02, 0.04, -0.01, ...]

Dont memorize the numbers.
Theyre learned numerical features.

#Now embed your actual chunks
texts = []

for chunk in chunks:
    texts.append(chunk.page_content)
vectors = embeddings.embed_documents(texts)
print(vectors)
len(chunks)
len(vector)
len(vectors[0])      #3 chunks × 384 dimensions
 print(len(vector[0]))------------->  384 : 384 means each chunk is represented by a 384-dimensional embedding vector.
       
Chunk 1 → [.....................]
Chunk 2 → [.....................]
Chunk 3 → [.....................]
-----------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------

*************************************Cosine Similarity & Semantic Search***************************************

      # We need to answer:
Which stored vector is most similar to the user's query vector?

That's where a similarity metric comes in.

#what is cosine similarity?
Cosine similarity is a mathematical measure of how similar two vectors are based on the angle between them.

  #Mathematically:
\[
\text{cosine similarity}(A,B)
=
\frac{A \cdot B}
{\|A\|\|B\|}
\]

For AI engineering, understand the purpose more than memorizing the formula.

#Real RAG example
Imagine our database contains three chunks.
Chunk 1
RAG retrieves external information before generating an answer.

Chunk 2
Python supports object-oriented programming.

Chunk 3
Agentic RAG can evaluate retrieved documents.

We embed all three:
Chunk 1 → Vector A
Chunk 2 → Vector B
Chunk 3 → Vector C

#User asks:
How does RAG retrieve information?

#We embed the question:
Question → Query Vector

#Then compare:
Query Vector ↔ Vector A = high similarity
Query Vector ↔ Vector B = low similarity
Query Vector ↔ Vector C = medium/high similarity

So the system retrieves Chunk 1, perhaps followed by Chunk 3.
Thats semantic retrieval.

#Let's actually calculate it
Use the embedding object you created in the previous lesson.
text1 = RAG retrieves information from external documents.
text2 = Retrieval augmented generation uses external knowledge.
text3 = I like eating pizza.

Create embeddings:
v1 = embeddings.embed_query(text1)
v2 = embeddings.embed_query(text2)
v3 = embeddings.embed_query(text3)

#Now we will use:
 from sklearn.metrics.pairwise import cosine_similarity 
#Your vector looks like:
[0.1, 0.2, 0.3, ...]

But cosine_similarity() expects a collection of samples, so use:
[v1]

#Then:
similarity_1 = cosine_similarity([v1], [v2])[0][0]
similarity_2 = cosine_similarity([v1], [v3])[0][0]

#Print:
print("RAG vs RAG:", similarity_1)print("RAG vs Pizza:", similarity_2)

#You should generally see:
RAG vs RAG    → higher similarity
RAG vs Pizza  → lower similarity

Don't expect specific numbers—the model determines the embeddings.


#What does the score mean?
 For cosine similarity, values mathematically range ***********IMP******from -1 to 1, though the distribution you see in embedding systems depends on the embedding model and normalization.                      
Higher score
    ↓
more similar according to embedding space

Lower score
    ↓
less similar   

Do not make a universal rule such as:
0.80 = relevant
0.50 = irrelevant

without evaluating your own embedding model and dataset.
That's important when we later build your retrieval-confidence logic.

------------------------------------------------------------------------------------------------------------
*****************************************SEMANTIC SEARCH*******************************************

Semantic search retrieves information based on meaning represented by embeddings, rather than relying only on exact keyword matches.

            #Example:
User:
How can I recover my account password?

Document:
Steps for resetting forgotten login credentials.

The wording is different:
recover ≠ reset
account password ≠ login credentials

but the meanings are related.
Embedding-based semantic search can capture that relationship.

DOCUMENT
   ↓
Loader
   ↓
Document objects
   ↓
Chunking
   ↓
Chunks
   ↓
Embedding model
   ↓
Vectors
   ↓
Vector database
   ↓
Similarity search
   ↓
Relevant chunks
