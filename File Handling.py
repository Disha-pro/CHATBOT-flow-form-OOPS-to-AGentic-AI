#main.py
with open("rag_notes.txt", "r") as file:
    document = file.read()
print(document)

 #run
py main.py (in terminal)

"""open() → opens the file
"rag_notes.txt" → file we want
"r" → read mode
as file → stores the opened file object in file
with → automatically closes the file afterward

read() takes the text from the file and stores it in:
document
   ↓
"RAG uses retrieval..." """

#Learning
rag_notes.txt
      ↓
   open()
      ↓
    read()
      ↓
document variable


""""r" → Read
"w" → Write (creates/overwrites)
"a" → Append (adds to existing content)

TXT file
   ↓
read()
   ↓
document string
   ↓
chunking
   ↓
embeddings
   ↓
vector database"""
-----------------------------------------------------------------------------------------------

Read — "r"
with open("rag_notes.txt", "r") as file:    document = file.read()


r = read existing content.
Write — "w"
with open("rag_notes.txt", "w") as file:    file.write("RAG uses external knowledge.")


w = write.
⚠️ Important: "w" overwrites the existing file content.
If the file doesn't exist, Python creates it.
Append — "a"
with open("rag_notes.txt", "a") as file:    file.write("\nEmbeddings convert text into vectors.")


a = append.
It adds new content at the end without deleting existing content.

#Remember this
Mode	Meaning	Existing content
"r"	Read	Keeps it
"w"	Write	⚠️ Overwrites it
"a"	Append	Adds to the end

