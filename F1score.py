trueData = open("crosstruedata.txt", "r").read().split("\n")

modelData = open("crossvalidationdata.txt", "r").read().split("\n")

trueData = map(int, trueData)
modelData = map(int, modelData)

print trueData
print modelData

precisionCount = 0

for pred in modelData:
	if pred in trueData:
		precisionCount += 1

precision = precisionCount * 1.0 / len(modelData)

print precision

recallCount = 0

for pred in trueData:
	if pred in modelData:
		recallCount += 1

recall = recallCount * 1.0 / len(trueData)

print recall

print precision * recall * 2