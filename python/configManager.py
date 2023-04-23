"""
 **********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : ConfigManager                                                         *
 * Created: November 2012                                                         *
 *                                                                                *
 * Description:                                                                   *
 *      Class to define a config-manager (singleton class) that manages           *
 *        fitConfig instances. Has a C++ counter-part.                            *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************
"""

from ROOT import THStack, TLegend, TCanvas, TFile, std, TH1D, TH2D, gStyle
from ROOT import ConfigMgr, FitConfig, ChannelStyle #this module comes from gSystem.Load("libSusyFitter.so")
from ROOT import gROOT, TObject, TProof
from prepareHistos import PrepareHistos
from copy import copy, deepcopy
from histogramsManager import histMgr
from logger import Logger
from math import sqrt

from inputTree import InputTree

import os
import sys

gROOT.SetBatch(True)
log = Logger('ConfigManager')

def mkdir_p(path):
    """
    Equivalent of mkdir -p on the commandline; wrapper around os.makedirs

    @param path The path to create
    """
    try:
        os.makedirs(path)
    except:
        pass

def replaceSymbols(s):
    """
    Strip a string from /, *, (, ), [, ], - and ,

    @param s The string to remove the symbols from
    """
    s = s.replace("/","").replace("*","").replace("(","").replace(")","").replace("[", "_").replace("]","_").replace("-", "_").replace(",", "_")
    return s
    
def enum(typename, field_names):
    """
    Create a new enumeration type
    
    @param typename Type to use for the enum
    @param field_names Names of the fields to create
    """

    if isinstance(field_names, str):
        field_names = field_names.replace(',', ' ').split()
    d = dict((reversed(nv) for nv in enumerate(field_names)), __slots__ = ())
    return type(typename, (object,), d)()    

