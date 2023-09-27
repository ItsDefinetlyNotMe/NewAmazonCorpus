import os
import random
import sys
import spacy
import statistics
from tqdm import tqdm
from bs4 import BeautifulSoup
from itertools import islice
import pandas as pd
import csv
import json
from collections import defaultdict


def increment_value(dictionary, key):
    current_value = dictionary.get(key, 0)
    dictionary[key] = current_value + 1
    return dictionary


def analysis(lengths, authors,name):
    # Text length
    average_length = statistics.mean(lengths)
    longest_length = max(lengths)
    shortest_length = min(lengths)
    std_deviation = statistics.stdev(lengths)

    # analyse authors
    num_authors = len(authors.keys())
    texts_per_author = [count for count, _ in authors.values()]
    topic_per_author_list = []
    topics_per_author = [len(topics.keys()) for _, topics in authors.values()]

    avg_texts_per_author = statistics.mean(texts_per_author)
    std_dev_texts_per_author = statistics.stdev(texts_per_author)
    avg_topics_per_author = statistics.mean(topics_per_author)
    std_dev_topics_per_author = statistics.stdev(topics_per_author)

    print(f"Analyse:{name}")
    print(f"Average Review Length: {average_length}")
    print(f"Longest Review Length: {longest_length}")
    print(f"Shortest Review Length: {shortest_length}")
    print(f"Standard Deviation of Lengths: {std_deviation}")
    print(f"Number of Authors: {num_authors}")
    print(f"Average Texts per Author: {avg_texts_per_author}")
    print(f"Standard Deviation of Texts per Author: {std_dev_texts_per_author}")
    print(f"Average Topics per Author: {avg_topics_per_author}")
    print(f"Standard Deviation of Topics per Author: {std_dev_topics_per_author}")

def train(jsonl_file, min_token = 500, max_token = 1000):
    base = "data"
    nlp = spacy.load("en_core_web_lg")

    with open(jsonl_file, 'r') as file1:
        lengths = []
        authors = defaultdict(lambda: (0, {}))
        for line in file1:
            data_raw = json.loads(line)
            bool_same_topic = False
            bool_same_author = False

            tokenized_doc = nlp(data_raw['review'])

            token_count = len(tokenized_doc)

            author = data_raw['id']
            topic = data_raw['topic']

            data_to_append = {"topic": topic, "review": data_raw['review']}

            # make file with author id if necessary, else append a jsonl with the text.
            if token_count >= min_token:
                if token_count >= max_token:
                    token_counter = 0
                    final_text = ""
                    for token in tokenized_doc:
                        final_text += token.text_with_ws
                        token_counter += 1
                        if token_counter >= max_token:
                            break
                    data_to_append["review"] = final_text
                file_path = os.path.join(base, author)
                if os.path.exists(file_path):
                    with open(file_path, 'a') as file:
                        file.write(json.dumps(data_to_append) + '\n')
                else:
                    with open(file_path, 'w') as file:
                        file.write(json.dumps(data_to_append) + '\n')

            # count author texts and topics
            if token_count >= min_token:
                    authors[author] = (authors[author][0] + 1, increment_value(authors[author][1], topic))
                    lengths.append(token_count)
        # analyse data
        analysis(lengths, authors,"train")

        with open('results_dict_train', 'w') as file:
                file.write(json.dumps(authors))
        return authors, lengths

