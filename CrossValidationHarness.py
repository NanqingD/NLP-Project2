import WeaselSentenceBaseline
import F1score
import pickle
import operator

[freqs, curFreqs] = WeaselSentenceBaseline.trainBigram()
for word in curFreqs.keys():
	if(curFreqs[word] < 2):
		curFreqs.pop(word, None)


print "Done training"

probabilities = WeaselSentenceBaseline.getProbabilities(freqs, curFreqs)

sorted_probs = sorted(probabilities.items(), key=operator.itemgetter(1))

print sorted_probs[-30:]


print "Done getting probabilities"

scores = WeaselSentenceBaseline.getBigramScores(probabilities)



# with open("scoresList.txt", "wb") as f:
#	pickle.dump(scores, f)

# with open("scoresList.txt", 'rb') as f:
    # scores = pickle.load(f)

print "Done computing scores"

for thresInt in range(0, 100): 
	thres = thresInt / 100.0

	WeaselSentenceBaseline.generateOutput(scores, thres)

	print str(thres) + "\t" + str(F1score.computeScore())
