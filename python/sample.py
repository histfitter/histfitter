import ROOT
from ROOT import TFile, TMath, RooRandom, TH1, TH1F
from ROOT import kBlack, kWhite, kGray, kRed, kPink, kMagenta, kViolet, kBlue, kAzure, kCyan, kTeal, kGreen, kSpring, kYellow, kOrange, kDashed, kSolid, kDotted
from os import system
from math import fabs
from logger import Logger
from systematic import SystematicBase

log = Logger('Sample')

import generateToys

TH1.SetDefaultSumw2(True)

from copy import deepcopy, copy
from configManager import configMgr

class Sample(object):
    """
    Defines a Sample in a channel XML file
    """

    def __init__(self, name, color=1):
        """
        Store configuration,  set sample name,  and if to normalize by theory

        Scales histograms to luminosity set in configuration
        """
        self.name = name
        self.color = color
        self.isData = False
        self.isQCD = False
        self.isDiscovery = False
        self.write = True
        self.normByTheory = False
        self.statConfig = False
        self.histoSystList = []
        self.shapeSystList = []
        self.overallSystList = []
        self.shapeFactorList = []
        self.systList = []
        self.weights = []
        self.systDict = {}
        self.normFactor = []
        self.qcdSyst = None
        self.unit = "GeV"
        self.cutsDict = {}
        self.files = []
        self.treeName = ''
        self.xsecWeight = None
        self.xsecUp = None
        self.xsecDown = None
        self.normRegions = None
        self.normSampleRemap = ''
        self.noRenormSys = True
        self.parentChannel = None

    def buildHisto(self, binValues, region, var):
        """
        Allow user to give bin values eg. for checking stats in papers
        """
        try:
            self.binValues[(region, var)] = binValues
        except AttributeError:
            self.binValues = {}
            self.binValues[(region, var)] = binValues
        if not self.isData:
            self.histoName = "h"+self.name+"Nom_"+region+"_obs_"+var
        else:
            self.histoName = "h"+self.name+"_"+region+"_obs_"+var
        configMgr.hists[self.histoName] = TH1F(self.histoName, self.histoName, len(self.binValues[(region, var)]), 0., float(len(self.binValues[(region, var)])))
        for (iBin, val) in enumerate(self.binValues[(region, var)]):
            configMgr.hists[self.histoName].SetBinContent(iBin+1, val)
        return

    def buildStatErrors(self, binStatErrors, region, var):
        """
        Allow user to give bin stat errors eg. for checking stats in papers
        """
        try:
            self.binStatErrors[(region, var)] = binStatErrors
        except AttributeError:
            self.binStatErrors = {}
            self.binStatErrors[(region, var)] = binStatErrors
        if not len(self.binStatErrors[(region, var)]) == len(self.binValues[(region, var)]):
            raise Exception("Length of errors list in region %s and variable %s does not match the nominal histogram!" % (region, var))
        if not self.isData:
            self.histoName = "h"+self.name+"Nom_"+region+"_obs_"+var
        else:
            self.histoName = "h"+self.name+"_"+region+"_obs_"+var
        for (iBin, err) in enumerate(self.binStatErrors[(region, var)]):
            try:
                configMgr.hists[self.histoName].SetBinError(iBin+1, err)
            except:
                raise Exception("Errors specified without building histogram!")

    def Clone(self):
        newInst = deepcopy(self)
        #for (key, val) in self.systDict.items():
        #    newInst.systDict[key] = val
        return newInst

    def setUnit(self, unit):
        self.unit = unit
        return

    def setCutsDict(self, cutsDict):
        self.cutsDict = cutsDict
        return

    def setData(self, isData=True):
        self.isData = isData
        return

    def setWeights(self, weights):
        """
        Set the weights for this sample - overrides
        """
        self.weights = deepcopy(weights)
        return

    def addWeight(self, weight):
        """
        Add a weight to this sample and propagate
        """
        if not weight in self.weights:
            self.weights.append(weight)
        else:
            raise RuntimeError("Weight %s already defined in sample %s" % (weight, self.name))
        for syst in self.systDict.values():
            if syst.type == "weight":
                if not weight in syst.high:
                    syst.high.append(weight)
                if not weight in syst.low:
                    syst.low.append(weight)
        return

    def removeWeight(self, weight):
        if weight in self.weights:
            self.weights.remove(weight)
        for syst in self.systDict.values():
            if syst.type == "weight":
                if weight in syst.high:
                    syst.high.remove(weight)
                if weight in syst.low:
                    syst.low.remove(weight)
        return
    def setQCD(self, isQCD=True, qcdSyst="uncorr"):
        self.isQCD = isQCD
        self.qcdSyst = qcdSyst
        return

    def setDiscovery(self, isDiscovery=True):
        self.isDiscovery = isDiscovery
        return

    def setNormByTheory(self, normByTheory=True):
        self.normByTheory = normByTheory
        return

    def setStatConfig(self, statConfig):
        self.statConfig = statConfig
        return

    def setWrite(self, write=True):
        self.write = write
        return

    def setHistoName(self, histoName):
        """
        Set the name of the nominal histogram for this sample
        """
        self.histoName = histoName
        return

    def setTreeName(self, treeName):
        self.treeName = treeName
        return

    def setNormRegions(self, normRegions):
        self.normRegions = normRegions
        self.noRenormSys = False
        return

    def propagateTreeName(self, treeName):
        if self.treeName == '':
            self.treeName = treeName
        ### MAB: Propagate treeName down to systematics of sample
        #for (systName, systList) in self.systDict.items():
        #    for syst in systList:
        #        syst.propagateTreeName(self.treeName)
        #        pass
        return

    def addHistoSys(self, systName, nomName, highName, lowName, includeOverallSys, normalizeSys, symmetrize=False, oneSide=False, samName="", normString=""):
        """
        Add a HistoSys entry using the nominal,  high and low histograms,  set if to include OverallSys

        If includeOverallSys then extract scale factors

        If normalizeSys then normalize shapes to nominal
        """

        if self.noRenormSys and normalizeSys:
            log.error("    sample.noRenormSys==True and normalizeSys==True for sample <%s> and syst <%s>. normalizeSys set to False."%(self.name,systName))
            normalizeSys = False

        if normalizeSys and not self.normRegions: 
            log.error("    normalizeSys==True but no normalization regions specified. This should never happen!")
            normChannels=[]
            tl=self.parentChannel.parentTopLvl
            for ch in tl.channels:
                if (ch.channelName in tl.bkgConstrainChannels) or (ch.channelName in tl.signalChannels):
                    normChannels.append((ch.regionString,ch.variableName))
                    pass
                pass
            self.setNormRegions(normChannels)
            log.warning("            For now, using all non-validation channels by default: %s"%self.normRegions)

        if normalizeSys:
            if not self.normRegions: 
                raise RuntimeError("You are using the Zero lepton modified version of HistFitter. Please specify normalization regions!")

            if oneSide and symmetrize:
                # symmetrize
                configMgr.hists[lowName] = configMgr.hists[nomName].Clone(lowName)
                configMgr.hists[lowName].Scale(2.0)
                configMgr.hists[lowName].Add(configMgr.hists[highName],  -1.0)

                for iBin in xrange(1, configMgr.hists[lowName].GetNbinsX()+1):
                    binVal = configMgr.hists[lowName].GetBinContent(iBin)
                    if binVal<0.:
                        configMgr.hists[lowName].SetBinContent(iBin, 0.)

            # use different renormalization region
            if len(self.normSampleRemap)>0: 
                samNameRemap = self.normSampleRemap
                log.info("remapping normalization of <%s> to sample:  %s"%(samName,samNameRemap))
            else:
                samNameRemap = samName

            highIntegral = configMgr.hists["h"+samNameRemap+systName+"High_"+normString+"Norm"].Integral()
            lowIntegral = configMgr.hists["h"+samNameRemap+systName+"Low_"+normString+"Norm"].Integral()
            nomIntegral = configMgr.hists["h"+samNameRemap+"Nom_"+normString+"Norm"].Integral()
            
            if oneSide and symmetrize:
                lowIntegral = 2.*nomIntegral - highIntegral # note,  this is an approximation!
                if lowIntegral<0:
                    lowIntegral = configMgr.hists["h"+samNameRemap+systName+"Low_"+normString+"Norm"].Integral()
                    if lowIntegral==0: lowIntegral=nomIntegral
                    # clearly a problem. Revert to unsymmetrize
                    log.warning("    generating HistoSys for %s syst=%s low=0. Revert to non-symmetrize." % (nomName, systName))
                    symmetrize = False

            try:
                high = highIntegral / nomIntegral
                low = lowIntegral / nomIntegral
            except ZeroDivisionError:
                log.error("    generating HistoSys for %s syst=%s nom=%g high=%g low=%g. Systematic is removed from fit." % (nomName, systName, nomIntegral, highIntegral, lowIntegral))
                return

            configMgr.hists[highName+"Norm"] = configMgr.hists[highName].Clone(highName+"Norm")
            configMgr.hists[lowName+"Norm"] = configMgr.hists[lowName].Clone(lowName+"Norm")

            try:
                configMgr.hists[highName+"Norm"].Scale(1./high)
                configMgr.hists[lowName+"Norm"].Scale(1./low)
            except ZeroDivisionError:
                log.error("    generating HistoSys for %s syst=%s nom=%g high=%g low=%g. Systematic is removed from fit." % (nomName, systName, nomIntegral, highIntegral, lowIntegral))
                return

            if includeOverallSys and not (oneSide and not symmetrize):
                nomIntegralN = configMgr.hists[nomName].Integral()
                lowIntegralN = configMgr.hists[lowName+"Norm"].Integral()
                highIntegralN = configMgr.hists[highName+"Norm"].Integral()

                if nomIntegralN==0 or highIntegralN==0 or lowIntegralN==0:
                    # MB : cannot renormalize,  so don't after all
                    log.warning("    will not generate overallNormHistoSys for %s syst=%s nom=%g high=%g low=%g. Revert to NormHistoSys." % (nomName, systName, nomIntegralN, highIntegralN, lowIntegralN))
                    includeOverallSys = False
                    pass
                else:
                    # renormalize
                    try:
                        highN = highIntegralN / nomIntegralN
                        lowN = lowIntegralN / nomIntegralN
                    except ZeroDivisionError:
                        log.error("    generating overallNormHistoSys for %s syst=%s nom=%g high=%g low=%g. Systematic is removed from fit." % (nomName, systName, nomIntegralN, highIntegralN, lowIntegralN))
                        return
                
                    try:
                        configMgr.hists[highName+"Norm"].Scale(1./highN)
                        configMgr.hists[lowName+"Norm"].Scale(1./lowN)
                    except ZeroDivisionError:
                        log.error("    generating overallNormHistoSys for %s syst=%s nom=%g high=%g low=%g keeping in fit (offending histogram should be empty)." % (nomName, systName, nomIntegralN, highIntegralN, lowIntegralN))
                        return


            # add the systematic
            if oneSide and not symmetrize:
                ## MB : avoid swapping of histograms
                self.histoSystList.append((systName, highName+"Norm", nomName, configMgr.histCacheFile, "", "", "", ""))
            else:
                self.histoSystList.append((systName, highName+"Norm", lowName+"Norm", configMgr.histCacheFile, "", "", "", ""))
            if includeOverallSys and not (oneSide and not symmetrize):
                self.addOverallSys(systName, highN, lowN)                
            

        if includeOverallSys and not normalizeSys:

            if oneSide and symmetrize:
                # symmetrize
                configMgr.hists[lowName] = configMgr.hists[nomName].Clone(lowName)
                configMgr.hists[lowName].Scale(2.0)
                configMgr.hists[lowName].Add(configMgr.hists[highName],  -1.0)

                for iBin in xrange(1, configMgr.hists[lowName].GetNbinsX()+1):
                    binVal = configMgr.hists[lowName].GetBinContent(iBin)
                    if binVal<0.:
                        configMgr.hists[lowName].SetBinContent(iBin, 0.)

            nomIntegral = configMgr.hists[nomName].Integral()
            lowIntegral = configMgr.hists[lowName].Integral()
            highIntegral = configMgr.hists[highName].Integral()

            if nomIntegral==0 or lowIntegral==0 or highIntegral==0:
                # MB : cannot renormalize,  so don't after all
                self.histoSystList.append((systName, highName, lowName, configMgr.histCacheFile, "", "", "", ""))
                return
            else:
                # renormalize
                try:
                    high = highIntegral / nomIntegral
                    low = lowIntegral / nomIntegral
                except ZeroDivisionError:
                    log.error("    generating HistoSys for %s syst=%s nom=%g high=%g low=%g. Systematic is removed from fit." % (nomName, systName, nomIntegral, highIntegral, lowIntegral))
                    return
                
                configMgr.hists[highName+"Norm"] = configMgr.hists[highName].Clone(highName+"Norm")
                configMgr.hists[lowName+"Norm"] = configMgr.hists[lowName].Clone(lowName+"Norm")
                try:
                    configMgr.hists[highName+"Norm"].Scale(1./high)
                    configMgr.hists[lowName+"Norm"].Scale(1./low)
                except ZeroDivisionError:
                    log.error("    generating HistoSys for %s syst=%s nom=%g high=%g low=%g keeping in fit (offending histogram should be empty)." % (nomName, systName, nomIntegral, highIntegral, lowIntegral))
                    return

                self.histoSystList.append((systName, highName+"Norm", lowName+"Norm", configMgr.histCacheFile, "", "", "", ""))
                self.addOverallSys(systName, high, low)


        if not includeOverallSys and not normalizeSys: # no renormalization,  and no overall systematic

            if symmetrize and not oneSide:
                nomIntegral = configMgr.hists[nomName].Integral()
                lowIntegral = configMgr.hists[lowName].Integral()
                highIntegral = configMgr.hists[highName].Integral()

                try:
                    high = highIntegral / nomIntegral
                    low = lowIntegral / nomIntegral
                except ZeroDivisionError:
                    log.error("    generating HistoSys for %s syst=%s nom=%g high=%g low=%g. Systematic is removed from fit." % (nomName, systName, nomIntegral, highIntegral, lowIntegral))
                    return

                if high<1.0 and low<1.0:
                    log.warning("    addHistoSys: high=%f is < 1.0 in %s. Taking symmetric value from low %f %f"% (high, systName, low, 2.-low))
                    configMgr.hists[highName+"Norm"] = configMgr.hists[highName].Clone(highName+"Norm")
                    try:
                        configMgr.hists[highName+"Norm"].Scale((2.-low)/high)
                    except ZeroDivisionError:
                        log.error("    generating HistoSys for %s syst=%s nom=%g high=%g low=%g. Systematic is removed from fit." % (nomName, systName, nomIntegral, highIntegral, lowIntegral))
                        return
                    self.histoSystList.append((systName, highName+"Norm", lowName, configMgr.histCacheFile, "", "", "", ""))
                    if not systName in configMgr.systDict.keys():
                        self.systList.append(systName)
                    return
                if low>1.0 and high>1.0:
                    log.warning("    addHistoSys: low=%f is > 1.0 in %s. Taking symmetric value from high %f %f"% (low, systName, high, 2.-high))
                    configMgr.hists[lowName+"Norm"] = configMgr.hists[lowName].Clone(lowName+"Norm")
                    try:
                        configMgr.hists[lowName+"Norm"].Scale((2.-high)/low)
                    except ZeroDivisionError:
                        log.error("    generating HistoSys for %s syst=%s nom=%g high=%g low=%g. Systematic is removed from fit." % (nomName, systName, nomIntegral, highIntegral, lowIntegral))
                        return
                    self.histoSystList.append((systName, highName, lowName+"Norm", configMgr.histCacheFile, "", "", "", ""))
                    if not systName in configMgr.systDict.keys():
                        self.systList.append(systName)
                    return
                if low<0.:
                    log.warning("    addHistoSys: low=%f is < 0.0 in %s. Setting negative bins to 0.0."% (low, systName))
                    configMgr.hists[lowName+"Norm"] = configMgr.hists[lowName].Clone(lowName+"Norm")
                    for iBin in xrange(1, configMgr.hists[lowName+"Norm"].GetNbinsX()+1):
                        if configMgr.hists[lowName+"Norm"].GetBinContent(iBin) < 0.:
                            configMgr.hists[lowName+"Norm"].SetBinContent(iBin, 0.)
                    self.histoSystList.append((systName, highName, lowName+"Norm", configMgr.histCacheFile, "", "", "", ""))
                    if not systName in configMgr.systDict.keys():
                        self.systList.append(systName)
                        return

                self.histoSystList.append((systName, highName, lowName, configMgr.histCacheFile, "", "", "", ""))
                return
            elif symmetrize and oneSide:
                # symmetrize
                configMgr.hists[lowName] = configMgr.hists[nomName].Clone(lowName)
                configMgr.hists[lowName].Scale(2.0)
                configMgr.hists[lowName].Add(configMgr.hists[highName],  -1.0)

                for iBin in xrange(1, configMgr.hists[lowName].GetNbinsX()+1):
                    binVal = configMgr.hists[lowName].GetBinContent(iBin)
                    if binVal<0.:
                        configMgr.hists[lowName].SetBinContent(iBin, 0.)

                # try to normalize
                nomIntegral = configMgr.hists[nomName].Integral()
                lowIntegral = configMgr.hists[lowName].Integral()
                highIntegral = configMgr.hists[highName].Integral()
                
                if nomIntegral==0 or lowIntegral==0 or highIntegral==0:
                    # cannot renormalize,  so don't
                    self.histoSystList.append((systName, highName, lowName, configMgr.histCacheFile, "", "", "", ""))
                else:
                    # renormalize
                    try:
                        high = highIntegral / nomIntegral
                        low = lowIntegral / nomIntegral
                    except ZeroDivisionError:
                        log.error("    generating HistoSys for %s syst=%s nom=%g high=%g low=%g. Systematic is removed from fit." % (nomName, systName, nomIntegral, highIntegral, lowIntegral))
                        return
                    
                    configMgr.hists[highName+"Norm"] = configMgr.hists[highName].Clone(highName+"Norm")
                    configMgr.hists[lowName+"Norm"] = configMgr.hists[lowName].Clone(lowName+"Norm")
                    try:
                        configMgr.hists[highName+"Norm"].Scale(1./high)
                        configMgr.hists[lowName+"Norm"].Scale(1./low)
                    except ZeroDivisionError:
                        log.error("    generating HistoSys for %s syst=%s nom=%g high=%g low=%g keeping in fit (offending histogram should be empty)." % (nomName, systName, nomIntegral, highIntegral, lowIntegral))
                        return

                    # overall histosys
                    self.histoSystList.append((systName, highName+"Norm", lowName+"Norm", configMgr.histCacheFile, "", "", "", ""))
                    self.addOverallSys(systName, high, low)
                    
                #self.histoSystList.append((systName, highName, nomName, configMgr.histCacheFile, "", "", "", ""))
                #self.histoSystList.append((systName, highName, lowName, configMgr.histCacheFile, "", "", "", ""))
                
                return    
            else: # default: don't do anything special
                self.histoSystList.append((systName, highName, lowName, configMgr.histCacheFile, "", "", "", ""))
                return

        if not systName in configMgr.systDict.keys():
            self.systList.append(systName)


    def addShapeSys(self, systName, nomName, highName, lowName, constraintType="Gaussian"):
        """
        Add a ShapeSys entry using the nominal,  high and low histograms
        """
        overallSystHigh = 1.
        overallSystLow = 1.

        configMgr.hists[highName+"Norm"] = configMgr.hists[highName].Clone(highName+"Norm")
        configMgr.hists[lowName+"Norm"]  = configMgr.hists[lowName].Clone(lowName+"Norm")
        configMgr.hists[nomName+"Norm"]  = configMgr.hists[nomName].Clone(nomName+"Norm")

        highIntegral = configMgr.hists[highName].Integral()
        lowIntegral  = configMgr.hists[lowName].Integral()
        nomIntegral  = configMgr.hists[nomName].Integral()

        for iBin in xrange(configMgr.hists[highName+"Norm"].GetNbinsX()+1):
            try:
                configMgr.hists[highName+"Norm"].SetBinContent(iBin,  fabs((configMgr.hists[highName+"Norm"].GetBinContent(iBin) / configMgr.hists[nomName].GetBinContent(iBin)) - 1.0) )
                configMgr.hists[highName+"Norm"].SetBinError(iBin, 0.)
            except ZeroDivisionError:
                configMgr.hists[highName+"Norm"].SetBinContent(iBin, 0.)
                configMgr.hists[highName+"Norm"].SetBinError(iBin, 0.)
        for iBin in xrange(configMgr.hists[lowName+"Norm"].GetNbinsX()+1):
            try:
                configMgr.hists[lowName+"Norm"].SetBinContent(iBin,  fabs((configMgr.hists[lowName+"Norm"].GetBinContent(iBin) / configMgr.hists[nomName].GetBinContent(iBin)) - 1.0) )
                configMgr.hists[lowName+"Norm"].SetBinError(iBin, 0.)
            except ZeroDivisionError:
                configMgr.hists[lowName+"Norm"].SetBinContent(iBin, 0.)
                configMgr.hists[lowName+"Norm"].SetBinError(iBin, 0.)

        for iBin in xrange(configMgr.hists[nomName+"Norm"].GetNbinsX()+1):
            try:
                configMgr.hists[nomName+"Norm"].SetBinContent(iBin,  max( configMgr.hists[highName+"Norm"].GetBinContent(iBin),  configMgr.hists[lowName+"Norm"].GetBinContent(iBin) )   )
                log.debug("!!!!!! shapeSys %s bin %g value %g" % (systName, iBin, configMgr.hists[nomName+"Norm"].GetBinContent(iBin)))
                configMgr.hists[nomName+"Norm"].SetBinError(iBin, 0.)
            except ZeroDivisionError:
                configMgr.hists[nomName+"Norm"].SetBinContent(iBin, 0.)
                configMgr.hists[nomName+"Norm"].SetBinError(iBin, 0.)
        if not systName in configMgr.systDict.keys():
            self.systList.append(systName)
        return


    def addShapeStat(self, systName, nomName, constraintType="Gaussian", statErrorThreshold=None):
        """
        Add a ShapeStat entry using the nominal histogram
        """
        configMgr.hists[nomName+"Norm"]  = configMgr.hists[nomName].Clone(nomName+"Norm")

        for iBin in xrange(configMgr.hists[nomName+"Norm"].GetNbinsX()+1):
            try:
                ratio = configMgr.hists[nomName].GetBinError(iBin) / configMgr.hists[nomName].GetBinContent(iBin)
                if (statErrorThreshold is not None) and (ratio<statErrorThreshold): ratio = 0.0   ## don't show if below threshold
                configMgr.hists[nomName+"Norm"].SetBinContent( iBin, ratio )
                configMgr.hists[nomName+"Norm"].SetBinError( iBin, 0. )
                log.debug("!!!!!! shapeStat %s bin %g value %g" % (systName, iBin, configMgr.hists[nomName+"Norm"].GetBinContent(iBin)) )
            except ZeroDivisionError:
                configMgr.hists[nomName+"Norm"].SetBinContent( iBin, 0. )
                configMgr.hists[nomName+"Norm"].SetBinError( iBin, 0.)
        if not systName in configMgr.systDict.keys():
            self.systList.append(systName)
        return


    def addOverallSys(self, systName, high, low):
        """
        Add an OverallSys entry using the high and low values
        """
        if high==1.0 and low==1.0:
            log.warning("    addOverallSys for %s high==1.0 and low==1.0. Systematic is removed from fit" % (systName))
            return

        if high==0.0 and low==0.0:
            log.warning("    addOverallSys for %s high=%g low=%g. Systematic is removed from fit." % (systName, systName, high, low))
            return

        if high==1.0 and low>0.0 and low!=1.0:
            highOld=high
            high = 2.0 - low
            log.warning("    addOverallSys: high=%f in %s. Taking symmetric value from low %f %f" % (highOld, systName, low, high))

        if low==1.0 and high>0.0 and high!=1.0:
            lowOld=low
            low = 2.0 - high
            log.warning("    addOverallSys: low=%f in %s. Taking symmetric value from high %f %f" % (lowOld, systName, low, high))

        if low<0.01:
            log.warning("    addOverallSys: low=%f is < 0.01 in %s. Setting to low=0.01. High=%f." % (low, systName, high))
            low = 0.01

        if high<0.01:
            log.warning("    addOverallSys: high=%f is < 0.01 in %s. Setting to high=0.01. Low=%f." % (high, systName, low))
            high = 0.01

        self.overallSystList.append((systName, high, low))
        if not systName in configMgr.systDict.keys():
            self.systList.append(systName)
        return

    def addNormFactor(self, name, val, high, low, const=False):
        """
        Add a normlization factor
        """
        self.normFactor.append( (name, val, high, low, const) )
        if not name in configMgr.normList:
            configMgr.normList.append(name)
        return

    def setNormFactor(self, name, val, low, high, const=False):
        """
        Set normalization factor
        """
        self.normFactor = []
        self.normFactor.append( (name, val, high, low, const) )
        if not name in configMgr.normList:
            configMgr.normList.append(name)
        return

    def setFileList(self, filelist):
        """
        Set file list for this Sample directly
        """
        self.files = filelist

    def setFile(self, file):
        """
        Set file for this Sample directly
        """
        self.files = [file]

    def propagateFileList(self,  fileList):
        """
        Propagate the file list downwards.
        """
        # if we don't have our own file list,  use the one given to us
        if self.files == []:
                self.files = fileList
        # we are the leaves of the configmgr->toplevelxml->channel->sample tree, 
        # so no propagation necessary

    def addShapeFactor(self, name):
        """
        Bin-by-bin factors to build histogram eg. for data-driven estimates
        """
        self.shapeFactorList.append(name)

    def addSystematic(self, syst):
        """
        Add a systematic to this Sample directly
        """
        if syst.name in self.systDict.keys():
            raise Exception("Attempt to overwrite systematic %s in Sample %s" % (syst.name, self.name))
        else:
            self.systDict[syst.name] = syst.Clone()
            return

    def getSystematic(self, systName):
        """
        Get systematic from internal storage
        """

        #protection against strange people who use getSystematic 
        # with the object they want to retrieve
        name = systName
        if(isinstance(systName, SystematicBase)):
            name = systName.name
        
        try:
            return self.systDict[name]
        except KeyError:
            log.warning("could not find systematic %s in sample %s" % (name, self.name))
        
        return

    def removeSystematic(self, systName):
        """
        Remove a systematic
        """

        # do we get a name or a Systematic passed?
        name = systName
        if(isinstance(systName, SystematicBase)):
            name = systName.name

        del self.systDict[name]

    def clearSystematics(self):
        """
        Remove a systematic
        """
        self.systDict.clear()
   
    def createHistFactoryObject(self):
        s = ROOT.RooStats.HistFactory.Sample(self.name, self.histoName, configMgr.histCacheFile)
        s.SetNormalizeByTheory(self.normByTheory)
        if self.statConfig:
            s.ActivateStatError()
        
        for histoSys in self.histoSystList:
            s.AddHistoSys(histoSys[0], histoSys[1], configMgr.histCacheFile, "", 
                                       histoSys[2], configMgr.histCacheFile, "")

        for shapeSys in self.shapeSystList:
            constraintType = ROOT.RooStats.HistFactory.Constraint.GetType(shapeSys[2])
            s.AddShapeSys(shapeSys[0], constraintType, shapeSys[1], configMgr.histCacheFile)

        for overallSys in self.overallSystList:
            s.AddOverallSys(overallSys[0], overallSys[2], overallSys[1])

        for shapeFact in self.shapeFactorList:
            s.AddShapeFactor(shapeFact)

        if len(self.normFactor) > 0:
            for normFactor in self.normFactor:
                s.AddNormFactor(normFactor[0], normFactor[1], normFactor[3], normFactor[2], normFactor[4])

        return s

    def __str__(self):
        """
        Convert instance to XML string
        """
        self.sampleString = "  <Sample Name=\"%s\" HistoName=\"%s\" InputFile=\"%s\" NormalizeByTheory=\"%s\">\n"  % (self.name, self.histoName, configMgr.histCacheFile, self.normByTheory)
        
        if self.statConfig:
            self.sampleString += "    <StatError Activate=\"%s\"/>\n" % (self.statConfig)
        
        for histoSyst in self.histoSystList:
            self.sampleString += "    <HistoSys Name=\"%s\" HistoNameHigh=\"%s\" HistoNameLow=\"%s\" />\n" % (histoSyst[0], histoSyst[1], histoSyst[2])
        
        for shapeSyst in self.shapeSystList:
            self.sampleString += "    <ShapeSys Name=\"%s\" HistoName=\"%s\" ConstraintType=\"%s\"/>\n" % (shapeSyst[0], shapeSyst[1], shapeSyst[2])
        
        for overallSyst in self.overallSystList:
            self.sampleString += "    <OverallSys Name=\"%s\" High=\"%g\" Low=\"%g\" />\n" % (overallSyst[0], float(overallSyst[1]), float(overallSyst[2]))
        
        for shapeFact in self.shapeFactorList:
            self.sampleString += "    <ShapeFactor Name=\"%s\" />\n" % (shapeFact)
        
        if len(self.normFactor)>0:
            for normFactor in self.normFactor:
                self.sampleString += "    <NormFactor Name=\"%s\" Val=\"%g\" High=\"%g\" Low=\"%g\" Const=\"%s\" />\n" % (normFactor[0], normFactor[1], normFactor[2], normFactor[3], normFactor[4])
                pass
        
        self.sampleString += "  </Sample>\n\n"
        return self.sampleString
