# David Cote, October 2013
# Place-holder for functions to interpret complex command line arguments
# common to HistFitter.py, YieldsTable.py, SysTable.py and other scripts.

from ROOT import Util,RooAddition,RooArgList 

def cmdStringToListOfLists(inputString):
    #This function expects an inputString of format:
    # '[topZ,topW,ttbarHiggs,singleTopZ],[diBosonWZ,diBosonPowhegZZ,triBoson],fakes'
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


def getPdfInRegions(w,sample,region):
    if isinstance(sample,list):
        sampleArgList = RooArgList()
        sample_str="group"
        for s in sample:
            componentTmp = Util.GetComponent(w,s,region,True)
            sample_str=sample_str+"_"+s
            sampleArgList.add(componentTmp)
            pass
        pdfInRegion = RooAddition(sample_str,sample_str,sampleArgList)
    else:
        pdfInRegion  = Util.GetComponent(w,sample,region)
        pass
    return pdfInRegion

def getName(obj):
    if isinstance(obj,str):
        return obj
    elif isinstance(obj,list):
        name="group"
        for i in obj:
            name=name+"_"+i
            pass
        return name
    else:
        print "WARNING: cannot handle object of type %s. Return 'N/A'"%type(obj)
    return "N/A"
