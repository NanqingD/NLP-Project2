import nltk
import os
import glob


def aggregate_training_files():

	read_files = glob.glob("train/*.txt")
	print read_files

	with open("aggregated_training.txt", "wb") as outfile:
	    for f in read_files:
	        with open(f, "rb") as infile:
	            outfile.write(infile.read())

	return read_files


def viterbi(observations, states, start_prob, trans_prob, em_prob):

	V = [{}] 

	for state in states:
		V[0][state] = start_prob[state] * em_prob[state][observations[0]]

	for x in range(1, len(obs)):
		V.append({})
    	for state in states:
    		(probability, state) = max((V[t - 1][s] * trans_prob[s][state] * em_prob[state][observations[x]], s) for s in states)
        	V[x][state] = probability

       	states = []
        for v in V:
        	for x,y in v.items():
        		if v[x] == max(v.values()):
        			states.append(x)

	highestProb = max(V[-1].values())

	return states, highestProb
	
	

def main():
	read_files = aggregate_training_files()

if __name__ == '__main__':
	main()