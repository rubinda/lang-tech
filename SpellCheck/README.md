# Popravljanje pravopisnih napak

Implementirajte program za popravljanje pravopisnih napak. Program naj vsebuje naslednje korake:

1. Ustvarite slovar, ki za vsako besedo vsebuje frekvenco pojavitev v učni množici. Vse besede so predstavljene z malimi črkami.
2. Napišite funkcijo, ki za podano besedo vrne vse besede na razdalji urejanja 1. Operacije urejanja so brisanje, transpozicija, zamenjava in vstavljanje.
3. Napišite funkcijo, ki za podano besedo vrne vse besede na razdalji urejanja 2. Pri tem uporabite funkcijo za vračanje besed, ki so na razdalji 1.
4. Napišite funkcijo, ki za podano besedo vrne vse besede iz slovarja na razdalji urejanja 2.
5. Napišite funkcijo, ki za podano besedo vrne seznam kandidatk in njihovih verjetnosti urejanja. Uporabimo poenostavljen model, ki uporablja naslednja pravila:
    + Če je podana beseda že v slovarju, je ta beseda prva in zadnja v seznamu kandidatk. Njena verjetnost urejanja je 1.
    + Če v slovarju ni podana besede, v seznam kandidatk dodamo besede, ki so v slovarju na razdalji urejanja 1. Njihove verjetnosti urejanja se normalizirajo glede na frekvence v slovarju in vsoto vseh frekvenc kandidatk.
    + Če v slovarju ni podane besede in kandidatk na razdalji urejanja 1, v  seznam kandidatk dodamo besede, ki so v slovarju na razdalji urejanja 2. Njihove verjetnosti urejanja se normalizirajo glede na frekvence v slovarju in vsoto vseh frekvenc kandidatk.
    + Če ni izpolnjen nobeden od predhodnih pogojev, je kandidatka podana beseda z verjetnostjo urejanja 1.
6. Napišite funkcijo, ki bo z uporabo jezikovnega modela, ki ste ga implementirali na eni od prejšnjih vaj, popravila podano poved s pomočjo naslednjih pravil:
    + Izračunamo verjetnost povedi brez uporabe kandidatk.
    + Izračunamo verjetnost povedi, pri kateri uporabimo le eno od kandidatk. Ko računamo verjetnost n-grama, verjetnost množimo z verjetnostjo urejanja kandidatke.
    + Za kandidatke, ki niso v slovarju uporabimo verjetnost 1/V.
Rezultat je poved, ki ima maksimalno verjetnost. Tukaj si pomagamo z logaritmi.

>Slovar ustvarite s pomočjo naslednjega korpusa: [big.txt](corpus/big.txt)
>Uspešnost algoritma preverite s pomočjo naslednjega korpusa: [Birkbeck spelling error corpus](holbrook-tagged.dat).

Oddajte programsko kodo programa in dokument pdf. V tem dokumentu opišite doseženo uspešnost opisane metode in metode, ki uporablja le kandidatko z največjo verjetnostjo urejanja (brez jezikovnega modela).