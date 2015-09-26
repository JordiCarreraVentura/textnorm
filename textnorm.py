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
    clean_up
)



if __name__ == '__main__':
    
#     CORPUS = '/Users/jordi/Laboratorio/corpora/raw/blog2008.txt'
    CORPUS = '/Users/jordi/Laboratorio/corpora/raw/Kaggle Billion word imputation corpus/train_v2.txt'
#     CORPUS = '/Users/jordi/Laboratorio/WebInterpret/data/UK.ES.txt'
    OUT = 'out.2b.txt'
    TMP = 'work.2b.temp.dat'
    N_GRAMS = 5
    F = 20
    MAX_K = 20
    MAX_F = 0.01
    MIN_F = 10
#     N_DOCS = 5000
    FLUSHING_RATIO = (1, 2500000)
    N_DOCS = 5000000

    curr = N_GRAMS
    WORK = CORPUS
    preprocessor = Preprocessor()

    
    print 'Starting preprocessing...'
    unigram_f = unigram_frequencies(preprocessor, WORK, MAX_K, MAX_F, N_DOCS)

    while curr > 1:

        print 'ngrams of n=%d\nngrams of n=%d: parsing...\nngrams of n=%d: starting parser...' % (curr, curr, curr)
        parser = Parser(curr, F, MIN_F, content=unigram_f)
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
        with open(TMP, 'wb') as wrt:
            for line in parser:
                wrt.write('%s\n' % line)
        WORK = TMP
        print 'ngrams of n=%d: done!' % curr
        curr -= 1
    
    print 'Applying annotation on original corpus...'
    restore(CORPUS, TMP, OUT)
    print 'Done!\nCleaning up...'
    clean_up(TMP)
    print 'Done!\nComplete.'
