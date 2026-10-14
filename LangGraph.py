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
