# Segmentacija besedila

Implementirajte program, ki bo za podan korpus segmentiral besedilo v naslednje namene:

Ugotavljanje katerim stranem pripadajo segmenti besedila in kaj se nahaja na kateri strani:
+ začetne strani (front), [ocena +0.5]
+ poglavja (body), [ocena +0.5]
+ končne strani (back), [ocena +0.5]
+ kazalo vsebine (toc), [ocena +0.5]
+ kazalo kratic (toa), [ocena +0.5]
+ povzetek (abstractSlo), [ocena +0.5]
+ povzetek v tujem jeziku (abstractEn, abstractDe), [ocena +0.5]
+ naslovna stran (titlePage), [ocena +0.5]
+ uvod (introduction), [ocena +0.5]
+ poglavje (chapter), [ocena +0.5]
+ zaključek (conclusion) in [ocena +0.5]
+ literatura (bibliography). [ocena +0.5]
+ Ugotavljanje v katerem jeziku je povzetek, [ocena +0.5]
+ Seznam poglavij v dokumentu, [ocena +1.0]
+ Razpoznava literature: prvi avtor, drugi avtor, naslov, založnik, strani, ..., [ocena +1.0]
+ Seznam uporabljenih kratic z njihovimi opisi [ocena +1.0]
+ Seznam slik in tabel z njihovimi opisi [ocena +1.0]
+ Implementacija v C++ s pomočjo regularnih izrazov [ocena +1.0]

Vhod v program bo dokument z besedilom (datoteka xml), izhod pa datoteka z rezultati (datoteka res):

Vhod: kas-4000.xml
```xml
<?xml version='1.0' encoding='UTF-8'?>

...

<page xml:id="pb2" n="2" pdf_url="http://nl.ijs.si/project/kas/pdf/000/kas-4000.pdf#page=2">
<p xml:id="pb2.p1" xml:lang="sl">PREDGOVOR</p>
<p xml:id="pb2.p2" xml:lang="sl">»Schengen, mesto ob reki Mosel, Luksemburg. Verjetno si pred slabimi dvajsetimi leti nihče
<p xml:id="pb2.p3" xml:lang="sl">Namreč ni naključje, da se mejam in obmejnim območjem posveča naraščajoča pozornost, še po
<p xml:id="pb2.p4" xml:lang="sl">Predvsem pa na svoj način pojasnjuje vse težave, omejitve in ovire, ki jih bo potrebno pre
<p xml:id="pb2.p5" xml:lang="sl">Slovenija je pristopila k Evropski uniji, ker je v njej videla sredstvo za uresničitev svo
<p xml:id="pb2.p6" xml:lang="sl">Ukrepi, kako zagotoviti varnost na slovenskih mejah, predstavljajo schengenska določila.</
<p xml:id="pb2.p7" xml:lang="sl">Le-tem je pri uresničevanju slovenske pristopne strategije namenjena osrednja pozornost, t
<p xml:id="pb2.p8" xml:lang="sl">V vsebinskem pogledu je osrednja pozornost namenjena prikazu in analizi obstoječega stanja
<p xml:id="pb2.p9" xml:lang="sl">Notranja meja Slovenije zajema bilateralne odnose s sosedi: Avstrijo, Italijo in Madžarsko
<p xml:id="pb2.p10" xml:lang="sl">V skladu s Schengenskim izvedbenim načrtom bo zunanja meja Slovenije postala schengenska 
<p xml:id="pb2.p11" xml:lang="sl">Slovenija bo tako po pričakovanjih konec leta 2006 ali v začetku 2007, kar zadeva policij
</page>
```
Izhod: kas-4000.res
```
ID CLASS
pb1.p1 titlePage 
pb1.p2 titlePage 
pb1.p3 titlePage 
...
pb3.p1 toc 
pb3.p2 toc 
pb3.p3 toc 
...

pb41.p1 abstractSlo
pb41.p2 abstractSlo
pb41.p3 abstractSlo
pb41.p4 abstractSlo
pb41.p7 abstractEn
pb41.p8 abstractEn
pb42.p1 bibliography 
pb42.p2 acronym 
...

pb5 body
pb6 body
pb7 body
...
pb1 front
pb2 front
pb3 front
...

pb41 back
pb42 back
pb43 back
...

pb6: chapter A

pb10: chapter B

keywords: a, b, c, d ...

acronyms:

HTML - .....

LaTeX - ....

FERI - ....

bibliography:

avtor1, avtor 2, ....

avtor1, avtor2, ...
```
