#!/usr/bin/env python3
#
# Python skripta, ki implementira N-Grame z glajenjem Kneser-Ney.
# Zgradi jezikovni model in ga shrani v datoteko. Z modelom lahko napovemo verjetnost povedi
#
# @author David Rubin
# @license MIT (check repository)
# FERI, Language technoligies, 2019


class LanguageModel:

    def __init__(self, n):
        # Velikost n-gramov
        self.n_size = n;

    def train(self, corpus_folder):
        """ Prebere vse tekstovne datoteke znotraj corpus_folder in zgradi model """
        # TODO implement train
        pass

    def save_to_file(self, filename):
        """ Shrani model v datoteko """
        # TODO implement save_to_file
        pass

    def read_from_file(self, filename):
        """ Prebere model, ki ga je shranil, iz datoteke """
        # TODO implement read_from_file
        pass

    def evaluate_sentence(self, sentence):
        """ Izracuna perpleksnost za podano poved. """
        # TODO implement evaluate sentence
        pass
