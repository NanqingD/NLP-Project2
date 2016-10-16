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

def main():
	aggregate_training_files()

if __name__ == '__main__':
	main()