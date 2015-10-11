#	fusionar hapax que aparezcan ~siempre juntos
#	juntar skipgrams que aparezcan ~siempre juntos
#	ir juntando órdenes menores



#	Script arguments
CORPUS = File containing the input corpus
OUT = File where the output will be stored
TMP = Temporary file for storing the postprocessed data.

 'work.temp.dat'

#	Model parameters
N = Maximum order of n-grams to be computed for multiword extraction. By the definition of multiwords, the minimum order is hard-coded to 2.

F = Minimum frequency for a multiword
Top F word n-grams most activated by their character n-grams that will be pooled for rewriting.

MAX_K = 100

MAX_F = float or int
Maximum frequency for any unigram. Unigrams with a frequency equal or higher than this number will not be considered content words and will be omitted as multiword anchors. They can still appear inside multiwords, but they will not appear at either their beginning or end.
If a float is provided (0 ≥ MAX_F ≥ 1.0), the final parameter will be calculated as the number of document lines in the input corpus times the initial floating point parameter.

N_DOCS = 5000
Maximum number of document lines to be streamed from the input file. This is useful in cases in which the input corpus is extremely large (in the current version, processing 5 million sentences requires 8GB of RAM).

UPDATE: with flushing of infrequent n-grams, the memory footprint has decreased to: 