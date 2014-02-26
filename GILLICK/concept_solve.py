from __future__ import division
from nltk import word_tokenize
import re
from pulp import *

def findConcept(sents):
    punct = re.compile(r"\W+")
    conMap = {}
    conWeight = {}
    sentCon = {}
    for i in range(len(sents)):
        sent = sents[i]
        sentCon[i] = []
        words = word_tokenize(sent.lower())
        bigrams = [words[j]+" "+words[j+1] for j in range(len(words)-1) if \
                   not punct.match(words[j]) and not punct.match(words[j+1])]
        bigrams = set(bigrams)
        for c in bigrams:
            if c not in conMap:
                conMap[c] = len(conMap)
            conID = conMap[c]
            conWeight.setdefault(conID, 0)
            conWeight[conID] += 1
            sentCon[i].append(conID)

    return conWeight, sentCon, conMap
        
def buildConSent(sentCon):
    items = sentCon.items()
    conSent = {}
    for item in items:
        sent = item[0]
        conList = item[1]
        for con in conList:
            conSent.setdefault(con, [])
            conSent[con].append(sent)
    return conSent

def modelling(conWeight, sentCon, lenList, limit):
    conLen = len(conWeight)
    sentLen = len(sentCon)
    conSent = buildConSent(sentCon)
    record = []
    # creating variables
    for i in range(sentLen):
        sm = "x_"+str(i)+" = LpVariable(\"x_"+str(i)+"\", 0, 1, \"Integer\")"
        record.append(sm)
        exec sm
    for i in range(conLen):
        sm = "y_"+str(i)+" = LpVariable(\"y_"+str(i)+"\", 0, 1, \"Integer\")"
        record.append(sm)
        exec sm
    # object function
    prob = LpProblem("summarization", LpMaximize)
    objList = []
    for i in range(len(conWeight)):
        S = str(conWeight[i])+"*"+"y_"+str(i)
        objList.append(S)
    sm = "prob += " + " + ".join(objList)
    record.append(sm)
    exec sm
    for i in range(sentLen):
        conList = sentCon[i]
        for c in conList:
            sm = "prob += "  + "x_"+str(i)+"-"+"y_"+str(c)+"<=0"
            record.append(sm)
            exec sm
    for i in range(conLen):
        sentList = conSent[i]
        constList = []
        for s in sentList:
            constList.append("x_"+str(s))
        sm = "prob += " + " + ".join(constList)+"-"+"y_"+str(i)+">=0"
        record.append(sm)
        exec sm
        
    # length constraint    
    const = []
    for i in range(sentLen):
        const.append(str(lenList[i])+"*"+"x_"+str(i))
    sm = "prob +=" + " + ".join(const) + "<="+str(limit)
    record.append(sm)
    exec sm
    
    status = prob.solve(GLPK(msg=0))
    #print LpStatus[status]
    result = []
    for i in range(sentLen):
        exec "v = value(x_"+str(i)+")"
        result.append(v)
    f = open("log_solver_concept.txt", "w")
    f.write("\n".join(record))
    f.close()
    return result
