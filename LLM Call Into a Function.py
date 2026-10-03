
import os
from groq import Groq #You're importing the Groq class from the installed groq package.

client = Groq(
    api_key=os.getenv("GROQ_API_KEY") #retrieves the secret from the environment.
)

response = client.chat.completions.create( #tells groq which models to run
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": "What is RAG?"
        }
    ]
)

print(response.choices[0].message.content) #This extracts the generated answer.


client
  ↓
chat
  ↓
completions
  ↓
create()
---------------
messages = LIST
              ↓
          DICTIONARY
           ↙       ↘
       role       content
        ↓            ↓
      user      What is RAG?
-------------------------------------
response
   ↓
choices
   ↓
[0]
   ↓
message
   ↓
content
   ↓
"RAG is Retrieval-Augmented Generation..."
  ↓
send request to Groq


import os
from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": "What is RAG?"
        }
    ]
)

print(response.choices[0].message.content)

---------------------------------------------------------
client → connection/client object
messages → input conversation
model → which LLM to use
response → returned result
choices[0] → first generated choice
message.content → actual answer

-------------------------------------------------------------------------------------------------------
#LLM Call Into a Function
ask_llm("What is RAG?")
ask_llm("What is LangChain?")
ask_llm("Explain embeddings")

1#.Funtion
def ask_llm(question):

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": question #That means the function is dynamic.
            }
        ]
    )

    return response.choices[0].message.content

question
   ↓
"What is LangChain?"
   ↓
content
   ↓
Groq
   ↓
LLM
   ↓
answer
----------------------------------------------------------------------------------------------
