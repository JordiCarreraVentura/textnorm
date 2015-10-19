import nltk
from nltk.corpus import PlaintextCorpusReader as reader
from nltk.corpus.util import LazyCorpusLoader
from nltk.collocations import *

ROOT = './'
PATH = 'essays.txt'

corpus = reader(ROOT, [PATH])
text = nltk.Text(corpus.words())

bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()

#	too rare; top results have a single occurrence
finder2 = BigramCollocationFinder.from_words(nltk.Text(corpus.words()))
finder3 = TrigramCollocationFinder.from_words(nltk.Text(corpus.words()))


finder2.apply_freq_filter(5)
finder3.apply_freq_filter(5)
print finder2.nbest(bigram_measures.pmi, 150)[-10:]
# print finder2.nbest(bigram_measures.pmi, 500)[-10:]
# print finder2.nbest(bigram_measures.pmi, 100000000000)[-20:]

print finder3.nbest(trigram_measures.pmi, 100000000000)[-20:]
