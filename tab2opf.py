#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Script for conversion of Stardict tabfile (<header>\t<definition>
# per line) into the OPF file for MobiPocket Dictionary
#
# For usage of dictionary convert it by:
# (wine) mobigen.exe DICTIONARY.opf
#
# MobiPocket Reader at: www.mobipocket.com for platforms:
#   PalmOs, Windows Mobile, Symbian (Series 60, Series 80, 90, UIQ), Psion, Blackberry, Franklin, iLiad (by iRex), BenQ-Siemens, Pepper Pad..
#   http://www.mobipocket.com/en/DownloadSoft/DownloadManualInstall.asp
# mobigen.exe available at:
#   http://www.mobipocket.com/soft/prcgen/mobigen.zip
#
# Copyright (C) 2007 - Klokan Petr Přidal (www.klokan.cz)
#
#
# Version history:
# 0.1 (19.7.2007) Initial version
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

# VERSION
VERSION = "0.2"

# FILENAME is a first parameter on the commandline now

import sys
import os
import argparse
from itertools import islice, count, ifilter
from contextlib import contextmanager
from operator import itemgetter
import importlib

from unicodedata import normalize, decomposition, combining
import string
from exceptions import UnicodeEncodeError

mapping_win = {
    0x80: 'e', #EURO SIGN
    #0x81: '', #UNDEFINED
    0x82: "'", #SINGLE LOW-9 QUOTATION MARK
    0x83: 'f', #LATIN SMALL LETTER F WITH HOOK
    0x84: '"', #DOUBLE LOW-9 QUOTATION MARK
    0x85: '...', #HORIZONTAL ELLIPSIS
    0x86: '', #DAGGER
    0x87: '', #DOUBLE DAGGER
    0x88: '', #MODIFIER LETTER CIRCUMFLEX ACCENT
    0x89: '%%', #PER MILLE SIGN
    0x8A: 'S', #LATIN CAPITAL LETTER S WITH CARON
    0x8B: '<<', #SINGLE LEFT-POINTING ANGLE QUOTATION MARK
    0x8C: 'O', #LATIN CAPITAL LIGATURE OE
    #0x8D: '', #UNDEFINED
    0x8E: 'Z', #LATIN CAPITAL LETTER Z WITH CARON
    #0x8F: '', #UNDEFINED
    #0x90: '', #UNDEFINED
    0x91: "'", #LEFT SINGLE QUOTATION MARK
    0x92: "'", #RIGHT SINGLE QUOTATION MARK
    0x93: '"', #LEFT DOUBLE QUOTATION MARK
    0x94: '"', #RIGHT DOUBLE QUOTATION MARK
    0x95: '.', #BULLET
    0x96: '-', #EN DASH
    0x97: '--', #EM DASH
    0x98: '~', #SMALL TILDE
    0x99: '(tm)', #TRADE MARK SIGN
    0x9A: 's', #LATIN SMALL LETTER S WITH CARON
    0x9B: '>', #SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
    0x9C: 'o', #LATIN SMALL LIGATURE OE
    #0x9D: '', #UNDEFINED
    0x9E: 'z', #LATIN SMALL LETTER Z WITH CARON
    0x9F: 'y', #LATIN CAPITAL LETTER Y WITH DIAERESIS
    0xA0: ' ', #NO-BREAK SPACE
    0xA1: '!', #INVERTED EXCLAMATION MARK
    0xA2: 'c', #CENT SIGN
    0xA3: 'L', #POUND SIGN
    0xA4: '$', #CURRENCY SIGN
    0xA5: 'Y', #YEN SIGN
    0xA6: '|', #BROKEN BAR
    0xA7: 'SS', #SECTION SIGN
    0xA8: '', #DIAERESIS
    0xA9: '(c)', #COPYRIGHT SIGN
    0xAA: '^a', #FEMININE ORDINAL INDICATOR
    0xAB: '<<', #LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    0xAC: '!', #NOT SIGN
    0xAD: '-', #SOFT HYPHEN
    0xAE: '(reg)', #REGISTERED SIGN
    0xAF: '', #MACRON
    0xB0: '^o', #DEGREE SIGN
    0xB1: '+/-', #PLUS-MINUS SIGN
    0xB2: '^2', #SUPERSCRIPT TWO
    0xB3: '^3', #SUPERSCRIPT THREE
    0xB4: '', #ACUTE ACCENT
    0xB5: 'm', #MICRO SIGN
    0xB6: 'PP', #PILCROW SIGN
    0xB7: '.', #MIDDLE DOT
    0xB8: '', #CEDILLA
    0xB9: '^1', #SUPERSCRIPT ONE
    0xBA: '^o', #MASCULINE ORDINAL INDICATOR
    0xBB: '>>', #RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    0xBC: '1/4', #VULGAR FRACTION ONE QUARTER
    0xBD: '1/2', #VULGAR FRACTION ONE HALF
    0xBE: '3/4', #VULGAR FRACTION THREE QUARTERS
    0xBF: '?', #INVERTED QUESTION MARK
    0xC0: 'A', #LATIN CAPITAL LETTER A WITH GRAVE
    0xC1: 'A', #LATIN CAPITAL LETTER A WITH ACUTE
    0xC2: 'A', #LATIN CAPITAL LETTER A WITH CIRCUMFLEX
    0xC3: 'A', #LATIN CAPITAL LETTER A WITH TILDE
    0xC4: 'A', #LATIN CAPITAL LETTER A WITH DIAERESIS
    0xC5: 'A', #LATIN CAPITAL LETTER A WITH RING ABOVE
    0xC6: 'A', #LATIN CAPITAL LETTER AE
    0xC7: 'C', #LATIN CAPITAL LETTER C WITH CEDILLA
    0xC8: 'E', #LATIN CAPITAL LETTER E WITH GRAVE
    0xC9: 'E', #LATIN CAPITAL LETTER E WITH ACUTE
    0xCA: 'E', #LATIN CAPITAL LETTER E WITH CIRCUMFLEX
    0xCB: 'E', #LATIN CAPITAL LETTER E WITH DIAERESIS
    0xCC: 'I', #LATIN CAPITAL LETTER I WITH GRAVE
    0xCD: 'I', #LATIN CAPITAL LETTER I WITH ACUTE
    0xCE: 'I', #LATIN CAPITAL LETTER I WITH CIRCUMFLEX
    0xCF: 'I', #LATIN CAPITAL LETTER I WITH DIAERESIS
    0xD0: 'I', #LATIN CAPITAL LETTER ETH
    0xD1: 'N', #LATIN CAPITAL LETTER N WITH TILDE
    0xD2: 'O', #LATIN CAPITAL LETTER O WITH GRAVE
    0xD3: 'O', #LATIN CAPITAL LETTER O WITH ACUTE
    0xD4: 'O', #LATIN CAPITAL LETTER O WITH CIRCUMFLEX
    0xD5: 'O', #LATIN CAPITAL LETTER O WITH TILDE
    0xD6: 'O', #LATIN CAPITAL LETTER O WITH DIAERESIS
    0xD7: '(x)', #MULTIPLICATION SIGN
    0xD8: 'O', #LATIN CAPITAL LETTER O WITH STROKE
    0xD9: 'U', #LATIN CAPITAL LETTER U WITH GRAVE
    0xDA: 'U', #LATIN CAPITAL LETTER U WITH ACUTE
    0xDB: 'U', #LATIN CAPITAL LETTER U WITH CIRCUMFLEX
    0xDC: 'U', #LATIN CAPITAL LETTER U WITH DIAERESIS
    0xDD: 'Y', #LATIN CAPITAL LETTER Y WITH ACUTE
    0xDE: 'TH', #LATIN CAPITAL LETTER THORN
    0xDF: 's', #LATIN SMALL LETTER SHARP S
    0xE0: 'a', #LATIN SMALL LETTER A WITH GRAVE
    0xE1: 'a', #LATIN SMALL LETTER A WITH ACUTE
    0xE2: 'a', #LATIN SMALL LETTER A WITH CIRCUMFLEX
    0xE3: 'a', #LATIN SMALL LETTER A WITH TILDE
    0xE4: 'a', #LATIN SMALL LETTER A WITH DIAERESIS
    0xE5: 'a', #LATIN SMALL LETTER A WITH RING ABOVE
    0xE6: 'a', #LATIN SMALL LETTER AE
    0xE7: 'c', #LATIN SMALL LETTER C WITH CEDILLA
    0xE8: 'e', #LATIN SMALL LETTER E WITH GRAVE
    0xE9: 'e', #LATIN SMALL LETTER E WITH ACUTE
    0xEA: 'e', #LATIN SMALL LETTER E WITH CIRCUMFLEX
    0xEB: 'e', #LATIN SMALL LETTER E WITH DIAERESIS
    0xEC: 'i', #LATIN SMALL LETTER I WITH GRAVE
    0xED: 'i', #LATIN SMALL LETTER I WITH ACUTE
    0xEE: 'i', #LATIN SMALL LETTER I WITH CIRCUMFLEX
    0xEF: 'i', #LATIN SMALL LETTER I WITH DIAERESIS
    0xF0: 'eth', #LATIN SMALL LETTER ETH
    0xF1: 'n', #LATIN SMALL LETTER N WITH TILDE
    0xF2: 'o', #LATIN SMALL LETTER O WITH GRAVE
    0xF3: 'o', #LATIN SMALL LETTER O WITH ACUTE
    0xF4: 'o', #LATIN SMALL LETTER O WITH CIRCUMFLEX
    0xF5: 'o', #LATIN SMALL LETTER O WITH TILDE
    0xF6: 'o', #LATIN SMALL LETTER O WITH DIAERESIS
    0xF7: '/', #DIVISION SIGN
    0xF8: 'o', #LATIN SMALL LETTER O WITH STROKE
    0xF9: 'u', #LATIN SMALL LETTER U WITH GRAVE
    0xFA: 'u', #LATIN SMALL LETTER U WITH ACUTE
    0xFB: 'u', #LATIN SMALL LETTER U WITH CIRCUMFLEX
    0xFC: 'u', #LATIN SMALL LETTER U WITH DIAERESIS
    0xFD: 'y', #LATIN SMALL LETTER Y WITH ACUTE
    0xFE: 'th', #LATIN SMALL LETTER THORN
    0xFF: 'y', #LATIN SMALL LETTER Y WITH DIAERESIS
}

