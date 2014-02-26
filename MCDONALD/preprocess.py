from __future__ import division
from math import sqrt, log
import xml.etree.ElementTree as ET
import nltk

def extractPostSent(inDir, fname, outDir):
    tree = ET.parse(inDir+fname)
    root = tree.getroot()
    length = len(root[0][1])
    sentList = []
    sumList = [[],[],[],[]]
    for i in range(length):
        sent = root[0][1][i].text
        words = nltk.word_tokenize(sent)
        sent = " ".join(words)
        sentList.append(sent)
        attrib = root[0][1][i].attrib
        if 'labelers' not in attrib:
            continue
        else:
            labStr = attrib["labelers"]
            labelers = labStr.split(", ")
            labelers = [int(t)-1 for t in labelers]
            for t in labelers:
                sumList[t].append(sent)
    fname = ".".join(fname.split(".")[:-1])
    f = open(outDir+fname+".sent","w")
    f.write("\n".join(sentList))
    f.close()
    for t in range(4):
        f = open(outDir+fname+".summary_"+str(t),"w")
        f.write("\n".join(sumList[t]))
        f.close()

def compIdf(fileList):
    Dict = {}
    N = len(fileList)
    for fname in fileList:
        f = open(fname)
        words = f.read().lower().split()
        for w in set(words):
            Dict.setdefault(w, 0)
            Dict[w] += 1
    for w in Dict:
        Dict[w] = log(N/Dict[w])
    return Dict

def tfDict(sent):
    sent = sent.split()
    D = {}
    for w in sent:
        D.setdefault(w, 0)
        D[w] += 1.0
    for w in sent:
        D[w] /= len(sent)
    return D

def tfIdfDict(sent, idfDict):
    tf = tfDict(sent)
    tfIdf = {}
    for w in tf:
        tfIdf[w] = tf[w]*idfDict[w]
    return tfIdf

def vecLen(Dict):
    values = Dict.values()
    values = [t*t for t in values]
    return sqrt(sum(values))

def similarity(Da, Db):
    La = vecLen(Da)
    Lb = vecLen(Db)
    V = 0
    for w in Da:
        if w in Db:
            V += Da[w]*Db[w]
    if V == 0:
        return 0
    return V/La/Lb
