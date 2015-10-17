from __future__ import division
import re

from collections import (
    defaultdict,
    Counter
)

class Parser:
    def __init__(self, n, min_f, unigram_f):
        self.n = n
        self.min_f = min_f
        self._f = Counter()
        self.epochs = defaultdict(int)
        self.space = []
        self.lines = []
        self._grams = []
        self.content = unigram_f
        self.lines_by_gram = defaultdict(set)
        self.blank = re.compile(' ')
        self.z = re.compile('Z+')

    def __call__(self, line, flush_at=None, flush_over=None):
        self.space.append(line)
        grams = self.grams(line)
        self.to_index(grams)
        self._grams.append(grams)
        self.__add(grams)
        if flush_at:
            self.__flush(flush_at)

    def __add(self, grams):
        for gram in grams:
            self._f[gram] += 1
            self.epochs[gram] = len(self.space)

    def to_index(self, grams):
        for g in grams:
            self.lines_by_gram[g].add(len(self.space) - 1)

    def grams(self, line):
        gg = []
        tokens = line.split()
        for i in range(len(tokens) - (self.n - 1)):
            g = tokens[i:i + self.n]
            left = tokens[:i]
            right = tokens[i + self.n:]
            if 'STOP' in g:
                continue
            if not (self.content[g[0]] and
                    self.content[g[-1]]):
                continue
            gg.append(' '.join(g))
        return gg

    def rewrite(self):
        found = self.best()
        for freq, gram in found:
            indexes = self.lines_by_gram[gram]
            regex = self.get_regex(gram)
            repl = self.blank.sub('_', gram)
            for position in indexes:
                received = self.space[position]
                out = regex.sub(repl, received)
                self.space[position] = out
    
    def get_regex(self, gram):
        regex = self.z.sub('[0-9]+', gram)
        return re.compile(regex)

    def __iter__(self):
        for line in self.space:
            yield line

    def best(self):
        return [
            (f, w) for w, f in self._f.most_common()
            if f >= self.min_f
        ]

    def __flush(self, flush_at):
        q, total = flush_at
        if self.space and not len(self.space) % total:
            print 'Flushing at %d' % len(self.space)
            flushed = 0
            current_epoch = len(self.space)
            for gram, epoch_created in self.epochs.items():
                epochs_since = current_epoch - epoch_created
                if epochs_since >= total:
                    expectation = epochs_since / total
                    if self._f[gram] < expectation:
                        del self._f[gram]
                        del self.lines_by_gram[gram]
                        del self.epochs[gram]
                        flushed += 1
            print 'Flushed %d n-grams' % flushed
