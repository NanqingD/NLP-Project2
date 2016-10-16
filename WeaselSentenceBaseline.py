import datetime

# seenCues = []

threshold = 0.075

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

probabilities = {}
for word in freqs:
	freq = freqs[word]
	ambiFreq = 0
	if(word in curFreqs.keys()):
		ambiFreq = curFreqs[word]
	probabilities[word] = ambiFreq * 1.0 / freq * 1.0

for word in probabilities:
	if(probabilities[word] != 0):
		print word, probabilities[word]

# quit()

outTime = datetime.datetime.now().strftime("%m-%d_%H:%M")
# outFileName = "s" + outTime + ".csv"

outFileName = "crossData.csv"
outfile = open(outFileName, "w")
count = 0

outString = ""

# print >>outfile, "Type,Indices"

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
		if(maxProb > threshold):
			print >>outfile, count
			outString += str(count) + " "
			# print constructedSent
		count += 1


print >>outfile, "CROSSVALIDATION," + outString


quit()

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
			word = (word, line.split("\t")[1])
			if (word in probabilities.keys()):
				maxProb = max(maxProb, probabilities[word])
		# print fileNum, count, maxProb
		if(maxProb > threshold):
			outString += str(count) + " "
			# print constructedSent
		count += 1


print >>outfile, "SENTENCE-private," + outString
print "CDE"

outfile.close()
print "CLOSED!"