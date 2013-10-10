s="[topZ,topW,ttbarHiggs,singleTopZ],[diBosonWZ,diBosonPowhegZZ,triBoson],fakes"

def cmdStringToListOfLists(inputString):
    rawList=inputString.split(",")
    finalList=[]
    openBlock=False
    tmpList=[]
    for s in rawList:
        if openBlock==False:
            if s.startswith("["):
                tmpList=[]
                tmpList.append(s[1:])
                openBlock=True
            elif s.endswith("]"):
                raise RuntimeError("Syntax error. Unable to decode '%s'"%inputString)
            else:
                finalList.append(s)
                pass
        elif openBlock==True:
            if s.endswith("]"):
                tmpList.append(s[:len(s)-1])
                finalList.append(tmpList)
                openBlock=False
            elif s.startswith("["):
                raise RuntimeError("Syntax error. Unable to decode '%s'"%inputString)
            else:        
                tmpList.append(s)
                pass
            pass
        pass
    return finalList
