GraphRAG Evaluation: Entity Accuracy, Relationship Accuracy & Multi-Hop Reasoning

#Why GraphRAG needs additional evaluation

In conventional RAG, we primarily evaluate whether the retriever finds relevant chunks and whether the LLM produces grounded answers.
GraphRAG introduces additional failure points:

                  BANKING POLICY DOCUMENT
                            |
                            v
                  Entity Extraction
                            |
                   Entity Accuracy
                            |
                            v
                Relationship Extraction
                            |
                Relationship Accuracy
                            |
                            v
                     Knowledge Graph
                            |
                            v
                       Graph Query
                            |
                 Graph Retrieval Quality
                            |
                            v
                     Retrieved Paths
                            |
                  Multi-Hop Correctness
                            |
                            v
                         Groq LLM
                            |
                            v
                     Generated Answer
                            |
                  Faithfulness / Relevance

2. Four important GraphRAG evaluation dimensions

Metric                                                          	What it checks
Entity Extraction Precision / Recall / F1                       	Did we identify the correct entities?
Relationship Extraction Precision / Recall / F1                  	Did we extract the correct relationships?
Graph Retrieval Recall                                          	Did the graph query retrieve the required facts?
Multi-Hop Answer Accuracy                                        	Did the system correctly combine connected facts?

Part A — Entity extraction evaluation
3. Create ground-truth entities
#Suppose our banking policy says:
Home Loan requires a minimum credit score of 720. Vehicle Loan requires 680. Personal Loan requires 700.

Our manually verified entities are:
ground_truth_entities = {
    "Home Loan",
    "Vehicle Loan",
    "Personal Loan",
    "Credit Score"
}

#Now suppose an extrcation model returns:
predicted_entities = {
    "Home Loan",
    "Vehicle Loan",
    "Credit Card",
    "Credit Score"
}

Notice that:
- Home Loan is correct.
- Vehicle Loan is correct.
- Credit Score is correct.
- Credit Card is an incorrect extra entity for this passage.
- Personal Loan is missing.
  
4. Calculate entity precision, recall and F1

true_positives = ground_truth_entities & predicted_entities

false_positives = predicted_entities - ground_truth_entities

false_negatives = ground_truth_entities - predicted_entities

precision = len(true_positives) / len(predicted_entities)

recall = len(true_positives) / len(ground_truth_entities)

f1 = 2 * precision * recall / (precision + recall)

print("Correct entities:", true_positives)
print("Extra entities:", false_positives)
print("Missing entities:", false_negatives)

print("Precision:", precision)
print("Recall:", recall)
print("F1:", f1)

#Expected results:
Precision
0.75

Recall
0.75

F1
0.75

#Understand the Python operators
Operator	                     Meaning
&	                             Intersection: elements present in both sets
-	                             Set difference: elements present in one set but not the other
len()                        	Counts elements
precision	                    How many predicted entities were correct
recall	                      How many expected entities were found
f1                           	Harmonic mean of precision and recall

Part B — Relationship extraction evaluation

5. Represent graph relationships as triples
A knowledge graph relationship can be represented as:
  (Subject, Predicate, Object)

  #for example
  (Home Loan, REQUIRES_SCORE, 720)
(Vehicle Loan, REQUIRES_SCORE, 680)
(Personal Loan, REQUIRES_SCORE, 700)

#lets create ground truth
  ground_truth_relations = {
    ("Home Loan", "REQUIRES_SCORE", 720),
    ("Vehicle Loan", "REQUIRES_SCORE", 680),
    ("Personal Loan", "REQUIRES_SCORE", 700)
}

  #Now imagine the extraction model predicts:
  predicted_relations = {
    ("Home Loan", "REQUIRES_SCORE", 720),
    ("Vehicle Loan", "REQUIRES_SCORE", 700),
    ("Personal Loan", "REQUIRES_SCORE", 700)
}
                     
The Vehicle Loan relationship is incorrect.
This is an important distinction: the entity may be correct, but the relationship or its value may be wrong.
  
6. Build a reusable evaluation function
Instead of writing the precision/recall formula repeatedly, create a reusable function.  

def evaluate_extraction(ground_truth, predictions):

    tp = len(ground_truth & predictions)
    fp = len(predictions - ground_truth)
    fn = len(ground_truth - predictions)

    precision = tp / (tp + fp) if (tp + fp) else 0

    recall = tp / (tp + fn) if (tp + fn) else 0

    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0
    )

    return {
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn
    }

    *********************8Important lines
tp counts correctly predicted relationships.
fp counts relationships predicted by the model that aren't in the ground truth.
fn counts expected relationships that the model missed.
The conditional expressions prevent division-by-zero errors.

          #Now run:
