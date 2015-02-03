# tab2opf
Remake of tab2opf dictionary builder for kindle

Script to convert tab delimited dictionary files into opf file to run
with kindlegen into a translation lookup dictionary for kindle.

Based on the generally available tab2opf.py by Klokan Petr Přidal
(www.klokan.cz) from 2007

The script has been mostly rewritten and extended. The encoding
convolutions have been removed, and the code migrated to python3

The input form is:
Word(s) \\t Definition

By running tab2opf.py path/file.txt in the current directory file.opf
and file*.html are created which can then be converted with kindlegen
file.opf into file.mobi

--source and --target options define which language to which we are
translating.

tab2opf has a -m option to load a module to load getkey and getdef
functions and mapping dictionary from that namespace into the current
one; if it doesn't find such defined member(s), no error is produced.

getkey converts the term (the Word(s)) into a search key.  getdef
converts Definition in some arbitrary way.  mapping is a dictionary
mapping from char -> char to replace some set of characters in the
input with characters in the output.

Used and tested is the dictcc.py, which converts a dict.cc german ->
english dictionary (http://www.dict.cc/?s=about%3Awordlist&l=e). The
keys are the longest word in the Word(s) after removal of
prepositional phrases and some pronouns (in getkey). The definitions
remap the dict.cc pattern of "definition \\t part-of-speech" into
(part-of-speech) definiton.
