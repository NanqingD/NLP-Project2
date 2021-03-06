import os
from collections import defaultdict
from itertools import *
import numpy as np


word_pos_BIO_count = {} # Dict in the format {(word, key):[B, I, O]}
EmissionProbability = {}
BIO_count = {'B':0, 'I':0, 'O':0}
InitialState = np.array([0,0,0])
# InitialStateByWord = {}
bigram = np.zeros((3, 3))
TransitionProbability = np.zeros((3, 3))
total = 0


def preprocessFile():
	f = open("aggregated_training.txt", 'r+')
	w = relabelFile(f)
	calculateCount()
	global word_pos_BIO_count
	# word_pos_BIO_count = goodTuring(word_pos_BIO_count)
	word_pos_BIO_count = addOne(word_pos_BIO_count)
	calculateInitialState(word_pos_BIO_count)
	calculateEmissionProbability(word_pos_BIO_count)
	word_pos_BIO_count = None
	calculateTransitionProbability()
	tuneTransitionProbability(0.1)
	BIO_count = None


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
	# global InitialStateByWord
	global BIO_count
	BIO_count = np.array([0.0,0.0,0.0])
	for (k,v) in smoothedCount.items():
		BIO_count += smoothedCount[k]
		# InitialStateByWord[k] = v*1.0/ sum(v)
	
	InitialState = BIO_count * 1.0 / sum(BIO_count)


def calculateEmissionProbability(smoothedCount):
	global EmissionProbability	
	global BIO_count
	for (k,v) in  smoothedCount.items():
		EmissionProbability[k] = v*1.0 / BIO_count


def calculateTransitionProbability():
	global bigram
	global TransitionProbability 
	buildBigramModel()
	for i in range(0,3):
		for j in range(0,3):
			TransitionProbability[i][j] = (bigram[i][j] + 1) *1.0 / (sum(bigram[i]) + 3)


def tuneTransitionProbability(alpha):
	global TransitionProbability
	TransitionProbability[2][0] = alpha
	TransitionProbability[2][2] = 1 - alpha

		
def goodTuring(dictionary, n = 5):
	# """
	# param n: maximum Good Turing counts
	# """
    from copy import deepcopy
    d = deepcopy(dictionary)   
    counts = [0]*(n+2)
    for i in range(0,n+2):
        for (k,v) in  dictionary.items():
        	for j in range(0,3):
        		if v[j] == i:
        			counts[i] += 1
    
    for j in range(0,n+1):
    	for (k,v) in  dictionary.items():
    		for q in range(0,3):
        		if v[q] == j:
					if q == 0:
						d[k] = d[k] + np.array([(v[q] + 1) * 1.0 * counts[j+1]/counts[j],0,0])
					if q == 1:
						d[k] = d[k] + np.array([0,(v[q] + 1) * 1.0 * counts[j+1]/counts[j],0])
					if q == 2:
						d[k] = d[k] + np.array([0,0,(v[q] + 1) * 1.0 * counts[j+1]/counts[j]])
	return d


def addOne(dictionary, n = 5):
	from copy import deepcopy
	d = deepcopy(dictionary)

	for (k,v) in  dictionary.items():
		d[k] = d[k] + np.array([1,1,1])

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
	public = labelTestFiles(path, 'public')
	private = labelTestFiles(path, 'private')
	w = open("phrase_labelling_submission.csv",'w+')
	w.write('Type,Spans\n')
	w.write('CUE-public,')
	writeToSubmissionFile(w,public)
	w.write('\n')
	w.write('CUE-private,')
	writeToSubmissionFile(w,private)
	w.write('\n')
	w.close()
	# public.close()
	# private.close()


def writeToSubmissionFile(w, w2):
	# labels = []
	# for line in w2:
	# 	labels = line.split()

	# print len(labels)
	last = 2
	for i, BIO in enumerate(w2):
		if float(BIO) == 0:
			w.write('%s' %(i+1))
			last = 0
		elif float(BIO) == 2 and last != 2:
			w.write('-%s ' %(i))
			last = 2
		elif float(BIO) == 1:
			last = 1


def labelTestFiles(path, folder_type):
	files, subpath = getTestFiles(path, folder_type)
	# s = open('seq_'+ folder_type +'.txt', 'w+')
	labels = []
	for doc in files:
		filepath = subpath + "\\" + doc
		f = open(filepath, 'r')
		labelFileBySentence(labels,f)
		f.close()
		print filepath,'finished'

	print len(labels)
	return labels


def labelFileBySentence(s, f):
	global total
	sentence = []
	for line in f:
		# print line
		if not isEmptyLine(line):			
			word, pos = line.strip().lower().split('\t')
			sentence.append((word,pos))
		elif isEmptyLine(line):
			labels = hmmLabeling(sentence)
			# for label in labels:
			# 	s.write('%s ' % (label))
			s += labels
			sentence = []
	if len(sentence) > 0 :
		labels = hmmLabeling(sentence)
		# for label in labels:
		# 	s.write('%s ' % (label))
		s += labels


def viterbi(sentence, distribution = 'trivial'):
	"""
	distribution: trivial, uniform, normal
	trivial: [1/3, 1/3, 1/3]
	uniform: numpy.random.uniform
	normal: numpy.random.normal
	"""
	l = len(sentence)
	score = np.ones((3,l))
	BPTR = np.ones((3,l))
	for i in range(0,3):
		if sentence[0] in EmissionProbability:
			score[i, 0] = InitialState[i] * EmissionProbability[sentence[0]][i]
		else:
			dist = np.zeros((1,3))
			if distribution == 'trivial':
				dist = np.array([1,1,1])
			elif distribution == 'uniform':
				dist = np.random.uniform(0.0001, 0.9999, 3)
			else:
				dist = np.absolute(np.random.normal(0.5, 0.5/3, 3))
			score[i, 0] = InitialState[i] * dist[i]	

	temp = [1,1,1]
	for t in range(1, l):
		for i in range(0,3):
			
			if sentence[t] in EmissionProbability:
				for j in range(0,3):
					temp[j] = score[j, t-1] * TransitionProbability[j][i] * EmissionProbability[sentence[t]][i]	
			else:
				dist = np.ones((1,3))
				if distribution == 'trivial':
					dist = np.array([1,1,1])
				elif distribution == 'uniform':
					dist = np.random.uniform(0.0001, 0.9999, 3)
				else:
					dist = np.absolute(np.random.normal(0.5, 0.5/3, 3))
				for j in range(0,3):
					# print '2', score
					temp[j] = score[j, t-1] * TransitionProbability[j][i] * dist[i]
			score[i,t] = max(temp)
			BPTR[i,t] = temp.index(max(temp))	

	lastColumn = score[:,-1]
	maxScoreIndex = lastColumn.argmax()
	seq = [int(maxScoreIndex)]

	for i in xrange(l - 1, 0, -1):
		next = seq[-1]
		seq.append(int(BPTR[next][i]))

	return seq[::-1]


def hmmLabeling(sentence):
	seq = viterbi(sentence, 'trivial')
	return seq


def getCurrentPath():
    path = os.getcwd()
    return path


def main():
	preprocessFile()
	path = getCurrentPath()
	label(path)

	
if __name__ == '__main__':
    main()
