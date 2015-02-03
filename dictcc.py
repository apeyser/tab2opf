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
sp = re.compile(r"\W+")
ssp = re.compile(r"\s+")

# goto exception for denoise
class Reject(Exception): pass

# apply reg -> ' ' on key
# if reduces to zero, goto Reject
def tryreg(key, reg):
    nkey = reg.sub(' ', key).strip()
    if len(nkey) == 0: raise Reject()
    return nkey

# Try a series of reductions
# tryreg goes out of sequence by calling goto
# return non-null key
def denoise(key):
    try: 
        key = tryreg(key, e)   # delete parenthesized
        key = tryreg(key, sp)  # non letters -> space
        key = tryreg(key, g)   # delete articles
        key = tryreg(key, p)   # delete prep + objects
    except Reject: pass

    try: key = tryreg(key, pr) # delete any preps left
    except Reject: pass

    return key

# Map key onto some sensible long word in the term,
# trying to avoid punctiation, gender marking
# and parenthesized information
def getkey(key):
    key = denoise(key)
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
