#API KEY
An API key is a secret credential.
Don't post it publicly, commit it to GitHub, or paste a real key into screenshots/messages.
Your Python program
       │
       │ API key
       ↓
    Provider
       │
       ↓
Authentication/authorization
       │
       ↓
      LLM

1.The Wrong Approach:
api_key = "gsk_REAL_SECRET_KEY"
This is called hardcoding the secret.

2.Environment variables
Instead, we store the secret outside our Python source code.

import os #os is a Python module for interacting with operating-system-related functionality.

api_key = os.getenv("GROQ_API_KEY") #Look for an environment variable called GROQ_API_KEY and return its value.

print(api_key)
Environment
│
└── GROQ_API_KEY = secret
          ↓
      os.getenv()
          ↓
       api_key

3. .env files
#The .env file should normally be excluded from Git using:
#.env
#inside .gitignore.

my_rag_project/
│
├── .env              ← secrets
├── main.py            ← Python
├── rag.py
├── requirements.txt
└── .gitignore

4.Loading .env in Python
#common package: python-dotenv
#Install:
py -m pip install python-dotenv

from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GROQ_API_KEY") #Find the secret stored under the name GROQ_API_KEY.

.env
 │
 │ GROQ_API_KEY=...
 ↓
load_dotenv()
 ↓
environment variable
 ↓
os.getenv("GROQ_API_KEY")
 ↓
api_key
------------------------------------------------------------
#EXERCISE

from dotenv import load_dotenv
import os

load_dotenv()

model = os.getenv("MODEL_NAME")
project = os.getenv("PROJECT_NAME")

print(model)
print(project)
