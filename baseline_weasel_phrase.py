'''
Put this file in the folder contains "train", "test-private" and "test-public" folder.
'''

import os


def getCurrentPath():
    path = os.getcwd()
    return path


def getTrainFiles(path):
    subpath = path + '\\train'
    files = os.listdir(subpath)
    return files, subpath


def isCue(cue):
    if cue == '_':
        return False
    return True


def isEmptyLine(line):
    if line.strip() == '':
        return True
    else:
        return False


# def getHedge(f, hedge):
#     for line in f:    
#         if not isEmptyLine(line):
#             word, pos, cue = line.strip().lower().split('\t')
#             if isCue(cue):
#                 hedge.add((word,pos))


def getHedge(f, hedge):
    consecutive = False
    for line in f:    
        if not isEmptyLine(line):
            word, pos, cue = line.strip().lower().split('\t')
            if isCue(cue) and not consecutive:
                hedge.add((word,pos))
                consecutive = True
            elif not isCue(cue):
                consecutive = False


def trainHedge(path):
    hedge = set()
    files, subpath = getTrainFiles(path)
    for doc in files:
        filepath = subpath + "\\" + doc
        f = open(filepath, 'r')
        getHedge(f, hedge)

    return hedge


def getTestFiles(path, folder_type):
    "Param folder_type: 'private' or 'public'"
    subpath = path + '\\test-' + folder_type
    files = os.listdir(subpath)
    return files, subpath


def outputSubmission(path, hedge, submission):
    writeToSubmission(path, hedge, submission, 'public')
    writeToSubmission(path, hedge, submission, 'private')


def writeToSubmission(path, hedge, submission, folder_type):
    files, subpath = getTestFiles(path, folder_type)
    w = open(submission, 'a+')
    w.write('CUE-'+ folder_type +',')
    count = 0
    for doc in files:
        filepath = subpath + "\\" + doc
        f = open(filepath, 'r')
        count = phraseDetection(f, hedge, w, count)

    w.write('\n')
    w.close()


def phraseDetection(f, hedge, w, count):
    consecutive = False
    span = []
    for line in f:    
        if not isEmptyLine(line):
            word, pos = line.strip().lower().split('\t')
            count += 1
            if (word,pos) in hedge:
                if not consecutive:
                    span.append(count)
                    consecutive = True
            else:
                if consecutive:
                    if len(span) == 1:
                        w.write('%s ' %(span[0]))
                    else:
                        w.write('%s-%s ' %(span[0],span[-1]))
                    consecutive = False   
                    span = []
    return count

def main():
    path = getCurrentPath()
    hedge = trainHedge(path)
    w = open('phrase_submission.csv','w+')
    w.write('Type,Spans\n')
    w.close()
    outputSubmission(path, hedge, 'phrase_submission.csv')


if __name__ == '__main__':
    main()