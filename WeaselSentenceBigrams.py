# Returns a list (sentences) of list of tuples (word, POS), 
def readFile(file, training):
	data = open(file, "r").read().split("\n\n")

	# print(len(data))

	# print data

	masterList = []
	for ele in data:
		myList = []
		sentenceData = ele.split("\n")
		# print sentenceData
		for line in sentenceData:
			# print line
			lineData = line.split("\t")
			# print "LD: " + str(lineData)
			if((len(lineData) == 3 and training) or (len(lineData) == 2 and not training)):
				if training:
					myList.append((lineData[0], lineData[1], lineData[2]))
				else:
					myList.append((lineData[0], lineData[1]))
		masterList.append(myList)

	return masterList[:-1]

def readFiles(fileList, training):
	myList = []
	for file in fileList:
		myList.extend(readFile(file, training))
	return myList

def generateFrequencies(tokens, nBefore, nAfter):
	freqs = {}
	cueFreqs = {}

	for fileInd in range(len(tokens)):
		file = tokens[fileInd]
		# file.insert(0, ("<B>", "<B>", "_"))
		# file.append(("<E>", "<E>", "_"))
		seenCues = []

		for wordNum in range(nBefore, len(file) - nAfter):
			word = file[wordNum]
			prevWord = file[wordNum - 1]
			nGramTok = []

			for tokInd in range(wordNum - nBefore, wordNum + nAfter + 1):
				nGramWord = file[tokInd]
				nGramTok.append((nGramWord[0])) # , nGramWord[1]))

			tupTok = tuple(nGramTok)

			if(word[2] != "_" and word[2] not in seenCues):
				seenCues.append(word[2])
				if tupTok not in cueFreqs:
					cueFreqs[tupTok] = 0
				cueFreqs[tupTok] += 1

			if tupTok not in freqs:
				freqs[tupTok] = 0
			freqs[tupTok] += 1

	return (freqs, cueFreqs)

def generateProbabilities(freqs, cueFreqs):
	probabilities = {}
	for nGram in freqs:
		if nGram in cueFreqs:
			probabilities[nGram] = cueFreqs[nGram] * 1.0 / freqs[nGram] * 1.0
		# else:
		# 	probabilities[nGram] = 0
	return probabilities

def generateFileList(dir, (start, end)):
	files = []
	for i in range(start, end):
		strNum = '%04d' % i
		fileName = dir + "/doc_" + strNum + ".txt"
		files.append(fileName)
	return files

def classifySentence(sentence, probabilities, threshold, nBefore, nAfter):
	maxProb = 0
	# print probabilities
	# print sentence
	for wordNum in range(nBefore, len(sentence) - nAfter):
		word = sentence[wordNum]
		prevWord = sentence[wordNum - 1]
		nGramTok = []

		for tokInd in range(wordNum - nBefore, wordNum + nAfter + 1):
			nGramWord = sentence[tokInd]
			nGramTok.append((nGramWord[0])) #, nGramWord[1]))

		tupTok = tuple(nGramTok)

		if tupTok in probabilities:
				maxProb = max(maxProb, probabilities[tupTok])

	# print maxProb, threshold
	
	return (maxProb > threshold)

def classifyFile(file, probabilities, threshold, nBefore, nAfter):
	results = []
	for sentence in file:
		results.append(classifySentence(sentence, probabilities, threshold, nBefore, nAfter))
	return results

def validateCrossFile(file):
	results = []
	for sentence in file:
		# print sentence
		ambig = False
		for word in sentence:
			if(word[2] != "_"):
				ambig = True
		results.append(ambig)

	# print "VCF", results
	return results

def calculateFScore(predictions, golden):
	precisionCount = 0
	recallCount = 0
	precDenom = 0
	recDenom = 0
	for i in range(len(predictions)):
		if(predictions[i] and golden[i]):
			precisionCount += 1
			recallCount += 1
		if(predictions[i]):
			precDenom += 1
		if(golden[i]):
			recDenom += 1

	precision = precisionCount * 1.0 / precDenom
	recall = recallCount * 1.0 / recDenom

	f1 = 2.0 * (precision * recall) / (precision + recall)

	return f1

def outputPredictions(predictions, outFileName):
	outFile = open(outFileName, "w")

	print predictions

	s = ""

	for i in range(len(predictions)):
		if predictions[i]:
			s += str(i) + " "

	print >>outFile, s
	outFile.close()

# for nBefore in range(0, 1):
# 	for nAfter in range(0, 1):
# 		for thresTimes in range(1, 51):
# 			thres = thresTimes * 0.01

# 			tokens = readFiles(generateFileList("cross_training", (1,950)))
# 			(freqs, cueFreqs) = generateFrequencies(tokens, nBefore, nAfter)

# 			probabilities = generateProbabilities(freqs, cueFreqs)

# 			fileTokens = readFiles(generateFileList("cross_validation", (951, 1187)))[:-1]

# 			predictions = classifyFile(fileTokens, probabilities, thres, nBefore, nAfter)
# 			golden = validateCrossFile(fileTokens)

# 			print nBefore, nAfter, thres, calculateFScore(predictions, golden)

nBefore = 0
nAfter = 0
thres = 0.2

tokens = readFiles(generateFileList("train", (1,1187)), True)
(freqs, cueFreqs) = generateFrequencies(tokens, nBefore, nAfter)

probabilities = generateProbabilities(freqs, cueFreqs)

fileTokens = readFiles(generateFileList("test-private", (1, 501)), False)


predictions = classifyFile(fileTokens, probabilities, thres, nBefore, nAfter)

outputPredictions(predictions, "newOut.txt")