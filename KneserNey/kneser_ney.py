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
import nltk
import math
import numpy
from collections import defaultdict
from timeit import default_timer as timer


class LanguageModel:
    table = str.maketrans('', '')

    def __init__(self, n=3):
        # Velikost n-gramov
        self.n_size = n
        self.n_grams = [defaultdict(int) for _ in range(n)]   # 0 - unigrams, 1 - bigrams, 2 - trigrams .. n-1 - n-grams

    def make_ngrams(self, sentence, n):
        """ Ustvari ngrame in jih vrne kot seznam stringov"""
        ngrams = []
        words = ('<s> ' + sentence.rstrip() + ' </s>').split()
        for i in range(len(words) - n + 1):
            ngrams.append(tuple(words[i:i + n]))
        return ngrams

    def count_ngrams(self, sentence, n, counter_dict):
        """ Ustvari ngrame besed iz podanega niza in jih doda sestevkam """
        # Dodaj se tokene <s>, </s> za zacetek in konec povedi
        words = ('<s> ' + sentence.rstrip() + ' </s>').split()
        for i in range(len(words) - n + 1):
            counter_dict[tuple((words[i:i+n]))] += 1

    def get_sentences(self, file):
        """ Vrne vse povedi v datoteki (pricakuje se slovensko besedilo """
        slovene_tokenizer = nltk.data.load('tokenizers/punkt/slovene.pickle')
        remove_punc = str.maketrans("", "", string.punctuation + '»«−…•')
        sentences = slovene_tokenizer.tokenize(''.join(file.readlines()))
        return [s.translate(remove_punc) for s in sentences]

    def train(self, folder='korpus/'):
        """ Prebere vse tekstovne datoteke znotraj corpus_folder in zgradi model """
        print('Learning from .txt files ...', end='')
        start = timer()
        txt_files = glob.glob(folder + '*.txt')
        for filename in txt_files:
            with open(filename) as f:
                sentences = self.get_sentences(f)
                for sentence in sentences:
                    # Zgradi besedne unigram, bigram ... n-gram
                    for k in range(self.n_size):
                        # Izgradi k-gram (1..n) in ga dodaj v ustrezno mesto
                        # K+1, ker stejemo od 0
                        self.count_ngrams(sentence, k+1, self.n_grams[k])
        # Ngrame, ki se pojavijo 2 ali manjkrat odstrani in nadomesti z UNK (na vsakem nivoju)
        for kgram_count in self.n_grams:
            ngrams_to_cut = []
            for kgram, occurrence in kgram_count.items():
                if occurrence <= 2:
                    ngrams_to_cut.append(kgram)
            # Pobrisi ven kljuce, ki se pojavijo <= 2
            for k in ngrams_to_cut:
                kgram_count.pop(k)
            # Dodaj nazaj UNK, ki ima stevilo pojavitev 2 (mejo)
            kgram_count['UNK'] = 2

        print(' %.2fs' % (timer() - start))

    def save_to_file(self, filename):
        """ Shrani model v datoteke """
        print('Dumping model into files ...', end='')
        start = timer()
        model_out = {'n': self.n_size, 'n_grams': [{' '.join(k): v for k, v in x.items()} for x in self.n_grams]}
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
            self.n_grams = [defaultdict(int, {tuple(k.split()): v for k, v in x.items()}) for x in model['n_grams']]
        print(' %.2fs' % (timer() - start))

    def kneser_ney_prob(self, d, k, k_gram):
        """
        Izracunaj Kneser-Ney glajenje

        :param d discount (float)
        :param k stopnja n-grama (k-gram)
        :returns logaritem zglajene verjetnosti
        """
        if k == 1:
            # Prestej kolikokrat se pojavi beseda
            # lambda(epsilon) = d, P(epsilon) - 1 / len(unigrams)
            # P_kn(unigram) = max(count(unigram) - d, 0) / count(len(unigrams) + lambda(epsilon) * P(epsilon)
            all_bigrams = len(self.n_grams[k])
            all_unigrams = len(self.n_grams[k-1])
            continuation_count = sum([1 for x in self.n_grams[k] if k_gram[:-1] == x[:-1]])
            return max(continuation_count - d, 0) / all_bigrams + d / all_unigrams
        else:
            # Zazeni rekurzijo

            # Kolikokrat se pojavi w_i-1
            count_w_less_1 = self.n_grams[k-2][k_gram[:-1]]
            if count_w_less_1 == 0:
                count_w_less_1 = 2

            # Koliko unique nadaljevanj imamo za w_i-1
            unique_completions = len([1 for x in self.n_grams[k-1].keys() if k_gram[:-1] == x[:-1]])
            if unique_completions == 0:
                unique_completions = 2
            lambda_weight = (d / count_w_less_1) * unique_completions

            # lambda(w_i-n+1) * P_kn(w_i | w_i-n+2)
            p_kn = lambda_weight * self.kneser_ney_prob(d, k-1, k_gram[1:])
            return max(self.n_grams[k-1][k_gram] - d, 0) / count_w_less_1 + lambda_weight * p_kn

    def calculate_probability(self, ngram):
        """ Izracuna pogojno verjenost n-grama P(n|n-1,n-2...)"""
        # Zgornji del (kolikokrat se pojavi celoten n-gram)
        upper = self.n_grams[self.n_size-1][ngram]
        lower = self.n_grams[self.n_size-2][ngram[:-1]]
        return math.log(upper/lower)

    def evaluate_sentence(self, sentence):
        """ Izracuna perpleksnost za podano poved. """
        ngrams = self.make_ngrams(sentence, self.n_size)
        log_probs = [self.calculate_probability(ngram) for ngram in ngrams]
        return math.exp(sum(log_probs))

    def kn_evaluate_sentence(self, sentence):
        """ Oceni verjetnost povedi s pomocjo Kneser-Ney"""
        ngrams = self.make_ngrams(sentence, n=self.n_size)
        probs = []
        for ngram in ngrams:
            probs.append(self.kneser_ney_prob(d=0.75, k=self.n_size, k_gram=ngram))
        return numpy.prod(probs)

    def sentence_perplexity(self, sentence):
        """ Izracuna perpleksnost ene povedi """
        words = len(sentence.split(' '))
        kn_score = self.kn_evaluate_sentence(sentence)
        return kn_score ** (-1.0 / words)

    def file_perplexity(self, filename):
        """  Izracuna povprecno perpleksnost povedi v datoteki """
        perplexes = []
        print('Calculating file perplexity ...', end=' ')
        start = timer()
        file_len = 0;
        with open(filename) as file:
            for sentence in self.get_sentences(file):
                if len(sentence.split(' ')) < 1:
                    continue
                file_len += 1
                perplexes.append(math.log(self.kn_evaluate_sentence(sentence)))
        print(' %.2fs' % (timer() - start))
        return math.pow(10, (sum(perplexes) * -1.0 / file_len))
