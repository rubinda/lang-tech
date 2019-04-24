#!/usr/bin/env python3
#
# Python skripta, ki implementira N-Grame z glajenjem Kneser-Ney.
# Zgradi jezikovni model in ga shrani v datoteko. Z modelom lahko napovemo verjetnost povedi
#
# @author David Rubin
# @license MIT (check repository)
# FERI, Language technoligies, 2019
import json
import glob
import string
import nltk.data
import math
from collections import defaultdict
from timeit import default_timer as timer


class LanguageModel:
    table = str.maketrans('', '')

    def __init__(self, n=3):
        # Velikost n-gramov
        self.n_size = n
        self.n_grams = defaultdict(int)
        self.n_less_one_grams = defaultdict(int)

    def make_ngrams(self, sentence, n):
        """ Ustvari ngrame in jih vrne kot seznam stringov"""
        ngrams = []
        words = ('<s> ' + sentence.rstrip() + ' </s>').split()
        for i in range(len(words) - n + 1):
            ngrams.append(' '.join(words[i:i + n]))
        return ngrams

    def count_ngrams(self, sentence, n, counter_dict):
        """ Ustvari ngrame besed iz podanega niza in jih doda sestevkam """
        # Dodaj se tokene <s>, </s> za zacetek in konec povedi
        words = ('<s> ' + sentence.rstrip() + ' </s>').split()
        for i in range(len(words) - n + 1):
            counter_dict[' '.join(words[i:i+n])] += 1

    def train(self, folder='korpus/'):
        """ Prebere vse tekstovne datoteke znotraj corpus_folder in zgradi model """
        print('Learning from .txt files ...', end='')
        start = timer()
        slovene_tokenizer = nltk.data.load('tokenizers/punkt/slovene.pickle')
        remove_punc = str.maketrans("", "", string.punctuation + '»«−…')
        txt_files = glob.glob(folder + '*.txt')
        for filename in txt_files:
            with open(filename) as f:
                sentences = slovene_tokenizer.tokenize(''.join(f.readlines()))
                for sentence in sentences:
                    sentence = sentence.translate(remove_punc)
                    # Zgradi besedne n grame in n-1 grame:
                    self.count_ngrams(sentence, self.n_size, self.n_grams)
                    self.count_ngrams(sentence, self.n_size-1, self.n_less_one_grams)
        print(' %.2fs' % (timer() - start))

    def save_to_file(self, filename):
        """ Shrani model v datoteke """
        print('Dumping model into files ...', end='')
        start = timer()
        model_out = {'n': self.n_size, 'n_grams': self.n_grams, 'n_less_one_grams': self.n_less_one_grams}
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(model_out, f, ensure_ascii=False)
        print(' %.2fs' % (timer() - start))

    def read_from_file(self, filename):
        """ Prebere model, ki ga je shranil, iz datoteke """
        print("Loading model from file ...", end='')
        start = timer()
        with open(filename, encoding='utf-8') as f:
            model = json.load(f)
            self.n_size = model['n']
            self.n_grams = model['n_grams']
            self.n_less_one_grams = model['n_less_one_grams']
        print(' %.2fs' % (timer() - start))

    def calculate_probability(self, ngram):
        """ Izracuna pogojno verjenost n-grama P(n|n-1,n-2...)"""
        # Zgornji del (kolikokrat se pojavi celoten n-gram)
        upper = self.n_grams[ngram]
        lower = self.n_less_one_grams[" ".join(ngram.split(" ")[:-1])]
        return math.log(upper/lower)

    def evaluate_sentence(self, sentence):
        """ Izracuna perpleksnost za podano poved. """
        ngrams = self.make_ngrams(sentence, self.n_size)
        log_probs = [self.calculate_probability(ngram) for ngram in ngrams]
        return math.exp(sum(log_probs))
