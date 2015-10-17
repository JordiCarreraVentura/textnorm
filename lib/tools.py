from __future__ import division
import math
import nltk
import os
import sys
import re
from collections import (
    defaultdict as deft,
    Counter
)

from Streamer import Streamer

from nltk.corpus import stopwords

STOPWORDS = stopwords.words('english')
HYPHENATED = re.compile('(([^_ ]+_)*[^_ ]+_[^_ ]+)')
LETTERS = re.compile('[a-z_]', re.IGNORECASE)

def is_word(string):
    l = len(string)
    letters = len(LETTERS.findall(string))
    if letters / l >= 0.75:
        return True
    else:
        return False


def logdiv(n, base=4):
    if n > 1:
        return n / math.log(n, base)
    else:
        return -1


def unigram_frequencies(preprocessor, WORK, _n):

    freqDist = Counter()
    print 'Collecting unigram frequencies...'
    for line in Streamer(WORK, n=_n):
        freqDist.update(set(preprocessor(line).split()))

    unigram_f = deft(bool)
    
    for word in freqDist.keys():
        unigram_f[word] = True
        
    for word in STOPWORDS:
        unigram_f[word] = False

    return unigram_f


def apply(multiwords, line):
    HYPHEN = re.compile('_')
    BLANK = re.compile(' ')
    if not multiwords:
        return line
    newline = line
    for mw in multiwords:
        regex = re.compile('%s' % HYPHEN.sub('[^_]{1,3}', mw), re.IGNORECASE)
        onset = 0
        while True:
            match = regex.search(newline[onset:])
            if not match:
                break
            start = match.start() + onset
            end = match.end() + onset
            section = newline[start:end]
            newline = newline[:start] + BLANK.sub('_', section) + newline[end:]
            onset = end
    return newline


def restore(CORPUS, TMP, OUT):
    newlines = []
    with open(CORPUS, 'rb') as src:
        with open(TMP, 'rb') as rd:
            for line in src:
                try:
                    rewritten = rd.next()
                except Exception:
                    break
                multiwords = [match[0] for match in HYPHENATED.findall(rewritten)]
                newline = apply(multiwords, line)
                newlines.append(newline)
    txt = ''.join(newlines)
    with open(OUT, 'wb') as wrt:
        wrt.write(txt)


def decode(string):
    try:
        return string.decode('utf-8').strip('\n')
    except Exception:
        return string.strip('\n')


def persist(TMP, parser):
    with open(TMP, 'wb') as wrt:
        for line in parser:
            wrt.write('%s\n' % line)
    return TMP


def clean_up(TMP):
    rm = 'rm %s' % TMP
    os.system(rm)
