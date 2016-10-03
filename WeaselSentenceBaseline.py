
# seenCues = []

freqs = {}
curFreqs = {}

for fileNum in range(1, 1187):#87):
	seenCues = []
	# print curFreqs
	strNum = '%04d' % fileNum
	fileName = "doc_" + strNum + ".txt"
	if (fileNum % 100 == 0):
		print fileName
	file = open("train/" + fileName).read().split("\n")

	for line in file:
		lineData = line.split("\t")
		word = lineData[0].lower()
		if(len(lineData) >= 2 and lineData[2] != "_" and (not lineData[2] in seenCues)):
			seenCues.append(lineData[2])
			if(word not in curFreqs.keys()):
				curFreqs[word] = 0
			curFreqs[word] += 1
		if(word not in freqs.keys()):
			freqs[word] = 0
		freqs[word] += 1

probabilities = {}
for word in freqs:
	freq = freqs[word]
	ambiFreq = 0
	if(word in curFreqs.keys()):
		ambiFreq = curFreqs[word]
	probabilities[word] = ambiFreq * 1.0 / freq * 1.0

# for word in probabilities:
# 	if(probabilities[word] != 0):
# 		print word, probabilities[word]

count = 0

outString = ""

for fileNum in range(1, 501):
	strNum = '%04d' % fileNum
	fileName = "doc_" + strNum + ".txt"
	if (fileNum % 100 == 0):
		print fileName
	file = open("test-private/" + fileName).read().split("\n\n")[:-1]

	for sentence in file:
		constructedSent = ""
		# print "SENT: " + sentence
		lines = sentence.split("\n")
		maxProb = 0
		for line in lines:
			word = line.split("\t")[0]
			constructedSent += word + " "
			if (word in probabilities.keys()):
				maxProb = max(maxProb, probabilities[word])
		# print fileNum, count, maxProb
		if(maxProb > 0.3):
			outString += str(count) + " "
			# print constructedSent
		count += 1


print "OUTSTRING: " + outString