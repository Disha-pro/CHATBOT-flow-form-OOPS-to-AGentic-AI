LangChain provides standardized building blocks for constructing LLM applications and RAG pipelines.
A useful mental model is:
LangChain = framework/components for connecting models, prompts, documents, retrievers, tools, and application logic.

It does not make the LLM intelligent by itself.


User
 ↓
Prompt
 ↓
LLM
 ↓
Document Loader
 ↓
Text Splitter
 ↓
Embeddings
 ↓
Vector Database
 ↓
Retriever
 ↓
LLM
 ↓
Answer


from langchain_groq import ChatGroq

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0 #Temperature controls the degree of randomness/variation in generation.
)

ChatGroq
   ↓
class

llm
   ↓
object
------------
Lower temperature
      ↓
more deterministic / conservative

Higher temperature
      ↓
more variation / creativity
------------------

#Invoke the Model
response=ll.invoke("what is RAG?") #efers to triggering, calling, or executing a specific function, model, or tool programmatically.
print(response) #returns a LangChain message object.

Usually what we actually want is:
print(response.content)

Direct Groq SDK

client.chat.completions.create(...)
        ↓
response.choices[0].message.content

LangChain

llm.invoke(...)
        ↓
response.content
-------------------------------------------------------

#FIRST CALL FOR LLM

!pip install -q langchain langchain-groq

import os
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

response = llm.invoke("Explain RAG in two sentences.")
#invoke = give this component an input and execute it.It's a LangChain interface method.

print(response.content)
