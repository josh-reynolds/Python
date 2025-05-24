from random import randint, choice

# Non-English place names in Sheldomar Valley ~~~~~~~~~~
# Cryllor, Sheldomar, Niole Dra, Gradsul, Javan, Hool, Hokar, Jurnre, Gryrax, Ulek, Keo(land),
# Tringlee, Kewl, Lortmil, Pomarj, Suss, Oyt(wood), Sterich, Istivin, Davish, Flen, Hochoch, Gorna

# Syllable counts ~~~~~~~~~~~~~~~~~~~~~~~~~
# 2, 3, 2 + 1, 2, 2, 1, 2, 2, 2, 2, (2), 2, 1, 2, 2, 1, (2), 2, 3, 2, 1, 2, 2

# Syllables ~~~~~~~~~~~~~~~~~~
# cry, llor, shel, do, mar, nio, le, dra, grad, sul, ja, van, hool, ho, kar, jurn, re, gry, rax, u,
# lek, keo, trin, glee, kewl, lort, mil, pom, arj, suss, oyt, ster, ich, ist, i, vin, dav, ish,
# flen, hoch, och, gor, na

# Initial Consonants
# cr, ll, sh, d, m, n, l, dr, gr, s, j, v, h, h, k, j, r, gr, r, _, l, k, tr, gl, k, l, m, p,
# _, s, _, st, _, _, _, v, d, _, fl, h, _, g, n

# Vowels
# y, o, e, o, a, io, e, a, a, u, a, a, oo, o, a, u, e, y, a, u, e, eo, i, ee, ew, o, i, o, a, u,
# oy, e, i, i, i, i, a, i, e, o, o, o, a

# Final Consonants
# _, r, l, _, r, _, _, _, d, l, _, n, l, _, r, rn, _, _, x, _, k, _, n, _, l, rt, l, m, rj,
# ss, t, r, ch, st, _, n, v, sh, n, ch, ch, r, _

def make_chain(word_list):
    chain = {}
    for word in word_list:
        for i in range(2,len(word)):
            key = word[i-2] + word[i-1]
            if key in chain:
                chain[key].append(word[i])
            else:
                chain[key] = [word[i]]
    return chain

def markov(keys, chain):
    start = choice(keys)
    w = start
    for i in range(randint(2,10)):
        k = w[-2] + w[-1]
        if k in chain:
            w += choice(chain[k])
        else:
            break
    return w

lengths = [2, 3, 2, 1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 1, 2, 3, 2, 1, 2, 2]

initials = ["cr", "ll", "sh", "d", "m", "n", "l", "dr", "gr", "s", "j", "v", "h", "h", "k", "j", "r", "gr", "r", "_", "l", "k", "tr", "gl", "k", "l", "m", "p", "_", "s", "_", "st", "_", "_", "_", "v", "d", "_", "fl", "h", "_", "g", "n"]

vowels = ["y", "o", "e", "o", "a", "io", "e", "a", "a", "u", "a", "a", "oo", "o", "a", "u", "e", "y", "a", "u", "e", "eo", "i", "ee", "ew", "o", "i", "o", "a", "u", "oy", "e", "i", "i", "i", "i", "a", "i", "e", "o", "o", "o", "a"]

finals = ["_", "r", "l", "_", "r", "_", "_", "_", "d", "l", "_", "n", "l", "_", "r", "rn", "_", "_", "x", "_", "k", "_", "n", "_", "l", "rt", "l", "m", "rj", "ss", "t", "r", "ch", "st", "_", "n", "v", "sh", "n", "ch", "ch", "r", "_"]


def make_word():
    result = ""
    length = choice(lengths)
    for i in range(length):
        result += choice(initials)
        result += choice(vowels)
        result += choice(finals)
    return result.replace("_","")

# This works, but most of the words are unusable junk... needs more filtering...

for i in range(20):
    print(make_word().capitalize())
print("------------------")

# trying an alternate approach using a Markov chain --------------------------

# 'pure' Sheldomar Valley word set
#words = ["cryllor", "sheldomar", "niole", "dra", "gradsul", "javan", "hool", "hokar", "jurnre", "gryrax", "ulek", "keo", "tringlee", "kewl", "lortmil", "pomarj", "suss", "oyt", "sterich", "istivin", "davish", "flen", "hochoch", "gorna"]

