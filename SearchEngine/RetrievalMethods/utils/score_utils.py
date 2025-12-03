import math

def bm25_score(term_frequency: int, doc_length: int, avg_doc_length: int, num_docs: int, num_docs_containing_term: int) -> float:
    """
    Calculates the BM25 score for a given term frequency and document length.
    """
    k = 1.2 * ((1-0.75) + 0.75 * (doc_length / avg_doc_length))
    return (term_frequency / (k + term_frequency)) * math.log((num_docs-num_docs_containing_term+0.5)/(num_docs_containing_term+0.5))

def cosine_similarity_score(term_frequency: int, num_docs: int, num_docs_containing_term: int) -> float:
    """
    Calculates the magnitude of a document.
    """
    return (1 + math.log(term_frequency)) * math.log(1 + (num_docs / num_docs_containing_term))