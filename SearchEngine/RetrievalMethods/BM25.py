import os
import sys
import json
import zlib
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from RetrievalMethods.utils.tokenize_utils import tokenize
from RetrievalMethods.utils.score_utils import bm25_score
from RetrievalMethods.utils.GetDoc import get_doc
from RetrievalMethods.utils.query_utils import get_query_biased_summary

def search(query: str, store_path: str, lexicon: dict, index_offsets, docnos: list, doc_lengths: list, offsets):
    """
    Searches the store for the given query using the BM25 retrieval method.
    
    Args:
        query: The query to search for.
        store_path: The path to the store directory.
        lexicon: Pre-loaded lexicon dictionary.
        index_offsets: Pre-loaded index offsets array.
        docnos: Pre-loaded list of document numbers.
        doc_lengths: Pre-loaded list of document lengths.
        offsets: Pre-loaded document offsets array.

    Returns:
        A list of results.
    """
    inverted_index_file = os.path.join(store_path, "inverted_index.bin")

    # Tokenize query
    all_results = []
    tokens = []
    tokenize(query, tokens)

    query_postings = []
    
    # Get postings for each token in the query
    for token in tokens:
        token_id = None
        if token in lexicon:
            token_id = lexicon[token]
        if token_id is not None:
            with open(inverted_index_file, 'rb') as index_file:
                index_file.seek(index_offsets[token_id])
                data_size = index_offsets[token_id + 1] - index_offsets[token_id]
                compressed_data = index_file.read(data_size)
                postings = zlib.decompress(compressed_data).decode('utf-8')
                postings = json.loads(postings)
                query_postings.append(postings)

    if not query_postings:
        print(f"Warning: No results found for {query}")
        return []

    result_set = {}

    # Get BM25 Scores for each document
    average_doc_length = sum(doc_lengths) / len(doc_lengths)
    for i, query_posting in enumerate(query_postings):

        for j in range(0, len(query_posting), 2):
            doc_id = query_posting[j]
            term_frequency = query_posting[j+1]
            doc_length = doc_lengths[doc_id]
            score = bm25_score(term_frequency, doc_length, average_doc_length, len(doc_lengths), len(query_posting)/2)
            if doc_id not in result_set:
                result_set[doc_id] = score
            else:
                result_set[doc_id] += score

    sorted_result_set = sorted(result_set.items(), key=lambda x: x[1], reverse=True)[:1000]

    # Get biased query for each document
    for i, (doc_id, score) in enumerate(sorted_result_set):
        if i < 10:
            docno = docnos[doc_id]

            # Get document content to extract headline, date, and biased query
            doc_content = get_doc(store_path, docno, docnos, offsets)
            lines = doc_content.split("\n")
            date = ""
            headline = ""
            raw_document = ""

            for line in lines:
                if "date:" in line:
                    date = line.split("date:")[1].strip()
                elif "headline:" in line:
                    headline = line.split("headline:")[1].strip()
                    
            raw_document = doc_content.split("raw document:")[1].strip()

            # Get biased query from document content and query tokens

            
            biased_query = get_query_biased_summary(tokens, raw_document)

            if not headline:
                headline = biased_query[:50].strip() + "..."

            all_results.append({
                "docno": docno,
                "date": date,
                "headline": headline,
                "biased_query": biased_query,
                "rank": i + 1
            })
        else:
            docno = docnos[doc_id]
            all_results.append({
                "docno": docno,
                "rank": i + 1
            })
    return all_results
