import re

# put the word at the front for the keys
preps = r"\b(?:mit|an|furs?|ubers?|als|i(?:ns?|m)?|zu[rm]?|vo[nm]|aufs?|bis|durch|gegen|ohne|um|aus|auser|beim?|gegenuber|nach|seit|entlang|hinter|neben|unter|vorm?|zwischen|(?:an)?statt|trotz|wahrend|wegen|auserhalb|innerhalb|oberhalb|unterhalb|diesseits|jenseits|beiderseits)\b"
word = r"\w+"
objs = r"\b(?:selbst|sich|etwas|jede[rnms]|etw|jd[rnms]?)\b"

p = re.compile(r"\b(?:{objs}|{preps}\s+{word})\b". \
               format(preps=preps, word=word, objs=objs))
pr = re.compile(r"(?:^|\s){preps}(?:\s|$)".format(preps=preps))

# remove {gender}, [type], (objects)
extras = r"(?:{[^\}]+}|\[[^\]]*\]|\([^\)]+\))"
e = re.compile(extras)

# remove articles
articles = r"(?:^|\s)(?:d(?:e[rnms]|as|ie)|k?ein(?:e[rnms]?)?)(?:\s|$)"
g = re.compile(articles)

# Not a word
spw = re.compile(r"[^\w\(\)\{\}\[\]]+")
sp = re.compile(r"\W+")
ssp = re.compile(r"\s+")

# We'll walk the strippers
# For each element, we'll go over all the sub-elements
# The sub-elements are regex, replacement pairs
# If one of these reduces the key to nothing,
# then reject it, and skip all following pairs
# until the next group
#
strippers = [
    [
        [spw, ' '],  # non letters -> space
        [e, ' '],   # delete parenthesized
        [g, ' '],   # delete articles
        [p, ' '],   # delete prep + objects
    ], [
        [sp, ' '],  # non letters -> space
        [pr, ' '],  # delete any preps left
    ], [
        [ssp, ' '], # collapse spaces
    ]
]

def getkey(key):
    for sstrippers in strippers:
        nkey = key
        for s, r in sstrippers:
            nkey = s.sub(r, nkey).strip()
            if len(nkey) == 0: break
            key = nkey

    # return the biggest word in the term
    return max(key.split(),
               key=lambda k: len(k))

# the definitions are
# definition {tab} part-of-speech pairs
# Return (part-of-speech) definition
d = re.compile(r"\s*\t\s*")
def getdef(odef):
    try: dfn, ops = d.split(odef, 1)
    except ValueError:
        print("Split error: '{}'".format(odef))
        raise

    if ops.strip() != '':
        dfn = "({}) {}".format(ops.strip(), dfn)
    return dfn