def test(jsonl_file, min_token = 500, max_token = 1000):
    base = "data"
    nlp = spacy.load("en_core_web_lg")

    with open(jsonl_file, 'r') as file1:
        lengths = []
        authors = defaultdict(lambda: (0, {}))
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
            if token_count_L >= min_token:
                if token_count_L >= max_token:
                    token_counter = 0
                    final_text = ""
                    for token in tokenized_doc_L:
                        final_text += token.text_with_ws
                        token_counter += 1
                        if token_counter>= max_token:
                            break
                    data_to_append["review"] = final_text
                file_path = os.path.join(base,author_L)
                if os.path.exists(file_path):
                    with open(file_path, 'a') as file:
                        file.write(json.dumps(data_to_append) + '\n')
                else:
                    with open(file_path, 'w') as file:
                        file.write(json.dumps(data_to_append) + '\n')

            data_to_append = {"topic": topic_R, "review":data_R['review'] }

            if token_count_R > min_token :
                if token_count_R >= max_token:
                    token_counter = 0
                    final_text = ""
                    for token in tokenized_doc_R:
                        final_text += token.text_with_ws
                        token_counter += 1
                        if token_counter >= max_token:
                            break
                    data_to_append["review"] = final_text
                file_path = os.path.join(base,author_R)
                if os.path.exists(file_path):
                    with open(file_path, 'a') as file:
                        file.write(json.dumps(data_to_append) + '\n')
                else:
                    with open(file_path, 'w') as file:
                        file.write(json.dumps(data_to_append) + '\n')


            #count author texts and topics
            if token_count_L > min_token:
                authors[author_L] = (authors[author_L][0] + 1,increment_value(authors[author_L][1],topic_L))
                lengths.append(token_count_L)

            if token_count_R > min_token:
                authors[author_R]  = (authors[author_R][0] + 1,increment_value(authors[author_R][1],topic_R))
                lengths.append(token_count_R)

        #analyse data
        analysis(lengths,authors,"test")

        with open('results_dict_test', 'w') as file:
            file.write(json.dumps(authors))

        return authors, lengths
def make_pairs(my_dict):
    my_array = my_dict.keys()

    #allow text to be x times in the set
    appearences = 2
    #how much % is test_set exclusive
    p_test = 0.2
    test_authors ={}
    training_authors = {}

    # Calculate the number of elements to select
    num_to_select = int(p_test * len(my_array))

    # seperate a test set with seperate authors
    selected_elements = random.sample(my_array, num_to_select)
    test_authors = dict.fromkeys(selected_elements)
    training_authors = dict.fromkeys([x for x in my_array if x not in selected_elements])


    test_set_number_texts = 0
    for author in test_authors.keys():
        text_numbers = my_dict[author][0]
        array = []
        for text_number in range(text_numbers):
            test_set_number_texts += text_number
            array.extend([text_number]*appearences)

        test_authors[author] = array

    training_set_number_texts = 0
    for author in training_authors.keys():
        text_numbers = my_dict[author][0]
        array = []
        for text_number in range(text_numbers):
            training_set_number_texts += text_number
            array.extend([text_number]*appearences)
        training_authors[author] = array

    #make pairs
    #50/50
    training_set_diff_number = int(training_set_number_texts * 0.5 * appearences)
    training_set_same_number = training_set_number_texts * appearences - training_set_diff_number
    training_set = []
    for _ in range(training_set_same_number):
        if any(len(set(authors_list)) > 2 for authors_list in training_authors.values()):
            while True:
                first_text = 0
                second_text = 0
                random_author = random.choice(list(training_authors.keys()))
                text_set = list(set(training_authors[random_author]))
                if len(text_set) > 1:
                    first_text = random.choice(text_set)
                    text_set.remove(first_text)
                    second_text = random.choice(text_set)
                    training_authors[random_author].remove(first_text)
                    training_authors[random_author].remove(second_text)
                    if len(training_authors[random_author]) < 1:
                        del training_authors[random_author]
                else:
                    continue
                training_set.append(((random_author,first_text),(random_author,second_text)))
                break
        else:
            print("Out of same author texts")
            break
    training_set_diff_number = len(training_set)
    for element in training_authors.values():
        if len(element) < 1:
            print(":C")
    for _ in range(training_set_diff_number):
        if len( training_authors.keys()) > 1:
            random_author_1 = random.choice(list(training_authors.keys()))

            authors = list(training_authors.keys())
            authors.remove(random_author_1)
            random_author_2 = random.choice(authors)

            text_1 = random.choice(list(set(training_authors[random_author_1])))

            text_2 = random.choice(list(set(training_authors[random_author_2])))
            training_authors[random_author_2].remove(text_2)
            if len(training_authors[random_author_2]) < 1:
                del training_authors[random_author_2]
            training_authors[random_author_1].remove(text_1)
            if len(training_authors[random_author_1]) < 1:
                del training_authors[random_author_1]
            training_set.append(((random_author_1, text_1),(random_author_2, text_2)))

    #get same number  

    # 90/10
    test_set_diff_number = int(test_set_number_texts * 0.9*appearences)
    test_set_same_number = test_set_number_texts  *appearences- test_set_diff_number
    test_set = []
    print("TEST:" + str(test_set_number_texts))

    for _ in range(test_set_same_number):
        if any(len(set(authors_list)) > 2 for authors_list in test_authors.values()):
            while True:
                first_text = 0
                second_text = 0
                random_author = random.choice(list(test_authors.keys()))
                text_set = list(set(test_authors[random_author]))
                if len(text_set) > 1:
                    first_text = random.choice(text_set)
                    text_set.remove(first_text)
                    second_text = random.choice(text_set)
                    test_authors[random_author].remove(second_text)
                    if len(test_authors[random_author]) < 1:
                        del test_authors[random_author]
                else:
                    continue
                test_set.append(((random_author, first_text), (random_author, second_text)))
                break
        else:
            print("Out of same author texts")
            break

    for _ in range(test_set_diff_number):
        if len(test_authors.keys()) > 1:
            random_author_1 = random.choice(list(test_authors.keys()))
            random_author_2 = random_author_1
            while random_author_2 == random_author_1:
                random_author_2 = random.choice(list(test_authors.keys()))
            text_1 = random.choice(list(set(test_authors[random_author_1])))

            text_2 = random.choice(list(set(test_authors[random_author_2])))
            test_authors[random_author_1].remove(text_1)
            if len(test_authors[random_author_1]) < 1:
                del test_authors[random_author_1]
            test_authors[random_author_2].remove(text_2)
            if len(test_authors[random_author_2]) < 1:
                del test_authors[random_author_2]
            test_set.append(((random_author_1, text_1), (random_author_2, text_2)))

    #shuffle sets
    random.shuffle(training_set)
    random.shuffle(test_set)
    print("finished sets")
    return training_set,test_set

