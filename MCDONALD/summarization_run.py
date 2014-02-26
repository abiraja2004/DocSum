import summarization as summ
import os
reload(summ)

inDir = "../data_blog_summarization/"
outDir = "../result_blog_summarization/"
fList = os.listdir(inDir)
fList = [f for f in fList if f[-4:]=="sent"]
idfDict = summ.readIdf("idfList.txt")
limit = 7

for fname in fList:
    repList, simList, summary = summ.summarize(inDir+fname, idfDict, 1, limit)
    fout = fname[:-4]+"mcdonald.result"
    f = open(outDir+fout, "w")
    f.write("\n".join(summary))
    f.close()
