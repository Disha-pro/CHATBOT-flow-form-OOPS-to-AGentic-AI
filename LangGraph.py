What is LangGraph?
LangGraph is a framework for building stateful, long-running AI workflows and agents.
 
You already know LangChain:
chain = prompt | llm
response = chain.invoke(inputs)

This is useful for a straightforward sequence.
But consider your banking RAG project:

                    USER QUESTION
                          |
                          v
                   ROUTE QUESTION
                          |
                +---------+---------+
                |                   |
                v                   v
           KNOWLEDGE BASE        DIRECT LLM
                |
                v
          RETRIEVE DOCUMENTS
                |
                v
           GRADE EVIDENCE
                |
          +-----+------+
          |            |
          v            v
        GOOD          WEAK
          |            |
          |            v
          |       REWRITE QUERY
          |            |
          |       RETRIEVE AGAIN
          |            |
          +-----+------+
                |
                v
          GENERATE ANSWER
                |
                v
         CHECK GROUNDEDNESS
                |
                v
               END

This architecture needs branching, shared state, retries and potentially persistent execution.
LangGraph provides primitives to implement that control flow.

2. Five concepts you must understand

Concept          	Meaning	                                         Python representation
State	            Shared data passed through the workflow	         TypedDict
Node	            Function that performs a step	                   Python function
Edge	            Connection between nodes                       	add_edge()
StateGraph	      Graph definition and state schema              	StateGraph(...)
Compile	          Builds an executable graph                    	.compile()

The central idea is:
Nodes read state, perform work and return state updates.
LangGraph merges those updates into the graphs state.

3.!pip install -q -U langgraph
4#Build your first state

from typing import TypedDict #defines the expected structure of a dictionary.

class AgentState(TypedDict): #AgentState is our state schema.
    question: str #means the state contains a question string
    answer: str #means the state contains an answer string.
  
{
    "question": "What is RAG?",
    "answer": ""
}

Important: TypedDict describes the data structure for static type checking; it doesn't automatically validate values at runtime.
 
5.Create a Node
A node is an ordinary Python funtion.
  
def generate_answer(state: AgentState):

    question = state["question"]

    answer = f"You asked: {question}"

    return {
        "answer": answer
}
  Understand the flow:
1. state receives the current graph state.
2. state["question"] reads the question.
3. The function creates an answer.
4. The returned dictionary updates the answer field.
Notice that we return only the field we want to update.
We don't need to return the entire state.

6. Create the graph
from langgraph.graph import StateGraph, START, END

workflow = StateGraph(AgentState)

workflow.add_node(
    "generate",
    generate_answer
)

workflow.add_edge(
    START,
    "generate"
)

workflow.add_edge(
    "generate",
    END
)

app = workflow.compile()

#Explain every component

StateGraph(AgentState) creates a graph builder using our state schema.
add_node("generate", generate_answer) registers the Python function as a graph node.
START is the graph's entry point.
END marks the terminal point.
add_edge() defines the execution path.
compile() creates the executable graph.

  The graph looks like:
         START
           |
           v
    +--------------+
    |   generate   |
    +--------------+
           |
           v
          END
7. Execute the graph
result = app.invoke({
    "question": "What is RAG?",
    "answer": ""
})

print(result)



Expected output:
{
    "question": "What is RAG?",
    "answer": "You asked: What is RAG?"
}
      #what happend internally
      Input Dictionary
      |
      v
LangGraph State
      |
      v
generate_answer(state)
      |
      v
Returns {"answer": "..."}
      |
      v
State Updated
      |
      v
END
      |
      v
Final Dictionary

      ***********This is the most important concept in todays lesson:
      a LangGraph node is a Python function that receives state and returns updates to that state.

8. Your first two-node LangGraph workflow
Now we'll add a second node to demonstrate how information moves through multiple function.

from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class BankingState(TypedDict):
    question: str
    category: str
    answer: str


def classify_question(state: BankingState):

    question = state["question"].lower()

    if "loan" in question:
        category = "loan"
    else:
        category = "general"

    return {"category": category}


