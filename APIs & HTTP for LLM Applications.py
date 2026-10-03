API = Application Programming Interface
For our purposes, think of an API as a way for your Python program to communicate with another service.
1#for llm
  Your Python program
       │
       │ request
       ▼
    LLM API
       │
       │ sends request to model
       ▼
      LLM
       │
       │ generated answer
       ▼
    LLM API
       │
       ▼
Your Python program

2#HTTP - Most web APIs communicate using HTTP
Request
├── URL / endpoint
├── Method
├── Headers
└── Body

Response
├── Status code
└── Data

3#. Endpoint - An endpoint tells Python where to send the request.
https://api.example.com/chat  #"This is the address of the service/function I want."
C:\Practice\main.py  #an API resource has an endpoint.

4.#GET vs POST
These are HTTP methods.
#GET
Usually means:
Give me some data.
requests.get(...)

#POST
Usually means:
I'm sending data to you for processing/creation.
  
{
    "model": "some-model",
    "messages": [
        {
            "role": "user",
            "content": "What is RAG?"
        }
    ]
}

  5# Headers
  Headers contain information about the request
  headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}

6#Request body/ payload
actual data you are sending
payload = {
    "model": "some-model",
    "messages": [
        {
            "role": "user",
            "content": "What is RAG?"
        }
    ]
}

  Python dictionary
       ↓
HTTP/API request
       ↓
JSON representation
       ↓
Server

7#Response
Server sends somethng back

  response = requests.post(..)
  response.status_code
  response.json
  data = response.json()

Now data may be a Python dictionary/list structure.
Then you can access values from it.

8#Status codes
Code	Meaning
200	✅ Request succeeded
400	❌ Bad request
401	🔑 Authentication problem
404	❌ Resource/endpoint not found
429	⏳ Rate limit / too many requests
500	💥 Server-side error

You'll encounter these while debugging LLM APIs.

9#Put everything together
  Python
  │
  ├── Endpoint ──────→ Where?
  │
  ├── POST ──────────→ What HTTP operation?
  │
  ├── Headers ───────→ Authentication/info
  │
  └── Payload ───────→ What data/question?
          │
          ▼
       LLM API
          │
          ▼
        Model
          │
          ▼
       Response
          │
          ├── status code
          └── JSON/data


-----------------------------------------------------------------
 Dictionary
    ↓
JSON
    ↓
Environment variable
    ↓
API key
    ↓
HTTP POST
    ↓
LLM
    ↓
JSON response
    ↓
Python dictionary
    ↓
Extract answer
---------------------------------------------------------------------------

  #EXAMPLE
headers = {
    "Authorization": f"Bearer test_key", #"Authorization": f"Bearer {api_key}"
    "Content-Type": "application/json"
}

payload = {
    "model": "llama",
    "question": "What is RAG?",
    "temperature": 0
}
