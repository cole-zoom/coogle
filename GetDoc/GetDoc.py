import array
import os
import sys
import zlib


def main():
    """
    Main function for GetDoc.

    Takes 3 parameters: store_path, lookup_type ("id" or "docno"), lookup_value
    """
    # Check number of arguments
    if len(sys.argv) != 4:
        print(f'''
        This program takes exactly three arguments. You have provided {len(sys.argv)-1} arguments.
        
        Usage: python GetDoc.py <store_path> <lookup_type> <lookup_value>

        Arguments:
          store_path     Path to the directory containing docs.bin, offsets.bin, and metadata.bin
          lookup_type    Either "id" or "docno" to specify the type of lookup
          lookup_value   Either an internal integer ID or a DOCNO string
          
        Examples:
          python GetDoc.py ./output/ id 5
          python GetDoc.py ./output/ docno LA010189-0001
        ''')
        sys.exit(1)
    
    store_path = sys.argv[1]
    lookup_type = sys.argv[2]
    docno = sys.argv[3]
    
    # Validate lookup_type
    if lookup_type not in ["id", "docno"]:
        print(f'''
        Error: Invalid lookup type '{lookup_type}'.
        
        The lookup_type must be either "id" or "docno".
        You provided: {lookup_type}
        ''')
        sys.exit(1)
    
    # Check if store directory exists
    if not os.path.exists(store_path):
        print(f"Error: Store directory '{store_path}' does not exist.\nPlease provide a valid store directory.")
        sys.exit(1)
    
    if not os.path.isdir(store_path):
        print(f"Error: '{store_path}' is not a directory.\nPlease provide a valid store directory.")
        sys.exit(1)
    
    # Check if required files exist
    docs_file = os.path.join(store_path, "docs.bin")
    offsets_file = os.path.join(store_path, "offsets.bin")
    docnos_text = os.path.join(store_path, "docnos.txt")
    
    missing_files = []
    for file_path, file_name in [(docs_file, "docs.bin"), (offsets_file, "offsets.bin"), (docnos_text, "docnos.txt")]:
        if not os.path.exists(file_path):
            missing_files.append(file_name)
    
    if missing_files:
        print(f'''
        Error: Required files are missing from store directory '{store_path}':
        {', '.join(missing_files)}
        
        The store directory must contain: docs.bin, offsets.bin, metadata.bin
        ''')
        sys.exit(1)
    
    try:
        with open(docnos_text, "r") as f:
            docnos_content = f.read()
            docnos = docnos_content.strip().split('\n')

        if not docnos[0].strip():
            print(f'''
            Error: No DOCNOs found in {docnos_text}.
            
            The docnos.txt file must contain at least one DOCNO.
            ''')
            sys.exit(1)
        
        with open(offsets_file, 'rb') as f:
            offsets = array.array('I')
            offsets.frombytes(f.read())

        if not offsets:
            print(f'''
            Error: No offsets found in {offsets_file}.
            
            Try Re-creating the store directory.
            ''')
            sys.exit(1)
        
        # Determine document index
        if lookup_type == "id":
            try:
                doc_index = int(docno)
                docno = docnos[doc_index]
                if doc_index < 0 or doc_index >= len(offsets):
                    print(f'''
                    Error: Internal ID {doc_index} does not exist.
                    
                    Valid internal IDs range from 0 to {len(offsets)-1}.
                    Total documents in store: {len(offsets)}
                    ''')
                    sys.exit(1)
            except ValueError:
                print(f'''
                Error: Invalid internal ID '{docno}'.
                
                When using lookup_type "id", the lookup_value must be a valid integer.
                ''')
                sys.exit(1)
            except IndexError:
                print(f'''
                Error: Internal ID {doc_index} does not exist.
                
                Valid internal IDs range from 0 to {len(docnos)-1}.
                Total documents in store: {len(docnos)}
                ''')
                sys.exit(1)
        
        elif lookup_type == "docno":
            try:
                doc_index = docnos.index(docno)
            except ValueError:
                print(f'''
                Error: DOCNO '{docno}' does not exist.
                
                Available DOCNOs: {len(docnos)} documents in store.
                Use lookup_type "id" with values 0-{len(docnos)-1} to browse documents.
                ''')
                sys.exit(1)
        
        # Read only needed document
        with open(docs_file, 'rb') as f:
            f.seek(offsets[doc_index])
            data_size = offsets[doc_index + 1] - offsets[doc_index]
            compressed_data = f.read(data_size)
            document_content = zlib.decompress(compressed_data).decode('utf-8')
            
            print(document_content)
            return document_content
    
    except (OSError, IOError) as e:
        print(f"Error reading store files: {e}")
        sys.exit(1)
    except zlib.error as e:
        print(f"Error decompressing document: {e}")
        sys.exit(1)
    except UnicodeDecodeError as e:
        print(f"Error decoding document content: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
