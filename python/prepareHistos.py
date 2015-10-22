"""
 **********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : PrepareHistos                                                         *
 * Created: November 2012                                                         *
 *                                                                                *
 * Description:                                                                   *
 *      Class to define histogram preparation methods                             *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************
"""

from ROOT import gROOT,TFile,TH1F,Double,gDirectory,TChain,TObject
from math import sqrt
from logger import Logger
import os

log = Logger('PrepareHistos')

class PrepareHistos(object):
    """
    Class to define histogram preparation methods
    """

    def __init__(self, useCache=False, useCacheToTreeFallback=False):
        """
        Initialise the preparation object

        @param useCache Read out histograms from the cache file rather than trees
        @param useCacheToTreeFallBack If reading from histograms, fall back to trees in case they are not found
        """
        from configManager import configMgr
        
        self.configMgr = configMgr
        self.var = ""
        self.cuts = ""
        self.weights = ""
        self.channel = None

        self.cutDict = {}
        self.cutList = []
        self.histList = []
        self.nameList = []

        # histos or trees?
        self.useCache = useCache

        # for trees
        self.currentChainName=''

        # for histos
        self.cacheFileName = ''
        self.cache2FileName = ''
       
        # fallback?
        self.useCacheToTreeFallback = useCacheToTreeFallback

    def __del__(self):
        if self.cacheFile != None: self.cacheFile.Close()
        if self.cache2File != None: self.cache2File.Close()
   
    def setUseCacheToTreeFallback(useCacheToTreeFallback):
        """
        Set the use of fallback to trees to the argument

        @param useCacheToTreeFallback Boolean to determine fallback
        """
        self.useCacheToTreeFallback = useCacheToTreeFallback

    def setHistoPaths(self, filepath, file2path=''):
        """
        Set histogram paths

        @param filepath Name of the cache file
        @param file2path Optional path of extra file (used in conjunction with fallback)
        """
        self.cacheFileName = filepath
        self.cache2FileName = file2path
        
        if file2path!='':
            self.cache2File = TFile.Open(file2path,"READ")
            if self.cache2File.IsZombie():
                self.cache2File = None
        else:
            self.cache2File = None
        
        if os.path.isfile(filepath):
            if file2path=='': # default, no archive file
                self.cacheFile = TFile(filepath,"READ")
                self.recreate = False
            else:
                self.cacheFile = TFile(filepath,"UPDATE")
                self.recreate = True
        else:
            self.cacheFile = TFile(filepath,"RECREATE")
            self.recreate = True

    def checkTree(self, treeName, fileList):
        """
        Check existence of a tree in a list of files

        @param treeName Name of the tree
        @param fileList List of files

        @retval Returns true if the tree has been found
        """
        if self.useCache and not self.useCacheToTreeFallback:
            log.debug("Not using cache or cache fallback: no trees")
            return False

        if len(fileList) == 0 or len(treeName) == 0: 
            return False
        
        for f in fileList:
            file = TFile.Open(f)
            if file is None:
                continue

            tree = file.Get(treeName)
            if not tree or tree is None:
                file.Close()
                continue

            if tree is not None and tree.ClassName() != 'TTree':
                file.Close()
                continue

            file.Close()
            return True

        return False

    def read(self, treeName, fileList):
        """
        Read in the root object that will make histograms and set the TChain objects in ConfigManager

        @param treeName Name of the tree to use
        @param fileList List of files to use
        """
        if self.useCache and not self.useCacheToTreeFallback and treeName == '':
            log.info("Not using trees, will read histograms from %s" % (fileList))
            return

        if not self.useCache and treeName == '':
            log.fatal("No tree name provided")
            return

        if self.useCache and self.useCacheToTreeFallback and treeName == '':
            log.warning("No tree name provided, cache fallback to trees will not work")
            return

        if not self.currentChainName == '' and not treeName in self.currentChainName:
            log.debug("read(): deleting chain {0} (treeName asked = {1})".format(self.currentChainName, treeName))
            del self.configMgr.chains[self.currentChainName]

        chainID = "{0}_{1}".format(treeName, "_".join(fileList))
        #chainID = treeName
        #for fileName in fileList: chainID += '_' +fileName
        
        self.currentChainName = chainID
        
        ## MB : no need to recreate chain if it already exists
        if not chainID in self.configMgr.chains:
            log.debug("Creating chain {0}".format(chainID))
            self.configMgr.chains[chainID] = TChain(treeName)
            for fileName in fileList:
                self.configMgr.chains[self.currentChainName].Add(fileName)

        return

    def addHisto(self, name, nBins=0, binLow=0., binHigh=0., nBinsY=0, binLowY=0., binHighY=0., useOverflow=False, useUnderflow=False, forceNoFallback=False):
        """
        Make histogram and add it to the dictionary of prepared histograms
        
        @param name Name of the histogram
        @param nBins Number of X bins
        @param binLow Lower edge of left X bin
        @param binHigh Higher edge of rigth X bin
        @param nBinsY Number of Y bins
        @param binLowY Lower edge of left Y bin
        @param binHighY Higher edge of right Y bin
        @param useOverflow Use the overflow bins or not? 
        @param useUnderflow Use the underflow bins or not ?
        @param forceNoFallBack If true, never use the fallback mechanism for this histogram
        
        @retval The constructed histogram
        """
        if self.useCache:
            return self.__addHistoFromCache(name, nBins, binLow, binHigh, useOverflow, useUnderflow, forceNoFallback)
   
        return self.__addHistoFromTree(name, nBins, binLow, binHigh, nBinsY, binLowY, binHighY, useOverflow, useUnderflow)

    def __addHistoFromTree(self, name, nBins=0, binLow=0., binHigh=0., nBinsY=0, binLowY=0., binHighY=0., useOverflow=False, useUnderflow=False):
        """
        Use the TTree::Draw method to create the histograms for var from cuts and weights defined in instance
        Recover from ROOT memory and add to dictionary of histograms
        
        @param name Name of the histogram
        @param nBins Number of X bins
        @param binLow Lower edge of left X bin
        @param binHigh Higher edge of rigth X bin
        @param nBinsY Number of Y bins
        @param binLowY Lower edge of left Y bin
        @param binHighY Higher edge of right Y bin
        @param useOverflow Use the overflow bins or not? 
        @param useUnderflow Use the underflow bins or not ?
        
        @retval The constructed histogram
        """

        log.debug("__addHistoFromTree: %s" % name)

        if self.var == "cuts":
            if self.configMgr.hists[name] is None:
                self.configMgr.hists[name] = TH1F(name, name, len(self.channel.regions), self.channel.binLow, float(len(self.channel.regions))+self.channel.binLow)
                for (iReg,reg) in enumerate(self.channel.regions):
                    log.debug("__addHistoFromTree: append %s in region %s" % (name, reg))
                    self.cuts = self.configMgr.cutsDict[reg]
                    
                    tempName = "%stemp%s" % (name, str(iReg))
                    tempHist = TH1F(tempName, tempName, 1, 0.5, 1.5)

                    log.debug("__addHistoFromTree: projecting into %s with cuts %s weights %s" % (tempName, self.cuts, self.weights))
                    log.debug("__addHistoFromTree: Project(\"%s\", \"%s\", \"%s\")" % (tempName, self.cuts, self.weights) )

                    self.configMgr.chains[self.currentChainName].Project(tempName, self.cuts, self.weights)
                    
                    error = Double()
                    integral = tempHist.IntegralAndError(1, tempHist.GetNbinsX(), error)
                    self.configMgr.hists[name].SetBinContent(iReg+1, integral)
                    self.configMgr.hists[name].SetBinError(iReg+1, error)
                    self.configMgr.hists[name].GetXaxis().SetBinLabel(iReg+1, reg)
                    tempHist.Delete()

                    for iBin in xrange(1, self.configMgr.hists[name].GetNbinsX()+1):
                        binVal = self.configMgr.hists[name].GetBinContent(iBin)
                        binErr = self.configMgr.hists[name].GetBinError(iBin)
                        if binVal < 0.0:
                            self.configMgr.hists[name].SetBinContent(iBin, 0.0)

        else:
            if self.configMgr.hists[name] is None:
                if self.var.find(":") == -1:
                    self.configMgr.hists[name] = TH1F(name, name, self.channel.nBins, self.channel.binLow, self.channel.binHigh)
                else:
                    self.configMgr.hists[name] = TH2F(name, name, self.channel.nBins, self.channel.binLow, self.channel.binHigh, self.channelnBinsY, self.channel.binLowY, self.channel.binHighY)
                for (iReg,reg) in enumerate(self.channel.regions):
                    tempName = "%stemp%s" % (name, str(iReg))
                    #self.cuts = self.configMgr.cutsDict[reg]
                    if self.var.find(":") == -1:                    
                        tempHist = TH1F(tempName, tempName, self.channel.nBins, self.channel.binLow, self.channel.binHigh)
                    else:
                        tempHist = TH2F(tempName, tempName, self.channel.nBins, self.channel.binLow, self.channel.binHigh, self.channelnBinsY, self.channel.binLowY, self.channel.binHighY)
                    #print "!!!!!! PROJECTING",name+"temp"+str(iReg)
                    #print "!!!!!! VAR",self.var
                    #print "!!!!!! WEIGHTS",self.weights
                    #print "!!!!!! CUTS",self.cuts
                    nCuts = self.configMgr.chains[self.currentChainName].Project(tempName, self.var, self.weights+" * ("+self.cuts+")")
                    self.configMgr.hists[name].Add(tempHist.Clone())
                    tempHist.Delete()

                    for iBin in xrange(1, self.configMgr.hists[name].GetNbinsX()+1):
                        binVal = self.configMgr.hists[name].GetBinContent(iBin)
                        binErr = self.configMgr.hists[name].GetBinError(iBin)
                        if binVal < 0.:
                            self.configMgr.hists[name].SetBinContent(iBin, 0.)
                        #if binErr==0:
                        #    self.configMgr.hists[name].SetBinError(iBin,1E-8)

        self.name = name

        #Over/Underflow bins
        if useOverflow or useUnderflow:
            self.updateOverflowBins(self.configMgr.hists[name], useOverflow, useUnderflow)
            
        return self.configMgr.hists[name]
    
    def __addHistoFromCacheWithoutFallback(self, name, nBins=None, binLow=None, binHigh=None, useOverflow=False, useUnderflow=False):
        """ simple helper to prevent specifying all the defaults """
        return self.__addHistoFromCache(name, nBins, binLow, binHigh, useOverflow, useUnderflow, True, True)

    def __addHistoFromCache(self, name, nBins=None, binLow=None, binHigh=None, useOverflow=False, useUnderflow=False, forceNoFallback=False, forceReturn=False):
        """
        Add this histogram to the dictionary of histograms.
        """
        #Note: useOverflow and useUnderflow has no effect. It's there just for symmetry with TreePrepare above.

        if self.configMgr.hists[name] is None:
            try:
                self.configMgr.hists[name] = self.cache2File.Get(name)
                testsum = self.configMgr.hists[name].GetSum()
            except: # IOError:
                log.info("Could not get histogram <%s> from backupCacheFile %s, trying cacheFile" % (name, self.cache2FileName))
                try:
                    self.configMgr.hists[name] = self.cacheFile.Get(name)
                    testsum = self.configMgr.hists[name].GetSum()
                except: # IOError:
                    if forceNoFallback or not self.useCacheToTreeFallback:
                        self.configMgr.hists[name] = None
                        if forceReturn: # used for QCD histograms
                            log.info("Could not find histogram <"+name+"> in "+self.cacheFileName+" ! Force return.")
                            return None
                        log.debug("__addHistoFromCache(): forceNoFallback=%s useCacheToTreeFallback=%s" % (forceNoFallback, self.useCacheToTreeFallback))
                        log.error("Could not find histogram <"+name+"> in "+self.cacheFileName+" ! ")
                        raise #Exception("Could not find histogram <"+name+"> in "+self.cacheFileName)
                    else:
                        log.info("Could not find histogram <"+name+"> in "+self.cacheFileName+", trying from tree ")
                        
                        self.configMgr.hists[name] = None
                        return self.__addHistoFromTree(name, nBins, binLow, binHigh, nBins, binLow, binHigh, useOverflow, useUnderflow)

        if not (self.configMgr.hists[name] is None):
            if not (int(self.channel.nBins) == int(self.configMgr.hists[name].GetNbinsX())) or \
               ( abs(self.channel.binLow - self.configMgr.hists[name].GetBinLowEdge(1))>0.00001 ) or \
               ( abs(self.channel.binHigh - self.configMgr.hists[name].GetXaxis().GetBinUpEdge(self.configMgr.hists[name].GetNbinsX())) > 0.00001):
                if forceNoFallback or not self.useCacheToTreeFallback:
                    self.configMgr.hists[name] = None
                    if forceReturn: # used for QCD histograms
                        log.info("Could not find histogram <"+name+"> in "+self.cacheFileName+" ! Force return.")
                        return None
                    log.debug("__addHistoFromCache(): forceNoFallback=%s useCacheToTreeFallback=%s" % (forceNoFallback, self.useCacheToTreeFallback))
                    log.error("Could not find histogram <"+name+"> in "+self.cacheFileName+" ! ")
                    raise #Exception("Could not find histogram <"+name+"> in "+self.cacheFileName)
                else:
                    log.info("Histogram has different binning <"+name+"> in "+self.cacheFileName+", trying from tree ")
                    log.info("addHistoFromCache: required binning %d,%f,%f, while histo has %d,%f,%f" % ( self.channel.nBins,self.channel.binLow,self.channel.binHigh,self.configMgr.hists[name].GetNbinsX(), self.configMgr.hists[name].GetBinLowEdge(1),self.configMgr.hists[name].GetXaxis().GetBinUpEdge(self.configMgr.hists[name].GetNbinsX()) ))
                    self.configMgr.hists[name] = None
                    return self.__addHistoFromTree(name, self.channel.nBins, self.channel.binLow, self.channel.binHigh, nBins, binLow, binHigh, useOverflow, useUnderflow)

        self.name = name
        return self.configMgr.hists[name]

    def addQCDHistos(self, sample, useOverflow=False, useUnderflow=False):
        """
        Make the nominal QCD histogram and its errors 

        @param sample The sample to use
        @param useOverflow Use the overflow bins or not
        @param useUnderflow Use the underflow bins or not
        """
        if self.useCache:
            return self.__addQCDHistosFromCache(sample, useOverflow, useUnderflow)
    
        return self.__addQCDHistosFromTree(sample, useOverflow, useUnderflow)
    
    def __addQCDHistosFromTree(self, sample, useOverflow=False, useUnderflow=False):
        """
        Make the nominal QCD histogram and its up and down fluctuations
        
        @param sample The sample to use
        @param useOverflow Use the overflow bins or not
        @param useUnderflow Use the underflow bins or not
        """
        regString = "".join(self.channel.regions)

        prefixNom = "h%sNom_%s_obs_%s" % (sample.name, regString, self.channel.variableName.replace("/","") )
        prefixHigh = "h%sHigh_%s_obs_%s" % (sample.name, regString, self.channel.variableName.replace("/","") )
        prefixLow = "h%sLow_%s_obs_%s" % (sample.name, regString, self.channel.variableName.replace("/","") )
        
        if self.channel.hasBQCD:
            self.weights = self.configMgr.weightsQCDWithB
            weightsQCD = self.configMgr.weightsQCDWithB
        else:
            self.weights = self.configMgr.weightsQCD
            weightsQCD = self.configMgr.weightsQCD
        
        self.__addHistoFromTree(prefixNom)
        self.__addHistoFromTree(prefixHigh)
        self.__addHistoFromTree(prefixLow)

        self.configMgr.hists[prefixNom].SetCanExtend(0)
        self.configMgr.hists[prefixHigh].SetCanExtend(0)
        self.configMgr.hists[prefixLow].SetCanExtend(0)

        systName = "%sSyst" % self.name
        statName = "%sStat" % self.name
        qcdHistoSyst = TH1F(systName, systName, self.channel.nBins, self.channel.binLow, self.channel.binHigh)
        qcdHistoStat = TH1F(statName, statName, self.channel.nBins, self.channel.binLow, self.channel.binHigh)
        
        if self.var == "cuts":
            for (iReg,reg) in enumerate(self.channel.regions):
                if self.configMgr.hists[prefixNom+"_"+str(iReg+1)] is None:
                    tempNameSyst = "%sSyst%s" % (self.name, str(iReg+1))
                    qcdHistoSystTemp = TH1F(tempNameSyst, tempNameSyst, self.channel.nBins, self.channel.binLow, self.channel.binHigh)
                    self.configMgr.chains[self.currentChainName].Project(tempNameSyst, self.configMgr.cutsDict[reg], self.weights+"Syst")
                    qcdHistoSyst.SetBinContent(iReg+1,qcdHistoSystTemp.GetBinContent(1))
                    
                    tempNameStat = "%sStat%s" % (self.name, str(iReg+1))
                    qcdHistoStatTemp = TH1F(tempNameStat, tempNameStat, self.channel.nBins, self.channel.binLow, self.channel.binHigh)
                    self.configMgr.chains[self.currentChainName].Project(tempNameStat, self.configMgr.cutsDict[reg], self.weights+"Stat")
                    qcdHistoStat.SetBinContent(iReg+1, qcdHistoStatTemp.GetBinContent(1))
        else:
            if self.weights == "1.0":
                sysWeightStat = "0.01" #rough average of Dan's results
                sysWeightSyst = "0.25" #rough average of Dan's results
            else:
                sysWeightStat = self.weights+"Stat"
                sysWeightSyst = self.weights+"Syst"
                
            if self.configMgr.hists[prefixNom+"_"+str(1)] is None:
                self.configMgr.chains[self.currentChainName].Project(systName, self.var, sysWeightSyst+" * ("+self.cuts+")")
                self.configMgr.chains[self.currentChainName].Project(statName, self.var, sysWeightStat+" * ("+self.cuts+")")

        ## correct nominal bins (not overflow)
        for iBin in xrange(1,self.configMgr.hists[prefixNom].GetNbinsX()+1):
            #
            if self.configMgr.hists[prefixNom+"_"+str(iBin)] is None:
                if self.channel.variableName == "cuts":
                    self.configMgr.hists[prefixNom+"_"+str(iBin)] = TH1F(prefixNom+"_"+str(iBin),prefixNom+"_"+str(iBin),len(self.channel.regions),self.channel.binLow,float(len(self.channel.regions))+self.channel.binLow)
                else:
                    self.configMgr.hists[prefixNom+"_"+str(iBin)] = TH1F(prefixNom+"_"+str(iBin),prefixNom+"_"+str(iBin),self.channel.nBins,self.channel.binLow,self.channel.binHigh)

                binVal = self.configMgr.hists[prefixNom].GetBinContent(iBin)
                #binError = sqrt(qcdHistoSyst.GetBinContent(iBin)**2+qcdHistoStat.GetBinContent(iBin)**2)
                #binStatError = qcdHistoStat.GetBinContent(iBin)
                if qcdHistoStat.GetBinContent(iBin)<-1*qcdHistoSyst.GetBinContent(iBin)**2: # Exception for folks using negative weights 
                    binError = sqrt(-qcdHistoSyst.GetBinContent(iBin)**2-qcdHistoStat.GetBinContent(iBin))
                else: 
                    binError = sqrt(qcdHistoSyst.GetBinContent(iBin)**2+qcdHistoStat.GetBinContent(iBin))

                if qcdHistoStat.GetBinContent(iBin)<0: # Check for negative weights (possible in QCD!)
                    binStatError = sqrt(-qcdHistoStat.GetBinContent(iBin))
                else:
                    binStatError = sqrt(qcdHistoStat.GetBinContent(iBin))
                binSystError = qcdHistoSyst.GetBinContent(iBin)

                ##self.configMgr.hists[prefixNom+"_"+str(iBin)].SetBinContent(iBin,self.configMgr.hists[prefixNom].GetBinContent(iBin))
                #
                #print "GREPME %s bin %g content %.2g stat error %.2g syst error %.2g total error %.2g" % (prefixNom,iBin,self.configMgr.hists[prefixNom].GetBinContent(iBin),binStatError,binSystError,binError)
                if binVal > 0.:
                    #self.configMgr.hists[prefixNom].SetBinContent(iBin,binVal) 
                    self.configMgr.hists[prefixNom+"_"+str(iBin)].SetBinContent(iBin,self.configMgr.hists[prefixNom].GetBinContent(iBin))
                else:
                    self.configMgr.hists[prefixNom+"_"+str(iBin)].SetBinContent(iBin,0.)
                    self.configMgr.hists[prefixNom+"_"+str(iBin)].SetBinError(iBin,binError)
                    self.configMgr.hists[prefixNom].SetBinContent(iBin,0.)
                    self.configMgr.hists[prefixNom].SetBinError(iBin,binError)
            #
            if self.configMgr.hists[prefixHigh+"_"+str(iBin)] is None:
                if self.channel.variableName == "cuts":
                    self.configMgr.hists[prefixHigh+"_"+str(iBin)] = TH1F(prefixHigh+"_"+str(iBin),prefixHigh+"_"+str(iBin),len(self.channel.regions),self.channel.binLow,float(len(self.channel.regions))+self.channel.binLow)
                else:
                    self.configMgr.hists[prefixHigh+"_"+str(iBin)] = TH1F(prefixHigh+"_"+str(iBin),prefixHigh+"_"+str(iBin),self.channel.nBins,self.channel.binLow,self.channel.binHigh)
                if binVal+binError > 0.: # self.configMgr.hists[prefixNom].GetBinContent(iBin) > 0.:
                    self.configMgr.hists[prefixHigh+"_"+str(iBin)].SetBinContent(iBin,binVal+binError) #self.configMgr.hists[prefixNom].GetBinContent(iBin)+binError)
                    self.configMgr.hists[prefixHigh].SetBinContent(iBin,binVal+binError) #self.configMgr.hists[prefixNom].GetBinContent(iBin)+binError)
                else:
                    self.configMgr.hists[prefixHigh+"_"+str(iBin)].SetBinContent(iBin,0.)
                    self.configMgr.hists[prefixHigh+"_"+str(iBin)].SetBinError(iBin,binError)
                    self.configMgr.hists[prefixHigh].SetBinContent(iBin,0.)
                    self.configMgr.hists[prefixHigh].SetBinError(iBin,binError)
            #
            if self.configMgr.hists[prefixLow+"_"+str(iBin)] is None:
                if self.channel.variableName == "cuts":
                    self.configMgr.hists[prefixLow+"_"+str(iBin)] = TH1F(prefixLow+"_"+str(iBin),prefixLow+"_"+str(iBin),len(self.channel.regions),self.channel.binLow,float(len(self.channel.regions))+self.channel.binLow)
                else:
                    self.configMgr.hists[prefixLow+"_"+str(iBin)] = TH1F(prefixLow+"_"+str(iBin),prefixLow+"_"+str(iBin),self.channel.nBins,self.channel.binLow,self.channel.binHigh)
                if (binVal-binError)>0. : # ( self.configMgr.hists[prefixNom].GetBinContent(iBin) - binError ) > 0.:
                    self.configMgr.hists[prefixLow+"_"+str(iBin)].SetBinContent(iBin,binVal-binError) # self.configMgr.hists[prefixNom].GetBinContent(iBin)-binError)
                    self.configMgr.hists[prefixLow].SetBinContent(iBin,binVal-binError) # self.configMgr.hists[prefixNom].GetBinContent(iBin)-binError)
                else:
                    self.configMgr.hists[prefixLow+"_"+str(iBin)].SetBinContent(iBin, 0.)
                    self.configMgr.hists[prefixLow+"_"+str(iBin)].SetBinError(iBin, binError)
                    self.configMgr.hists[prefixLow].SetBinContent(iBin, 0.)
                    self.configMgr.hists[prefixLow].SetBinError(iBin, binError)

        ## MB : also correct the overflow bin!
        for iBin in xrange(self.configMgr.hists[prefixNom].GetNbinsX()+1, self.configMgr.hists[prefixNom].GetNbinsX()+2):
            #
            binVal = self.configMgr.hists[prefixNom].GetBinContent(iBin)
            binError = sqrt(qcdHistoSyst.GetBinContent(iBin)**2+qcdHistoStat.GetBinContent(iBin))
            binStatError = sqrt(qcdHistoStat.GetBinContent(iBin))
            ##binError = sqrt(qcdHistoSyst.GetBinContent(iBin)**2+qcdHistoStat.GetBinContent(iBin)**2)
            ##binStatError = qcdHistoStat.GetBinContent(iBin)
            binSystError = qcdHistoSyst.GetBinContent(iBin)
            #print "GREPME %s bin %g content %.2g stat error %.2g syst error %.2g total error %.2g" % (prefixNom,iBin,self.configMgr.hists[prefixNom].GetBinContent(iBin),binStatError,binSystError,binError)
            if binVal > 0.: # self.configMgr.hists[prefixNom].GetBinContent(iBin) > 0.:
                pass
            else:
                self.configMgr.hists[prefixNom].SetBinContent(iBin, 0.)
            #
            if binVal+binError > 0.: # self.configMgr.hists[prefixNom].GetBinContent(iBin) > 0.:
                self.configMgr.hists[prefixHigh].SetBinContent(iBin, binVal+binError) #self.configMgr.hists[prefixNom].GetBinContent(iBin)+binError)
            else:
                self.configMgr.hists[prefixHigh].SetBinContent(iBin, 0.)
                self.configMgr.hists[prefixHigh].SetBinError(iBin, binStatError)
            #
            if (binVal-binError)>0. : # ( self.configMgr.hists[prefixNom].GetBinContent(iBin) - binError ) > 0.:
                self.configMgr.hists[prefixLow].SetBinContent(iBin, binVal-binError) # self.configMgr.hists[prefixNom].GetBinContent(iBin)-binError)
            else:
                self.configMgr.hists[prefixLow].SetBinContent(iBin, 0.)
                self.configMgr.hists[prefixLow].SetBinError(iBin, binStatError)

        #Over/Underflow bins
        if useOverflow or useUnderflow:
            self.updateOverflowBins(self.configMgr.hists[prefixNom], useOverflow, useUnderflow)
            self.updateOverflowBins(self.configMgr.hists[prefixLow], useOverflow, useUnderflow)
            self.updateOverflowBins(self.configMgr.hists[prefixHigh], useOverflow, useUnderflow)

        return
    
    def __addQCDHistosFromCache(self, sample, useOverflow=False, useUnderflow=False):
        #Note: useOverflow and useUnderflow has no effect. It's there just for symmetry with TreePrepare above.
        """
        Read the nominal, high and low QCD histograms. Fallback only in case nominals not present.
        
        @param sample The sample to use
        @param useOverflow Use the overflow bins or not. Note: has no effect, only present for symmetry with TreePrepare
        @param useUnderflow Use the underflow bins or not. Note: has no effect, only present for symmetry with TreePrepare
        """
        regString = "".join(self.channel.regions)

        prefixNom = "h%sNom_%s_obs_%s" % (sample.name, regString, self.channel.variableName.replace("/","") )
        prefixHigh = "h%sHigh_%s_obs_%s" % (sample.name, regString, self.channel.variableName.replace("/","") )
        prefixLow = "h%sLow_%s_obs_%s" % (sample.name, regString, self.channel.variableName.replace("/","") )

        # NOTE: these histograms should NOT fallback to trees, but we fallback this entire function!
        self.__addHistoFromCacheWithoutFallback(prefixNom) 
        self.__addHistoFromCacheWithoutFallback(prefixHigh)
        self.__addHistoFromCacheWithoutFallback(prefixLow)

        # if _any_ of them don't exist, just return the tree function
        if self.configMgr.hists[prefixNom] == None or self.configMgr.hists[prefixHigh] == None or self.configMgr.hists[prefixLow] == None:
            return self.__addQCDHistosFromTree(sample, useUnderflow, useOverflow)

        if self.channel.variableName == "cuts":
            nHists = len(self.channel.regions)
        else:
            nHists = self.channel.nBins

        for iBin in xrange(1,nHists+1):
            self.__addHistoFromCacheWithoutFallback(prefixNom+"_"+str(iBin))
            self.__addHistoFromCacheWithoutFallback(prefixHigh+"_"+str(iBin))
            self.__addHistoFromCacheWithoutFallback(prefixLow+"_"+str(iBin))

        return self.configMgr.hists[prefixNom], self.configMgr.hists[prefixLow], self.configMgr.hists[prefixHigh]

    def updateHistBin(self, h, binIn, binOver):
        """
        Update a histogram bin with the overflow information

        @param h The histogram
        @param binIn The bin to add the content to
        @param binOver The overflow bin touse
        """

        newVal = h.GetBinContent(binIn) + h.GetBinContent(binOver)
        h.SetBinContent(binIn,newVal)
        h.SetBinContent(binOver,0.0)
        e1 = h.GetBinError(binIn)
        e2 = h.GetBinError(binOver)
        newErr = sqrt(e1*e1 + e2*e2)
        h.SetBinError(binIn,newErr)
        h.SetBinError(binOver,0.0)
        return

    def updateOverflowBins(self, h, useOverflow, useUnderflow):
        """
        Update all underflow and overflow bins for the histogram depending on the parameters. Calls updateHistBin().

        @param h The histogram
        @param useOverflow Use the overflow bin? 
        @param useUnderflow Use the underflow bin?
        """
        if useOverflow:
            binIn = h.GetNbinsX()
            binOver = binIn+1
            self.updateHistBin(h, binIn, binOver)

        if useUnderflow:
            binIn = 1
            binOver = 0
            self.updateHistBin(h, binIn, binOver)

        return

