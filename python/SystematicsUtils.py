from systematic import Systematic
from configManager import configMgr
from ROOT import TMath

def getISRSyst(sig):
    errisr = 0.
    if sig.find("slepton"):
        mgl = int(sig.split('_')[4])
        mlsp = int(sig.split('_')[7])
    else:
        mgl = int(sig.split('_')[3])
        mlsp = int(sig.split('_')[4])
    mdiff = mgl - mlsp

    norm = TMath.sqrt(0.25**2 + 0.10**2) # these are the max. showering parameter variations we found (variations recommended for pythia 2011 tunes)
            
    if mgl<300: norm += (1.-(mgl-200)/100.)*0.25
    if mdiff<300: errisr = (1.-(mdiff/300.))*norm # the uncertainty grows towards the mass diagonal, and when mgl gets smaller.

    isrHighWeights = ("genWeight",str(1+errisr),"eventWeight","leptonWeight","triggerWeightUp","truthWptWeight","bTagWeight3Jet")
    isrLowWeights = ("genWeight",str(1-errisr),"eventWeight","leptonWeight","triggerWeightDown","truthWptWeight","bTagWeight3Jet")

    isrUnc = Systematic("ISR",configMgr.weights,isrHighWeights,isrLowWeights,"weight","overallSys")
    return isrUnc


