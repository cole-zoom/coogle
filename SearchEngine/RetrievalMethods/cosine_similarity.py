import os
import sys
import json
import array
import zlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.tokenize_utils import tokenize
from utils.score_utils import cosine_similarity_score

def main():
    if len(sys.argv) != 4:
        print(f'''
        This program takes exactly three arguments. You have provided {len(sys.argv)-1} arguments.
        
        Usage: python QueryEngine.py <store_path> <topic_path> <results_path>

        Arguments:
          store_path     Path to the directory containing index files
          topic_path     Path to the topic file
          results_path   Path to the directory to store the results
          
        Examples:
          python QueryEngine.py ./output/ topics/topic_index.txt ./output/results.txt
        ''')
        sys.exit(1)

    store_path = sys.argv[1]
    topic_path = sys.argv[2]
    results_path = sys.argv[3]

    if not os.path.exists(store_path):
        print(f"Error: Store directory '{store_path}' does not exist.\nPlease provide a valid store directory.")
        sys.exit(1)
    
    if not os.path.exists(topic_path):
        print(f"Error: Topic file '{topic_path}' does not exist.\nPlease provide a valid topic file.")
        sys.exit(1)

    if topic_path[-4:] != ".txt":
        print(f"Error: Topic file '{topic_path}' is not a text file.\nPlease provide a valid path to the topic file.")
        sys.exit(1)

    if results_path[-4:] != ".txt":
        print(f"Error: Results file '{results_path}' is not a text file.\nPlease provide a valid path to the results file.")
        sys.exit(1)

    if os.path.exists(results_path):
        print(f'''
        Error: Results directory '{results_path}' already exists.

        This program will not overwrite existing directories to prevent data loss.
        Please choose a different output path or remove the existing directory.
        ''')
        sys.exit(1)

    topics = []

    with open(topic_path, "r") as topic_index_file:
        i = 0
        for line in topic_index_file:
            if i % 2 == 0:
                topic_id = line.strip()
            else:
                topic_title = line.strip()
                topics.append([topic_id, topic_title])
            i += 1

    if not topics:
        print(f'''
        Error: No topics found in {topic_path}.
        
        Try populating the topic file with topics! Make sure the topic file is in the correct format.
        ''')
        sys.exit(1)

    docs_file = os.path.join(store_path, "docs.bin")
    offsets_file = os.path.join(store_path, "offsets.bin")
    docnos_text = os.path.join(store_path, "docnos.txt")
    inverted_index_file = os.path.join(store_path, "inverted_index.bin")
    index_offsets_file = os.path.join(store_path, "index_offsets.bin")
    lexicon_file = os.path.join(store_path, "lexicon.json")
    doc_magnitudes_file = os.path.join(store_path, "doc_magnitudes.txt")

    missing_files = []
    for file_path, file_name in [(docs_file, "docs.bin"), (offsets_file, "offsets.bin"), (docnos_text, "docnos.txt"), (inverted_index_file, "inverted_index.bin"), (index_offsets_file, "index_offsets.bin"), (lexicon_file, "lexicon.json"), (doc_magnitudes_file, "doc_magnitudes.txt")]:
        if not os.path.exists(file_path):
            missing_files.append(file_name)
    
    if missing_files:
        print(f"Error: The following files are missing: {', '.join(missing_files)}")
        sys.exit(1)

    try:
        with open(lexicon_file, "r") as f:
            lexicon = json.load(f)
    except Exception as e:
        print(f"Error: {e}\nTry Re-creating the store directory or check the lexicon file.")
        sys.exit(1)

    try:
        with open(index_offsets_file, 'rb') as f:
                index_offsets = array.array('I')
                index_offsets.frombytes(f.read())
    except Exception as e:
        print(f"Error: {e}\nTry Re-creating the store directory or check the index offsets file.")
        sys.exit(1)

    try:
        with open(docnos_text, "r") as f:
            docnos_content = f.read()
            docnos = docnos_content.strip().split('\n')
    except Exception as e:
        print(f"Error: {e}\nTry Re-creating the store directory or check the docnos file.")
        sys.exit(1)

    try:
        with open(doc_magnitudes_file, "r") as f:
            doc_magnitudes_content = f.read()
            doc_magnitudes = [float(magnitude) for magnitude in doc_magnitudes_content.strip().split('\n')]
    except Exception as e:
        print(f"Error: {e}\nTry Re-creating the store directory or check the doc magnitudes file.")
        sys.exit(1)

    if not doc_magnitudes:
        print(f'''
        Error: No doc magnitudes found in {doc_magnitudes_file}.
        
        Try Re-creating the store directory.
        ''')
        sys.exit(1)

    if not index_offsets:
        print(f'''
        Error: No index offsets found in {index_offsets_file}.
        
        Try Re-creating the store directory.
        ''')
        sys.exit(1)

    if not docnos:
        print(f'''
        Error: No docnos found in {docnos_text}.
        
        Try Re-creating the store directory.
        ''')
        sys.exit(1)

    if not lexicon:
        print(f'''
        Error: Empty lexicon found in {lexicon_file}.
        
        Try Re-creating the store directory.
        ''')
        sys.exit(1)

    try:

        # Search each topic
        all_results = []
        for topic in topics:
            topic_results = []
            topic_id = topic[0]
            tokens = []
            tokenize(topic[1], tokens)

            query_postings = []
            
            # Get postings for each token in the topic
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
                print(f"Warning: No postings found for topic {topic_id}")
                continue

            result_set = {}

            # Get BM25 Scores for each document
            for i, query_posting in enumerate(query_postings):

                for j in range(0, len(query_posting), 2):
                    doc_id = query_posting[j]
                    term_frequency = query_posting[j+1]
                    score = cosine_similarity_score(term_frequency, len(doc_magnitudes), len(query_posting)/2)
                    if doc_id not in result_set:
                        result_set[doc_id] = score
                    else:
                        result_set[doc_id] += score

            for doc_id in result_set:
                result_set[doc_id] /= doc_magnitudes[doc_id]

            sorted_result_set = sorted(result_set.items(), key=lambda x: x[1], reverse=True)[:1000]
            for i, (doc_id, score) in enumerate(sorted_result_set):
                docno = docnos[doc_id]
                topic_results.append({
                    "topicID": topic_id,
                    "Q0": "Q0",
                    "docno": docno,
                    "rank": i+1,
                    "score": score,
                    "runTag": "cadumansCosineSimilarity"
                })
            all_results.extend(topic_results)
    
    except IndexError as e:
        print(f"Error: {e}\nTry Re-creating the store directory or check the topic file.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}\nTry Re-creating the store directory or check the topic file.")
        sys.exit(1)

    try:
        with open(results_path, "w") as f:
            for result in all_results:
                    f.write(f"{result['topicID']} {result['Q0']} {result['docno']} {result['rank']} {result['score']} {result['runTag']}\n")
    except Exception as e:
        print(f"Error: {e}\nresults path is invalid.")
        sys.exit(1)
        

       

if __name__ == "__main__":
    main()