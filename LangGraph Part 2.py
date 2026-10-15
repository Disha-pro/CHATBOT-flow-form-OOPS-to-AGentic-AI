*************************LangGraph Tool Calling & Agent Decision-Making**********************************
Today we move from fixed workflows to LLM-driven tool selection. This is the bridge between LangGraph and Agentic AI.

1.What is TOOL CALLING?
An LLM normally receives a question and generates a response.
With tool calling, it can instead request an action through a tool you made available.

                  USER QUESTION
                        |
                        v
                      LLM
                        |
                  DECISION POINT
                        |
             +----------+----------+
             |                     |
       Answer directly        Call a tool
             |                     |
             |                     v
             |                TOOL EXECUTION
             |                     |
             |                     v
             |                 TOOL RESULT
             |                     |
             |                     v
             |                    LLM
             |                     |
             +----------+----------+
                        |
                        v
                   FINAL ANSWER

Important: The LLM does not execute Python functions by itself. It produces a structured tool-call request. Your application or LangGraph executes the corresponding function and returns its result to the model.

Fixed workflow  vs tool-calling agent
               
Fixed workflow	                                               Tool-calling agent
Developer specifies the execution path	                       LLM can select among permitted tools
Predictable routing	                                           More flexible decisions
Easier to test                                               	Requires additional safeguards
Good for known business processes                            	Useful when different questions require different capabilities

PART A - CREATE YOUR FIRST TOOL
2.Install the required libraries
!pip install -q -U langgraph langchain-core langchain-groq

3.Define a tool using @tool
from langchain_core.tools import tool

@tool #@tool converts the Python function into a LangChain tool with a name, description and argument schema.
def get_loan_credit_score(loan_type: str) -> str: #loan_type: str defines the expected input type.
    """Return the minimum credit score for a loan product."""

    loan_scores = {
        "home": 720,
        "vehicle": 680,
        "personal": 700
    }

    loan_type = loan_type.lower().strip()

    if loan_type not in loan_scores:
        return "Loan product not found."

    score = loan_scores[loan_type]

    return f"Minimum credit score for {loan_type} loan: {score}"   

loan_type: str defines the expected input type.
The docstring tells the LLM what the tool does. Tool descriptions are important because the model uses them when deciding which tool to call.
The dictionary is our temporary knowledge base.
The return value becomes the tool result available to the LLM.

#Test the funtion directly:
print(
    get_loan_credit_score.invoke({
        "loan_type": "vehicle"
    })
)

PART B- CREATE MULTIPLE TOOLS

4.Add a loan tenure tool
@tool
def get_loan_tenure(loan_type: str) -> str:
    """Return the maximum permitted tenure for a loan product."""

    tenures = {
        "home": "25 years",
        "vehicle": "84 months",
        "personal": "60 months"
    }

    loan_type = loan_type.lower().strip()

    if loan_type not in tenures:
        return "Loan product not found."

    return (
        f"Maximum tenure for {loan_type} loan: "
        f"{tenures[loan_type]}"
    )

#Now our assianatnt has 2 capabiliites:
                 BANKING ASSISTANT
                        |
             +----------+----------+
             |                     |
             v                     v
       Credit Score Tool       Loan Tenure Tool
             |                     |
             v                     v
       Returns Score          Returns Tenure

PART C- CONNECTS TOOLS

5.Configure the LLM
import os
from getpass import getpass
from langchain_groq import ChatGroq

if not os.getenv(GROQ_API_KEY):
    os.environ[GROQ_API_KEY] = getpass(Enter Groq API key: )

llm = ChatGroq(
    model=openai/gpt-oss-20b,
    temperature=0
)
Tool-calling support depends on the model and provider. This lesson uses the LangChain tool-calling interface; if the selected Groq model rejects a tool schema, we will need to inspect the provider error or use another supported model.

6.Bind tools to the LLM
tools = [
    get_loan_credit_score,
    get_loan_tenure
]

llm_with_tools = llm.bind_tools(tools)
#A successful tool-call decision may resemble:
[
    {
        "name": "get_loan_credit_score",
        "args": {"loan_type": "vehicle"},
        "id": "call_123",
        "type": "tool_call"
    }
]

The tool-call ID and exact response structure vary. The model might also answer without calling a tool; binding tools makes them available, not mandatory.

#What happened?
User:
"What is the minimum credit score for a vehicle loan?"
                     |
                     v
               Groq LLM
                     |
                     v
          Available Tool Schemas
                     |
           +---------+---------+
           |                   |
    Credit Score Tool     Tenure Tool
           |
           v
     LLM selects:
     get_loan_credit_score
           |
           v
     Arguments:
     {"loan_type": "vehicle"} 

At this stage, the LLM has requested a tool call. We still need to execute it.

