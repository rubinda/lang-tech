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
import math
from bs4 import BeautifulSoup
from collections import defaultdict
from string import punctuation
from kneser_ney import LanguageModel


def compare_words(file1, file2='actual.dat'):
    """ Compares the words in two files"""
    with open(file1) as test, open(file2) as actual:
        test_lines = test.readlines()
        actual_lines = actual.readlines()
    line_count = 0
    correct_count = 0
    for a, t in zip(actual_lines, test_lines):
        if a == t:
            correct_count += 1
        line_count += 1
    return correct_count, line_count


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
        self.kn = LanguageModel()
        self.kn.read_from_file('big_model.lm')
        #self.kn.train(folder='corpus/')
        #self.kn.save_to_file("big_model.lm")
        self.V_len = len(self.model.values())

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

        # If none of the generated words matched return the given word with probability 1
        candidates[word] = 1
        return candidates

    def check_sentence(self, sentence, mp=1):
        """ Returns the most probable sentence using Kneser-Ney """
        sentence = preprocess_string(sentence)
        evaluations = {}

        # Calculate the probability if only one word is fixed
        words = sentence.split()
        original_multiplier = mp
        for i in range(0, len(words)):
            prefix = ' '.join(words[:i]).lstrip()
            appendix = ' '.join(words[i+1:]).rstrip()
            candidates = self.generate_candidates(words[i])

            for word in candidates.keys():
                candidate_sent = ' '.join([prefix, word.strip(), appendix]).strip()
                evaluations[candidate_sent] = (self.kn.kn_evaluate_sentence(candidate_sent))

        evaluations[sentence] = original_multiplier * self.kn.kn_evaluate_sentence(sentence)
        return max(evaluations, key=evaluations.get)

    def get_best_candidate(self, word):
        """ Vrne najboljso kandidatko za podano nepravilno besedo """
        candidates = self.generate_candidates(word)
        return max(candidates, key=candidates.get)

    def evaluate_get_actual(self, test_set='holbrook-tagged.dat'):
        """ Izparsa ven dejanske povedi """
        errors_present = 0
        actual_sentence = []
        actual_word = []
        with open(test_set) as test_set:
            lines = test_set.readlines()
            # Parse each line and create a valid sentence dict and sentence dict with mistakes
            for line in lines:
                # Build the sentences with mistakes
                if errors_present > 100:
                    break;
                soup = BeautifulSoup(line, 'html.parser')
                mistakes = soup.select('ERR')
                # Take only sentences with at least one mistake
                if len(mistakes) < 1 or len(mistakes) > 1:
                    continue
                errors_present += 1
                soup = BeautifulSoup(line, 'html.parser')
                mistakes = soup.select('ERR')
                for mistake in mistakes:
                    mistake.string = mistake['targ'].strip()
                    actual_word.append(preprocess_string(mistake['targ'].strip()))
                    mistake.unwrap()
                # After removing the ERR badges we get the sentence with typos
                actual_sentence.append(preprocess_string(soup.text))
        with open('actual.dat', 'w') as a:
            a.write('\n'.join(actual_word) + '\n')

    def evaluate_model(self, test_set='holbrook-tagged.dat'):
        """ Evaluates the model (how many errors it successfully corrected """
        errors_present = 0
        corrections = []
        with open(test_set) as test_set:
            lines = test_set.readlines()
            # Parse each line and create a valid sentence dict and sentence dict with mistakes

            for line in lines:
                # Build the sentences with mistakes
                if errors_present > 100:
                    break;
                soup = BeautifulSoup(line, 'html.parser')
                mistakes = soup.select('ERR')
                # Take only sentences with at least one mistake
                if len(mistakes) < 1 or len(mistakes) > 1:
                    continue

                typo_sentence = []
                typo_probs = []
                fix_words = []
                errors_present += 1
                for mistake in mistakes:
                    # Split the sentence with the bad word, generate candidates for
                    # the bad word and append sentences with the candidates
                    bad_word = preprocess_string(mistake.text.strip())
                    mistake.unwrap()
                    splits = preprocess_string(soup.text).split(bad_word)
                    prefix = splits[0].strip()
                    appendix = splits[1].rstrip()

                    # Should be only 1
                    candidates = self.generate_candidates(bad_word)
                    typo_sentence.append('{} {}{}'.format(prefix, bad_word, appendix))
                    typo_probs.append(1/self.V_len)
                    fix_words.append(bad_word)
                    for c, p in candidates.items():
                        typo_probs.append(p)
                        typo_sentence.append('{} {}{}'.format(prefix, c, appendix))
                        fix_words.append(c)

                # Find the most probable sentence using Kneser-Ney
                best_i = 0
                max_prob = 0
                for i in range(len(typo_probs)):
                    # Evaluate the current sentence
                    prob = typo_probs[i] * self.kn.kn_evaluate_sentence(typo_sentence[i])
                    if prob > max_prob:
                        best_i = i
                        max_prob = prob
                corrections.append(fix_words[best_i])

        with open('corrected.dat', 'w') as cor:
            cor.write('\n'.join(corrections) + '\n')

    def evaluate_best_candidate(self, test_set='holbrook-tagged.dat'):
        """ Poskusa popraviti besedo samo z uporabo najbolsega kandidata """
        errors_present = 0
        candidate_sentences = []
        corrections = []
        with open(test_set) as test_set:
            lines = test_set.readlines()
            # Parse each line and create a valid sentence dict and sentence dict with mistakes

            for line in lines:
                # Build the sentences with mistakes
                if errors_present > 100:
                    break;
                soup = BeautifulSoup(line, 'html.parser')
                mistakes = soup.select('ERR')
                # Take only sentences with at least one mistake
                if len(mistakes) != 1:
                    continue

                errors_present += 1
                for mistake in mistakes:
                    current_word = mistake.contents[0].strip()
                    try_fix = self.get_best_candidate(current_word)
                    corrections.append(try_fix)
                    mistake.contents = try_fix
                    mistake.unwrap()
                candidate_sentences.append(preprocess_string(soup.text))
        with open('candid_only.dat', 'w') as cdid:
            cdid.write('\n'.join(corrections) + '\n')


# Example usage:
# p = SpellCheck()
# print(p.check_sentence("siter"))
#sp.evaluate_model()
# sp.evaluate_get_actual()
# sp.evaluate_best_candidate()
# p, l = compare_words('corrected.dat')
# print(p, l, p/l)