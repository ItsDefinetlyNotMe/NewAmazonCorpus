import os
from tqdm import tqdm
from bs4 import BeautifulSoup
import pandas as pd

def analyse_and_seperate():
    corpus = pd.read_csv('amazon.csv', sep='\t')
    #each author is represented as the sum of their texts
    authors = []
    not_same_author = []
    total_texts = set()
    #is the sum of their text all text ?
    # what if texts are only used as not same author
    #only possible if we compare n^2 pairs
    # first compare all to get the complete picture of authors -> look wether all authors are complete. de
    for idx in tqdm(range(corpus.review.shape[0]), desc='extracting docs '):

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
        else:#help
            #doc_1_index,doc_2_index = -1,-1
            #count = 0
            #for author in authors:
            #    for text in author:
            #        if doc_1 == text:
            #            doc_1_index = count
            #        if doc_2 == text:
            #            doc_2_index = count
            #    count += 1
            #    if doc_1 != -1:
            #        authors[doc_1_index].add(doc_1)
            #    if doc_2 != -1:
            #        authors[doc_2_index].add(doc_2)
            not_same_author.append([doc_1,doc_2])

    total_texts_under_authors = 0
    for author in authors:
         total_texts_under_authors += len(author)

    print(f'There are {len(authors)} authors with an average of {total_texts_under_authors/len(authors)}({0})sd texts per author.')
    print(f'There are {total_texts_under_authors} texts from {len(total_texts)} total texts')