# 'High Gygaxian" word set
words = ["cryllor", "sheldomar", "niole", "dra", "gradsul", "javan", "hool", "hokar", "jurnre", "gryrax", "ulek", "keo", "tringlee", "kewl", "lortmil", "pomarj", "suss", "oyt", "sterich", "istivin", "davish", "flen", "hochoch", "gorna", "oerik", "oerth", "flanaess", "dramidj", "deklo", "galda", "kara", "ipp", "phost", "usk", "yarpick", "flan", "oeridian", "suel", "baklunish", "suloise", "kendeen", "euroz", "jebli", "celbit", "amedio", "tilvanot", "duxchan", "hepmona", "rhola", "neheli", "aerdi", "nyr", "dyv", "nyrondy", "furyondy", "sunndi", "yar", "telfic", "tenh", "voll", "yatil", "rax", "fruztii", "schnai", "naelax", "onnwal", "iuz", "veluna", "celene", "emridy", "kron", "velverdyva", "hommlet", "zuggtmoy", "almor", "bissel", "dyvers", "ekbir", "chendl", "rauxes", "molag", "cruski", "idee", "dorakaa", "ket", "lopolla", "rel", "mord", "ratik", "asperdi", "lendore", "reltarma", "lo", "nevond", "yecha", "tusmit", "sefmur", "ull", "ulakand", "urnst", "leukish", "radigast", "mitrik", "verbobonc", "elredd", "wegwiur", "zeif", "densac", "gearnat", "grendep", "jeklea", "oljatt", "quag", "relmor", "solnor", "whyestil", "abbor", "alz", "blemu", "tusman", "yecha", "pelisso", "corusk", "clatspur", "sulhaut", "ulsprue", "artonsamay", "att", "blashikmund", "dulsi", "ery", "fals", "flanmi", "fler", "imeda", "neen", "opicm", "ritensa", "selintan", "teesar", "thelly", "trask", "tuflik", "veng", "yol", "zumker", "adri", "celadon", "gamboge", "vesve", "fellreev", "hraak", "nuther", "meno", "rieu", "boccob", "beory", "incabulos", "istus", "kord", "nerull", "pelor", "procan", "rao", "tharizdun", "ulaa", "wee", "jas", "zilchus", "cyndor", "allitur", "atroa", "beltar", "berei", "bleredd", "bralm", "celestian", "delleb", "ehlonna", "fharlanghn", "erythnul", "fortubo", "geshta", "heironeous", "hextor", "joramy", "kurell", "lirr", "llerg", "lydia", "myhriss", "norebo", "obad", "hai", "olidammara", "phaulkon", "pholtus", "phyton", "pyremius", "ralishaz", "raxivort", "sotillion", "syrul", "telchur", "trithereon", "velnius", "wenta", "xan", "yae", "xerbo", "zodal", "rudd", "wastri", "zagyg", "zuoken", "iggwilv", "tsojcanth"]


c = make_chain(words)
k = list(c.keys())
for i in range(20):
    w = markov(k, c).capitalize()
    print(w) if w.lower() not in words else print("DUPLICATE")
print("------------------")

# alternate list - only words containing an 'a' - see vowel groupings below ~~~~~~~
words2 = ["alz", "att", "bralm", "dra", "fals", "fharlanghn", "flan", "galda", "jas", "javan", "kara", "quag", "rax", "trask", "xan", "yar", "hraak", "ulaa", "aerdi", "hai", "schnai", "rao", "rauxes", "phaulkon", "sulhaut", "dorakaa", "flanaess", "naelax", "artonsamay", "beltar", "densac", "geshta", "reltarma", "wenta", "yecha", "yecha", "gearnat", "teesar", "asperdi", "selintan", "amedio", "celadon", "ehlonna", "hepmona", "sheldomar", "gamboge", "veluna", "velverdyva", "adri", "davish", "dramidj", "flanmi", "radigast", "ralishaz", "ratik", "wastri", "yarpick", "yatil", "imeda", "ritensa", "olidammara", "raxivort", "tilvanot", "allitur", "baklunish", "blashikmund", "tharizdun", "incabulos", "abbor", "almor", "gorna", "hokar", "joramy", "lopolla", "molag", "obad", "oljatt", "onnwal", "pomarj", "procan", "rhola", "tsojcanth", "zodal", "atroa", "clatspur", "duxchan", "gradsul", "tusman", "ulakand", "gryrax", "zagyg"]

c = make_chain(words2)
keys = list(c.keys())
for i in range(20):
    w = markov(k, c).capitalize()
    print(w) if w.lower() not in words else print("DUPLICATE")
print("------------------")

