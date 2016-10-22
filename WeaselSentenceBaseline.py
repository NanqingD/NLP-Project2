def train():
	freqs = {}
	curFreqs = {}

	for fileNum in range(1, 950):
		seenCues = []
		# print curFreqs
		strNum = '%04d' % fileNum
		fileName = "doc_" + strNum + ".txt"
		if (fileNum % 100 == 0):
			print fileName
		file = open("cross_training/" + fileName).read().split("\n")

		for line in file:
			lineData = line.split("\t")
			if(len(lineData) > 1):
				word = (lineData[0].lower(), lineData[1])
				if(len(lineData) >= 2 and lineData[2] != "_" and (not lineData[2] in seenCues)):
					seenCues.append(lineData[2])
					if(word not in curFreqs.keys()):
						curFreqs[word] = 0
					curFreqs[word] += 1
				if(word not in freqs.keys()):
					freqs[word] = 0
				freqs[word] += 1

	return [freqs, curFreqs]

def trainBigram():
	freqs = {}
	curFreqs = {}

	for fileNum in range(1, 950):
		seenCues = []
		# print curFreqs
		strNum = '%04d' % fileNum
		fileName = "doc_" + strNum + ".txt"
		if (fileNum % 100 == 0):
			print fileName
		file = open("cross_training/" + fileName).read().split("\n")

		prevWord = ""
		for line in file:
			lineData = line.split("\t")
			if(len(lineData) > 1):
				# word = (prevWord + "_" + lineData[0].lower(), lineData[1])
				word = (prevWord + "_" + lineData[0].lower())
				if(len(lineData) >= 2 and lineData[2] != "_" and (not lineData[2] in seenCues)):
					seenCues.append(lineData[2])
					if(word not in curFreqs.keys()):
						curFreqs[word] = 0
					curFreqs[word] += 1
				if(word not in freqs.keys()):
					freqs[word] = 0
				freqs[word] += 1
				prevWord = lineData[0].lower()

	return [freqs, curFreqs]

def getProbabilities(freqs, curFreqs):
	probabilities = {}
	for word in freqs:
		freq = freqs[word]
		ambiFreq = 0
		if(word in curFreqs.keys()):
			ambiFreq = curFreqs[word]
		probabilities[word] = ambiFreq * 1.0 / freq * 1.0

	return probabilities

def getScores(probabilities):
	scores = []
	for fileNum in range(951, 1187):
		strNum = '%04d' % fileNum
		fileName = "doc_" + strNum + ".txt"
		if (fileNum % 100 == 0):
			print fileName
		file = open("cross_validation/" + fileName).read().split("\n\n")[:-1]

		for sentence in file:
			constructedSent = ""
			# print "SENT: " + sentence
			lines = sentence.split("\n")
			maxProb = 0
			for line in lines:
				word = line.split("\t")[0]
				constructedSent += word + " "
				word = (word, line.split("\t")[1])
				if (word in probabilities.keys()):
					maxProb = max(maxProb, probabilities[word])
			# print fileNum, count, maxProb
			scores.append(maxProb)
	return scores


def getBigramScores(probabilities):
	scores = []
	for fileNum in range(951, 1187):
		strNum = '%04d' % fileNum
		fileName = "doc_" + strNum + ".txt"
		if (fileNum % 100 == 0):
			print fileName
		file = open("cross_validation/" + fileName).read().split("\n\n")[:-1]

		for sentence in file:
			constructedSent = ""
			# print "SENT: " + sentence
			lines = sentence.split("\n")
			maxProb = 0
			prevWord = ""
			for line in lines:
				word = line.split("\t")[0]
				constructedSent += word + " "
				# word = (prevWord + "_" + word, line.split("\t")[1])
				word = (prevWord + "_" + word)
				# print word
				if (word in probabilities.keys()):
					maxProb = max(maxProb, probabilities[word])
				prevWord = line.split("\t")[0]
			# print fileNum, count, maxProb
			scores.append(maxProb)
	return scores


def generateOutput(scores, threshold):
	outFileName = "crossData.txt"
	outfile = open(outFileName, "w")
	count = 0

	for score in scores:
		if(score > threshold):
			print >>outfile, count
		count += 1

	outfile.close()


if __name__ == "__main__":

	threshold = 0.075

	[freqs, curFreqs] = trainBigram()

	probabilities = getProbabilities(freqs, curFreqs)

	scores = getBigramScores(probabilities)

	generateOutput(scores, threshold)