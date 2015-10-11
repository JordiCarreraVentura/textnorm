import math
import os
import sys
import re
from collections import (
    defaultdict as deft,
    Counter
)

from Streamer import Streamer


class FrequencyBand:
    def __init__(self, freqDist):
        self.bands = deft(set)
        for word, freq in freqDist.items():
            self.bands[freq].add(word)
        for i, band in enumerate(sorted(self.bands.keys(), reverse=True)):
            words = self.bands[band]
            if i >= band:
                self.k = i
                self.f = band
                break
        
    def max_k(self):
        return self.k
    
    def max_f(self):
        return self.f
        
    def min_f(self):
        lens = sorted([(len(words), band) for band, words in self.bands.items()])
        maxim = lens[-1][0]
        return int(round(math.log(maxim, 10)))


def unigram_frequencies(preprocessor, WORK, MAX_K, MAX_F, _n):

    freqDist = Counter()
    print 'Collecting unigram frequencies...'
    for line in Streamer(WORK, n=_n):
        freqDist.update(set(preprocessor(line).split()))

    freqBand = FrequencyBand(freqDist)

    print 'Determining frequency thresholds...'
    if isinstance(MAX_F, float):
        maxfreq = int(_n * MAX_F)
    elif isinstance(MAX_F, int):
        maxfreq = MAX_F
    else:
        maxfreq = freqBand.max_f()

    unigram_f = deft(bool)
    most_freq = freqDist.most_common()
    for i, (w, f) in enumerate(most_freq):
        #    the system ignore the top k
        #    most frequent words.
        if ((MAX_K != 'auto' and i < MAX_K) or		
            (MAX_K == 'auto' and i < freqBand.max_k())):
            continue
        if f < maxfreq:                 #    the system stores a True value for all
            unigram_f[w] = True         #    words below the maximum frequency (these
                                   	    #    words constitute relevant, informative
                                        #    content.
    print 'Done!'
    print 'maxfreq=%d' % maxfreq
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
    hyphenated = re.compile('(([^_ ]+_)*[^_ ]+_[^_ ]+)')
    newlines = []
    with open(CORPUS, 'rb') as src:
        with open(TMP, 'rb') as rd:
            for line in src:
                try:
                    rewritten = rd.next()
                except Exception:
                    break
                multiwords = [match[0] for match in hyphenated.findall(rewritten)]
                newline = apply(multiwords, line)
                newlines.append(newline)
    txt = ''.join(newlines)
    with open(OUT, 'wb') as wrt:
        wrt.write(txt)


def persist(TMP, parser):
    with open(TMP, 'wb') as wrt:
        for line in parser:
            wrt.write('%s\n' % line)
    return TMP

            
def clean_up(TMP):
    rm = 'rm %s' % TMP
    os.system(rm)