# breaking out vowel groupings ~~~~~~~~~
# [a] alz
# [a] att
# [a] bralm
# [a] dra
# [a] fals
# [a] fharlanghn
# [a] flan
# [a] galda
# [a] jas
# [a] javan
# [a] kara
# [a] quag
# [a] rax
# [a] trask
# [a] xan
# [a] yar
# [aa] hraak
# [aa|u] ulaa
# [ae|i] aerdi
# [ai] hai
# [ai] schnai
# [ao] rao
# [au|e] rauxes
# [au|o] phaulkon
# [au|u] sulhaut
# [a|aa|o] dorakaa
# [a|ae] flanaess
# [a|ae] naelax
# [a|ay|o] artonsamay
# [a|e] beltar
# [a|e] densac
# [a|e] geshta
# [a|e] reltarma
# [a|e] wenta
# [a|e] yecha
# [a|e] yecha
# [a|ea] gearnat
# [a|ee] teesar
# [a|e|i] asperdi
# [a|e|i] selintan
# [a|e|io] amedio
# [a|e|o] celadon
# [a|e|o] ehlonna
# [a|e|o] hepmona
# [a|e|o] sheldomar
# [a|e|o]gamboge
# [a|e|u] veluna
# [a|e|y] velverdyva
# [a|i] adri
# [a|i] davish
# [a|i] dramidj
# [a|i] flanmi
# [a|i] radigast
# [a|i] ralishaz
# [a|i] ratik
# [a|i] wastri
# [a|i] yarpick
# [a|i] yatil
# [a|i|e] imeda
# [a|i|e] ritensa
# [a|i|o] olidammara
# [a|i|o] raxivort
# [a|i|o] tilvanot
# [a|i|u] allitur
# [a|i|u] baklunish
# [a|i|u] blashikmund
# [a|i|u] tharizdun
# [a|i|u|o] incabulos
# [a|o] abbor
# [a|o] almor
# [a|o] gorna
# [a|o] hokar
# [a|o] joramy
# [a|o] lopolla
# [a|o] molag
# [a|o] obad
# [a|o] oljatt
# [a|o] onnwal
# [a|o] pomarj
# [a|o] procan
# [a|o] rhola
# [a|o] tsojcanth
# [a|o] zodal
# [a|oa] atroa
# [a|u] clatspur
# [a|u] duxchan
# [a|u] gradsul
# [a|u] tusman
# [a|u] ulakand
# [a|y] gryrax
# [a|y] zagyg
# [e] bleredd
# [e] celene
# [e] chendl
# [e] delleb
# [e] elredd
# [e] flen
# [e] fler
# [e] grendep
# [e] ket
# [e] kewl
# [e] llerg
# [e] rel
# [e] tenh
# [e] veng
# [e] vesve
# [ee] neen
# [ee] wee
# [ee|i] idee
# [ee|i] tringlee
# [ei] zeif
# [ei|eou|o] heironeous
# [eo] keo
# [eo|y] beory
# [eu|i] leukish
# [eu|o] euroz
# [e|ea] jeklea
# [e|ee] fellreev
# [e|ee] kendeen
# [e|ei] berei
# [e|eo|i] trithereon
# [e|i] bissel
# [e|i] celbit
# [e|i] ekbir
# [e|i] jebli
# [e|i] neheli
# [e|i] sterich
# [e|i] telfic
# [e|ia] celestian
# [e|io] niole
# [e|iu] velnius
# [e|iu] wegwiur
# [e|iu|y] pyremius
# [e|i|o] pelisso
# [e|i|y] emridy
# [e|o] deklo
# [e|o] hextor
# [e|o] hommlet
# [e|o] lendore
# [e|o] nevond
# [e|o] norebo
# [e|o] pelor
# [e|o] relmor
# [e|o] verbobonc
# [e|o] xerbo
# [e|oi|u] suloise
# [e|o} meno
# [e|u] blemu
# [e|u] jurnre
# [e|u] kurell
# [e|u] nerull
# [e|u] nuther
# [e|u] sefmur
# [e|u] telchur
# [e|u] ulek
# [e|u] zumker
# [e|uo] zuoken
# [e|u|y] erythnul
# [e|y] dyvers
# [e|y] ery
# [e|y] thelly
# [i] iggwilv
# [i] ipp
# [i] istivin
# [i] lirr
# [i] mitrik
# [ia|y] lydia
# [ieu] rieu
# [ii|u] fruztii
# [iu] iuz
# [i|ia|oe] oeridian
# [i|io|o] sotillion
# [i|o] lortmil
# [i|o] opicm
# [i|oe] oerik
# [i|u] cruski
# [i|u] dulsi
# [i|u] istus
# [i|u] sunndi
# [i|u] tuflik
# [i|u] tusmit
# [i|u] zilchus
# [i|y] myhriss
# [i|ye] whyestil
# [o] boccob
# [o] hochoch
# [o] kord
# [o] kron
# [o] lo
# [o] mord
# [o] phost
# [o] solnor
# [o] voll
# [oe] oerth
# [oo] hool
# [oy] oyt
# [oy|u] zuggtmoy
# [o|u] corusk
# [o|u] fortubo
# [o|u] pholtus
# [o|y] cryllor
# [o|y] cyndor
# [o|y] nyrondy
# [o|y] phyton
# [u] rudd
# [u] suss
# [u] ull
# [u] urnst
# [u] usk
# [ue] suel
# [u|ue] ulsprue
# [u|y|yo] furyondy
# [y] dyv
# [y] nyr
# [y] syrul
# [yae] yae
# [yo] yol

