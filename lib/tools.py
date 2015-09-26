import os
import sys
import re
from collections import (
    defaultdict,
    Counter
)

from Streamer import Streamer


def unigram_frequencies(preprocessor, WORK, MAX_K, MAX_F, _n):
    freqDist = Counter()
    print 'Collecting unigram frequencies...'
    for line in Streamer(WORK, n=_n):
        freqDist.update(set(preprocessor(line).split()))
    print 'Determining frequency thresholds...'
    if isinstance(MAX_F, float):
        maxfreq = int(_n * MAX_F)
    else:
        maxfreq = MAX_F
    unigram_f = defaultdict(bool)
    freqDist = freqDist.most_common()
    for i, (w, f) in enumerate(freqDist):

        if i < MAX_K:				#	the system ignore the top k
            continue				#	most frequent words.

        if f < maxfreq:				# the system stores a True value for all
            unigram_f[w] = True		# words below the maximum frequency (these
            						# words constitute relevant, informative
            						# content.
    print 'Done!'
    print 'maxfreq=%d' % maxfreq
    print '%d words below maxfreq' % (
        len([w for w, boolean in unigram_f.items() if boolean])
    )
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
    
            
def clean_up(TMP):
    rm = 'rm %s' % TMP
    os.system(rm)
