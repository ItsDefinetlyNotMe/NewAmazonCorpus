import os
import sys
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
    print(f"There are {corpus.review.shape} pairs")
    for idx in tqdm(range(corpus.review.shape[0]), desc='Analysing Corpus'):

        temp = corpus.review[idx].split('$$$')
        doc_2 = BeautifulSoup(temp[0], 'html.parser').get_text().encode('utf-8').decode('utf-8')
        doc_1 = BeautifulSoup(temp[1], 'html.parser').get_text().encode('utf-8').decode('utf-8')
        total_texts.update([doc_1,doc_2])

        if corpus.sentiment[idx] == 1:
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
            not_same_author.append([doc_1,doc_2])

    count = 0
    total_texts_under_authors = 0
    texts_from_authors = set()
    for author in authors:
        texts_from_authors.union(author)
        total_texts_under_authors += len(author)
        if(len(texts_from_authors) != total_texts_under_authors):
            print('Wrong amaount of texts in: ' +str(count))
        count += 1

    print(f'There are {len(authors)} authors with an average of {total_texts_under_authors/len(authors)}({0})sd texts per author.')
    print(f'There are {total_texts_under_authors} texts from {len(total_texts)} total texts')
    print(f'Test: Length of all Text from the authors: {len(set().union(*authors))}')
if __name__ == '__main__':
    args = sys.argv[1:]
    analyse_and_seperate(args[0])