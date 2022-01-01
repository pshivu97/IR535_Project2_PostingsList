import math


class Node:

    def __init__(self, value=None, next=None, doc_token_count=None):
        """ Class to define the structure of each node in a linked list (postings list).
            Value: document id, Next: Pointer to the next node
            Add more parameters if needed.
            Hint: You may want to define skip pointers & appropriate score calculation here"""
        self.value = value
        self.next = next
        self.skip = None
        self.frequency = 1
        self.tfidf = 0
        self.doc_token_count = doc_token_count

class LinkedList:
    """ Class to define a linked list (postings list). Each element in the linked list is of the type 'Node'
        Each term in the inverted index has an associated linked list object.
        Feel free to add additional functions to this class."""
    def __init__(self):
        self.start_node = None
        self.end_node = None
        self.length, self.n_skips, self.idf = 0, 0, 0.0
        self.skip_length = None

    def traverse_list(self):
        traversal = []
        if self.start_node is None:
            print("List has no element")
            return
        else:
            n = self.start_node
            # Start traversal from head, and go on till you reach None
            while n is not None:
                traversal.append(n)
                n = n.next
            return traversal

    def traverse_list_value(self):
        traversal = []
        if self.start_node is None:
            print("List has no element")
            return
        else:
            n = self.start_node
            # Start traversal from head, and go on till you reach None
            while n is not None:
                traversal.append(n.value)
                n = n.next
            return traversal

    def traverse_skips(self):
        traversal = []
        if self.start_node is None:
            return
        else:
            node = self.start_node
            traversal.append(node)
            while node is not None:
                if not node.skip is None:
                    node = node.skip
                    traversal.append(node)
                else:
                    node = node.next
        if len(traversal) is 1:
            return []
        return traversal

    def traverse_skips_value(self):
        traversal = []
        if self.start_node is None:
            return
        else:
            node = self.start_node
            traversal.append(node.value)
            while node is not None:
                if not node.skip is None:
                    node = node.skip
                    traversal.append(node.value)
                else:
                    node = node.next
        if len(traversal) is 1:
            return []
        return traversal

    def add_skip_connections(self):
        # n_skips = math.floor(math.sqrt(self.length))
        # if n_skips * n_skips == self.length:
        #     n_skips = n_skips - 1
        n_skips = math.floor(self.length / math.ceil(math.sqrt(self.length)))
        if n_skips * n_skips == self.length:
            n_skips = n_skips - 1

        """ Write logic to add skip pointers to the linked list. 
            This function does not return anything.
            To be implemented."""
        if n_skips < 1:
            return
        else:
            n_skips += 1
            index = 1
            crnt_node = self.start_node
            traverse_node = self.start_node.next
            while traverse_node is not None:
                if index % n_skips == 0:
                    crnt_node.skip = traverse_node
                    crnt_node = traverse_node
                traverse_node = traverse_node.next
                index += 1

    def get_node(self, value):
        if self.length == 0:
            return None
        else:
            node = self.start_node
            while node is not None:
                if node.value == value:
                    return node
                node = node.next
            return None

    def insert_at_end(self, value, doc_token_count):
        """ Write logic to add new elements to the linked list.
            Insert the element at an appropriate position, such that elements to the left are lower than the inserted
            element, and elements to the right are greater than the inserted element.
            To be implemented. """
        node_exist = self.get_node(value)
        if not node_exist == None:
            node_exist.frequency += 1
            return
        new_node = Node(value=value,doc_token_count=doc_token_count)
        n = self.start_node
        self.length += 1

        if self.start_node is None:
            self.start_node = new_node
            self.end_node = new_node
            return

        elif self.start_node.value >= value:
            self.start_node = new_node
            self.start_node.next = n
            return

        elif self.end_node.value <= value:
            self.end_node.next = new_node
            self.end_node = new_node
            return

        else:
            while n.value < value < self.end_node.value and n.next is not None:
                n = n.next

            m = self.start_node
            while m.next != n and m.next is not None:
                m = m.next
            m.next = new_node
            new_node.next = n
            return

    def calculate_idf(self, doc_count):
        self.idf = doc_count/self.length
        return self.idf

    def calculate_tfidf(self):
        if not self.length == 0:
            node = self.start_node
            while node is not  None:
                node.tfidf = (node.frequency/node.doc_token_count) * self.idf
                node = node.next