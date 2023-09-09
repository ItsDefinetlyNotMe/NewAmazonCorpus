import os
import sys
import spacy
import statistics
from tqdm import tqdm
from bs4 import BeautifulSoup
import pandas as pd
import json
from collections import defaultdict
def analyse(jsonl_file, min_token = 500, max_token = 1000):
    base = "data"
    nlp = spacy.load("en_core_web_lg")

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

            for key, value in data_raw.items():
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

            #create jsonl for new filesystem
            data_to_append = {"topic": topic_L, "review":data_L['review'] }

            #make file with author id if necessary, else append a jsonl with the text.
            if token_count_L >= 500 and token_count_L <= max_token:
                file_path = os.path.join(base,author_L)
                if os.path.exists(file_path):
                    with open(file_path, 'a') as file:
                        file.write(json.dumps(data_to_append) + '\n')
                else:
                    with open(file_path, 'w') as file:
                        file.write(json.dumps(data_to_append) + '\n')

            data_to_append = {"topic": topic_R, "review":data_R['review'] }

            if token_count_R > min_token and token_count_R <= max_token:
                file_path = os.path.join(base,author_R)
                if os.path.exists(file_path):
                    with open(file_path, 'a') as file:
                        file.write(json.dumps(data_to_append) + '\n')
                else:
                    with open(file_path, 'w') as file:
                        file.write(json.dumps(data_to_append) + '\n')


            def increment_value(dictionary, key):
                current_value = dictionary.get(key, 0)
                dictionary[key] = current_value + 1
                return dictionary

            #count author texts and topics
            if token_count_L > min_token and token_count_L <= max_token:
                authors[author_L] = (authors[author_L][0] + 1,increment_value(authors[author_L][1],topic_L))
                lengths.append(token_count_L)

            if token_count_R > min_token and token_count_R <= max_token:
                authors[author_R]  = (authors[author_R][0] + 1,increment_value(authors[author_R][1],topic_R))
                lengths.append(token_count_R)

        #analyse data
        #Text length
        average_length = statistics.mean(lengths)
        longest_length = max(lengths)
        shortest_length = min(lengths)
        std_deviation = statistics.stdev(lengths)

        #analyse authors
        num_authors = len(authors.keys())
        texts_per_author = [count for count, _ in authors.values()]
        topic_per_author_list    = []
        topics_per_author = [len(topics.keys()) for _,topics in authors.values()]

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

        with open('results_dict', 'w') as file:
            file.write(json.dumps(authors))

        return authors
def make_pairs():
    pass
    #remove text if to short,
    #seperate a test set with seperate authors
    #mix and match pairs
if __name__ == '__main__':
    args = sys.argv[1:]
    analyse(args[0])
