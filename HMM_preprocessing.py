import os
from collections import defaultdict
from itertools import *
from hmm import viterbi


word_pos_BIO_count = {}
EmissionProbability = {}
InitialState = {}
Ngram = {}
TransitionProbability = defaultdict(int)


def preprocessFile(ngram):
	f = open("aggregated_training.txt", 'r+')
	w = relabelFile(f)
	calculateCount()
	smoothed_word_pos_BIO_Count = goodTuring(word_pos_BIO_count)
	emissions = calculateEmissionProbability(smoothed_word_pos_BIO_Count)
	states = calculateInitialState(smoothed_word_pos_BIO_Count)
	transitions = calculateTransitionProbability(ngram)
	observations = ['test']
	start_prob = [0.5]
	print "viter", viterbi(observations, states, start_prob, transitions, emissions)


def relabelFile(f):
	w = open("relabeled_aggregated_training.txt",'w+')
	start_word = True
	for line in f:
		if not isEmptyLine(line):
			word, pos, cue = line.strip().lower().split('\t')
			if cue == '_':
				w.write('%s\t%s\t%s\n' %(word, pos, 'O'))
				start_word = True
			elif start_word:
				w.write('%s\t%s\t%s\n' %(word, pos, 'B'))
				start_word = False
			else:
				w.write('%s\t%s\t%s\n' %(word, pos, 'I'))
	w.close()


def calculateCount():
	global word_pos_BIO_count
	f = open("relabeled_aggregated_training.txt",'r+')
	for line in f:    
	    word, pos, cue = line.strip().split('\t')
	    if (word,pos,cue) not in word_pos_BIO_count:
	      	word_pos_BIO_count[(word,pos,'B')] = 0
	      	word_pos_BIO_count[(word,pos,'I')] = 0
	      	word_pos_BIO_count[(word,pos,'O')] = 0
	      	word_pos_BIO_count[(word,pos,cue)] += 1
	    else:
	    	word_pos_BIO_count[(word,pos,cue)] += 1
	f.close()


def calculateEmissionProbability(smoothedCount):
	global EmissionProbability
	BIO_count = {'B':0, 'I':0, 'O':0}
	for (k,v) in  smoothedCount.items():
		BIO_count[k[2]] += 1

	for (k,v) in  smoothedCount.items():
		EmissionProbability[k] = v*1.0 / BIO_count[k[2]]

	return EmissionProbability.values()


def buildNgramModel(n):
	global Ngram
	f = open("relabeled_aggregated_training.txt",'r+')
	unigram = set()
	for line in f:
		word, pos, cue = line.strip().split('\t')
		unigram.add((word, pos, cue))
	f.close()
	combinations = combinations_with_replacement(unigram, n)
	Ngram = Ngram.fromkeys(combinations, 0)

	f2 = open("relabeled_aggregated_training.txt",'r+')
	prep = []
	cur = None
	for line in f2:
		word, pos, cue = line.strip().split('\t')
		cur = (word, pos, cue)
		if len(prep) == (n-1):
			Ngram[(tuple(prep) + cur)] += 1
			prep.pop(0)
			prep.append(cur)
		else:
			prep.append(cur)


def calculateTransitionProbability(ngram):
	global Ngram
	global TransitionProbability 
	buildNgramModel(ngram)
	smoothedNgram = goodTuring(Ngram)
	condition_count = {}
	for (k,v) in smoothedNgram.items():
		if k[0:ngram] in condition_count:
			condition_count[k[0:ngram]] += v
		else:
			condition_count[k[0:ngram]] = v

	for (k,v) in smoothedNgram.items():
		TransitionProbability[k] = v*1.0/condition_count[k[0:ngram]]

	return TransitionProbability.values()


def calculateInitialState(smoothedCount):
	global InitialState
	tuple_count = {}
	for (k,v) in smoothedCount.items():
		if k[0:2] in tuple_count:
			tuple_count[k[0:2]] += v
		else:
			tuple_count[k[0:2]] = v

	for (k,v) in smoothedCount.items():
		InitialState[k] = v*1.0 / tuple_count[k[0:2]]

	return InitialState.values()

		
def goodTuring(dictionary, n = 5):
	# """
	# param n: maximum Good Turing counts
	# """
    from copy import deepcopy
    d = deepcopy(dictionary)
    
    counts = [0]*(n+2)
    for i in range(0,n+2):
        for (k,v) in  dictionary.items():
        	if v == i:
    			counts[i] += 1

    for j in range(0,n+1):
    	for (k,v) in  d.items():
    		if v == i:
    			d[k] = (v+1) * 1.0 * counts[j+1]/counts[j]
	return d


def isEmptyLine(line):
    if line.strip() == '':
        return True
    else:
        return False


def main():
	preprocessFile(2)


if __name__ == '__main__':
    main()