class ConfigManager:
    """
    Singleton manager class to store the configuration information
    """
    _instance = None

    def __new__(cls,*args,**kwargs):
        """
        Make singleton by only instanciating once
        """
        if not cls._instance:
            cls._instance = super().__new__(cls,*args,**kwargs)
        else:
            raise Exception("Only one instance allowed")

        return cls._instance

    def __init__(self):
        """
        Configuration variables
        """
        self.analysisName = None # Name to give the analysis
        self.nomName = "" # suffix of nominal trees names
        self.cppMgr = ConfigMgr.getInstance() #C++ alter ego of this configManager
        self.userArg="" #arbitrary user-defined string configurable from command line (-u) and usable freely

        self.inputLumi = None # Luminosity of input histograms
        self.outputLumi = None # Output luminosity
        self.lumiUnits = 1.0 # 1=fb-1, 1000=pb-1, etc.
        self.energy = '13.6 TeV' # center-of-mass energy, to be used in plots
        self.nTOYs =- 1 #<=0 means to use real data
        self.nCPUs = 1 # number of CPUs used for toy simulation
        self.calculatorType = 0 # frequentist calculator
        self.testStatType = 3   # one-sided test statistic
        self.useCLs = True # use CLs for upper limits, or not
        self.doExclusion = True # true = exclusion, false = discovery test
        self.fixSigXSec = False # true = fix SigXSec by nominal, +/-1sigma
        self.runOnlyNominalXSec = False #t true = for fixed xsec, run only nominal fit and not +/- 1 sigma fits
        self.nPoints = 20 # number of points in upper limit evaluation
        self.disableULRangeExtension = False # disable the UL range extender
        self.seed = 0 # seed for random generator. default is clock
        self.muValGen = 0.0 # mu_sig used for toy generation
        self.toySeedSet = False # Set the seed for toys
        self.toySeed = 0 # CPU clock, default
        self.useAsimovSet = False # Use the Asimov dataset
        self.generateAsimovDataForObserved = False # Generate Asimov data as obsData for UL
        self.blindSR = False # Blind the SRs only
        self.blindCR = False # Blind the CRs only
        self.blindVR = False # Blind the VRs only
        self.useSignalInBlindedData = False # Add signal MC on top when building blinded data histogram in SR
        self.keepSignalRegionType = False # Force SR to always remain an SR and no autochanging to VR
        self.FitType = enum('FitType','Discovery , Exclusion , Background') # to distinguish between background, exclusion and discovery fit
        self.myFitType = None #propagted from HistFitter.py
        self.scanRange = None # possibility to define a scan range with a tuple (min, max) (when the first fit fails)
        self.autoScan = False # use automatic determination of scan range for UL
        self.normList = [] # List of normalization factors
        self.outputFileName = None # Output file name used to store fit results
        self.stackList = [] # List of stacks for plotting
        self.canvasList = [] # List of canvases for plotting
        self.qcdList = []
        self.weights = [] # List of weights
        self.weightsQCD = [] # List of QCD weights
        self.weightsQCDWithB = [] # List of QCD weights if there is a b-jet selection

        self.systDict = {} # Dictionary mapping systematic name to tuple of isTree and high/low
        self.cutsDict = {} # Dictionary mapping region names to cut strings
        self.histoDict = {} # Dictionary mapping histogram names to histograms
        self.hists = {} # Instances of all histograms in memory
        self.chains = {} # Instances of all trees in memory
        self.friend_chains = {} # Instances of all friend trees in memory

        self.includeOverallSys = True # Boolean to chose if HistoSys should also have OverallSys
        self.readFromTree = False # Boolean to chose if reading histograms from tree will also write to file
        self.plotHistos = None # Boolean to chose to plot out the histograms
        self.plotStacked = True # Boolean to choose to do stacked before/after plots, or just individual histograms
        self.storeSinglePlotFiles = True # Boolean to choose to store single files for each before/after plot
        self.storeMergedPlotFile = False # Boolean to choose to store a central file for all before/after plots
        self.plotRatio="ratio" #Pass to cppMgr to configure drawing options: "ratio", "pull", "none"
        self.removeEmptyBins = False # Boolean to chose to remove empty bins from data histogram on plot
        self.executeHistFactory = True # Boolean to chose to execute HistFactory
        self.writeXML = True # Boolean to chose whether to write HistFactory XML files by hand
        self.printHistoNames = False # Print out the names of generated histograms
        self.doHypoTest = False
        self.doDiscoveryHypoTest = False
        self.ReduceCorrMatrix = False # Boolean to make a reduced correlation matrix
        self.prun = False
        self.prunThreshold = 0.01
        self.prunMethod = 2 # method 1: chi2 test for histoSys, method 2: comparison of yields in every histogram bin for histoSys. Method 2 takes the prunThreshold. Method 1 uses defines a p-value of below 5% as not fitting

        self.fitConfigs = [] # fitConfig object
        self.prepare = None # PrepareHistos object

        self.histCacheFile = ""
        self.histBackupCacheFile = ""
        self.useCacheToTreeFallback = False
        self.useHistBackupCacheFile = False
        self.forceNorm = True #Force building of normalized histograms
        self.minValue = 0.0001
        
        self.input_files = set() # Input list to be used for tree production
       
        self.deactivateBinnedLikelihood = False # Deactive the use of binned likelihoods in RooStats? 

        self.ignoreSystematics = False # Turn off systematics?

        self.bkgParName = ''
        self.bkgCorrVal = -1.

        self.rebin = False # Automatically rebin histograms into proxy histograms with edged [0, 1, ..., N]
        return

    def setLumiUnits(self,unit):
        """
        Set units for integretaed luminosity to use

        @param unit The unit: fb, pb, fb-1 or pb-1 (fb and pb are automatically treated as inverse)
        """
        # 1=fb-1, 1000=pb-1, etc.
        if unit == "fb-1" or unit == "fb":
            self.lumiUnits = 1.0
        elif unit == "pb-1" or unit == "pb":
            self.lumiUnits = 1000.0
        else:
            raise TypeError("lumi unit '%s' is not supported."%unit)
        return

    def addTopLevelXML(self, input, name=""):
        """
        @deprecated Deprecated method; use addFitConfig
        """

        log.warning("addTopLevelXML() is deprecated and has been renamed addFitConfig()")
        return self.addFitConfig(input, name)

    def addFitConfig(self, input, name=""):
        """
        Add a fit configuration to this configManager

        @param input The configuration to add
        @param name The name for the fit configuration
        """
        
        from fitConfig import fitConfig
        if len(name) > 0:
            newName = name
        elif isinstance(input, str):
            newName = input
        elif isinstance(input, fitConfig):
            newName = input.name
        else:
            raise RuntimeError("Logic error in addFitConfig")

        # check that newName is not already used
        for tl in self.fitConfigs:
            if tl.name == newName:
                raise RuntimeError("fitConfig %s already exists in configManager. Please use a different name." %
                                   newName )
            pass

        # create new fitConfig object and return reference
        if isinstance(input, fitConfig):
            newFitConfig = input.Clone(newName)
        else:
            newFitConfig = fitConfig(newName)
            pass

        newFitConfig.setWeights(self.weights)
        newFitConfig.removeEmptyBins = self.removeEmptyBins

        self.fitConfigs.append(newFitConfig)
        log.info(f"Created fitConfig: {newName}")
        
        log.debug(f"Appending existing files to fit configuration {newName}")
        for i in self.input_files:
            newFitConfig.addInput(i.filename, i.treename)

        return self.fitConfigs[-1]

    def addInput(self, filename, treename):
        # add an input with a treename
        self.input_files.add(InputTree(filename, treename))
       
        for fitConfig in self.fitConfigs:
            fitConfig.addInput(filename, treename)

    def addInputs(self, filenames, treename):
        # bulk add a bunch of filenames with the same treename
        for f in filenames:
            self.addInput(f, treename)

    def addTopLevelXMLClone(self, obj, name):
        """
        @deprecated Deprecated in favour of addFitConfigClone()
        """
        log.warning("addTopLevelXMLClone() has been deprecated and is now addFitConfigClone()")
        return self.addFitConfigClone(obj, name)

    def addFitConfigClone(self, obj, name):
        """
        Add a clone of a fit configuration

        @param obj The configuration to clone
        @param name The name for the new configuration
        """
        return self.addFitConfig(obj, name)

    def removeTopLevelXML(self, name):
        """
        @deprecated Deprecated in favour of removeFitConfig()
        """
        log.warning("removeTopLevelXML() has been deprecated and is now removeFitConfig()")
        self.removeFitConfig(name)
        return

    def removeFitConfig(self, name):
        """
        Remove fit configuration

        @param name Name of the configuration to remove
        """
        for i in range(0,len(self.fitConfigs)):
            tl = self.fitConfigs[i]
            if tl.name == name:
                self.fitConfigs.pop(i)
                return
        log.warning("fitConfig named '%s' does not exist. Cannot be removed." % name)
        return

    def getTopLevelXML(self, name):
        """
        Deprecated in favour of getFitConfig()
        """
        log.warning("getTopLevelXML() has been deprecated and is now getFitConfig()")
        return self.getFitConfig(name)

    def getFitConfig(self, name):
        """
        Find a fit configuration by name

        @param name Name of the configuration to find
        """
        for tl in self.fitConfigs:
            if tl.name == name:
                return tl
        log.warning("fitConfig named '%s' does not exist. Cannot be returned." % name)
        return 0

    def initializePythonObjects(self):
        # Propagate stuff down from config manager
        log.info("  -initialize python objects...")
        for tl in self.fitConfigs:
            tl.initialize()
            for chan in tl.channels:
                chan.initialize()
                for sam in chan.sampleList:
                    if not sam.isData and not sam.isQCD and not sam.isDiscovery:
                        pass
                        for (name,syst) in list(self.systDict.items()):
                            if not name in list(chan.getSample(sam.name).systDict.keys()):
                                chan.getSample(sam.name).addSystematic(syst)
                        ## MB: sample-specific weights (for example cuts)
                        ##     Make sure these weights propagate down to actual sample and systematics
                        for w in sam.tempWeights: sam.addWeight(w) 
                    elif sam.isQCD or sam.isData:
                        chan.getSample(sam.name).setWrite(False)

    def setCacheFilename(self):
        if self.histCacheFile == '':
            tmpName = "data/%s.root" % self.analysisName
            log.info("Giving default name histCacheFile: %s" % tmpName)
            self.histCacheFile = tmpName
            pass

    def setLumi(self):
        if self.inputLumi is None and self.outputLumi is None:
            self.inputLumi = 1.0
            self.outputLumi = 1.0
            pass

    def initializeHistograms(self):
        log.info("  -initialize global histogram dictionary...")
        for tl in self.fitConfigs:
            for channel in tl.channels:
                for sam in channel.sampleList:
                    regString = "".join(channel.regions)

                    nomName = sam.getHistogramName(tl)
                        
                    if sam.isData:
                        _name = sam.getHistogramName(tl)
                        if not _name in self.hists:
                            self.hists[_name] = None

                    elif sam.isQCD:
                        highName = sam.getHistogramName(tl, variation="High")
                        lowName = sam.getHistogramName(tl, variation="Low")

                        systName = f"h{sam.name}Syst_{regString}_obs_{replaceSymbols(channel.variableName)}"
                        statName = f"h{sam.name}Stat_{regString}_obs_{replaceSymbols(channel.variableName)}"

                        if not nomName in self.hists:
                            self.hists[nomName] = None

                        if not highName in self.hists:
                            self.hists[highName] = None

                        if not lowName in self.hists:
                            self.hists[lowName] = None

                        if not systName in self.hists:
                            self.hists[systName] = None

                        if not statName in self.hists:
                            self.hists[statName] = None

                        if channel.variableName == "cuts":
                            nHists = len(channel.regions)
                        else:
                            nHists = channel.nBins

                        for iBin in range(1, nHists+1):
                            if not f"{nomName}_{str(iBin)}" in self.hists:
                                self.hists[f"{nomName}_{str(iBin)}"] = None

                            if not f"{highName}_{str(iBin)}" in self.hists:
                                self.hists[f"{highName}_{str(iBin)}"] = None

                            if not f"{lowName}_{str(iBin)}" in self.hists:
                                self.hists[f"{lowName}_{str(iBin)}"] = None

                    elif not sam.isDiscovery:
                        if not nomName in self.hists:
                            self.hists[nomName] = None

                        # Build for all the systematic variations by looping over a generator object
                        for name in sam.getAllHistogramNamesForSystematics(tl):
                            if name in self.hists: continue
                            self.hists[name] = None

        return

    
    def initializeHistoPrepareObjectFromTrees(self):
        """
        Initialize the internal tree-to-histogram method
        """
        log.info("  -build PrepareHistos() for trees...")
        self.prepare = PrepareHistos(False)
        if self.plotHistos is None:    # set plotHistos if not already set by user
            self.plotHistos = False    # this is essentially for debugging
        return

    def initializeHistoPrepareObjectFromHistograms(self):
        """
        Initialize the reading from histograms
        """
        if self.useCacheToTreeFallback:
            log.info("  -build PrepareHistos() for cache, with fallback to trees...")
            self.prepare = PrepareHistos(True, True)
        else:
            log.info("  -build PrepareHistos() for cache...")
            self.prepare = PrepareHistos(True)

        if self.useHistBackupCacheFile:
            self.prepare.setHistoPaths(self.histCacheFile, self.histBackupCacheFile)
        else:
            self.prepare.setHistoPaths(self.histCacheFile)

        return
    
    def initializeHistoPrepareObject(self):
        """
        Initialize the inputdata-to-histograms builder
        """
        if self.readFromTree:
            self.initializeHistoPrepareObjectFromTrees()
        else:
            self.initializeHistoPrepareObjectFromHistograms()

        return

    def checkSignalRegionType(self):
        """
        Change the SRs to VRs in case of a background only fit - unless you overrule it
        """
        if self.doHypoTest or self.doDiscoveryHypoTest:
            # Running a hypothesis test - SRs needed
            return

        if self.myFitType != self.FitType.Background:
            # Not a background fit. Must be on purpose.
            return
        
        if self.keepSignalRegionType:
            # User wants to keep the SR
            return

        log.warning("Detected a background-only fit - will change your SRs to become VRs")
        log.info("(Change this behaviour by setting configMgr.keepSignalRegionType = True)")

        for fc in self.fitConfigs:
            SRs = fc.signalChannels
            fc.signalChannels = []

            # Check whether we're blinded for VR; if so, blind the SRs
            if self.blindSR:
                log.info("Running with blindSR - blinding the new VRs individually")
                for r in SRs:
                    log.debug(f"Blinded region {r}")
                    fc.getChannelByChannelName(r).blind = True
             
            # Now add them as validation channels 
            fc.addValidationChannels(SRs)
        return

    def initialize(self):
        """
        Initializes the configuration manager by propagating setting down to channels, samples, etc.
        """
        
        log.info("Initializing...")
        
        # Set various output settings & lumi
        self.setCacheFilename()
        self.setLumi()
       
        # Check if we want to change the SRs to VRs
        self.checkSignalRegionType()

        # Initialize the histogram bookkeeping; their reader; and our C++ counterpart
        self.initializePythonObjects()
        self.initializeHistograms()
        self.initializeHistoPrepareObject()
        self.initializeCppMgr()

        ## Propagate the relevant settings down
        #self.propagateInputFiles() 
        #self.propagateTreeName()

        # Summary
        self.Print() 
        return

    def initializeCppMgr(self):
        """
        Initialise the C++ side copy of the configuration manager and set its properties
        """

        log.info("  -initialize C++ mgr...")

        # settings for hypothesis test
        self.cppMgr.m_doHypoTest = self.doHypoTest
        self.cppMgr.m_doDiscoveryHypoTest = self.doDiscoveryHypoTest
        self.cppMgr.setNToys( self.nTOYs )
        self.cppMgr.setNCPUs( self.nCPUs )
        self.cppMgr.setCalcType( self.calculatorType )# frequentist calculator
        self.cppMgr.setTestStatType( self.testStatType )  # one-sided test statistic
        self.cppMgr.setCLs( self.useCLs )
        self.cppMgr.setExclusion( self.doExclusion )
        self.cppMgr.setfixSigXSec( self.fixSigXSec )
        self.cppMgr.setRunOnlyNominalXSec( self.runOnlyNominalXSec )
        self.cppMgr.setNPoints( self.nPoints )
        self.cppMgr.setDisableULRangeExtension( self.disableULRangeExtension )
        self.cppMgr.setSeed( self.toySeed )
        self.cppMgr.setMuValGen( self.muValGen )
        self.cppMgr.setUseAsimovSet( self.useAsimovSet)
        self.cppMgr.m_plotRatio = self.plotRatio

        self.cppMgr.m_deactivateBinnedLikelihood = self.deactivateBinnedLikelihood
        self.cppMgr.m_generateAsimovDataForObserved = self.generateAsimovDataForObserved

        if self.outputFileName:
            self.cppMgr.m_outputFileName = self.outputFileName
            self.cppMgr.m_saveTree=True
            
        if self.scanRange:
            self.cppMgr.setScanRange(True, self.scanRange[0], self.scanRange[1])
        else:
            self.cppMgr.setScanRange(False)

        if self.autoScan and self.scanRange:
            log.warning("Do not set a scan range if you want to use auto scan for the UL.")
            self.cppMgr.setAutoScan(False)
        elif self.autoScan:
            self.cppMgr.setAutoScan(True)
        else:
            self.cppMgr.setAutoScan(False)

        # Fill FitConfigs from TopLevelXMLs
        for fc in self.fitConfigs:
            cppFC = self.cppMgr.addFitConfig(fc.name)
            cppFC.m_inputWorkspaceFileName = fc.wsFileName
            cppFC.m_Lumi = self.lumiUnits*self.outputLumi
            cppFC.m_hypoTestName = fc.hypoTestName
            if not fc.signalSample is None:
                cppFC.m_signalSampleName = fc.signalSample
     
            # CR/SR/VR channels
            for cName in fc.signalChannels:
                cppFC.m_signalChannels.push_back(cName)
            for cName in fc.validationChannels:
                cppFC.m_validationChannels.push_back(cName)
            for cName in fc.bkgConstrainChannels:
                cppFC.m_bkgConstrainChannels.push_back(cName)
       
            # Plot cosmetics per channel
            for c in fc.channels:
                 style = ChannelStyle(c.channelName)
                 style.setNBins(c.nBins)
                 if not c.title is None:
                     style.setTitle(c.title)     
                 if not c.minY is None:
                    style.setMinY(c.minY)
                 if not c.maxY is None:
                   style.setMaxY(c.maxY)
                 if not c.titleX is None:
                     style.setTitleX(c.titleX)
                 if not c.titleY is None:
                     style.setTitleY(c.titleY)
                 if not c.logY is None:
                     style.setLogY(c.logY)
                 if not c.ATLASLabelX is None:
                     style.setATLASLabelX(c.ATLASLabelX)
                 if not c.ATLASLabelY is None:
                     style.setATLASLabelY(c.ATLASLabelY)
                 if not c.ATLASLabelX is None:
                     style.setATLASLabelText(c.ATLASLabelText)
                 if not c.showLumi is None:
                     style.setShowLumi(c.showLumi)     
                 if not self.outputLumi is None:
                     if c.lumi is None:
                         style.setLumi(self.outputLumi)
                     else: style.setLumi(c.lumi)
                     style.setEnergy(self.energy)
                 if not c.lumiX is None:
                     style.setLumiX(c.lumiX)
                 if not c.lumiY is None:
                     style.setLumiY(c.lumiY)
                 if not c.xErrorSize is None:
                     style.setXErrorSize(c.xErrorSize)
                 if not c.integerStyle is None:
                     style.setIntegerStyle(c.integerStyle)
                 if not c.regionLabelX is None:
                     style.setRegionLabelX(c.regionLabelX)
                 if not c.regionLabelY is None:
                     style.setRegionLabelY(c.regionLabelY)
                 if not c.regionLabelText is None:
                     style.setRegionLabelText(c.regionLabelText)
                 if not c.arrowX is None:
                     style.setArrowX(c.arrowX)
                 if not c.arrowY is None:
                     style.setArrowY(c.arrowY)
                 if not c.arrowEnd is None:
                     style.setArrowEnd(c.arrowEnd)
                 if not c.arrowAngle is None:
                     style.setArrowAngle(c.arrowAngle)
                 if not c.arrowWidth is None:
                     style.setArrowWidth(c.arrowWidth)
                 if not c.arrowColor is None:
                     style.setArrowColor(c.arrowColor)
                 if not c.arrowRatio is None:
                     style.setArrowRatio(c.arrowRatio)
                 if len(c.text1)>0:
                     style.setText1(c.text1)
                 if len(c.text2)>0:
                     style.setText2(c.text2)
                 style.setTextSize1(c.textsize1)
                 style.setTextSize2(c.textsize2)

                 # Plot cosmetics per fitConfig 
                 style.setDataColor(fc.dataColor)
                 style.setTotalPdfColor(fc.totalPdfColor)
                 style.setErrorLineColor(fc.errorLineColor)
                 style.setErrorLineStyle(fc.errorLineStyle)
                 style.setErrorFillColor(fc.errorFillColor)
                 style.setErrorFillStyle(fc.errorFillStyle)
                 style.setRemoveEmptyBins(self.removeEmptyBins)
                 if not fc.tLegend is None:
                     style.setTLegend(fc.tLegend)

                 # Sample name and color
                 for s in c.sampleList:
                     style.addSample(s.name, s.color)
                     #style.m_sampleNames.push_back(s.name)
                     #style.m_sampleColors.push_back(s.color)

                 # add channel and style for channel to C++ FitConfig (these two are expected to be synchronous
                 cppFC.m_channels.push_back(c.channelName)
                 cppFC.m_channelsStyle.push_back(style)
                 
        self.cppMgr.checkConsistency()
        self.cppMgr.initialize()
        return

    def Print(self):
        """
        Print a summary of the settings defined in this configuration manager
        """

        log.info("*-------------------------------------------------*")
        log.info("              Summary of ConfigMgr\n")
        log.info("analysisName: %s" % self.analysisName)
        log.info("cache file: %s" % self.histCacheFile)
        log.info("output file: %s" % self.outputFileName)
        log.info("write own XML: %s" % self.writeXML)
        log.info("nomName: %s" % self.nomName)
        log.info("inputLumi: %.3f" % self.inputLumi)
        log.info("outputLumi: %.3f" % self.outputLumi)
        log.info("nTOYs: %i" % self.nTOYs)
        log.info("doHypoTest: %s" % self.doHypoTest)
        log.info("doDiscoveryHypoTest: %s" % self.doDiscoveryHypoTest)
        log.info("fixSigXSec: %s" % self.fixSigXSec)
        log.info("runOnlyNominalXSec: %s" % self.runOnlyNominalXSec)
        log.info("Systematics: %s" % list(self.systDict.keys()))
        log.debug("Cuts Dictionary: %s" % self.cutsDict)
        log.info("readFromTree: %s" % self.readFromTree)
        log.info("plotHistos: %s" % self.plotHistos)
        log.info("executeHistFactory: %s" % self.executeHistFactory)
        log.info("fitConfig objects:")
        for tl in self.fitConfigs:
            log.info("  %s" % tl.name)
            for c in tl.channels:
                log.info(f"    {c.name}: {c.systDict.keys()}")
        log.info("C++ ConfigMgr status: %s" % self.cppMgr.m_status)
        log.info("Histogram names: (set log level DEBUG)")
        configMgr.printHists()
        log.info("Chain names: (set log level DEBUG & note chains are only generated with -t)")
        configMgr.printChains()
        log.info("Inputs: (set log level DEBUG)")
        configMgr.printFiles()
        #log.info("Input tree names: (set log level DEBUG)")
        #configMgr.printTreeNames()
        log.info("*-------------------------------------------------*\n")
        return

    def printHists(self):
        """
        Print all the histograms defined in the manager
        """
        hists = sorted(self.hists.keys())
        log.info(f"# Histograms defined: {len(hists)}")
        for i, hist in enumerate(hists):
            log.debug(f"Histogram {i+1}/{len(hists)}: {hist}")
        return

    def printChains(self):
        """
        Print all the ROOT TChains defined in the manager
        """
        chainList = list(self.chains.keys())
        chainList.sort()
        for chain in chainList:
            log.debug(chain)
        return

    def printFiles(self):
        """
        Print all the input files used for the various fit configurations
        """
        
        width = 3 
        depth = 1
        
        log.info("ConfigManager:")
        for i, inputTree in enumerate(self.input_files):
            log.info("{}Input {:d}/{:d}: '{}' from {} ".format(" "*depth*width, i+1, len(self.input_files), inputTree.treename, inputTree.filename))

        for idx, fitConfig in enumerate(self.fitConfigs):
            depth = 1
            log.info("{}fitConfig {:d}/{:d}: {} - {:d} channels,  {:d} inputs".format(" "*depth*width, idx+1, len(self.fitConfigs), fitConfig.name, len(fitConfig.channels), len(fitConfig.input_files)))
            for i, inputTree in enumerate(fitConfig.input_files):
                log.info("{}Input {:d}/{:d}: '{}' from {} ".format(" "*depth*width, i+1, len(fitConfig.input_files), inputTree.treename, inputTree.filename))

            for i, channel in enumerate(fitConfig.channels):
                depth = 2
                log.info("{}Channel {:d}/{:d}: {} - {:d} samples, {:d} inputs".format(" "*depth*width, i+1, len(fitConfig.channels), channel.name, len(channel.sampleList), len(channel.input_files)))
                for j, inputTree in enumerate(channel.input_files):
                    depth = 3
                    log.info("{}Input {:d}/{:d}: '{}' from {} ".format(" "*depth*width, j+1, len(channel.input_files), inputTree.treename, inputTree.filename))

                for j, sample in enumerate(channel.sampleList):
                    depth = 3
                    log.info("{}Sample {:d}/{:d}: {} - {:d} systematics, {:d} inputs".format(" "*depth*width, j+1, len(channel.sampleList), sample.name, len(sample.systDict), len(sample.input_files)))

                    for k, inputTree in enumerate(sample.input_files):
                        depth = 4
                        log.info("{}Input {:d}/{:d}: '{}' from {} ".format(" "*depth*width, k+1, len(sample.input_files), inputTree.treename, inputTree.filename))
                    
                    for k, syst_name in enumerate(sample.systDict.keys()):
                        depth = 4
                        syst = sample.systDict[syst_name]
                        
                        log.info("{}Systematic {:d}/{:d}: {}".format(" "*depth*width, k+1, len(list(sample.systDict.keys())), syst_name))

                    #for (systName, syst) in sample.systDict.items():
                        #log.info("                            ---> Systematic: %s" % syst.name)
                        #log.info("                                       Low : %s" % str(syst.filesLo))
                        #log.info("                                       High: %s" % str(syst.filesHi))
        
        return
      
    def printPrunedSyst(self):
        """
        Print a list with all pruned systematics
        """
        
        width = 3 
        depth = 1
        
        for idx, fitConfig in enumerate(self.fitConfigs):
            depth = 1
            log.info("{}fitConfig {:d}/{:d}: {}".format(" "*depth*width, idx+1, len(self.fitConfigs), fitConfig.name))

            for i, channel in enumerate(fitConfig.channels):
              
                prunedDict={}
                prunedDict_histo={}
                syst_list=[]
              
                depth = 2
                log.info("{}Channel {:d}/{:d}: {}".format(" "*depth*width, i+1, len(fitConfig.channels), channel.name))
                for j, sample in enumerate(channel.sampleList):
                    depth = 3
                    log.info("{}Sample {:d}/{:d}: {} ".format(" "*depth*width, j+1, len(channel.sampleList), sample.name))
                    log.info("{}Pruned systematics:".format(" "*depth*width))
                    if sample.isData: continue
                    prunedDict[sample.name]=[]
                    prunedDict_histo[sample.name]=[]
                    
                    for k, syst_name in enumerate(sample.systDict.keys()):
                        depth = 4
                        if syst_name in sample.systListOverallPruned:
                            log.info("{}. {} (overallSys)".format(" "*depth*width, syst_name))
                            prunedDict[sample.name].append(syst_name)
                            if not syst_name in syst_list: syst_list.append(syst_name)
                        if syst_name in sample.systListHistoPruned:
                            log.info("{}. {} (histoSys)".format(" "*depth*width, syst_name))
                            prunedDict_histo[sample.name].append(syst_name)
                            if not syst_name in syst_list: syst_list.append(syst_name)
                            
                canvasSyst = TCanvas("canvasSyst_"+str(i),"canvasSyst_"+channel.name,800,1200)
                canvasSyst.SetLeftMargin(0.3)
                canvasSyst.SetRightMargin(0.25)
                
                gStyle.SetOptTitle(False)
                gStyle.SetOptStat(0)
                
                if len(syst_list)==0: continue
                
                histPrunedOverallHisto = TH2D("histPrunedOverallHisto_"+str(i), "Pruned systematics affecting the normalization and shape for channel "+channel.name,len(channel.sampleList)-1,0,len(channel.sampleList)-1,len(syst_list),0,len(syst_list))
                histPrunedOverall = TH2D("histPrunedOverall_"+str(i), "Pruned systematics affecting the normalization for channel "+channel.name,len(channel.sampleList)-1,0,len(channel.sampleList)-1,len(syst_list),0,len(syst_list))
                histPrunedHisto = TH2D("histPrunedHisto_"+str(i), "Pruned systematics affecting the shape for channel "+channel.name,len(channel.sampleList)-1,0,len(channel.sampleList)-1,len(syst_list),0,len(syst_list))
                
                
                xbin = 1
                for j2, thisSample in enumerate(prunedDict.keys()):
                    for i2 in range(0,len(syst_list)):
                        if syst_list[i2] in prunedDict[thisSample] and syst_list[i2] in prunedDict_histo[thisSample]:
                            histPrunedOverallHisto.SetBinContent(xbin,i2+1,1)
                        elif syst_list[i2] in prunedDict[thisSample]:
                            histPrunedOverall.SetBinContent(xbin,i2+1,1)
                        elif syst_list[i2] in prunedDict_histo[thisSample]:
                            histPrunedHisto.SetBinContent(xbin,i2+1,1)    
                        #else:
                        #    histPrunedOverall.SetBinContent(j2,i2,-1)
                        
                    histPrunedOverallHisto.GetXaxis().SetBinLabel(xbin,thisSample)
                    histPrunedHisto.GetXaxis().SetBinLabel(xbin,thisSample)
                    histPrunedOverall.GetXaxis().SetBinLabel(xbin,thisSample)
                    xbin=xbin+1
                
                for i2 in range(0,len(syst_list)):
                    histPrunedOverallHisto.GetYaxis().SetBinLabel(i2+1,syst_list[i2])
                    histPrunedOverall.GetYaxis().SetBinLabel(i2+1,syst_list[i2])
                    histPrunedHisto.GetYaxis().SetBinLabel(i2+1,syst_list[i2])
            
                histPrunedOverallHisto.GetXaxis().SetTitle("Channel")
                histPrunedOverallHisto.GetYaxis().SetTitle("systematic")
                histPrunedOverall.GetXaxis().SetTitle("Channel")
                histPrunedOverall.GetYaxis().SetTitle("systematic")
                histPrunedHisto.GetXaxis().SetTitle("Channel")
                histPrunedHisto.GetYaxis().SetTitle("systematic")
                histPrunedOverallHisto.SetFillColor(5)
                histPrunedOverall.SetFillColor(9)
                histPrunedHisto.SetFillColor(2)
            
                if histPrunedOverallHisto.GetEntries()>0: histPrunedOverallHisto.Draw("boxPFC")
                if histPrunedOverall.GetEntries()>0: histPrunedOverall.Draw("boxsamePFC")
                if histPrunedHisto.GetEntries()>0: histPrunedHisto.Draw("boxsamePFC")
                
                leg = TLegend(0.76,0.75,1.,0.9)
                leg.SetBorderSize(0)
                leg.SetTextSize(0.02)
                entry = leg.AddEntry(histPrunedOverallHisto,"histoSys/ overallSys","f")
                entry = leg.AddEntry(histPrunedOverall,"overallSys","f")
                entry = leg.AddEntry(histPrunedHisto,"histoSys","f")
                leg.Draw("same")
                
                plotsDir = f"plots/{self.analysisName}/{fitConfig.name}"
                mkdir_p(plotsDir)

                canvasSyst.Print(plotsDir+"/canvasSyst_"+channel.name+".pdf")
                canvasSyst.Print(plotsDir+"/canvasSyst_"+channel.name+".eps")


        return

    #def printTreeNames(self):
        #"""
        #Print the names of all the ROOT TTrees used in the fit configurations defined
        #"""
        #if str(self.treeName).strip() == "":
            #log.debug("No tree used")
            #return

        #log.debug("ConfigManager:")
        #log.debug(str(self.treeName).strip())

        #for fitConfig in self.fitConfigs:
            #log.debug("  fitConfig: %s" % fitConfig.name)
            #log.debug("             %s" % str(fitConfig.treeName))

            #for channel in fitConfig.channels:
                #log.debug("    ---> Channel: %s" % channel.name)
                #log.debug("                  %s" % str(channel.treeName))

                #for sample in channel.sampleList:
                    #log.debug("           ---> Sample: %s" % sample.name)
                    #log.debug("                        %s" % str(sample.treeName))

                    #for (systName,syst) in sample.systDict.items():
                        #log.debug("                   ---> Systematic: %s" % syst.name)
                        #log.debug("                        Low : %s" % str(syst.treeLoName))
                        #log.debug("                        High: %s" % str(syst.treeHiName))
        #return

    #def setInputFiles(self, filelist):
        #"""
        #Set file list for config manager.
        #This will be used as default for top level xmls that don't specify
        #their own file list.

        #@param input_files A list of input files
        #"""
        #self.input_files = filelist

    #def setInputFile(self, file):
        #"""
        #Set file list for config manager.
        #This will be used as default for top level xmls that don't specify
        #their own file list.

        #@param file A filename to set as a list
        #"""
        #self.input_files = [file]

    #def propagateInputFiles(self):
        #"""
        #Propagate the file list downwards.
        #"""
        #log.info("  -propagate file list and tree names to fit configurations")
        
        ## propagate our file list downwards (if we don't have one,
        ## this will result in the propagation of the files belonging
        ## to our top level xml)
        #for fitConfig in self.fitConfigs:
            #fitConfig.propagateInputFiles(self.input_files)

    #def setTreeName(self, treeName):
        #"""
        #Set the treename

        #@param treeName The name of the tree to use
        #"""
        #self.treeName = treeName
        #return

    #def propagateTreeName(self):
        #"""
        #Propogate the tree name down to all owned fit configurations
        #"""
        #for fc in self.fitConfigs:
            #fc.propagateTreeName(self.treeName)
            #pass
        #return

    def executeAll(self):
        """
        Execute all fit configurations owned
        """
        for tl in self.fitConfigs:
            self.execute(tl)
        return

    def execute(self, fitConfig):
        """
        Execute a particular fit configuration

        @param fitConfig The configuration to execute
        """
        log.info(f"Preparing histograms and/or workspace for fitConfig {fitConfig.name}\n")
        if self.ignoreSystematics:
            log.info("NOTE: ignoring any defined systematics. Change configMgr.ignoreSystematics if this behaviour is not desired.\n")
    

        if self.plotHistos:
            cutHistoDict = {}
            cutStackDict = {}
            varStackDict = {}
            varSUSYDict = {}
            varDataDict = {}
        systDict = {}

        for (name, syst) in list(self.systDict.items()):
            systDict[name] = syst

        for (name, syst) in list(fitConfig.systDict.items()):
            if not name in list(systDict.keys()):
                systDict[name] = syst
            else:
                raise Exception

        # Build channel string and cuts for normalization
        normRegions = []
        normString = ""
        normCuts = ""
        for (iChan,chan) in enumerate(fitConfig.channels):
            if not chan.channelName in fitConfig.validationChannels:
                normCutsList = [ "(%s) || " % (self.cutsDict[reg]) for reg in chan.regions ]
                normCuts = "".join(normCutsList)

                for reg in chan.regions:
                    normRegions.append(reg)
        
        normCuts = normCuts.rstrip(" || ")
        for (iChan, chan) in enumerate(fitConfig.channels):
            for (iSam, sam) in enumerate(chan.sampleList):
                chan.infoDict[sam.name] = [("Nom", self.nomName, sam.weights, "")]
                if not sam.isData and not sam.isQCD:
                    for (systName, syst) in list(sam.systDict.items()):
                        ###depending on the systematic type: chan.infoDict[sam.name].append(...)
                        self.appendSystinChanInfoDict(chan, sam, systName, syst)

        for (iChan, chan) in enumerate(fitConfig.channels):
            log.info(f"Channel {iChan+1}/{len(fitConfig.channels)}: {chan.name}")
            regionString = "".join(chan.regions)
            self.prepare.channel = chan
            
            sampleListRun = deepcopy(chan.sampleList)
            #for (iSam, sam) in enumerate(fitConfig.sampleList):
            for (iSam, sam) in enumerate(sampleListRun):
                log.info(f"   Sample {iSam+1}/{len(sampleListRun)}: {sam.name}")
                sam.removeCurrentSystematic()  # make sure that we are not mistakenly using a systematic variation tree
                
                # Run over the nominal configuration first
                # Set the weights, cuts, weights and actually call prepare.read() internally
                self.setWeightsCutsVariable(chan, sam, regionString)
                
                #depending on the sample type, the Histos and up/down weights are added
                log.debug(f"Calling addSampleSpecificHists() for {chan.name}")
                self.addSampleSpecificHists(fitConfig, chan, sam, regionString, normRegions, normString, normCuts)

                #sys.exit(0)
        #sys.exit(0)

        # post-processing 1: loop for user-norm systematics
        log.verbose("Adding user-defined norm systematics")
        for chan in fitConfig.channels:
            regionString = "".join(chan.regions)

            log.verbose(f"Systematics in channel {chan.channelName}")
            for sam in chan.sampleList:
                log.verbose(f"Systematics in channel {chan.channelName}, sample {sam.name}")
                for syst in list(sam.systDict.values()):
                    if syst.method != "userNormHistoSys":
                        log.verbose(f"Skipping systematic {syst.name} - not of type userNormHistoSys")
                        continue
                
                    log.verbose(f"Adding systematic {syst.name} in channel {chan.channelName}, sample {sam.name}")

                    nomName = f"h{sam.name}Nom_{regionString}_obs_{replaceSymbols(chan.variableName)}"
                    highName = f"h{sam.name}{syst.name}High_{regionString}_obs_{replaceSymbols(chan.variableName)}"
                    lowName = f"h{sam.name}{syst.name}Low_{regionString}_obs_{replaceSymbols(chan.variableName)}"

                    normString = ""
                    if sam.normRegions is not None:
                        for normReg in sam.normRegions:
                            if not type(normReg[0]) == "list":
                                normList = [normReg[0]]
                                c = fitConfig.getChannel(normReg[1], normList)
                            else:
                                c = fitConfig.getChannel(normReg[1], normReg[0])
                            normString += c.regionString

                    # Do not fall back if the sample has no input files defined!
                    forceNoFallback = len(sam.input_files) == 0
                    syst.PrepareGlobalNormalization(normString, self, chan, sam, forceNoFallback)
                    sam.addHistoSys(syst.name, nomName, highName, lowName, False, True, False, False, sam.name, normString)

        # post-processing 2: swapping of overall systematics for specified channel by systematics from other channel
        log.verbose("Remapping overall systematics to systematics from other channels")
        for chan in fitConfig.channels:
            # only consider channels for which a remap channel has been defined.
            if len(chan.remapSystChanName) == 0:
                log.verbose(f"Skipping {chan.channelName} - no remapping defined")
                continue
                
            log.debug(f"Remapping systematics for {chan.channelName}")

            log.info("For overallSys: now setting systematic(s)s of channel <%s> to those of channel: <%s>"%(chan.name,chan.remapSystChanName))
            rc = fitConfig.getChannelByName(chan.remapSystChanName)
            # loop over overallSystematics of all samples, and swap for those of remap channel
            for sam in chan.sampleList:
                if not sam.allowRemapOfSyst:
                    log.verbose(f"Sample {sam.name} does not allow remapping - skipping")
                    continue
                if sam.isData: 
                    log.verbose(f"Sample {sam.name} is data - skipping")
                    continue
                if not rc.hasSample(sam.name): 
                    log.verbose(f"Sample {sam.name} not present in remapped channel - skipping")
                    continue

                rs = rc.getSample(sam.name)

                for (key, ssys) in list(sam.systDict.items()):
                    if not ssys.allowRemapOfSyst: 
                        log.verbose(f"Sample {sam.name}: systematic {ssys.name} does not allow remapping - skipping")
                        continue

                    log.verbose(f"Sample {sam.name}: remapping for systematic {ssys.name}")

                    osys = sam.getOverallSys(key) # overall sys part is to be modified
                    rsys = rs.getOverallSys(osys[0]) # get replacement overall systematic, by name
                    
                    if rsys is None:
                        log.warning(f"For channel {chan.name} and sample {sam.name}, replacement systematic {osys[0]} could not be found. Skipping replacement of this overall syst.")
                        continue

                    log.info(f"For channel {chan.name} and sample {sam.name}, replacement of overall systematic {osys[0]} from {rc.name}.")
                    sam.replaceOverallSys(rsys)
                    pass

