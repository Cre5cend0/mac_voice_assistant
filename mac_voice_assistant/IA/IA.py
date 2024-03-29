"""Intelligent Assistant"""
import random
import json
import pickle
import numpy as np
import os
import sys

# If you're using TensorFlow => 2.0, make sure to put these lines before importing tensorflow to be effective.
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Change 3 to values (0, 1, 2, 3) according to the messages you want avoid.

import nltk
from abc import ABCMeta, abstractmethod
from queue import Queue
from multiprocessing.pool import ThreadPool
from ..utils.logger import log
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.models import load_model

nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)


class IAssistant(metaclass=ABCMeta):

    @abstractmethod
    def train_model(self):
        """ Implemented in child class """

    @abstractmethod
    def request_tag(self, message):
        """ Implemented in child class """

    @abstractmethod
    def get_tag_by_id(self, id):
        """ Implemented in child class """

    @abstractmethod
    def request_method(self, message):
        """ Implemented in child class """

    @abstractmethod
    def request(self, message):
        """ Implemented in child class """


class GenericAssistant(IAssistant):

    def __init__(self, intents, intent_methods=None, model_name="assistant_model"):
        self.model_name = model_name
        self.log = log

        # Initialize queue instances
        self.tasks = Queue(maxsize=20)
        self.audio_queue = Queue(maxsize=20)
        self.commands = Queue(maxsize=20)
        self.responses = Queue(maxsize=20)

        # Initialize thread pool instance
        self.thread_pool = ThreadPool(processes=10)

        # Initialize intents files
        if intent_methods is None:
            intent_methods = {}
        self.intents = intents
        self.intent_methods = intent_methods
        self.default_intents_file_path = 'mac_voice_assistant/IA/default_intents.json'

        self.load_default_intents()
        self.load_custom_intents(intents)

        self.lemmatizer = WordNetLemmatizer()

    def get_default_intents_file_path(self):
        default_file_path = self.default_intents_file_path
        if os.path.exists(default_file_path):
            return default_file_path
        else:
            for path in sys.path:
                if 'site-packages' in path:
                    return path + '/mac_voice_assistant/IA/default_intents.json'

    def load_default_intents(self):
        path = self.get_default_intents_file_path()
        self.intents = json.loads(open(path).read())

    def load_custom_intents(self, intents):
        custom_intents = json.loads(open(intents).read())
        for intent in custom_intents['intents']:
            self.intents['intents'].append(intent)

    def train_model(self):

        self.words = []
        self.classes = []
        documents = []
        ignore_letters = ['!', '?', ',', '.']

        for intent in self.intents['intents']:
            for pattern in intent['patterns']:
                word = nltk.word_tokenize(pattern.lower())
                self.words.extend(word)
                documents.append((word, intent['tag']))
                if intent['tag'] not in self.classes:
                    self.classes.append(intent['tag'])

        self.words = [self.lemmatizer.lemmatize(w.lower()) for w in self.words if w not in ignore_letters]
        self.words = sorted(list(set(self.words)))

        self.classes = sorted(list(set(self.classes)))

        training = []
        output_empty = [0] * len(self.classes)

        for doc in documents:
            bag = []
            word_patterns = doc[0]
            word_patterns = [self.lemmatizer.lemmatize(word.lower()) for word in word_patterns]
            for word in self.words:
                bag.append(1) if word in word_patterns else bag.append(0)

            output_row = list(output_empty)
            output_row[self.classes.index(doc[1])] = 1
            training.append([bag, output_row])

        random.shuffle(training)
        training = np.array(training, dtype=object)

        train_x = list(training[:, 0])
        train_y = list(training[:, 1])

        self.model = Sequential()
        self.model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(len(train_y[0]), activation='softmax'))

        sgd = SGD(learning_rate=0.01, weight_decay=1e-6, momentum=0.9, nesterov=True)
        self.model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
        self.hist = self.model.fit(np.array(train_x), np.array(train_y), epochs=50, batch_size=5, verbose=0)

    def save_model(self, model_name=None):
        if model_name is None:
            self.model.save(f"{self.model_name}.keras", self.hist)
            pickle.dump(self.words, open(f'{self.model_name}_words.pkl', 'wb'))
            pickle.dump(self.classes, open(f'{self.model_name}_classes.pkl', 'wb'))
        else:
            self.model.save(f"{model_name}.keras", self.hist)
            pickle.dump(self.words, open(f'{model_name}_words.pkl', 'wb'))
            pickle.dump(self.classes, open(f'{model_name}_classes.pkl', 'wb'))

    def load_model(self, model_name=None):
        if model_name is None:
            self.words = pickle.load(open(f'{self.model_name}_words.pkl', 'rb'))
            self.classes = pickle.load(open(f'{self.model_name}_classes.pkl', 'rb'))
            self.model = load_model(f'{self.model_name}.keras')
        else:
            self.words = pickle.load(open(f'{model_name}_words.pkl', 'rb'))
            self.classes = pickle.load(open(f'{model_name}_classes.pkl', 'rb'))
            self.model = load_model(f'{model_name}.keras')

    def _clean_up_sentence(self, sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [self.lemmatizer.lemmatize(word.lower()) for word in sentence_words]
        return sentence_words

    def _bag_of_words(self, sentence, words):
        sentence_words = self._clean_up_sentence(sentence)
        bag = [0] * len(words)
        for s in sentence_words:
            for i, word in enumerate(words):
                if word == s:
                    bag[i] = 1
        return np.array(bag)

    def _predict_class(self, sentence):
        p = self._bag_of_words(sentence, self.words)
        res = self.model.predict(np.array([p]))[0]
        ERROR_THRESHOLD = 0.1
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append({'intent': self.classes[r[0]], 'probability': str(r[1])})
        return return_list

    def _get_response(self, ints, intents_json):
        result = None
        try:
            tag = ints[0]['intent']
            list_of_intents = intents_json['intents']
            for i in list_of_intents:
                if i['tag'] == tag:
                    result = random.choice(i['responses'])
                    break
        except IndexError:
            pass
        return result

    def request_tag(self, message):
        pass

    def get_tag_by_id(self, id):
        pass

    def request_method(self, intent):
        pass

    def request(self, message):
        ints = self._predict_class(message)
        intent = ints[0]['intent']
        if intent in self.intent_methods.keys():
            method = self.intent_methods[intent]
            return method, self._get_response(ints, self.intents)
        else:
            return False, self._get_response(ints, self.intents)
