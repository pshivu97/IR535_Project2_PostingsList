from tqdm import tqdm
from preprocessor import Preprocessor
from indexer import Indexer
from collections import OrderedDict
from linkedlist import LinkedList
import inspect as inspector
import sys
import argparse
import json
import time
import random
import flask
from flask import Flask
from flask import request
import hashlib

app = Flask(__name__)


class ProjectRunner:
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.indexer = Indexer()

    def _merge(self, list1, list2, with_skip):
        """ Implement the merge algorithm to merge 2 postings list at a time.
            Use appropriate parameters & return types.
            While merging 2 postings list, preserve the maximum tf-idf value of a document.
            To be implemented."""
        results = []
        comparisons = 0
        if with_skip:
            while (list1 is not None) and (list2 is not None):
                if list1.value == list2.value:
                    if list1.tfidf > list2.tfidf:
                        results.append(list1)
                    else:
                        results.append(list2)
                    list1 = list1.next
                    list2 = list2.next
                elif list1.value < list2.value:
                    if (not list1.skip is None) and (list1.skip.value <= list2.value):
                        while list1.skip.value <= list2.value:
                            list1 = list1.skip
                            if not list1.value == list2.value:
                                comparisons += 1
                            if list1.skip is None:
                                break
                        if not list1.value == list2.value:
                            comparisons -= 1
                    else:
                        list1 = list1.next
                else:
                    if (not list2.skip is None) and (list2.skip.value <= list1.value):
                        while list2.skip.value <= list1.value:
                            list2 = list2.skip
                            if not list1.value == list2.value:
                                comparisons += 1
                            if list2.skip is None:
                                break
                        if not list1.value == list2.value:
                            comparisons -= 1
                    else:
                        list2 = list2.next
                comparisons += 1

        else:
            while (list1 is not None) and (list2 is not None):
                if list1.value == list2.value:
                    if list1.tfidf > list2.tfidf:
                        results.append(list1)
                    else:
                        results.append(list2)
                    list1 = list1.next
                    list2 = list2.next
                elif list1.value < list2.value:
                    list1 = list1.next
                else:
                    list2 = list2.next

                comparisons += 1
        return results, comparisons

    def _daat_and(self, input_term_arr, postings_list, with_skip, sort_by_tfidf):
        """ Implement the DAAT AND algorithm, which merges the postings list of N query terms.
            Use appropriate parameters & return types.
            To be implemented."""
        sorted_input_term_arr = self.get_sorted_terms_list(input_term_arr, postings_list)
        merge_list = postings_list[sorted_input_term_arr[0]]
        comparison = 0
        for term in sorted_input_term_arr[1:]:
            merge_list, crnt_comparison = self._merge(merge_list[0], postings_list[term][0], with_skip)
            comparison = comparison + crnt_comparison

        merge_list_arr = []

        if sort_by_tfidf:
            merge_list = self.sort_by_tfidf(merge_list)

        for node in merge_list:
            merge_list_arr.append(node.value)

        return merge_list_arr, comparison

    def sort_by_tfidf(self, merge_list):
        for i in range(0, len(merge_list)):
            max_id = i
            for j in range(i+1, len(merge_list)):
                if merge_list[max_id].tfidf == merge_list[j].tfidf:
                    if merge_list[max_id].value > merge_list[j].value:
                        max_id = j
                if merge_list[max_id].tfidf < merge_list[j].tfidf:
                    max_id = j
            merge_list[i], merge_list[max_id] =  merge_list[max_id], merge_list[i]
        return  merge_list

    def get_sorted_terms_list(self, input_term_arr, postings_list):
        sorted_input_term_arr = []
        input_term_arr_weights = []
        for term in input_term_arr:
            input_term_arr_weights.append(len(postings_list[term]))

        def find_smallest(arr):
            smallest_index = 0,
            smallest = sys.maxsize
            for i, weight in enumerate(input_term_arr_weights):
                if weight < smallest:
                    smallest_index = i
                    smallest = weight
            return smallest_index

        for i, weight in enumerate(input_term_arr_weights):
            smallest_index = find_smallest(input_term_arr_weights)
            input_term_arr_weights[smallest_index] = sys.maxsize
            sorted_input_term_arr.append(input_term_arr[smallest_index])

        return sorted_input_term_arr

    def _get_postings(self, term):
        """ Function to get the postings list of a term from the index.
            Use appropriate parameters & return types.
            To be implemented."""
        return self.indexer.inverted_index[term].traverse_list(), self.indexer.inverted_index[term].traverse_skips()

    def _output_formatter(self, op):
        """ This formats the result in the required format.
            Do NOT change."""
        if op is None or len(op) == 0:
            return [], 0
        op_no_score = [int(i) for i in op]
        results_cnt = len(op_no_score)
        return op_no_score, results_cnt

    def run_indexer(self, corpus):
        """ This function reads & indexes the corpus. After creating the inverted index,
            it sorts the index by the terms, add skip pointers, and calculates the tf-idf scores.
            Already implemented, but you can modify the orchestration, as you seem fit."""
        doc_count = 0
        with open(corpus, 'r') as fp:
            for line in tqdm(fp.readlines()):
                doc_id, document = self.preprocessor.get_doc_id(line)
                tokenized_document = self.preprocessor.tokenizer(document)
                self.indexer.generate_inverted_index(doc_id, tokenized_document)
                doc_count += 1
        self.indexer.sort_terms()
        self.indexer.add_skip_connections()
        self.indexer.calculate_tf_idf(doc_count)
        a = 0

    def sanity_checker(self, command):
        """ DO NOT MODIFY THIS. THIS IS USED BY THE GRADER. """

        index = self.indexer.get_index()
        kw = random.choice(list(index.keys()))
        return {"index_type": str(type(index)),
                "indexer_type": str(type(self.indexer)),
                "post_mem": str(index[kw]),
                "post_type": str(type(index[kw])),
                "node_mem": str(index[kw].start_node),
                "node_type": str(type(index[kw].start_node)),
                "node_value": str(index[kw].start_node.value),
                "command_result": eval(command) if "." in command else ""}

    def run_queries(self, query_list, random_command):
        """ DO NOT CHANGE THE output_dict definition"""
        output_dict = {'postingsList': {},
                       'postingsListSkip': {},
                       'daatAnd': {},
                       'daatAndSkip': {},
                       'daatAndTfIdf': {},
                       'daatAndSkipTfIdf': {},
                       'sanity': self.sanity_checker(random_command)}

        for query in tqdm(query_list):
            """ Run each query against the index. You should do the following for each query:
                1. Pre-process & tokenize the query.
                2. For each query token, get the postings list & postings list with skip pointers.
                3. Get the DAAT AND query results & number of comparisons with & without skip pointers.
                4. Get the DAAT AND query results & number of comparisons with & without skip pointers, 
                    along with sorting by tf-idf scores."""

            input_term_arr = self.preprocessor.tokenizer(query)  # Tokenized query. To be implemented.

            for term in input_term_arr:
                postings_node, skip_postings_node = self._get_postings(term)


                """ Implement logic to populate initialize the above variables.
                    The below code formats your result to the required format.
                    To be implemented."""

                output_dict['postingsList'][term] = postings_node
                output_dict['postingsListSkip'][term] = skip_postings_node

            and_op_no_skip, and_comparisons_no_skip = self._daat_and(input_term_arr, output_dict['postingsList'], False, False)
            and_op_skip, and_comparisons_skip = self._daat_and(input_term_arr, output_dict['postingsList'], True, False)
            and_op_no_skip_sorted, and_comparisons_no_skip_sorted = self._daat_and(input_term_arr, output_dict['postingsList'], False, True)
            and_op_skip_sorted, and_comparisons_skip_sorted = self._daat_and(input_term_arr, output_dict['postingsList'], True, True)
            # and_op_no_skip, and_op_skip, and_op_no_skip_sorted, and_op_skip_sorted = None, None, None, None
            # and_comparisons_no_skip, and_comparisons_skip, \
            #     and_comparisons_no_skip_sorted, and_comparisons_skip_sorted = None, None, None, None
            """ Implement logic to populate initialize the above variables.
                The below code formats your result to the required format.
                To be implemented."""
            and_op_no_score_no_skip, and_results_cnt_no_skip = self._output_formatter(and_op_no_skip)
            and_op_no_score_skip, and_results_cnt_skip = self._output_formatter(and_op_skip)
            and_op_no_score_no_skip_sorted, and_results_cnt_no_skip_sorted = self._output_formatter(and_op_no_skip_sorted)
            and_op_no_score_skip_sorted, and_results_cnt_skip_sorted = self._output_formatter(and_op_skip_sorted)

            output_dict['daatAnd'][query.strip()] = {}
            output_dict['daatAnd'][query.strip()]['results'] = and_op_no_score_no_skip
            output_dict['daatAnd'][query.strip()]['num_docs'] = and_results_cnt_no_skip
            output_dict['daatAnd'][query.strip()]['num_comparisons'] = and_comparisons_no_skip

            output_dict['daatAndSkip'][query.strip()] = {}
            output_dict['daatAndSkip'][query.strip()]['results'] = and_op_no_score_skip
            output_dict['daatAndSkip'][query.strip()]['num_docs'] = and_results_cnt_skip
            output_dict['daatAndSkip'][query.strip()]['num_comparisons'] = and_comparisons_skip

            output_dict['daatAndTfIdf'][query.strip()] = {}
            output_dict['daatAndTfIdf'][query.strip()]['results'] = and_op_no_score_no_skip_sorted
            output_dict['daatAndTfIdf'][query.strip()]['num_docs'] = and_results_cnt_no_skip_sorted
            output_dict['daatAndTfIdf'][query.strip()]['num_comparisons'] = and_comparisons_no_skip_sorted

            output_dict['daatAndSkipTfIdf'][query.strip()] = {}
            output_dict['daatAndSkipTfIdf'][query.strip()]['results'] = and_op_no_score_skip_sorted
            output_dict['daatAndSkipTfIdf'][query.strip()]['num_docs'] = and_results_cnt_skip_sorted
            output_dict['daatAndSkipTfIdf'][query.strip()]['num_comparisons'] = and_comparisons_skip_sorted


            for term in output_dict['postingsList'].keys():
                # postings = []
                # for node in output_dict['postingsList'][term]:
                #     if node is not None and node.value is not None:
                #         postings.append(node.value)
                output_dict['postingsList'][term] = self.indexer.inverted_index[term].traverse_list_value()

            for term in output_dict['postingsListSkip'].keys():
                # postings_skip= []
                # for node in output_dict['postingsListSkip'][term]:
                #     if node is not None and node.value is not None:
                #         postings_skip.append(node.value)
                output_dict['postingsListSkip'][term] = self.indexer.inverted_index[term].traverse_skips_value()

        return output_dict


