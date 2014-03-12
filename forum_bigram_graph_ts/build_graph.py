import re, numpy, nltk

class sentGroup:
    def __init__(self, fname, sentFile):
        f = open(fname)
        lines = f.readlines()
        f.close()
        wordMap = {}
        f = open(sentFile)
        cont = f.read()
        post = cont.split("\n\n")
        f.close()

        self.sentMap = {}
        self.reply = {}
        self.authorSent = {}
        self.postSent = {}
        
        sentID = 0

        reply_pattern = re.compile(r"##Replied to (\d+)##")
        if len(lines) != len(post):
            print "Error!!"
        for i in range(len(lines)):
            l = lines[i]
            p = post[i]
            if p == "# # There is no sentence in this post .":
                continue
            cont = l.split("\t\t")[-1]
            #print cont
            replyID = reply_pattern.findall(cont)
            #print replyID
            replyID = [r for r in replyID if r in self.postSent]
            postID = l.split("\t\t")[0]
            #print l
            author = l.split("\t\t")[2]
            if replyID:
                self.reply[postID] = replyID
            if author not in self.authorSent:
                self.authorSent[author] = []
                
            self.postSent[postID] = []
            sents = p.split("\n")
            for s in sents:
                self.sentMap[sentID] = s
                self.postSent[postID].append(sentID)
                self.authorSent[author].append(sentID)
                sentID += 1


class wordGraph:
    def __init__(self, sentGroup, rmStop = False):
        self.sentGroup = sentGroup
        self.readStopWord()
        pattern = re.compile(r"\w+")
        self.wordMap = {}
        self.tokensMap = {}
        sentMap = sentGroup.sentMap
        for item in sentMap.items():
            ID = item[0]
            sent = item[1]
            tokens = nltk.word_tokenize(sent.lower())
            #tokens = [t for t in tokens if pattern.match(t) and t not in self.stopWord]
            if rmStop:
                self.readStopWord()
                tokens = [tokens[i]+" "+tokens[i+1] for i in range(len(tokens)-1) if pattern.match(tokens[i]) and pattern.match(tokens[i+1]) \
                    and (tokens[i] not in self.stopWord or tokens[i+1] not in self.stopWord)]
            else:
                tokens = [tokens[i]+" "+tokens[i+1] for i in range(len(tokens)-1) if pattern.match(tokens[i]) and pattern.match(tokens[i+1])]

            for t in tokens:
                if t not in self.wordMap:
                    self.wordMap[t] = len(self.wordMap)
            self.tokensMap[ID] = set(tokens) # in each sentence, each word is just counted once

    def readStopWord(self):
        f = open("D:\\Project\\package\\stopWord.txt")
        cont = f.read()
        f.close()
        self.stopWord = cont.split()
        self.stopWord.append("n't")
        self.stopWord = set(self.stopWord)


    def buildWordGraph(self, alpha, beta, gamma):
        N = len(self.wordMap)
        self.graphMatrix = numpy.matrix(numpy.zeros((N,N)))
        # sentence relationship
        for tokenMap in self.tokensMap.values():
            tokenList = list(tokenMap)
            for i in range(len(tokenList)):
                m = self.wordMap[tokenList[i]]
                for j in range(i+1, len(tokenList)):
                    n = self.wordMap[tokenList[j]]
                    self.graphMatrix[m,n] += alpha
                    self.graphMatrix[n,m] += alpha
        # author level
        for List in self.sentGroup.authorSent.values():
            N = len(List)
            for i in range(len(List)):
                for j in range(i+1, len(List)):
                    for v in self.tokensMap[List[i]]:
                        for w in self.tokensMap[List[j]]:
                            m = self.wordMap[v]
                            n = self.wordMap[w]
                            
                            if m!=n:
                                self.graphMatrix[m,n] += beta
                                self.graphMatrix[n,m] += beta
        #reply
        self.postToken = {}
        for postID in self.sentGroup.postSent:
            self.postToken[postID] = set()
            sentList = self.sentGroup.postSent[postID]
            for sent in sentList:
                self.postToken[postID] |= self.tokensMap[sent]

        for postID in self.sentGroup.reply:
            for replyID in self.sentGroup.reply[postID]:
                for v in self.postToken[postID]:
                    for w in self.postToken[replyID]:
                        m = self.wordMap[v]
                        n = self.wordMap[w]

                        if m!=n:
                            self.graphMatrix[m,n] += gamma
                            #self.graphMatrix[n,m] += gamma

    def textRank(self, delta, eta, maxIter):
        N = len(self.wordMap)
        self.score = numpy.matrix(numpy.ones((1, N)))*1/N
        rowSum = self.graphMatrix.sum(1)
        # in case there is no out link
        for i in range(len(rowSum)):
            if rowSum[i] == 0:
                rowSum[i] = 1

        # restart vector for topic sensitive pagerank
        topicWord = self.readTopWord()
        restart = numpy.zeros((1,N))
        items = self.wordMap.items()
        items = [list(t) for t in items]
        [t.reverse() for t in items]
        revWordMap = dict(items)

        for i in range(N):
            term = revWordMap[i]
            if term in topicWord:
                restart[0,i] = 1
            else:
                words = term.split()
                if words[0] in topicWord or words[1] in topicWord:
                    restart[0,i] = 1
        restart_matrix = numpy.tile(restart, (N,1))
        denoMatrix = numpy.tile(rowSum, (1,N))
        #self.weightMatrix = self.graphMatrix/denoMatrix
        #self.weightMatrix = self.graphMatrix/denoMatrix*eta+ (1-eta)*1.0/N*numpy.matrix(numpy.ones((N,N)))
        self.weightMatrix = self.graphMatrix/denoMatrix*eta+ (1-eta)*1.0/restart.sum()*restart_matrix
        #print self.weightMatrix
        tmp_score = self.score.copy()
        for i in range(maxIter):
            self.score = self.score*self.weightMatrix
            self.score /= self.score.sum() #normalization
            #print self.score
            diff = abs(tmp_score-self.score).sum()
            if diff <= delta:
                break
            tmp_score = self.score.copy()
        print "Iteration terminated at: ", i + 1
        print "Difference is: ", diff

    def readTopWord(self):
        f = open("D:/Project/Document_Summarization/forum_bigram_graph_ts/sentiWords.txt")
        topicWord = f.read().split()
        f.close()
        f = open("D:/Project/Document_Summarization/forum_bigram_graph_ts/actionWords.txt")
        topicWord += f.read().split()
        f.close()
        return set(topicWord)

    def saveScore(self, fname):
        items = self.wordMap.items()
        items = [list(t) for t in items]
        [t.reverse() for t in items]
        revWordMap = dict(items)
        scoreList = [(revWordMap[i], self.score[0,i]) for i in range(self.score.size)]
        scoreList.sort(key=lambda x:x[1], reverse=True)
        contList = [t[0]+"\t"+str(t[1]) for t in scoreList]
        f = open(fname, "w")
        f.write("\n".join(contList))
        f.close()
