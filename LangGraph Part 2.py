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
***********************************LangGraph Memory, Checkpointing & Human-in-the-Loop***********************************************************************************************************************
Today we're completing the core LangGraph module. You'll learn how to make your AI application remember conversations, resume execution, inspect previous states and pause for human approval.

1.Why does an AI agent need memory?
#Consider a banking assistant.

Conversation 1:
User: "What is the minimum credit score for a home loan?"
Assistant: "720."

Conversation 2:
User: "What about the maximum tenure?"
Without conversation memory, the assistant may not know that "the maximum tenure" refers to the home loan.
With memory, it can use previous messages to understand the follow-up.

#Architecture
                     USER MESSAGE
                           |
                           v
                     LANGGRAPH APP
                           |
                           v
                      THREAD ID
                           |
                           v
                    CHECKPOINTER
                           |
                  +--------+--------+
                  |                 |
                  v                 v
             Existing State      New Thread
                  |                 |
                  v                 v
             Load History       Empty History
                  |                 |
                  +--------+--------+
                           |
                           v
                       LLM NODE
                           |
                           v
                    GENERATE RESPONSE
                           |
                           v
                    SAVE CHECKPOINT
                           |
                           v
                       RESPONSE
A checkpoint stores graph state at execution boundaries. It can include conversation messages and other state fields, not just a transcript.

PART A- SHORT TERM MEMORY WITH A CHECKPOINTER
2.INSTALL:
!pip install -q -U langgraph langchain-groq

3.CReate the Groq Model
import os
from getpass import getpass
from langchain_groq import ChatGroq

