from __future__ import division
import re

from collections import (
    defaultdict,
    Counter
)

class Parser:
    def __init__(self, n, f, min_f, content=defaultdict(bool)):
        self.n = n
        self.f = f
        self.min_f = min_f
        self._f = Counter()
        self.space = []
        self.lines = []
        self._grams = []
        self.content = content
        self.lines_by_gram = defaultdict(set)
        self.blank = re.compile(' ')
    
    def __call__(self, line, flush_at=None, flush_over=None):
        self.space.append(line)
        grams = self.grams(line)
        self.to_index(grams)
        self._grams.append(grams)
        self._f.update(grams)
        if flush_at:
            self.__flush(flush_at)
    
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
#             parts = self.revert(g)
#             if not (self.content[parts[0]] and
#                     self.content[parts[-1]]):
#                 continue
            gg.append(' '.join(g))
        return gg
    
#     def revert(self, g):
#         _g = []
#         for part in g:
#             _g += part.split('_')
#         return _g
    
    def rewrite(self):
        found = self.best()
        for freq, gram in found:
            if freq < self.min_f:
                continue
            indexes = self.lines_by_gram[gram]
            regex, repl = re.compile(gram), self.blank.sub('_', gram)
            for position in indexes:
                received = self.space[position]
                out = regex.sub(repl, received)
                self.space[position] = out
    
    def __iter__(self):
        for line in self.space:
            yield line
    
    def best(self):
        return [
            (f, w) for w, f in self._f.most_common()
            if f >= self.f
        ]
    
    def __flush(self, flush_at):
        q, total = flush_at
        if self.space and not len(self.space) % total:
            print 'Flushing at %d' % len(self.space)
            flushed = 0
            ratio = len(self.space) / total
            threshold = q * ratio
            print len(self.space), total, q, ratio, threshold
            for gram, freq in self._f.items():
                if freq < threshold:
                    flushed += 1
                    del self._f[gram]
                    del self.lines_by_gram[gram]
            print 'Flushed %d n-grams' % flushed
