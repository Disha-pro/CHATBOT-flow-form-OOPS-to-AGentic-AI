!pip install -q langchain-core langchain-text-splitters langchain-huggingface langchain-groq sentence-transformers

import os

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

#Create banking knowledge documents
documents = [
    Document(
        page_content=(
            "Personal loan applicants must have a minimum "
            "monthly income of INR 25000. The maximum "
            "loan tenure is 60 months."
        ),
        metadata={"source": "personal_loan_policy.txt", "page": 1}
    ),
    Document(
        page_content=(
            "Home loan applicants must have a minimum "
            "credit score of 700. The maximum repayment "
            "tenure is 25 years."
        ),
        metadata={"source": "home_loan_policy.txt", "page": 1}
    ),
    Document(
        page_content=(
            "Credit card applications require identity "
            "verification and income documentation."
        ),
        metadata={"source": "credit_card_policy.txt", "page": 1}
    )
]

#Split Documents
splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=40
)

chunks = splitter.split_documents(documents)

print("Total chunks:", len(chunks))

#Create the embeddings and vector store
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = InMemoryVectorStore(
    embedding=embeddings
)

vector_store.add_documents(chunks)

#create the retriver
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 2} #Why k=2? We want the two closest chunks for each question. This is a learning configuration, not a universally optimal production value.
)

#Connect Groq
import os

# Using the GROQ_API_KEY variable defined in the earlier cell
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

#Build the RAG PROMPT
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are a banking policy assistant.

        Answer questions using only the supplied context.

        If the context does not contain enough information,
        say: "I don't have enough information."

        Do not invent banking policies or eligibility rules.

        Context:
        {context}
        """
    ),
    ("user", "{question}")
])
  
]


#****************RAG FUNTION COMPLETE*********************************
def ask_rag(question):

    # Step 1: Retrieve relevant documents
    retrieved_docs = retriever.invoke(question)

    # Step 2: Format retrieved context
    context = "\n\n".join(
        f"Source: {doc.metadata.get('source', 'unknown')}\n"
        f"Content: {doc.page_content}"
        for doc in retrieved_docs
    )

    # Step 3: Combine prompt with LLM
    chain = prompt | llm

    # Step 4: Generate the answer
    response = chain.invoke({
        "context": context,
        "question": question
    })

    # Step 5: Return answer and retrieved sources
    return {
        "answer": response.content,
        "sources": [
            doc.metadata for doc in retrieved_docs
        ]
    }

#FLOW
ask_rag(question)
       ↓
retriever.invoke(question)
       ↓
List[Document]
       ↓
Extract page_content + metadata
       ↓
Build context string
       ↓
ChatPromptTemplate
       ↓
ChatGroq
       ↓
response.content
       ↓
Return answer + sources


#TEST THE CODE
result = ask_rag(
    "What is the minimum monthly income for a personal loan?"
)

print("ANSWER:")
print(result["answer"])

print("\nRETRIEVED SOURCES:")
print(result["sources"])

#TEST
result = ask_rag(
    "What is the interest rate for a personal loan?"
)

print(result["answer"])

-------------------------------------------------------------------------------
#First: Answers to your three RAG modifications
You've completed the basic RAG pipeline. Here are the exact changes from your assignment.
1. Change top-k from 2 to 3
retriever = vector_store.as_retriever(   
  search_type="similarity",  
  search_kwargs={"k": 3})

Now the retriever can return up to three documents rather than two.

2. Add a vehicle-loan document
documents.append(   
  Document(      
    page_content=(      
      "Vehicle loan applicants must have a minimum "    
      "monthly income of INR 30000 and a credit "       
      "score of at least 680."        ),    
    metadata={          
      "source": "vehicle_loan_policy.txt",     
      "page": 1     
    }  
  ))

Rebuild the chunks and vector store:
chunks = splitter.split_documents(documents)
vector_store = InMemoryVectorStore(  
  embedding=embeddings)
vector_store.add_documents(chunks)
retriever = vector_store.as_retriever( 
  search_kwargs={"k": 3}
)


Test:
result = ask_rag(  
  "What are the eligibility requirements for a vehicle loan?")
print(result["answer"])

The fictional policy specifies a minimum income of INR 30,000 and a credit score of 680.

3. Return the number of retrieved documents
Modify your existing ask_rag() function's return statement:

return {   
  "answer": response.content,  
  "sources": [doc.metadata for doc in retrieved_docs],   
  "retrieved_count": len(retrieved_docs)}

Then:
result = ask_rag("What is the vehicle loan eligibility?")
print(result["answer"])
print(result["retrieved_count"])


That's all three modifications.
