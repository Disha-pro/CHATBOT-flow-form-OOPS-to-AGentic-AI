#MY FIRST CHATBOT
import os 
from groq import Groq
client = Groq(
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
