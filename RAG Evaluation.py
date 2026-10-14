Our evaluation learning roadmap
Session    	Topics	                                                                        Practical outcome
1         	Contextual Precision, Contextual Recall, Contextual Relevancy                 	Evaluate retrieval quality
2          	Faithfulness, groundedness, answer relevancy, hallucination	                        Evaluate generated answers
3	      LLM-as-a-Judge, DeepEval, RAGAS, G-Eval                                       	Build automated evaluation tests
4	      GraphRAG evaluation	                                                            Measure entity, relationship and multi-hop retrieval quality
5          	Observability and production evaluation	                                          Track latency, cost, traces and quality regressions

#WHY DO WE NEED EVALUATION?
User Question
      ↓
Retriever (Pinecone / Vector DB)
      ↓
Retrieved Context
      ↓
LLM (Groq)
      ↓
Generated Answer

#Two fundamentally different failures can occur.
Retrieval failure: The retriever supplies irrelevant or incomplete evidence.
Generation failure: The retriever supplies correct evidence, but the LLM invents, omits or misinterprets information.

2#3 contextual evaluation metrics
User question:
What is the minimum credit score required for a vehicle loan?

#Suppose the retriever returns:
Chunk 1
Relevant
Vehicle loan applicants must have a minimum credit score of 680.

Chunk 2
Irrelevant
Home loan applicants require a minimum credit score of 720.

Chunk 3
Irrelevant
Credit card applicants must submit identity documentation.

A.CONTEXTUAL PRECISION
#Question it answers: Are the relevant chunks ranked near the top?
In RAG evaluation, contextual precision generally rewards placing relevant evidence higher in the retrieved ranking.
This is closely related to information-retrieval precision and ranking metrics.

For a simple, unranked example:
\[
\text{Precision@3}=\frac{\text{Relevant chunks in top 3}}{3}
\]

