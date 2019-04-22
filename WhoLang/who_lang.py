#!/usr/bin/env python3
#
# Program za detekcijo jezika s pomocjo metode N-terk.
# based on N-Gram-Based Text Categorization, Cavnar et al. 1994
#
# Datoteke znotraj zahtevanega direktorija 'train/dohr' so prevodi
# Deklaracije o clovekovih pravicah pridobljene s strani
# https://www.ohchr.org/EN/UDHR/Pages/Introduction.aspx
#
# TODO: read xml files by paragraphs and guess the language for each
#
# @author David Rubin
# @license MIT
# FERI, Language Technologies, 2019
import json
import sys
from collections import defaultdict, Counter, OrderedDict
from math import sqrt
from pathlib import Path
from re import escape, compile
from string import punctuation


def cos_linkage(n_grams1, n_grams2):
    """ Vrne kosinusno razdaljo med dvema besediloma (oziroma med njunimi n-terkami). """
    common_grams = set(n_grams1.keys()).intersection(n_grams2.keys())
    dot_product = sum(n_grams1[key] * n_grams2[key] for key in common_grams)
    grams1_length = sqrt(sum(x ** 2 for x in n_grams1.values()))
    grams2_length = sqrt(sum(x ** 2 for x in n_grams2.values()))
    return 1 - dot_product / (grams1_length * grams2_length)


def out_of_place_linkage(cat_profile, doc_profile, max_oop=301):
    """
    Poracuna out of place razdaljo med dvema seznamoma n gramov
    (Manjsa razdalja pomeni, da sta si dokumenta bolj podobna)

    :param cat_profile: seznam n gramov kategorije
    :param doc_profile: seznam n gramov dokumenta
    :param max_oop: vrednost out of place za n grame, ki niso bili najdeni
    :return (int): skalar razdalje
    """
    oop_sum = 0
    for position, ngram in enumerate(doc_profile.keys()):
        try:
            oop = list(cat_profile.keys()).index(ngram)
            oop_sum += oop
        except ValueError:
            # N-gram ni najden v mnozici
            oop_sum += max_oop
    return oop_sum


def walk(s, n=2):
    """ Kreira n-grame po n elementov iz s. """
    for i in range(len(s) - (n - 1)):
        yield s[i:i + n]


