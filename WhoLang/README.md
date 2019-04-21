# Ugotavljanje jezika besedila

Implementirajte algoritem za detekcijo jezika, ki temelji na osnovi znakovnih n-gramov. 


Podrobnejši opis delovanja algoritma najdete v prosojnicah in v naslednjem članku:

[N-Gram-Based Text Categorization](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.21.3248&rep=rep1&type=pdf)

##### English:

Implement a  n-gram based text categorization algorithm from the following article:

[N-Gram-Based Text Categorization](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.21.3248&rep=rep1&type=pdf)


Using the implemented algorithm annotate the language of paragraphs in various languages.

### Resitev

Znotraj `who_lang.py` se nahaja razred imenovan `LanguageIdentifier`. Kreiramo novo instanco razreda in poklicemo metodo
`LanguageIdentifier.identify(<datoteka>)`, pri cemer je _datoteka_ parameter poti do tekstovne
datoteke z besedilom, katerega jezik zelimo ugotoviti. Primera datoteke za [slovenski](slovene.txt) in 
[nemski](deutsch.txt) jezik sta prilozena repozitoriju.