mapping_punct = {
    0x2000: ' ', #EN QUAD (0x2000)
    0x2001: ' ', #EM QUAD (0x2001)
    0x2002: ' ', #EN SPACE (0x2002)
    0x2003: ' ', #EM SPACE (0x2003)
    0x2004: ' ', #THREE-PER-EM SPACE (0x2004)
    0x2005: ' ', #FOUR-PER-EM SPACE (0x2005)
    0x2006: ' ', #SIX-PER-EM SPACE (0x2006)
    0x2007: ' ', #FIGURE SPACE (0x2007)
    0x2008: ' ', #PUNCTUATION SPACE (0x2008)
    0x2009: ' ', #THIN SPACE (0x2009)
    0x200A: ' ', #HAIR SPACE (0x200A)
    0x200B: ' ', #ZERO WIDTH SPACE (0x200B)
    0x200C: ' ', #ZERO WIDTH NON-JOINER (0x200C)
    0x200D: ' ', #ZERO WIDTH JOINER (0x200D)
    0x200E: '->', #LEFT-TO-RIGHT MARK (0x200E)
    0x200F: '<-', #RIGHT-TO-LEFT MARK (0x200F)
    0x2010: '-', #HYPHEN (0x2010)
    0x2011: '-', #NON-BREAKING HYPHEN (0x2011)
    0x2012: '-', #FIGURE DASH (0x2012)
    0x2013: '-', #EN DASH (0x2013)
    0x2014: '-', #EM DASH (0x2014)
    0x2015: '-', #HORIZONTAL BAR (0x2015)
    0x2016: '||', #DOUBLE VERTICAL LINE (0x2016)
    0x2017: '--', #DOUBLE LOW LINE (0x2017)
    0x2018: "'", #LEFT SINGLE QUOTATION MARK (0x2018)
    0x2019: "'", #RIGHT SINGLE QUOTATION MARK (0x2019)
    0x201A: "'", #SINGLE LOW-9 QUOTATION MARK (0x201A)
    0x201B: "'", #SINGLE HIGH-REVERSED-9 QUOTATION MARK (0x201B)
    0x201C: '"', #LEFT DOUBLE QUOTATION MARK (0x201C)
    0x201D: '"', #RIGHT DOUBLE QUOTATION MARK (0x201D)
    0x201E: '"', #DOUBLE LOW-9 QUOTATION MARK (0x201E)
    0x201F: '"', #DOUBLE HIGH-REVERSED-9 QUOTATION MARK (0x201F)
    0x2020: '(d)', #DAGGER (0x2020)
    0x2021: '(dd)', #DOUBLE DAGGER (0x2021)
    0x2022: '(.)', #BULLET (0x2022)
    0x2023: '(.)', #TRIANGULAR BULLET (0x2023)
    0x2024: '.', #ONE DOT LEADER (0x2024)
    0x2025: '..', #TWO DOT LEADER (0x2025)
    0x2026: '...', #HORIZONTAL ELLIPSIS (0x2026)
    0x2027: '', #HYPHENATION POINT (0x2027)
    0x2028: ' ', #LINE SEPARATOR (0x2028)
    0x2029: ' ', #PARAGRAPH SEPARATOR (0x2029)
    0x202A: ' ', #LEFT-TO-RIGHT EMBEDDING (0x202A)
    0x202B: ' ', #RIGHT-TO-LEFT EMBEDDING (0x202B)
    0x202C: ' ', #POP DIRECTIONAL FORMATTING (0x202C)
    0x202D: ' ', #LEFT-TO-RIGHT OVERRIDE (0x202D)
    0x202E: ' ', #RIGHT-TO-LEFT OVERRIDE (0x202E)
    0x202F: ' ', #NARROW NO-BREAK SPACE (0x202F)
    0x2030: '%%', #PER MILLE SIGN (0x2030)
    0x2031: '%%%', #PER TEN THOUSAND SIGN (0x2031)
    0x2032: "'", #PRIME (0x2032)
    0x2033: "''", #DOUBLE PRIME (0x2033)
    0x2034: "'''", #TRIPLE PRIME (0x2034)
    0x2035: "'", #REVERSED PRIME (0x2035)
    0x2036: "''", #REVERSED DOUBLE PRIME (0x2036)
    0x2037: "'''", #REVERSED TRIPLE PRIME (0x2037)
    0x2038: '', #CARET (0x2038)
    0x2039: '<', #SINGLE LEFT-POINTING ANGLE QUOTATION MARK (0x2039)
    0x203A: '>', #SINGLE RIGHT-POINTING ANGLE QUOTATION MARK (0x203A)
    0x203B: '(r)', #REFERENCE MARK (0x203B)
    0x203C: '!!', #DOUBLE EXCLAMATION MARK (0x203C)
    0x203D: '!?', #INTERROBANG (0x203D)
    0x203E: '', #OVERLINE (0x203E)
    0x203F: '', #UNDERTIE (0x203F)
    0x2040: '', #CHARACTER TIE (0x2040)
    0x2041: '', #CARET INSERTION POINT (0x2041)
    0x2042: '*', #ASTERISM (0x2042)
    0x2043: '-', #HYPHEN BULLET (0x2043)
    0x2044: '/', #FRACTION SLASH (0x2044)
    0x2045: '[', #LEFT SQUARE BRACKET WITH QUILL (0x2045)
    0x2046: ']', #RIGHT SQUARE BRACKET WITH QUILL (0x2046)
    0x2047: '??', #DOUBLE QUESTION MARK (0x2047)
    0x2048: '?!', #QUESTION EXCLAMATION MARK (0x2048)
    0x2049: '!?', #EXCLAMATION QUESTION MARK (0x2049)
    0x204A: '(t)', #TIRONIAN SIGN ET (0x204A)
    0x204B: '(P)', #REVERSED PILCROW SIGN (0x204B)
    0x204C: '', #BLACK LEFTWARDS BULLET (0x204C)
    0x204D: '', #BLACK RIGHTWARDS BULLET (0x204D)
    0x204E: '*', #LOW ASTERISK (0x204E)
    0x204F: ';', #REVERSED SEMICOLON (0x204F)
    0x2050: '', #CLOSE UP (0x2050)
    0x2051: '**', #TWO ASTERISKS ALIGNED VERTICALLY (0x2051)
    0x2052: '-', #COMMERCIAL MINUS SIGN (0x2052)
    0x2053: '-', #SWUNG DASH (0x2053)
    0x2054: '', #INVERTED UNDERTIE (0x2054)
    0x2055: '', #FLOWER PUNCTUATION MARK (0x2055)
    0x2056: '...', #THREE DOT PUNCTUATION (0x2056)
    0x2057: "''''", #QUADRUPLE PRIME (0x2057)
    0x2058: '....', #FOUR DOT PUNCTUATION (0x2058)
    0x2059: '.....', #FIVE DOT PUNCTUATION (0x2059)
    0x205A: '..', #TWO DOT PUNCTUATION (0x205A)
    0x205B: '....', #FOUR DOT MARK (0x205B)
    0x205C: '', #DOTTED CROSS (0x205C)
    0x205D: ':', #TRICOLON (0x205D)
    0x205E: ':', #VERTICAL FOUR DOTS (0x205E)
    0x205F: ' ', #MEDIUM MATHEMATICAL SPACE (0x205F)
    0x2060: ' ', #WORD JOINER (0x2060)
    0x2061: '(f)', #FUNCTION APPLICATION (0x2061)
    0x2062: ' ', #INVISIBLE TIMES (0x2062)
    0x2063: ' ', #INVISIBLE SEPARATOR (0x2063)
    0x2064: ' ', #INVISIBLE PLUS (0x2064)
    0x2066: '', #LEFT-TO-RIGHT ISOLATE (0x2066)
    0x2067: '', #RIGHT-TO-LEFT ISOLATE (0x2067)
    0x2068: '', #FIRST STRONG ISOLATE (0x2068)
    0x2069: '', #POP DIRECTIONAL ISOLATE (0x2069)
    0x206A: '', #INHIBIT SYMMETRIC SWAPPING (0x206A)
    0x206B: '', #ACTIVATE SYMMETRIC SWAPPING (0x206B)
    0x206C: '', #INHIBIT ARABIC FORM SHAPING (0x206C)
    0x206D: '', #ACTIVATE ARABIC FORM SHAPING (0x206D)
    0x206E: '', #NATIONAL DIGIT SHAPES (0x206E)
    0x206F: '', #NOMINAL DIGIT SHAPES (0x206F)
}

