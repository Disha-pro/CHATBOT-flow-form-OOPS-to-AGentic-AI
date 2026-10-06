1#MY FIRST CHATBOT
import os 
from groq import Groq
client = Groq( #creates an object and stores it in the variable client
    api_key="------------------------------------------------" 
)

#Now started
def hey_llm(asking):
    response = client.chat.completions.create(
    model = "openai/gpt-oss-20b",
    messages = [
        {
            "role":"user",
            "content" : asking
            
        }
    ]
    )
    return response.choices[0].message.content
  
answer = hey_llm("Wht is RAG?")
print(answer)

----------------------------------------------------------------------------------------------------

2#Build Your First Chatbot Loop
answer = ask_llm("What is RAG?")
print(answer)

You: What is RAG?
AI: ...

You: What are embeddings?
AI: ...

You: Explain vector databases.
AI: ...

You: exit
Chat ended.

#Now : 
question = input("Ask something: ")

answer = ask_llm(question)

print(answer)


You type question
       ↓
    input()
       ↓
   question
       ↓
 ask_llm(question)
       ↓
     Groq
       ↓
      LLM
       ↓
    response
       ↓
   print(answer)

#We need a loop
while True:  #You may remember that True is always true,
so means:
Keep running indefinitely.
while True:
    question = input("You: ")

#How do we stop it?
if question == "exit":
    break #Immediately leave the loop.

while True
    ↓
input question
    ↓
Is question "exit"?
    │
    ├── YES → break → chatbot ends
    │
    └── NO → continue

#Connect 
while True:

    question = input("You: ")

    if question == "exit":     # if question.lower() == "exit": .lower() converts the string to lowercase before comparison.
        break 

    answer = ask_llm(question)

    print("AI:", answer)
----------------------------------------------------------------------------------------------------

3#Conversational History & Memory
#Current chatbot 
messages=[
    {
        "role": "user",
        "content": question
    }
]
Every request contains only the latest question.
So the LLM doesn't automatically know what you previously discussed.

3.1 The Problem :
#imagine
You: My name is Disha.
AI: Nice to meet you, Disha.

You: What is my name?

#second api contains
{
    "role": "user",
    "content": "What is my name?"
}

#he model hasn't been given: 
"My name is Disha."
so we need to start converstaion history

3.2 Create a message list

messages = []
#WE add:
messages.append(
    {
        "role": "user",
        "content": "What is RAG?"
    }

messages.append(
    {
        "role": "assistant",
        "content": answer
    }
)
    
)

#Now the histiry we have 
[
    {
        "role": "user",
        "content": "What is RAG?"
    },
    {
        "role": "assistant",
        "content": "RAG stands for Retrieval-Augmented Generation."
    }
] #This is convestaional history

3.3. Second question
User asks: why is it useful?

Append it:
messages.append(
    {
        "role": "user",
        "content": "Why is it useful?"
    }
)

#Now 
messages
│
├── user      → What is RAG?
├── assistant → RAG stands for...
└── user      → Why is it useful?

    We send the whole list to the model.
Therefore the model can understand what it refers to.


3.4 Modify your ask_llm() funtion

def ask_llm(messages): #imp change instaed of question its messages 
#ask_llm(question) - One question
#ask_llm(messages) - Entire convesations


    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages
    )

    return response.choices[0].message.content


messages = []

      ↓

User asks question

      ↓

append USER message

      ↓

send messages → LLM

      ↓

receive answer

      ↓

append ASSISTANT answer

      ↓

repeat


#EXERCISE
def ask_llm(messages):
    response = client.chat.completions.create(
        model = "openai/gpt-oss-20b",
        messages = messages)
    return response.choices[0].message.content #it must be message only

messages =[] #imp for history

while True:
    question = input("USER: ")

    if question.lower() == "exit":
        break

    messages.append(
        {
            "role":"user",
            "content":question  #first quetsion
        }
        
    )

    answer = ask_llm(messages) #imp

    messages.append(
        {
            "role": "assistant",
            "content":answer
        }
    )

    print("AI: ",answer)

#flow 
Take USER question
        ↓
Store USER question in history
        ↓
Send history to LLM
        ↓
Get AI answer
        ↓
