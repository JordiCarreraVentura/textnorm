from __future__ import division
import re
from collections import defaultdict
from collections import Counter


class Streamer:
    def __init__(self, f, n=None):
        self.source = f
        self.n = n
        self.c = 0
    
    def __iter__(self):
        with open(self.source, 'rb') as rd:
            for l in rd:
                self.c += 1
                try:
                    yield l.decode('utf-8').strip()
                except Exception:
                    yield l.strip()
                if self.c >= self.n:
                    break
                if not self.c % 100000:
                    print self.c, self.n


class Preprocessor:
    def __init__(self, using=[
        'lowercasing',
        'punctuation',
        'numerical_normalization',
        'non_alphabetical',
        'blanks'
    ]):
        self._2do = using
        self.implemented = {
            'lowercasing': self.lowercase,
            'numerical_normalization': self.num_norm,
            'punctuation': self.punct,
            'non_alphabetical': self.clean,
            'blanks': self.blanks
        }
        self.punct = re.compile('[\.,;:!\?\-\(\)]')
        self.num = re.compile('([0-9]+(.){,3})?[0-9]+')
        self.spaces = re.compile(' {2,}')
        self.junk = re.compile('[^a-z ]', re.IGNORECASE)
        self.stop = re.compile('STOP')
        self.z = re.compile('Z')
    
    def __call__(self, line):
        line = self.stop.sub('.', line)
        line = self.z.sub('1', line)
        for method in self._2do:
            funct = self.implemented[method]
            line = funct(line)
        return line
    
    def lowercase(self, line):
        return line.lower()
    
    def num_norm(self, line):
        return self.num.sub('Z', line)
    
    def punct(self, line):
        return self.punct.sub(' STOP ', line)
    
    def blanks(self, line):
        return self.spaces.sub(' ', line)
    
    def clean(self, line):
        return self.junk.sub(' ', line)
        
        


class Parser:
    def __init__(self, n, f, content=defaultdict(bool)):
        self.n = n
        self.f = f
        self._f = Counter()
        self._unif = unigram_f
        self.space = []
        self.lines = []
        self._grams = []
        self.content = unigram_f
        self.lines_by_gram = defaultdict(set)
        self.blank = re.compile(' ')
    
    def __call__(self, line):
        self.space.append(line)
        grams = self.grams(line)
        self.to_index(grams)
        self._grams.append(grams)
        self._f.update(grams)
    
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
        


def unigram_frequencies(preprocessor, WORK, MAX_K, MAX_F, _n):
    dump = []
    for line in Streamer(WORK, n=_n):
        dump += list(set(preprocessor(line).split()))
    if isinstance(MAX_F, float):
        maxfreq = int(_n * MAX_F)
    else:
        maxfreq = MAX_F
    unigram_f = defaultdict(bool)
    freqDist = Counter(dump).most_common()
    for i, (w, f) in enumerate(freqDist):
        if i < MAX_K:
            continue
        if f < maxfreq:
            unigram_f[w] = True
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
    
            


if __name__ == '__main__':
    
    CORPUS = '/Users/jordi/Laboratorio/corpora/raw/blog2008.txt'
    CORPUS = '/Users/jordi/Laboratorio/corpora/raw/Kaggle Billion word imputation corpus/train_v2.txt'
    OUT = 'out.txt'
    TMP = 'work.temp.dat'
    N_GRAMS = 10
    F = 10
    MAX_K = 100
    MAX_F = 0.1
    N_DOCS = 200000
    
    curr = N_GRAMS
    WORK = CORPUS
    preprocessor = Preprocessor()

    unigram_f = unigram_frequencies(preprocessor, WORK, MAX_K, MAX_F, N_DOCS)

    while curr > 1:
        
        print '\n', curr
        parser = Parser(curr, F, content=unigram_f)
        for line in Streamer(WORK, n=N_DOCS):
            if WORK == CORPUS:
                parser(preprocessor(line))
            else:
                parser(line)
        parser.rewrite()

        with open(TMP, 'wb') as wrt:
            for line in parser:
                wrt.write('%s\n' % line)
        WORK = TMP
        curr -= 1
    
    restore(CORPUS, TMP, OUT)
