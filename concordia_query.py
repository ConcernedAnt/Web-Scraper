from pathlib import Path
import json
import re
from nltk.corpus import stopwords
from operator import itemgetter
import math
from nltk.stem import PorterStemmer
import linecache

ps = PorterStemmer()
disk_path = Path("DISK")
inverted_index = []
count = 0
stop_words = list(stopwords.words('english'))
stopw_150 = stop_words[0:150]
total_length = 0

# Vars for BM25
avg_length = 0
num_docs = 0
k1 = 1.8
b = 0.5

# Read the document lengths from the file
document_lengths = []
length_file = open("document_lengths.txt", "r")
lines = length_file.readlines()

for line in lines:
    document_lengths.append(int(line.rstrip("\n")))

# Compute avg doc length and number of documents
for doc_length in document_lengths:
    total_length += doc_length
    num_docs += 1

avg_length = total_length/num_docs

for file in disk_path.glob("merged_block*.json"):
    opened_file = file.open()
    file_contents = opened_file.read()
    opened_file.close()

    inverted_index.insert(count, json.loads(file_contents))
    count += 1


def get_from_index(inv_index, term):
    for index in inv_index:
        if term in index:
            return index.get(term)
    return None


def compress(word):
    pattern = re.compile('[\W_]+')
    word = pattern.sub('', word)
    word = re.sub('[0-9]', '', word)
    word = word.lower()
    word = ps.stem(word)
    return word


# Basic AND intersection algo from textbook
def and_intersect(p1, p2):
    answer = []
    i = 0
    j = 0
    while i < len(p1) and j < len(p2):
        if p1[i] == p2[j]:
            answer.append(p1[i])
            i += 1
            j += 1
        elif p1[i] < p2[j]:
            i += 1
        else:
            j += 1
    return answer


def or_intersect(p1, p2):
    return list(set(p1 + p2))


# Calculate the BM25 for the query
def compute_bm25(result, n, postings_lists, query_terms, doc_frequencies, query_string):
    rsv = []
    tf_list = []

    # Loop through all of the documents that satisfy the query and calculate their BM25 weight
    for doc in result:
        rsv_comp = 0
        tf = 0
        tf_idf_comp = 0

        for i in range(0, n):
            postings = postings_lists[i]
            list_with_freq = get_from_index(inverted_index, query_terms[i])

            if postings is None or postings == []:
                term_frequency = 0
            else:
                if doc not in postings:
                    continue
                term_index = postings.index(doc)
                term_frequency = list_with_freq[term_index][1]

            # BM25 Calculations
            numerator = math.log10(num_docs / (1 + doc_frequencies[i])) * ((k1 + 1) * term_frequency)
            denom = k1 * ((1 - b) + b * (document_lengths[doc - 1] / avg_length)) + term_frequency
            rsv_comp += (numerator / denom)
            tf += term_frequency

            # TF-IDF Calculations
            log_tf = math.log10(1 + term_frequency)
            idf = math.log10(num_docs / (1 + doc_frequencies[i]))
            tf_idf_comp += log_tf * idf;

        rsv.append([doc, rsv_comp, document_lengths[doc - 1], tf])
        tf_list.append([doc, tf_idf_comp])

    # Ranks the documents based on the BM25 weight and displays the documents without the rank
    ranked_results = sorted(rsv, key=itemgetter(1), reverse=True)
    display_ranked = []
    for item in ranked_results:
        display_ranked.append(item[0])

    # Ranks the documents based on the TF-IDF weight and displays the documents without the rank
    ranked_results_2 = sorted(tf_list, key=itemgetter(1), reverse=True)
    display_ranked_2 = []
    for item in ranked_results_2:
        display_ranked_2.append(item[0])

    return display_ranked[0:100], display_ranked_2[0:100]


def option_2():
    query_terms = []
    postings_lists = []
    display_terms = []
    doc_frequencies = []

    user_query = input(f"Enter the query: ")
    user_input = user_query.split()
    n = len(user_input)

    for i in range(0, n):
        term = user_input[i].strip()
        display_terms.append(term)
        term = compress(term)
        postings = get_from_index(inverted_index, term)

        query_terms.insert(i, term)
        if term in stopw_150 or term == "and" or term == "or":
            postings_lists.insert(i, None)
            doc_frequencies.insert(i, 0)
        else:
            if postings is None:
                postings_lists.insert(i, [])
                doc_frequencies.insert(i, 0)
            else:
                p_list = []
                for item in postings:
                    p_list.append(item[0])
                postings_lists.insert(i, p_list)
                doc_frequencies.insert(i, len(postings))
        print(f"Term {term} returned {postings_lists[i]}")
    res = postings_lists[0]

    for i in range(1, n):
        postings_list = postings_lists[i]
        if res is None:
            res = postings_list
        else:
            if postings_list is not None:
                res = and_intersect(res, postings_list)

    query_string = display_terms[0]
    for i in range(1, n):
        query_string += " AND " + display_terms[i]

    return compute_bm25(res, n, postings_lists, query_terms, doc_frequencies, query_string)


