#	-*- encoding: utf-8 -*-
from __future__ import division
import re
from collections import defaultdict
from collections import Counter

from lib import (
    Streamer,
    Preprocessor,
    Parser,
    restore,
    apply,
    unigram_frequencies,
    clean_up,
    persist
)



if __name__ == '__main__':
    
    CORPUS = '/Users/jordi/Laboratorio/corpora/raw/blog2008.txt'
#     CORPUS = '/Users/jordi/Laboratorio/corpora/raw/Kaggle Billion word imputation corpus/train_v2.txt'

    CORPUS = '/Users/jordi/Laboratorio/WebInterpret/data/UK.ES.txt'
#     CORPUS = './kaggle.tail.3000000.txt'
#     CORPUS = './test.txt'
    OUT = 'out.oct.2.txt'
    TMP = 'work.oct.2.temp.dat'

#     CORPUS = '/Users/jordi/Laboratorio/Python/bin/webtext_downloader/meneame.corpus.es.txt'
#     OUT = 'out.meneame.2.txt'
#     TMP = 'work.meneame.2.temp.dat'
    N_GRAMS = 5
#     MAX_K = 200
#     MAX_F = 0.3
#     MIN_F = 5
    MAX_K = 'auto'
    MAX_F = 'auto'
    MIN_F = 'auto'
    FLUSHING_RATIO = (1, 200000)
    N_DOCS = 1000000

    curr = N_GRAMS
    WORK = CORPUS
    preprocessor = Preprocessor()

    
    print 'Starting preprocessing...'
    unigram_f, freqBand = unigram_frequencies(preprocessor,
                                              WORK, MAX_K,
                                              MAX_F, N_DOCS)

#     print freqBand.min_f()
#     print freqBand.max_f()
#     print freqBand.max_k()
#     exit()
    while curr > 1:

        print 'ngrams of n=%d\nngrams of n=%d: parsing...\nngrams of n=%d: starting parser...' % (curr, curr, curr)
        parser = Parser(curr, MIN_F, unigram_f, freqBand)
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
    print 'Done!\nCleaning up...'
    clean_up(TMP)
    print 'Done!\nComplete.'
