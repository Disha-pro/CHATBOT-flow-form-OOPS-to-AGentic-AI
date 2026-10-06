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

-------------

from langchain_groq import ChatGroq

llm = ChatGroq(
    model = "openai/gpt-oss-20b",
    temperature=0,
    api_key="g--------------------------------")

response = llm.invoke("Explain data analytics skillset in 2026 in 4 bullet points")
print(response.content)

----------------------------------------------------------------------------------------------------
#Prompts

llm.invoke("explain RAG simply")
#Suppose we want:
You are an AI engineering tutor.
Explain the following topic:
RAG

We dont want to manually construct that string every time.

LangChain provides prompt templates. #IMP
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an AI engineering tutor. Explain concepts clearly."
    ),
    (
        "user",
        "Explain {topic}."
    )
])

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AI tutor."),
    ("user", "{question}")
])


----------------------------------------------------------------------------------------
************************************LCEL (|)************************************************
This style is part of LCEL — LangChain Expression Language.
LCEL (LangChain Expression Language) is LangChains
declarative syntax for connecting runnable components into an execution pipeline, 
where the output of one component becomes the input of the next component.

chain = component1 | component2 | component3
Think:
Input → Component 1 → Component 2 → Component 3 → Output

The | operator represents composition/piping in this context.

Your order
   ↓
Waiter
   ↓
Kitchen
   ↓
Food
   ↓
You
Each stage receives something and produces something for the next stage.
You don't personally:
- walk into the kitchen,
- tell the chef,
- collect ingredients,
- cook,
- plate,
- bring the food back.
The process is connected as a pipeline.
LCEL does something conceptually similar with AI components.

 
Don't think of | here as mathematical OR.
#In this context, think:
Send the output of the left component into the component on the right.

Langchain allows:
chain = prompt | llm
#Take the input → pass it through prompt → send the resulting messages to llm
 
#means:
INPUT
  ↓
PROMPT
  ↓
LLM
  ↓
OUTPUT

 response = chain.invoke({
  "topic":"RAG"
 })
 print(response.content)

 {"topic": "RAG"}
       ↓
ChatPromptTemplate
       ↓
System: You are an AI engineering tutor.
User: Explain RAG.
       ↓
ChatGroq
       ↓
AIMessage
       ↓
response.content
------------------

{"question": "What is RAG?"}
             ↓
           prompt
             ↓
System: You are an AI tutor.
User: What is RAG?
             ↓
            llm
             ↓
         AIMessage
             ↓
      response.content           #prompt | llm : You're creating a pipeline of compatible runnable components.


 #Without LCEL vs with LCEL
Without LCEL, conceptually you might do:
formatted_prompt = prompt.invoke({    "question": "What is RAG?"})response = llm.invoke(formatted_prompt)print(response.content)


You're manually saying:
Run prompt
↓
take result
↓
give result to LLM

With LCEL:
chain = prompt | llmresponse = chain.invoke({    "question": "What is RAG?"})print(response.content)


LangChain handles the connection.
That's the important idea.


 Question
   ↓
Retriever
   ↓
Retrieved documents
   ↓
Formatting
   ↓
RAG Prompt
   ↓
LLM
   ↓
Output parser
   ↓
Final answer


 LCEL gives me a way to compose LangChain runnable components into an execution pipeline.

#EXAMPLE
 Raw material
     ↓
Cutting machine
     ↓
Shaping machine
     ↓
Painting machine
     ↓
Finished product

factory = cutting | shaping | painting
product = factory.invoke(Raw_material)
Each component has a specific responsibility.
This is close to how you should mentally visualize LCEL.

-----------------------------------------------------------------------------------------------------
******************************************RUNNABLE**************************************************

 A runnable is essentially a component that follows LangChain's execution interface and can participate in these pipelines. 
 
Runnable
   ↓
something LangChain can execute

LCEL
   ↓
a way to compose compatible runnables

invoke()
   ↓
execute the runnable/chain   

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AI tutor."),
    ("user", "{question}")
])

chain = prompt | llm

response = chain.invoke({
    "question": "Explain RAG in two sentences."
})

print(response.content) #The key name and placeholder correspond.
