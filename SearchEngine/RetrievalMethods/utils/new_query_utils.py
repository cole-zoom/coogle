import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from RetrievalMethods.utils.tokenize_utils import tokenize

def get_scentence_score(tokenized_sentence: list[str], tokens: list[str]) -> float:
    """
    Gets a score for a sentence based on the number of tokens in the sentence that are in the query.
    """
    c = 0
    k = 0
    d = 0
    distinct = []
    continuous_run = 0

    # Get score for sentence
    for token in tokenized_sentence:
        if token in tokens:
            if token not in distinct:
                distinct.append(token)
                d += 1
            c += 1
            continuous_run += 1
        else:
            if continuous_run > k:
                k = continuous_run
            continuous_run = 0
    return 5*k + 4*d + c
    
        
def get_query_biased_summary(tokens: list[str], doc_content: str):
    """
    Gets a query biased summary from the given query and document content.
    """
    is_tag = False
    is_start = False
    is_headline = False
    is_caption = False
    scentences = {}
    scentence = []
    tokenized_sentence = []
    l = 0
    word = ""
    i = 0

    # Create and score sentences
    for char in doc_content:

        if char == ">":
            is_tag = False

        elif is_tag:
            tag_name += char
            if tag_name.lower() == "title":
                is_headline = True
            elif tag_name.lower() == "content":
                l = 2
                is_start = True
            elif tag_name.lower() == "item key=\"og_image:alt\"":
                is_caption = True
            
            # If we are at the end of the headline, make it a scentence
            elif tag_name.lower() == "/title":
                is_headline = False
                i += 1
                if word:
                    scentence.append(word)
                    tokenize(word, tokenized_sentence)
                score = get_scentence_score(tokenized_sentence, tokens)
                score += l + 1/i 
                word = ""
                if score in scentences:
                    while score in scentences:
                        score -= 0.1
                    scentences[score] = scentence
                else:
                    scentences[score] = scentence

                scentence = []
                tokenized_sentence = []
                l = 0

            # If we are at the end of the text, make it a scentence
            elif tag_name.lower() == "/content":
                i += 1
                if word:
                    scentence.append(word)
                    tokenize(word, tokenized_sentence)

                score = get_scentence_score(tokenized_sentence, tokens)
                score += l + 1/i
                    
                word = ""
                if score in scentences:
                    while score in scentences:
                        score -= 0.1
                    scentences[score] = scentence
                else:
                    scentences[score] = scentence

                scentence = []
                tokenized_sentence = []
                l = 0
                break
            
            # If we are at the end of the caption, make it a scentence
            elif tag_name.lower() == "/item":
                is_caption = False
                i += 1
                if word:
                    scentence.append(word)
                    tokenize(word, tokenized_sentence)
                score = get_scentence_score(tokenized_sentence, tokens)
                score += l + 1/i
                word = ""
                if score in scentences:
                    while score in scentences:
                        score -= 0.1
                    scentences[score] = scentence
                else:
                    scentences[score] = scentence
                scentence = []
                tokenized_sentence = []
                l = 0

        elif char == "<":
            is_tag = True
            tag_name = ""

        elif not is_start and not is_headline and not is_caption:
            continue

        elif char == " ":
            scentence.append(word)
            tokenize(word, tokenized_sentence)
            word = ""

        # end of scentence so add it to the scentences dictionary
        elif char == "." or char == "?" or char == "!":
            word += char
            scentence.append(word)
            tokenize(word, tokenized_sentence)
            i += 1
            score = get_scentence_score(tokenized_sentence, tokens) 
            score += l + 1/i
                
            word = ""
            
            # ensures no duplicate scores
            if score in scentences:
                while score in scentences:
                    score -= 0.1
                scentences[score] = scentence
            else:
                scentences[score] = scentence

            scentence = []
            tokenized_sentence = []
            l = 0
        else:
            word += char

    sorted_scentences = sorted(scentences.items(), key=lambda x: x[0], reverse=True)

    biased_query = ""
    j = 0
    for score, scentence in sorted_scentences:
        add_dot_dot_dot = False
        if len(scentence) > 50:
            scentence = scentence[:50]
            add_dot_dot_dot = True
        if j == 2:
            break
        j += 1
        biased_query += " ".join(scentence).strip().replace("\n", "") + " "
        if add_dot_dot_dot:
            biased_query =  biased_query.strip() + "..."

    return biased_query
