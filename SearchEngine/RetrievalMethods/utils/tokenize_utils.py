def convert_tokens_to_ids(text: list[str], lexicon: dict[str, int], word_counts: dict[int, int]) -> None:
    """
    Converts a list of tokens to their corresponding ids and adds them to the lexicon if necessary.
    Also adds to the word counts.
    """
    token_ids = []

    # Convert tokens to ids and add to lexicon if necessary
    for token in text:
        if token in lexicon:
            token_ids.append(lexicon[token])
        else:
            token_ids.append(len(lexicon))
            lexicon[token] = len(lexicon)

    # Add to word counts
    for token_id in token_ids:
        if token_id in word_counts:
            word_counts[token_id] += 1
        else:
            word_counts[token_id] = 1

def add_to_postings(word_counts: dict[int, int], doc_id: int, inverted_index: list[list[int]]) -> None:
    """
    Adds the word counts and doc id to the inverted index.
    """
    for token_id in word_counts:
        count = word_counts[token_id]

        # if tokend_id in inverted_index
        if token_id < len(inverted_index):
            inverted_index[token_id].append(doc_id)
            inverted_index[token_id].append(count)
        else:
            inverted_index.append([doc_id, count])

def tokenize(text: str, tokens: list[str]) -> None:
    text = text.lower() 

    start = 0 
    i = 0

    for currChar in text:
        if not currChar.isdigit() and not currChar.isalpha() :
            if start != i :
                token = text[start:i]
                tokens.append( token )
                
            start = i + 1
        i += 1
    if start != i :
        tokens.append(text[start:i])