# -*- encoding: utf-8 -*-
from __future__ import division
import re
import sys

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
    persist,
    smooth
)


BASE_CONFIG = {
    'corpus': '',
    'out': '',
    'tmp': '',
    'maxk': 'auto',
    'maxf': 'auto',
    'minf': 'auto',
    'flush': (1, 200000),
    'ngrams': 5,
    'ndocs': None,
    'silent': False,
    'smooth': None
}

HELP = 'No help available yet.'



class ArgumentMapper:

    def __init__(self, args):
        self.args = args
        self.names = {
            '-i': 'corpus',
            '-o': 'out',
            '-t': 'tmp',
            '--maxk': 'maxk',
            '--flush': 'flush',
            '--silent': 'silent',
            '-n': 'ngrams',
            '--ndocs': 'ndocs',
            '--maxf': 'maxf',
            '--minf': 'minf',
            '--smooth': 'smooth'
        }
        self.parsers = {
            '-i': None,
            '-o': None,
            '-t': None,
            '--maxk': self.integer,
            '--flush': self.flush,
            '-n': self.integer,
            '--ndocs': self.integer,
            '--maxf': self.floatint,
            '--minf': self.integer,
            '--smooth': self.autofloat
        }
        return
    
    def is_flag(self, flag):
        if flag in self.names.keys():
            return True
        else:
            return False

    def integer(self, arg):
        return int(arg)

    def floatint(self, arg):
        if len(arg.split('.')) > 1:
            return float(arg)
        else:
            return int(arg)

    def autofloat(self, arg):
        if arg == 'auto':
            return None
        else:
            return float(arg)

    def flush(self, arg):
        x, over = arg.split(':')
        return (int(x), int(over))
    
    def make_paths(self, args):
        corpus = args['corpus']
        if not args['out']:
            args['out'] = '%s.textnorm.out.txt' % corpus
        if not args['tmp']:
            args['tmp'] = '/tmp/textnorm.main.temp'

    def parseargs(self):
        # -i            corpus
        # -o            out, default out wrt corpus
        # -t            tmp, default tmp wrt corpus
        # --maxk        (max_k, max_f, min_f) or 'auto'
        # --flush       flushing ratio, default (1, 200000)
        # --silent      silent, default verbose
        # -n            ngrams, default 10
        # --ndocs       ndocs, default None
        args = BASE_CONFIG
        for i, flag in enumerate(self.args):
            if self.is_flag(flag):
                argname = self.names[flag]
                if argname == 'silent':
                    args[argname] = True
                    continue
                parser = self.parsers[flag]
                if not parser:
                    args[argname] = self.args[i + 1]
                else:
                    args[argname] = parser(self.args[i + 1])
        if not args['corpus']:
            exit(HELP)
        self.make_paths(args)
        return args


if __name__ == '__main__':

    args = ArgumentMapper(sys.argv).parseargs()

    CORPUS = args['corpus']
    OUT = args['out']
    TMP = args['tmp']
    N_GRAMS = args['ngrams']
    MAX_K = args['maxk']
    MAX_F = args['maxf']
    MIN_F = args['minf']
    FLUSHING_RATIO = args['flush']
    N_DOCS = args['ndocs']
    CONFIDENCE = args['smooth']
    SILENT = args['silent']
#     N_GRAMS = 5                        # generic parameter
#     MAX_K = 200                        # generic parameter
#     MAX_F = 0.3                        # generic parameter
#     MIN_F = 5                            # generic parameter
#     FLUSHING_RATIO = (1, 200000)        # generic parameter
#     N_DOCS = 1000000                    # generic parameter

    curr = N_GRAMS
    WORK = CORPUS
    preprocessor = Preprocessor()

    print 'Starting preprocessing...'
    unigram_f, freqBand = unigram_frequencies(
        preprocessor, WORK, MAX_F, N_DOCS
    )

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
    print 'Applying linguistic smoothing around high frequency tokens...'
    smooth(OUT, TMP, CONFIDENCE)
    print 'Done!\nCleaning up...'
    clean_up(TMP)
    print 'Done!\nComplete.'
