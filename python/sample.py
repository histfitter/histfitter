"""
 **********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : Sample                                                                *
 * Created: November 2012                                                         *
 *                                                                                *
 * Description:                                                                   *
 *      Class to define a sample                                                  *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************
"""

import ROOT
from ROOT import TFile, TMath, RooRandom, TH1, TH1F
from ROOT import kBlack, kWhite, kGray, kRed, kPink, kMagenta, kViolet, kBlue, kAzure, kCyan, kTeal, kGreen, kSpring, kYellow, kOrange, kDashed, kSolid, kDotted
from math import fabs
from logger import Logger
from systematic import SystematicBase

log = Logger('Sample')

TH1.SetDefaultSumw2(True)

from copy import deepcopy
from configManager import configMgr

class Sample(object):
    """
    Defines a Sample belonging to a Channel
    """

    def __init__(self, name, color=1):
        """
        Store configuration, set sample name, and if to normalize by theory

        Scales histograms to luminosity set in configuration

        @param name Name of the sample
        @param colour Colour of the sample used in before/after plotting
        """
        
        ## Name of the sample
        self.name = name
        ## Colour used in before/after fit plots
        self.color = color 
        ## Flag indicating whether the sample is data
        self.isData = False
        ## Flag indicating whether the sample is QCD
        self.isQCD = False
        ## Flag indicating whether the sample is a discovery sample
        self.isDiscovery = False
        self.write = True
        ## Normalise the sample to various regions or not
        self.normByTheory = False
        ## Use HistFactory statConfig for the channel
        self.statConfig = False
        ## Internal list of histogram-based systematics
        self.histoSystList = []
        ## Internal list of shape systematics
        self.shapeSystList = []
        ## Internal list of overall systematics
        self.overallSystList = []
        ## Internal list of shape factors
        self.shapeFactorList = []
        ## Internal list of all systematics
        self.systList = []
        ## Internal list of weights
        self.weights = []
        ## Internal list of sample-specific weights
        self.tempWeights = []
        ## Internal dictionary of systematics
        self.systDict = {}
        ## Internal list of normalisation factors
        self.normFactor = []
        self.qcdSyst = None
        ## Units used for the sample
        self.unit = "GeV"
        ## Dictionary of cuts placed on the sample in various regions
        self.cutsDict = {}
        ## List of input files
        self.files = []
        ## Name of input tree
        self.treeName = ""
        ## Nominal cross-section weight for signal samples
        self.xsecWeight = None
        ## +1 sigma variation of cross-section weight
        self.xsecUp = None
        ## -1 sigma variation of cross-section weight
        self.xsecDown = None
        ## List of regions to normalise the samples to
        self.normRegions = None
        ## Remap sample to another one in normalisation
        self.normSampleRemap = ''
        self.noRenormSys = True
        self.parentChannel = None
        self.allowRemapOfSyst = True
        self.mergeOverallSysSet = []

        if self.name[0].isdigit():
            log.warning("Sample name %s starts with a digit - this can confuse HistFactory internals" % self.name)

    def buildHisto(self, binValues, region, var, binLow=0.5, binWidth=1.):
        """
        Allow user to give bin values eg. for checking stats in papers

        @param binValues Values in the bins
        @param region Region to add the histogram to 
        @param var The variable to bin in
        @param binLow Lower bin edge (default 0.5)
        @param binWidth Widths of the bins (default 1.)	
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

        configMgr.hists[self.histoName] = TH1F(self.histoName, self.histoName, len(self.binValues[(region, var)]), binLow, float(len(self.binValues[(region, var)]))*binWidth+binLow)
        for (iBin, val) in enumerate(self.binValues[(region, var)]):
            configMgr.hists[self.histoName].SetBinContent(iBin+1, val)

        return

    def buildStatErrors(self, binStatErrors, region, var):
        """
        Allow user to give bin stat errors eg. for checking stats in papers
        
        @param binStatErrors Statistical errors for the bins
        @param region Region to add the errors to
        @param var The variable the region is binned in; 'cuts' for a cut-and-count analysis
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
        """
        Copy a the sample into a new instance
        """
        newInst = deepcopy(self)
        #for (key, val) in self.systDict.items():
        #    newInst.systDict[key] = val
        return newInst

    def setUnit(self, unit):
        """
        Set the units units for this sample

        @param unit String representing the unit
        """
        self.unit = unit
        return

    def setCutsDict(self, cutsDict):
        """
        Set cuts dictionary for the sample

        @param cutsDict A dictionary of regions to cuts
        """
        self.cutsDict = cutsDict
        return

    def setData(self, isData=True):
        """
        Flag the sample as a data sample

        @param isData A boolean indicating whether the sample contains data or not
        """
        self.isData = isData
        return

    def setWeights(self, weights):
        """
        Set the weights for this sample - overrides
        
        @param weights List of weights to set
        """
        self.weights = deepcopy(weights)
        return

    def addSampleSpecificWeight(self, weight):
        """
        Add a sample-specific weight to this sample

        @param weight The weight to append to the list of weights
        """
        if not weight in self.tempWeights:
            self.tempWeights.append(weight)
            ## MB : propagated to actual weights in configManager, after all
            ##      systematics have been added
        else:
            raise RuntimeError("Weight %s already defined for sample %s" % (weight, self.name))

    def addWeight(self, weight):
        """
        Add a weight to this sample and propagate

        @param weight The weight to append ot the various lists of weights. High/low values will be ignored if already present; if the nominal value is present, a RunTimeError is thrown.
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
        """
        Remove a weight from the sample and the associated systematics

        @param weight The weight to remove
        """
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
        """
        Set a flag that the sample is QCD

        @param isQCD A boolean
        @param qcdSyst A string to indicate the systematic
        """
        self.isQCD = isQCD
        self.qcdSyst = qcdSyst
        return

    def setDiscovery(self, isDiscovery=True):
        """
        Flag the sample as a discovery sample

        @param isDiscovery Boolean to set (default True)
        """
        self.isDiscovery = isDiscovery
        return

    def setNormByTheory(self, normByTheory=True):
        """
        Flag the sample as normalised by the luminosity

        @param normByTheory Boolean to set (default True)
        """
        self.normByTheory = normByTheory
        return

    def setStatConfig(self, statConfig):
        """
        Set the stat configuration for this sample (see HistFactory documentation)

        @param statConfig String to indicate the configuration 
        """
        self.statConfig = statConfig
        return

    def setWrite(self, write=True):
        self.write = write
        return

    def setHistoName(self, histoName):
        """
        Set the name of the nominal histogram for this sample
        
        @param histoName Name of the histogram
        """
        self.histoName = histoName
        return

    def setTreeName(self, treeName):
        """
        Set the tree name used for this sample

        @param treeName Name of the tree
        """
        self.treeName = treeName
        return

    def setNormRegions(self, normRegions):
        """
        Normalise the sample in various regions

        @param normRegions A list of regions used to constrain the sample normalisation
        """
        self.normRegions = normRegions
        self.noRenormSys = False
        return

    def propagateTreeName(self, treeName):
        """
        Propagate the tree name

        @param treeName The tree name to set and propagate down
        """
        if self.treeName == '':
            self.treeName = treeName
        # MAB: Propagate treeName down to systematics of sample
        #for (systName, systList) in self.systDict.items():
           #for syst in systList:
               #syst.propagateTreeName(self.treeName)
               #pass
        return

    def addHistoSys(self, systName, nomName, highName, lowName, includeOverallSys, normalizeSys, symmetrize=False, oneSide=False, samName="", normString="", nomSysName=""):
        """
        Add a HistoSys entry using the nominal,  high and low histograms,  set if to include OverallSys

        If includeOverallSys then extract scale factors

        If normalizeSys then normalize shapes to nominal

        @param systName Name of the systematic
        @param nomName Nominal name for the systematic
        @param highName Name of the +1sigma systematic value
        @param lowName Name of the -1sigma systematic value
        @param includeOverallSys Include an overallSys for the systematic uncertainty
        @param normalizeSys Normalize the systematic to the normRegions set through setNormRegions()
        @param symmetrize Boolean to indicate whether the low value has to be taken from the high value (default false)
        @param oneSide Boolean to indicate whether the uncertainty is one-sided (default False)
        @param samName Name of the sample
        @param normString String to append to the name of renormalised samples (default empty)
        @param nomSysName Name of the nominal systematic to generate high/low from (optional use (see source); default empty)
        """

        ### usecase of different tree from nominal histogram in case of 
        if len(nomSysName)>0:
            if configMgr.hists[nomSysName] != None:
                configMgr.hists[lowName+"_test"] = configMgr.hists[lowName].Clone(lowName+"_test")
                log.info(lowName + " / " + nomSysName)
                success = configMgr.hists[lowName].Divide( configMgr.hists[nomSysName] )
                if not success:
                    log.error( "Can not divide: " + lowName + " by " + nomSysName )
                    raise RuntimeError("Divide by zero.")
                else:
                    log.info(lowName + " * " + nomName)
                    configMgr.hists[lowName].Multiply( configMgr.hists[nomName] )
                    pass
                #
                configMgr.hists[highName+"_test"] = configMgr.hists[highName].Clone(highName+"_test")
                log.info(highName + " * " + nomSysName)
                success = configMgr.hists[highName].Divide( configMgr.hists[nomSysName] )
                if not success:
                    log.error( "Can not divide: " + highName + " by " + nomSysName )
                    raise RuntimeError("Divide by zero.")
                else:
                    log.info(highName + " * " + nomName)
                    configMgr.hists[highName].Multiply( configMgr.hists[nomName] )
                    pass

        if self.noRenormSys and normalizeSys:
            log.debug("    sample.noRenormSys==True and normalizeSys==True for sample <%s> and syst <%s>. normalizeSys set to False."%(self.name,systName))
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

        ## Three use-cases:
        ## 1. Normalized systematics over control regions, and all sub-cases (symmetrize, includeOverallSys)
        ## 2. includeOverallSys and not normalizeSys:
        ## 3. No renormalization, and no overall-systematics

        if normalizeSys:
            if not self.normRegions: 
                raise RuntimeError("Please specify normalization regions!")

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
            lowIntegral  = configMgr.hists["h"+samNameRemap+systName+"Low_"+normString+"Norm"].Integral()
            nomIntegral  = configMgr.hists["h"+samNameRemap+"Nom_"+normString+"Norm"].Integral()
            if len(nomSysName)>0:  ## renormalization done based on consistent set of trees
                if configMgr.hists[nomSysName] != None:
                    nomIntegral  = configMgr.hists["h"+samNameRemap+systName+"Nom_"+normString+"Norm"].Integral()
            
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

            configMgr.hists["%sNorm" % highName] = configMgr.hists[highName].Clone("%sNorm" % highName)
            configMgr.hists["%sNorm" % lowName] = configMgr.hists[lowName].Clone("%sNorm" % lowName)

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
                ## MB : avoid swapping of histograms, always pass high and nominal
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

            if symmetrize and not oneSide: ## symmetrize the systematic uncertainty
                nomIntegral = configMgr.hists[nomName].Integral()
                lowIntegral = configMgr.hists[lowName].Integral()
                highIntegral = configMgr.hists[highName].Integral()

                try:
                    high = highIntegral / nomIntegral
                    low = lowIntegral / nomIntegral
                except ZeroDivisionError:
                    log.error("    generating HistoSys for %s syst=%s nom=%g high=%g low=%g. Systematic is removed from fit." % (nomName, systName, nomIntegral, highIntegral, lowIntegral))
                    return

                if high<1.0 and 1.0 > low > 0.0:
                    log.warning("    addHistoSys: high=%f is < 1.0 in %s. Taking symmetric value from low %f %f"% (high, systName, low, 2.-low))
                    configMgr.hists[highName+"Norm"] = configMgr.hists[highName].Clone(highName+"Norm")
                    try:
                        configMgr.hists[highName+"Norm"].Scale((2.-low)/high)
                    except ZeroDivisionError:
                        log.error("    generating HistoSys for %s syst=%s nom=%g high=%g low=%g. Systematic is removed from fit." % (nomName, systName, nomIntegral, highIntegral, lowIntegral))
                        return
                    self.histoSystList.append((systName, highName+"Norm", lowName, configMgr.histCacheFile, "", "", "", ""))
                elif low>1.0 and high>1.0:
                    log.warning("    addHistoSys: low=%f is > 1.0 in %s. Taking symmetric value from high %f %f"% (low, systName, high, 2.-high))
                    configMgr.hists[lowName+"Norm"] = configMgr.hists[lowName].Clone(lowName+"Norm")
                    try:
                        configMgr.hists[lowName+"Norm"].Scale((2.-high)/low)
                    except ZeroDivisionError:
                        log.error("    generating HistoSys for %s syst=%s nom=%g high=%g low=%g. Systematic is removed from fit." % (nomName, systName, nomIntegral, highIntegral, lowIntegral))
                        return
                    self.histoSystList.append((systName, highName, lowName+"Norm", configMgr.histCacheFile, "", "", "", ""))
                elif low<0.:
                    log.warning("    addHistoSys: low=%f is < 0.0 in %s. Setting negative bins to 0.0."% (low, systName))
                    configMgr.hists[lowName+"Norm"] = configMgr.hists[lowName].Clone(lowName+"Norm")
                    for iBin in xrange(1, configMgr.hists[lowName+"Norm"].GetNbinsX()+1):
                        if configMgr.hists[lowName+"Norm"].GetBinContent(iBin) < 0.:
                            configMgr.hists[lowName+"Norm"].SetBinContent(iBin, 0.)
                    self.histoSystList.append((systName, highName, lowName+"Norm", configMgr.histCacheFile, "", "", "", ""))
                else:
                    self.histoSystList.append((systName, highName, lowName, configMgr.histCacheFile, "", "", "", ""))
            elif symmetrize and oneSide:
                # symmetrize one-side systematic, nothing else
                configMgr.hists[lowName] = configMgr.hists[nomName].Clone(lowName)
                configMgr.hists[lowName].Scale(2.0)
                configMgr.hists[lowName].Add(configMgr.hists[highName],  -1.0)

                for iBin in xrange(1, configMgr.hists[lowName].GetNbinsX()+1):
                    binVal = configMgr.hists[lowName].GetBinContent(iBin)
                    if binVal<0.:
                        configMgr.hists[lowName].SetBinContent(iBin, 0.)

                self.histoSystList.append((systName, highName, lowName, configMgr.histCacheFile, "", "", "", "")) 
            else: # default: don't do anything special
                self.histoSystList.append((systName, highName, lowName, configMgr.histCacheFile, "", "", "", ""))

        if not systName in configMgr.systDict.keys():
            self.systList.append(systName)
        return


    def addShapeSys(self, systName, nomName, highName, lowName, constraintType="Gaussian"):
        """
        Add a ShapeSys entry using the nominal,  high and low histograms

        @param systName Name of the systematic
        @param nomName Nominal name of the systematic
        @param highName Name of the systematic corresponding to +1sigma
        @param lowName Name of the systematic corresponding to -1sigma
        @param constraintType Type of the constraint in a string (default 'Gaussian')
        """

        highHistName = highName + "Norm"
        configMgr.hists[highHistName] = configMgr.hists[highName].Clone(highHistName)

        lowHistName = lowName + "Norm"
        configMgr.hists[lowHistName]  = configMgr.hists[lowName].Clone(lowHistName)

        nomHistName = nomName + "Norm"
        configMgr.hists[nomHistName]  = configMgr.hists[nomName].Clone(nomHistName)

        for iBin in xrange(configMgr.hists[highHistName].GetNbinsX()+1):
            try:
                configMgr.hists[highHistName].SetBinContent(iBin,  fabs((configMgr.hists[highHistName].GetBinContent(iBin) / configMgr.hists[nomName].GetBinContent(iBin)) - 1.0) )
                configMgr.hists[highHistName].SetBinError(iBin, 0.)
            except ZeroDivisionError:
                configMgr.hists[highHistName].SetBinContent(iBin, 0.)
                configMgr.hists[highHistName].SetBinError(iBin, 0.)

        for iBin in xrange(configMgr.hists[lowHistName].GetNbinsX()+1):
            try:
                configMgr.hists[lowHistName].SetBinContent(iBin,  fabs((configMgr.hists[lowHistName].GetBinContent(iBin) / configMgr.hists[nomName].GetBinContent(iBin)) - 1.0) )
                configMgr.hists[lowHistName].SetBinError(iBin, 0.)
            except ZeroDivisionError:
                configMgr.hists[lowHistName].SetBinContent(iBin, 0.)
                configMgr.hists[lowHistName].SetBinError(iBin, 0.)

        for iBin in xrange(configMgr.hists[nomHistName].GetNbinsX()+1):
            try:
                configMgr.hists[nomHistName].SetBinContent(iBin, max( configMgr.hists[highHistName].GetBinContent(iBin),
                                                                      configMgr.hists[lowHistName].GetBinContent(iBin)))
                log.debug("!!!!!! shapeSys %s bin %g value %g" % (systName, iBin, configMgr.hists[nomHistName].GetBinContent(iBin)))
                configMgr.hists[nomHistName].SetBinError(iBin, 0.)
            except ZeroDivisionError:
                configMgr.hists[nomHistName].SetBinContent(iBin, 0.)
                configMgr.hists[nomHistName].SetBinError(iBin, 0.)

        if not systName in configMgr.systDict.keys():
            self.systList.append(systName)

        return


    def addShapeStat(self, systName, nomName, constraintType="Gaussian", statErrorThreshold=None):
        """
        Add a ShapeStat entry using the nominal histogram

        @param systName Name of the systematic
        @param nomName Name of the nominal histogram for the systematic
        @param constraintType String indicating the type of costraint (default Gaussian)
        @param statErrorThreshold Optional threshold for size of the error; any bins for which the error is below this ratio are ignored
        """
        histName = nomName + "Norm"
        configMgr.hists[histName]  = configMgr.hists[nomName].Clone(histName)

        for iBin in xrange(configMgr.hists[histName].GetNbinsX()+1):
            try:
                ratio = configMgr.hists[nomName].GetBinError(iBin) / configMgr.hists[nomName].GetBinContent(iBin)
                if (statErrorThreshold is not None) and (ratio<statErrorThreshold): 
                    log.info( "shapeStat %s bin %g value %g, below threshold of: %g. Will ignore." % (systName, iBin, ratio, statErrorThreshold) )
                    ratio = 0.0   ## don't show if below threshold
                configMgr.hists[histName].SetBinContent( iBin, ratio )
                configMgr.hists[histName].SetBinError( iBin, 0. )
                log.debug("!!!!!! shapeStat %s bin %g value %g" % (systName, iBin, configMgr.hists[histName].GetBinContent(iBin)) )
            except ZeroDivisionError:
                configMgr.hists[histName].SetBinContent( iBin, 0. )
                configMgr.hists[histName].SetBinError( iBin, 0.)
        if not systName in configMgr.systDict.keys():
            self.systList.append(systName)
        return


    def addOverallSys(self, systName, high, low):
        """
        Add an OverallSys entry using the high and low values
        
        @param systName Name of the systematic
        @param high Value at +1sigma
        @param low Value at -1sigma
        """
        if high==1.0 and low==1.0:
            log.warning("    addOverallSys for %s high==1.0 and low==1.0. Systematic is removed from fit" % systName)
            return

        if high==0.0 and low==0.0:
            log.warning("    addOverallSys for %s high=%g low=%g. Systematic is removed from fit." % (systName, high, low))
            return

        if high==low:
            low = 2.0 - high
            log.error("    addOverallSys '%s' has invalid inputs: high==low==%.3f.\n    This would result in error=(high-low)/(high+low)=0, silently cancelled by HistFactory.\n    Please fix your user configuration.\n    For now, will recover by symmetrizing error: high=%.3f low=%.3f."%(systName,high,high,low))

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
        Add a normalization factor

        @param name Name of normalisation factor
        @param val Nominal value
        @param high Value at +1sigma
        @param low Value at -1sigma
        @param const Boolean that indicates whether the factor is constant or not
        """
        self.normFactor.append( (name, val, high, low, const) )
        if not name in configMgr.normList:
            configMgr.normList.append(name)
        return

    def setNormFactor(self, name, val, low, high, const=False):
        """
        Set normalization factor
        
        @param name Name of normalisation factor
        @param val Nominal value
        @param high Value at +1sigma
        @param low Value at -1sigma
        @param const Boolean that indicates whether the factor is constant or not
        """
        self.normFactor = []
        self.normFactor.append( (name, val, high, low, const) )
        if not name in configMgr.normList:
            configMgr.normList.append(name)
        return

    def setFileList(self, filelist):
        """
        Set file list for this Sample directly

        @param filelist A list of filenames
        """
        self.files = filelist

    def setFile(self, file):
        """
        Set file for this Sample directly

        @param file a filename
        """
        self.files = [file]

    def propagateFileList(self,  fileList):
        """
        Propagate the file list downwards.
        
        @param filelist A list of filenames
        """
        # if we don't have our own file list,  use the one given to us
        if not self.files:
            self.files = fileList
        # we are the leaves of the configMgr->fitConfig->channel->sample tree,
        # so no propagation necessary

    def addShapeFactor(self, name):
        """
        Bin-by-bin factors to build histogram eg. for data-driven estimates

        @param name Name of the shape factor
        """
        self.shapeFactorList.append(name)

    def addSystematic(self, syst):
        """
        Add a systematic to this Sample directly. Will not overwrite existing systematics.

        @param syst An object of type Systematic
        """
        if syst.name in self.systDict.keys():
            raise Exception("Attempt to overwrite systematic %s in Sample %s" % (syst.name, self.name))
        else:
            self.systDict[syst.name] = syst.Clone()
            return

    def getOverallSys(self, name):
        """
        Get overall systematic by name

        @param name Name of the systematic to return
        """
        for syst in self.overallSystList:
            if name == syst[0]: return syst
        return None

    def replaceOverallSys(self, rsyst):
        """
        Replace overall systematic based on name. If no systematic of the name exists, nothing is replaced.

        @param rsyst Systematic object to replace the systematic with the same name
        """
        for idx in xrange(len(self.overallSystList)):
            syst = self.overallSystList[idx]
            if rsyst[0]==syst[0]:
                self.overallSystList[idx] = rsyst
                return

    def getHistoSys(self, name):
        """
        Return the systematic associated to the name

        @param name Name of the histoSys systematic
        """
        for syst in self.histoSystList:
            if name==syst[0]: return syst
        return None

    def replaceHistoSys(self, rsyst):
        """
        Replace histo systematic based on name. If no systematic of the name exists, nothing is replaced.

        @param rsyst Systematic object to replace the systematic with the same name
        """
        for idx in xrange(len(self.histoSystList)):
            syst = self.histoSystList[idx]
            if rsyst[0]==syst[0]:
                self.histoSystList[idx] = rsyst
                return

    def removeOverallSys(self, systName):
        """
        Remove overall systematic

        @param systName Name of the overall systematic to remove
        """
        for idx in xrange(len(self.overallSystList)):
            syst = self.overallSystList[idx]
            if systName==syst[0]:
                del self.overallSystList[idx]
                self.removeSystematic(systName)
                return

    def getSystematic(self, systName):
        """
        Get systematic from internal storage

        @param systName Name of the systematic to return
        """

        # protection against strange people who use getSystematic 
        # with the object they want to retrieve
        name = systName
        if isinstance(systName, SystematicBase):
            name = systName.name
        try:
            return self.systDict[name]
        except KeyError:
            log.warning("could not find systematic %s in sample %s" % (name, self.name))
        
        return

    def removeSystematic(self, systName):
        """
        Remove a systematic
        
        @param systName Name of the systematic to remove
        """
        # do we get a name or a Systematic passed?
        name = systName
        if isinstance(systName, SystematicBase):
            name = systName.name

        del self.systDict[name]

    def clearSystematics(self):
        """
        Remove all systematics from the sample
        """
        self.systDict.clear()
  
    # TODO: it would be nice to change the internal lists to dictionaries instead of arrays in a next iteration
    def createHistFactoryObject(self):
        """
        Construct the HistFactory object for this sample
        """
        s = ROOT.RooStats.HistFactory.Sample(self.name, self.histoName, configMgr.histCacheFile)
        s.SetNormalizeByTheory(self.normByTheory)
        if self.statConfig:
            s.ActivateStatError()
       
        #high = 1, low = 2
        for histoSys in self.histoSystList:
            s.AddHistoSys(histoSys[0], histoSys[2], configMgr.histCacheFile, "", 
                                       histoSys[1], configMgr.histCacheFile, "")

        for shapeSys in self.shapeSystList:
            constraintType = ROOT.RooStats.HistFactory.Constraint.GetType(shapeSys[2])
            s.AddShapeSys(shapeSys[0], constraintType, shapeSys[1], configMgr.histCacheFile)

        # high = 1, low = 2
        for overallSys in self.overallSystList:
            s.AddOverallSys(overallSys[0], overallSys[2], overallSys[1])

        for shapeFact in self.shapeFactorList:
            s.AddShapeFactor(shapeFact)

        # high = 2, low = 3
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
            self.sampleString += "    <StatError Activate=\"%s\"/>\n" % self.statConfig
        
        for histoSyst in self.histoSystList:
            self.sampleString += "    <HistoSys Name=\"%s\" HistoNameHigh=\"%s\" HistoNameLow=\"%s\" />\n" % (histoSyst[0], histoSyst[1], histoSyst[2])
        
        for shapeSyst in self.shapeSystList:
            self.sampleString += "    <ShapeSys Name=\"%s\" HistoName=\"%s\" ConstraintType=\"%s\"/>\n" % (shapeSyst[0], shapeSyst[1], shapeSyst[2])
        
        for overallSyst in self.overallSystList:
            self.sampleString += "    <OverallSys Name=\"%s\" High=\"%g\" Low=\"%g\" />\n" % (overallSyst[0], float(overallSyst[1]), float(overallSyst[2]))
        
        for shapeFact in self.shapeFactorList:
            self.sampleString += "    <ShapeFactor Name=\"%s\" />\n" % shapeFact
        
        if len(self.normFactor)>0:
            for normFactor in self.normFactor:
                self.sampleString += "    <NormFactor Name=\"%s\" Val=\"%g\" High=\"%g\" Low=\"%g\" Const=\"%s\" />\n" % (normFactor[0], normFactor[1], normFactor[2], normFactor[3], normFactor[4])
                pass
        
        self.sampleString += "  </Sample>\n\n"
        return self.sampleString