if not os.getenv("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = getpass("Groq API key: ")

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

4.Define conversational state
from langgraph.graph import MessagesState

MessagesState provides a messages field with an appropriate reducer for adding and updating messages.
This avoids manually concatenating the conversation history.

5.Create the chatbot node
from langchain_core.messages import SystemMessage

def chatbot(state: MessagesState):

    messages = [
        SystemMessage(
            content=(
                "You are a helpful banking assistant. "
                "Answer clearly and use the conversation "
                "history to understand follow-up questions. "
                "Do not invent banking policy facts."
            )
        ),
        *state["messages"]
    ]

    response = llm.invoke(messages)

    return {
        "messages": [response]
    }
#FLOW:

    Existing Messages
       |
       v
Add System Instruction
       |
       v
Call Groq LLM
       |
       v
Receive AIMessage
       |
       v
Append AIMessage to State

The *state["messages"] syntax unpacks the message list.
Returning [response] allows LangGraph's message reducer to merge the response into the stored conversation.

6.ADD In Memory Saver
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()

InMemorySaver is useful for learning, prototyping and tests.
It stores checkpoints in process memory, so the saved state disappears when the process or Colab runtime ends.
For persistent applications, use a durable checkpointer backed by a database.

7.Build the graph

from langgraph.graph import StateGraph, START, END

workflow = StateGraph(MessagesState)

workflow.add_node("chatbot", chatbot)

workflow.add_edge(START, "chatbot")

workflow.add_edge("chatbot", END)

app = workflow.compile(
    checkpointer=checkpointer
)

app = workflow.compile(checkpointer=checkpointer)
The checkpointer enables LangGraph to save and restore state for a thread.

PART B - Understand thread_id
8.First conversation

from langchain_core.messages import HumanMessage

config = {
    "configurable": {
        "thread_id": "banking-user-001"
    }
}

response1 = app.invoke(
    {
        "messages": [
            HumanMessage(
                content="I want to understand home loans."
            )
        ]
    },
    config=config
)

print(response1["messages"][-1].content)

The thread ID identifies a conversation's saved state.

9.Follow-up conversation
response2 = app.invoke(
    {
        "messages": [
            HumanMessage(
                content="What documents are usually required?"
            )
        ]
    },
    config=config
)

print(response2["messages"][-1].content)

Because the thread ID is unchanged, LangGraph loads the previously saved conversation state.
The model can interpret the follow-up in the context of home loans.
-------
Thread ID: banking-user-001

Message 1:
"I want to understand home loans."
             |
             v
      Save Checkpoint
             |
             v
Message 2:
"What documents are usually required?"
             |
             v
      Load Previous Messages
             |
             v
       Groq LLM Receives
       Full Available History
             |
             v
        Contextual Answer

The model can still make mistakes or lose context when histories become too long. Checkpointing preserves state; it does not guarantee perfect recall.

PART C - SEPARATE CONVERSATIONS

10.Create a different thread
config2 = {
    "configurable": {
        "thread_id": "banking-user-002"
    }
}

response3 = app.invoke(
    {
        "messages": [
            HumanMessage(
                content="Explain vehicle loans."
            )
        ]
    },
    config=config2
)

print(response3["messages"][-1].content)

This is a separate conversation.

                 CHECKPOINTER
                      |
           +----------+----------+
           |                     |
           v                     v
      Thread 001             Thread 002
           |                     |
           v                     v
      Home Loan              Vehicle Loan
      Conversation           Conversation

Production security: A thread_id is not an authorization mechanism. Your backend must verify that the authenticated user is permitted to access the requested thread.

PART D: INSPECT SAVED STATE1
11. Retrieve the latest checkpoint

snapshot = app.get_state(config)

print(snapshot.values)
get_state() returns a state snapshot associated with the supplied thread configuration.
Inspect the messages:

for message in snapshot.values["messages"]:
    print(message.type, ":", message.content)

 #you can also inspect checkpoint history:
for message in snapshot.values["messages"]:
print(message.type, ":", message.content)

This is useful for debugging how state changed over time.
Checkpoint history is also foundational for more advanced features such as replay and time travel.

*****************PART E:Human-in-the-loop approval**************************************
Suppose an AI assistant drafts a customer-facing message, but a human must approve it before it can be released.
The correct architecture is:

                  USER REQUEST
                       |
                       v
                  DRAFT MESSAGE
                       |
                       v
                 HUMAN APPROVAL
                       |
                +------+------+
                |             |
              APPROVE        REJECT
                |             |
                v             v
           MARK APPROVED   MARK REJECTED
                |             |
                +------+------+
                       |
                       v
                      END

Human approval is especially important before actions that are financially consequential, irreversible or involve external communication.

12.Create an approval state

from typing import TypedDict

class ApprovalState(TypedDict):
    request: str
    draft: str

13.Create a drafting node

def draft_message(state: ApprovalState):

    draft = (
        "Your banking request has been received "
        "and will be reviewed by our team."
    )

    return {
        "draft": draft,
        "status": "pending"
    }
For this example, we use a fixed draft so the approval mechanism can be tested without relying on model output.

14.Create the human-approval node

from langgraph.types import interrupt

def human_approval(state: ApprovalState):

    decision = interrupt({
        "question": "Approve this draft?",
        "draft": state["draft"]
    })

    approved = decision.get("approved", False)

    return {
        "status": "approved" if approved else "rejected"
    }

#What does interrupt() do?
It pauses graph execution and exposes an approval request.
The application can then collect a human decision and resume execution.
This is different from simply calling Python's input() inside a node. 
LangGraph interrupts are designed to work with its persistence and resumption mechanisms.
Important: When a node resumes after an interrupt, code before the interrupt can execute again. Avoid irreversible side effects before an interrupt unless you have designed for idempotency.
    

15.Build the approval graph

approval_workflow = StateGraph(ApprovalState)

approval_workflow.add_node("draft", draft_message)
approval_workflow.add_node("approval", human_approval)

approval_workflow.add_edge(START, "draft")
approval_workflow.add_edge("draft", "approval")
approval_workflow.add_edge("approval", END)

approval_app = approval_workflow.compile(
    checkpointer=InMemorySaver()
)

16.Start the workflow
approval_config = {
    "configurable": {
        "thread_id": "approval-001"
    }
}

result = approval_app.invoke(
    {
        "request": "Draft an acknowledgement message.",
        "draft": "",
        "status": ""
    },
    config=approval_config
)

print(result)

Execution pauses at the interrupt. Depending on the LangGraph version, the returned result exposes interrupt information, commonly under __interrupt__.

17.Resume after approval

from langgraph.types import Command

result = approval_app.invoke(
    Command(
        resume={"approved": True}
    ),
    config=approval_config
)

print(result)

#Expected final state:
{
    "request": "Draft an acknowledgement message.",
    "draft": (
        "Your banking request has been received "
        "and will be reviewed by our team."
    ),
    "status": "approved"
}
#To test rejection, start a new thread and resume it with:

Command(resume={"approved": False})

This workflow records the approval decision; it does not actually send a message.

Part F — Short-term vs long-term memory

These are related but different concepts.

Feature            	Short-term memory	                        Long-term memory
Main purpose	      Maintain a conversation's state         	Retain information across sessions or threads
Typical mechanism	  Checkpointer	                            Persistent store
Scope	              Thread-specific	                          Potentially user- or application-specific
Example	            Previous question about home loans	      A saved, authorized user preference

LangGraph provides store abstractions for longer-lived information.
For example, an application may store approved user preferences separately from conversation checkpoints.

Long-term memory needs explicit design for access permissions, data retention, deletion and privacy. Do not automatically store sensitive financial details simply because an LLM mentions them.

PART G- PRODUCTION PERSISTENCE
from langgraph.checkpoint.memory import InMemorySaver

For production, a database-backed checkpointer is generally more appropriate.
A PostgreSQL-backed setup can use the separate LangGraph Postgres checkpoint package, with APIs and setup requirements that should be checked against the installed version.

                   FRONTEND
                       |
                       v
                   FASTAPI
                       |
                       v
                 LANGGRAPH APP
                       |
          +------------+------------+
          |                         |
          v                         v
      POSTGRESQL                VECTOR STORE
      Checkpoints                Pinecone
          |                         |
          v                         v
      Thread State              RAG Evidence
          |                         |
          +------------+------------+
                       |
                       v
                     GROQ
                       |
                       v
                   RESPONSE

  PostgreSQL and Pinecone serve different purposes here.
PostgreSQL persists graph execution state.
Pinecone stores and retrieves vector embeddings.
One does not replace the other.


