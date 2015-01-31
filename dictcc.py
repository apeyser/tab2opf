import re

p = re.compile(r"\s*(?:(?:jd\.|jdn\.|jdm\.|etw\.|\\|/)\s*)*")
g = re.compile(r"\s*(?:{[^\}]+}|\[[^\]]*\])")
s = re.compile(r"^\s*(\([^\)]+\))\s*(.*)")

def getkey(okey):
    key = p.sub("", okey)
    key = g.sub("", key)
    m = s.match(key)
    if m:
        paren, head = m.group(1, 2)
        key = "{} {}".format(head, paren)

    if len(key) == 0:
        print "Missing key {}".format(okey)
    return key
