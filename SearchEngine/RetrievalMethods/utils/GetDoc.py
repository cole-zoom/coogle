import os
import zlib


def get_doc(store_path: str, docno: str, docnos: list, offsets):
    """
    Gets a document from the store.

    Args:
        store_path: The path to the store directory.
        docno: The DOCNO of the document to get.
        docnos: Pre-loaded list of document numbers.
        offsets: Pre-loaded document offsets array.

    Returns:
        The document content.
    """
    
    docs_file = os.path.join(store_path, "docs.bin")
    
    try:
        doc_index = docnos.index(docno)
    except ValueError:
        print(f"Error: DOCNO '{docno}' does not exist.")
        return ""
    
    # Read only needed document
    with open(docs_file, 'rb') as f:
        f.seek(offsets[doc_index])
        data_size = offsets[doc_index + 1] - offsets[doc_index]
        compressed_data = f.read(data_size)
        document_content = zlib.decompress(compressed_data).decode('utf-8')
        
        return document_content
