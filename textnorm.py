# -*- encoding: utf-8 -*-
from __future__ import division
import re
import sys

from collections import defaultdict
from collections import Counter

from lib import (
    ArgumentParser,
    Streamer,
    Preprocessor,
    Parser,
    restore,
    apply,
    unigram_frequencies,
    clean_up,
    persist,
    smooth
)

if __name__ == '__main__':

    args = ArgumentParser(sys.argv).parseargs()

    CORPUS = args['corpus']
    OUT = args['out']
    TMP = args['tmp']
    N_GRAMS = args['ngrams']
    MIN_F = args['minf']
    FLUSHING_RATIO = args['flush']
    N_DOCS = args['ndocs']
    CONFIDENCE = args['smooth']
    SILENT = args['silent']

    curr = N_GRAMS
    WORK = CORPUS
    preprocessor = Preprocessor()

#     print args
#     exit()
    print 'Starting preprocessing...'
    unigram_f = unigram_frequencies(preprocessor, WORK, N_DOCS)

    while curr > 1:

        print 'ngrams of n=%d\nngrams of n=%d: parsing...\nngrams of n=%d: starting parser...' % (curr, curr, curr)
        parser = Parser(curr, MIN_F, unigram_f)
        print 'ngrams of n=%d: started!\nngrams of n=%d: parsing input from stream...' % (
            curr, curr
        )
        streamer = Streamer(WORK, n=N_DOCS)
        for line in streamer:
            if WORK == CORPUS:
                parser(preprocessor(line), flush_at=FLUSHING_RATIO)
            else:
                parser(line, flush_at=FLUSHING_RATIO)
        print 'ngrams of n=%d: finished parsing.' % curr
        print 'ngrams of n=%d: rewriting corpus with multiwords...' % curr
        parser.rewrite()

        print 'ngrams of n=%d: storing temporary snapshot of the data for feedback...' % curr
        WORK = persist(TMP, parser)
        print 'ngrams of n=%d: done!' % curr
        curr -= 1

    print 'Applying annotation on original corpus...'
    restore(CORPUS, TMP, OUT)
    print 'Applying linguistic smoothing around high frequency tokens...'
    smooth(OUT, TMP, CONFIDENCE)
    print 'Done!\nCleaning up...'
    clean_up(TMP)
    print 'Done!\nComplete.'
