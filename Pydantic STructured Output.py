Pydantic is a Python library used to define the structure of data and validate that incoming data follows that structure.
In simple terms:
Pydantic = Data structure + validation

Suppose your Agentic RAG router is only allowed to produce:
kb
web
direct

Without validation, you might receive:
route = youtube


Python itself doesn't care.


from pydantic import BaseModel
We need validation.
That's where Pydantic becomes useful.

class RouteDecision(BaseModel):
    route: str  #.This is a Pydantic model

Now:
decision = RouteDecision(route="kb")


and:
print(decision.route)


outputs:
kb

Notice something interesting:
Instead of dictionary syntax:
a["route"]


we can use:
decision.route


#But str isn't strict enough
This still allows:
RouteDecision(route="banana")


because "banana" is technically a string.
We want only three possible values.
Python provides:
from typing import Literal


Now:
class RouteDecision(BaseModel):    route: Literal["kb", "web", "direct"]


We've created a rule:
route MUST be:

"kb"
OR
"web"
OR
"direct"

So this is valid:
decision = RouteDecision(route="kb")


But:
decision = RouteDecision(route="banana")

will produce a validation error.
That's exactly what we want.

#Why you're learning this for Agentic RAG
Later your router may look conceptually like:
class RouteDecision(BaseModel):    route: Literal["kb", "web", "direct"]


Another grader might have:
class EvidenceGrade(BaseModel):    grade: Literal["relevant", "irrelevant"]


Or your upgraded RAG system could have:
class RetrievalDecision(BaseModel):    relevance_score: float    confidence: float


So your earlier OOP lesson is now connecting to LLM engineering:
Python Class
    ↓
Pydantic BaseModel
    ↓
Schema
    ↓
Structured LLM Output
    ↓
Reliable routing
    ↓
LangGraph Agent

#Your exercise
RouteDecision       → class
BaseModel           → parent class
route               → attribute/field
Literal[...]        → allowed values


from pydantic import BaseModel
from typing import Literal
class RouteDiretion(BaseModel):
  route:Literal["kb","web","direct"]
decision = RouteDecision(route="kb")
print(decision)
print(decision.route)


Normal Python string
        ↓
could contain anything

Pydantic + Literal
        ↓
validates the value
tube"  ❌

----------------------------------------------------------------------------------------------------------------

#LLM + STRUCTURED OUTPUT

User question
      ↓
     LLM
      ↓
structured decision
      ↓
RouteDecision
      ↓
KB / WEB / DIRECT


def route_question(question):

    messages = [
        {
            "role": "system",
            "content": """
            You are a routing agent.

            Classify the user's question into exactly one route:

            kb = questions requiring the private knowledge base
            web = questions requiring current internet information
            direct = greetings or questions answerable directly

            Return only JSON:
            {"route": "kb"}
            """
        },
        {
            "role": "user",
            "content": question
        }
    ]

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages
    )

    return response.choices[0].message.content
answer = route_question(
    "What does my uploaded RAG document say?"
)

print(answer)
print(type(answer))


arse and validate it
You've already learned:
import json


Convert:
data = json.loads(answer)


Now:
data


is approximately:
{"route": "kb"}


Then validate:
decision = RouteDecision(**data)


This ** is new.
If:
data = {"route": "kb"}


then:
RouteDecision(**data)


is essentially equivalent to:
RouteDecision(route="kb")


** unpacks a dictionary into keyword arguments.
So:
decision.route


gives:
kb

Question
   ↓
route_question(question)
   ↓
LLM
   ↓
'{"route":"kb"}'
        ↑
      string
   ↓
json.loads()
   ↓
{"route":"kb"}
        ↑
       dict
   ↓
RouteDecision(**data)
   ↓
RouteDecision(route="kb")
        ↑
validated Pydantic object
   ↓
decision.route
   ↓
"kb"
