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