# Greek is getting lost
# UnicodeData.txt does not contain normalization of Greek letters.
mapping_greek = {
912: 'i', 913: 'A', 914: 'B', 915: 'G', 916: 'D', 917: 'E', 918: 'Z',
919: 'I', 920: 'TH', 921: 'I', 922: 'K', 923: 'L', 924: 'M', 925: 'N',
926: 'KS', 927: 'O', 928: 'P', 929: 'R', 931: 'S', 932: 'T', 933: 'Y',
934: 'F', 936: 'PS', 937: 'O', 938: 'I', 939: 'Y', 940: 'a', 941: 'e',
943: 'i', 944: 'y', 945: 'a', 946: 'b', 947: 'g', 948: 'd', 949: 'e',
950: 'z', 951: 'i', 952: 'th', 953: 'i', 954: 'k', 955: 'l', 956: 'm',
957: 'n', 958: 'ks', 959: 'o', 960: 'p', 961: 'r', 962: 's', 963: 's',
964: 't', 965: 'y', 966: 'f', 968: 'ps', 969: 'o', 970: 'i', 971: 'y',
972: 'o', 973: 'y' }

# This may be specific to German...
#mapping_two_chars = {
#140 : 'O', 156: 'o', 196: 'A', 246: 'o', 252: 'u', 214: 'O',
#228 : 'a', 220: 'U', 223: 's', 230: 'e', 198: 'E' }

