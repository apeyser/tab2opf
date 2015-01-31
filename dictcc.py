import re

# put the word at the front for the keys
preps = r"\b(?:mit|an|fur|uber|als|in|zu|von|auf|bis|durch|gegen|ohne|um|aus|auser|bei|gegenuber|nach|seit|entlang|hinter|neben|unter|vor|zwischen|(?:an)?statt|trotz|wahrend|wegen|auserhalb|innerhalb|oberhalb|unterhalb|diesseits|jenseits|beiderseits)\b"
word = r"[\w\.]+"
objs = r"\b(?:(?:selbst|sich|etwas|jede[rnms]?)\b|etw\.|jd[rnms]?\.)"
p = re.compile(r"^(?:\s*(?:{objs}|{preps}\s+{word}))+". \
               format(preps=preps, word=word, objs=objs))
pr = re.compile(preps)

# puncts
puncts = re.compile(r"[,%'\"\\/]")
per = re.compile(r"(?:\.\.+|\s\.\s)")
aper = re.compile(r"\.+")

# remove {gender}, [type], (objects)
extras = r"(?:{[^\}]+}|\[[^\]]*\]|\([^\)]+\))"
e = re.compile(r"\s*{extras}".format(extras=extras))

# remove articles
articles = r"\b(?:(?:d(?:er|as|ie|en|em|es)|ein(?:e|er|en|em|es))\b)"
g = re.compile(r"{articles}".format(articles=articles))

sp = re.compile(r"\s+")

strippers = [
    [[puncts], " "],
    [[per], " "],
    [[e], ''], 
    [[g], ''], 
    [[p, aper], ''],
    [[pr], '']
]

def getkey(key):
    for s, r in strippers:
        nkey = key
        for s_ in s:
            nkey = s_.sub(r, nkey).strip()

        if len(nkey) == 0: break
        key = nkey

    key = key.lstrip().split(None, 1)[0]
    return sp.sub(" ", key)

d = re.compile(r"\s*\t\s*")

def getdef(odef):
    dfn, ops = d.split(odef, 1)
    if ops.strip() != '':
        dfn = "({}) {}".format(ops.strip(), dfn)
    return dfn
