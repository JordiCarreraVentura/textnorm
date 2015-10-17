from __future__ import division
import nltk
import math
import os
import re
# import time

from nltk import wordpunct_tokenize as tokenize

from tools import (
    is_word,
    logdiv,
    decode,
    HYPHENATED
)

from collections import (
    defaultdict as deft,
    Counter
)


class Smoothing:
    
    def __init__(self, OUT, TMP, CONFIDENCE):
        self.src = OUT
        self.temp = '%s.smoothing.temp' % '.'.join(TMP.split('.')[:-2])
        self.confidence = CONFIDENCE
        self.posterior = Counter()
        self.prior = Counter()
        self.i = 0
        self.minimum = 0
        self.head = dict([])
        self.grams_by_line = deft(set)
        self.smoothed = deft(bool)
        self.regexs = dict([])
    
    def __iter__(self):
        c = 0
        with open(self.src, 'rb') as stream:
            for line in stream:
                c += 1
#                 if not int(c % 1000):
#                     print c
                yield line
    
    def train(self):
        for line in self:
            self.i += 1
        self.minimum = int(round(math.log(self.i, 10)))
        i = 0
        for line in self:
            tokens = tokenize(decode(line).lower())
            targets = self.get_targets(tokens)
            for gram in targets:
                self.posterior[gram] += 1
                self.grams_by_line[i].add(gram)
                for token in gram:
                    self.prior[token] += 1
            i += 1
#         print self.prior.most_common(10)
#         print self.posterior.most_common(10)
        self.crunch()
    
    def get_threshold(self, baseline):
        if self.confidence:
            return self.confidence
        else:
            return logdiv(baseline) / baseline
    
    def crunch(self):
        for gram, freq in self.posterior.items():
            if freq < self.minimum:
                continue
            head = self.head[gram]
            baseline = self.prior[head]
            threshold = self.get_threshold(baseline)
            if freq / baseline >= threshold:
                self.smoothed[gram] = True
                self.regexs[gram] = self.regex(gram)
#                 print '+', gram, freq, ' | ', head, baseline, '|', threshold
#             else:
#                 print '-', gram, freq, ' | ', head, baseline, '|', threshold
    
    def regex(self, gram):
        r = '[^_]{1,3}'.join(['(%s)' % token for token in gram])
        return re.compile(r, re.IGNORECASE)
        
    def get_targets(self, tokens):
        targets = set([])
        for i, token in enumerate(tokens):
            target = None
            if HYPHENATED.match(token):
                if i > 0 and is_word(tokens[i - 1]):
                    if i < (len(tokens) - 1) and is_word(tokens[i + 1]):
                        target = tuple([tokens[i - 1], token, tokens[i + 1]])
                        targets.add(target)
                        self.head[target] = token
                    target = tuple([tokens[i - 1], token])
                    targets.add(target)
                    self.head[target] = token
                elif 0 < i < (len(tokens) - 1) and is_word(tokens[i + 1]):
                    target = tuple([token, tokens[i + 1]])
                    targets.add(target)
                    self.head[target] = token
        return targets

    def annotate(self):
        i = 0
        with open(self.temp, 'wb') as wrt:
            for line in self:
                triples = self.activate(i)
                annotated = self.__annotate(line, triples)
                wrt.write('%s' % annotated)
                i += 1
        self.replace()
        
    def replace(self):
        mv = 'mv %s %s' % (self.temp, self.src)
#         mv = 'cp %s .' % self.temp
        os.system(mv)
    
    def __annotate(self, line, triples):
        prev = line
        for o, gram, regex in triples:
            while True:
                o_start = 1
                o_end = len(gram) + 1
                match = regex.search(line)
                if not match:
                    break
                start = match.start()
                end = match.end()
                replacement = '_'.join([
                    match.group(n) for n in range(o_start, o_end)
                ])
                line = line[:start] + replacement + line[end:]
#         if line != prev:
#             print prev.strip()
#             print line.strip()
#             print
        return line
   
    def activate(self, i):
        grams = self.grams_by_line[i]
        kept = []
        for gram in grams:
            if self.smoothed[gram]:
                triple = (len(gram), gram, self.regexs[gram])
                kept.append(triple)
        return sorted(kept, reverse=True)



# def smooth(OUT, n=[2, 3, 4, 5]):
def smooth(OUT, TMP, CONFIDENCE):

    #    smoothing
    smoothing = Smoothing(OUT, TMP, CONFIDENCE)
    
    #    collect statistics 
    smoothing.train()
    
    #    annotate
    smoothing.annotate()