# mapping_latin_chars = {
# 192 : 'A', 193 : 'A', 194 : 'A', 195 : 'a', 197 : 'A', 199 : 'C', 200 : 'E',
# 201 : 'E', 202 : 'E', 203 : 'E', 204 : 'I', 205 : 'I', 206 : 'I', 207 : 'I',
# 208 : 'D', 209 : 'N', 210 : 'O', 211 : 'O', 212 : 'O', 213 : 'O', 215 : 'x',
# 216 : 'O', 217 : 'U', 218 : 'U', 219 : 'U', 221 : 'Y', 224 : 'a', 225 : 'a',
# 226 : 'a', 227 : 'a', 229 : 'a', 231 : 'c', 232 : 'e', 233 : 'e', 234 : 'e',
# 235 : 'e', 236 : 'i', 237 : 'i', 238 : 'i', 239 : 'i', 240 : 'd', 241 : 'n',
# 242 : 'o', 243 : 'o', 244 : 'o', 245 : 'o', 248 : 'o', 249 : 'u', 250 : 'u',
# 251 : 'u', 253 : 'y', 255 : 'y' }

# Feel free to add new user-defined mapping. Don't forget to update mapping dict
# with your dict.

mapping = {}
mapping.update(mapping_win)
mapping.update(mapping_greek)
mapping.update(mapping_punct)
#mapping.update(mapping_two_chars)
#mapping.update(mapping_latin_chars)