Here:
\[
\frac{1}{3}=0.333

#But DeepEval's ContextualPrecisionMetric is not simply Precision@k. It uses an LLM judge to assess relevance and calculate a ranking-sensitive score.

B.CONTEXTUAL RECALL
Question it answers: Did the retrieved context contain the information needed to answer correctly?

#Suppose the reference answer is:
A vehicle loan requires a minimum credit score of 680.
Chunk 1 contains that fact, so the retrieved context has sufficient evidence for this particular answer.
In a more complex question asking for income, credit score and tenure, 
retrieving only the credit score would leave important facts missing.

**Contextual recall focuses on coverage of the required answer information.
#Important: DeepEval's contextual recall is judged against an expected answer, whereas classical Recall@k requires knowing the relevant documents in the corpus. These are related but different evaluation approaches.

C.CONTEXTAUL RELEVANCY
Question it answers: How much of the retrieved context is actually useful for the question?

In our example, one chunk is relevant and two are distracting.
Contextual relevancy evaluates whether the retrieved content is relevant to the query. 
It is useful for detecting retrieval noise that can increase token costs and confuse generation.

  Metric	                  Core concern	Failure it detects
Contextual Precision	      Ranking	      Relevant chunks appear too low
Contextual Recall       	Coverage	      Required evidence is missing
Contextual Relevancy	      Relevance	      Retrieved context contains unnecessary information

      These three metrics overlap, but they are not interchangeable.

3#Hands-on: Evaluate retrieval without an LLM judge

import networkx as nx

graph = nx.DiGraph()

graph.add_node(
    "Home Loan",
    type="LoanProduct"
)

graph.add_node(
    "Vehicle Loan",
    type="LoanProduct"
)
graph.add_node(
    "Personal Loan",
    type="LoanProduct"
)
graph.add_edge(
    "Home Loan",
    "Credit Score",
    relationship="REQUIRES",
    minimum_score=720
)

graph.add_edge(
    "Vehicle Loan",
    "Credit Score",
    relationship="REQUIRES",
    minimum_score=680
)
graph.add_edge(
    "Personal Loan",
    "Credit Score",
    relationship="REQUIRES",
    minimum_score=700
)
from IPython.utils.path import target_outdated
for source,target,data in graph.edges(data=True):
  print(source,"->",target)
  print("Relationship: ",data["relationship"])
  print("Minimim Score: ",data["minimum_score"])
for source,target,data in graph.edges(data=True):
  if data["minimum_score"] >= 700:
    print(source)

def retrieve_graph_context(min_score):

    results = []

    for source, target, data in graph.edges(data=True):

        if data["minimum_score"] >= min_score:

            fact = (
                f"{source} requires a minimum "
                f"credit score of {data['minimum_score']}."
            )

            results.append(fact)

    return "\n".join(results)

--------------------
      
retrieved_ids = ["doc_vehicle", "doc_home", "doc_credit_card"] #Documents returned by your retriever, in ranked order

relevant_ids = {"doc_vehicle"} #Ground-truth documents known to be relevant

k = 3 #Evaluate the top three retrieved documents

top_k = retrieved_ids[:k] #Select the first k results

relevant_retrieved = [
    doc_id for doc_id in top_k
    if doc_id in relevant_ids   #Check whether each result is relevant
]

precision = len(relevant_retrieved) / len(top_k) #Count relevant retrieved documents
#Fraction of retrieved documents that are relevant - precision
recall = len(relevant_retrieved) / len(relevant_ids)

print("Precision@3:", precision) 
print("Recall@3:", recall)     #Fraction of all known relevant documents that were retrieved

4#DEEPEVAL - INDUSTRY ORIENTED EVALUATION
DeepEval provides evaluation test cases and metrics, including contextual precision, contextual recall and contextual relevancy.

Install:!pip install -q -U deepeval
#IMP components are:
from deepeval.test_case import LLMTestCase

from deepeval.metrics import (
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric
)

#step 1- Create a Test Case
test_case = LLMTestCase(
    input="What is the minimum credit score for a vehicle loan?",

    actual_output="The minimum credit score is 680.",

    expected_output="Vehicle loan applicants require a minimum credit score of 680.",

    retrieval_context=[
        "Vehicle loan applicants require a minimum credit score of 680.",
        "Home loan applicants require a minimum credit score of 720.",
        "Credit card applications require identity verification."
    ]
)
Understand these four parameters:
- input: the user's question.
- actual_output: the answer generated by your RAG system.
- expected_output: the verified reference answer.
- retrieval_context: the actual chunks returned by your retriever, preserving their ranking.

#step 2- Initialize metrics

precision_metric = ContextualPrecisionMetric(
    threshold=0.7
)

recall_metric = ContextualRecallMetric(
    threshold=0.7
)

relevancy_metric = ContextualRelevancyMetric(
    threshold=0.7

Here, threshold=0.7 sets the minimum passing score for each metric.
It is an evaluation policy, not a universal industry standard.

#Step 3- Measure the test cases
metrics = [
    precision_metric,
    recall_metric,
    relevancy_metric
]

for metric in metrics:
    metric.measure(test_case)

    print("Metric:", metric.__class__.__name__)
    print("Score:", metric.score)
    print("Reason:", metric.reason)
    print("Passed:", metric.is_successful())
    print("---")

Important: These contextual metrics require an LLM judge. Depending on your DeepEval version, the default evaluator may require an OpenAI API key and incur API costs.

Because you're using Groq, we'll configure a compatible custom evaluator in the next lesson rather than assume your Groq key works automatically with DeepEval's default model.
The scores will depend on the judge, evaluation rubric and model behavior; they are not fixed mathematical results.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
***************************** Faithfulness, Groundedness, Hallucination & LLM-as-a-Judge*****************************************************************************************
Today we're moving from retrieval evaluation to answer-generation evaluation

Even when our retriever finds the correct documents, can we trust the LLM's answer?
This is one of the most important production skills for a GenAI Engineer.


2#Four concepts you must distinguish
We'll use a fictional banking example.
                                                   
Question: What is the minimum credit score for a vehicle loan?
Retrieved context: Vehicle loan applicants must have a minimum credit score of 680.
                                                   
Consider three possible answers.
Answer A — Supported
"The minimum credit score is 680."
Faithful to the retrieved context and relevant to the question.
                                                   
Answer B — Unsupported
"The minimum credit score is 750."
Contradicts the evidence. This is a factual hallucination relative to the provided context.

Answer C — Off-topic
"Vehicle loans are popular financing products."
May be generally true, but doesn't answer the user's question.

Metric	      What it measures
Faithfulness	Whether claims in the answer are supported by retrieved evidence
Groundedness	Whether the answer is supported by the designated sources
Answer Relevancy	Whether the answer addresses the user's question
Hallucination	Whether the answer contains invented, unsupported or contradictory claims

Faithfulness and groundedness are closely related. Their precise scoring depends on the evaluation framework.
                                                   Hallucination is not always simply 1 - faithfulness, because evaluators may define different claim categories and scoring rules.

3#FAITHFULNESS - UNDERSTAND THE CALCULATION
#suppose the retrieved context contains:
Vehicle loan minimum score: 680. Maximum tenure: 84 months.

The LLM generates:
The minimum score is 680, the maximum tenure is 84 months, and the interest rate is 7%.

We can split the answer into three factual claims.
Minimum score is 680                 Supported
Maximum tenure is 84 months          Supported
Interest rate is 7%                  Unsupported

llustrative claim-support ratio
2 supported claims out of 3
0.67

A simple claim-level faithfulness formula is:
{Faithfulness}={Supported claims}/{Total factual claims}
This gives approximately 0.67.


In practice, RAGAS-style faithfulness uses an evaluator to extract and verify claims. 
DeepEval's faithfulness implementation may use a different rubric and aggregation, so scores from different frameworks are not necessarily interchangeable.

4#Answer relevancy — a different dimension
  Suppose the answer is:
Vehicle loans require a credit score of 680. Banks also offer home loans, personal loans and credit cards.

The answer contains the correct fact, but additional information may be unnecessary.
Answer relevancy asks whether the response directly addresses the user's question.

#An answer can be:
- Faithful but irrelevant.
- Relevant but unfaithful.
- Both faithful and relevant.
- Neither faithful nor relevant.

For production, we need both.                            


5#Hands-on: DeepEval evaluation test case
!pip install -q -U deepeval
#imports:
from deepeval.test_case import LLMTestCase

from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    HallucinationMetric
)

#Create the test case:
test_case = LLMTestCase(
    input="What is the minimum credit score for a vehicle loan?",

    actual_output=(
        "The minimum credit score is 680, "
        "and the interest rate is 7%."
    ),

    expected_output=(
        "The minimum credit score for a vehicle loan is 680."
    ),

    retrieval_context=[
        "Vehicle loan applicants require a minimum credit score of 680."
    ],

    context=[
        "Vehicle loan applicants require a minimum credit score of 680."
    ]
)
#Understand the difference
retrieval_context contains evidence retrieved by your RAG system.
context contains the reference material against which a metric such as DeepEval's HallucinationMetric can assess the answer.
In this example, they contain the same document, but they are separate fields because different metrics use different test-case inputs.

6#Initialize the metrics
faithfulness = FaithfulnessMetric(
    threshold=0.8
)

answer_relevancy = AnswerRelevancyMetric(
    threshold=0.8
)

hallucination = HallucinationMetric(
    threshold=0.2
)
#Important threshold difference:
For faithfulness and answer relevancy, higher scores are better.
For DeepEval's hallucination metric, lower scores are better. Here, 0.2 is the maximum acceptable score.
These thresholds are examples, not industry-wide standards.

7#Run the evaluation
metrics = [
    faithfulness,
    answer_relevancy,
    hallucination
]

for metric in metrics:

    metric.measure(test_case)

    print("Metric:", metric.__class__.__name__)
    print("Score:", metric.score)
    print("Reason:", metric.reason)
    print("Passed:", metric.is_successful())
    print("---")
The expected qualitative result is that the unsupported 7% interest-rate claim should reduce faithfulness and potentially increase the hallucination score.
However, the exact values are not deterministic. They depend on the evaluator model and framework implementation.
API configuration: DeepEval's default judge commonly relies on OpenAI. Since you're using Groq, this code may require an OpenAI API key unless you configure a compatible custom evaluation model. We'll address that next.         

8#LLM as Judge- how it works
An LLM-as-a-Judge is a language model used to evaluate another model's output against explicit criteria.
For example, you can use your Groq-hosted model to evaluate a RAG answer.
This is useful when you want to avoid immediately setting up a second evaluation provider.

#step 1 Create a judge schema
from pydantic import BaseModel, Field

class JudgeResult(BaseModel):

    score: float = Field(ge=0, le=1) #Field(ge=0, le=1) validates that the score is between zero and one.

    reason: str

    supported: bool

#Step 2 - Create the judge prompt
from langchain_core.prompts import ChatPromptTemplate

judge_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an evidence-grounding evaluator.

        Evaluate whether the answer is supported
        by the supplied context.

        Score from 0 to 1:
        1 = all factual claims supported
        0 = no factual claims supported

        Do not use outside knowledge.
        Explain unsupported claims.
        """
    ),
    (
        "human",
        """
        Question:
        {question}

        Context:
        {context}

        Answer:
        {answer}
        """
    )
])
#step 3 = Create the sructured judge
judge_llm = llm.with_structured_output(
    JudgeResult
)

judge_chain = judge_prompt | judge_llm
with_structured_output() asks the model to return data matching the Pydantic schema. Actual support depends on the model and provider integration.

#Step 4: Evaluates an answer
result = judge_chain.invoke({
    "question": "What is the minimum credit score for a vehicle loan?",

    "context": (
        "Vehicle loan applicants require "
        "a minimum credit score of 680."
    ),

    "answer": (
        "The minimum credit score is 680 "
        "and the interest rate is 7%."
    )
})

print("Score:", result.score)
print("Reason:", result.reason)
print("Supported:", result.supported)

The judge should identify that the interest rate is unsupported. But LLM judges can also make mistakes, so we must validate their reliability using known examples.
******This is a custom groundedness evaluator, not an exact reproduction of DeepEval's FaithfulnessMetric or RAGAS faithfulness.

9#**********Why LLM-as-a-Judge is important in production
LLM-based evaluation is useful for semantic properties that are difficult to assess using exact string comparisons.
But it introduces additional engineering concerns.
         
Concern	                     Production consideration
Judge reliability	               Compare judgments against human-labeled examples
Bias	                           A judge may favor certain wording or model outputs
Cost	                           Each evaluation may require additional LLM calls
Latency	                     Evaluating every live request can slow the application
Reproducibility	               Track judge model, prompts and evaluation versions
Security	                     Retrieved documents may contain prompt-injection instructions
  For your AI Engineer project, we'll use deterministic checks where possible and LLM-based evaluation where semantic judgment is necessary.

------------------------------------------------------------------------------------------------------------------------------------------------------------
**************************************Production RAG Evaluation with DeepEval, RAGAS & Groq*****************************************************************

                  RAG EVALUATION PIPELINE

                     User Question
                           |
                           v
                   Document Retriever
                           |
                           v
                    Retrieved Chunks
                           |
                           v
                     Groq LLM
                           |
                           v
                   Generated Answer
                           |
              +------------+------------+
              |                         |
              v                         v
       Retrieval Evaluation     Generation Evaluation
              |                         |
       Context Precision           Faithfulness
       Context Recall              Groundedness
       Context Relevancy           Answer Relevancy
       Precision@k                 Hallucination
       Recall@k                         |
              |                         |
              +------------+------------+
                           |
                           v
                    LLM-as-a-Judge
                           |
                           v
                   Evaluation Results
                           |
                           v
                Scores + Reasons + Logs
                           |
                           v
                Production Monitoring

2.# Understand the three tools
Tool	        Main purpose
DeepEval	  LLM evaluation metrics, test cases and automated tests
RAGAS	        RAG-focused evaluation metrics, including faithfulness and context quality
Groq	        Hosts the LLM that can generate answers or serve as an evaluation judge
#An important distinction:
DeepEval and RAGAS are evaluation frameworks.
Groq is a model inference provider, not an evaluation framework.
We'll first build a reusable judge with Groq, then connect it to DeepEval. This helps you understand the underlying mechanism rather than memorizing library-specific APIs.

!pip install -q -U deepeval ragas langchain-groq pydantic
question = "What is the minimum credit score for a vehicle loan?"

retrieved_contexts = [
    "Vehicle loan applicants require a minimum credit score of 680.",
    "Home loan applicants require a minimum credit score of 720."
]

actual_answer = (
    "The minimum credit score for a vehicle loan is 680."
)

expected_answer = (
    "A vehicle loan requires a minimum credit score of 680."
)

#Why these variables?
- question is the user's input.
- retrieved_contexts is a list of chunks returned by the retriever.
- actual_answer is the LLM's generated response.
- expected_answer is a human-verified reference answer.
In production, retrieved_contexts and actual_answer should come from your real RAG pipeline.

4#Connect Groq as a DeepEval Judge
DeepEval supports custom LLM evaluators through DeepEvalBaseLLM.
Recent documentation also explains why structured-output support matters for metrics such as faithfulness.

import os
from getpass import getpass
from langchain_groq import ChatGroq

if not os.getenv("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = getpass("Groq API key: ")

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

#BUILD THE CUSTOM EVALUATOR
from pydantic import BaseModel
from deepeval.models.base_model import DeepEvalBaseLLM

class GroqEvaluator(DeepEvalBaseLLM):

    def __init__(self, model):
        self.model = model

    def load_model(self):
        return self.model

    def generate(self, prompt: str, schema: type[BaseModel] | None = None):

        if schema is not None:
            structured_model = self.model.with_structured_output(schema)
            return structured_model.invoke(prompt)

        response = self.model.invoke(prompt)
        return response.content

    async def a_generate(
        self,
        prompt: str,
        schema: type[BaseModel] | None = None
    ):

        if schema is not None:
            structured_model = self.model.with_structured_output(schema)
            return await structured_model.ainvoke(prompt)

        response = await self.model.ainvoke(prompt)
        return response.content

    def get_model_name(self):
        return "Groq Evaluation Model"

This is the most important code in today's lesson.
Method	                   Responsibility
__init__()	                  Stores the LangChain model
load_model()	            Returns the stored model
generate()	                  Calls the model synchronously
a_generate()	            Calls the model asynchronously
schema	                  Specifies an expected Pydantic output structure
with_structured_output()	Requests validated, structured responses
get_model_name()	            Identifies the judge in evaluation records

#NOW INSTANTIATE IT :
groq_judge = GroqEvaluator(llm)

#EVALUATE FAITHGULNESS WITH DEEPEVAL
from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric

test_case = LLMTestCase(
    input=question,
    actual_output=actual_answer,
    expected_output=expected_answer,
    retrieval_context=retrieved_contexts
)

faithfulness_metric = FaithfulnessMetric(
    threshold=0.8,
    model=groq_judge,
    include_reason=True,
    async_mode=False
)

faithfulness_metric.measure(test_case)

print("Score:", faithfulness_metric.score)
print("Reason:", faithfulness_metric.reason)
print("Passed:", faithfulness_metric.is_successful())

                   LLMTestCase
                      |
          +-----------+-----------+
          |                       |
     Actual Answer          Retrieved Context
          |                       |
          +-----------+-----------+
                      |
                      v
             FaithfulnessMetric
                      |
                      v
                GroqEvaluator
                      |
                      v
             Extract/Assess Claims
                      |
                      v
               Score + Reason
                      |
                      v
                Pass or Fail

The metric's evaluation process checks factual alignment with retrieved context. DeepEval describes this as extracting and assessing claims against evidence. 

DeepEval - The LLM Evaluation Framework



A high score indicates stronger alignment according to that evaluator; it does not prove the underlying source itself is correct.

6#.EVALUATE THE SAME EXAMPLE USING RAGAS
         RAGAS uses a different test-case structure. Instead of LLMTestCase, we can use EvaluationDataset.
         The documented LangChain integration supports wrapping a LangChain model using LangchainLLMWrapper. 
                                                                
Step 1 — Prepare the evaluation dataset

from ragas import EvaluationDataset

dataset = EvaluationDataset.from_list([
    {
        "user_input": question,
        "retrieved_contexts": retrieved_contexts,
        "response": actual_answer,
        "reference": expected_answer
    }
])
#The fields correspond to:
RAGAS field       	Meaning
user_input	            User's question
retrieved_contexts	Evidence retrieved by RAG
response	            Generated answer
reference	            Verified expected answer         

Step 2 — Configure the evaluator
from ragas.llms import LangchainLLMWrapper
evaluator_llm = LangchainLLMWrapper(llm)

This adapts the LangChain model to the evaluator interface used by this RAGAS API.

Step 3 — Evaluate faithfulness and contextual recall
from ragas import evaluate
from ragas.metrics import Faithfulness, LLMContextRecall

results = evaluate(
    dataset=dataset,
    metrics=[
        Faithfulness(),
        LLMContextRecall()
    ],
    llm=evaluator_llm,
    raise_exceptions=False
)

print(results)

raise_exceptions=False allows failed metric computations to be reported without necessarily stopping the entire evaluation.
Inspect missing or NaN scores rather than treating them as successful evaluations.

7. DeepEval vs RAGAS — which should you use?
                                                                
Dimension                  	DeepEval     	RAGAS
RAG-specific metrics	      Yes	            Yes
Custom LLM judges       	Yes	            Yes
Automated test cases	      Strong focus	Supported through evaluation workflows
LLM application evaluation	Broad	             Strong RAG emphasis
GraphRAG evaluation  Custom metrics possible	Custom metrics possible

RAGAS is evolving, and newer releases also offer metric-specific scoring APIs. 
                                                                This example follows its documented dataset-based integration; if your installed version has changed the API, we'll adapt it based on the error.


8#************************G-EVAL CUSTOM EVALUATION CRITERIA
Suppose you want to evaluate whether your banking chatbot gives a clear, professional answer without inventing policy details.
DeepEval provides GEval for custom criteria.


from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams

banking_quality = GEval(
    name="Banking Answer Quality",
    criteria=(
        "Evaluate whether the answer directly addresses "
        "the user's banking question, is clear, and "
        "does not introduce unsupported policy claims."
    ),
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.RETRIEVAL_CONTEXT
    ],
    threshold=0.8,
    model=groq_judge,
    async_mode=False
)

banking_quality.measure(test_case)

print("Quality:", banking_quality.score)
print("Reason:", banking_quality.reason)

G-Eval is useful when standard metrics do not fully capture your application's requirements. However, one combined score can hide whether the problem was clarity, relevance or factual support. For serious testing, separate criteria are usually easier to diagnose.

                        EVALUATION DATASET
                  50-100+ Questions
                         |
                         v
                    Run RAG System
                         |
              +----------+----------+
              |                     |
              v                     v
       Retrieved Context       Generated Answer
              |                     |
              v                     v
       Retrieval Metrics      Generation Metrics
       - Precision@k          - Faithfulness
       - Recall@k             - Answer Relevancy
       - Context Recall       - Hallucination
       - Context Precision    - Groundedness
              |                     |
              +----------+----------+
                         |
                         v
                 Evaluation Report
                         |
                         v
             Compare with Previous Run
                         |
                         v
               Pass / Investigate / Fail
