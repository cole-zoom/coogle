import array
import gzip
import json
import os
import sys
import zlib
try:
    from utils.date_utils import convert_month_to_letter
    from utils.tokenize_utils import convert_tokens_to_ids, add_to_postings, tokenize_and_stem
except ImportError:
    from .utils.date_utils import convert_month_to_letter
    from .utils.tokenize_utils import convert_tokens_to_ids, add_to_postings, tokenize_and_stem

def main():
    """
    Main function for the IndexEngine.
    
    Takes in 2 parameters: the path to documents and path to output
    """
    # Check number of arguments
    if len(sys.argv) != 3:
        print(f'''
        This program takes in two arguments. You have provided {len(sys.argv)-1} arguments.
        
        Usage: python IndexEngine.py <documents_file> <output_path>

        Arguments:
        documents_file  Path to the gzip file containing documents to index
        output_path     Path where the index and metadata will be stored
        ''')
        
        sys.exit(1)
    
    documents_file = sys.argv[1]
    output_path = sys.argv[2]
    
    # Check argument validity
    if not os.path.exists(documents_file):
        print(f"Error: Documents file '{documents_file}' does not exist.\nPlease provide a valid documents file.")
        sys.exit(1)
    
    if not os.path.isfile(documents_file):
        print(f"Error: '{documents_file}' is not a file.\nPlease provide a valid documents file.")
        sys.exit(1)
    
    if os.path.exists(output_path):
        print(f'''
        Error: Output directory '{output_path}' already exists.

        This program will not overwrite existing directories to prevent data loss.
        Please choose a different output path or remove the existing directory.
        ''')
        sys.exit(1)
    
    # Create output directory
    try:
        os.makedirs(output_path, exist_ok=False)
        print(f"Created output directory: {output_path}")
    except OSError as e:
        print(f"Error creating output directory '{output_path}': {e}\nPlease provide a valid output path.")
        sys.exit(1)
    
    print(f"Indexing documents from: {documents_file}")
    print(f"Output will be stored in: {output_path}")

    documents = []
    docnos = []
    lexicon = {}
    inverted_index = []
    doc_lengths = array.array('I')

    # Decode and append documents
    try:
        with gzip.open(documents_file, 'rt', encoding='utf-8') as f:
            document = []
            is_headline = False
            is_text = False
            is_graphic = False
            index = 0
            for line in f:
                if "<DOC>" in line:
                    document = []
                    document.append(line)
                    headline = ""
                    word_counts = {}
                    doc_length = 0
                elif "</DOC>" in line:
                    metadata_string = f"docno: {DOCNO}\ninternal id: {index}\ndate: {date}\nheadline: {headline}\nraw document:\n"
                    document.append(line)
                    documents.append(metadata_string + "".join(document))
                    add_to_postings(word_counts, index, inverted_index)
                    doc_lengths.append(doc_length)
                    index += 1
                elif "<DOCNO>" in line:
                    DOCNO = line.replace('<DOCNO>', '').replace('</DOCNO>', '').strip()
                    docnos.append(DOCNO)
                    date = f"{convert_month_to_letter(DOCNO[2:4])} {DOCNO[4:6]}, 19{DOCNO[6:8]}"
                    document.append(line)
                elif "<HEADLINE>" in line:
                    if "</HEADLINE>" in line:
                        document.append(line)
                        headline = line.replace('<HEADLINE>', '').replace('</HEADLINE>', '').strip()
                        words = []
                        tokenize_and_stem(headline, words)
                        doc_length += len(words)
                        convert_tokens_to_ids(words, lexicon, word_counts)
                        continue
                    is_headline = True
                    document.append(line)
                elif "</HEADLINE>" in line:
                    is_headline = False
                    document.append(line)
                elif is_headline:
                    if line and not "<" in line:
                        headline += f"{line.strip()} "
                        text = line.strip()
                        words = []
                        tokenize_and_stem(text, words)
                        doc_length += len(words)
                        convert_tokens_to_ids(words, lexicon, word_counts)
                    document.append(line)
                elif "<TEXT>" in line:
                    if "</TEXT>" in line:
                        document.append(line)
                        text = line.replace('<TEXT>', '').replace('</TEXT>', '').strip()
                        words = []
                        tokenize_and_stem(text, words)
                        doc_length += len(words)
                        convert_tokens_to_ids(words, lexicon, word_counts)
                        continue
                    is_text = True
                    document.append(line)
                elif "</TEXT>" in line:
                    is_text = False
                    document.append(line)
                elif is_text:
                    if line and not "<" in line:
                        text = line.strip()
                        words = []
                        tokenize_and_stem(text, words)
                        doc_length += len(words)
                        convert_tokens_to_ids(words, lexicon, word_counts)
                    document.append(line)
                elif "<GRAPHIC>" in line:
                    if "</GRAPHIC>" in line:
                        document.append(line)
                        graphic = line.replace('<GRAPHIC>', '').replace('</GRAPHIC>', '').strip()
                        words = []
                        tokenize_and_stem(graphic, words)
                        doc_length += len(words)
                        convert_tokens_to_ids(words, lexicon, word_counts)
                        continue
                    is_graphic = True
                    document.append(line)
                elif "</GRAPHIC>" in line:
                    is_graphic = False
                    document.append(line)
                elif is_graphic:
                    if line and not "<" in line:
                        graphic = line.strip()
                        words = []
                        tokenize_and_stem(graphic, words)
                        doc_length += len(words)
                        convert_tokens_to_ids(words, lexicon, word_counts)
                    document.append(line)
                else:
                    document.append(line)
    except (OSError, IOError, gzip.BadGzipFile, zlib.error) as e:
        print(f"Error reading gzip file '{documents_file}': {e}")
        sys.exit(1)
    except UnicodeDecodeError as e:
        print(f"Error decoding file '{documents_file}': {e}")
        sys.exit(1)
    
    if not documents:
        print(f"Warning: No documents found in '{documents_file}'")
    
    print(f"Found {len(documents)} documents to index")
    
    offsets = array.array('I')
    index_offsets = array.array('I')
    
    # Write files
    try:
        offset = 0
        with open(f"{output_path}/docs.bin", "wb") as docbin:
            for doc in documents:
                offsets.append(offset)
                zipped_doc = zlib.compress(doc.encode('utf-8'))
                docbin.write(zipped_doc)
                offset += len(zipped_doc)
        offsets.append(offset)
    except (OSError, IOError) as e:
        print(f"Error writing to docs.bin: {e}")
        sys.exit(1)
            
    try:
        with open(f"{output_path}/offsets.bin", "wb") as offsetbin:
            offsets.tofile(offsetbin)
    except (OSError, IOError) as e:
        print(f"Error writing to offsets.bin: {e}")
        sys.exit(1)

    try:
        offset = 0
        with open(f"{output_path}/inverted_index.bin", "wb") as invertedindexbin:
            for posting in inverted_index:
                index_offsets.append(offset)
                zipped_posting = zlib.compress(json.dumps(posting).encode('utf-8'))
                invertedindexbin.write(zipped_posting)
                offset += len(zipped_posting)
        index_offsets.append(offset)
    except (OSError, IOError) as e:
        print(f"Error writing to inverted_index.bin: {e}")
        sys.exit(1)

    try:
        with open(f"{output_path}/index_offsets.bin", "wb") as indexoffsetsbin:
            index_offsets.tofile(indexoffsetsbin)
    except (OSError, IOError) as e:
        print(f"Error writing to index_offsets.bin: {e}")
        sys.exit(1)

    try: 
        with open(f"{output_path}/docnos.txt", "w") as docnostxt:
            for docno in docnos:
                docnostxt.write(f"{docno}\n")
    except (OSError, IOError) as e:
        print(f"Error writing to docnos.txt: {e}")
        sys.exit(1)

    try:
        with open(f"{output_path}/doc_lengths.txt", "w") as doclengthstxt:
            for doc_length in doc_lengths:
                doclengthstxt.write(f"{doc_length}\n")
    except (OSError, IOError) as e:
        print(f"Error writing to doc_lengths.txt: {e}")
        sys.exit(1)

    try:
        with open(f"{output_path}/lexicon.json", "w") as lexiconjson:
            json.dump(lexicon, lexiconjson)
    except (OSError, IOError) as e:
        print(f"Error writing to lexicon.json: {e}")
        sys.exit(1)

    print(f"Output files created: docs.bin, offsets.bin, docnos.txt, doc_lengths.txt, lexicon.json, inverted_index.bin, index_offsets.bin")

if __name__ == "__main__":
    main()