# On OpenBSD string.whitespace has a non-standard implementation
# See http://plone.org/collector/4704 for details
whitespace = ''.join([c for c in string.whitespace if ord(c) < 128])
allowed = string.ascii_letters + string.digits + string.punctuation + whitespace

def normalizeLetter(ch, ishuman, enc):
    global allowed
    if ishuman and (ch in allowed):
        # ASCII chars, digits etc. stay untouched
        return ch

    try:
        ch.encode(enc, 'strict')
        return ch
    except UnicodeEncodeError:
        ordinal = ord(ch)
        if mapping.has_key(ordinal):
            # try to apply custom mappings
            return mapping.get(ordinal)

        if decomposition(ch) or len(normalize('NFKD',ch)) > 1:
            normalized = filter(lambda i: not combining(i), 
                                normalize('NFKD', ch)).strip()
            # normalized string may contain non-letter chars too. Remove them
            # normalized string may result to  more than one char
            return ''.join([c for c in normalized if c in allowed])

        # hex string instead of unknown char
        return "0x%x" % ordinal

def normalizeUnicode(text, encoding='humanascii'):
    """
    This method is used for normalization of unicode characters to the base ASCII
    letters. Output is ASCII encoded string (or char) with only ASCII letters,
    digits, punctuation and whitespace characters. Case is preserved.
    """
    ishuman = encoding == 'humanascii'
    if isinstance(text, unicode):
        unicodeinput = True
    else:
        unicodeinput = False
        text = unicode(text, 'utf-8')

    if ishuman: enc = 'ascii'
    else: enc = encoding

    res = ''
    for ch in text:
        res += normalizeLetter(ch, ishuman, enc)

    if not unicodeinput: res = res.encode('utf-8')
    return res

