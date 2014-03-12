import build_graph as bg
reload(bg)
from GILLICK_graph import summarization_concept as sc
reload(sc)

def summarize(origFile, sentFile, limit=100, outDir="./", alpha=1, beta=1, gamma=1, diff=0.000000001, damping=0.85, maxIter=200,  suffix=".gillick_graph_ts.result", rmStop=False):
    sentG = bg.sentGroup(origFile, sentFile)
    wordG = bg.wordGraph(sentG, rmStop)
    wordG.buildWordGraph(alpha, beta, gamma)
    wordG.textRank(diff, damping, maxIter)
    prefix = ".".join(origFile.split("/")[-1].split(".")[:-1])
    scoreFile = outDir+prefix+".score"
    wordG.saveScore(scoreFile)
    #print wordG.graphMatrix
    sents, conWeight, sentCon, conMap, result, summary = sc.summarize(sentFile, scoreFile, limit)
    f = open(outDir+prefix+suffix,"w")
    f.write("\n".join(summary))
    f.close()