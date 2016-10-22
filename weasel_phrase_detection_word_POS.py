import os
from collections import defaultdict
from itertools import *
import numpy as np


word_pos_BIO_count = {} # Dict in the format {(word, key):[B, I, O]}
EmissionProbability = {}
BIO_count = {'B':0, 'I':0, 'O':0}
InitialState = np.array([0,0,0])
InitialStateByWord = {}
bigram = np.zeros((3, 3))
TransitionProbability = np.zeros((3, 3))


def preprocessFile():
	f = open("aggregated_training.txt", 'r+')
	w = relabelFile(f)
	calculateCount()
	smoothed_word_pos_BIO_Count = word_pos_BIO_count
	calculateInitialState(smoothed_word_pos_BIO_Count)
	calculateEmissionProbability(smoothed_word_pos_BIO_Count)
	calculateTransitionProbability()


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
	    if (word,pos) not in word_pos_BIO_count:
	      	word_pos_BIO_count[(word,pos)] = np.array([0,0,0])
	    addBIOCount(word_pos_BIO_count[(word,pos)],cue)  	
	f.close()


def addBIOCount(obj, varName):
	if varName == 'B':
		obj[0] += 1
	elif varName == 'I':
		obj[1] += 1
	else:
		obj[2] += 1


def buildBigramModel():
	global bigram
	f = open("relabeled_aggregated_training.txt",'r+')
	prep = None
	cur = None
	for line in f:
		word, pos, cue = line.strip().split('\t')
		cur = cue
		if prep is None:
			prep = cur
		else:
			if prep == 'B':
				addBIOCount(bigram[0],cur)
			elif prep == 'I':
				addBIOCount(bigram[1],cur)
			else:
				addBIOCount(bigram[2],cur)
			prep = cur
	f.close()


def calculateInitialState(smoothedCount):
	global InitialState
	global InitialStateByWord
	global BIO_count
	BIO_count = np.array([0,0,0])
	for (k,v) in smoothedCount.items():
		BIO_count += smoothedCount[k]
		InitialStateByWord[k] = v / sum(v)
	
	InitialState = BIO_count / sum(BIO_count)


def calculateEmissionProbability(smoothedCount):
	global EmissionProbability	
	global BIO_count
	#print "smoooooth", smoothedCount.items()
	for (k,v) in  smoothedCount.items():
		#print "k", k
		#print "v", v
		EmissionProbability[k] = v / BIO_count

	#print 'EP', EmissionProbability


def calculateTransitionProbability():
	global bigram
	global TransitionProbability 
	buildBigramModel()
	for i in range(0,3):
		for j in range(0,3):
			TransitionProbability[i][j] = bigram[i][j] / sum(bigram[i])

		
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


def getTestFiles(path, folder_type):
    "Param folder_type: 'private' or 'public'"
    subpath = path + '\\test-' + folder_type
    files = os.listdir(subpath)
    return files, subpath 


def label(path):
	private_labels = labelTestFiles(path, 'private')
	public_labels = labelTestFiles(path, 'public')
	print public_labels
	# w = open("phrase_labelling_submission.csv",'w+')
	# w.write('Type,Spans\n')
	# w.write('CUE-public,')
	# writeToSubmissionFile(w,public_labels)
	# w.write('\n')
	# w.write('CUE-private,')
	# writeToSubmissionFile(w,private_labels)
	# w.write('\n')
	# w.close()


def writeToSubmissionFile(w, labels):
	last = None
	for i, BIO in enumerate(labels):
		if BIO == 0:
			w.write('%s',i+1)
			last = 0
		elif BIO == 2 and last != 2:
			w.write('-%s ',i)
			last = 2
		elif BIO == 1:
			last = 1


def labelTestFiles(path, folder_type):
	files, subpath = getTestFiles(path, folder_type)
	labels = []
	for doc in files:
		filepath = subpath + "\\" + doc
		f = open(filepath, 'r')
		labels = labels + labelFileBySentence(f,labels)
	return labels


def labelFileBySentence(f,labels):
	sentence = []
	for line in f:
		if not isEmptyLine(line):
			word, pos = line.strip().lower().split('\t')
			sentence.append((word,pos))
    	else:
        	hmmLabeling(sentence, labels)
        	sentence = []
	return labels


def viterbi(sentence, InitialState, InitialStateByWord, TransitionProbability, 
	EmissionProbability, distribution = 'trivial'):
	"""
	distribution: trivial, uniform, normal
	trivial: [1/3, 1/3, 1/3]
	uniform: numpy.random.uniform
	normal: numpy.random.normal
	"""
	l = len(sentence)
	score = np.zeros((3,l))
	BPTR = np.zeros	((3,l))
	print InitialState
	for i in range(0,3):
		if sentence[0] in InitialStateByWord:
			score[i, 0] = InitialStateByWord[sentence[0]][i] * EmissionProbability[sentence[0]][i]
		else:
			if sentence[0] in EmissionProbability:
				score[i, 0] = InitialState[i] * EmissionProbability[sentence[0]][i]
			else:
				dist = np.zeros((1,3))
				if distribution == 'trivial':
					dist = np.array([1,1,1])
				elif distribution == 'uniform':
					dist = np.random.uniform(0.0001, 0.9999, 3)
				else:
					while sum(dist > 0) < 3:
						dist = np.random.normal(0.5, 0.5/3, 3)
				score[i, 0] = InitialState[i] * dist[i]


	for t in range(1, l):
		for i in range(0,3):
			temp = np.array([0,0,0])
			if sentence[t] in EmissionProbability:
				for j in range(0,3):
					temp[j] = score[j, t-1] * TransitionProbability[j][i] * EmissionProbability[sentence[t]][i]		
			else:
				dist = np.zeros((1,3))
				if distribution == 'trivial':
					dist = np.array([1,1,1])
				elif distribution == 'uniform':
					dist = np.random.uniform(0.0001, 0.9999, 3)
				else:
					
					while sum(dist > 0) < 3:
						dist = np.random.normal(0.5, 0.5/3, 3)
				for j in range(0,3):
					temp[j] = score[j, t-1] * TransitionProbability[j][i] * dist[i]		


			score[i,t] = max(temp)
			BPTR[i,t] = temp.argmax()	
	lastColumn = score[:,-1]
	maxScoreIndex = lastColumn.argmax()
	seq = [maxScoreIndex]


	for i in xrange(l - 2, -1, -1):
		seq = [BPTR[seq[0]][i]] + seq

	return seq 

def hmmLabeling(sentence, labels):
	seq = viterbi(sentence, InitialState, InitialStateByWord, TransitionProbability, EmissionProbability)
	labels = labels + seq

def getCurrentPath():
    path = os.getcwd()
    return path

def main():
	preprocessFile()
	path = getCurrentPath()
	# label(path)

	
if __name__ == '__main__':
    main()