Store AI answer in history
        ↓
Print AI answer
        ↓
Repeat

----------------------------------------------------------------------------------------------------------------------------

4#system, user, assistant Roles + Prompt Engineering

4.1 # imp roles
messages = [
 "   {
        "role": "system",
        "content": "You are an AI tutor."
    },
    {
        "role": "user",
        "content": "What is RAG?"
    },
    {
        "role": "assistant",
        "content": "RAG stands for Retrieval-Augmented Generation."
    }
]
"
system	Defines chatbot behavior/instructions
user	What the human says
assistant	What the AI previously answered

#System
messages = [
    {
        "role": "system",
        "content": "You are an AI tutor. Explain concepts simply with examples."
    }
]

messages = [
  "  {
        "role": "system",
        "content": """
        You are an AI engineering tutor.

        Explain Python, LLMs, RAG and Agentic AI
        using beginner-friendly explanations.

        Give practical examples.
        Keep answers concise.
        """
    }
]"

ROLE
↓
AI engineering tutor

DOMAIN
↓
Python / LLM / RAG / Agentic AI

STYLE
↓
beginner-friendly

BEHAVIOR
↓
practical examples

CONSTRAINT
↓
concise


like 
messages = [
    {
        "role": "system",
        "content": "You are an AI engineering tutor. Explain concepts simply with practical examples."
    }
]
messages = []

#USER
messages.append({
    "role": "user",
    "content": question
})

#assistant
messages.append({
    "role": "assistant",
    "content": answer
})


SYSTEM:
Answer using the provided context.
If the answer isn t in the context, say you don't know.

CONTEXT:
<retrieved documents>

USER:
What happens when retrieved documents aren't relevant?

User question
      ↓
Retriever
      ↓
Relevant documents
      ↓
Construct prompt
      ↓
System instructions
+ retrieved context
+ user question
      ↓
LLM
      ↓
grounded answer

#Prompt key points
ROLE:
You are a banking-domain AI assistant.

TASK:
Answer the user's question.

CONTEXT:
Use only the retrieved documents.

CONSTRAINT:
Do not invent unsupported information.

OUTPUT:
Return a concise answer and sources.

#EXAMPLE
def ask_llm(messages):
    response = client.chat.completions.create(
        model = "openai/gpt-oss-20b",
        messages = messages
    )
    return response.choices[0].message.content

messages = [            #IMP CHNAGE TO ADD here because it is knowing to chatbot about the instructions perticuarity .
    {
        "role": "system",
        "content": """
        You are a professional AI interviewer focused on
        LLMs, RAG, and Agentic AI.

        Give technically accurate and concise responses.
        Point out incorrect technical statements.
        """
    }
]

while True:
    question = input("USER: ")

    if question.lower() == "exit":
        break

    messages.append(
        {
            "role":"user",
            "content":question
        }
        
    )

    answer = ask_llm(messages)

    messages.append(
        {
            "role": "assistant",
            "content":answer
        }
    )

    print("AI: ",answer)

#architecture
messages
│
├── SYSTEM
│
├── USER
│
├── ASSISTANT
│
├── USER
│
└── ASSISTANT
        ↓
ask_llm(messages)
        ↓
Entire history sent to LLM


-------------------------------------------------------------------------------------------------------------
 5#STRUCTURED OUTPUT
{
    "route": "kb"
} #This is called structured output.

USER QUESTION
      ↓
    ROUTER
      ↓
 ┌────┼─────┐
 ↓    ↓     ↓
KB   WEB   DIRECT

LLM
 ↓
{"route":"kb"}
 ↓
json.loads()
 ↓
Python dictionary
 ↓
decision["route"]
 ↓
IF / ELIF
 ↓
Choose next action
------------------------
if decision["route"] == "kb":
    print("Search vector database")

elif decision["route"] == "web":
    print("Search web")

else:
    print("Answer directly")

-------------------------------
answer = '{"route": "kb"}'

a=json.loads(answer)
print(type(answer))
print(type(a))
-----------------
JSON string
'{"route": "kb"}'
        ↓
json.loads()
        ↓
Python dictionary
{"route": "kb"}
        ↓
a["route"]
        ↓
"kb"
        ↓
if / elif / else
        ↓
next action