@app.route("/execute_query", methods=['POST'])
def execute_query():
    """ This function handles the POST request to your endpoint.
        Do NOT change it."""
    start_time = time.time()

    queries = request.json["queries"]
    random_command = request.json["random_command"]

    """ Running the queries against the pre-loaded index. """
    output_dict = runner.run_queries(queries, random_command)

    """ Dumping the results to a JSON file. """
    with open(output_location, 'w') as fp:
        print(output_dict)
        print(output_dict)
        json.dump(output_dict, fp)

    response = {
        "Response": output_dict,
        "time_taken": str(time.time() - start_time),
        "username_hash": username_hash
    }
    return flask.jsonify(response)


if __name__ == "__main__":
    """ Driver code for the project, which defines the global variables.
        Do NOT change it."""

    output_location = "project2_output.json"
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--corpus", type=str, help="Corpus File name, with path.")
    parser.add_argument("--output_location", type=str, help="Output file name.", default=output_location)
    parser.add_argument("--username", type=str,
                        help="Your UB username. It's the part of your UB email id before the @buffalo.edu. "
                             "DO NOT pass incorrect value here")

    argv = parser.parse_args()

    corpus = argv.corpus
    output_location = argv.output_location
    username_hash = hashlib.md5(argv.username.encode()).hexdigest()

    """ Initialize the project runner"""
    runner = ProjectRunner()

    """ Index the documents from beforehand. When the API endpoint is hit, queries are run against 
        this pre-loaded in memory index. """
    runner.run_indexer(corpus)

    #runner.run_queries([" xyz district  "], 0)
    #runner.run_queries([" the novel coronavirus  "], 0)
    #runner.run_queries([" from an epidemic to a pandemic  "], 0)
    #runner.run_queries([" is hydroxychloroquine effective?  "], 0)

    app.run(host="0.0.0.0", port=9999)