relation_results = evaluate_extraction(
    ground_truth_relations,
    predicted_relations
)

print(relation_results)

        #EXpected
{
    'precision': 0.667,
    'recall': 0.667,
    'f1': 0.667,
    'true_positives': 2,
    'false_positives': 1,
    'false_negatives': 1
}
A wrong relationship contributes both a false positive and a false negative when we use exact triple matching.

Part C — Graph retrieval evaluation
7. Evaluate whether graph retrieval finds the correct facts
#Suppose the user asks:
Which loan products require a credit score of at least 700?

Ground-truth answers:
expected_loans = {
    "Home Loan",
    "Personal Loan"
}
              #Suppose our graph retrival returns:
retrieved_loans = {
    "Home Loan"
}
              #Calculate recall:
matched = expected_loans & retrieved_loans

graph_recall = len(matched) / len(expected_loans)

print("Graph Retrieval Recall:", graph_recall)

Expected:
Graph Retrieval Recall: 0.5


Interpretation: the graph retriever found only half the required loan products.
Even if the LLM generates a fluent answer, the retrieval stage has already lost important information.
Production insight: Evaluate graph retrieval separately from answer generation. Otherwise, it becomes difficult to identify whether the problem originated in graph construction, graph querying or the LLM.

          
Part D — Multi-hop reasoning evaluation
8. What is multi-hop reasoning?
                          Home Loan
                    |
             REQUIRES_DOCUMENT
                    |
                    v
               Income Proof
                    |
                ISSUED_BY
                    |
                    v
                 Employer

    Now the user asks:
Which loan requires a document issued by an employer?

The system must traverse two relationships:      
          Home Loan
    |
    +--> Income Proof
              |
              +--> Employer      #This is a two-hop graph query.

          #IMPLEMENT MULTI HOP RETRIVAK WITH NETWOKX
import networkx as nx

bank_graph = nx.DiGraph()

bank_graph.add_edge(
    "Home Loan",
    "Income Proof",
    relationship="REQUIRES_DOCUMENT"
)

bank_graph.add_edge(
    "Income Proof",
    "Employer",
    relationship="ISSUED_BY"
)

bank_graph.add_edge(
    "Vehicle Loan",
    "Identity Proof",
    relationship="REQUIRES_DOCUMENT"
)

bank_graph.add_edge(
    "Identity Proof",
    "Government",
    relationship="ISSUED_BY"
)

          #Now query the graph:
def find_loans_by_issuer(graph, issuer):

    matching_loans = []#creates a list for results.

    for loan in ["Home Loan", "Vehicle Loan"]:

        for document in graph.successors(loan): #returns nodes directly connected by outgoing edges from the loan node.

            if graph.has_edge(document, issuer): #graph.has_edge(document, issuer) checks whether the document has a direct relationship to the requested issuer.

                matching_loans.append(loan) #stores the matching loan.

    return matching_loans

This is a simplified two-hop traversal. It assumes the graph follows our intended schema. In a production graph, we would also verify relationship types and avoid hardcoding the loan list.

#Test:
result = find_loans_by_issuer(
    bank_graph,
    "Employer"
)

print(result)

10. Evaluate multi-hop answer accuracy
We need a verified test dataset.

test_questions = [
    {
        "issuer": "Employer",
        "expected": ["Home Loan"]
    },
    {
        "issuer": "Government",
        "expected": ["Vehicle Loan"]
    }
]
#Evaluate:

correct = 0

for test in test_questions:

    predicted = find_loans_by_issuer(
        bank_graph,
        test["issuer"]
    )

    if set(predicted) == set(test["expected"]):
        correct += 1

accuracy = correct / len(test_questions)

print("Multi-hop Answer Accuracy:", accuracy)

Expected:
Multi-hop Answer Accuracy: 1.0

This evaluates exact-match correctness over two test cases. It is not enough to establish production reliability, but it demonstrates the evaluation pattern.

                    GRAPH RAG PIPELINE
                          |
              +-----------+-----------+
              |                       |
              v                       v
       Graph Construction       Graph Retrieval
              |                       |
       Entity Extraction         Query Execution
       Relation Extraction       Path Traversal
              |                       |
              v                       v
       Entity Precision          Retrieval Recall
       Entity Recall             Path Correctness
       Entity F1                 Multi-hop Accuracy
       Relation Precision              |
       Relation Recall                 |
       Relation F1                     |
              |                       |
              +-----------+-----------+
                          |
                          v
                    LLM Generation
                          |
                          v
                 Faithfulness / Grounding
                          |
                          v
                   Evaluation Report

