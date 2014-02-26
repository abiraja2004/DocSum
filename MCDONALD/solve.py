from __future__ import division
from pulp import *

def modeling(lenList, repList, simList, limit):
    length = len(repList)
    record = []
    # variables clarification
    for i in range(length):
        sm = "x_"+str(i)+" = LpVariable(\"x_"+str(i)+"\", 0, 1, \"Integer\")"
        #print sm
        record.append(sm)
        exec sm
        for j in range(i+1, length):
            sm = "x_"+str(i)+"_"+str(j)+" = LpVariable(\"x_"+str(i)+"_"+str(j)+"\", 0, 1, \"Integer\")"
            record.append(sm)
            exec sm
        
    prob = LpProblem("summarization", LpMaximize)
    #object function
    objList = []
    objStr = ""
    for i in range(length):
        objList.append(str(repList[i])+"*"+"x_"+str(i))
    objStr = " + ".join(objList)
    objList = []
    for i in range(length):
        for j in range(i+1, length):
            objList.append(str(simList[i][j])+"*"+"x_"+str(i)+"_"+str(j))
    objStr += " - "+ " - ".join(objList)
    sm = "prob += " + objStr
    record.append(sm)
    #print sm
    exec sm

    # constraints
    # length
    const = []
    for i in range(length):
        const.append(str(lenList[i])+"*"+"x_"+str(i))
    sm = "prob +=" + " + ".join(const) + "<="+str(limit)
    record.append(sm)
    exec sm
    #########
    for i in range(length):
        for j in range(length):
            if i == j:
                continue
            if i < j:
                a = i
                b = j
            else:
                a = j
                b = i
            S = "x_"+str(a)+"_"+str(b)+" - "+"x_"+str(b)+"<=0"
            sm = "prob += " + S
            record.append(sm)
            #print sm
            exec sm
            S = "x_"+str(a)+"_"+str(b)+" - "+"x_"+str(a)+"<=0"
            sm = "prob += " + S
            record.append(sm)
            #print sm
            exec sm
            S = "x_"+str(a)+"+"+"x_"+str(b)+" - "+"x_"+str(a)+"_"+str(b)+"<=1"
            sm = "prob += " + S
            record.append(sm)
            #print sm
            exec sm
    status = prob.solve(GLPK(msg=0))
    #print LpStatus[status]
    result = []
    for i in range(length):
        exec "v = value(x_"+str(i)+")"
        result.append(v)
    f = open("log_solver.txt", "w")
    f.write("\n".join(record))
    f.close()
    return result
            
