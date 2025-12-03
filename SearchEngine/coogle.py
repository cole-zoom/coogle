import sys
import os
import SearchEngine
import time
from RetrievalMethods.utils.GetDoc import get_doc

def main():
    if len(sys.argv) != 2:
        print(f"Usage: python coogle.py <index_path>")
        sys.exit(1)

    # Create engine from index with error handling
    index_path = sys.argv[1]
    
    # Check if index path exists before creating engine
    if not os.path.exists(index_path):
        print(f"Error: Index path '{index_path}' does not exist.")
        print("Please provide a valid index directory path.")
        sys.exit(1)
    
    if not os.path.isdir(index_path):
        print(f"Error: '{index_path}' is not a directory.")
        print("Please provide a valid index directory path.")
        sys.exit(1)
    
    # Coogle logo
    print("\n")
    print("   \033[94m██████\033[0m  \033[91m██████\033[0m   \033[93m██████\033[0m   \033[94m█████\033[0m  \033[92m██\033[0m      \033[91m███████\033[0m")
    print("  \033[94m██\033[0m      \033[91m██\033[0m    \033[91m██\033[0m \033[93m██\033[0m    \033[93m██\033[0m \033[94m██\033[0m      \033[92m██\033[0m      \033[91m██\033[0m     ")
    print("  \033[94m██\033[0m      \033[91m██\033[0m    \033[91m██\033[0m \033[93m██\033[0m    \033[93m██\033[0m \033[94m██\033[0m  \033[94m███\033[0m \033[92m██\033[0m      \033[91m█████\033[0m   ")
    print("  \033[94m██\033[0m      \033[91m██\033[0m    \033[91m██\033[0m \033[93m██\033[0m    \033[93m██\033[0m \033[94m██\033[0m   \033[94m██\033[0m \033[92m██\033[0m      \033[91m██\033[0m     ")
    print("   \033[94m██████\033[0m  \033[91m██████\033[0m   \033[93m██████\033[0m   \033[94m█████\033[0m  \033[92m███████\033[0m \033[91m███████\033[0m")
    print("\n")
    
    # Loading bar
    print("Loading search engine", end="")
    sys.stdout.flush()
    bar_length = 30
    for i in range(0,bar_length + 1,5):
        progress = int((i / bar_length) * 100)
        bar = "█" * i + "░" * (bar_length - i)
        print(f"\r[{bar}] {progress}%", end="")
        sys.stdout.flush()
        time.sleep(0.03)
    print("\n")
    
    try:
        engine = SearchEngine.SearchEngine(index_path)
    except Exception as e:
        print(f"Error loading index: {e}")
        print("Please ensure the index path contains valid index files.")
        sys.exit(1)
    
    print("Welcome to Coogle! Enter a query to search the index.\n")
    search_method = "BM25"

    # Main Application Loop
    while True:
        query = input("\nEnter a query: ")

        start_time = time.perf_counter()
        results = engine.search(query, search_method)
        end_time = time.perf_counter()
        
        # Check if there are any results
        if not results:
            print("No results found for your query.\n")
            continue
        
        for result in results[:10]:
            print(f"{result['rank']}. {result['headline']} ({result['date']})\n{result['biased_query']} ({result['docno']})")
            print("\n")

        print(f"\nFound results in: {end_time - start_time:.4f} seconds\n")
        # View Document Loop
        while True:
            print("Type a valid rank to view the full document, type 'n' to continue searching, or type 'q' to quit.")
            rank = input("Enter a rank: ")
            print("\n")
            if rank == "n":
                break
            elif rank == "q":
                sys.exit(0)
            elif rank.isdigit():
                rank_num = int(rank)
                # Check if rank is within valid range
                if rank_num < 1:
                    print("Invalid rank. Please enter a rank greater than 0.\n")
                elif rank_num > len(results):
                    print(f"Invalid rank. Please enter a valid rank between 1 and {len(results)}.\n")
                else:
                    try:
                        doc_content = get_doc(engine.store_path, results[rank_num-1]['docno'], engine.docnos, engine.offsets)
                        print(doc_content)
                    except Exception as e:
                        print(f"Error retrieving document: {e}\n")
            else:
                print("Invalid rank. Please enter a valid rank.\n")

if __name__ == "__main__":
    main()