PART D: BUILD THE LANGGRAPH TOOL EXECUTION LOOP
LangGraph provides ToolNode, which executes tool calls from an AI message.
7.DEFINE THE AGENT STATE

from langgraph.graph import MessagesState

MessagesState is a prebuilt state schema for storing conversation messages.
It uses a message reducer so that new messages can be appended to the conversation history.
This is different from our earlier TypedDict examples, where we manually defined fields such as question, answer and retry_count.

8.Create the assistant node
from langchain_core.messages import SystemMessage

def assistant_node(state: MessagesState):

    messages = [
        SystemMessage(
            content=(
                "You are a banking-policy assistant. "
                "Use the available tools for loan score "
                "and tenure questions. "
                "Do not invent banking policy details."
            )
        ), #state["messages"] contains the conversation history.
        *state["messages"] #unpacks the messages into the new list.
    ]

    response = llm_with_tools.invoke(messages) #sends the conversation and tool schemas to the model.

    return {
        "messages": [response] #adds the model's response to graph state.
    }

9.CReate the tool node
from langgraph.prebuilt import ToolNode, tools_condition

tool_node = ToolNode(tools)

ToolNode is responsible for executing the requested tools.
tools_condition checks whether the latest AI message contains tool calls.

#Conceptually:
                    ASSISTANT NODE
                          |
                          v
                 Did LLM call a tool?
                          |
                 +--------+--------+
                 |                 |
                YES                NO
                 |                 |
                 v                 v
              TOOL NODE           END
                 |
                 v
             TOOL RESULT
                 |
                 v
            ASSISTANT NODE

Notice the loop from the tool node back to the assistant.
The model can receive a tool result and decide whether another tool call is necessary.

10.Build the complete graph

from langgraph.graph import StateGraph, START, END

workflow = StateGraph(MessagesState)

workflow.add_node("assistant", assistant_node)

workflow.add_node("tools", tool_node)

workflow.add_edge(START, "assistant")

workflow.add_conditional_edges(
    "assistant",
    tools_condition,
    {
        "tools": "tools",
        "__end__": END
    }
)

workflow.add_edge("tools", "assistant")

agent_app = workflow.compile()

#ARCHITECTURE
                       START
                         |
                         v
                   ASSISTANT NODE
                         |
                         v
                   tools_condition
                         |
                +--------+--------+
                |                 |
             Tool Call          No Tool
                |                 |
                v                 v
             TOOL NODE           END
                |
                v
           Execute Function
                |
                v
            ToolMessage
                |
                v
           ASSISTANT NODE

The ToolNode sends tool results back as messages, and the assistant can use those results to generate its final response.
The graph is now capable of selecting and executing tools

PART E - EXECUTE YOUR FIRST TOOL-CALLING AGENT

11.Ask a banking question
from langchain_core.messages import HumanMessage

result = agent_app.invoke(
    {
        "messages": [
            HumanMessage(
                content=(
                    "What is the minimum credit score "
                    "for a vehicle loan?"
                )
            )
        ]
    },
    config={"recursion_limit": 10}
)

print(result["messages"][-1].content)

The expected factual answer, if the model uses the tool correctly, is:
The minimum credit score for a vehicle loan is 680.

#Now try:
result = agent_app.invoke(
    {
        "messages": [
            HumanMessage(
                content=(
                    "What is the minimum credit score "
                    "and maximum tenure for a home loan?"
                )
            )
        ]
    },
    config={"recursion_limit": 10}
)

print(result["messages"][-1].content)

The agent should be able to use both tools to retrieve the two policy facts.
The model decides which tools to call, and the graph handles their execution

PART F: INSPECT THE ACTUA; TOOL CALLS
for message in result["messages"]:

    print("\nMessage type:", message.type)

    if hasattr(message, "tool_calls"):
        print("Tool calls:", message.tool_calls)

    print("Content:", message.content)

    HumanMessage
     |
     v
AIMessage (tool-call request)
     |
     v
ToolMessage (tool result)
     |
     v
AIMessage (final answer)


2. What can go wrong?
Failure	                                            Cause	                                   Engineering response
Model doesn't call a tool	                    Tool choice is model-controlled	               Improve descriptions or enforce tool usage where supported
Wrong tool selected                         	Ambiguous tool descriptions	                    Clarify tool responsibilities
Invalid arguments                            	Model generates incompatible inputs            	Validate schemas and handle errors
Repeated tool calls                         	Agent loops unnecessarily	                      Limit steps and detect repetition
Tool returns wrong data	                      Incorrect tool implementation	                   Unit-test tools independently
Sensitive data exposure	                      Tool has excessive permissions                  	Apply authorization and least privilege

Security principle: A model choosing a tool does not grant permission to access data. Authorization must be enforced by the tool or backend.

For production, you should also enforce limits on tool calls, timeouts and API usage. The graph recursion limit is a useful safeguard, but it is not a complete resource-control strategy.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
