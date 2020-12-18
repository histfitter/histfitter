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

from ROOT import gROOT, TFile, TH1F, gDirectory, SetOwnership
from ROOT import TChain, TObject, TTree, TIter
from math import sqrt
from logger import Logger
import os

log = Logger('PrepareHistos')

def pairwise(iterable):
    import itertools
    
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)

def getBinEdges(hist, axis, index=None, overflow=False):
    if axis == 0:
        nbins = hist.GetNbinsX()
        ax = hist.GetXaxis()
    elif axis == 1:
        nbins = hist.GetNbinsY()
        ax = hist.GetYaxis()
    elif axis == 2:
        nbins = hist.GetNbinsZ()
        ax = hist.GetZaxis()
    else:
        raise ValueError("axis must be 0, 1, or 2")   
 
    if index is None:
        def temp_generator():
            if overflow:
                yield float('-inf')
            for index in range(1, nbins + 1):
                yield ax.GetBinLowEdge(index)
            yield ax.GetBinUpEdge(nbins)
            if overflow:
                yield float('+inf')
        return temp_generator()
    
    index = index % (nbins + 3)
    if index == 0:
        return float('-inf')
    if index == nbins + 2:
        return float('+inf')
    
    return ax.GetBinLowEdge(index)

def range_subset(range1, range2):
    """Whether range1 is a subset of range2."""
    if not range1:
        return True  # empty range is subset of anything
    if not range2:
        return False  # non-empty range can't be subset of empty range
    if len(range1) > 1 and range1.step % range2.step:
        return False  # must have a single value or integer multiple step
    return range1.start in range2 and range1[-1] in range2

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

        # for checking bin edge consistency
        self.regBins = {}

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
        
        # Check if optional file is accessible and not a zombie
        if file2path != '': 
            self.cache2File = TFile.Open(file2path,"READ")
            if self.cache2File and self.cache2File.IsZombie():
                self.cache2File = None
        else: 
            self.cache2File = None
        
        # Check if cache file is accessible and not a zombie
        self.cacheFile = TFile.Open(filepath, "READ")

        if (self.cacheFile) and (not self.cacheFile.IsZombie()):
            if file2path=='' and not self.useCacheToTreeFallback:
                '''
                default, no archive file and no fallback activated
                all possible sources of histograms not in self.cacheFile
                are therefore excluded and read-only mode applied for opening the TFile
                '''
                self.cacheFile = TFile.Open(filepath,"READ")
                self.recreate = False
            else:
                self.cacheFile = TFile.Open(filepath,"UPDATE")
                self.recreate = True
        else:
            self.cacheFile = TFile.Open(filepath,"RECREATE")
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

    def read(self, input_files, suffix="", friendTreeName=""):
        """
        Read in the root object that will make histograms and set the TChain objects in ConfigManager

        @param input_files List of input trees to use
        """
        if self.useCache and not self.useCacheToTreeFallback and len(input_files) == 0:
            log.info("Not using trees, will read histograms")
            return

        if self.useCache and self.useCacheToTreeFallback and len(input_files) == 0:
            log.warning("No input files provided, cache fallback to trees will not work for current sample")
            return

        if (not self.useCache) or (self.useCache and self.useCacheToTreeFallback):
            # If we're not using the cache, or if we're using the fallback to trees, check that all treenames are given
            for i in input_files:
                if i.treename == '':
                    log.fatal("No tree name provided for input file {}".format(i.filename))
                    return

        log.debug("read(): current chain ID = '{}'".format(self.currentChainName))
        log.debug("read(): constructing with suffix = '{}', friend tree = '{}'".format(suffix, friendTreeName))

        sorted_input_files = sorted(list(input_files))
    
        # Construct a combined set of tree and filenames. The sorting is performed to ensure every time we build the same chain.
        # The set is needed as, although the _combinations_ in input_files are by construction unique, it could be that the same file or chain is
        # used multiple times!
        treenames = "_".join(sorted("{}{}".format(x, suffix) for x in set(i.treename for i in input_files)))
        filenames = "_".join(sorted(x for x in set(i.filename for i in input_files)))

        chainID = "{0}_{1}".format(treenames, filenames)
        log.debug("read(): looking for chain ID {}".format(chainID))

        if not self.currentChainName == '' and chainID != self.currentChainName:
            log.debug("read(): desired ID does not exist; deleting chain {0} (chainID asked = {1})".format(self.currentChainName, chainID))

            # this deletion is necessary for the garbage collector to kick in. The overhead of building a new chain is minimal.
            # Do NOT try it without deleting the chains -- it will leak.
            #self.configMgr.chains[self.currentChainName].Reset()
            if self.currentChainName in self.configMgr.chains:

                if self.currentChainName in self.configMgr.friend_chains:
                    log.verbose("Deleting friend chain {}".format(self.currentChainName))
                    self.configMgr.friend_chains[self.currentChainName].Reset()
                    del self.configMgr.friend_chains[self.currentChainName]

                self.configMgr.chains[self.currentChainName].Reset()
                del self.configMgr.chains[self.currentChainName]
                
        self.currentChainName = chainID
        
        ## MB : no need to recreate chain if it already exists
        if chainID in self.configMgr.chains:
            log.debug("Chain {} already exists - not rebuilding".format(chainID))
            return
        
        # ROOT has a nasty problem in combining TChains and friends, in that indices in a chain are not automatically built. 
        # You can easily test this in a simple .C macro to confirm.
        # What we do is the following.
        # - For each tree, create a TChain with _just_ _that_ tree
        # - Then, create a combined TChain of those TChains
        # - Add _all_ the friends to that. Otherwise, Project() calls give 0 magically.

        log.debug("Creating chain {}".format(chainID))
        self.configMgr.chains[chainID] = TChain(treenames)
       
        #self.configMgr.chains[chainID].CanDeleteRefs(True)
        self.configMgr.chains[chainID].Project._creates = True
        self.configMgr.chains[chainID].Draw._creates = True
        
        log.verbose("Created chain {} @ {}".format(chainID, hex(id(self.configMgr.chains[chainID])) ))
        
        # Build a temporary chain for each file
        tmp_chains = []
        for i in sorted_input_files:
            log.debug("read(): attempting to load {} from {}".format(i.treename+suffix, i.filename))
            f = TFile.Open(i.filename)
            # Make sure f isn't a null pointer or a zombie file
            if (not f) or (f.IsZombie()):
                log.error("input file {} does not exist - cannot load {} from it".format(i.filename, i.treename+suffix))
                continue

            self.configMgr.chains[self.currentChainName].AddFile(i.filename, -1, i.treename+suffix)

            for f in i.friends:
                # TODO: check that this doesn't increase the number of open files!
                self.configMgr.chains[self.currentChainName].AddFriend(f.treename+suffix, f.filename)

        # Add any friends to the combined one 
        if friendTreeName != "":
            log.debug("Adding friend tree {} to {}".format(friendTreeName, self.currentChainName)) 
      
            #friend_tree_idx = "{}_{}".format(self.currentChainName, friendTreeName)
            friend_tree_idx = "{}_{}".format(friendTreeName, filenames)

            log.debug("Friend tree idx = {}".format(friend_tree_idx))
            
            major_idx = set()
            minor_idx = set()
            for i in sorted_input_files:
                try:
                    _file = TFile.Open(i.filename)
                    _friend = _file.Get(friendTreeName) 
                    if _friend.GetTreeIndex() != 0:
                        major_idx.add(_friend.GetTreeIndex().GetMajorName())
                        minor_idx.add(_friend.GetTreeIndex().GetMinorName())

                    _file.Close()
                except:
                    log.warning("Could not retrieve indices for friend tree {} in file {}".format(friendTreeName, i.filename))
                    pass
           
            # Check if we've got multiple indices. ROOT silently gives nonsense in such cases, so this is a hard stop.
            if len(major_idx) > 1:
                log.fatal("Found multiple major indices for your friend trees: {}. The projections are going to go wrong as the merged friend tree needs a common index".format(", ".join(s for s in major_idx)))
            
            if len(minor_idx) > 1:
                log.fatal("Found multiple minor indices for your friend trees: {}. The projections are going to go wrong as the merged friend tree needs a common index".format(", ".join(s for s in minor_idx)))
            
            # If the friend chains have any indices (e.g. for normalisation weights with run numbers),
            # we HAVE to rebuild the index. ROOT doesn't do that for us. Yay ROOT.
            friend_chain = TChain(friendTreeName)
            SetOwnership(friend_chain, False )
            friend_chain.Project._creates = True
            friend_chain.BuildIndex._creates = True
            friend_chain.Draw._creates = True

            for i in sorted_input_files:
                try:
                    log.debug("Trying to add friend {}/{}".format(i.filename, friendTreeName))
                    friend_chain.Add("{}/{}".format(i.filename, friendTreeName))
                except:
                    log.warning("Could not add friend {} - this is not necessarily bad; if we don't need the trees you're safe".format(friendTreeName))
  
            major_idx_name = ""
            minor_idx_name = ""
            if len(major_idx) == 1:
                major_idx_name = major_idx.pop()
            if len(minor_idx) == 1:
                minor_idx_name = minor_idx.pop()

            if major_idx_name == "0":
                major_idx_name = ""
            
            if minor_idx_name == "0":
                minor_idx_name = ""
            
            try:
                if major_idx_name != "" and minor_idx_name != "": 
                    log.verbose("Building index({}, {}) for friend chain".format(major_idx_name, minor_idx_name))
                    friend_chain.BuildIndex(major_idx_name, minor_idx_name)
                    pass
                elif major_idx_name != "": 
                    log.verbose("Building index({}) for friend chain".format(major_idx_name))
                    friend_chain.BuildIndex(major_idx_name)
                    pass
            except Exception as ex:
                # Catch all exceptions. Note that PyROOT doesn't do exceptions. Some users might be using rootpy however, which
                # treats a BuildIndex error as fatal
                pass

            # Make sure the tree index is owned; keep the friend chain in a list for deletions
            SetOwnership(friend_chain.GetTreeIndex() , False )
            self.configMgr.chains[self.currentChainName].AddFriend(friend_chain)
            self.configMgr.friend_chains[self.currentChainName] = friend_chain

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
        log.debug("addHisto(): attempting to find {}".format(name))
        if self.useCache:
            log.debug("addHisto(): will use cache for {}".format(name))
            return self.__addHistoFromCache(name, nBins, binLow, binHigh, useOverflow, useUnderflow, forceNoFallback)
   
        log.debug("addHisto(): will use tree for {}".format(name))
        return self.__addHistoFromTree(name, nBins, binLow, binHigh, nBinsY, binLowY, binHighY, useOverflow, useUnderflow)

    def __addHistoFromTree(self, name, nBins=0, binLow=0., binHigh=0., nBinsY=0, binLowY=0., binHighY=0., useOverflow=False, useUnderflow=False):
        """
        Use the TTree::Project method to create the histograms for var from cuts and weights defined in instance
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

        log.debug("__addHistoFromTree: attempting to load {}".format(name))

        if self.var == "cuts":
            if self.configMgr.hists[name] is None:
                self.configMgr.hists[name] = TH1F(name, name, len(self.channel.regions), self.channel.binLow, float(len(self.channel.regions))+self.channel.binLow)
                for (iReg,reg) in enumerate(self.channel.regions):
                    log.debug("__addHistoFromTree: loading %s in region %s" % (name, reg))
                    
                    #self.cuts = self.configMgr.cutsDict[reg] # wtf is this doing here? -- GJ 24/5/17.
                    # NOTE: Changed configManager.py for it to behave the same as the binned version 
                    
                    tempName = "%stemp%s" % (name, str(iReg))
                    tempHist = TH1F(tempName, tempName, 1, 0.5, 1.5)

                    log.debug("__addHistoFromTree: current chain name {}".format(self.currentChainName))
                    log.debug("__addHistoFromTree: projecting into {}".format(tempName))
                    log.verbose("__addHistoFromTree: cuts: {}".format(self.cuts))
                    log.verbose("__addHistoFromTree: weights: {}".format(self.weights))
                    log.debug('__addHistoFromTree: {}->Project("{}", "{}", "{}")'.format(self.currentChainName, tempName, self.cuts, self.weights) )

                    self.configMgr.chains[self.currentChainName].Project(tempName, self.cuts, self.weights)
                    
                    error = ROOT.Double()
                    integral = tempHist.IntegralAndError(1, tempHist.GetNbinsX(), error)
                    self.configMgr.hists[name].SetBinContent(iReg+1, integral)
                    self.configMgr.hists[name].SetBinError(iReg+1, error)
                    self.configMgr.hists[name].GetXaxis().SetBinLabel(iReg+1, reg)
                  
                    del tempHist
                    del error
                    #tempHist.Delete()

                    for iBin in xrange(1, self.configMgr.hists[name].GetNbinsX()+1):
                        binVal = self.configMgr.hists[name].GetBinContent(iBin)
                        binErr = self.configMgr.hists[name].GetBinError(iBin)
                        if binVal < 0.0:
                            self.configMgr.hists[name].SetBinContent(iBin, 0.0)

        else:
            if self.configMgr.hists[name] is None:
                log.verbose("Constructing binned histogram for {}".format(name))
                #if self.var.find(":") == -1:
                    #self.configMgr.hists[name] = TH1F(name, name, self.channel.nBins, self.channel.binLow, self.channel.binHigh)
                #else:
                    #self.configMgr.hists[name] = TH2F(name, name, self.channel.nBins, self.channel.binLow, self.channel.binHigh, self.channelnBinsY, self.channel.binLowY, self.channel.binHighY)
                
                for (iReg,reg) in enumerate(self.channel.regions):
                    tempName = "%stemp%s" % (name, str(iReg))
                    #self.cuts = self.configMgr.cutsDict[reg]
                    
                    if self.var.find(":") == -1:
                        tempHist = TH1F(tempName, tempName, self.channel.nBins, self.channel.binLow, self.channel.binHigh)
                    else:
                        tempHist = TH2F(tempName, tempName, self.channel.nBins, self.channel.binLow, self.channel.binHigh, 
                                                            self.channelnBinsY, self.channel.binLowY, self.channel.binHighY)
                    
                    log.debug("__addHistoFromTree: projecting binned {} into {}".format(self.var, tempName))
                    log.debug("__addHistoFromTree: chain: {} ({})".format(self.currentChainName, hex(id(self.configMgr.chains[self.currentChainName])) ))
                    log.verbose("__addHistoFromTree: cuts: {}".format(self.cuts))
                    log.verbose("__addHistoFromTree: weights: {}".format(self.weights))
                    log.debug('__addHistoFromTree: {}->Project("{}", "{}", "{} * ({})" )'.format(self.currentChainName, tempName, self.var, self.cuts, self.weights) )
                    
                    nCuts = self.configMgr.chains[self.currentChainName].Project(tempName, self.var, self.weights+" * ("+self.cuts+")")
                    self.configMgr.hists[name] = tempHist.Clone()
                    self.configMgr.hists[name].SetName(name)
                    self.configMgr.hists[name].SetName(name)
                   
                    del tempHist

                    #tempHist.Delete()

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
        
        log.verbose("Loaded histogram {} with integral {}".format(self.configMgr.hists[name], self.configMgr.hists[name].Integral()))
        return self.configMgr.hists[name]


    def __addHistoFromCacheWithoutFallback(self, name, nBins=None, binLow=None, binHigh=None, useOverflow=False, useUnderflow=False):
        """ simple helper to prevent specifying all the defaults """
        return self.__addHistoFromCache(name, nBins, binLow, binHigh, useOverflow, useUnderflow, True, True)


    def __addHistoFromCache(self, name, nBins=None, binLow=None, binHigh=None, useOverflow=False, useUnderflow=False, forceNoFallback=False, forceReturn=False):
        """
        Add this histogram to the dictionary of histograms.
        """
        # NOTE: useOverflow and useUnderflow has no effect. It's there just for symmetry with TreePrepare above.
        
        if self.configMgr.hists[name] is None:
            log.debug("Attempting to load {}".format(name))
            try:
                self.configMgr.hists[name] = self.cache2File.Get(name)
                testsum = self.configMgr.hists[name].GetSum()
            except: # IOError:
                log.verbose("Could not get histogram <%s> from backupCacheFile '%s', trying cacheFile '%s'" % (name, self.cache2FileName, self.cacheFileName))
                try:
                    self.configMgr.hists[name] = self.cacheFile.Get(name)
                    testsum = self.configMgr.hists[name].GetSum()
                except: # IOError:
                    if forceNoFallback or not self.useCacheToTreeFallback:
                        self.configMgr.hists[name] = None
                        if forceReturn: # used for QCD histograms
                            log.warning("Could not find histogram <"+name+"> in "+self.cacheFileName+" ! Force return.")
                            return None
                        
                        log.debug("__addHistoFromCache(): forceNoFallback=%s useCacheToTreeFallback=%s for %s" % (forceNoFallback, self.useCacheToTreeFallback, name))
                        log.warning("Could not find histogram <"+name+"> in "+self.cacheFileName+" ! ")
                        return None
                        #raise #Exception("Could not find histogram <"+name+"> in "+self.cacheFileName)
                    else:
                        log.debug("Could not find histogram <"+name+"> in "+self.cacheFileName+", trying from tree ")

                        self.configMgr.hists[name] = None
                        return self.__addHistoFromTree(name, nBins, binLow, binHigh, nBins, binLow, binHigh, useOverflow, useUnderflow)

        if not (self.configMgr.hists[name] is None):
            log.debug("Loaded histogram {} from cache with integral {}".format(name, self.configMgr.hists[name].Integral()))

            # this is a ugly hack for now, to add an exception for 'Norm' histograms that originate from a channel with multiple bins   
            if 'Norm' in self.configMgr.hists[name].GetTitle():
                if (int(self.configMgr.hists[name].GetNbinsX()) == 1 and \
                    self.configMgr.hists[name].GetBinLowEdge(1) == 0.5 and \
                    self.configMgr.hists[name].GetXaxis().GetBinUpEdge(self.configMgr.hists[name].GetNbinsX()) == 1.5): 
                        log.debug("This is ugly: Stupid hack to evade check of histogram binning for 'Norm' histograms")
                        self.name = name
                        return self.configMgr.hists[name]

            # Check if histogram has equidistant bins
            if self.configMgr.rebin:
                log.info("addHistoFromCache: histogram {} will be mapped to a proxy equidistant histogram.".format(self.configMgr.hists[name].GetName()))
                self.mapIntoEquidistant(name)
                # No further checks are needed at this point
                self.name = name
                return self.configMgr.hists[name]
            
            # Define a function to check for almost-equality between floats
            desired_binSize = float(self.channel.binHigh - self.channel.binLow) / self.channel.nBins
            isClose = lambda x, y: abs(x - y) < desired_binSize/1e6
            
            if not (round(self.channel.nBins) == round(self.configMgr.hists[name].GetNbinsX())) or \
               ( not isClose(self.channel.binLow, self.configMgr.hists[name].GetBinLowEdge(1)) ) or \
               ( not isClose(self.channel.binHigh, self.configMgr.hists[name].GetXaxis().GetBinUpEdge(self.configMgr.hists[name].GetNbinsX()))):
                
                # Check if we can rebin the cached histogram to get the requested histogram
                log.error("addHistoFromCache: required binning %d,%f,%f, while found histogram has %d,%f,%f" % ( self.channel.nBins, self.channel.binLow, self.channel.binHigh, self.configMgr.hists[name].GetNbinsX(), self.configMgr.hists[name].GetBinLowEdge(1), self.configMgr.hists[name].GetXaxis().GetBinUpEdge(self.configMgr.hists[name].GetNbinsX()) ))

                log.debug("Checking if found histogram can be rebinned to get the requested histogram.")
                log.debug("Found histogram has the required lower limit? %s!" % isClose(self.channel.binLow, self.configMgr.hists[name].GetBinLowEdge(1)))
                log.debug("Found histogram has the required upper limit? %s!" % isClose(self.channel.binHigh, self.configMgr.hists[name].GetXaxis().GetBinUpEdge(self.configMgr.hists[name].GetNbinsX())))
                
                if isClose(self.channel.binLow, self.configMgr.hists[name].GetBinLowEdge(1)) and isClose(self.channel.binHigh, self.configMgr.hists[name].GetXaxis().GetBinUpEdge(self.configMgr.hists[name].GetNbinsX())):
                
                    log.debug("Found histogram has a multiple of the required number of bins? %s!" % round(self.configMgr.hists[name].GetNbinsX()) % round(self.channel.nBins) == 0)
                    
                    if round(self.configMgr.hists[name].GetNbinsX()) % round(self.channel.nBins) == 0:
                        # this should be rebinnable!
                        ngroup = self.configMgr.hists[name].GetNbinsX() / self.channel.nBins
                        log.warning("Original has a multiple of desired number of bins. Attempting solution of rebinning input histogram with ngroup={}".format(ngroup))
                        self.configMgr.hists[name].Rebin(ngroup)
                        return self.configMgr.hists[name]   
                        
                log.debug("Found histogram is NOT rebinnable.")

                # Check if the found binning is a subset of the binning that's desired
                # Since HistFactory only eats uniformly binned histograms, this always works.
                log.debug("Checking if required binning is a subset of the found binning.")
                desired_binning = [float(self.channel.binLow + i*desired_binSize) for i in range(0, self.channel.nBins+1)]
                found_binning = [float(x) for x in getBinEdges(self.configMgr.hists[name], 0)]

                log.debug("Found histogram has more bins than requested? %s!" % (len(set(desired_binning)) < len(set(found_binning))))
                if len(set(desired_binning)) < len(set(found_binning)):
                    log.warning("Original is wider than the desired histogram. Attempting to load appropriate bin content.")

                    # What are the bin indices of the bins we need?
                    needs_bins = [i for i, x in enumerate(pairwise(found_binning)) for y in pairwise(desired_binning) if isClose(x[0],y[0]) and isClose(x[1],y[1])]
                    log.debug("Indices of needed bins from original histogram: %s" % needs_bins)

                    temp = TH1F("h_temp", "h_temp", self.channel.nBins, self.channel.binLow, self.channel.binHigh)

                    log.verbose("Loading bin content from {}".format(name))
                    for i, x in enumerate(needs_bins):
                        #print i+1, x+1, self.configMgr.hists[name].GetBinContent(x+1)
                        temp.SetBinContent(i+1, self.configMgr.hists[name].GetBinContent(x+1)) 
                        temp.SetBinError(i+1, self.configMgr.hists[name].GetBinError(x+1)) 

                    temp_name = self.configMgr.hists[name].GetName()
                    temp_title = self.configMgr.hists[name].GetTitle()

                    log.verbose("Deleting original histogram from memory")
                    del self.configMgr.hists[name]

                    log.verbose("Moving temporary to {}".format(name))
                    self.configMgr.hists[name] = temp
                    self.configMgr.hists[name].SetName(temp_name)
                    self.configMgr.hists[name].SetTitle(temp_title)
                        
                    return self.configMgr.hists[name]
                
                self.configMgr.hists[name] = None
                
                log.debug("Required binning is NOT a subset of the found binning.")
                
                if forceNoFallback or not self.useCacheToTreeFallback:
                    if forceReturn: # used for QCD histograms
                        log.info("Could not find histogram <"+name+"> in "+self.cacheFileName+" ! Force return.")
                        return None
                    log.debug("__addHistoFromCache(): forceNoFallback=%s useCacheToTreeFallback=%s" % (forceNoFallback, self.useCacheToTreeFallback))
                    log.error("Could not find histogram <"+name+"> in "+self.cacheFileName+" ! ")
                    log.error("Requested nBins: {} / found: {}".format(int(self.channel.nBins), int(self.configMgr.hists[name].GetNbinsX())))
                    log.error("Requested low: {} / found: {}".format(self.channel.binLow, self.configMgr.hists[name].GetBinLowEdge(1)))
                    log.error("Requested up: {} / found: {}".format(self.channel.binHigh, self.configMgr.hists[name].GetXaxis().GetBinUpEdge(self.configMgr.hists[name].GetNbinsX())))
                    
                    self.configMgr.hists[name] = None
                    raise Exception("Could not find histogram <"+name+"> in "+self.cacheFileName+" with correct binning")
                else:
                    log.error("Histogram has different binning <"+name+"> in "+self.cacheFileName+", trying from tree ")
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
        h.SetCanExtend(False) #to avoid axis extension when overflow bin is set 
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

    def mapIntoEquidistant(self, name):
        """
        Remap histogram into a proxy equidistant histogram.
        WARNING: will also change self.channel.binLow/High accordingly.

        @param name the histogram
        """
        h = self.configMgr.hists[name]
        nx = h.GetNbinsX()
        currentBinEdges = []
        htemp = TH1F(h.GetName()+"TempNameForRemapping",h.GetName()+"TempNameForRemapping",h.GetNbinsX(),0,h.GetNbinsX())
        for i in range(1,nx+1):
            currentBinEdges += [h.GetBinLowEdge(i)]
            htemp.SetBinContent(i,h.GetBinContent(i))
            htemp.SetBinError(i,h.GetBinError(i))
        currentBinEdges += [h.GetBinLowEdge(nx)+h.GetBinWidth(nx)]
        h = htemp
        h.SetTitle(h.GetTitle().replace("TempNameForRemapping",""))
        h.SetName(h.GetName().replace("TempNameForRemapping",""))
        self.configMgr.hists[name] = h
        # need to shuffle the name, because cxx code uses a different order
        regName = self.channel.regionString + "_" + self.channel.niceVarName
        # save bins only once per channel
        if not self.configMgr.cppMgr.getRebinMapBool(regName):
            # save bin edges for later checks
            self.regBins[regName] = currentBinEdges
            for edge in currentBinEdges:
                self.configMgr.cppMgr.rebinMapPushBack(regName,edge)
        # check whether bin edges are consistent within one channel
        elif not currentBinEdges==self.regBins[regName]:
            log.error("histogram {} does not match previously mapped bins from region {}".format(h.GetName(), regName))
            raise Exception("Array {} does not match {}".format(currentBinEdges, self.regBins[regName]))
        self.channel.binLow = 0
        self.channel.binHigh = nx

