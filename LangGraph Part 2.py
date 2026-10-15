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

What does bind_tools() do?
It makes the tool definitions available to the model during inference.
It does not automatically execute them.

