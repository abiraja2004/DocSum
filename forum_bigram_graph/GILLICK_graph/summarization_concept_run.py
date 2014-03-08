import os
import summarization_concept as sc
reload(sc)

inDir = "D:/Project/forum_sum_program/preprocess/"
outDir = "D:/Project/forum_sum_program/preprocess/"
limit = 100
fileList = os.listdir(inDir)
sentFileList = [f for f in fileList if f.endswith(".pp.txt")]
for fname in sentFileList:
    sents, conWeight, sentCon, conMap, result, summary = sc.summarize(inDir+fname, limit)
    f = open(outDir+fname.split(".")[0]+".gillick.result","w")
    f.write("\n".join(summary))
    f.close()
    