def generate_response(state: BankingState):

    category = state["category"]

    if category == "loan":
        answer = "This is a banking loan question."
    else:
        answer = "This is a general question."

    return {"answer": answer}


workflow = StateGraph(BankingState)

workflow.add_node("classify", classify_question)
workflow.add_node("respond", generate_response)

workflow.add_edge(START, "classify")
workflow.add_edge("classify", "respond")
workflow.add_edge("respond", END)

app = workflow.compile()

result = app.invoke({
    "question": "What is the minimum score for a home loan?",
    "category": "",
    "answer": ""
})

print(result)

START
  |
  v
classify_question()
  |
  | Reads:
  |   question
  |
  | Writes:
  |   category = "loan"
  |
  v
generate_response()
  |
  | Reads:
  |   category
  |
  | Writes:
  |   answer = "This is a banking loan question."
  |
  v
END

The second node can read category because the first node updated the shared state.
This is how we'll eventually connect routing, retrieval, evidence grading, query rewriting and answer generation.
-----------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------
***********************LangGraph Conditional Edges & Dynamic Routing

Today's goal: Independently build a workflow that decides whether a question should use the banking knowledge base or go directly to an LLM.

1. Why conditional edges matter
Your previous graph followed a fixed sequence:

START
  |
  v
Classify Question
  |
  v
Generate Response
  |
  v
END

Every question followed the same path.
But your future AI assistant needs different behavior depending on the question.
                      START
                        |
                        v
                  ROUTER NODE
                        |
                Is it banking?
                        |
              +---------+---------+
              |                   |
             YES                  NO
              |                   |
              v                   v
         KB RETRIEVAL         DIRECT LLM
              |                   |
              v                   |
         KB GENERATION            |
              |                   |
              +---------+---------+
                        |
                        v
                       END

This is conditional routing.
#In LangGraph, we implement it using:
workflow.add_conditional_edges()

2.Understand the difference between a node and a router
A node performs work and returns state updates.
A routing function examines the current state and returns a destination label. 

def route_question(state):
    if state["category"] == "banking":
        return "knowledge_base"
    return "direct"

Notice that this function returns a string, not a state-update dictionary.
That is because its responsibility is to select the next path.

3.Build the complete conditional workflow

  step1 : Define the state
from typing import TypedDict

class AgentState(TypedDict):
    question: str #Original user input
    category: str #Classification result
    answer: str #Final response
    source_used: str #Records which path generated the response

Step 2:Create the classification Node
def classify_question(state: AgentState):

    question = state["question"].lower()

    banking_keywords = [
        "loan",
        "credit card",
        "bank",
        "interest rate"
    ]

    if any(word in question for word in banking_keywords): #This checks whether at least one keyword exists in the question
        category = "banking"
    else:
        category = "general"

    return {"category": category}

Ex : This checks whether at least one keyword exists in the question
question = "What is a home loan?"

keywords = ["loan", "bank", "credit card"]

print(any(word in question for word in keywords))

O/P-True
Production limitation: Keyword routing can misclassify questions. For example, Explain bank erosion contains bank but isnt a banking-policy question. Later, well use an LLM with structured output for more reliable routing.

Step 3: Create the routing funtion
def route_question(state: AgentState):

    if state["category"] == "banking":
        return "knowledge_base"

    return "direct"

This function decides which branch to execute.
It does not call the LLM or update the state.

Step 4: Create the knwoledge base node
banking_kb = {
    "home loan": "Minimum credit score: 720.",
    "vehicle loan": "Minimum credit score: 680.",
    "personal loan": "Minimum credit score: 700."
}


def knowledge_base_node(state: AgentState):

    question = state["question"].lower()

    for product, policy in banking_kb.items():

        if product in question:

            return {
                "answer": f"{product.title()}: {policy}",
                "source_used": "knowledge_base"
            }

    return {
        "answer": "No matching banking policy was found.",
        "source_used": "knowledge_base"
    }

We use a dictionary here to isolate and understand routing behavior. This is not semantic retrieval yet.
Later, we replace this dictionary lookup with your existing Pinecone retrieve

Step 5: Create the direct answer node

def direct_answer_node(state: AgentState):

    return {
        "answer": (
            f"Direct path selected for: {state['question']}"
        ),
        "source_used": "direct"
    }