def option_3():
    query_terms = []
    display_terms = []
    postings_lists = []
    doc_frequencies = []
    rsv = []

    index = 0
    # Read the user input

    user_query = input(f"Enter the query: ")
    user_input = user_query.split()
    n = len(user_input)

    for i in range(0, n):
        term = user_input[i].strip()
        display_terms.append(term)
        term = compress(term)
        postings = get_from_index(inverted_index, term)

        if term in stopw_150 or term == "and" or term == "or":
            postings_lists.insert(i, None)
            doc_frequencies.insert(i, 0)
            query_terms.insert(index, term)
            index += 1
        else:
            if postings is None:  # If the term has no postings do nothing
                print(f"\n{term} isn't in the index.")
                doc_frequencies.insert(i, 0)
                continue

            p_list = []
            for item in postings:
                p_list.append(item[0])

            query_terms.insert(index, term)
            postings_lists.insert(index, p_list)
            doc_frequencies.insert(i, len(postings))
            print(f"Term {term} returned {p_list}")
            index += 1

    if len(query_terms) != 0:
        # Perform or intersection
        res = None
        for post in postings_lists:
            if not res:
                res = post
            else:
                if post is not None:
                    res = or_intersect(res, post)

        query_string = display_terms[0]
        for i in range(1, len(display_terms)):
            query_string += " OR " + display_terms[i]

        return compute_bm25(res, n, postings_lists, query_terms, doc_frequencies, query_string)
    else:
        print("None of the terms you looked for are in the index.")


def get_url(doc_id):
    doc_line = linecache.getline("doc_id_pairs.txt", doc_id)
    split = doc_line.split(':')
    url = split[1]
    url = 'https://www.concordia.ca/' + url
    url = url.replace('_', '/')
    url = url.replace('DotHtml', '.html')
    url = url.replace('$', '?')
    url = url.replace('.txt', '')

    return url


def query_index():
    choice = None
    bm25_results = []
    tf_idf_results = []
    rank = 1
    while choice != 4:
        print("\n\n=====================QUERY MENU========================")
        print("What type of query do you want to do?")
        print("1. Single term query")
        print("2. Multi-term AND query")
        print("3. Multi-term query with at least 1 OR")
        print("4. Exit the program")
        choice = int(input("Enter the number associated with your choice: "))

        if choice == 1:
            print("\n\n=====================SINGLE TERM QUERY========================")
            display_term = input("Enter the term you want to look for: ")
            query_term = compress(display_term)
            result = get_from_index(inverted_index, query_term)

            # calculates BM25 weight for a single term.
            if result is not None:
                doc_frequency = len(result)

                postings = []
                for item in result:
                    postings.append(item[0])

                rsv = []
                for doc in postings:
                    rsv_comp = 0

                    if postings is None or postings == []:
                        term_frequency = 0
                    else:
                        term_index = postings.index(doc)
                        term_frequency = result[term_index][1]

                    numerator = math.log10(num_docs / (1 + doc_frequency)) * ((k1 + 1) * term_frequency)
                    denom = k1 * ((1 - b) + b * (document_lengths[doc - 1] / avg_length)) + term_frequency
                    rsv_comp += (numerator / denom)

                    rsv.append([doc, rsv_comp])

                ranked_results = sorted(rsv, key=itemgetter(1), reverse=True)
                display_ranked = []
                for item in ranked_results:
                    display_ranked.append(item[0])

                print(f"\nQuery term {display_term} returned the following result {display_ranked}")
            else:
                print(f"\nQuery term {display_term} was not in the index")
        elif choice == 2:
            print("\n\n=====================MULTI-TERM AND QUERY========================")
            [bm25_results, tf_idf_results] = option_2()

        elif choice == 3:
            print("\n\n=====================MULTI-TERM OR QUERY========================")
            [bm25_results, tf_idf_results] = option_3()

        if choice != 1:
            print("===================================================================================================")
            print("Ranking Using BM25")
            rank = 1
            for result in bm25_results:
                url = get_url(result)
                print(f"{rank} {result} - {url}")
                rank += 1
            rank = 1

            print("===================================================================================================")
            print("Ranking Using TF-IDF")
            for result in tf_idf_results:
                url = get_url(result)
                print(f"{rank} {result} - {url}")
                rank += 1


# Uncomment to test
query_index()
