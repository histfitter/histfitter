from systematic import Systematic
from configManager import configMgr
from ROOT import TMath
from copy import deepcopy


def addWeight(oldList,newWeight):
    newList = deepcopy(oldList)
    newList.append(newWeight)
    return newList
            
def getISRerr(sig):
    errisr = 0.
    if "slepton" in sig:
        mgl = int(sig.split('_')[4])
        mlsp = int(sig.split('_')[7])
    else:
        mgl = int(sig.split('_')[3])
        mlsp = int(sig.split('_')[4])
    mdiff = mgl - mlsp

    norm = TMath.sqrt(0.25**2 + 0.10**2) # these are the max. showering parameter variations we found (variations recommended for pythia 2011 tunes)
            
    if mgl<300: norm += (1.-(mgl-200)/100.)*0.25
    if mdiff<300: errisr = (1.-(mdiff/300.))*norm # the uncertainty grows towards the mass diagonal, and when mgl gets smaller.

    return errisr

def getISRSyst(sig):

    errisr=getISRerr(sig)

    isrHighWeights = addWeight(configMgr.weights,str(1+errisr)) 
    isrLowWeights = addWeight(configMgr.weights,str(1-errisr)) 

    isrUnc = Systematic("ISR",configMgr.weights,isrHighWeights,isrLowWeights,"weight","overallSys")
    return isrUnc

def getISRWeightsHigh(sig):

    errisr=getISRerr(sig)

    isrHighWeights = addWeight(configMgr.weights,str(1+errisr)) 
    return isrHighWeights


def getISRWeightsLow(sig):

    errisr=getISRerr(sig)

    isrLowWeights = addWeight(configMgr.weights,str(1-errisr)) 
    return isrLowWeights


def getHadronizationSyst(CRval,SRval,sample,observable):
    if CRval>SRval:
        raise RuntimeError("Unsupported case: CRval=%f is larger than SRval=%f"%(CRval,SRval))
    #Linear relation of form: y=ax+b

    if sample=="ttbar" and observable=="meff":
        a=0.000220 #+- 0.000083
        #b=1.092 +- 0.045
    elif sample=="ttbar" and observable=="met":
        a=0.0001109077
        #b=0.9918109
    elif sample=="WZ" and observable=="meff":
        raise RuntimeError("Unsupported case: sample=%s, observable=%s"%(sample,observable))
    elif sample=="WZ" and observable=="met":
        raise RuntimeError("Unsupported case: sample=%s, observable=%s"%(sample,observable))
    else:
        raise RuntimeError("Unsupported case: sample=%s, observable=%s"%(sample,observable))

    syst=a*(SRval-CRval)
    print "%s %s CR=%f SR=%f --> syst=%f"%(sample,observable,CRval,SRval,syst)
    return syst
