from ROOT import THStack,TLegend,TCanvas,TFile,std,TH1F
from ROOT import ConfigMgr,FitConfig #this module comes from gSystem.Load("libSusyFitter.so")
from prepareHistos import TreePrepare,HistoPrepare
from copy import deepcopy
from systematic import Systematic
import os

from ROOT import gROOT

gROOT.SetBatch(True)

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
        self.nomName = None # Name of nominal tree
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
        self.toySeedSet = False
        self.toySeed = 0 # CPU clock, default
        self.useAsimovSet = False

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
        
        self.verbose=1
        self.includeOverallSys = True # Boolean to chose if HistoSys should also have OverallSys
        self.readFromTree = False # Boolean to chose if reading histograms from tree will also write to file
        self.plotHistos = None # Boolean to chose to plot out the histograms
        self.executeHistFactory = True # Boolean to chose to execute HistFactory
        self.printHistoNames = False # Print out the names of generated histograms
        self.doHypoTest = False

        self.topLvls = [] # TopLevelXML object
        self.prepare = None # PrepareHistos object

        self.histCacheFile = ""
        self.fileList = [] # File list to be used for tree production
        self.treeName = ''
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

    def addTopLevelXML(self,input,name=""):
        from configWriter import TopLevelXML
        if len(name)>0:
            newName=name
        elif isinstance(input,str):
            newName=input
        elif isinstance(input,TopLevelXML):
            newName=input.name
        else:
            raise RuntimeError("Logic error in addTopLevelXML")

        #check that newName is not already used
        for tl in self.topLvls:
            if tl.name==newName:
                raise RuntimeError("TopLevelXML %s already exists in configManager. Please use a different name."%(newName))
            pass

        #create new TopLevelXML object and return pointer
        if isinstance(input,TopLevelXML):
            newTLX = input.Clone(newName)
        else:
            newTLX = TopLevelXML(newName)
            pass
        newTLX.verbose=self.verbose
        newTLX.setWeights(self.weights)
        self.topLvls.append(newTLX)
        print "Created Fit Config: %s"%(newName)
        return self.topLvls[len(self.topLvls)-1]

    def addTopLevelXMLClone(self,obj,name): 
        return self.addTopLevelXML(obj,name)

    def removeTopLevelXML(self,name):
        for i in xrange(0,len(self.topLvls)):
            tl=self.topLvls[i]
            if tl.name==name:
                self.topLvls.pop(i)
                return
        print "WARNING TopLevelXML named '%s' does not exist. Cannot be removed."%(name)
        return

    def getTopLevelXML(self,name):
        for tl in self.topLvls:
            if tl.name==name:
                return tl
        print "WARNING TopLevelXML named '%s' does not exist. Cannot be returned."%(name)
        return 0

    def initialize(self):        
        print "Initializing..."
        if self.histCacheFile=='':
            tmpName="data/"+self.analysisName+".root"
            print "Giving default name histCacheFile: %s"%(tmpName)
            self.histCacheFile=tmpName
            pass
        if self.inputLumi==None and self.outputLumi==None:
            self.inputLumi=1.0
            self.outputLumi=1.0
            pass

        # Propagate stuff down from config manager
        print "  -initialize python objects..."
        for tl in self.topLvls:
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

        print "  -initialize global histogram dictionary..."
        for tl in self.topLvls:
            for chan in tl.channels:
                for sam in chan.sampleList:
                    regString = ""
                    for reg in chan.regions:
                        #self.hists["h"+sam.name+"Nom_"+reg+"_obs_"+chan.variableName] = None
                        #self.hists["h"+sam.name+"High_"+reg+"_obs_"+chan.variableName] = None
                        #self.hists["h"+sam.name+"Low_"+reg+"_obs_"+chan.variableName] = None
                        regString += reg
                    if sam.isData:
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
            print "  -build TreePrepare()..."
            self.prepare = TreePrepare()
            if self.plotHistos==None:    #set plotHistos if not already set by user
                self.plotHistos = False  #this is essentially for debugging
                pass
        else:
            print "  -build HistoPrepare()..."
            self.prepare = HistoPrepare(self.histCacheFile)        
        #C++ alter-ego
        print "  -initialize C++ mgr..."
        self.initializeCppMgr()
        print "  -propagate file list and tree names..."
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

        if self.outputFileName:
            self.cppMgr.m_outputFileName = self.outputFileName
            self.cppMgr.m_saveTree=True            
        #Fill FitConfigs from TopLevelXMLs
        for tl in self.topLvls:
            cppTl = self.cppMgr.addFitConfig(tl.name)
            cppTl.m_inputWorkspaceFileName = tl.wsFileName
            cppTl.m_Lumi = self.lumiUnits*self.outputLumi
            if not tl.signalSample == None:
                cppTl.m_signalSampleName = tl.signalSample

            #samples name & color
            for s in tl.sampleList:
                cppTl.m_sampleNames.push_back(s.name)
                cppTl.m_sampleColors.push_back(s.color)

            # Sample name and color for discovery mode
            for c in tl.channels:
                for s in c.sampleList:
                    if s.isDiscovery:
                        cppTl.m_sampleNames.push_back(s.name)
                        cppTl.m_sampleColors.push_back(s.color)

            #CR/SR/VR channels
            for cName in tl.signalChannels:
                cppTl.m_signalChannels.push_back(cName)
            for cName in tl.validationChannels:
                cppTl.m_validationChannels.push_back(cName)
            for cName in tl.bkgConstrainChannels:
                cppTl.m_bkgConstrainChannels.push_back(cName)
           
            # Plot cosmetics per TopLevelXML (FitConfig in C++)
            cppTl.m_dataColor = tl.dataColor
            cppTl.m_totalPdfColor = tl.totalPdfColor
            cppTl.m_errorLineColor = tl.errorLineColor
            cppTl.m_errorLineStyle = tl.errorLineStyle
            cppTl.m_errorFillColor = tl.errorFillColor
            cppTl.m_errorFillStyle = tl.errorFillStyle
            if not tl.tLegend == None:
                cppTl.m_legend = tl.tLegend

            # Plot cosmetics per channel
            for c in tl.channels:
                 cppTl.m_channels.push_back(c.channelName)
                 cppTl.m_channelsNBins.push_back(c.nBins)
                 if not c.minY == None:
                     cppTl.m_channelsMinY.push_back(c.minY)
                 if not c.maxY == None:
                   cppTl.m_channelsMaxY.push_back(c.maxY)
                 if not c.titleX == None:
                     cppTl.m_channelsTitleX.push_back(c.titleX)
                 if not c.titleY == None:
                     cppTl.m_channelsTitleY.push_back(c.titleY)
                 if not c.logY == None:
                     cppTl.m_channelsLogY.push_back(c.logY)
                 if not c.ATLASLabelX == None:
                     cppTl.m_channelsATLASLabelX.push_back(c.ATLASLabelX)
                 if not c.ATLASLabelY == None:
                     cppTl.m_channelsATLASLabelY.push_back(c.ATLASLabelY)
                 if not c.ATLASLabelX == None:
                     cppTl.m_channelsATLASLabelText.push_back(c.ATLASLabelText)
                 if not c.showLumi == None:
                     cppTl.m_channelsShowLumi.push_back(c.showLumi)
                     

        self.cppMgr.checkConsistency()
        self.cppMgr.initialize()
        return

    def Print(self,verbose=None):
        if verbose == None:
            verbose = self.verbose
        print "*-------------------------------------------------*"
        print "              Summary of ConfigMgr\n"
        print "analysisName: %s"%self.analysisName
        print "cache file: %s"%self.histCacheFile
        print "output file: %s"%self.outputFileName
        print "nomName: %s"%self.nomName
        print "inputLumi: %.3f"%self.inputLumi
        print "outputLumi: %.3f"%self.outputLumi
        print "nTOYs: %i"%self.nTOYs
        print "doHypoTest: %s"%self.doHypoTest
        print "fixSigXSec: %s"%self.fixSigXSec
        print "Systematics: %s"%self.systDict.keys()
        if verbose > 1:
            print "Cuts Dictionnary: %s"%self.cutsDict
        print "readFromTree: %s"%self.readFromTree
        print "plotHistos: %s"%self.plotHistos
        print "executeHistFactory: %s"%self.executeHistFactory
        print "TopLevelXML objects:"
        for tl in self.topLvls:
            print "  %s"%tl.name
        print "C++ ConfigMgr status: %s"%(self.cppMgr.m_status)
        print "Histogram names: (requires verbose > 1)"
        if verbose > 1:
            configMgr.printHists()
        print "Chain names: (requires verbose > 1 & note chains are only generated with -t)"
        if verbose > 1:
            configMgr.printChains()
        print "File names: (requires verbose > 1)"
        if verbose > 1:
            configMgr.printFiles()
        print "Input tree names: (requires verbose > 1)"
        if verbose > 1:
            configMgr.printTreeNames()
        print "*-------------------------------------------------*\n"
        return

    def printHists(self):
        histList = self.hists.keys()
        histList.sort()
        for hist in histList:
            print " ",hist
        return

    def printChains(self):
        chainList = self.chains.keys()
        chainList.sort()
        for chain in chainList:
            print " ",chain
        return

    def printFiles(self):
        print "ConfigManager:"
        print str(self.fileList)
        for topLvl in self.topLvls:
            print "                TopLvlXML: " + topLvl.name
            print "                " + str(topLvl.files)
            for channel in topLvl.channels:
                print "                ---------> Channel: " + channel.name
                print "                           " + str(channel.files)
                for sample in channel.sampleList:
                    print "                           ---------> Sample: " + sample.name
                    print "                                      "+str(sample.files)
                    for (systName,syst) in sample.systDict.items():
                        print "                                      ---------> Systematic: " + syst.name
                        print "                                                 Low : " + str(syst.filesLo)
                        print "                                                 High: " + str(syst.filesHi)
        return

    def printTreeNames(self):
        print "ConfigManager:"
        print str(self.treeName)
        for topLvl in self.topLvls:
            print "                TopLvlXML: " + topLvl.name
            print "                " + str(topLvl.treeName)
            for channel in topLvl.channels:
                print "                ---------> Channel: " + channel.name
                print "                           " + str(channel.treeName)
                for sample in channel.sampleList:
                    print "                           ---------> Sample: " + sample.name
                    print "                                      "+str(sample.treeName)
                    for (systName,syst) in sample.systDict.items():
                        print "                                      ---------> Systematic: " + syst.name
                        print "                                                 Low : " + str(syst.treeLoName)
                        print "                                                 High: " + str(syst.treeHiName)
        return

    def setVerbose(self,lvl):
        self.verbose=lvl
        for tl in self.topLvls:
            tl.verbose=lvl
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
        for toplvlxml in self.topLvls:
            toplvlxml.propagateFileList(self.fileList)

    def setTreeName(self,treeName):
        self.treeName = treeName
        return

    def propagateTreeName(self):
        for toplvlxml in self.topLvls:
            toplvlxml.propagateTreeName(self.treeName)
            pass
        return
        
    def executeAll(self):
        for tl in self.topLvls:
            self.execute(tl)
        return

    def execute(self,topLvl):
        """
        Make or get the histograms and generate the XML
        """
        print "Preparing histograms and/or workspace for TopLevelXML %s\n"%topLvl.name

        if self.plotHistos:
            cutHistoDict = {}
            cutStackDict = {}
            varStackDict = {}
            varSUSYDict = {}
            varDataDict = {}

        systDict = {}

        for (name,syst) in self.systDict.items():
            systDict[name] = syst

        for (name,syst) in topLvl.systDict.items():
            if not name in systDict.keys():
                systDict[name] = syst
            else:
                raise(Exception,"Syst name %s already defined at global level. Rename for top level %s",(name,topLvl.name))

        # Build channel string and cuts for normalization
        normRegions = []
        normString = ""
        normCuts = ""
        userNormDict = {}
        for (iChan,chan) in enumerate(topLvl.channels):
            for reg in chan.regions:
                if not chan.channelName in topLvl.validationChannels:
                    for reg in chan.regions:
                        normRegions.append(reg)
                        normString += reg
                        normCuts += "("+self.cutsDict[reg] + ") || "
        normCuts = normCuts.rstrip(" || ")                

        for (iChan,chan) in enumerate(topLvl.channels):
            for (iSam,sam) in enumerate(chan.sampleList):
                chan.infoDict[sam.name] = [("Nom",self.nomName,sam.weights,"")]
                if not sam.isData and not sam.isQCD:
                    for (systName,syst) in sam.systDict.items():
                        if self.verbose > 1:
                            print "!!!!!!!!!!!!!!"
                            print "CHAN",chan.name
                            print "SAM",sam.name
                            print "SYST",systName
                            print "TYPE",syst.type
                            print "METHOD",syst.method
                            print "LOW",syst.low
                            print "HIGH",syst.high
                            pass
                        if syst.type == "tree":
                            chan.infoDict[sam.name].append((systName+"High",syst.high,sam.weights,syst.method))
                            chan.infoDict[sam.name].append((systName+"Low",syst.low,sam.weights,syst.method))
                        elif syst.type == "weight":
                            chan.infoDict[sam.name].append((systName+"High",self.nomName,syst.high,syst.method))
                            chan.infoDict[sam.name].append((systName+"Low",self.nomName,syst.low,syst.method))
                        else:
                            chan.infoDict[sam.name].append((systName,syst.high,syst.low,syst.method))
                    
        
        for (iChan,chan) in enumerate(topLvl.channels):
            print "Channel: %s"%chan.name

            regionString = ""
            for reg in chan.regions:
                regionString += reg

            self.prepare.channel = chan

            sampleListRun = deepcopy(chan.sampleList)
