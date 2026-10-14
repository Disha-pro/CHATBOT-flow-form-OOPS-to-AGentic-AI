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
