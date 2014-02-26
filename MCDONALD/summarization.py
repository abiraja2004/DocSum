import preprocess as pp
import solve
reload(pp)
reload(solve)

def readIdf(fname):
    f = open(fname)
    lines = f.readlines()
    items = [l.split() for l in lines]
    items = [(e[0],float(e[1])) for e in items]
    return dict(items)

def summarize(fname, idfDict, alpha, limit):
    f = open(fname)
    sents = f.readlines()
    sents = [s.strip() for s in sents]
    f.close()
    cont = " ".join(sents)
    contVec = pp.tfIdfDict(cont.lower(), idfDict)
    
    sents = [s.strip() for s in sents]
    tiVec = []
    repList = []
    lenList = []
    for sent in sents:
        v = pp.tfIdfDict(sent.lower(), idfDict)
        tiVec.append(v)
        repList.append(pp.similarity(v, contVec))
        lenList.append(1)
    simList = []
    for i in range(len(sents)):
        simList.append([])
        for j in range(len(sents)):
            simList[i].append(0)
    for i in range(len(sents)):
        for j in range(i+1, len(sents)):
            sim = pp.similarity(tiVec[i],tiVec[j])
            if sim == -1:
                print sents[i], sents[j]
            simList[i][j] = sim
            simList[j][i] = sim
            
    result = solve.modeling(lenList, repList, simList, limit)
    print result
    summary = [sents[i] for i in range(len(result)) if result[i] == 1]
    return repList, simList, summary
