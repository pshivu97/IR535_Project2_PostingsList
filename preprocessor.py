import collections
from nltk.stem import PorterStemmer
import re
from nltk.corpus import stopwords
import nltk
from nltk.tokenize import WhitespaceTokenizer

nltk.download('stopwords')


class Preprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.ps = PorterStemmer()

    def get_doc_id(self, doc):
        """ Splits each line of the document, into doc_id & text.
            Already implemented"""
        arr = doc.split("\t")
        return int(arr[0]), arr[1]

    def tokenizer(self, text):
        """ Implement logic to pre-process & tokenize document text.
            Write the code in such a way that it can be re-used for processing the user's query.
            To be implemented."""
        # a.converting to lowercase
        text = text.lower()

        # text = text.replace("-", " ")
        # text = text.replace("–", " ")
        # text = text.replace("‐", " ")
        # text = text.replace("—", " ")
        # text = text.replace("/", " ")

        # b.Remove non alphanumeric except whitespace
        text = re.sub(r'[^A-Za-z0-9 ]+', ' ', text)

        # c.Remove excess whitespace
        text = ' '.join(text.split())

        # d.Tokenise using white space
        # tk = WhitespaceTokenizer()
        terms_with_stopwords = text.split()  # tk.tokenize(text)
        terms_without_stopwords = []

        # e.remove stopwords
        for words in terms_with_stopwords:
            if words not in self.stop_words:
                # f.perform porter stemming
                terms_without_stopwords.append(self.ps.stem(words))

        return terms_without_stopwords
from nltk.stem import PorterStemmer
import re
from nltk.corpus import stopwords
import nltk
from nltk.tokenize import WhitespaceTokenizer

nltk.download('stopwords')


class Preprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.ps = PorterStemmer()

    def get_doc_id(self, doc):
        """ Splits each line of the document, into doc_id & text.
            Already implemented"""
        arr = doc.split("\t")
        return int(arr[0]), arr[1]

    def tokenizer(self, text):
        """ Implement logic to pre-process & tokenize document text.
            Write the code in such a way that it can be re-used for processing the user's query.
            To be implemented."""
        # a.converting to lowercase
        text = text.lower()

        # text = text.replace("-", " ")
        # text = text.replace("–", " ")
        # text = text.replace("‐", " ")
        # text = text.replace("—", " ")
        # text = text.replace("/", " ")

        # b.Remove non alphanumeric except whitespace
        text = re.sub(r'[^A-Za-z0-9 ]+', ' ', text)

        # c.Remove excess whitespace
        text = ' '.join(text.split())

        # d.Tokenise using white space
        # tk = WhitespaceTokenizer()
        terms_with_stopwords = text.split()  # tk.tokenize(text)
        terms_without_stopwords = []

        # e.remove stopwords
        for words in terms_with_stopwords:
            if words not in self.stop_words:
                # f.perform porter stemming
                terms_without_stopwords.append(self.ps.stem(words))

        return terms_without_stopwords