OPFTEMPLATEHEAD1 = """<?xml version="1.0"?><!DOCTYPE package SYSTEM "oeb1.ent">

<!-- the command line instruction 'prcgen dictionary.opf' will produce the dictionary.prc file in the same folder-->
<!-- the command line instruction 'mobigen dictionary.opf' will produce the dictionary.mobi file in the same folder-->

<package unique-identifier="uid" xmlns:dc="Dublin Core">

<metadata>
	<dc-metadata>
		<dc:Identifier id="uid">%s</dc:Identifier>
		<!-- Title of the document -->
		<dc:Title><h2>%s</h2></dc:Title>
		<dc:Language>EN</dc:Language>
	</dc-metadata>
	<x-metadata>
"""
OPFTEMPLATEHEADNOUTF = """		<output encoding="Windows-1252" flatten-dynamic-dir="yes"/>"""
OPFTEMPLATEHEAD2 = """
		<DictionaryInLanguage>%s</DictionaryInLanguage>
		<DictionaryOutLanguage>%s</DictionaryOutLanguage>
	</x-metadata>
</metadata>

<!-- list of all the files needed to produce the .prc file -->
<manifest>
"""

OPFTEMPLATELINE = """ <item id="dictionary%d" href="%s%d.html" media-type="text/x-oeb1-document"/>
"""