--------------------------------------------------------------------------------------------------------------------------------------
**************************PRODUCTION RAG OBSERVABILITY: LOGGING,TRACING,LATENCY & MONITORING********************************************************

Today's objective is to make your RAG system observable: when something goes wrong, you should be able to identify where it happened, why it happened and how to investigate it.
This is an important distinction between a working RAG notebook and a production-ready AI application.

             1. Evaluation vs observability
Evaluation                                                         	Observability
Measures answer and retrieval quality	                              Explains system behavior during execution
Faithfulness, Recall@k, hallucination                              	Logs, traces, latency, token usage
Often runs on test datasets	                                        Often runs on live and test requests
Answers: How good is the system?	                                  Answers: What happened during this request?
We need both.

                               USER QUESTION
                        |
                        v
                   RAG PIPELINE
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
      RETRIEVAL     LLM GENERATION   EVALUATION
          |             |             |
          v             v             v
     Document IDs    Model Name    Faithfulness
     Chunk Scores    Token Usage   Answer Relevance
     Retrieval Time  LLM Latency   Hallucination
          |             |             |
          +-------------+-------------+
                        |
                        v
                 OBSERVABILITY
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
         LOGS         TRACES        METRICS
          |             |             |
          +-------------+-------------+
                        |
                        v
               MONITORING DASHBOARD
                        |
                        v
              DEBUGGING + IMPROVEMENT

2. The three pillars of observability
Logs: Individual records of what happened.

INFO  Request started
INFO  Retrieved 4 documents
INFO  LLM generation completed
ERROR Groq API request failed

Traces : Show how a request travels through multuple components.
Request ID: rag-001
|
+-- Retrieve Documents         180 ms
|   +-- Generate Query Embedding
|   +-- Vector Search
|
+-- Build Context               3 ms
|
+-- Generate Answer           940 ms
|
+-- Return Response

Metrics: Numerical measurements collected over time, such as request latency, error rate, retrieval counts and token consumption.
These are different from RAG quality metrics, although we can monitor both.

Part A — Implement observability using Python
We'll start without an external platform. This helps you understand what monitoring tools do internally.

3. Python logging

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("cortexrag")

#Line-by-line explanation
Code                         	Purpose
import logging	              Imports Python's built-in logging library
basicConfig()               	Configures logging output
level=logging.INFO           	Shows INFO, WARNING, ERROR and CRITICAL messages
%(asctime)s	                  Adds the timestamp
%(levelname)s               	Displays the severity
%(message)s                 	Displays the log message
getLogger("cortexrag")	      Creates a named logger

#Test it
logger.info("RAG application started")
logger.warning("Retrieval confidence is low")
logger.error("LLM request failed")

4.Measure execution time
Use Python's time.perf_counter() for elapsed-time measurement.

import time

start = time.perf_counter()

time.sleep(0.5)

end = time.perf_counter()

latency_ms = (end - start) * 1000

print(f"Latency: {latency_ms:.2f} ms")

Why perf_counter() instead of time.time()?
perf_counter() is appropriate for measuring elapsed durations because it uses a monotonic performance clock.
time.time() is useful for wall-clock timestamps, but clock adjustments can affect elapsed-time calculations.


Part B — Add observability to your RAG pipeline
                     
5. Instrument the existing RAG function
We'll reuse your existing variables:
- retriever
- prompt
- llm

import time
import uuid
import logging

logger = logging.getLogger("cortexrag")

def ask_rag_observed(question):

    request_id = str(uuid.uuid4())

    start_time = time.perf_counter()

    logger.info("Request started | id=%s", request_id)

    try:
        # Stage 1: Retrieval
        retrieval_start = time.perf_counter()

        docs = retriever.invoke(question)

        retrieval_ms = (
            time.perf_counter() - retrieval_start
        ) * 1000

        logger.info(
            "Retrieval completed | id=%s | count=%d | ms=%.2f",
            request_id,
            len(docs),
            retrieval_ms
        )

        # Stage 2: Context construction
        context = "\n\n".join(
            doc.page_content for doc in docs
        )

        # Stage 3: LLM generation
        generation_start = time.perf_counter()

        chain = prompt | llm

        response = chain.invoke({
            "context": context,
            "question": question
        })

        generation_ms = (
            time.perf_counter() - generation_start
        ) * 1000

        total_ms = (
            time.perf_counter() - start_time
        ) * 1000

        logger.info(
            "Generation completed | id=%s | ms=%.2f",
            request_id,
            generation_ms
        )

        return {
            "request_id": request_id,
            "answer": response.content,
            "retrieved_count": len(docs),
            "retrieval_ms": round(retrieval_ms, 2),
            "generation_ms": round(generation_ms, 2),
            "total_ms": round(total_ms, 2),
            "sources": [
                {
                    "source": doc.metadata.get("source"),
                    "page": doc.metadata.get("page"),
                    "content_type": doc.metadata.get("content_type")
                }
                for doc in docs
            ]
        }

    except Exception:
        logger.exception(
            "RAG request failed | id=%s",
            request_id
        )
        raise