def write_csv_from_sets(training_set,test_set):
    base = "data"
    field_names = ["id", "sentiment","topic" ,"review"]
    with open("training.csv",mode="w+", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        counter = 0
        for pair in tqdm(training_set, desc="Writing_Training_set"):
            author_1 =  pair[0][0]
            author_2 = pair[1][0]
            same_author = author_1 == author_2

            text_1 = ""
            with open(os.path.join(base,author_1), 'r') as file:
                json_1 = json.loads(next(islice(file, pair[0][1], pair[0][1] + 1), None))
                text_1 = json_1.get('review', '')
                topic_1 = json_1.get('topic', '')

            text_2 = ""
            with open(os.path.join(base,author_2), 'r') as file:
                json_2 = json.loads(next(islice(file, pair[1][1], pair[1][1] + 1), None))
                text_2 = json_2.get('review', '')
                topic_2 = json_2.get('topic', '')

            text = text_1 + "$$$" + text_2
            row = {'id':counter, 'sentiment':same_author,'topic':topic_1 == topic_2,'review':text}
            writer.writerow(row)

    with open("test.csv",mode="w+", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        counter = 0
        for pair in tqdm(test_set, desc="Writing_Test_set"):
            author_1 =  pair[0][0]
            author_2 = pair[1][0]
            same_author = author_1 == author_2

            text_1 = ""
            topic_1 = ""
            with open(os.path.join(base,author_1), 'r') as file:
                json_1 = json.loads(next(islice(file, pair[0][1], pair[0][1] + 1), None))
                text_1 = json_1.get('review', '')
                topic_1 = json_1.get('topic', '')

            text_2 = ""
            topic_2 = ""
            with open(os.path.join(base,author_2), 'r') as file:
                json_2 = json.loads(next(islice(file, pair[1][1], pair[1][1] + 1), None))
                text_2 = json_2.get('review', '')
                topic_2 = json_2.get('topic', '')

            text = text_1 + "$$$" + text_2
            row = {'id':counter, 'sentiment':same_author,'topic':topic_1 == topic_2, 'review':text}
            writer.writerow(row)


if __name__ == '__main__':
    args = sys.argv[1:]
    author_dict_test, length_test = test(args[0])
    author_dict_train, length_train = train(args[1])
    author_dict = {**author_dict_train, **author_dict_test}
    length_train.extend(length_test)
    analysis(length_train,author_dict,"combined")
    combined_dict = {**author_dict_train, **author_dict_test}
    training_set,test_set = make_pairs(combined_dict)
    write_csv_from_sets(training_set, test_set)