from ROOT import THStack,TLegend,TCanvas,TFile,std,TH1F
from ROOT import ConfigMgr,FitConfig,ChannelStyle #this module comes from gSystem.Load("libSusyFitter.so")
from prepareHistos import TreePrepare,HistoPrepare
from copy import deepcopy
from systematic import Systematic
from histogramsManager import histMgr
from logger import Logger
import os
from ROOT import gROOT

gROOT.SetBatch(True)
log = Logger('ConfigManager')

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

        self.inputLumi = None # Luminosity of input histograms
        self.outputLumi = None # Output luminosity
        self.lumiUnits = 1.0 # 1=fb-1, 1000=pb-1, etc.
        self.nTOYs=-1 #<=0 means to use real data
        self.calculatorType=0 # frequentist calculator
        self.testStatType=3   # one-sided test statistic
        self.useCLs=True # use CLs for upper limits, or not
        self.doExclusion=True # true = exclusion, false = discovery test
        self.fixSigXSec=False # true = fix SigXSec by nominal, +/-1sigma
        self.nPoints=20 # number of points in upper limit evaluation
        self.seed=0 # seed for random generator. default is clock
        self.muValGen = 0.0 # mu_sig used for toy generation
        self.toySeedSet = False # Set the seed for toys
        self.toySeed = 0 # CPU clock, default
        self.useAsimovSet = False # Use the Asimov dataset
        self.blindSR = False # Blind the SRs only
        self.blindCR = False # Blind the CRs only
        self.useSignalInBlindedData=False 

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
        if unit=="fb-1" or unit=="fb":
            self.lumiUnits = 1.0
        elif unit=="pb-1" or unit=="pb":
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
                raise RuntimeError("fitConfig %s already exists in configManager. Please use a different name."%(newName))
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
        log.info("Created Fit Config: %s" % (newName))
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
        log.warning("fitConfig named '%s' does not exist. Cannot be removed." % (name))
        return

    def getTopLevelXML(self, name):
        log.warning("getTopLevelXML() has been deprecated and is now getFitConfig()")
        return self.getFitConfig(name)

    def getFitConfig(self, name):
        for tl in self.fitConfigs:
            if tl.name == name:
                return tl
        log.warning("fitConfig named '%s' does not exist. Cannot be returned." % (name))
        return 0

    def initialize(self):
        log.info("Initializing...")
        if self.histCacheFile=='':
            tmpName="data/"+self.analysisName+".root"
            log.info("Giving default name histCacheFile: %s"%(tmpName))
            self.histCacheFile=tmpName
            pass
        if self.inputLumi==None and self.outputLumi==None:
            self.inputLumi=1.0
            self.outputLumi=1.0
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
                    elif sam.isQCD or sam.isData:
                        chan.getSample(sam.name).setWrite(False)

        log.info("  -initialize global histogram dictionary...")
        for tl in self.fitConfigs:
            for chan in tl.channels:
                for sam in chan.sampleList:
                    regString = ""
                    for reg in chan.regions:
                        #self.hists["h"+sam.name+"Nom_"+reg+"_obs_"+chan.variableName] = None
                        #self.hists["h"+sam.name+"High_"+reg+"_obs_"+chan.variableName] = None
                        #self.hists["h"+sam.name+"Low_"+reg+"_obs_"+chan.variableName] = None
                        regString += reg
                    if sam.isData:
                        if (self.blindSR and (chan.channelName in tl.signalChannels)) or (self.blindCR and (chan.channelName in tl.bkgConstrainChannels)):
                            sam.blindedHistName="h"+tl.name+sam.name+"Blind_"+regString+"_obs_"+replaceSymbols(chan.variableName)
                            if not sam.blindedHistName in self.hists.keys():
                                self.hists[sam.blindedHistName] = None
                        else:
                            if not "h"+sam.name+"_"+regString+"_obs_"+replaceSymbols(chan.variableName) in self.hists.keys():
                                self.hists["h"+sam.name+"_"+regString+"_obs_"+replaceSymbols(chan.variableName)] = None                            
                    elif sam.isQCD:
                        if not "h"+sam.name+"Nom_"+regString+"_obs_"+replaceSymbols(chan.variableName) in self.hists.keys():
                            self.hists["h"+sam.name+"Nom_"+regString+"_obs_"+replaceSymbols(chan.variableName)] = None
                        if not "h"+sam.name+"High_"+regString+"_obs_"+replaceSymbols(chan.variableName) in self.hists.keys():
                            self.hists["h"+sam.name+"High_"+regString+"_obs_"+replaceSymbols(chan.variableName)] = None
                        if not "h"+sam.name+"Low_"+regString+"_obs_"+replaceSymbols(chan.variableName) in self.hists.keys():
                            self.hists["h"+sam.name+"Low_"+regString+"_obs_"+replaceSymbols(chan.variableName)] = None
                        if not "h"+sam.name+"Syst_"+regString+"_obs_"+replaceSymbols(chan.variableName) in self.hists.keys():
                            self.hists["h"+sam.name+"Syst_"+regString+"_obs_"+replaceSymbols(chan.variableName)] = None
                        if not "h"+sam.name+"Stat_"+regString+"_obs_"+replaceSymbols(chan.variableName) in self.hists.keys():
                            self.hists["h"+sam.name+"Stat_"+regString+"_obs_"+replaceSymbols(chan.variableName)] = None
                        if chan.variableName == "cuts":
                            nHists = len(chan.regions)
                        else:
                            nHists = chan.nBins
                        for iBin in xrange(1,nHists+1):
                            if not "h"+sam.name+"Nom_"+regString+"_obs_"+replaceSymbols(chan.variableName)+"_"+str(iBin) in self.hists.keys():
                                self.hists["h"+sam.name+"Nom_"+regString+"_obs_"+replaceSymbols(chan.variableName)+"_"+str(iBin)] = None
                            if not "h"+sam.name+"High_"+regString+"_obs_"+replaceSymbols(chan.variableName)+"_"+str(iBin) in self.hists.keys():
                                self.hists["h"+sam.name+"High_"+regString+"_obs_"+replaceSymbols(chan.variableName)+"_"+str(iBin)] = None
                            if not "h"+sam.name+"Low_"+regString+"_obs_"+replaceSymbols(chan.variableName)+"_"+str(iBin) in self.hists.keys():
                                self.hists["h"+sam.name+"Low_"+regString+"_obs_"+replaceSymbols(chan.variableName)+"_"+str(iBin)] = None
                    elif not sam.isDiscovery:
                        if not "h"+sam.name+"Nom_"+regString+"_obs_"+replaceSymbols(chan.variableName) in self.hists.keys():
                            self.hists["h"+sam.name+"Nom_"+regString+"_obs_"+replaceSymbols(chan.variableName)] = None
                        for (name,syst) in chan.getSample(sam.name).systDict.items():
                            if not "h"+sam.name+syst.name+"High_"+regString+"_obs_"+replaceSymbols(chan.variableName) in self.hists.keys():
                                self.hists["h"+sam.name+syst.name+"High_"+regString+"_obs_"+replaceSymbols(chan.variableName)] = None
                            if not "h"+sam.name+syst.name+"Low_"+regString+"_obs_"+replaceSymbols(chan.variableName) in self.hists.keys():
                                self.hists["h"+sam.name+syst.name+"Low_"+regString+"_obs_"+replaceSymbols(chan.variableName)] = None
                            if syst.merged:
                                mergedName = ""
                                for s in syst.sampleList:
                                    mergedName += s
                                if not "h"+mergedName+"Nom_"+regString+"_obs_"+replaceSymbols(chan.variableName) in self.hists.keys():
                                    self.hists["h"+mergedName+"Nom_"+regString+"_obs_"+replaceSymbols(chan.variableName)] = None
                                if not "h"+mergedName+syst.name+"High_"+regString+"_obs_"+replaceSymbols(chan.variableName) in self.hists.keys():
                                    self.hists["h"+mergedName+syst.name+"High_"+regString+"_obs_"+replaceSymbols(chan.variableName)] = None
                                if not "h"+mergedName+syst.name+"Low_"+regString+"_obs_"+replaceSymbols(chan.variableName) in self.hists.keys():
                                    self.hists["h"+mergedName+syst.name+"Low_"+regString+"_obs_"+replaceSymbols(chan.variableName)] = None

        if self.readFromTree:
            log.info("  -build TreePrepare()...")
            self.prepare = TreePrepare()
            if self.plotHistos==None:    #set plotHistos if not already set by user
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
        self.cppMgr.setNPoints( self.nPoints )
        self.cppMgr.setSeed( self.seed )
        self.cppMgr.setMuValGen( self.muValGen )
        self.cppMgr.setUseAsimovSet( self.useAsimovSet)

        if self.outputFileName:
            self.cppMgr.m_outputFileName = self.outputFileName
            self.cppMgr.m_saveTree=True
        #Fill FitConfigs from TopLevelXMLs
        for tl in self.fitConfigs:
            cppTl = self.cppMgr.addFitConfig(tl.name)
            cppTl.m_inputWorkspaceFileName = tl.wsFileName
            cppTl.m_Lumi = self.lumiUnits*self.outputLumi
            if not tl.signalSample == None:
                cppTl.m_signalSampleName = tl.signalSample
     
            #CR/SR/VR channels
            for cName in tl.signalChannels:
                cppTl.m_signalChannels.push_back(cName)
            for cName in tl.validationChannels:
                cppTl.m_validationChannels.push_back(cName)
            for cName in tl.bkgConstrainChannels:
                cppTl.m_bkgConstrainChannels.push_back(cName)
       
            # Plot cosmetics per channel
            for c in tl.channels:
                 style = ChannelStyle(c.channelName)
                 style.setNBins(c.nBins)
                 if not c.minY == None:
                    style.setMinY(c.minY)
                 if not c.maxY == None:
                   style.setMaxY(c.maxY)
                 if not c.titleX == None:
                     style.setTitleX(c.titleX)
                 if not c.titleY == None:
                     style.setTitleY(c.titleY)
                 if not c.logY == None:
                     style.setLogY(c.logY)
                 if not c.ATLASLabelX == None:
                     style.setATLASLabelX(c.ATLASLabelX)
                 if not c.ATLASLabelY == None:
                     style.setATLASLabelY(c.ATLASLabelY)
                 if not c.ATLASLabelX == None:
                     style.setATLASLabelText(c.ATLASLabelText)
                 if not c.showLumi == None:
                     style.setShowLumi(c.showLumi)     

                 # Plot cosmetics per fitConfig 
                 style.setDataColor(tl.dataColor)
                 style.setTotalPdfColor(tl.totalPdfColor)
                 style.setErrorLineColor(tl.errorLineColor)
                 style.setErrorLineStyle(tl.errorLineStyle)
                 style.setErrorFillColor(tl.errorFillColor)
                 style.setErrorFillStyle(tl.errorFillStyle)
                 style.setRemoveEmptyBins = self.removeEmptyBins
                 if not tl.tLegend == None:
                     style.setTLegend(tl.tLegend)

                 # Sample name and color
                 for s in c.sampleList:
                     style.m_sampleNames.push_back(s.name)
                     style.m_sampleColors.push_back(s.color)

                 # add channel and style for channel to C++ FitConfig (these two are expected to be synchronous
                 cppTl.m_channels.push_back(c.channelName)
                 cppTl.m_channelsStyle.push_back(style)
                 
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
        log.info("Systematics: %s" % self.systDict.keys())
        log.debug("Cuts Dictionary: %s" % self.cutsDict)
        log.info("readFromTree: %s" % self.readFromTree)
        log.info("plotHistos: %s" % self.plotHistos)
        log.info("executeHistFactory: %s" % self.executeHistFactory)
        log.info("fitConfig objects:")
        for tl in self.fitConfigs:
            log.info("  %s"%tl.name)
            for c in tl.channels:
                log.info("    %s: %s"%(c.name,c.systDict.keys()))
        log.info("C++ ConfigMgr status: %s"%(self.cppMgr.m_status))
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
                log.debug("             Channel: " + channel.name)
                log.debug("             " + str(channel.files))
                for sample in channel.sampleList:
                    log.debug("             ---> Sample: " + sample.name)
                    log.debug("                          " + str(sample.files))
                    for (systName,syst) in sample.systDict.items():
                        log.debug("                            ---> Systematic: " + syst.name)
                        log.debug("                                       Low : " + str(syst.filesLo))
                        log.debug("                                       High: " + str(syst.filesHi))
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
                log.debug("    ---> Channel: " + channel.name)
                log.debug("                  " + str(channel.treeName))
                for sample in channel.sampleList:
                    log.debug("           ---> Sample: " + sample.name)
                    log.debug("                        "+str(sample.treeName))
                    for (systName,syst) in sample.systDict.items():
                        log.debug("                   ---> Systematic: " + syst.name)
                        log.debug("                        Low : " + str(syst.treeLoName))
                        log.debug("                        High: " + str(syst.treeHiName))
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
        userNormDict = {}
        for (iChan,chan) in enumerate(fitConfig.channels):
            for reg in chan.regions:
                if not chan.channelName in fitConfig.validationChannels:
                    normString = "".join(chan.regions)
                    normCutsList = [ "(%s) || " % (self.cutsDict[reg]) for reg in chan.regions ]
                    normCuts = "".join(normCutsList)
                    
                    for reg in chan.regions:
                        normRegions.append(reg)
                        #normString += reg
                        #normCuts += "("+self.cutsDict[reg] + ") || "
        
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

        #post-processing loop for norm systematics
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

        # Build blinded histograms here
        for (iChan, chan) in enumerate(fitConfig.channels):
            for sam in chan.sampleList:
                if sam.isData:
                    self.buildBlindedHistos(fitConfig, chan, sam)
                else:
                    pass
        
        if self.plotHistos:
            if not os.path.isdir("plots/"+self.analysisName):
                os.makedirs("plots/"+self.analysisName)
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
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, True, False)
        elif syst.method == "overallNormHistoSys":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, True, True, False, False, sam.name, normString)
        elif syst.method == "overallNormHistoSysOneSide":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, True, True, False, True, sam.name, normString)
        elif syst.method == "overallNormHistoSysOneSideSym":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, True, True, True, True, sam.name, normString)
        elif syst.method == "normHistoSys":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, False, True, False, False, sam.name, normString)
        elif syst.method == "normHistoSysOneSide":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, False, True, False, True, sam.name, normString)
        elif syst.method == "normHistoSysOneSideSym":
            chan.getSample(sam.name).addHistoSys(syst.name, nomName, highName, lowName, False, True, True, True, sam.name, normString)
        elif syst.method == "userHistoSys" or syst.method == "userNormHistoSys":
            if configMgr.hists[highName] == None:
                configMgr.hists[highName] = histMgr.buildUserHistoSysFromHist(highName,  syst.high,  configMgr.hists[nomName])
            if configMgr.hists[lowName] == None:
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
                    if self.hists[nomMergedName] == None:
                        self.hists[nomMergedName] = self.hists[nomName].Clone(nomMergedName)
                    else:
                        self.hists[nomMergedName].Add(self.hists[nomName])
                    if self.hists[highMergedName] == None:
                        self.hists[highMergedName] = self.hists[highName].Clone(highMergedName)
                    else:
                        self.hists[highMergedName].Add(self.hists[highName])
                    if self.hists[lowMergedName] == None:
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
            chan.getSample(sam.name).shapeSystList.append(('shape_' + syst.name + '_' + sam.name + "_" + regionString + "_obs_" + replaceSymbols(chan.variableName), \
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
        prefixNom= "h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName)
        prefixHigh="h"+sam.name+"High_"+regionString+"_obs_"+replaceSymbols(chan.variableName)
        prefixLow= "h"+sam.name+"Low_"+regionString+"_obs_"+replaceSymbols(chan.variableName)
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
            
            chan.getSample(sam.name).addOverallSys("QCDNorm_"+regionString,overallSystHigh,overallSystLow)
        elif chan.getSample(sam.name).qcdSyst == "overallHistoSys":
            chan.getSample(sam.name).addHistoSys("QCDNorm_"+regionString,prefixNom,prefixHigh,prefixLow,True,False)
        elif chan.getSample(sam.name).qcdSyst == "normHistoSys":
            chan.getSample(sam.name).addHistoSys("QCDNorm_"+regionString,prefixNom,prefixHigh,prefixLow,False,True)
        elif chan.getSample(sam.name).qcdSyst == "shapeSys":
            chan.getSample(sam.name).addShapeSys("QCDNorm_"+regionString,prefixNom,prefixHigh,prefixLow)
            chan.getSample(sam.name).shapeSystList.append(("QCDNorm_"+regionString,prefixNom+"Norm","data/"+configMgr.analysisName+".root","","","",""))
        elif chan.getSample(sam.name).qcdSyst == "uncorr":
            chan.getSample(sam.name).setWrite(False)
            for iBin in xrange(1,nHists+1):
                qcdSam = sam.Clone()
                qcdSam.name = sam.name+"_"+regionString+"_"+str(iBin)
                chan.addSample(qcdSam)
                chan.getSample(qcdSam.name).setWrite(True)
                chan.getSample(qcdSam.name).setHistoName("h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName)+"_"+str(iBin))
                chan.getSample(qcdSam.name).addHistoSys("NormQCD"+regionString+"_"+str(iBin),prefixNom+"_"+str(iBin),prefixHigh+"_"+str(iBin),prefixLow+"_"+str(iBin),False,False)
        else:
            raise Exception("Incorrect systematic method specified for QCD: %s"%getSample(sam.name).qcdSyst)

    def setWeightsCutsVariable(self,chan,sam,regionString):
        if not sam.isData and not sam.isQCD and not sam.isDiscovery:
            self.prepare.weights = str(self.lumiUnits*self.outputLumi/self.inputLumi)
            self.prepare.weights += " * " + " * ".join(sam.weights)
            if self.readFromTree and not sam.isDiscovery:
                    treeName = sam.treeName
                    if treeName=='': treeName = sam.name+self.nomName
                    self.prepare.read(treeName, sam.files)
        else:
            self.prepare.weights = "1."
            if self.readFromTree:
                treeName = sam.treeName
                if treeName=='': treeName = sam.name
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

        if sam.isData:
            if chan.channelName in fitConfig.signalChannels:
                if self.blindSR:
                    chan.addData(sam.blindedHistName)
                else:
                    self.prepare.addHisto("h"+sam.name+"_"+regionString+"_obs_"+replaceSymbols(chan.variableName),useOverflow=chan.useOverflowBin,useUnderflow=chan.useUnderflowBin)
                    chan.addData("h"+sam.name+"_"+regionString+"_obs_"+replaceSymbols(chan.variableName))
            elif chan.channelName in fitConfig.bkgConstrainChannels:
                if self.blindCR:
                    chan.addData(sam.blindedHistName)
                else:
                    self.prepare.addHisto("h"+sam.name+"_"+regionString+"_obs_"+replaceSymbols(chan.variableName),useOverflow=chan.useOverflowBin,useUnderflow=chan.useUnderflowBin)
                    chan.addData("h"+sam.name+"_"+regionString+"_obs_"+replaceSymbols(chan.variableName))
            else:
                self.prepare.addHisto("h"+sam.name+"_"+regionString+"_obs_"+replaceSymbols(chan.variableName),useOverflow=chan.useOverflowBin,useUnderflow=chan.useUnderflowBin)
                chan.addData("h"+sam.name+"_"+regionString+"_obs_"+replaceSymbols(chan.variableName))


        elif not sam.isQCD and not sam.isDiscovery:
            if not len(sam.shapeFactorList):
                tmpName="h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName)
                self.prepare.addHisto(tmpName,useOverflow=chan.useOverflowBin,useUnderflow=chan.useUnderflowBin)
                ###check that nominal sample is not empty for that channel
                if self.hists[tmpName].GetSum() == 0.0:
                    log.warning("    ***nominal sample %s is empty for channel %s. Remove from PDF.***"%(sam.name,chan.name))
                    chan.removeSample(sam.name)
                #    del self.hists[tmpName]
                #    self.hists[tmpName]=None    ## MB : do not delete, else cannot rerun later with -w
                    return
            else:
                self.hists["h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName)] = TH1F("h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName), \
                                                                                                              "h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName), \
                                                                                                              chan.nBins,chan.binLow,chan.binHigh)
                for iBin in xrange(self.hists["h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName)].GetNbinsX()+1):
                    self.hists["h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName)].SetBinContent(iBin+1,1.)
            chan.getSample(sam.name).setHistoName("h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName))


            if not sam.normRegions and (not sam.noRenormSys): 
                needsNorm=False
                for sys in sam.systDict.values():
                    if sys.method == "userNormHistoSys" or sys.method == "normHistoSys" \
                           or sys.method == "normHistoSysOneSide" \
                           or sys.method == "normHistoSysOneSideSym" \
                           or sys.method == "overallNormHistoSys" \
                           or sys.method == "overallNormHistoSysOneSide" \
                           or sys.method == "overallNormHistoSysOneSideSym":
                        log.error("    %s needs normRegions because of %s of type %s but no normalization regions specified. This is not safe, please fix." % (sam.name,sys.name,sys.method))
                        needsNorm=True
                        break
                if needsNorm:
                    normChannels=[]
                    tl=sam.parentChannel.parentTopLvl
                    for ch in tl.channels:
                        if (ch.channelName in tl.bkgConstrainChannels) or (ch.channelName in tl.signalChannels):
                            normChannels.append((ch.regionString,ch.variableName))
                            pass
                        pass
                    sam.setNormRegions(normChannels)
                    log.warning("            For now, using all non-validation channels by default: %s"%sam.normRegions)
                    
            if sam.normRegions and (not sam.noRenormSys):
                normString = ""
                for normReg in sam.normRegions:
                    if not type(normReg[0]) == "list":
                        normList = []
                        normList.append(normReg[0])
                        c = fitConfig.getChannel(normReg[1],normList)
                    else:
                        c = fitConfig.getChannel(normReg[1],normReg[0])
                    normString += c.regionString
                if not "h"+sam.name+"Nom_"+normString+"Norm" in self.hists.keys():
                    if self.readFromTree:
                        self.hists["h"+sam.name+"Nom_"+normString+"Norm"] = TH1F("h"+sam.name+"Nom_"+normString+"Norm","h"+sam.name+"Nom_"+normString+"Norm",1,0.5,1.5)
                        for normReg in sam.normRegions:
                            if not type(normReg[0]) == "list":
                                normList = []
                                normList.append(normReg[0])
                                c = fitConfig.getChannel(normReg[1],normList)
                            else:
                                c = fitConfig.getChannel(normReg[1],normReg[0])
                            for r in c.regions:
                                try:
                                    s = c.getSample(sam.name)
                                except:    
                                    # assume that if no histogram is made, then it is not needed  
                                    continue

                                treeName = s.treeName
                                if treeName=='': treeName = s.name+self.nomName
                                self.prepare.read(treeName, s.files)

                                tempHist = TH1F("temp","temp",1,0.5,1.5)

                                self.chains[self.prepare.currentChainName].Project("temp",self.cutsDict[r], \
                                                                                   str(self.lumiUnits*self.outputLumi/self.inputLumi)+" * "+"*".join(s.weights)+" * ("+self.cutsDict[r]+")")

                                # if the overflow bin is used for this channel, make sure the normalization takes it into account
                                if c.useOverflowBin:
                                    self.hists["h"+s.name+"Nom_"+normString+"Norm"].SetBinContent(1, self.hists["h"+s.name+"Nom_"+normString+"Norm"].GetBinContent(1) + tempHist.Integral())
                                else:
                                    self.hists["h"+s.name+"Nom_"+normString+"Norm"].SetBinContent(1, self.hists["h"+s.name+"Nom_"+normString+"Norm"].GetBinContent(1) + tempHist.GetSumOfWeights())
                                del tempHist

                                log.verbose("nom =%f"%self.hists["h"+s.name+"Nom_"+normString+"Norm"].GetSumOfWeights()) 
                    else:
                        self.hists["h"+sam.name+"Nom_"+normString+"Norm"] = None
                        try:
                            self.prepare.addHisto("h"+sam.name+"Nom_"+normString+"Norm")
                        except:    
                            # assume that if no histogram is made, then it is not needed  
                            pass

            for (systName,syst) in chan.getSample(sam.name).systDict.items():
                log.info("    Systematic: %s"%(systName))
                #first reset weight to nominal value
                self.setWeightsCutsVariable(chan,sam,regionString)
                syst.PrepareWeightsAndHistos(regionString,normString,normCuts,self,fitConfig,chan,sam)
                self.addHistoSysforNoQCD(regionString,normString,normCuts,fitConfig,chan,sam,syst)
        elif sam.isQCD:
            #Add Histos for Sample-type QCD
            self.addHistoSysForQCD(regionString,normString,normCuts,chan,sam)
        return

    
    def buildBlindedHistos(self, fitConfig, chan, sam):
        regString = "".join(chan.regions)
        if (self.blindSR and (chan.channelName in fitConfig.signalChannels)) or (self.blindCR and chan.channelName in fitConfig.bkgConstrainChannels):
            if not self.hists[sam.blindedHistName]:
                self.hists[sam.blindedHistName] = TH1F(sam.blindedHistName,sam.blindedHistName,chan.nBins,chan.binLow,chan.binHigh)
                for s in chan.sampleList:
                    if (not s.isData) and (self.useSignalInBlindedData or s.name!=fitConfig.signalSample):
                        self.hists[sam.blindedHistName].Add(self.hists[s.histoName])
        return
    
    def makeDicts(self,fitConfig, chan):
        regString = ""
        for reg in chan.regions:
            regString += reg

        canDict = {}
        stackDict = {}
        mcDict = {}
        legDict = {}
        dataNameDict = {}
        qcdNameDict = {}
        for (samName,infoList) in chan.infoDict.items():
            for info in infoList:
                if info[3] == "userOverallSys": continue
                if not info[0] == "Nom": continue
                if not (info[0],regString,replaceSymbols(chan.variableName)) in canDict.keys():
                    canDict[(info[0],regString,replaceSymbols(chan.variableName))] = TCanvas("c"+fitConfig.name+"_"+info[0]+"_"+regString+"_obs_"+replaceSymbols(chan.variableName), \
                                                                                             "c"+info[0]+"_"+regString+"_obs_"+replaceSymbols(chan.variableName),800,600,800,600)

                    stackDict[(info[0],regString,replaceSymbols(chan.variableName))] = THStack(fitConfig.name+"_"+regString+"_obs_"+replaceSymbols(chan.variableName)+"Stack"+info[0],"")

                    legDict[(info[0],regString,replaceSymbols(chan.variableName))] = TLegend(0.7,0.7,0.88,0.88)
                    legDict[(info[0],regString,replaceSymbols(chan.variableName))].SetBorderSize(0)
                    legDict[(info[0],regString,replaceSymbols(chan.variableName))].SetTextFont(42)
                    legDict[(info[0],regString,replaceSymbols(chan.variableName))].SetTextSize(0.05)
                    legDict[(info[0],regString,replaceSymbols(chan.variableName))].SetFillColor(0)
                    legDict[(info[0],regString,replaceSymbols(chan.variableName))].SetLineColor(0)

                    legDict[(info[0],regString,replaceSymbols(chan.variableName))].Clear()

                if not (regString,replaceSymbols(chan.variableName)) in dataNameDict.keys():
                    dataNameDict[(regString,replaceSymbols(chan.variableName))] = ""
                if not (regString,replaceSymbols(chan.variableName)) in qcdNameDict.keys():
                    qcdNameDict[(regString,replaceSymbols(chan.variableName))] = ""

                if not fitConfig.getSample(samName).isData and not fitConfig.getSample(samName).isQCD:
                    self.hists["h"+samName+info[0]+"_"+regString+"_obs_"+replaceSymbols(chan.variableName)].SetLineColor(fitConfig.getSample(samName).color)
                    self.hists["h"+samName+info[0]+"_"+regString+"_obs_"+replaceSymbols(chan.variableName)].SetFillColor(fitConfig.getSample(samName).color)
                    stackDict[(info[0],regString,replaceSymbols(chan.variableName))].Add(self.hists["h"+samName+info[0]+"_"+regString+"_obs_"+replaceSymbols(chan.variableName)],"hist")
                    legDict[(info[0],regString,replaceSymbols(chan.variableName))].AddEntry(self.hists["h"+samName+info[0]+"_"+regString+"_obs_"+replaceSymbols(chan.variableName)], \
                                                                                            samName+info[0],"lf")
                elif fitConfig.getSample(samName).isQCD:
                    self.hists["h"+samName+"Nom_"+regString+"_obs_"+replaceSymbols(chan.variableName)].SetLineColor(fitConfig.getSample(samName).color)
                    self.hists["h"+samName+"Nom_"+regString+"_obs_"+replaceSymbols(chan.variableName)].SetFillColor(fitConfig.getSample(samName).color)
                    self.hists["h"+samName+"Low_"+regString+"_obs_"+replaceSymbols(chan.variableName)].SetLineColor(fitConfig.getSample(samName).color)
                    self.hists["h"+samName+"Low_"+regString+"_obs_"+replaceSymbols(chan.variableName)].SetFillColor(fitConfig.getSample(samName).color)
                    self.hists["h"+samName+"High_"+regString+"_obs_"+replaceSymbols(chan.variableName)].SetLineColor(fitConfig.getSample(samName).color)
                    self.hists["h"+samName+"High_"+regString+"_obs_"+replaceSymbols(chan.variableName)].SetFillColor(fitConfig.getSample(samName).color)
                    qcdNameDict[(regString,replaceSymbols(chan.variableName))] = "h"+samName+"Nom_"+regString+"_obs_"+replaceSymbols(chan.variableName)
                else:
                    self.hists["h"+samName+"_"+regString+"_obs_"+replaceSymbols(chan.variableName)].SetLineColor(fitConfig.getSample(samName).color)
                    dataNameDict[(regString,replaceSymbols(chan.variableName))] = "h"+samName+"_"+regString+"_obs_"+replaceSymbols(chan.variableName)

        for info in stackDict.keys():
            canDict[info].cd()

            if not qcdNameDict[(info[1],info[2])] == "":
                stackDict[info].Add(self.hists[qcdNameDict[(info[1],info[2])]],"hist")
                legDict[info].AddEntry(self.hists[qcdNameDict[(info[1],info[2])]],"QCDNom","lf")

            if not dataNameDict[(info[1],info[2])] == "":
                legDict[info].AddEntry(self.hists[dataNameDict[(info[1],info[2])]],"Data","lf")
                self.hists[dataNameDict[(info[1],info[2])]].SetStats(False)
                self.hists[dataNameDict[(info[1],info[2])]].GetYaxis().SetTitleOffset(1.3)
                self.hists[dataNameDict[(info[1],info[2])]].Draw()
                self.hists[dataNameDict[(info[1],info[2])]].GetXaxis().SetTitle(chan.variableName)
                self.hists[dataNameDict[(info[1],info[2])]].GetYaxis().SetTitle("entries")
                stackDict[info].Draw("same")
                self.hists[dataNameDict[(info[1],info[2])]].Draw("same")

                if self.hists[dataNameDict[(info[1],info[2])]].GetBinContent(self.hists[dataNameDict[(info[1],info[2])]].GetMaximumBin()) > stackDict[info].GetMaximum():
                    rangeMax = self.hists[dataNameDict[(info[1],info[2])]].GetBinContent(self.hists[dataNameDict[(info[1],info[2])]].GetMaximumBin())
                else:
                    rangeMax = stackDict[info].GetMaximum()

                if self.hists[dataNameDict[(info[1],info[2])]].GetBinContent(self.hists[dataNameDict[(info[1],info[2])]].GetMinimumBin()) < stackDict[info].GetMinimum():
                    rangeMin = self.hists[dataNameDict[(info[1],info[2])]].GetBinContent(self.hists[dataNameDict[(info[1],info[2])]].GetMinimumBin())
                else:
                    rangeMin = stackDict[info].GetMinimum()

                self.hists[dataNameDict[(info[1],info[2])]].GetYaxis().SetRangeUser(rangeMin-0.1*rangeMin,rangeMax+0.1*rangeMax)
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

            if not os.path.isdir("plots/"+self.analysisName+"/"+fitConfig.name):
                os.makedirs("plots/"+self.analysisName+"/"+fitConfig.name)
            canDict[info].SaveAs("plots/"+self.analysisName+"/"+fitConfig.name+"/stack"+info[1]+"_obs_"+info[2]+"_"+info[0]+".png")

            self.canvasList.append(canDict[info])
            self.stackList.append(stackDict[info])
    
    def outputRoot(self):
        outputRootFile=None
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