Important concepts in this function
uuid.uuid4() generates a unique request identifier. It helps correlate logs from the same request.
try/except captures execution failures.
logger.exception() logs an error along with the Python traceback.
raise propagates the original exception rather than silently returning a misleading answer.
retrieval_ms measures retrieval latency.
generation_ms measures LLM generation latency.
total_ms measures the complete function's execution time.
The function also returns source metadata, which helps identify what documents were used.

#Test it
result = ask_rag_observed(
    "What is the minimum credit score for a vehicle loan?"
)

print("Answer:", result["answer"])
print("Request ID:", result["request_id"])
print("Retrieval latency:", result["retrieval_ms"])
print("Generation latency:", result["generation_ms"])
print("Total latency:", result["total_ms"])
print("Sources:", result["sources"])             

Your timing values will depend on your environment, retriever and API response time.
Production note: This is lightweight instrumentation, not full distributed tracing. It does not yet create nested spans or capture downstream service timings.

Part C — Token usage and cost monitoring
  
6. Track LLM token usage
Token consumption matters because model inference has usage limits and may incur costs.
With ChatGroq, an AIMessage may expose token information through usage_metadata.
For direct model calls:

 response = llm.invoke(
    "Explain RAG in one sentence."
)

print(response.content)
print(response.usage_metadata) 

  #you may see fields such as:

{
    "input_tokens": 15,
    "output_tokens": 20,
    "total_tokens": 35
}
These numbers are illustrative, not expected exact output.
You can extract them:

usage = response.usage_metadata or {}

input_tokens = usage.get("input_tokens", 0)
output_tokens = usage.get("output_tokens", 0)

print("Input tokens:", input_tokens)
print("Output tokens:", output_tokens)

****************************************IMP**********************************************
Part D — Production observability tools
You should recognize these three tools in interviews.

LangSmith
Useful for tracing LangChain and LangGraph executions, debugging chains, inspecting tool calls, managing datasets and running evaluations.

Langfuse
Useful for LLM tracing, prompt management, cost tracking and evaluation. Offers self-hosting options.

Arize Phoenix
Useful for OpenTelemetry-based tracing, RAG debugging, experiments and evaluations, including local workflows.

#7. Your independent coding task
Modify ask_rag_observed() to add the following to its return dictionary:
{    "input_tokens": ...,    "output_tokens": ...,    "total_tokens": ...}



Hint: When using a ChatPromptTemplate | ChatGroq chain, the returned object is usually an AIMessage, so inspect:
print(response.usage_metadata)



Use .get() to handle missing token fields safely.
8. Evaluation module completion checkpoint
Topic	Status
Contextual Precision, Recall, Relevancy	Covered
Faithfulness, Groundedness, Hallucination	Covered
DeepEval, RAGAS, LLM-as-a-Judge	Covered; execution quality to validate
GraphRAG evaluation	Covered
Logging, latency, token usage	Today's lesson
Full production monitoring integration	Later in project deployment
Your next major milestone is building a stateful, self-correcting RAG workflow, rather than continuing to accumulate evaluation libraries.

Next — Lesson 42: LangGraph Fundamentals
We'll build your first real LangGraph application, beginning with:
                    START
                      |
                      v
                 Receive Query
                      |
                      v
                Retrieve Documents
                      |
                      v
                 Generate Answer
                      |
                      v
                     END


Then we'll introduce StateGraph, TypedDict, nodes, edges, conditional routing and tool integration, one at a time.
After mastering those fundamentals, we'll expand the workflow into your planned Adaptive Agentic RAG with evidence grading, query rewriting, web fallback and hallucination checks.
This is where your previous work on RAG, GraphRAG and evaluation comes together into an AI Engineer portfolio project.

7. Your independent coding task
Modify ask_rag_observed() to add the following to its return dictionary:
                                                    {
    "input_tokens": ...,
    "output_tokens": ...,
    "total_tokens": ...
}
    Hint: When using a ChatPromptTemplate | ChatGroq chain, the returned object is usually an AIMessage, so inspect:
          print(response.usage_metadata)

  Use .get() to handle missing token fields safely.                   