OPFTEMPLATEMIDDLE = """</manifest>


<!-- list of the html files in the correct order  -->
<spine>
"""

OPFTEMPLATELINEREF = """	<itemref idref="dictionary%d"/>
"""

OPFTEMPLATEEND = """</spine>

<tours/>
<guide> <reference type="search" title="Dictionary Search" onclick= "index_search()"/> </guide>
</package>
"""

################################################################
# MAIN
################################################################

def parseargs():
    if len(sys.argv) < 1:
        print "tab2opf (Stardict->MobiPocket)"
        print "------------------------------"
        print "Version: %s" % VERSION
        print "Copyright (C) 2007 - Klokan Petr Pridal"
        print
        print "Usage: python tab2opf.py [-utf] DICTIONARY.tab"
        print
        print "ERROR: You have to specify a .tab file"
        sys.exit(1)

    parser = argparse.ArgumentParser("tab2opf")
    parser.add_argument("-v", "--verbose", help="make verbose", 
                        action="store_true")
    parser.add_argument("-u", "--utf", help="input is utf8", 
                        action="store_true")
    parser.add_argument("-g", "--getkey", help="Import getkey")
    parser.add_argument("-d", "--getdef", help="Import getdef")
    parser.add_argument("-m", "--mapping", help="Import added mapping")
    parser.add_argument("-s", "--source", default="en", help="Source language")
    parser.add_argument("-t", "--target", default="en", help="Target language")
    parser.add_argument("file", help="tab file to input")    
    return parser.parse_args()

def importgetkey():
    global GETKEY
    global getkey

    if GETKEY is None:
        def getkey(key): return key
        return

    mod = importlib.import_module(GETKEY)
    print "Loading getkey from: {}".format(mod.__file__)
    getkey = mod.getkey

def importgetdef():
    global GETDEF
    global getdef

    if GETDEF is None:
        def getdef(dfn): return dfn
        return

    mod = importlib.import_module(GETDEF)
    print "Loading getdef from: {}".format(mod.__file__)
    getdef = mod.getdef

def importmapping():
    global MAPPING
    global mapping

    if MAPPING is None:
        return

    mod = importlib.import_module(MAPPING)
    print "Loading mapping from: {}".format(mod.__file__)
    mapping.update(mod.mapping)

args = parseargs()
UTFINDEX = args.utf
VERBOSE = args.verbose
FILENAME = args.file
GETKEY = args.getkey
GETDEF = args.getdef
MAPPING = args.mapping
INLANG = args.source
OUTLANG = args.target
importgetkey()
importgetdef()
importmapping()

