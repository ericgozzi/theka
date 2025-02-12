import re

import json
import os

from collections import Counter

import networkx as nx

# NATURAL LANGUAGE TOOLKIT
# pip install nltk
import nltk

# Download WordNet data needed for Lemmatization
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
nltk.download('omw-1.4')

#Download stopwords
from nltk.corpus import stopwords
nltk.download('stopwords')



class AddBook(object):

    def __init__(self, author, title, book):

        author = author.upper()
        author = author.replace(" ", "-")
        self.author = author

        title = title.lower()
        title = title.replace(" ", "-")
        self.title = title

        self.path = author + "_" + title

        self.create_metadata()

        self.book = book
        self.text = self.curate_book()

        self.sentences_list()
        self.words_list()

        self.word_connections()

        self.create_graph()

        self.word_count()

        #self.add_to_theka()

        
    def create_metadata(self):

        data = {
                "author" : self.author, 
                "title" : self.title
            }
        os.makedirs("./theka/" + self.path, exist_ok=True)
        file_path = "./theka/" + self.path + "/data.json"
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)



    def add_metadata(self, key, value):
        
        file_path = "./theka/" + self.path + "/data.json"
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        data[key] = value

        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def read_metadata(self, key):

        file_path = "./theka/" + self.path + "/data.json"
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        value = data[key]
        return value
    
    """
    def add_to_theka(self):
        file_path = "./theka/data.json"
        with open(file_path, "r") as file:
            data = json.load(file)
        data["books"].append(self.path)
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
    """



    def curate_book(self):
        text = self.book
        text = text.replace("}", " ")
        text = text.replace("{", " ")
        text = text.replace("-", " ")
        text = text.replace("\n", " ") 
        text = text.replace(" .", ".")
        text = text.replace(" ,", ",")
        text = text.replace("\r", " ")
        text = re.sub(r'\s+', ' ', text)
        return text
    

    def sentences_list(self):

        all_sentences = self.text.split(". ")

        sentences = []
        for sentence in all_sentences:
            if len(sentence) > 3:
                sentence = sentence + "."
                sentences.append(sentence)
                
        self.add_metadata("sentences", sentences)


    def get_sentences(self):
        sentences = self.read_metadata("sentences")
        return sentences



    def words_list(self):

        lemmatizer = WordNetLemmatizer()

        all_words = re.findall(r'\b\w+\b', self.text.lower())

        words = []
        stop_words = set(stopwords.words("english"))
        for word in all_words:

            base_form = lemmatizer.lemmatize(word)

            if base_form not in stop_words and len(base_form)>2:
                words.append(base_form)

        self.add_metadata("words", words)


    def get_words(self):
        words = self.read_metadata("words")
        return words



    def word_connections(self):
        word_connections = []
        words = self.get_words()

        for i in range(len(words) - 1):
            word_connections.append((words[i], words[i+1]))
        self.word_connections = word_connections
        self.add_metadata("word_connections", word_connections)


    def word_count(self):
        words = self.get_words()
        words_count = Counter(words)
        self.add_metadata("words_count", words_count)

    def get_words_count(self):
        words_count = self.read_metadata("words_count")
        return words_count
    
    
    def create_graph(self):
        graph = nx.Graph()
        for word1, word2 in self.word_connections:
            graph.add_edge(word1, word2)
        self.eigenvector_centrality = nx.eigenvector_centrality(graph)
        self.add_metadata("eigenvector", self.eigenvector_centrality)

    def get_eigen_vector(self):
        eigen_vector = self.read_metadata("eigenvector")
        return eigen_vector
    

    def get_eigen_vector_of(self, word):
        vectors = self.get_eigen_vector()
        try:
            word_vector = vectors[word]
        except:
            word_vector = 0
        return word_vector
    



class Book(object):

    def __init__(self, id_string):
        self.id = id_string

    def __str__(self):
        return f"({self.get_author()}, {self.get_title()})"
    
    def _read_metadata(self, key):
        file_path = "./theka/" + self.id + "/data.json"
        with open(file_path, 'r') as file:
            data = json.load(file)    
        value = data[key]
        return value
    
    def get_sentences(self):
        sentences = self._read_metadata("sentences")
        return sentences
    
    def get_words(self):
        words = self._read_metadata("words")
        return words
    
    def get_word_eigen_vector(self, word):
        vectors = self.get_eigen_vector_list()
        try:
            word_vector = vectors[word]
        except:
            word_vector = 0
        return word_vector
        
    def get_eigen_vector_list(self):
        eigen_vector = self._read_metadata("eigenvector")
        return eigen_vector
    
    def get_author(self):
        author = self._read_metadata("author")
        author = author.replace('-', ' ')
        return author
    
    def get_title(self):
        title = self._read_metadata("title")
        title = title.replace('-', ' ')
        return title



def get_books():
    directory = "./theka"
    folders = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
    books = []
    for f in folders:
        book = Book(f)
        books.append(book)
    return books



def sort_books_by_eigen_vector(books, topic):
    sorted_books = {}
    for book in books:
        vector = book.get_word_eigen_vector(topic)
        sorted_books[book] = vector

    sorted_books = dict(sorted(sorted_books.items(), key=lambda item: item[1], reverse=True))

    return sorted_books





def get_answers_to_question(books, question):

    answer = []

    for i, book in enumerate(books.keys()):
        sentences_list = book.get_sentences()

        results = []
        for sentence in sentences_list:
            if all(word in sentence.split() for word in question):
                results.append(sentence)
        
        if len(results) != 0:
            answer.append(f"**{book.get_author()}, _{book.get_title()}_**")
            for j, result in enumerate(results):
                answer.append(f"- {result}")
            answer.append("---")
    
    return answer



def ask_theka(topic, question):
    books = get_books()
    books = sort_books_by_eigen_vector(books, topic)
    answers = get_answers_to_question(books, question)
    return answers


answers = ask_theka("planet", ["architecture"])
