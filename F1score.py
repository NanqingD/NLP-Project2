def computeScore():

	trueData = open("crosstruedata.txt", "r").read().split("\n")
	modelData = open("crossdata.txt", "r").read().split("\n")[:-1]

	trueData = map(int, trueData)
	modelData = map(int, modelData)

	precisionCount = 0

	for pred in modelData:
		if pred in trueData:
			precisionCount += 1

	precision = precisionCount * 1.0 / len(modelData)

	# print "P: " + str(precision)

	recallCount = 0

	for pred in trueData:
		if pred in modelData:
			recallCount += 1

	recall = recallCount * 1.0 / len(trueData)

	# print "R: " + str(recall)

	# print "F: " + str(precision * recall * 2)
	return (precision * recall * 2)