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

chain = {}
for word in words:
    for i in range(2,len(word)):
        key = word[i-2] + word[i-1]
        if key in chain:
            chain[key].append(word[i])
        else:
            chain[key] = [word[i]]

keys = list(chain.keys())
def markov():
    start = choice(keys)
    w = start
    for i in range(randint(2,10)):
        k = w[-2] + w[-1]
        if k in chain:
            w += choice(chain[k])
        else:
            break
    return w

for i in range(20):
    w = markov().capitalize()
    print(w) if w.lower() not in words else print("DUPLICATE")



