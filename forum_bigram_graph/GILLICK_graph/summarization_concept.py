import concept_solve as cs
import re
reload(cs)

def summarize(fname, conWeightFile, limit):
    f = open(fname)
    sents = re.split(r"\n+", f.read())
    sents = [s for s in sents if not s == "# # There is no sentence in this post ."]
    sents = [s.strip() for s in sents]
    f.close()
    conWeight, sentCon, conMap = cs.findConcept(sents, conWeightFile)
    lenList = [len(s.split()) for s in sents]
    result = cs.modelling(conWeight, sentCon, lenList, limit)
    summary = [sents[i] for i in range(len(result)) if result[i] == 1]
    return sents, conWeight, sentCon, conMap, result, summary
