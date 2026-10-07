A vector database/vector store stores embedding vectors together with their 
associated content and metadata and provides efficient similarity search over those vectors.


A vector database will still return the nearest available chunks even when none are genuinely relevant.

Chunk
 │
 ├── Text
 ├── Metadata
 └── Embedding vector
        ↓
     Pinecone
#Later:
User question
      ↓
Embedding model
      ↓
Query vector
      ↓
Pinecone similarity search
      ↓
Top-k closest vectors
      ↓
Relevant chunks

k=4 - Return the top 4 matching chunks/results.

from langchain_core.vectorstores import InMemoryVectorStore
#Create it using the emdedding model:
vector_store = InMemoryVectorStore(
    embedding=embeddings
)
#add your chunks 
vector_store.add_documents(chunks)
----
chunks
 ↓
embedding model
 ↓
vectors
 ↓
stored alongside chunk content/metadata
-------
#Now Serach:
results = vector_store.similarity_search(
    "What is Retrieval-Augmented Generation?",
    k=2
)
#Then Inspect
for result in results:
    print(result.page_content)
    print(result.metadata)
    print() #ou've now built your first semantic retrieval system.

#output:
RAG is Retrieval-Augmented Generation. It enhances Large Language Models by
{'source': 'rag_notes.txt'}

Language Models by retrieving relevant information from an external knowledge
{'source': 'rag_notes.txt'}
