import os
import sys
import json
import array

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from RetrievalMethods.BM25 import search as bm25_search
from RetrievalMethods.New_BM25 import search as new_bm25_search


class SearchEngine:
    """
    Main search engine class that loads all index files and manages retrieval.
    """
    
    def __init__(self, store_path: str):
        """
        Initialize the search engine with a store path.
        
        Args:
            store_path: The path to the store directory containing all index files.
        """
        self.store_path = store_path
        self.lexicon = None
        self.index_offsets = None
        self.docnos = None
        self.doc_lengths = None
        self.offsets = None
        
        # Load all index files
        self._load_index_files()
    
    def _load_index_files(self):
        """
        Load all index files and handle errors.
        """
        # Check if store directory exists
        if not os.path.exists(self.store_path):
            print(f"Error: Store directory '{self.store_path}' does not exist.\nPlease provide a valid store directory.")
            sys.exit(1)
        
        if not os.path.isdir(self.store_path):
            print(f"Error: '{self.store_path}' is not a directory.\nPlease provide a valid store directory.")
            sys.exit(1)
        
        # Define all required files
        docnos_text = os.path.join(self.store_path, "docnos.txt")
        inverted_index_file = os.path.join(self.store_path, "inverted_index.bin")
        index_offsets_file = os.path.join(self.store_path, "index_offsets.bin")
        lexicon_file = os.path.join(self.store_path, "lexicon.json")
        doc_lengths_file = os.path.join(self.store_path, "doc_lengths.txt")
        docs_file = os.path.join(self.store_path, "docs.bin")
        offsets_file = os.path.join(self.store_path, "offsets.bin")
        
        # Check if all required files exist
        missing_files = []
        for file_path, file_name in [
            (docnos_text, "docnos.txt"),
            (inverted_index_file, "inverted_index.bin"),
            (index_offsets_file, "index_offsets.bin"),
            (lexicon_file, "lexicon.json"),
            (doc_lengths_file, "doc_lengths.txt"),
            (docs_file, "docs.bin"),
            (offsets_file, "offsets.bin")
        ]:
            if not os.path.exists(file_path):
                missing_files.append(file_name)
        
        if missing_files:
            print(f"Error: The following files are missing: {', '.join(missing_files)}")
            sys.exit(1)
        
        # Load lexicon
        try:
            with open(lexicon_file, "r") as f:
                self.lexicon = json.load(f)
        except Exception as e:
            print(f"Error: {e}\nTry Re-creating the store directory or check the lexicon file.")
            sys.exit(1)
        
        # Load index offsets
        try:
            with open(index_offsets_file, 'rb') as f:
                self.index_offsets = array.array('I')
                self.index_offsets.frombytes(f.read())
        except Exception as e:
            print(f"Error: {e}\nTry Re-creating the store directory or check the index offsets file.")
            sys.exit(1)
        
        # Load docnos
        try:
            with open(docnos_text, "r") as f:
                docnos_content = f.read()
                self.docnos = docnos_content.strip().split('\n')
        except Exception as e:
            print(f"Error: {e}\nTry Re-creating the store directory or check the docnos file.")
            sys.exit(1)
        
        # Load doc lengths
        try:
            with open(doc_lengths_file, "r") as f:
                doc_lengths_content = f.read()
                self.doc_lengths = [int(length) for length in doc_lengths_content.strip().split('\n')]
        except Exception as e:
            print(f"Error: {e}\nTry Re-creating the store directory or check the doc lengths file.")
            sys.exit(1)
        
        # Load document offsets
        try:
            with open(offsets_file, 'rb') as f:
                self.offsets = array.array('I')
                self.offsets.frombytes(f.read())
        except Exception as e:
            print(f"Error: {e}\nTry Re-creating the store directory or check the offsets file.")
            sys.exit(1)
        
        # Validate loaded data
        if not self.doc_lengths:
            print(f'''
        Error: No doc lengths found in {doc_lengths_file}.
        
        Try Re-creating the store directory.
        ''')
            sys.exit(1)
        
        if not self.index_offsets:
            print(f'''
        Error: No index offsets found in {index_offsets_file}.
        
        Try Re-creating the store directory.
        ''')
            sys.exit(1)
        
        if not self.docnos:
            print(f'''
        Error: No docnos found in {docnos_text}.
        
        Try Re-creating the store directory.
        ''')
            sys.exit(1)
        
        if not self.lexicon:
            print(f'''
        Error: Empty lexicon found in {lexicon_file}.
        
        Try Re-creating the store directory.
        ''')
            sys.exit(1)
        
        if not self.offsets:
            print(f'''
        Error: No offsets found in {offsets_file}.
        
        Try Re-creating the store directory.
        ''')
            sys.exit(1)
    
    def search(self, query: str, method: str = "BM25"):
        """
        Search the index using the specified retrieval method.
        
        Args:
            query: The query string to search for.
            method: The retrieval method to use (default: "BM25").
            
        Returns:
            A list of search results.
        """
        if method == "BM25":
            return bm25_search(
                query=query,
                store_path=self.store_path,
                lexicon=self.lexicon,
                index_offsets=self.index_offsets,
                docnos=self.docnos,
                doc_lengths=self.doc_lengths,
                offsets=self.offsets
            )
        elif method == "New_BM25":
            return new_bm25_search(
                query=query,
                store_path=self.store_path,
                lexicon=self.lexicon,
                index_offsets=self.index_offsets,
                docnos=self.docnos,
                doc_lengths=self.doc_lengths,
                offsets=self.offsets
            )
        else:
            print(f"Error: Unknown retrieval method '{method}'")
            sys.exit(1)


if __name__ == "__main__":
    engine = SearchEngine("/Users/coledumanski/Documents/Workspace/MSE 543/mse-541-f25-hw5-cole-zoom/index")
    results = engine.search("gorbachev policy of glasnost world")
    
    for i, result in enumerate(results):
        if i == 10:
            break
        print(result)

