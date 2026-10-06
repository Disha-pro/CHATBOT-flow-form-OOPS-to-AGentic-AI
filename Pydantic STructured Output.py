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