#            for (iSam,sam) in enumerate(topLvl.sampleList):
            for (iSam,sam) in enumerate(sampleListRun):
                print "  Sample: %s"%sam.name

                # Run over the nominal configuration first

                # Set the weights
                if not sam.isData and not sam.isQCD:
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

                # Set the cuts
                if len(sam.cutsDict.keys()) == 0:
                    if not chan.variableName == "cuts":
                        self.prepare.cuts = self.cutsDict[regionString]
                else:
                    if not chan.variableName == "cuts":
                        self.prepare.cuts = sam.cutsDict[regionString]

                # Set the variable
                if sam.unit == "GeV":  
                    self.prepare.var = chan.variableName
                elif sam.unit == "MeV" and chan.variableName.find("/") < 0 and not chan.variableName.startswith("n"):
                    self.prepare.var = chan.variableName+"/1000."
                
                if sam.isData:
                    self.prepare.addHisto("h"+sam.name+"_"+regionString+"_obs_"+replaceSymbols(chan.variableName),useOverflow=chan.useOverflowBin,useUnderflow=chan.useUnderflowBin)
                    chan.addData("h"+sam.name+"_"+regionString+"_obs_"+replaceSymbols(chan.variableName))


                elif not sam.isQCD and not sam.isDiscovery:
                    if not len(sam.shapeFactorList):
                        self.prepare.addHisto("h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName),useOverflow=chan.useOverflowBin,useUnderflow=chan.useUnderflowBin)                
                    else:
                        self.hists["h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName)] = TH1F("h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName),"h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName),chan.nBins,chan.binLow,chan.binHigh)
                        for iBin in xrange(self.hists["h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName)].GetNbinsX()+1):
                            self.hists["h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName)].SetBinContent(iBin+1,1.)
                    chan.getSample(sam.name).setHistoName("h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName))

                    if not "h"+sam.name+"Nom_"+normString+"Norm" in self.hists.keys():
                        if self.readFromTree:
                            self.hists["h"+sam.name+"Nom_"+normString+"Norm"] = TH1F("h"+sam.name+"Nom_"+normString+"Norm","h"+sam.name+"Nom_"+normString+"Norm",1,0.5,1.5)
                            self.chains[self.prepare.currentChainName].Project("h"+sam.name+"Nom_"+normString+"Norm",normCuts,self.prepare.weights+" * ("+normCuts+")")
                        else:
                            self.hists["h"+sam.name+"Nom_"+normString+"Norm"] = None
                            try:
                                self.prepare.addHisto("h"+sam.name+"Nom_"+normString+"Norm")
                            except:    
                                # assume that if no histogram is made, then it is not needed  
                                pass

                    for (systName,syst) in chan.getSample(sam.name).systDict.items():
                        print "    Systematic: %s"%(systName)
                        self.prepare.weights = str(self.lumiUnits*self.outputLumi/self.inputLumi)
                        if syst.type == "weight":
                            self.prepare.weights += " * " + " * ".join(syst.high)
                            if self.readFromTree:
                                treeName = sam.treeName
                                if treeName=='': treeName = sam.name+self.nomName
                                self.prepare.read(treeName, sam.files)
                        elif syst.type == "tree":
                            self.prepare.weights += " * " + " * ".join(sam.weights)
                            if self.readFromTree:
                                # if the systematic has a dedicated file list - use it
                                if sam.name in syst.filesHi:
                                    filelist = syst.filesHi[sam.name]
                                else:
                                    # otherwise - take the sample file list
                                    filelist = sam.files
                                if sam.name in syst.treeHiName:
                                    treeName = syst.treeHiName[sam.name]
                                else:
                                    # otherwise - take the default tree name for the sample 
                                    treeName = sam.treeName + syst.high # NM
                                if treeName=='' or treeName==syst.high:
                                    treeName = sam.name+syst.high
                                self.prepare.read(treeName, filelist)
                        elif syst.type == "user":
                            self.prepare.weights += " * " + " * ".join(sam.weights)
                            if self.readFromTree:
                                treeName = sam.treeName
                                if treeName=='': treeName = sam.name+self.nomName
                                self.prepare.read(treeName, sam.files)
                            
                        if not syst.type == "user" or not self.readFromTree: 
                            if self.verbose>1:
                                print "!!!!!! adding histo","h"+sam.name+syst.name+"High_"+regionString+"_obs_"+replaceSymbols(chan.variableName)
                            try:    
                                self.prepare.addHisto("h"+sam.name+syst.name+"High_"+regionString+"_obs_"+replaceSymbols(chan.variableName),useOverflow=chan.useOverflowBin,useUnderflow=chan.useUnderflowBin)
                            except:
                                pass
                                
                        if syst.method == "userNormHistoSys" or syst.method == "normHistoSys":
                            if not "h"+sam.name+syst.name+"High_"+normString+"Norm" in self.hists.keys():
                                if self.readFromTree:
                                    self.hists["h"+sam.name+syst.name+"High_"+normString+"Norm"] = TH1F("h"+sam.name+syst.name+"High_"+normString+"Norm","h"+sam.name+syst.name+"High_"+normString+"Norm",1,0.5,1.5)
                                    self.chains[self.prepare.currentChainName].Project("h"+sam.name+syst.name+"High_"+normString+"Norm",normCuts,self.prepare.weights+" * ("+normCuts+")")
                                else:
                                    self.hists["h"+sam.name+syst.name+"High_"+normString+"Norm"] = None
                                    self.prepare.addHisto("h"+sam.name+syst.name+"High_"+normString+"Norm")

                        self.prepare.weights = str(self.lumiUnits*self.outputLumi/self.inputLumi)
                        if syst.type == "weight":
                            self.prepare.weights += " * " + " * ".join(syst.low)
                            if self.readFromTree:
                                treeName = sam.treeName
                                if treeName=='': treeName = sam.name+self.nomName
                                self.prepare.read(treeName, sam.files)
                        elif syst.type == "tree":
                            self.prepare.weights += " * " + " * ".join(sam.weights)
                            if self.readFromTree:
                                # if the systematic has a dedicated file list - use it
                                if sam.name in syst.filesLo:
                                    filelist = syst.filesLo[sam.name]
                                else:
                                    # otherwise - take the sample file list
                                    filelist = sam.files
                                    if sam.name in syst.treeLoName:
                                        treeName = syst.treeLoName[sam.name]
                                    else:
                                        # otherwise - take default tree name for the sample
                                        treeName = sam.treeName + syst.low
                                    if treeName=='' or treeName==syst.low:
                                        treeName = sam.name+syst.low
                                    self.prepare.read(treeName, filelist)
                        elif syst.type == "user":
                            self.prepare.weights += " * " + " * ".join(sam.weights)
                            if self.readFromTree:
                                treeName = sam.treeName
                                if treeName=='': treeName = sam.name+self.nomName
                                self.prepare.read(treeName, sam.files)

                        if not syst.type == "user" or not self.readFromTree:
                            if self.verbose>1:
                                print "!!!!!! adding histo","h"+sam.name+syst.name+"Low_"+regionString+"_obs_"+replaceSymbols(chan.variableName)
                            try:    
                                self.prepare.addHisto("h"+sam.name+syst.name+"Low_"+regionString+"_obs_"+replaceSymbols(chan.variableName),useOverflow=chan.useOverflowBin,useUnderflow=chan.useUnderflowBin)
                            except:
                                pass
                                
                        if syst.method == "userNormHistoSys" or syst.method == "normHistoSys":
                            if not "h"+sam.name+syst.name+"Low_"+normString+"Norm" in self.hists.keys():
                                if self.readFromTree:
                                    self.hists["h"+sam.name+syst.name+"Low_"+normString+"Norm"] = TH1F("h"+sam.name+syst.name+"Low_"+normString+"Norm","h"+sam.name+syst.name+"Low_"+normString+"Norm",1,0.5,1.5)
                                    self.chains[self.prepare.currentChainName].Project("h"+sam.name+syst.name+"Low_"+normString+"Norm",normCuts,self.prepare.weights+" * ("+normCuts+")")
                                else:
                                    self.hists["h"+sam.name+syst.name+"Low_"+normString+"Norm"] = None
                                    self.prepare.addHisto("h"+sam.name+syst.name+"Low_"+normString+"Norm")

                        nomName = "h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName)
                        highName = "h"+sam.name+syst.name+"High_"+regionString+"_obs_"+replaceSymbols(chan.variableName)
                        lowName = "h"+sam.name+syst.name+"Low_"+regionString+"_obs_"+replaceSymbols(chan.variableName)
                        
                        if syst.method == "histoSys":
                            chan.getSample(sam.name).addHistoSys(syst.name,nomName,highName,lowName,False,False)
                        elif syst.method == "histoSysOneSide":
                            chan.getSample(sam.name).addHistoSys(syst.name,nomName,highName,lowName,False,False,False,True)
                        elif syst.method == "overallSys":
                            highIntegral = configMgr.hists[highName].Integral()
                            lowIntegral = configMgr.hists[lowName].Integral()
                            nomIntegral = configMgr.hists[nomName].Integral()
                            try:
                                overallSystHigh = highIntegral / nomIntegral
                            except ZeroDivisionError:
                                print "WARNING generating High HistoSys for %s syst=%s nom=%g high=%g low=%g" % (nomName,syst.name,nomIntegral,highIntegral,lowIntegral)
                                overallSystHigh = 1.0 
                            try:
                                overallSystLow = lowIntegral / nomIntegral
                            except ZeroDivisionError:
                                print "WARNING generating Low HistoSys for %s syst=%s nom=%g high=%g low=%g" % (nomName,syst.name,nomIntegral,highIntegral,lowIntegral)
                                overallSystLow = 1.0
                            chan.getSample(sam.name).addOverallSys(syst.name,overallSystHigh,overallSystLow)
                        elif syst.method == "userOverallSys":
                            chan.getSample(sam.name).addOverallSys(syst.name,syst.high,syst.low)
                        elif syst.method == "overallHistoSys":
                            chan.getSample(sam.name).addHistoSys(syst.name,nomName,highName,lowName,True,False)
                        elif syst.method == "normHistoSys":
                            chan.getSample(sam.name).addHistoSys(syst.name,nomName,highName,lowName,False,True,False,False,sam.name,normString)
                        elif syst.method == "normHistoSysOneSide":
                            chan.getSample(sam.name).addHistoSys(syst.name,nomName,highName,lowName,False,True,False,True)
                        elif syst.method == "userHistoSys":
                            if not len(syst.high) == configMgr.hists[nomName].GetNbinsX() or not len(syst.low) == configMgr.hists[nomName].GetNbinsX():
                                raise ValueError("High and low must both be the same as the binning in nominal for userHistoSys %s"%(syst.name))
                            if configMgr.hists[highName] == None:
                                configMgr.hists[highName] = TH1F(highName,highName,configMgr.hists[nomName].GetNbinsX(),configMgr.hists[nomName].GetXaxis().GetXmin(),configMgr.hists[nomName].GetXaxis().GetXmax())
                                for iBin in xrange(configMgr.hists[nomName].GetNbinsX()):
                                    configMgr.hists[highName].SetBinContent(iBin+1,configMgr.hists[nomName].GetBinContent(iBin+1)*syst.high[iBin])
                            if configMgr.hists[lowName] == None:
                                configMgr.hists[lowName] = TH1F(lowName,lowName,configMgr.hists[nomName].GetNbinsX(),configMgr.hists[nomName].GetXaxis().GetXmin(),configMgr.hists[nomName].GetXaxis().GetXmax())
                                for iBin in xrange(configMgr.hists[nomName].GetNbinsX()):
                                    configMgr.hists[lowName].SetBinContent(iBin+1,configMgr.hists[nomName].GetBinContent(iBin+1)*syst.low[iBin])
                            chan.getSample(sam.name).addHistoSys(syst.name,nomName,highName,lowName,False,False)
                        elif syst.method == "userNormHistoSys":
                            if not len(syst.high) == configMgr.hists[nomName].GetNbinsX() or not len(syst.low) == configMgr.hists[nomName].GetNbinsX():
                                raise ValueError("High and low must both be the same as the binning in nominal for userHistoSys")
                            if configMgr.hists[highName] == None:
                                configMgr.hists[highName] = TH1F(highName,highName,configMgr.hists[nomName].GetNbinsX(),configMgr.hists[nomName].GetXaxis().GetXmin(),configMgr.hists[nomName].GetXaxis().GetXmax())
                                for iBin in xrange(configMgr.hists[nomName].GetNbinsX()):
                                    configMgr.hists[highName].SetBinContent(iBin+1,configMgr.hists[nomName].GetBinContent(iBin+1)*syst.high[iBin])
                            if configMgr.hists[lowName] == None:
                                configMgr.hists[lowName] = TH1F(lowName,lowName,configMgr.hists[nomName].GetNbinsX(),configMgr.hists[nomName].GetXaxis().GetXmin(),configMgr.hists[nomName].GetXaxis().GetXmax())
                                for iBin in xrange(configMgr.hists[nomName].GetNbinsX()):
                                    configMgr.hists[lowName].SetBinContent(iBin+1,configMgr.hists[nomName].GetBinContent(iBin+1)*syst.low[iBin])
                            if not (syst.name,sam.name) in userNormDict.keys():
                                userNormDict[(syst.name,sam.name)] = []
                                userNormDict[(syst.name,sam.name)].append((regionString,highName,lowName,nomName))
                            else:
                                userNormDict[(syst.name,sam.name)].append((regionString,highName,lowName,nomName))
                            chan.getSample(sam.name).addHistoSys(syst.name,nomName,highName,lowName,False,True,False,False,sam.name,normString)
                        elif syst.method == "shapeSys":
                            if syst.merged:
                                mergedName = ""
                                for s in syst.sampleList:
                                    mergedName += s
                                nomMergedName = "h"+mergedName+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName)
                                highMergedName = "h"+mergedName+syst.name+"High_"+regionString+"_obs_"+replaceSymbols(chan.variableName)
                                lowMergedName = "h"+mergedName+syst.name+"Low_"+regionString+"_obs_"+replaceSymbols(chan.variableName)
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
                                    chan.getSample(sam.name).shapeSystList.append((systName,nomMergedName+"Norm",syst.constraint,"","","",""))
                            else:
                                chan.getSample(sam.name).addShapeSys(syst.name,nomName,highName,lowName)
                                chan.getSample(sam.name).shapeSystList.append((systName,nomName+"Norm",configMgr.histCacheFile,"","","",""))
                elif sam.isQCD:
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
                        chan.getSample(sam.name).addHistoSys("QCDNorm_"+regionString+"_"+replaceSymbols(chan.variableName),prefixNom,prefixHigh,prefixLow,False,False)
                    elif chan.getSample(sam.name).qcdSyst == "overallSys":
                        highIntegral = configMgr.hists[prefixHigh].Integral()
                        lowIntegral = configMgr.hists[prefixLow].Integral()
                        nomIntegral = configMgr.hists[prefixNom].Integral()
                        try:
                            overallSystHigh = highIntegral / nomIntegral
                            overallSystLow = lowIntegral / nomIntegral
                        except ZeroDivisionError:
                            print "Error generating HistoSys for %s syst=%s nom=%g high=%g low=%g" % (nomName,"QCDNorm_"+regionString+"_"+replaceSymbols(chan.variableName),nomIntegral,highIntegral,lowIntegral)
                        chan.getSample(sam.name).addOverallSys("QCDNorm_"+regionString+"_"+replaceSymbols(chan.variableName),overallSystHigh,overallSystLow)
                    elif chan.getSample(sam.name).qcdSyst == "overallHistoSys":
                        chan.getSample(sam.name).addHistoSys("QCDNorm_"+regionString+"_"+replaceSymbols(chan.variableName),prefixNom,prefixHigh,prefixLow,True,False)
                    elif chan.getSample(sam.name).qcdSyst == "normHistoSys":
                        chan.getSample(sam.name).addHistoSys("QCDNorm_"+regionString+"_"+replaceSymbols(chan.variableName),prefixNom,prefixHigh,prefixLow,False,True)
                    elif chan.getSample(sam.name).qcdSyst == "shapeSys":
                        chan.getSample(sam.name).addShapeSys("QCDNorm_"+regionString+"_"+replaceSymbols(chan.variableName),prefixNom,prefixHigh,prefixLow)
                        chan.getSample(sam.name).shapeSystList.append(("QCDNorm_"+regionString+"_"+replaceSymbols(chan.variableName),prefixNom+"Norm","data/"+configMgr.analysisName+".root","","","",""))
                    elif chan.getSample(sam.name).qcdSyst == "uncorr":
                        chan.getSample(sam.name).setWrite(False)
                        for iBin in xrange(1,nHists+1):
                            qcdSam = sam.Clone()
                            qcdSam.name = sam.name+"_"+regionString+"_"+str(iBin)
                            chan.addSample(qcdSam)
                            chan.getSample(qcdSam.name).setWrite(True)
                            chan.getSample(qcdSam.name).setHistoName("h"+sam.name+"Nom_"+regionString+"_obs_"+replaceSymbols(chan.variableName)+"_"+str(iBin))
                            chan.getSample(qcdSam.name).addHistoSys("NormQCD"+regionString+"_"+replaceSymbols(chan.variableName)+"_"+str(iBin),prefixNom+"_"+str(iBin),prefixHigh+"_"+str(iBin),prefixLow+"_"+str(iBin),False,False)
                    else:
                        raise Exception("Incorrect systematic method specified for QCD: %s"%getSample(sam.name).qcdSyst)

        for (syst,sam) in userNormDict.keys():
            highIntegral = 0.
            lowIntegral = 0.
            nomIntegral = 0.
            for (reg,high,low,nom) in userNormDict[(syst,sam)]:
                highIntegral += self.hists[high].GetSumOfWeights()
                lowIntegral += self.hists[low].GetSumOfWeights()
                nomIntegral += self.hists[nom].GetSumOfWeights()

            for (reg,high,low,nom) in userNormDict[(syst,sam)]:
                try:
                    highWeight = highIntegral / nomIntegral
                    lowWeight = lowIntegral / nomIntegral

                    self.hists[high+"Norm"].Scale(1./highWeight)
                    self.hists[low+"Norm"].Scale(1./lowWeight)

                except ZeroDivisionError:
                    print "ERROR: generating HistoSys for %s syst=%s nom=%g high=%g low=%g remove from fit." % (nom,syst,nomIntegral,highIntegral,lowIntegral)

        if self.plotHistos:
            if not os.path.isdir("plots/"+self.analysisName):
                os.makedirs("plots/"+self.analysisName)

            for (iChan,chan) in enumerate(topLvl.channels):
                if chan.hasDiscovery: continue
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
                            canDict[(info[0],regString,replaceSymbols(chan.variableName))] = TCanvas("c"+topLvl.name+"_"+info[0]+"_"+regString+"_obs_"+replaceSymbols(chan.variableName),"c"+info[0]+"_"+regString+"_obs_"+replaceSymbols(chan.variableName),800,600,800,600)

                            stackDict[(info[0],regString,replaceSymbols(chan.variableName))] = THStack(topLvl.name+"_"+regString+"_obs_"+replaceSymbols(chan.variableName)+"Stack"+info[0],"")

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

                        if not topLvl.getSample(samName).isData and not topLvl.getSample(samName).isQCD:
                            self.hists["h"+samName+info[0]+"_"+regString+"_obs_"+replaceSymbols(chan.variableName)].SetLineColor(topLvl.getSample(samName).color)
                            self.hists["h"+samName+info[0]+"_"+regString+"_obs_"+replaceSymbols(chan.variableName)].SetFillColor(topLvl.getSample(samName).color)
                            stackDict[(info[0],regString,replaceSymbols(chan.variableName))].Add(self.hists["h"+samName+info[0]+"_"+regString+"_obs_"+replaceSymbols(chan.variableName)],"hist")
                            legDict[(info[0],regString,replaceSymbols(chan.variableName))].AddEntry(self.hists["h"+samName+info[0]+"_"+regString+"_obs_"+replaceSymbols(chan.variableName)],samName+info[0],"lf")
                        elif topLvl.getSample(samName).isQCD:
                            self.hists["h"+samName+"Nom_"+regString+"_obs_"+replaceSymbols(chan.variableName)].SetLineColor(topLvl.getSample(samName).color)
                            self.hists["h"+samName+"Nom_"+regString+"_obs_"+replaceSymbols(chan.variableName)].SetFillColor(topLvl.getSample(samName).color)
                            self.hists["h"+samName+"Low_"+regString+"_obs_"+replaceSymbols(chan.variableName)].SetLineColor(topLvl.getSample(samName).color)
                            self.hists["h"+samName+"Low_"+regString+"_obs_"+replaceSymbols(chan.variableName)].SetFillColor(topLvl.getSample(samName).color)
                            self.hists["h"+samName+"High_"+regString+"_obs_"+replaceSymbols(chan.variableName)].SetLineColor(topLvl.getSample(samName).color)
                            self.hists["h"+samName+"High_"+regString+"_obs_"+replaceSymbols(chan.variableName)].SetFillColor(topLvl.getSample(samName).color)
                            qcdNameDict[(regString,replaceSymbols(chan.variableName))] = "h"+samName+"Nom_"+regString+"_obs_"+replaceSymbols(chan.variableName)
                        else:
                            self.hists["h"+samName+"_"+regString+"_obs_"+replaceSymbols(chan.variableName)].SetLineColor(topLvl.getSample(samName).color)
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

                    if not os.path.isdir("plots/"+self.analysisName+"/"+topLvl.name):
                        os.mkdir("plots/"+self.analysisName+"/"+topLvl.name)
                    canDict[info].SaveAs("plots/"+self.analysisName+"/"+topLvl.name+"/stack"+info[1]+"_obs_"+info[2]+"_"+info[0]+".png")
                    
                    self.canvasList.append(canDict[info])
                    self.stackList.append(stackDict[info])
                    
        outputRootFile=None
        if self.readFromTree:
            outputRootFile = TFile(self.histCacheFile,"RECREATE")
        elif self.prepare.recreate:
            outputRootFile = self.prepare.cacheFile
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

        #if not self.readFromTree:
            #self.prepare.close()

        if self.executeHistFactory:
            topLvl.close()   #<--- this internally calls channel.close()
            topLvl.execute()

# Shouldn't have multiple imports... doesn't matter as singleton but good to check user isn't doing something strange

if vars().has_key("configMgr"):
    raise RuntimeError("ConfigManager already exists, no multiple imports allowed!!!")

# Instantiate the singleton

configMgr = ConfigManager()