def readkey(r, defs):
    term, defn =  r.split('\t',1)
    if not UTFINDEX:
        term = normalizeUnicode(term,'cp1252')
        defn = normalizeUnicode(defn,'cp1252')

    term = term.strip()
    nkey = normalizeUnicode(term).\
        replace('"', "'").\
        replace('<', '\\<').\
        replace('>', '\\>').\
        lower().strip()
    defn = defn.replace("\\\\","\\").\
        replace(">", "\\>").\
        replace("<", "\\<").\
        replace("\\n","<br/>\n")

    key = getkey(nkey).strip()
    if key == '':
        raise Exception("Missing key {}".format(term))
    defn = getdef(defn).strip()
    if defn == '':
        raise Exception("Missing definition {}".format(term))
    
    if VERBOSE: print key, ":", term

    ndef = [term, defn, nkey]
    if key not in defs:
        defs[key] = [ndef]
    else:
        defs[key].append(ndef)

def readkeys():
    if VERBOSE: print "Reading {}".format(FILENAME)
    with open(FILENAME,'rb') as fr:
        defns = {}
        for r in ifilter(lambda l: len(l.strip()) != 0, 
                         fr.xreadlines()):
            readkey(r, defns)
        return defns

@contextmanager
def writekeyfile(name, i):
    fname = "%s%d.html" % (name, i)
    if VERBOSE: print "Key file: {}".format(fname)
    with open(fname, 'w') as to:
        to.write("""<?xml version="1.0" encoding="utf-8"?>
<html xmlns:idx="www.mobipocket.com" xmlns:mbp="www.mobipocket.com" xmlns:xlink="http://www.w3.org/1999/xlink">
  <body>
    <mbp:pagebreak/>
    <mbp:frameset>
      <mbp:slave-frame display="bottom" device="all" breadth="auto" leftmargin="0" rightmargin="0" bottommargin="0" topmargin="0">
        <div align="center" bgcolor="yellow"/>
        <a onclick="index_search()">Dictionary Search</a>
        </div>
      </mbp:slave-frame>
      <mbp:pagebreak/>
""")
        try: yield to
        finally:
            to.write("""
    </mbp:frameset>
  </body>
</html>
        """)

# key -> terms, defns
def writekey(to, key, defn):
    def keyf(defn):
        term = defn[0]
        if key == defn[2]: return [0, term]
        return [len(term), term]

    terms = iter(sorted(defn, key=keyf))
    bterm, bdefn, _ = next(terms)
    
    for nterm, ndefn, _ in terms:
        bdefn += "; "
        if nterm != bterm:
            bdefn += "{}: ".format(nterm)
        bdefn += ndefn

    to.write("""      <idx:entry name="word" scriptable="yes">
        <h2>
          <idx:orth>%s</idx:orth><idx:key key="%s">
        </h2>
        %s
      </idx:entry>
      <mbp:pagebreak/>
""" % (bterm, key, bdefn))
    
    if VERBOSE: print key

def writekeys(defns, name):
    keyit = iter(sorted(defns))
    for j in count():
        with writekeyfile(name, j) as to:
            keys = list(islice(keyit, 10000))
            if len(keys) == 0: break
            for key in keys:
                writekey(to, key, defns[key])
    return j+1

def writeopf(ndicts, name):
    fname = "%s.opf" % name
    if VERBOSE: print "Opf: {}".format(fname)
    with open(fname, 'w') as to:
        to.write(OPFTEMPLATEHEAD1 % (name, name))
        if not UTFINDEX: to.write(OPFTEMPLATEHEADNOUTF)

        to.write(OPFTEMPLATEHEAD2 % (INLANG, OUTLANG))
        for i in range(ndicts):
            to.write(OPFTEMPLATELINE % (i, name, i))

        to.write(OPFTEMPLATEMIDDLE)
        for i in range(ndicts):
            to.write(OPFTEMPLATELINEREF % i)
        to.write(OPFTEMPLATEEND)


print "Reading keys"
defns = readkeys()
name = os.path.splitext(os.path.basename(FILENAME))[0]
print "Writing keys"
ndicts = writekeys(defns, name)
print "Writing opf"
writeopf(ndicts, name)
