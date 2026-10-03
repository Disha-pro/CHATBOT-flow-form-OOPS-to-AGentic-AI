JSON = JavaScript Object Notation
import json
It's a standard text format used to exchange structured data between systems.
{
    "model": "gpt-model",
    "message": "What is RAG?"
}

Python	 JSON
dict  -	 text/data format
True   -   true
False	- false
None  -	 null

Python object ↔ JSON
#Two functions are particularly important:
json.dumps()
json.loads()

dumps → Python → JSON string
loads → JSON string → Python
-------------------------------------------------------
import json

data = {
    "model": "GPT",
    "question": "What is RAG?"
}
print(type(data))
output:<class 'dict'>

#Now
json_data = json.dumps(data)

print(json_data)
print(type(json_data))

#Output
{"model": "GPT", "question": "What is RAG?"}

<class 'str'>


Python dictionary
      ↓
json.dumps()
      ↓
JSON-formatted string

------------------------------------------------------------
#json.loads() — JSON → Python
json_data = '{"model": "GPT", "answer": "RAG uses retrieval."}'
print(type(json_data))

Oupt = str

Convert it:
data = json.loads(json_data)
print(type(data))
out = dict
-------------------------------------------------------------

#EXAMPLE

data = {
    "model": "GPT",
    "question": "What is rag?",
    "temperature": 0
}

import json

json_data = json.dumps(data) #produces a JSON-formatted Python string
print(type(json_data))

json_load = json.loads(json_data)
print(type(json_load))

print(json_data)
print(json_load["question"])

#What code proves


Python dictionary
      ↓
json.dumps(data)
      ↓
json_data
JSON string
<class 'str'>
      ↓
json.loads(json_data)
      ↓
json_load
Python dictionary
<class 'dict'>
      ↓
json_load["question"]
      ↓
"What is rag?"

#dumps / loads → work primarily with strings
json.dumps()   # Python → JSON string
json.loads()   # JSON string → Python
#dump / load   → work with files

-----------------------------------------------------------------------------
1. json.dump() — Python → JSON file

import json

data = {
    "model": "GPT",
    "question": "What is RAG?",
    "temperature": 0
}
#we want to store at 
chat_data.json
#means 
data
 ↓
Python dictionary
 ↓
json.dump()
 ↓
chat_data.json

#Write
with open("chat_data.json", "w") as file:
    json.dump(data, file)

2. Make the JSON readable
with open("chat_data.json", "w") as file:
    json.dump(data, file, indent=4) #indent=4 is primarily for human readability.
O/P:
{
    "model": "GPT",
    "question": "What is RAG?",
    "temperature": 0
}

3. json.load() — JSON file → Python
with open("chat_data.json", "r") as file:
    chatbot_data = json.load(file)
print(type(chatbot_data))
<class 'dict'>
#you can access
print(chatbot_data["model"])
print(chatbot_data["question"])

#The four functions — don't confuse them
Function	Purpose
json.dumps()	Python object → JSON string
json.loads()	JSON string → Python object
json.dump()	Python object → JSON file
json.load()	JSON file → Python object

S = String

dumps / loads
        ↑
      string

dump / load
        ↑
       file
--------------------------------------------------------------
#Exercise
data = {
    "model": "Llama",
    "question": "What is Agentic AI?",
    "source": "RAG"
}
with open("ai_data.json", "w") as files:
    json.dump(data, files)
    
with open("ai_data.json", "r") as files:
    data = json.load(files)
    print(data)    

#Flow
Python dict
    ↓
json.dump()
    ↓
ai_data.json
    ↓
json.load()
    ↓
Python dict
