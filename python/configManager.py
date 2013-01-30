from ROOT import THStack,TLegend,TCanvas,TFile,std,TH1F
from ROOT import ConfigMgr,FitConfig,ChannelStyle #this module comes from gSystem.Load("libSusyFitter.so")
from prepareHistos import TreePrepare,HistoPrepare
from copy import deepcopy
from histogramsManager import histMgr
from logger import Logger
import os
from ROOT import gROOT

gROOT.SetBatch(True)
log = Logger('ConfigManager')

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def replaceSymbols(s):
    s = s.replace("/","").replace("*","").replace("(","").replace(")","")
    return s

class ConfigManager(object):
    """
    Singleton manager class to store the configuration information
    """
    _instance = None

    def __new__(cls,*args,**kwargs):
        """
        Make singleton by only instanciating once
        """
        if not cls._instance:
            cls._instance = super(ConfigManager,cls).__new__(cls,*args,**kwargs)
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
        self.nTOYs =- 1 #<=0 means to use real data
        self.calculatorType = 0 # frequentist calculator
        self.testStatType = 3   # one-sided test statistic
        self.useCLs = True # use CLs for upper limits, or not
        self.doExclusion = True # true = exclusion, false = discovery test
        self.fixSigXSec = False # true = fix SigXSec by nominal, +/-1sigma
        self.runOnlyNominalXSec = False #t true = for fixed xsec, run only nominal fit and not +/- 1 sigma fits
        self.nPoints = 20 # number of points in upper limit evaluation
        self.seed = 0 # seed for random generator. default is clock
        self.muValGen = 0.0 # mu_sig used for toy generation
        self.toySeedSet = False # Set the seed for toys
        self.toySeed = 0 # CPU clock, default
        self.useAsimovSet = False # Use the Asimov dataset
        self.blindSR = False # Blind the SRs only
        self.blindCR = False # Blind the CRs only
        self.blindVR = False # Blind the VRs only
        self.useSignalInBlindedData = False

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

        self.includeOverallSys = True # Boolean to chose if HistoSys should also have OverallSys
        self.readFromTree = False # Boolean to chose if reading histograms from tree will also write to file
        self.plotHistos = None # Boolean to chose to plot out the histograms
        self.removeEmptyBins = False # Boolean to chose to remove empty bins from data histogram on plot
        self.executeHistFactory = True # Boolean to chose to execute HistFactory
        self.writeXML = False # Boolean to chose whether to write HistFactory XML files by hand
        self.printHistoNames = False # Print out the names of generated histograms
        self.doHypoTest = False

        self.fitConfigs = [] # fitConfig object
        self.prepare = None # PrepareHistos object

        self.histCacheFile = ""
        self.fileList = [] # File list to be used for tree production
        self.treeName = ''
        self.bkgParName = ''
        self.bkgCorrVal = -1.
        return

    def setLumiUnits(self,unit):
        # 1=fb-1, 1000=pb-1, etc.
        if unit == "fb-1" or unit == "fb":
            self.lumiUnits = 1.0
        elif unit == "pb-1" or unit == "pb":
            self.lumiUnits = 1000.0
        else:
            raise TypeError("lumi unit '%s' is not supported."%unit)
        return

    def addTopLevelXML(self, input, name=""):
        log.warning("addTopLevelXML() is deprecated and has been renamed addFitConfig()")
        return self.addFitConfig(input, name)

    def addFitConfig(self, input, name=""):
        from fitConfig import fitConfig
        if len(name) > 0:
            newName = name
        elif isinstance(input, str):
            newName = input
        elif isinstance(input, fitConfig):
            newName = input.name
        else:
            raise RuntimeError("Logic error in addFitConfig")

        #check that newName is not already used
        for tl in self.fitConfigs:
            if tl.name == newName:
                raise RuntimeError("fitConfig %s already exists in configManager. Please use a different name." %
                                   newName )
            pass

        #create new fitConfig object and return pointer
        if isinstance(input, fitConfig):
            newFitConfig = input.Clone(newName)
        else:
            newFitConfig = fitConfig(newName)
            pass

        newFitConfig.setWeights(self.weights)
        newFitConfig.removeEmptyBins=self.removeEmptyBins

        self.fitConfigs.append(newFitConfig)
        log.info("Created Fit Config: %s" % newName)

        return self.fitConfigs[len(self.fitConfigs)-1]

    def addTopLevelXMLClone(self, obj, name):
        log.warning("addTopLevelXMLClone() has been deprecated and is now addFitConfigClone()")
        return self.addFitConfigClone(obj, name)

    def addFitConfigClone(self, obj, name):
        return self.addFitConfig(obj, name)

    def removeTopLevelXML(self, name):
        log.warning("removeTopLevelXML() has been deprecated and is now removeFitConfig()")
        self.removeFitConfig(name)
        return

    def removeFitConfig(self, name):
        for i in xrange(0,len(self.fitConfigs)):
            tl = self.fitConfigs[i]
            if tl.name == name:
                self.fitConfigs.pop(i)
                return
        log.warning("fitConfig named '%s' does not exist. Cannot be removed." % name)
        return

    def getTopLevelXML(self, name):
        log.warning("getTopLevelXML() has been deprecated and is now getFitConfig()")
        return self.getFitConfig(name)

    def getFitConfig(self, name):
        for tl in self.fitConfigs:
            if tl.name == name:
                return tl
        log.warning("fitConfig named '%s' does not exist. Cannot be returned." % name)
        return 0

    def initialize(self):
        log.info("Initializing...")
        if self.histCacheFile == '':
            tmpName = "data/%s.root" % self.analysisName
            log.info("Giving default name histCacheFile: %s" % tmpName)
            self.histCacheFile = tmpName
            pass
        if self.inputLumi is None and self.outputLumi is None:
            self.inputLumi = 1.0
            self.outputLumi = 1.0
            pass

        # Propagate stuff down from config manager
        log.info("  -initialize python objects...")
        for tl in self.fitConfigs:
            tl.initialize()
            for chan in tl.channels:
                chan.initialize()
                for sam in chan.sampleList:
                    if not sam.isData and not sam.isQCD and not sam.isDiscovery:
                        pass
                        for (name,syst) in self.systDict.items():
                            if not name in chan.getSample(sam.name).systDict.keys():
                                chan.getSample(sam.name).addSystematic(syst)
                        ## MB: sample-specific weights (for example cuts)
                        ##     Make sure these weights propagate down to actual sample and systematics
                        for w in sam.tempWeights: sam.addWeight(w) 
                    elif sam.isQCD or sam.isData:
                        chan.getSample(sam.name).setWrite(False)
        
        log.info("  -initialize global histogram dictionary...")
        for tl in self.fitConfigs:
            for chan in tl.channels:
                for sam in chan.sampleList:
                    regString = "".join(chan.regions)

                    nomName = "h%sNom_%s_obs_%s" % (sam.name, regString, replaceSymbols(chan.variableName))
                    highName = "h%sHigh_%s_obs_%s" % (sam.name, regString, replaceSymbols(chan.variableName))
                    lowName = "h%sLow_%s_obs_%s" % (sam.name, regString, replaceSymbols(chan.variableName))

                    if sam.isData:
                        if (self.blindSR and (chan.channelName in tl.signalChannels)) or \
                           (self.blindCR and (chan.channelName in tl.bkgConstrainChannels)) or \
                           (self.blindVR and (chan.channelName in tl.validationChannels)):
                            sam.blindedHistName = "h%s%sBlind_%s_obs_%s" % (tl.name, sam.name, regString,
                                                                            replaceSymbols(chan.variableName))
                            if not sam.blindedHistName in self.hists.keys():
                                self.hists[sam.blindedHistName] = None
                        else:
                            histName = "h%s_%s_obs_%s" % (sam.name, regString, replaceSymbols(chan.variableName))
                            if not histName in self.hists.keys():
                                self.hists[histName] = None
                    elif sam.isQCD:
                        systName = "h%sSyst_%s_obs_%s" % (sam.name, regString, replaceSymbols(chan.variableName))
                        statName = "h%sStat_%s_obs_%s" % (sam.name, regString, replaceSymbols(chan.variableName))

                        if not nomName in self.hists.keys():
                            self.hists[nomName] = None

                        if not highName in self.hists.keys():
                            self.hists[highName] = None

                        if not lowName in self.hists.keys():
                            self.hists[lowName] = None

                        if not systName in self.hists.keys():
                            self.hists[systName] = None

                        if not statName in self.hists.keys():
                            self.hists[statName] = None

                        if chan.variableName == "cuts":
                            nHists = len(chan.regions)
                        else:
                            nHists = chan.nBins

                        for iBin in xrange(1, nHists+1):
                            if not "%s_%s" % (nomName, str(iBin)) in self.hists.keys():
                                self.hists["%s_%s" % (nomName, str(iBin))] = None

                            if not "%s_%s" % (highName, str(iBin)) in self.hists.keys():
                                self.hists["%s_%s" % (highName, str(iBin))] = None

                            if not "%s_%s" % (lowName, str(iBin)) in self.hists.keys():
                                self.hists["%s_%s" % (lowName, str(iBin))] = None

                    elif not sam.isDiscovery:
                        if not nomName in self.hists.keys():
                            self.hists[nomName] = None

                        for (name, syst) in chan.getSample(sam.name).systDict.items():
                            highSystName = "h%s%sHigh_%s_obs_%s" % (sam.name, syst.name, regString,
                                                                    replaceSymbols(chan.variableName))
                            if not highSystName in self.hists.keys():
                                self.hists[highSystName] = None

                            lowSystName = "h%s%sLow_%s_obs_%s" % (sam.name, syst.name, regString,
                                                                  replaceSymbols(chan.variableName))
                            if not lowSystName in self.hists.keys():
                                self.hists[lowSystName] = None

                            if syst.merged:
                                mergedName = "".join(syst.sampleList)

                                nomMergedName = "h%sNom_%s_obs_%s" % (mergedName, regString,
                                                                      replaceSymbols(chan.variableName))
                                if not nomMergedName in self.hists.keys():
                                    self.hists[nomMergedName] = None

                                highMergedName = "h%s%sHigh_%s_obs_%s" % (mergedName, syst.name, regString,
                                                                          replaceSymbols(chan.variableName))
                                if not highMergedName in self.hists.keys():
                                    self.hists[highMergedName] = None

                                lowMergedName = "h%s%sLow_%s_obs_%s" % (mergedName, syst.name, regString,
                                                                        replaceSymbols(chan.variableName))
                                if not lowMergedName in self.hists.keys():
                                    self.hists[lowMergedName] = None

        if self.readFromTree:
            log.info("  -build TreePrepare()...")
            self.prepare = TreePrepare()
            if self.plotHistos is None:    #set plotHistos if not already set by user
                self.plotHistos = False  #this is essentially for debugging
                pass
        else:
            log.info("  -build HistoPrepare()...")
            self.prepare = HistoPrepare(self.histCacheFile)

        #C++ alter-ego
        log.info("  -initialize C++ mgr...")
        self.initializeCppMgr()

        log.info("  -propagate file list and tree names...")
        self.propagateFileList() # propagate file lists down the tree

        ## Assume that all tree names have been set
        self.propagateTreeName()

        #Summary
        self.Print() 
        return

    def initializeCppMgr(self):
        # settings for hypothesis test
        self.cppMgr.m_doHypoTest = self.doHypoTest
        self.cppMgr.setNToys( self.nTOYs )
        self.cppMgr.setCalcType( self.calculatorType )# frequentist calculator
        self.cppMgr.setTestStatType( self.testStatType )  # one-sided test statistic
        self.cppMgr.setCLs( self.useCLs )
        self.cppMgr.setExclusion( self.doExclusion )
        self.cppMgr.setfixSigXSec( self.fixSigXSec )
        self.cppMgr.setRunOnlyNominalXSec( self.runOnlyNominalXSec )
        self.cppMgr.setNPoints( self.nPoints )
        self.cppMgr.setSeed( self.toySeed )
        self.cppMgr.setMuValGen( self.muValGen )
        self.cppMgr.setUseAsimovSet( self.useAsimovSet)

        if self.outputFileName:
            self.cppMgr.m_outputFileName = self.outputFileName
            self.cppMgr.m_saveTree=True

        #Fill FitConfigs from TopLevelXMLs
        for fc in self.fitConfigs:
            cppFC = self.cppMgr.addFitConfig(fc.name)
            cppFC.m_inputWorkspaceFileName = fc.wsFileName
            cppFC.m_Lumi = self.lumiUnits*self.outputLumi
            cppFC.m_hypoTestName = fc.hypoTestName
            if not fc.signalSample is None:
                cppFC.m_signalSampleName = fc.signalSample
     
            #CR/SR/VR channels
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

                 # Plot cosmetics per fitConfig 
                 style.setDataColor(fc.dataColor)
                 style.setTotalPdfColor(fc.totalPdfColor)
                 style.setErrorLineColor(fc.errorLineColor)
                 style.setErrorLineStyle(fc.errorLineStyle)
                 style.setErrorFillColor(fc.errorFillColor)
                 style.setErrorFillStyle(fc.errorFillStyle)
                 style.setRemoveEmptyBins = self.removeEmptyBins
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
        log.info("fixSigXSec: %s" % self.fixSigXSec)
        log.info("runOnlyNominalXSec: %s" % self.runOnlyNominalXSec)
        log.info("Systematics: %s" % self.systDict.keys())
        log.debug("Cuts Dictionary: %s" % self.cutsDict)
        log.info("readFromTree: %s" % self.readFromTree)
        log.info("plotHistos: %s" % self.plotHistos)
        log.info("executeHistFactory: %s" % self.executeHistFactory)
        log.info("fitConfig objects:")
        for tl in self.fitConfigs:
            log.info("  %s" % tl.name)
            for c in tl.channels:
                log.info("    %s: %s" % (c.name, c.systDict.keys()))
        log.info("C++ ConfigMgr status: %s" % self.cppMgr.m_status)
        log.info("Histogram names: (set log level DEBUG)")
        configMgr.printHists()
        log.info("Chain names: (set log level DEBUG & note chains are only generated with -t)")
        configMgr.printChains()
        log.info("File names: (set log level DEBUG)")
        configMgr.printFiles()
        log.info("Input tree names: (set log level DEBUG)")
        configMgr.printTreeNames()
        log.info("*-------------------------------------------------*\n")
        return

    def printHists(self):
        histList = self.hists.keys()
        histList.sort()
        for hist in histList:
            log.debug(hist)
        return

    def printChains(self):
        chainList = self.chains.keys()
        chainList.sort()
        for chain in chainList:
            log.debug(chain)
        return

    def printFiles(self):
        log.debug("ConfigManager:")
        log.debug(str(self.fileList))

        for fitConfig in self.fitConfigs:
            log.debug("  fitConfig: %s " % fitConfig.name)
            log.debug("             %s " % str(fitConfig.files))

            for channel in fitConfig.channels:
                log.debug("             Channel: %s" % channel.name)
                log.debug("             %s" % str(channel.files))

                for sample in channel.sampleList:
                    log.debug("             ---> Sample: %s" % sample.name)
                    log.debug("                          %s" % str(sample.files))

                    for (systName,syst) in sample.systDict.items():
                        log.debug("                            ---> Systematic: %s" % syst.name)
                        log.debug("                                       Low : %s" % str(syst.filesLo))
                        log.debug("                                       High: %s" % str(syst.filesHi))
        return

    def printTreeNames(self):
        if str(self.treeName).strip() == "":
            log.debug("No tree used")
            return

        log.debug("ConfigManager:")
        log.debug(str(self.treeName).strip())

        for fitConfig in self.fitConfigs:
            log.debug("  fitConfig: %s" % fitConfig.name)
            log.debug("             %s" % str(fitConfig.treeName))

            for channel in fitConfig.channels:
                log.debug("    ---> Channel: %s" % channel.name)
                log.debug("                  %s" % str(channel.treeName))

                for sample in channel.sampleList:
                    log.debug("           ---> Sample: %s" % sample.name)
                    log.debug("                        %s" % str(sample.treeName))

                    for (systName,syst) in sample.systDict.items():
                        log.debug("                   ---> Systematic: %s" % syst.name)
                        log.debug("                        Low : %s" % str(syst.treeLoName))
                        log.debug("                        High: %s" % str(syst.treeHiName))
        return

    def setFileList(self,filelist):
        """
        Set file list for config manager.
        This will be used as default for top level xmls that don't specify
        their own file list.
        """
        self.fileList = filelist

    def setFile(self,file):
        """
        Set file list for config manager.
        This will be used as default for top level xmls that don't specify
        their own file list.
        """
        self.fileList = [file]

    def propagateFileList(self):
        """
        Propagate the file list downwards.
        """
        # propagate our file list downwards (if we don't have one,
        # this will result in the propagation of the files belonging
        # to our top level xml)
        for fc in self.fitConfigs:
            fc.propagateFileList(self.fileList)

    def setTreeName(self,treeName):
        self.treeName = treeName
        return

    def propagateTreeName(self):
        for fc in self.fitConfigs:
            fc.propagateTreeName(self.treeName)
            pass
        return

    def executeAll(self):
        for tl in self.fitConfigs:
            self.execute(tl)
        return

    def execute(self, fitConfig):
        """
        Make or get the histograms and generate the XML
        """
        log.info("Preparing histograms and/or workspace for fitConfig %s\n"%fitConfig.name)

        if self.plotHistos:
            cutHistoDict = {}
            cutStackDict = {}
            varStackDict = {}
            varSUSYDict = {}
            varDataDict = {}
        systDict = {}

        for (name, syst) in self.systDict.items():
            systDict[name] = syst

        for (name, syst) in fitConfig.systDict.items():
            if not name in systDict.keys():
                systDict[name] = syst
            else:
                raise(Exception, "Syst name %s already defined at global level. Rename for top level %s", (name, fitConfig.name))

        # Build channel string and cuts for normalization
        normRegions = []
        normString = ""
        normCuts = ""
        for (iChan,chan) in enumerate(fitConfig.channels):
            if not chan.channelName in fitConfig.validationChannels:
                normString = "".join(chan.regions)
                normCutsList = [ "(%s) || " % (self.cutsDict[reg]) for reg in chan.regions ]
                normCuts = "".join(normCutsList)

                for reg in chan.regions:
                    normRegions.append(reg)
        
        normCuts = normCuts.rstrip(" || ")
        for (iChan, chan) in enumerate(fitConfig.channels):
            for (iSam, sam) in enumerate(chan.sampleList):
                chan.infoDict[sam.name] = [("Nom", self.nomName, sam.weights, "")]
                if not sam.isData and not sam.isQCD:
                    for (systName, syst) in sam.systDict.items():
                        ###depending on the systematic type: chan.infoDict[sam.name].append(...)
                        self.appendSystinChanInfoDict(chan, sam, systName, syst)

        for (iChan, chan) in enumerate(fitConfig.channels):
            log.info("Channel: %s" % chan.name)
            regionString = "".join(chan.regions)
            self.prepare.channel = chan
            
            sampleListRun = deepcopy(chan.sampleList)
            #for (iSam, sam) in enumerate(fitConfig.sampleList):
            for (iSam, sam) in enumerate(sampleListRun):
                log.info("  Sample: %s" % sam.name)                
                # Run over the nominal configuration first
                # Set the weights, cuts, weights
                self.setWeightsCutsVariable(chan, sam, regionString)
                #depending on the sample type,  the Histos and up/down weights are added
                self.addSampleSpecificHists(fitConfig, chan, sam, regionString, normRegions, normString, normCuts)

        #post-processing 1: loop for norm systematics
        for chan in fitConfig.channels:
            regionString = "".join(chan.regions)
            
            for sam in chan.sampleList:
                for syst in sam.systDict.values():
                    if syst.method == "userNormHistoSys":
                        nomName = "h%sNom_%s_obs_%s" % (sam.name, regionString, replaceSymbols(chan.variableName) )
                        highName = "h%sHigh_%s_obs_%s" % (sam.name, regionString, replaceSymbols(chan.variableName) )
                        lowName = "h%sLow_%s_obs_%s" % (sam.name, regionString, replaceSymbols(chan.variableName) )
                        
                        syst.PrepareGlobalNormalization(normString, self, fitConfig, chan, sam)
                        sam.addHistoSys(syst.name, nomName, highName, lowName, False, True, False, False, sam.name, normString)

        #post-processing 2: swapping of overall systematics for specified channel by systematics from ohter channel
        for chan in fitConfig.channels:
            # only consider channels for which a remap channel has been defined.
            if len(chan.remapSystChanName) == 0:
                continue

            log.info("For overallSys: now setting systematics of channel <%s> to those of channel: <%s>"%(chan.name,chan.remapSystChanName))
            rc = fitConfig.getChannelByName(chan.remapSystChanName)
            # loop over overallSystematics of all samples, and swap for those of remap channel
            for sam in chan.sampleList:
                if not sam.allowRemapOfSyst:
                    continue

                rs = rc.getSample(sam.name)
                for osys in sam.overallSystList:
                    if not osys.allowRemapOfSyst:
                        continue

                    rsys = rs.getOverallSys(osys[0]) # get replacement overall systematic, by name
                    if rsys is None:
                        log.warning("For channel %s and sample %s, replacement systematic %s could not be found. Skipping replacement of this overall syst." % (chan.name,sam.name,osys[0]))
                        continue

                    log.info("For channel %s and sample %s, replacement of systematic %s from %s." % (chan.name,sam.name,osys[0],rc.name))
                    sam.replaceOverallSys(rsys)
                    pass

        # Build blinded histograms here
        for (iChan, chan) in enumerate(fitConfig.channels):
            for sam in chan.sampleList:
                if sam.isData:
                    self.buildBlindedHistos(fitConfig, chan, sam)
                else:
                    pass
        
        if self.plotHistos:
            mkdir_p("plots/%s" % self.analysisName)
            for (iChan,chan) in enumerate(fitConfig.channels):
                if chan.hasDiscovery:
                    continue
                self.makeDicts(fitConfig, chan)
        
        self.outputRoot()
        
        if self.executeHistFactory:
            if self.writeXML:
                fitConfig.writeXML()   #<--- this internally calls channel.writeXML()
                fitConfig.executehist2workspace()
            else:
                fitConfig.writeWorkspaces()       

    def appendSystinChanInfoDict(self, chan, sam, systName, syst):
        log.debug("appendSystinChanInfoDict: appending info:")
        log.debug("  CHAN %s" % chan.name)
        log.debug("  SAM %s" % sam.name)
        log.debug("  SYST %s" % systName)
        log.debug("  TYPE %s" % syst.type)
        log.debug("  METHOD %s" % syst.method)
        log.debug("  LOW %s" % str(syst.low))
        log.debug("  HIGH %s" % str(syst.high))
        
        if syst.type == "tree":
            chan.infoDict[sam.name].append((systName+"High",syst.high,sam.weights,syst.method))
            chan.infoDict[sam.name].append((systName+"Low",syst.low,sam.weights,syst.method))
        elif syst.type == "weight":
            chan.infoDict[sam.name].append((systName+"High",self.nomName,syst.high,syst.method))
            chan.infoDict[sam.name].append((systName+"Low",self.nomName,syst.low,syst.method))
        else:
            chan.infoDict[sam.name].append((systName,syst.high,syst.low,syst.method))
        return

    def addHistoSysforNoQCD(self, regionString, normString, normCuts, fitConfig, chan, sam, syst):
        nomName = "h%sNom_%s_obs_%s" % (sam.name, regionString, replaceSymbols(chan.variableName) )
        highName = "h%s%sHigh_%s_obs_%s" % (sam.name, syst.name, regionString, replaceSymbols(chan.variableName) )
        lowName = "h%s%sLow_%s_obs_%s" % (sam.name, syst.name, regionString, replaceSymbols(chan.variableName) )

        if syst.method == "histoSys":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, False, False)
        elif syst.method == "histoSysOneSide":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, False, False, False, True)
        elif syst.method == "histoSysOneSideSym":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, False, False, True, True)
        elif syst.method == "overallSys":
            highIntegral = configMgr.hists[highName].Integral()
            lowIntegral = configMgr.hists[lowName].Integral()
            nomIntegral = configMgr.hists[nomName].Integral()
            try:
                overallSystHigh = highIntegral / nomIntegral
            except ZeroDivisionError:
                log.warning("    generating High overallSys for %s syst=%s nom=%g high=%g low=%g" % (nomName, syst.name, nomIntegral, highIntegral, lowIntegral))
                overallSystHigh = 1.0
            try:
                overallSystLow = lowIntegral / nomIntegral
            except ZeroDivisionError:
                log.warning("    generating Low overallSys for %s syst=%s nom=%g high=%g low=%g" % (nomName, syst.name, nomIntegral, highIntegral, lowIntegral))
                overallSystLow = 1.0
            chan.getSample(sam.name).addOverallSys(syst.name, overallSystHigh, overallSystLow)
        elif syst.method == "userOverallSys":
            chan.getSample(sam.name).addOverallSys(syst.name, syst.high, syst.low)
        elif syst.method == "overallHistoSys":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, True,  False)
        elif syst.method == "overallNormSys":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, True,  True, False, False, sam.name, normString)
        elif syst.method == "overallNormHistoSys":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, True,  True, False, False, sam.name, normString)
        elif syst.method == "overallNormHistoSysOneSide":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, True,  True, False, True,  sam.name, normString)
        elif syst.method == "overallNormHistoSysOneSideSym":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, True,  True, True,  True,  sam.name, normString)
        elif syst.method == "normHistoSys":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, False, True, False, False, sam.name, normString)
        elif syst.method == "normHistoSysOneSide":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, False, True, False, True,  sam.name, normString)
        elif syst.method == "normHistoSysOneSideSym":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, False, True, True,  True,  sam.name, normString)
        elif syst.method == "userHistoSys" or syst.method == "userNormHistoSys":
            if configMgr.hists[highName] is None:
                configMgr.hists[highName] = histMgr.buildUserHistoSysFromHist(highName,  syst.high,  configMgr.hists[nomName])
            if configMgr.hists[lowName] is None:
                configMgr.hists[lowName] = histMgr.buildUserHistoSysFromHist(lowName,  syst.low,  configMgr.hists[nomName])
            if syst.method == "userHistoSys":
                chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, False, False)
            pass
        elif syst.method == "shapeSys":
            if syst.merged:
                mergedName = "".join(syst.sampleList)
                
                nomMergedName = "h%sNom_%s_obs_%s" % (mergedName, regionString, replaceSymbols(chan.variableName) )
                highMergedName = "h%sHigh_%s_obs_%s" % (mergedName, regionString, replaceSymbols(chan.variableName) )
                lowMergedName = "h%sLow_%s_obs_%s" % (mergedName, regionString, replaceSymbols(chan.variableName) )
                
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
            chan.getSample(sam.name).shapeSystList.append(('shape_%s_%s_%s_obs_%s' % (syst.name, sam.name,
                                                                                      regionString,
                                                                                      replaceSymbols(chan.variableName)),
                                                           nomName+"Norm", syst.constraint, "", "", "", ""))
        else:
            log.error("ERROR don't know what to do with %s %s"%(syst.name,syst.method))
        return

    def addHistoSysForQCD(self,regionString,normString,normCuts,chan,sam):
        self.prepare.addQCDHistos(sam,chan.useOverflowBin,chan.useUnderflowBin)

        if chan.variableName == "cuts":
            nHists = len(chan.regions)
        else:
            nHists = chan.nBins

        prefixNom = "h%sNom_%s_obs_%s" % (sam.name, regionString, replaceSymbols(chan.variableName))
        prefixHigh = "h%sHigh_%s_obs_%s" % (sam.name, regionString, replaceSymbols(chan.variableName))
        prefixLow = "h%sLow_%s_obs_%s" % (sam.name, regionString, replaceSymbols(chan.variableName))

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
                log.warning("Error generating HistoSys for %s syst=%s nom=%g high=%g low=%g" % (nomName,"QCDNorm_"+regionString,nomIntegral,highIntegral,lowIntegral))
            
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

            for iBin in xrange(1,nHists+1):
                qcdSam = sam.Clone()
                qcdSam.name = "%s_%s_%s" % (sam.name, regionString, str(iBin))
                chan.addSample(qcdSam)
                chan.getSample(qcdSam.name).setWrite(True)
                chan.getSample(qcdSam.name).setHistoName("h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName)+"_"+str(iBin))
                chan.getSample(qcdSam.name).addHistoSys("NormQCD"+regionString+"_"+str(iBin),prefixNom+"_"+str(iBin),prefixHigh+"_"+str(iBin),prefixLow+"_"+str(iBin),False,False)
        else:
            raise Exception("Incorrect systematic method specified for QCD: %s" % getSample(sam.name).qcdSyst)

    def setWeightsCutsVariable(self,chan,sam,regionString):
        if not sam.isData and not sam.isQCD and not sam.isDiscovery:
            self.prepare.weights = str(self.lumiUnits*self.outputLumi/self.inputLumi)
            self.prepare.weights += " * " + " * ".join(sam.weights)
            if self.readFromTree and not sam.isDiscovery:
                    treeName = sam.treeName
                    if treeName == '': 
                        treeName = sam.name+self.nomName
                    self.prepare.read(treeName, sam.files)
        else:
            self.prepare.weights = "1."
            if self.readFromTree:
                treeName = sam.treeName
                if treeName == '': 
                    treeName = sam.name
                self.prepare.read(treeName, sam.files)

        if len(sam.cutsDict.keys()) == 0:
            if not chan.variableName == "cuts":
                self.prepare.cuts = self.cutsDict[regionString]
        else:
            if not chan.variableName == "cuts":
                self.prepare.cuts = sam.cutsDict[regionString]

        if sam.unit == "GeV":
            self.prepare.var = chan.variableName
        elif sam.unit == "MeV" and chan.variableName.find("/") < 0 and not chan.variableName.startswith("n"):
            self.prepare.var = chan.variableName+"/1000."

        return

    def addSampleSpecificHists(self,fitConfig,chan,sam,regionString,normRegions,normString,normCuts):
        log.debug('addSampleSpecificHists()')
        histoName = "h%s_%s_obs_%s" % (sam.name, regionString, replaceSymbols(chan.variableName) )

        if sam.isData:
            if chan.channelName in fitConfig.signalChannels:
                if self.blindSR:
                    chan.addData(sam.blindedHistName)
                else:
                    self.prepare.addHisto(histoName, useOverflow=chan.useOverflowBin, useUnderflow=chan.useUnderflowBin)
                    chan.addData(histoName)
            elif chan.channelName in fitConfig.bkgConstrainChannels:
                if self.blindCR:
                    chan.addData(sam.blindedHistName)
                else:
                    self.prepare.addHisto(histoName, useOverflow=chan.useOverflowBin, useUnderflow=chan.useUnderflowBin)
                    chan.addData(histoName)
            elif chan.channelName in fitConfig.validationChannels:
                if self.blindVR:
                    chan.addData(sam.blindedHistName)
                else:
                    self.prepare.addHisto(histoName, useOverflow=chan.useOverflowBin, useUnderflow=chan.useUnderflowBin)
                    chan.addData(histoName)
            else:
                self.prepare.addHisto(histoName, useOverflow=chan.useOverflowBin, useUnderflow=chan.useUnderflowBin)
                chan.addData(histoName)
        elif not sam.isQCD and not sam.isDiscovery:
            tmpName="h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName)
            if not len(sam.shapeFactorList):
                self.prepare.addHisto(tmpName, useOverflow=chan.useOverflowBin, useUnderflow=chan.useUnderflowBin)
                ###check that nominal sample is not empty for that channel
                if self.hists[tmpName].GetSum() == 0.0:
                    log.warning("    ***nominal sample %s is empty for channel %s. Remove from PDF.***"%(sam.name, chan.name))
                    chan.removeSample(sam.name)
                #    del self.hists[tmpName]
                #    self.hists[tmpName]=None    ## MB : do not delete, else cannot rerun later with -w
                    return
            else:
                self.hists[tmpName] = TH1F(tmpName, tmpName, chan.nBins, chan.binLow, chan.binHigh)
                for iBin in xrange(self.hists[tmpName].GetNbinsX()+1):
                    self.hists[tmpName].SetBinContent(iBin+1, 1.)
            chan.getSample(sam.name).setHistoName(tmpName)

            if not sam.normRegions and (not sam.noRenormSys): 
                needsNorm = False
                for sys in sam.systDict.values():
                    if sys.method == "userNormHistoSys" \
                           or sys.method == "normHistoSys" \
                           or sys.method == "normHistoSysOneSide" \
                           or sys.method == "normHistoSysOneSideSym" \
                           or sys.method == "overallNormSys" \
                           or sys.method == "overallNormHistoSys" \
                           or sys.method == "overallNormHistoSysOneSide" \
                           or sys.method == "overallNormHistoSysOneSideSym":
                        log.error("    %s needs normRegions because of %s of type %s but no normalization regions specified. This is not safe,  please fix." % (sam.name, sys.name, sys.method))
                        needsNorm = True
                        break
                if needsNorm:
                    normChannels=[]
                    tl=sam.parentChannel.parentTopLvl
                    for ch in tl.channels:
                        if (ch.channelName in tl.bkgConstrainChannels) or (ch.channelName in tl.signalChannels):
                            normChannels.append((ch.regionString, ch.variableName))
                            pass
                        pass
                    sam.setNormRegions(normChannels)
                    log.warning("            For now, using all non-validation channels by default: %s" % sam.normRegions)
                    
            if sam.normRegions and (not sam.noRenormSys):
                normString = ""
                for normReg in sam.normRegions:
                    if not type(normReg[0]) == "list":
                        normList = [normReg[0]]
                        c = fitConfig.getChannel(normReg[1],normList)
                    else:
                        c = fitConfig.getChannel(normReg[1],normReg[0])
                    normString += c.regionString

                tmpName = "h%sNom_%sNorm" % (sam.name, normString )
                if not tmpName in self.hists.keys():
                    if self.readFromTree:
                        self.hists[tmpName] = TH1F(tmpName, tmpName, 1, 0.5, 1.5)
                        for normReg in sam.normRegions:
                            if not type(normReg[0]) == "list":
                                normList = [normReg[0]]
                                c = fitConfig.getChannel(normReg[1], normList)
                            else:
                                c = fitConfig.getChannel(normReg[1], normReg[0])
                            for r in c.regions:
                                try:
                                    s = c.getSample(sam.name)
                                except:    
                                    # assume that if no histogram is made, then it is not needed  
                                    continue

                                treeName = s.treeName
                                if treeName=='': treeName = s.name+self.nomName
                                self.prepare.read(treeName, s.files)

                                tempHist = TH1F("temp", "temp", 1, 0.5, 1.5)

                                self.chains[self.prepare.currentChainName].Project("temp",self.cutsDict[r], \
                                                                                   str(self.lumiUnits*self.outputLumi/self.inputLumi)+" * "+"*".join(s.weights)+" * ("+self.cutsDict[r]+")")

                                # if the overflow bin is used for this channel, make sure the normalization takes it into account
                                nomName = "h%sNom_%sNorm" % (s.name, normString)
                                if c.useOverflowBin:
                                    self.hists[nomName].SetBinContent(1, self.hists[nomName].GetBinContent(1) + tempHist.Integral())
                                else:
                                    self.hists[nomName].SetBinContent(1, self.hists[nomName].GetBinContent(1) + tempHist.GetSumOfWeights())
                                del tempHist

                                log.verbose("nom =%f" % self.hists[nomName].GetSumOfWeights())
                    else:
                        nomName = "h%sNom_%sNorm" % (sam.name, normString)
                        self.hists[nomName] = None
                        try:
                            self.prepare.addHisto(nomName)
                        except:    
                            # assume that if no histogram is made, then it is not needed  
                            pass

            for (systName,syst) in chan.getSample(sam.name).systDict.items():
                log.info("    Systematic: %s" % systName)

                #first reset weight to nominal value
                self.setWeightsCutsVariable(chan, sam, regionString)
                syst.PrepareWeightsAndHistos(regionString, normString, normCuts, self, fitConfig, chan, sam)

                self.addHistoSysforNoQCD(regionString, normString, normCuts, fitConfig, chan, sam, syst)
        elif sam.isQCD:
            #Add Histos for Sample-type QCD
            self.addHistoSysForQCD(regionString,normString,normCuts,chan,sam)
        return

    
    def buildBlindedHistos(self, fitConfig, chan, sam):
        if (self.blindSR and (chan.channelName in fitConfig.signalChannels)) or \
           (self.blindCR and chan.channelName in fitConfig.bkgConstrainChannels) or \
           (self.blindVR and (chan.channelName in fitConfig.validationChannels)):
            if not self.hists[sam.blindedHistName]:
                self.hists[sam.blindedHistName] = TH1F(sam.blindedHistName,sam.blindedHistName,chan.nBins,chan.binLow,chan.binHigh)

                for s in chan.sampleList:
                    if (not s.isData) and (self.useSignalInBlindedData or s.name!=fitConfig.signalSample):
                        self.hists[sam.blindedHistName].Add(self.hists[s.histoName])
        return
    
    def makeDicts(self, fitConfig, chan):
        regString = "".join(chan.regions)

        canDict = {}
        stackDict = {}
        legDict = {}
        dataNameDict = {}
        qcdNameDict = {}

        for (samName,infoList) in chan.infoDict.items():
            for info in infoList:
                if info[3] == "userOverallSys":
                    continue

                if not info[0] == "Nom":
                    continue

                myKey = (info[0], regString, replaceSymbols(chan.variableName))
                if not myKey in canDict.keys():
                    canDict[myKey] = TCanvas("c"+fitConfig.name+"_"+info[0]+"_"+regString+"_obs_"+replaceSymbols(chan.variableName), "c"+info[0]+"_"+regString+"_obs_"+replaceSymbols(chan.variableName),800,600,800,600)

                    stackDict[myKey] = THStack(fitConfig.name+"_"+regString+"_obs_"+replaceSymbols(chan.variableName)+"Stack"+info[0],"")

                    legDict[myKey] = TLegend(0.7,0.7,0.88,0.88)
                    legDict[myKey].SetBorderSize(0)
                    legDict[myKey].SetTextFont(42)
                    legDict[myKey].SetTextSize(0.05)
                    legDict[myKey].SetFillColor(0)
                    legDict[myKey].SetLineColor(0)

                    legDict[myKey].Clear()

                if not (regString,replaceSymbols(chan.variableName)) in dataNameDict.keys():
                    dataNameDict[(regString,replaceSymbols(chan.variableName))] = ""

                if not (regString,replaceSymbols(chan.variableName)) in qcdNameDict.keys():
                    qcdNameDict[(regString,replaceSymbols(chan.variableName))] = ""

                if not fitConfig.getSample(samName).isData and not fitConfig.getSample(samName).isQCD:
                    histName = "h"+samName+info[0]+"_"+regString+"_obs_"+replaceSymbols(chan.variableName)
                    self.hists[histName].SetLineColor(fitConfig.getSample(samName).color)
                    self.hists[histName].SetFillColor(fitConfig.getSample(samName).color)

                    stackDict[myKey].Add(self.hists[histName],"hist")
                    legDict[myKey].AddEntry(self.hists[histName], samName+info[0], "lf")
                elif fitConfig.getSample(samName).isQCD:
                    nomName = "h%sNom_%s_obs_%s" % (samName, regString, replaceSymbols(chan.variableName))
                    self.hists[nomName].SetLineColor(fitConfig.getSample(samName).color)
                    self.hists[nomName].SetFillColor(fitConfig.getSample(samName).color)

                    lowName = "h%sLow_%s_obs_%s" % (samName, regString, replaceSymbols(chan.variableName))
                    self.hists[lowName].SetLineColor(fitConfig.getSample(samName).color)
                    self.hists[lowName].SetFillColor(fitConfig.getSample(samName).color)

                    highName = "h%sHigh_%s_obs_%s" % (samName, regString, replaceSymbols(chan.variableName))
                    self.hists[highName].SetLineColor(fitConfig.getSample(samName).color)
                    self.hists[highName].SetFillColor(fitConfig.getSample(samName).color)

                    qcdNameDict[(regString,replaceSymbols(chan.variableName))] = nomName
                else:
                    histName = "h%s_%s_obs_%s" % (samName, regString, replaceSymbols(chan.variableName))
                    self.hists[histName].SetLineColor(fitConfig.getSample(samName).color)
                    dataNameDict[(regString,replaceSymbols(chan.variableName))] = histName

        for info in stackDict.keys():
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

            plotsDir = "plots/%s/%s" % (self.analysisName, fitConfig.name)
            mkdir_p(plotsDir)

            outputPNG = "%s/stack%s_obs_%s_%s.png" % (plotsDir, info[1], info[2], info[0])
            canDict[info].SaveAs(outputPNG)

            self.canvasList.append(canDict[info])
            self.stackList.append(stackDict[info])
    
    def outputRoot(self):
        outputRootFile = None
        if self.readFromTree:
            outputRootFile = TFile(self.histCacheFile,"RECREATE")
        elif self.prepare.recreate:
            outputRootFile = self.prepare.cacheFile
            if not outputRootFile.IsOpen():
                outputRootFile = outputRootFile.Open(self.histCacheFile,"UPDATE")

        if outputRootFile:
            outputRootFile.cd()
            histosToWrite = self.hists.values()
            def notNull(x): return not type(x).__name__ == "TObject"
            histosToWrite = filter(notNull,histosToWrite)
            histosToWrite.sort()
            for histo in histosToWrite:
                if histo:
                    histo.Write()
            outputRootFile.Close()

if vars().has_key("configMgr"):
    raise RuntimeError("ConfigManager already exists, no multiple imports allowed!!!")

# Instantiate the singleton

configMgr = ConfigManager()
