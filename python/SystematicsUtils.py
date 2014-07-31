"""
 **********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Namespace: SystematicsUtils                                                    *
 * Created: November 2012                                                         *
 *                                                                                *
 * Description:                                                                   *
 *             Functions for processing systematics                               *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************
"""

from systematic import Systematic
from configManager import configMgr
from ROOT import TMath
from copy import deepcopy


def matchName(aChan, chanList):
    for chan in chanList:
        if aChan.name == chan.name:
            return True
        pass
    return False


def appendIfMatchName(aChan, chanList):
    if aChan in chanList:
        print "WARNING instance of channel %s already in chanList. " \
              "Not the typical use case." % (aChan.name)
    if matchName(aChan, chanList):
        chanList.append(aChan)
        pass
    return


def addWeight(oldList, newWeight):
    newList = deepcopy(oldList)
    newList.append(newWeight)
    return newList


# ATLAS specific - FIXME ; remove for public release
def getISRerr(sig):
    errisr = 0.
    if "slepton" in sig:
        mgl = int(sig.split('_')[4])
        mlsp = int(sig.split('_')[7])
    else:
        mgl = int(sig.split('_')[3])
        mlsp = int(sig.split('_')[4])
    mdiff = mgl - mlsp

    # these are the max. showering parameter variations we found
    # (variations recommended for pythia 2011 tunes)
    norm = TMath.sqrt(0.25 ** 2 + 0.10 ** 2)

    if mgl < 300:
        norm += (1.0 - (mgl - 200) / 100.0) * 0.25
    if mdiff < 300:
        # the uncertainty grows towards the mass diagonal,
        # and when mgl gets smaller.
        errisr = (1.0 - (mdiff / 300.0)) * norm

    return errisr

# ATLAS specific - FIXME ; remove for public release
def getISRSyst(sig):
    errisr = getISRerr(sig)

    isrHighWeights = addWeight(configMgr.weights, str(1 + errisr))
    isrLowWeights = addWeight(configMgr.weights, str(1 - errisr))

    isrUnc = Systematic("ISR", configMgr.weights, isrHighWeights,
                        isrLowWeights, "weight", "overallSys")
    return isrUnc


# ATLAS specific - FIXME ; remove for public release
def getISRWeightsHigh(sig):
    errisr = getISRerr(sig)

    isrHighWeights = addWeight(configMgr.weights, str(1 + errisr))
    return isrHighWeights

# ATLAS specific - FIXME ; remove for public release
def getISRWeightsLow(sig):
    errisr = getISRerr(sig)

    isrLowWeights = addWeight(configMgr.weights, str(1 - errisr))
    return isrLowWeights


# ATLAS specific - FIXME ; remove for public release
def hadroSys(CRval, SRval, sample, observable):
    if CRval > SRval:
        raise RuntimeError("Unsupported case: CRval=%f is "
                           "larger than SRval=%f" % (CRval, SRval))
    #Linear relation of form: y=ax+b

    if sample == "ttbar" and observable == "meff":
        #f(x) = 1.092 -0.000220*x
        a = -0.000220  # +- 0.000083
        #b=1.092 #+- 0.045
    elif sample == "ttbar" and observable == "met":
        #f(x) = 1.015 - 0.000216 * x
        a = -0.000216
        #b=1.015
    elif sample == "WZ" and observable == "metovermeff":
        #f(x) = 0.9503 + 0.2263 * x
        a = 0.2263
    elif sample == "WZ" and observable == "meff":
        #f(x)= 1.075 - 0.000177*x
        a =- 0.000177
        #b=1.075
    elif sample == "WZ" and observable == "met":
        #f(x) = 9.918109e-01+1.109077e-04 * x
        a = 0.0001109077
        #b=0.9918109
    else:
        raise RuntimeError("Unsupported case: sample=%s,"
                           " observable=%s" % (sample, observable))

    syst = abs(a * (SRval - CRval))
    #print "hadronization systematic for %s %s CR=%f SR=%f " \
    # "--> syst=%f"%(sample,observable,CRval,SRval,syst)
    return syst


# ATLAS specific - FIXME ; remove for public release
def hadroSysBins(CRval, SRNBins, SRBinLow, SRBinHigh, sample, observable):
    weights_up = []
    weights_down = []
    for bin in xrange(SRNBins):
        hadsystvalue = hadroSys(CRval,
                                SRBinLow + (SRBinHigh - SRBinLow) * (bin + 0.5) / SRNBins,
                                sample, observable)
        weights_up.append(1 + hadsystvalue)
        weights_down.append(1 - hadsystvalue)
    return weights_up, weights_down


# ATLAS specific - FIXME ; remove for public release
def addHadronizationSyst(chan, topSyst, WZSyst):
    for s in chan.sampleList:
        if s.name.startswith("Top"):
            s.addSystematic(topSyst)
        elif s.name.startswith("WZ"):
            s.addSystematic(WZSyst)
    return



