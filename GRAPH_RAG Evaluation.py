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