##      AK - 28-jan-2014, commenting out remapping for histoSys-type. The problem is that not only should one remap the normalization for this to work, but also the shape, which is not implemented yet.
##             rc = fitConfig.getChannelByName(chan.remapSystChanName)
##             # Check that for histoSys remapping, the channels have the same binning and binWidth
##             # If they do not, then no remapping is performed
##             channelsCompatible = chan.compareChannelFormat(rc)
##             if not channelsCompatible:
##                 continue
            
##             log.info("For histoSys: now setting systematics of channel <%s> to those of channel: <%s>"%(chan.name,chan.remapSystChanName))
##             # loop over overallSystematics of all samples, and swap for those of remap channel
##             for sam in chan.sampleList:
##                 if not sam.allowRemapOfSyst: continue
##                 if sam.isData: continue
##                 if not rc.hasSample(sam.name): continue

##                 rs = rc.getSample(sam.name)

##                 for (key, ssys) in sam.systDict.items():
##                     if not ssys.allowRemapOfSyst: continue

##                     osys = sam.getHistoSys(key) # histo sys part is to be modified
                  
##                     rsys = rs.getHistoSys(osys[0]) # get replacement histo systematic, by name
##                     if rsys is None:
##                         log.warning("For channel %s and sample %s, replacement systematic %s could not be found. Skipping replacement of this histo syst." % (chan.name,sam.name,osys[0]))
##                         continue

