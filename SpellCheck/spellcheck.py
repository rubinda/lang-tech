#!/usr/bin/env python3
#
# Skripta, ki preveri slovnicno pravilnost povedi.
# V kolikor meni, da je katerakoli beseda napacna poskusa predlagati popravek.
# Iz ucnega korpusa 'big.txt' izdelamo model in racunamo verjetnosti povedi.
#
#   Example usage:
# sp = SpellCheck
# probable_sent = sp.check_sentence(<my sentence>)
#
#   Requires kneser_ney.py (see ../KneserNey) to function
#
# @author David Rubin
# @license MIT
import re
from collections import defaultdict
from string import punctuation
from kneser_ney import LanguageModel


def preprocess_file(filename):
    """ Preprocesses the file contents """
    with open(filename) as f:
        data = ''.join(f.readlines())
        return preprocess_string(data)


def preprocess_string(some_string):
    """ Remove punctuation/numbers, to lower case """
    return some_string.lower().replace("\n", " ").replace("\r", "").translate(str.maketrans('', '', punctuation))


def words_at_distance1(word):
    """ Return all words that are at (levenshtein) distance 1"""
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletions = [L + R[1:] for L, R in splits if R]
    transpositions = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    insertions = [L + c + R for L, R in splits for c in letters]
    return set(deletions + transpositions + replaces + insertions)


def words_at_distance2(word):
    """
    Returns all words at edit distance 2
    (calculate distance 1 on all words that are 1 away from 'word')
    """
    return set(words2 for words1 in words_at_distance1(word) for words2 in words_at_distance1(words1))


class SpellCheck:
    def __init__(self, learn_corpus='corpus/big.txt'):
        self.model = defaultdict(int)  # The dictionary with word frequencies
        self.learn_file = learn_corpus  # The file with the learning set
        self.regex = re.compile(r'[0-9%s^(\s)]' % re.escape(punctuation))

        self.build_model()

    def build_model(self):
        """ Counts the frequencies of the word in the given corpus"""
        corpus = preprocess_file(self.learn_file)
        for word in corpus.split():
            # Go through every word in the corpus and increase its frequency
            self.model[word] += 1

    def valid_words(self, words):
        """ Returns the words from the set if they are in the dictionary (model) """
        return set(word for word in words if word in self.model)

    def generate_candidates(self, word):
        """ Generates all candidates for the given word with probabilities """
        candidates = {}

        # If the given word is in the dict it is the only option with probability 1.0
        if word in self.model:
            candidates[word] = 1
            return candidates

        # If the given word is not in the dict, calculate the probabilities for words
        # at distance 1. Normalize the frequencies with the sum of given words
        w1 = self.valid_words(words_at_distance1(word))
        if len(w1) > 0:
            freq_sum = 0
            for w in w1:
                candidates[w] = self.model[w]
                freq_sum += self.model[w]
            for k, v in candidates.items():
                candidates[k] = v / freq_sum
            return candidates

        # If none of the edit distance 1 are in the dictionary, generate distance 2 words
        w2 = self.valid_words(words_at_distance2(word))
        if len(w2) > 0:
            freq_sum = 0
            for w in w2:
                candidates[w] = self.model[w]
                freq_sum += self.model[w]

            for k, v in candidates.items():
                candidates[k] = v / freq_sum
            return candidates

        # If none of the generated words matched return the given word with probability one
        candidates[word] = 1
        return candidates

    def check_sentence(self, sentence):
        """ Returns the most probable sentence using Kneser-Ney """
        kn = LanguageModel()
        sentence = preprocess_string(sentence)
        # kn.train(folder='corpus/')
        # kn.save_to_file("big_model.lm")
        kn.read_from_file("big_model.lm")
        evaluations = {sentence: kn.kn_evaluate_sentence(sentence)}
        words = sentence.split()
        for i in range(0, len(words)):
            prefix = ' '.join(words[:i]).lstrip()
            appendix = ' '.join(words[i+1:]).rstrip()
            for word in self.generate_candidates(words[i]):
                candidate_sent = ' '.join([prefix, word.strip(), appendix]).strip()
                evaluations[candidate_sent] = kn.kn_evaluate_sentence(candidate_sent)
        return max(evaluations, key=evaluations.get)

