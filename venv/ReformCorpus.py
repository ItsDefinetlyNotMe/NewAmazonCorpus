import os
import sys
import spacy
import statistics
from tqdm import tqdm
from bs4 import BeautifulSoup
import pandas as pd

def analyse_and_seperate(path):
    corpus = pd.read_csv(path, sep='\t')
    #each author is represented as the sum of their texts
    authors = []
    not_same_author = []
    total_texts = set()
    #is the sum of their text all text ?
    # what if texts are only used as not same author
    #only possible if we compare n^2 pairs
    # first compare all to get the complete picture of authors -> look wether all authors are complete. de
    same_author_pairs  = 0
    different_author_pairs = 0
    print(f"There are {corpus.review.shape} pairs")
    for idx in tqdm(range(corpus.review.shape[0]), desc='Analysing Corpus'):

        temp = corpus.review[idx].split('$$$')
        doc_2 = BeautifulSoup(temp[0], 'html.parser').get_text().encode('utf-8').decode('utf-8')
        doc_1 = BeautifulSoup(temp[1], 'html.parser').get_text().encode('utf-8').decode('utf-8')
        total_texts.update([doc_1,doc_2])

        if corpus.sentiment[idx] == 1:
            same_author_pairs += 1
            # if either text is already in corpus match them
            found = False
            for author in authors:
                for text in author:
                    if doc_1 == text or doc_2 == text:
                        found = True
                        author.update([doc_1,doc_2])
                        break
            if not found:
                authors.append({doc_1,doc_2})
        else:
            different_author_pairs += 1
            not_same_author.append([doc_1,doc_2])

    count = 0
    total_texts_under_authors = 0
    texts_from_authors = set()
    for author in authors:
        texts_from_authors = texts_from_authors.union(author)
        total_texts_under_authors += len(author)
        if(len(texts_from_authors) != total_texts_under_authors):
            print(f'Wrong amount of texts in: {str(count)}. There are {len(texts_from_authors)} text in the set, but we count {total_texts_under_authors}.')
        count += 1

    print(f'There are {len(authors)} authors with an average of {round(total_texts_under_authors/len(authors),3)} texts per author.')
    print(f'There are {total_texts_under_authors} texts from {len(total_texts)} total texts')
    print(f'There are {same_author_pairs} Same author Pairs and {different_author_pairs} different Author pairs.')
    print(f'Test: Length of all Text from the authors: {len(set().union(*authors))}')
def analyse(jsonl_file):
    nlp = spacy.load("en_core_web_sm")

    with open(jsonl_file, 'r') as file1:
        lengths = []
        authors = defaultdict(lambda: (0, {}))
        all_data = []
        for line in file1:
            data_raw = json.loads(line)
            data_L = {}
            data_R = {}
            bool_same_topic = False
            bool_same_author = False

            for key, value in data.items():
                pass
            if key.endswith("_L"):
                data_L[ key[:-2] ] = value
            elif key.endswith("_R"):
                data_R[ key[:-2] ] = value
            elif key == 'label_c':
                bool_same_topic = True if value == 1 else False
            elif key == 'label_a':
                bool_same_author = True if value == 1 else False

            #todo check for length in tokens ? exclude long and short ones
            tokenized_doc_L = nlp(data_L['review'])
            tokenized_doc_R = nlp(data_R['review'])

            # Count the tokens
            token_count_L = len(tokenized_doc_L)
            token_count_R = len(tokenized_doc_R)

            #count authors / texts per author / topics / topic per author => author as {'id':(number texts,{topic1, topic2, ...})}
            #as a dict with value: tuple of number and a dict of topics
            author_L, author_R = data_L['id'], data_R['id']
            topic_L, topic_R = data_L['topic'], data_R['topic']

            #count author texts and topics
            authors[author_L] = (authors[author_L][0] + 1,authors[author_L][1].get(topic_L,0) +1)
            authors[author_R]  = (authors[author_L][0] + 1,authors[author_L][1].get(topic_R,0) +1)

            lengths.append(token_count_L)
            lengths.append(token_count_R)

        #analyse data
        #Text length
        average_length = statistics.mean(lengths)
        longest_length = max(lengths)
        shortest_length = min(lengths)
        std_deviation = statistics.stdev(lengths)

        #analyse authors
        num_authors = len(authors)
        texts_per_author = [count for count, _ in authors.values()]
        topics_per_author = [len(topics) for topics in topics_per_author]

        avg_texts_per_author = statistics.mean(texts_per_author)
        std_dev_texts_per_author = statistics.stdev(texts_per_author)
        avg_topics_per_author = statistics.mean(topics_per_author)
        std_dev_topics_per_author = statistics.stdev(topics_per_author)

        print(f"Average Review Length: {average_length}")
        print(f"Longest Review Length: {longest_length}")
        print(f"Shortest Review Length: {shortest_length}")
        print(f"Standard Deviation of Lengths: {std_deviation}")
        print(f"Number of Authors: {num_authors}")
        print(f"Average Texts per Author: {avg_texts_per_author}")
        print(f"Standard Deviation of Texts per Author: {std_dev_texts_per_author}")
        print(f"Average Topics per Author: {avg_topics_per_author}")
        print(f"Standard Deviation of Topics per Author: {std_dev_topics_per_author}")
if __name__ == '__main__':
    args = sys.argv[1:]
    analyse(args[0])