##                     log.info("For channel %s and sample %s, replacement of histo systematic %s from %s." % (chan.name,sam.name,osys[0],rc.name))
##                     sam.replaceHistoSys(rsys)
##                     pass
            
        #post-processing 3: merging of overall systematics (e.g. signal theory), if so requested
        for chan in fitConfig.channels:
            for sam in chan.sampleList:
                if len(sam.mergeOverallSysSet)>=1:
                    if isinstance(sam.mergeOverallSysSet[0],list):
                        for i in range(len(sam.mergeOverallSysSet)): 
                            if len(sam.mergeOverallSysSet[i])<=1: continue
                            log.info(f"Post-processing: for channel {chan.name} and sample {sam.name}, merging of systematics {str(sam.mergeOverallSysSet[i])}.")
                            keepName = sam.mergeOverallSysSet[i][0]
                            lowErr2 = 0.0
                            highErr2 = 0.0
                            for systName in sam.mergeOverallSysSet[i]:
                                sys = sam.getOverallSys(systName)
                                if sys!=None:
                                    highErr2 += (sys[1]-1.0)**2
                                    lowErr2 += (sys[2]-1.0)**2
                                    log.info(f"Now processing : {systName} {sys[1]-1.0:f} {sys[2]-1.0:f}")
                                    # and remove ... to be readded merged below
                                    sam.removeOverallSys(systName)
                                pass
                            highErr = sqrt(highErr2)
                            lowErr = sqrt(lowErr2)
                            log.info(f"Merged systematic : {keepName} {1+highErr:f} {1-lowErr:f}")
                            sam.addOverallSys(keepName,1.0+highErr,1.0-lowErr)

                    elif isinstance(sam.mergeOverallSysSet[0],str):
                        if len(sam.mergeOverallSysSet)<=1: continue
                        log.info(f"Post-processing: for channel {chan.name} and sample {sam.name}, merging of systematics {str(sam.mergeOverallSysSet)}.")
                        keepName = sam.mergeOverallSysSet[0]
                        lowErr2 = 0.0
                        highErr2 = 0.0
                        for systName in sam.mergeOverallSysSet:
                            sys = sam.getOverallSys(systName)
                            if sys != None:
                                highErr2 += (sys[1]-1.0)**2
                                lowErr2 += (sys[2]-1.0)**2
                                log.info(f"Now processing : {systName} {sys[1]-1.0:f} {sys[2]-1.0:f}")
                                # and remove ... to be readded merged below
                                sam.removeOverallSys(systName)
                            pass
                        highErr = sqrt(highErr2)
                        lowErr = sqrt(lowErr2)
                        log.info(f"Merged systematic : {keepName} {1+highErr:f} {1-lowErr:f}")
                        sam.addOverallSys(keepName, 1.0+highErr, 1.0-lowErr)
                
        # Build blinded histograms here
        log.debug("Checking if blinded histograms need to be built")
        for (iChan, chan) in enumerate(fitConfig.channels):
            for sam in chan.sampleList:
                if sam.isData:
                    self.buildBlindedHistos(fitConfig, chan, sam)
                else:
                    pass
        
        # Plot histograms, if asked
        if self.plotHistos:
            mkdir_p("plots/%s" % self.analysisName)
            for (iChan,chan) in enumerate(fitConfig.channels):
                if chan.hasDiscovery:
                    continue
                self.makeDicts(fitConfig, chan)

        # Clear chains
        for name, chain in list(self.chains.items()):
            if name in self.friend_chains:
                self.chains[name].RemoveFriend(self.friend_chains[name])
                self.friend_chains[name].Reset()
                log.info(f"Removing friend chain {self.friend_chains[name].GetName()}")
                del self.friend_chains[name]

            log.info(f"Removing chain {name}")
            self.chains[name].Reset()
            del self.chains
            self.chains = {}

        # Clear leftover friend chains
        for name, chain in list(self.friend_chains.items()):
            log.info(f"Removing friend chain {chain.GetName()} @ {hex(id(chain))} ({name})")
            for _file in chain.GetListOfFiles():
                log.info(f"Chain {chain.GetName()} ({hex(id(chain))}) includes {_file.GetTitle()}")

            self.friend_chains[name].Reset()
            del self.friend_chains[name]
 
        ##TODO: things are broken up to here
        #sys.exit()
    
        # Write the data file
        self.outputRoot()
       
        if self.executeHistFactory:
            #removing regions used for remapping systematic uncertainties, but only for exclusion fits
            #execute the folllowing only if some channel with a remapped systematic uncertaintiy was used
            #in this case, keep only channels belonging to the signalchannels or the bkgConstrainchannels
            if self.myFitType == self.FitType.Exclusion and len([chan for chan in fitConfig.channels if len(chan.remapSystChanName)>0]) > 0:
                log.info("Found top level object for exclusion fit: %s" % fitConfig.name)
                
                for chan in fitConfig.channels:
                    if not chan.channelName in fitConfig.signalChannels and not chan.channelName in fitConfig.bkgConstrainChannels:
                        try:
                            fitConfig.channels.remove(chan)
                            log.info(f"Removing channel {chan.name} from top level object {fitConfig.name} as not signal region and not control region")
                        except:
                            log.warning(f"Unable to remove channel {chan.name} from top level object {fitConfig.name}")

            if self.writeXML:
                fitConfig.writeXML() # <- this internally calls channel.writeXML()
                fitConfig.executehist2workspace()
            else:
                fitConfig.writeWorkspaces()
                
        if self.prun:
            self.printPrunedSyst()

    def appendSystinChanInfoDict(self, chan, sam, systName, syst):
        """
        Append a systematic to a particular sample and channel

        @param chan The channel to add systematics to
        @param sam The sample in the channel to add systematics to
        @param systName The name of the new systematic
        @param syst The systematic to add
        """
        log.debug("appendSystinChanInfoDict: appending info:")
        log.debug("  CHAN %s" % chan.name)
        log.debug("  SAM %s" % sam.name)
        log.debug("  SYST %s" % systName)
        log.debug("  TYPE %s" % syst.type)
        log.debug("  METHOD %s" % syst.method)
        log.debug("  LOW %s" % str(syst.low))
        log.debug("  HIGH %s" % str(syst.high))
        
        if syst.type == "tree":
            chan.infoDict[sam.name].append((systName+"High", syst.high, sam.weights, syst.method))
            chan.infoDict[sam.name].append((systName+"Low", syst.low, sam.weights, syst.method))
        elif syst.type == "weight":
            chan.infoDict[sam.name].append((systName+"High", self.nomName, syst.high, syst.method))
            chan.infoDict[sam.name].append((systName+"Low", self.nomName, syst.low, syst.method))
        else:
            chan.infoDict[sam.name].append((systName, syst.high, syst.low, syst.method))
        return

    def addHistoSysforNoQCD(self, regionString, normString, normCuts, fitConfig, chan, sam, syst):
        nomName    = f"h{sam.name}Nom_{regionString}_obs_{replaceSymbols(chan.variableName)}"
        nomSysName = f"h{sam.name}{syst.name}Nom_{regionString}_obs_{replaceSymbols(chan.variableName)}"
        highName   = f"h{sam.name}{syst.name}High_{regionString}_obs_{replaceSymbols(chan.variableName)}"
        lowName    = f"h{sam.name}{syst.name}Low_{regionString}_obs_{replaceSymbols(chan.variableName)}"

        if syst.method == "histoSys":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, 
                                                includeOverallSys=False, normalizeSys=False, nomSysName=nomSysName)
        elif syst.method == "histoSysOneSide":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, 
                                                includeOverallSys=False, normalizeSys=False, symmetrize=False, oneSide=True, nomSysName=nomSysName)
        elif syst.method == "histoSysOneSideSym":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, 
                                                includeOverallSys=False, normalizeSys=False, symmetrize=True, oneSide=True, nomSysName=nomSysName)
        elif syst.method == "histoSysEnvelopeSym": 
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, 
                                                includeOverallSys=False, normalizeSys=False, symmetrize=True, oneSide=False, symmetrizeEnvelope=True, 
                                                samName=sam.name, normString=normString, nomSysName=nomSysName)
        elif syst.method == "overallSys" or syst.method == 'userOverallSys':
            highIntegral = configMgr.hists[highName].Integral()
            lowIntegral = configMgr.hists[lowName].Integral()
            nomIntegral = configMgr.hists[nomName].Integral()
            try:
                overallSystHigh = highIntegral / nomIntegral
            except ZeroDivisionError:
                log.warning(f"    generating High overallSys for {nomName} syst={syst.name} nom={nomIntegral:g} high={highIntegral:g} low={lowIntegral:g}")
                overallSystHigh = 1.0
            try:
                overallSystLow = lowIntegral / nomIntegral
            except ZeroDivisionError:
                log.warning(f"    generating Low overallSys for {nomName} syst={syst.name} nom={nomIntegral:g} high={highIntegral:g} low={lowIntegral:g}")
                overallSystLow = 1.0
            chan.getSample(sam.name).addOverallSys(syst.name, overallSystHigh, overallSystLow)
        elif syst.method == "overallHistoSys":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, 
                                                includeOverallSys=True, normalizeSys=False, nomSysName=nomSysName)
        elif syst.method == "overallNormSys":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, 
                                                includeOverallSys=True, normalizeSys=True, symmetrize=False, oneSide=False, 
                                                samName=sam.name, normString=normString, nomSysName=nomSysName)
        elif syst.method == "overallNormHistoSys":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, 
                                                includeOverallSys=True, normalizeSys=True, symmetrize=False, oneSide=False, 
                                                samName=sam.name, normString=normString, nomSysName=nomSysName)
        elif syst.method == "overallNormHistoSysOneSide":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, 
                                                includeOverallSys=True, normalizeSys=True, symmetrize=False, oneSide=True,
                                                samName=sam.name, normString=normString, nomSysName=nomSysName)
        elif syst.method == "overallNormHistoSysOneSideSym":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, 
                                                includeOverallSys=True, normalizeSys=True, symmetrize=True, oneSide=True,
                                                samName=sam.name, normString=normString, nomSysName=nomSysName)
        elif syst.method == "overallNormHistoSysEnvelopeSym":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, 
                                                includeOverallSys=True, normalizeSys=True, symmetrize=True, oneSide=False, symmetrizeEnvelope=True,
                                                samName=sam.name, normString=normString, nomSysName=nomSysName)
        elif syst.method == "normHistoSys":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, 
                                                includeOverallSys=False, normalizeSys=True,symmetrize= False, oneSide=False, 
                                                samName=sam.name, normString=normString, nomSysName=nomSysName)
        elif syst.method == "normHistoSysOneSide":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, 
                                                includeOverallSys=False, normalizeSys=True, symmetrize=False, oneSide=True, 
                                                samName=sam.name, normString=normString, nomSysName=nomSysName)
        elif syst.method == "normHistoSysOneSideSym":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, 
                                                includeOverallSys=False, normalizeSys=True, symmetrize=True, oneSide=True, 
                                                samName=sam.name, normString=normString, nomSysName=nomSysName)
        elif syst.method == "normHistoSysEnvelopeSym": 
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, 
                                                includeOverallSys=False, normalizeSys=True, symmetrize=True, oneSide=False, symmetrizeEnvelope=True, 
                                                samName=sam.name, normString=normString, nomSysName=nomSysName)
        elif syst.method == "userHistoSys" or syst.method == "userNormHistoSys":
            if configMgr.hists[highName] is None:
                log.warning(f'    addHistoSysforNoQCDEmpty: {highName} histogram is not found in configMgr.hists')
            if configMgr.hists[lowName] is None:
                log.warning(f'    addHistoSysforNoQCDEmpty: {lowName} histogram is not found in configMgr.hists')

            if syst.method == "userHistoSys":
                chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, False, False, nomSysName=nomSysName)
        elif syst.method == "shapeSys":
            if syst.merged:
                mergedName = "".join(syst.sampleList)
                
                nomMergedName = f"h{mergedName}Nom_{regionString}_obs_{replaceSymbols(chan.variableName)}"
                highMergedName = f"h{mergedName}High_{regionString}_obs_{replaceSymbols(chan.variableName)}"
                lowMergedName = f"h{mergedName}Low_{regionString}_obs_{replaceSymbols(chan.variableName)}"
                
                if sam.name in syst.sampleList:
                    syst.foundSample()
                    if self.hists[nomMergedName] is None:
                        self.hists[nomMergedName] = self.hists[nomName].Clone(nomMergedName)
                    else:
                        self.hists[nomMergedName].Add(self.hists[nomName])
                    if self.hists[highMergedName] is None:
                        self.hists[highMergedName] = self.hists[highName].Clone(highMergedName)
                    else:
                        self.hists[highMergedName].Add(self.hists[highName])
                    if self.hists[lowMergedName] is None:
                        self.hists[lowMergedName] = self.hists[lowName].Clone(lowMergedName)
                    else:
                        self.hists[lowMergedName].Add(self.hists[lowName])
                    if syst.isMerged():
                        chan.getSample(sam.name).addShapeSys(syst.name,nomMergedName,highMergedName,lowMergedName,syst.constraint)
                        syst.Reset()
                    chan.getSample(sam.name).shapeSystList.append((syst.name, nomMergedName+"Norm", syst.constraint, "", "", "", ""))
            else:
                chan.getSample(sam.name).addShapeSys(syst.name, nomName, highName, lowName)
                chan.getSample(sam.name).shapeSystList.append((syst.name, nomName+"Norm", syst.constraint, "", "", "", ""))
        elif syst.method == "shapeStat":
            try:
                threshold = chan.statErrorThreshold
            except:
                threshold = None     
            chan.getSample(sam.name).addShapeStat(syst.name, nomName, statErrorThreshold = threshold ) # this stores a new histogram called: nomName+"Norm" 
            chan.getSample(sam.name).shapeSystList.append(('shape_{}_{}_{}_obs_{}'.format(syst.name, sam.name,
                                                                                      regionString,
                                                                                      replaceSymbols(chan.variableName)),
                                                           nomName+"Norm", syst.constraint, "", "", "", ""))
        else:
            log.error(f"ERROR don't know what to do with {syst.name:s} (type: {syst.method:s})")
        return

    def addHistoSysForQCD(self,regionString,normString,normCuts,chan,sam):
        self.prepare.addQCDHistos(sam,chan.useOverflowBin,chan.useUnderflowBin)

        if chan.variableName == "cuts":
            nHists = len(chan.regions)
        else:
            nHists = chan.nBins

        prefixNom = f"h{sam.name}Nom_{regionString}_obs_{replaceSymbols(chan.variableName)}"
        prefixHigh = f"h{sam.name}High_{regionString}_obs_{replaceSymbols(chan.variableName)}"
        prefixLow = f"h{sam.name}Low_{regionString}_obs_{replaceSymbols(chan.variableName)}"

        chan.getSample(sam.name).setWrite(True)
        chan.getSample(sam.name).setHistoName(prefixNom)

        if chan.getSample(sam.name).qcdSyst == "histoSys":
            chan.getSample(sam.name).addHistoSys("QCDNorm_"+regionString,prefixNom,prefixHigh,prefixLow,False,False)
        elif chan.getSample(sam.name).qcdSyst == "overallSys":
            highIntegral = configMgr.hists[prefixHigh].Integral()
            lowIntegral = configMgr.hists[prefixLow].Integral()
            nomIntegral = configMgr.hists[prefixNom].Integral()
            
            try:
                overallSystHigh = highIntegral / nomIntegral
                overallSystLow = lowIntegral / nomIntegral
            except ZeroDivisionError:
                log.warning("Error generating HistoSys for {} syst={} nom={:g} high={:g} low={:g}".format(nomName,"QCDNorm_"+regionString,nomIntegral,highIntegral,lowIntegral))
            
            chan.getSample(sam.name).addOverallSys("QCDNorm_"+regionString, overallSystHigh, overallSystLow)
        elif chan.getSample(sam.name).qcdSyst == "overallHistoSys":
            chan.getSample(sam.name).addHistoSys("QCDNorm_"+regionString, prefixNom, prefixHigh, prefixLow, True, False)
        elif chan.getSample(sam.name).qcdSyst == "normHistoSys":
            chan.getSample(sam.name).addHistoSys("QCDNorm_"+regionString, prefixNom, prefixHigh, prefixLow, False, True)
        elif chan.getSample(sam.name).qcdSyst == "shapeSys":
            chan.getSample(sam.name).addShapeSys("QCDNorm_"+regionString, prefixNom, prefixHigh, prefixLow)
            chan.getSample(sam.name).shapeSystList.append(("QCDNorm_"+regionString, prefixNom+"Norm", "data/"+configMgr.analysisName+".root", "", "", "", ""))
        elif chan.getSample(sam.name).qcdSyst == "uncorr":
            chan.getSample(sam.name).setWrite(False)

            for iBin in range(1,nHists+1):
                qcdSam = sam.Clone()
                qcdSam.name = f"{sam.name}_{regionString}_{str(iBin)}"
                chan.addSample(qcdSam)
                chan.getSample(qcdSam.name).setWrite(True)
                chan.getSample(qcdSam.name).setHistoName("h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName)+"_"+str(iBin))
                chan.getSample(qcdSam.name).addHistoSys("NormQCD"+regionString+"_"+str(iBin),prefixNom+"_"+str(iBin),prefixHigh+"_"+str(iBin),prefixLow+"_"+str(iBin),False,False)
        else:
            raise Exception("Incorrect systematic method specified for QCD: %s" % getSample(sam.name).qcdSyst)

    def setWeightsCutsVariable(self, chan, sam, regionString, noRead=False):
        """
        Generate the string of weights applied to a sample

        @param chan The channel to use
        @param sam The sample to use
        @param regionString Internal string to use in the dictionary of cuts
        """
        log.debug(f"setWeightsCutsVariable() for channel {chan.name} sample {sam.name}")
        if not sam.isData and not sam.isQCD and not sam.isDiscovery:
            oldWeights = copy(self.prepare.weights)
            self.prepare.weights = str(self.lumiUnits*self.outputLumi/self.inputLumi)
            self.prepare.weights += " * " + " * ".join(sam.weights)
            log.debug(f"settings weights to {self.prepare.weights}")
            if oldWeights == self.prepare.weights:
                log.debug(" => NOTE: no change in weights!")

            if (self.readFromTree and not sam.isDiscovery) or self.useCacheToTreeFallback:
                    #treeName = sam.treeName
                    #if treeName == '': 
                    #    treeName = sam.name+self.nomName
                    if not noRead:
                        log.debug(f"setWeightsCutsVariable(): calling prepare.read() for {sam.treename}")
                        #print sam.input_files
                        
                        #self.prepare.read(sam.treename, sam.files, friendTreeName=sam.friendTreeName)
                        self.prepare.read(sam.input_files, suffix=sam.getTreenameSuffix(), friendTreeName=sam.friendTreeName)
        else:
            self.prepare.weights = "1."
            if self.readFromTree or self.useCacheToTreeFallback:
                #treeName = sam.treeName
                #if treeName == '': 
                #    treeName = sam.name
                if not noRead:
                    log.debug(f"setWeightsCutsVariable(): calling prepare.read() for {sam.treename}")
                    #self.prepare.read(sam.treename, sam.files, friendTreeName=sam.friendTreeName)
                    self.prepare.read(sam.input_files, suffix=sam.getTreenameSuffix(), friendTreeName=sam.friendTreeName)

        oldCuts = copy(self.prepare.cuts)
        #if len(sam.cutsDict.keys()) == 0:
            #if not chan.variableName == "cuts":
                #self.prepare.cuts = self.cutsDict[regionString]
        #else:
            #if not chan.variableName == "cuts":
                #self.prepare.cuts = sam.cutsDict[regionString]
        
        if len(list(sam.cutsDict.keys())) == 0:
            #if not chan.variableName == "cuts":
            self.prepare.cuts = self.cutsDict[regionString]
        else:
            #if not chan.variableName == "cuts":
            self.prepare.cuts = sam.cutsDict[regionString]
       
        log.debug(f"Cuts currently: '{self.prepare.cuts}'")
        if sam.additionalCuts != "":
            if chan.ignoreAdditionalCuts:
                log.debug(f"Ignoring additional cuts in channel {chan.channelName} for sample {sam.name}")
            else:
                log.debug(f"Using additional cuts for sample {sam.name}: '{sam.additionalCuts}'")
                if len(self.prepare.cuts.strip()) != 0:
                    # ROOT doesn't like "()" as a cut, so we only use the string if it's non-empty
                    self.prepare.cuts = f"(({self.prepare.cuts}) && ({sam.additionalCuts}))"
                else:
                    log.verbose("No current cuts; only using the additional ones")
                    self.prepare.cuts = copy(sam.additionalCuts)

        log.debug(f"Setting cuts to '{self.prepare.cuts}'")
        if oldCuts == self.prepare.cuts:
            log.debug(" => NOTE: no change in cuts!")
        
        if sam.unit == "GeV":
            self.prepare.var = chan.variableName
        elif sam.unit == "MeV" and chan.variableName.find("/") < 0 and not chan.variableName.startswith("n"):
            self.prepare.var = chan.variableName+"/1000."

        return

    def addSampleSpecificHists(self, fitConfig, chan, sam, regionString, normRegions, normString, normCuts):
        """
        Add histograms to a specific sample

        @param fitConfig The fit configuration
        @param chan The channel
        @param sam The sample
        @param regionString String for the region to use
        @param normRegions Regions to normalise histograms in (optional)
        @param normCuts Cuts to apply in the normalisation
        """
        log.debug('addSampleSpecificHists()')
        histoName = f"h{sam.name}_{regionString}_obs_{replaceSymbols(chan.variableName)}"

        # Do not fall back if the sample has no input files defined!
        forceNoFallback = len(sam.input_files) == 0

        if sam.isData:
            #if self.channelIsBlinded(fitConfig, chan):
            if sam.isBlinded(fitConfig):
                log.info(f"Using blinded data for channel {chan.name} for sample {sam.name}") 
                #chan.addData(sam.blindedHistName)
            else:
                self.prepare.addHisto(sam.getHistogramName(fitConfig), 
                                      useOverflow=chan.useOverflowBin, 
                                      useUnderflow=chan.useUnderflowBin, 
                                      forceNoFallback=forceNoFallback)
                #chan.addData(histoName)
            
            chan.addData(sam.getHistogramName(fitConfig))

            #if chan.channelName in fitConfig.signalChannels:
                #if self.blindSR:
                    #chan.addData(sam.blindedHistName)
                #else:
                    #self.prepare.addHisto(histoName, useOverflow=chan.useOverflowBin, useUnderflow=chan.useUnderflowBin)
                    #chan.addData(histoName)
            #elif chan.channelName in fitConfig.bkgConstrainChannels:
                #if self.blindCR:
                    #chan.addData(sam.blindedHistName)
                #else:
                    #self.prepare.addHisto(histoName, useOverflow=chan.useOverflowBin, useUnderflow=chan.useUnderflowBin)
                    #chan.addData(histoName)
            #elif chan.channelName in fitConfig.validationChannels:
                #if self.blindVR or chan.blind:
                    #chan.addData(sam.blindedHistName)
                #else:
                    #self.prepare.addHisto(histoName, useOverflow=chan.useOverflowBin, useUnderflow=chan.useUnderflowBin)
                    #chan.addData(histoName)
            #else:
                #self.prepare.addHisto(histoName, useOverflow=chan.useOverflowBin, useUnderflow=chan.useUnderflowBin)
                #chan.addData(histoName)
        elif not sam.isQCD and not sam.isDiscovery:
            log.info("      - Loading nominal") # layout aligned with call for systematic
            tmpName="h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName)
            if not len(sam.shapeFactorList):
                log.debug(f"Building temporary histogram {tmpName}")
                self.prepare.addHisto(tmpName, useOverflow=chan.useOverflowBin, useUnderflow=chan.useUnderflowBin, forceNoFallback=forceNoFallback)
                ###check that nominal sample is not empty for that channel
                if self.hists[tmpName] is None or self.hists[tmpName].GetSum() == 0.0:
                    log.warning(f"    ***nominal sample {sam.name} is empty for channel {chan.name}. Remove from PDF.***")
                    chan.removeSample(sam.name)
                #    del self.hists[tmpName]
                #    self.hists[tmpName]=None    ## MB : do not delete, else cannot rerun later with -w
                    return
            else:
                self.hists[tmpName] = TH1D(tmpName, tmpName, chan.nBins, chan.binLow, chan.binHigh)
                for iBin in range(self.hists[tmpName].GetNbinsX()+1):
                    self.hists[tmpName].SetBinContent(iBin+1, 1.)
            chan.getSample(sam.name).setHistoName(tmpName)

            if not sam.normRegions and (not sam.noRenormSys): 
                needsNorm = False
                log.debug(f"Checking whether sample {sam.name} needs normalisation regions")
                for sys in list(sam.systDict.values()):
                    if sys.method == "userNormHistoSys" \
                           or sys.method == "normHistoSys" \
                           or sys.method == "normHistoSysOneSide" \
                           or sys.method == "normHistoSysEnvelopeSym" \
                           or sys.method == "normHistoSysOneSideSym" \
                           or sys.method == "overallNormSys" \
                           or sys.method == "overallNormHistoSys" \
                           or sys.method == "overallNormHistoSysOneSide" \
                           or sys.method == "overallNormHistoSysEnvelopeSym" \
                           or sys.method == "overallNormHistoSysOneSideSym":
                        log.error(f"    {sam.name} needs normRegions because of {sys.name} of type {sys.method} but no normalization regions specified. This is not safe, please fix.")
                        needsNorm = True
                        break
    
                if needsNorm:
                    log.verbose(f"Setting normalisation regions for {sam.name}")
                    normChannels = []
                    tl = sam.parentChannel.parentTopLvl
                    for ch in tl.channels:
                        if (ch.channelName in tl.bkgConstrainChannels) or (ch.channelName in tl.signalChannels):
                            normChannels.append((ch.regionString, ch.variableName))
                            pass
                        pass
                    sam.setNormRegions(normChannels)
                    log.warning("            For now, using all non-validation channels by default: %s" % sam.normRegions)
                    
            log.info(f"SettingNormRegion. RegionString: {regionString}, sample: {sam.name}, normRegion: {sam.normRegions} ")
            if sam.normRegions and (not sam.noRenormSys):
                log.debug(f"addSampleSpecificHists(): sample {sam.name} has normalisation regions -- will construct histograms for these")
                log.info("      - Loading norm regions") # layout aligned with call for systematic
                regionStrings = []
                for normReg in sam.normRegions:
                    if not isinstance(normReg[0], list):
                        c = fitConfig.getChannel(normReg[1], [normReg[0]])
                    else:
                        c = fitConfig.getChannel(normReg[1], normReg[0])
                    
                    regionStrings.append(c.regionString)
         
                normString = "".join(regionStrings)

                log.verbose(f"addSampleSpecificHists(): constructed normString {normString} for sample {sam.name}")

                tmpName = f"h{sam.name}Nom_{normString}Norm"
                if not tmpName in list(self.hists.keys()):
                    
                    """
                        if not self.readFromTree:    
                        nomName = "h%sNom_%sNorm" % (sam.name, normString)
                        self.hists[nomName] = None
                        try:
                            self.prepare.addHisto(nomName, forceNoFallback=forceNoFallback)
                        except:    
                            # assume that if no histogram is made, then it is not needed  
                            pass
                        else:
                    """

                    self.hists[tmpName] = None
                    if self.forceNorm==False and self.prepare.useCache:
                        self.hists[tmpName] = self.prepare.addHisto(tmpName, forceNoFallback=True)
                    if self.hists[tmpName] == None:
                        self.hists[tmpName] = TH1D(tmpName, tmpName, 1, 0.5, 1.5)
                        log.debug(f"addSampleSpecificHists(): building temporary histogram {tmpName}")
                        for normReg in sam.normRegions:
                            log.verbose(f"addSampleSpecificHists(): using normalisation in {normReg}")
                            if not type(normReg[0]) == "list":
                                normList = [normReg[0]]
                                c = fitConfig.getChannel(normReg[1], normList)
                            else:
                                c = fitConfig.getChannel(normReg[1], normReg[0])
                            for r in c.regions:
                                log.verbose(f"At normalisation region {r}")
                                try:
                                    s = c.getSample(sam.name)
                                except:    
                                    # assume that if no histogram is made, then it is not needed  
                                    continue

                                log.debug(f"addSampleSpecificHists(): calling prepare.read() for {s.treename}")
                                #print s.input_files
                                self.prepare.read(s.input_files, suffix=s.getTreenameSuffix(), friendTreeName=s.friendTreeName)
                                #check if specific cuts are applied to a specific sample
                                _cuts = self.cutsDict[r]
                                if s.additionalCuts != "":
                                    if c.ignoreAdditionalCuts:
                                        log.debug(f"Ignoring additional cuts in channel {c.channelName} for sample {s.name}")
                                    else:
                                        log.debug(f"Using additional cuts for sample {s.name}: '{s.additionalCuts}'")
                                        if len(_cuts.strip()) != 0:
                                            # ROOT doesn't like "()" as a cut, so we only use the string if it's non-empty
                                            _cuts = f"(({_cuts}) && ({s.additionalCuts}))"
                                        else:
                                            log.warning("No region cuts applied; only using the additional ones")
                                            _cuts = copy(s.additionalCuts)

                                # TODO: why don't we store this histogram in its proper name for a region? then it can be recycled
                                tempHist = TH1D("temp", "temp", 1, 0.5, 1.5)
                                try:
                                  self.chains[self.prepare.currentChainName].Project("temp",_cuts, \
                                                                                   str(self.lumiUnits*self.outputLumi/self.inputLumi)+" * "+"*".join(s.weights)+" * ("+_cuts+")")
                                except:
                                  log.warning(f"chainName {self.prepare.currentChainName} not found in self.chains.keys(): {self.chains.keys()}")
                                  log.warning(f"Norm histograms {tmpName} will be empty and removed")
                                  continue
                                # if the overflow bin is used for this channel, make sure the normalization takes it into account
                                nomName = f"h{s.name}Nom_{normString}Norm"
                                if c.useOverflowBin:
                                    self.hists[nomName].SetBinContent(1, self.hists[nomName].GetBinContent(1) + tempHist.Integral())
                                else:
                                    self.hists[nomName].SetBinContent(1, self.hists[nomName].GetBinContent(1) + tempHist.GetSumOfWeights())
                                del tempHist

                                log.verbose(f"Integral of nominal norm histogram {nomName} = {self.hists[nomName].GetSumOfWeights():f}")
                                #sys.exit()

                         
                        #if self.hists[tmpName].Integral() == 0: del self.hists[tmpName]
            ## Now move on to systematics, adding weights first

            ## Remove any current systematic
            #chan.getSample(sam.name).removeCurrentSystematic()

            ## first reset weight to nominal value; this won't load a histogram as the nominal one is already done 
            #self.setWeightsCutsVariable(chan, sam, regionString) 
          
            ## copy the weights to find common string -> save some memory
            #need_weights = set(copy(sam.weights))
            
            #for syst in (s for s in sorted(chan.getSample(sam.name).systDict.values(), key=lambda s: s.name) if s.type == "weight"):
                #print syst.name
                ##print syst.nominal
                ##print syst.low, syst.high

                #if syst.differentNominalTreeWeight:
                    #for x in syst.nominal: need_weights.add(x)
               
                #for x in syst.low: need_weights.add(x)
                #for x in syst.high: need_weights.add(x)
                ##need_weights.add([x for x in syst.low])
                ##need_weights.add([x for x in syst.high])

                ## TODO: find lowest common denominator of all these weights, for now we don't care
                ## 
                #pass

            #print sorted(need_weights)

            #sys.exit()

            if not self.ignoreSystematics:
                # Construct a simple double loop to ensure all the weights go first, and then all the trees
                syst_types = ["weight", "tree", "user"]
                systs_by_type = {}
                for syst_type in syst_types:
                    systs_by_type[syst_type] = [s for s in sorted(list(chan.getSample(sam.name).systDict.values()), key=lambda s: s.name) if s.type == syst_type] 

                log.info("      - Will load {} weights, {} tree-based and {} user systematics".format(len(systs_by_type["weight"]), len(systs_by_type["tree"]), len(systs_by_type["user"])))

                i = 0
                for syst_type in syst_types:
                    j = 0
                    for syst in systs_by_type[syst_type]: 
                        i += 1
                        j += 1
                        log.info(f"      - Systematic {i}/{len(list(chan.getSample(sam.name).systDict.values()))}: {syst.name}")
                        log.verbose(f"systematic type: {syst_type}")
                        log.verbose(f"current normString = {normString}")

                        # Remove any current systematic
                        chan.getSample(sam.name).removeCurrentSystematic()

                        # If rebinning is used, check if user syst has applied!
                        if self.rebin:
                           log.verbose(f"      - Checking if {syst.name} is used syst and is  used together with rebinning")
                           if syst.type=="user":
                              log.error(f"      - User syst identified: rebinning can not be used -> please change {syst.name} to weight or tree based syst")
                              log.error("exiting from HistFitter")
                              sys.exit(-1)
                           log.verbose(f"      - {syst.name} is NOT user based syst")


                        # first reset weight to nominal value
                        # NOTE: this won't actually load a histogram as the nominal one is already done 
                        self.setWeightsCutsVariable(chan, sam, regionString) 
                      
                        # this method actually calls the hard work. 
                        # NOTE: this NEEDS to not rely on this method. Now it's not parallelizable.
                        syst.PrepareWeightsAndHistos(regionString, normString, normCuts, self, fitConfig, chan, sam)
                        self.addHistoSysforNoQCD(regionString, normString, normCuts, fitConfig, chan, sam, syst)
                
                # and remove the last systematic
                chan.getSample(sam.name).removeCurrentSystematic()

        elif sam.isQCD:	
            #Add Histos for Sample-type QCD
            self.addHistoSysForQCD(regionString,normString,normCuts,chan,sam)
        return

    def channelIsBlinded(self, fitConfig, chan):
        if chan.blind or \
           (self.blindSR and (chan.channelName in fitConfig.signalChannels)) or \
           (self.blindCR and chan.channelName in fitConfig.bkgConstrainChannels) or \
           (self.blindVR and (chan.channelName in fitConfig.validationChannels)):
            return True

        return False

    def buildBlindedHistos(self, fitConfig, channel, sample):
        """
        Build blinded histograms for a fit configuration

        @param fitConfig The fit configuratio
        @param channel The channelnel
        @param sample The sample
        """
        log.debug(f"buildBlindedHistos: checking channel {channel.channelName}")

        if not sample.isBlinded(fitConfig):
            log.verbose(f"buildBlindedHistos: sample {sample.name} is not blinded, performing nothing")
            return 

        histname = sample.getHistogramName(fitConfig)

        if self.hists[histname]:
            log.verbose(f"buildBlindedHistos: histogram {histname} already exists")
            return

        log.verbose(f"buildBlindedHistos: constructing {histname}")
        self.hists[histname] = TH1D(histname, histname, channel.nBins, channel.binLow, channel.binHigh)

        log.info(f"Blinding sample {sample.name} in {channel.channelName} with the following samples:")
        for s in channel.sampleList:
            if (not s.isData) and (self.useSignalInBlindedData or s.name != fitConfig.signalSample):
                log.info(s.name)			
                self.hists[histname].Add(self.hists[s.histoName])
        
        return
    
    def makeDicts(self, fitConfig, chan):
        """
        Prepare various internal dictionaries for a channel in a fit configuration

        @param fitConfig The fit configuration
        @param chan The channel
        """
        regString = "".join(chan.regions)

        canDict = {}
        stackDict = {}
        legDict = {}
        dataNameDict = {}
        qcdNameDict = {}

        for (samName,infoList) in list(chan.infoDict.items()):
            for info in infoList:
                if info[3] == "userOverallSys":
                    continue

                if not info[0] == "Nom":
                    continue

                myKey = (info[0], regString, replaceSymbols(chan.variableName))
                if not myKey in list(canDict.keys()):
                    canDict[myKey] = TCanvas("c"+fitConfig.name+"_"+info[0]+"_"+regString+"_obs_"+replaceSymbols(chan.variableName), "c"+info[0]+"_"+regString+"_obs_"+replaceSymbols(chan.variableName),800,600,800,600)

                    stackDict[myKey] = THStack(fitConfig.name+"_"+regString+"_obs_"+replaceSymbols(chan.variableName)+"Stack"+info[0],"")

                    legDict[myKey] = TLegend(0.7,0.7,0.88,0.88)
                    legDict[myKey].SetBorderSize(0)
                    legDict[myKey].SetTextFont(42)
                    legDict[myKey].SetTextSize(0.05)
                    legDict[myKey].SetFillColor(0)
                    legDict[myKey].SetLineColor(0)

                    legDict[myKey].Clear()

                if not (regString,replaceSymbols(chan.variableName)) in list(dataNameDict.keys()):
                    dataNameDict[(regString,replaceSymbols(chan.variableName))] = ""

                if not (regString,replaceSymbols(chan.variableName)) in list(qcdNameDict.keys()):
                    qcdNameDict[(regString,replaceSymbols(chan.variableName))] = ""

                if not fitConfig.getSample(samName).isData and not fitConfig.getSample(samName).isQCD:
                    histName = "h"+samName+info[0]+"_"+regString+"_obs_"+replaceSymbols(chan.variableName)
                    self.hists[histName].SetLineColor(fitConfig.getSample(samName).color)
                    self.hists[histName].SetFillColor(fitConfig.getSample(samName).color)

                    stackDict[myKey].Add(self.hists[histName],"hist")
                    legDict[myKey].AddEntry(self.hists[histName], samName+info[0], "lf")
                elif fitConfig.getSample(samName).isQCD:
                    nomName = f"h{samName}Nom_{regString}_obs_{replaceSymbols(chan.variableName)}"
                    self.hists[nomName].SetLineColor(fitConfig.getSample(samName).color)
                    self.hists[nomName].SetFillColor(fitConfig.getSample(samName).color)

                    lowName = f"h{samName}Low_{regString}_obs_{replaceSymbols(chan.variableName)}"
                    self.hists[lowName].SetLineColor(fitConfig.getSample(samName).color)
                    self.hists[lowName].SetFillColor(fitConfig.getSample(samName).color)

                    highName = f"h{samName}High_{regString}_obs_{replaceSymbols(chan.variableName)}"
                    self.hists[highName].SetLineColor(fitConfig.getSample(samName).color)
                    self.hists[highName].SetFillColor(fitConfig.getSample(samName).color)

                    qcdNameDict[(regString,replaceSymbols(chan.variableName))] = nomName
                else:
                    histName = f"h{samName}_{regString}_obs_{replaceSymbols(chan.variableName)}"
                    self.hists[histName].SetLineColor(fitConfig.getSample(samName).color)
                    dataNameDict[(regString,replaceSymbols(chan.variableName))] = histName

        for info in list(stackDict.keys()):
            canDict[info].cd()

            infoKey = (info[1], info[2])
            if not qcdNameDict[infoKey] == "":
                stackDict[info].Add(self.hists[qcdNameDict[infoKey]],"hist")
                legDict[info].AddEntry(self.hists[qcdNameDict[infoKey]],"QCDNom","lf")

            if not dataNameDict[infoKey] == "":
                legDict[info].AddEntry(self.hists[dataNameDict[infoKey]],"Data","lf")
                self.hists[dataNameDict[infoKey]].SetStats(False)
                self.hists[dataNameDict[infoKey]].GetYaxis().SetTitleOffset(1.3)
                self.hists[dataNameDict[infoKey]].Draw()
                self.hists[dataNameDict[infoKey]].GetXaxis().SetTitle(chan.variableName)
                self.hists[dataNameDict[infoKey]].GetYaxis().SetTitle("entries")
                stackDict[info].Draw("same")
                self.hists[dataNameDict[infoKey]].Draw("same")

                if self.hists[dataNameDict[infoKey]].GetBinContent(self.hists[dataNameDict[infoKey]].GetMaximumBin()) > stackDict[info].GetMaximum():
                    rangeMax = self.hists[dataNameDict[infoKey]].GetBinContent(self.hists[dataNameDict[infoKey]].GetMaximumBin())
                else:
                    rangeMax = stackDict[info].GetMaximum()

                if self.hists[dataNameDict[infoKey]].GetBinContent(self.hists[dataNameDict[infoKey]].GetMinimumBin()) < stackDict[info].GetMinimum():
                    rangeMin = self.hists[dataNameDict[infoKey]].GetBinContent(self.hists[dataNameDict[infoKey]].GetMinimumBin())
                else:
                    rangeMin = stackDict[info].GetMinimum()

                self.hists[dataNameDict[infoKey]].GetYaxis().SetRangeUser(rangeMin-0.1*rangeMin,rangeMax+0.1*rangeMax)
            else:
                stackDict[info].Draw()
                stackDict[info].GetHistogram().GetYaxis().SetTitleOffset(1.3)
                stackDict[info].GetHistogram().GetXaxis().SetTitle(chan.variableName)
                stackDict[info].GetHistogram().GetYaxis().SetTitle("entries")
                stackDict[info].Draw()

                rangeMax = stackDict[info].GetHistogram().GetMaximum()
                rangeMin = stackDict[info].GetHistogram().GetMinimum()

                stackDict[info].GetHistogram().GetYaxis().SetRangeUser(rangeMin-0.1*rangeMin,rangeMax+0.1*rangeMax)

            legDict[info].Draw()

            plotsDir = f"plots/{self.analysisName}/{fitConfig.name}"
            mkdir_p(plotsDir)

            outputPNG = f"{plotsDir}/stack{info[1]}_obs_{info[2]}_{info[0]}.png"
            canDict[info].SaveAs(outputPNG)

            self.canvasList.append(canDict[info])
            self.stackList.append(stackDict[info])
    
    def outputRoot(self):
        """
        Write out the histograms defined in the analysis to a data file
        """
        outputRootFile = None
        if self.readFromTree:
            outputRootFile = TFile.Open(self.histCacheFile, "RECREATE")
        elif self.prepare.recreate:
            outputRootFile = self.prepare.cacheFile
            if not outputRootFile.IsOpen():
                outputRootFile = outputRootFile.Open(self.histCacheFile, "UPDATE")

        if outputRootFile:
            log.info(f"Storing histograms in file: {self.histCacheFile}")

            outputRootFile.cd()

            # list comprehension faster than filter with lambda
            hists_to_write = [hist for hist in list(self.hists.values()) if hist is not None]
            hists_sorted_by_name = sorted(hists_to_write, key=TObject.GetName)
            for hist in hists_sorted_by_name:
                if hist:
                    hist.Write(hist.GetName(), TObject.kOverwrite)
            outputRootFile.Close()

if "configMgr" in vars():
    raise RuntimeError("ConfigManager already exists, no multiple imports allowed!")

# Instantiate the singleton

configMgr = ConfigManager()
