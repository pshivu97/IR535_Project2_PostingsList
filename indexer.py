
from linkedlist import LinkedList
from collections import OrderedDict


class Indexer:
    def __init__(self):
        """ Add more attributes if needed"""
        self.inverted_index = OrderedDict({})


    def get_index(self):
        """ Function to get the index.
            Already implemented."""
        return self.inverted_index

    def generate_inverted_index(self, doc_id, tokenized_document):
        """ This function adds each tokenized document to the index. This in turn uses the function add_to_index
            Already implemented."""
        for t in tokenized_document:
            self.add_to_index(t, doc_id, len(tokenized_document))

    def add_to_index(self, term_, doc_id_, doc_token_count):
        """ This function adds each term & document id to the index.
            If a term is not present in the index, then add the term to the index & initialize a new postings list (linked list).
            If a term is present, then add the document to the appropriate position in the posstings list of the term.
            To be implemented."""
        if not term_ in self.inverted_index:
            self.inverted_index[term_] = LinkedList()
        self.inverted_index[term_].insert_at_end(doc_id_, doc_token_count)

    def sort_terms(self):
        """ Sorting the index by terms.
            Already implemented."""
        sorted_index = OrderedDict({})
        for k in sorted(self.inverted_index.keys()):
            sorted_index[k] = self.inverted_index[k]
        self.inverted_index = sorted_index

    def add_skip_connections(self):
        """ For each postings list in the index, add skip pointers.
            To be implemented."""
        for term in self.inverted_index:
            self.inverted_index[term].add_skip_connections()

    def calculate_tf_idf(self, doc_count):
        """ Calculate tf-idf score for each document in the postings lists of the index.
            To be implemented."""
        for term in self.inverted_index:
            self.inverted_index[term].calculate_idf(doc_count)
            self.inverted_index[term].calculate_tfidf()