class LanguageIdentifier:
    def __init__(self, learn_folder='train/dohr', n=2):
        # train/dohr vsebuje Declaration of Human Rights v razlicnih prevodih

        # Slovar, v katerem so shranjeni mozni jeziki, pri cemer je kljuc oznaka jezika,
        # vrednost pa predstavlja ime jezika v izvirniku
        self.possible_langs = {
            "eng": "English",
            "ger": "Deutsch",
            "slv": "Slovensko"
        }
        # Ime datoteke kamor shranimo jezikovni model
        self.model_file = 'models/language_model_%d.json' % n
        # Slovar v katerm se nahaja predprocesirano besedilo deklaracije o neodvisnosti
        self.declaration = defaultdict(str)
        # Modeli za posamezne jezike
        self.lang_model = {}
        # Podatek o velikosti terk
        self.n_size = n
        # Regularni izraz za delno predprocesiranje besedila (odstrani stevilke in locila)
        self.regex = compile(r'[0-9%s^(\s)]' % escape(punctuation))
        # Poskusaj prebrati model iz datoteke, drugace se nauci iz deklaracij
        if not self.load_model():
            print("Creating a new model")
            self.read_learn_set(learn_folder)

    def preprocess_string(self, string):
        """ Zazene regularni izraz nad povedjo in spremeni vse whitespace v _
        prav tako oznaci zacetek in konec povedi z _ """
        return '_' + '_'.join(self.regex.sub(' ', (string.lower()).replace('\n', ' ')).split()) + '_'

    def K_most_ngrams(self, text, k=300):
        """ Vrne K najpogostejsih N-gramov iz podanega besedila. """
        # return dict(sorted(Counter(walk(text, n=self.n_size)).items(), key=lambda s: s[1], reverse=True))[:k]
        return OrderedDict(Counter(walk(text, n=self.n_size)).most_common(k))

    def read_learn_set(self, folder):
        """ Prebere deklaracije o clovekovih pravicah za izgradnjo modela. """
        for code in self.possible_langs:
            path = folder + '/' + code + '.txt'
            if not Path(path).is_file():
                print('Human rights file not found: ' + path)
                sys.exit(1)
            with open(path, 'rt', encoding='utf-8') as f:
                # use unidecode for problematic languages
                declaration = f.read()
                # Zamenja newline s presledki, prav tako spremeni vse v male crke,
                # namesto presledkov se dodajno podcrtaji (_)
                self.declaration[code] = self.preprocess_string(declaration)
        self.lang_model = {key: self.K_most_ngrams(self.declaration[key], 300) for key in self.declaration.keys()}

    def save_model(self):
        """ Shrani model jezikov v datoteko. """
        # Preko JSON shrani v datoteko
        with open(self.model_file, 'w+', encoding='utf-8') as f:
            # Write a header with model info
            f.write(str(self.n_size) + "," + ','.join(self.possible_langs.keys()) + '\n')
            json.dump(self.lang_model, f, ensure_ascii=False)

    def load_model(self):
        """ Poskusa prebrati model iz diska. """
        if Path(self.model_file).is_file():
            with open(self.model_file) as f:
                # Ima N_size,lang_codes
                model_info = f.readline().rstrip().split(',')
                if int(model_info[0]) != self.n_size:
                    # Model nima enake velikosti n, nauci se na novo
                    return False
                for lang in self.possible_langs.keys():
                    if lang not in model_info[1:]:
                        # Nov jezik za model je zaznan
                        return False
                self.lang_model = json.load(f)
                return True
        return False

    def identify(self, text):
        """
        Poskusa ugotoviti v katerem jeziku je podano besedilo

        :param text: Besedilo za katerega ugotavljamo v katerem jeziku je,
                     lahko je string ali pa ime datoteke
        :return:
        """
        # Preveri ali je podani text datoteka ali samo plaintext
        if Path(text).is_file():
            with open(text, 'rt', encoding='utf-8') as f:
                text_to_id = self.preprocess_string(f.read())
        else:
            text_to_id = self.preprocess_string(text)

        # Izgradi terke za vsak poznan jezik (iz deklaracij)
        unknown_lang_grams = self.K_most_ngrams(text_to_id, 300)

        self.save_model()
        # Izracunaj kosinusno razdaljo med tema dvema
        '''guesses = 3
        cos_similarity = {key + '+unknown': cos_linkage(known_lang_grams[key], unknown_lang_grams)
                          for key in known_lang_grams.keys()}
        guess = heapq.nsmallest(guesses, cos_similarity, key=cos_similarity.get)
        distance_sum = sum(1 / x for x in cos_similarity.values() if x > 0)
        probability_sum = 0;
        print('Guessing the language for the given text:')
        for i in range(0, guesses):
            try:
                guess_prob = (1 / cos_similarity[guess[i]]) / distance_sum
                probability_sum += guess_prob
                print('  ' + self.possible_langs[guess[i].split('+')[0]] + ' %.2f%%' % (guess_prob * 100))
            except ZeroDivisionError:
                print("Deljenje z 0! Teksta sta identicna?")'''

        # Izracunaj out of place razdaljo za podane jezike in izberi najmanjso
        distances = {lang_code: out_of_place_linkage(self.lang_model[lang_code], unknown_lang_grams)
                     for lang_code in self.possible_langs}
        guessed_lang = min(distances, key=distances.get)
        print("\nInput: %s\nGuessed language: %s\n" % (text, self.possible_langs[guessed_lang]))
        print("Distances (out of place):")
        for dist in dict(sorted(distances.items(), key=lambda x: x[1])):
            print('\t%s %d' % (self.possible_langs[dist], distances[dist]))

    def help(self):
        """ Izpise pomoc za program. """
        print("A Python script for language identification of a given text using N-grams.\n\n" +
              "Currenlty supports English, German and Slovene texts, text files and xml files.\nMore can be added" +
              " by adding the DOHR files and inserting the filename into 'possible_langs'.")
        print("\nUsage:\n\tlt = LanguageIdentifier(n=3)\n\tlt.identify(<text|file>)\n")
        print("The model is built using translations of human rights, view the header of the file for a link.")


lt = LanguageIdentifier(n=3)
lt.identify('slovene.txt')
