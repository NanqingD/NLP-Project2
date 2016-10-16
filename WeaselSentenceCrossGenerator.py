

count = 0

for fileNum in range(951, 1187):
	seenCues = []
	# print curFreqs
	strNum = '%04d' % fileNum
	fileName = "doc_" + strNum + ".txt"
	# if (fileNum % 100 == 0):
	# 	print fileName
	file = open("cross_validation/" + fileName).read().split("\n\n")[:-1]

	for sent in file:
		ambi = False
		lines = sent.split("\n")
		# print lines
		for line in lines:
			lineData = line.split("\t")
			# print lineData
			if(len(lineData) >= 2 and lineData[2] != "_"):
				# print "LINE : " + lineData[2]
				ambi = True
		# print sent
		if ambi:
			print count

		count += 1
		# print "---------------------------------------------------------"
