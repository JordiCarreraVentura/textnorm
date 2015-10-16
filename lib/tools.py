from __future__ import division
import math
import os
import sys
import re
from collections import (
    defaultdict as deft,
    Counter
)

from Streamer import Streamer


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


class FrequencyBand:
    def __init__(self, freqDist):
        self.bands = deft(set)
        for word, freq in freqDist.items():
            self.bands[freq].add(word)
        for i, band in enumerate(sorted(self.bands.keys(), reverse=True)):
            l = len(self.bands[band])
#             print i, band, len(self.bands[band])
          #		metric 1
#             if i >= band:
#                 self.k = i
#                 self.f = band
#                 #break
          #		metric 2
#             if len(self.bands[band]) >= band:
#                 self.k = i
#                 self.f = band
#                 break
          #		metric 3: squared frequency depth
            if l >= band:
#                 self.k = l
                self.f = i
                break
#         exit()

    def max_f(self):
        return self.f

    def min_f(self):
        lens = sorted([(len(words), band) for band, words in self.bands.items()])
        maxim = lens[-1][0]
        return int(round(math.log(maxim, 10)))

    def __str__(self):
#         max_k = self.max_k()
#         min_f = self.min_f()
#         max_f = self.max_f()
#         args = (max_k, min_f, max_f)
#         message = 'maxk=%d\nminfreq=%d\nmaxfreq=%d' % args
#         max_k = self.max_k()
        min_f = self.min_f()
        max_f = self.max_f()
        args = (min_f, max_f)
        message = 'minfreq=%d\nmaxfreq=%d' % args
        return message



def unigram_frequencies(preprocessor, WORK, MAX_F, _n):

    freqDist = Counter()
    print 'Collecting unigram frequencies...'
    ndocs = 0
    for line in Streamer(WORK, n=_n):
        freqDist.update(set(preprocessor(line).split()))
        ndocs += 1

    freqBand = FrequencyBand(freqDist)

    print 'Determining frequency thresholds...'
    if isinstance(MAX_F, float):
        maxfreq = int(ndocs * MAX_F)
    elif isinstance(MAX_F, int):
        maxfreq = MAX_F
    else:
        maxfreq = freqBand.max_f()

    unigram_f = deft(bool)
    most_freq = freqDist.most_common()
    for i, (w, f) in enumerate(most_freq):
        #    the system ignore the top k
        #    most frequent words.
        if f < maxfreq:                 #    the system stores a True value for all
            unigram_f[w] = True         #    words below the maximum frequency (these
                                   	    #    words constitute relevant, informative
                                        #    content.
    print 'Done!'
    print freqBand
    print '%d words below maxfreq' % (
        len([w for w, boolean in unigram_f.items() if boolean])
    )
    return unigram_f, freqBand


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
