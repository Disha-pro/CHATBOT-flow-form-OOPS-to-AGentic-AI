#MY FIRST CHATBOT
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
