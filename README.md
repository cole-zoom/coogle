# HW5

## Cole Dumanski | cadumans

## Set up repo

Clone repo then run the following commands to set up your repository:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Installing Requirements

After activating the virtual environment, install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running the IndexEngine

The basic command to build the index:

```bash
python IndexEngine/IndexEngine.py <documents_file> <output_path>
```

#### Arguments:

- `documents_file`: Path to the gzip file containing documents to index
- `output_path`: Path where the index and metadata will be stored

#### Example:

```bash
python IndexEngine/IndexEngine.py data/latimes.gz index
```

#### Output:

The IndexEngine creates the following files in the output directory:

- `docs.bin` - Compressed binary file containing all documents
- `offsets.bin` - Binary file containing document offsets
- `docnos.txt` - Text file containing document numbers
- `doc_lengths.txt` - Text file containing document lengths
- `doc_magnitudes.txt` - Text file containing document magnitudes (for cosine similarity)
- `lexicon.json` - JSON file containing the lexicon (vocabulary)
- `inverted_index.bin` - Binary file containing the inverted index
- `index_offsets.bin` - Binary file containing inverted index offsets

The stemmed index will tokenize and stem words using the Porter stemmer algorithm before indexing, which can improve recall by matching words with the same stem (e.g., "running", "runs", "ran" all stem to "run").

### Running Coogle Search Interface

Coogle is an interactive search interface that allows you to search the indexed documents using BM25 retrieval.

#### Command:

```bash
python SearchEngine/coogle.py <index_path>
```

#### Arguments:

- `index_path`: Path to the directory containing index files (output from IndexEngine)

#### Example with Index:

```bash
python SearchEngine/coogle.py index/
```

#### Using Coogle:

Once Coogle starts, you will see the colorful Coogle logo and can start searching:

1. **Enter a query**: Type any search query and press Enter
2. **View results**: The top 10 results will be displayed with rank, headline, date, snippet, and document number
3. **View full document**: 
   - Type a valid rank number (1-10) to view the complete document
   - Type `n` to enter a new query
   - Type `q` to quit the application

#### Example Session:

```
Enter a query: foreign policy
1. Germany's Foreign Policy Shift (Jan 15, 1989)
The German government announced... (LA011589-0075)

Type a valid rank to view the full document, type 'n' to continue searching, or type 'q' to quit.
Enter a rank: 1
[Full document content displayed]

Enter a rank: n

Enter a query: technology innovation
[New results displayed]
```

## Complete Workflow Example

Here's a complete example workflow from indexing to interactive search:

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Build index
python IndexEngine/IndexEngine.py data/latimes.gz index

# 4. Run Coogle interactive search
python SearchEngine/coogle.py index/

```