This is also a placeholder. In the real application, this node will invoke Groq.

4#Connect everything using StateGraph
from langgraph.graph import StateGraph, START, END

workflow = StateGraph(AgentState)

# Register nodes
workflow.add_node("classify", classify_question)

workflow.add_node("knowledge_base", knowledge_base_node)

workflow.add_node("direct", direct_answer_node)

# Entry point
workflow.add_edge(START, "classify")

# Conditional routing
workflow.add_conditional_edges(
    "classify",
    route_question,
    {
        "knowledge_base": "knowledge_base",
        "direct": "direct"
    }
)

# Terminal paths
workflow.add_edge("knowledge_base", END)

workflow.add_edge("direct", END)

# Compile
app = workflow.compile()

5#Understand add_conditional_edges() line by line
workflow.add_conditional_edges(
    "classify",
    route_question,
    {
        "knowledge_base": "knowledge_base",
        "direct": "direct"
    }
)

First argument: "classify"
The node after which the routing decision happens.
  
Second argument: route_question
The Python function that determines the next destination.
  
Third argument: dictionary
Maps the routing functions returned labels to actual node names.

classify
   |
   v
route_question(state)
   |
   +-- returns "knowledge_base"
   |          |
   |          v
   |    knowledge_base node
   |
   +-- returns "direct"
              |
              v
          direct node

6.Execute your workflow
     
 questions = [
    "What is the minimum score for a home loan?",
    "Explain artificial intelligence",
    "What is the minimum score for a vehicle loan?"
]

for question in questions:

    result = app.invoke({
        "question": question,
        "category": "",
        "answer": "",
        "source_used": ""
    })

    print("\nQuestion:", question)
    print("Category:", result["category"])
    print("Answer:", result["answer"])

Expected behavior:
Question	               Route	               Result
Home loan score         	Knowledge base	      720
Explain AI	              Direct	               Placeholder direct response
Vehicle loan score	      Knowledge base	       680

You now have a branching workflow.

7.Replace the rule based router with Groq
This is the first step toward an LLM-powered workflow.
We will use Pydantic structured output, which you learned previously.

from pydantic import BaseModel
from typing import Literal

class RouteDecision(BaseModel):
    route: Literal["banking", "general"]

#Why Literal?
It restricts the expected route values to:
banking
general

The model should not return arbitrary labels such as "finance" or "other".

#Now creates the classifier:
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

router_llm = llm.with_structured_output(RouteDecision)

#Replace your original classification node:
def classify_question(state: AgentState):

    decision = router_llm.invoke(
        f"""
        Classify the user's question.

        banking:
        Questions about banking products, loans,
        credit cards or banking policies.

        general:
        All other questions.

        Question: {state['question']}
        """
    )

    return {
        "category": decision.route
    }

Important: Your existing route_question() checks for "banking", so it still works.
Rebuild and recompile the graph after replacing the node function:

workflow = StateGraph(AgentState)

workflow.add_node("classify", classify_question)
workflow.add_node("knowledge_base", knowledge_base_node)
workflow.add_node("direct", direct_answer_node)

workflow.add_edge(START, "classify")

workflow.add_conditional_edges(
    "classify",
    route_question,
    {
        "knowledge_base": "knowledge_base",
        "direct": "direct"
    }
)

workflow.add_edge("knowledge_base", END)
workflow.add_edge("direct", END)

app = workflow.compile()

Now your routing decision is generated by an LLM instead of keyword matching.
Structured-output support depends on the model and Groq API. If this raises an error, inspect the error message before changing the model or output method.

8.Production considerations

**********************************************IMP*****************************************************
 Three things matter when implementing routers in production.
Routing reliability: Test the router using a labeled dataset containing banking, non-banking and ambiguous questions.

Latency and cost: Every LLM-based routing decision adds an inference call. For obvious cases, a deterministic router can be faster and cheaper.

Security: Treat document contents and user messages as untrusted inputs. A routing model should not be allowed to select privileged tools solely because a user asks it to.  

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
******************************************* LOOPS AND QUERY REWRITING ********************************************************************************************************
   
