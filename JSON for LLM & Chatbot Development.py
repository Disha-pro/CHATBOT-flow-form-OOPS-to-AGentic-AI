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
















