"""
 **********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : Systematic                                                            *
 * Created: November 2012                                                         *
 *                                                                                *
 * Description:                                                                   *
 *      Class to define a systematic                                              *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************
"""

from ROOT import THStack,TLegend,TCanvas,TFile,TH1D
from ROOT import ConfigMgr,FitConfig  #from gSystem.Load("libSusyFitter.so")
from histogramsManager import histMgr
from copy import deepcopy
from logger import Logger
from ROOT import gROOT

from configManager import replaceSymbols

log = Logger('Systematic')

###############################################
# Systematic is a function which returns an object. This object can be a
# TreeWeightSystematic or a UserSystematic. These classes are derived classes
# and the Baseclass for both of them is the SystematicBase. In
# TreeWeightSystematic the set of the weights differs for the systematic type
# tree and weight. Therefore, the functions PrepareWAHforWeight
# or PrepareWAHforTree exist. All three types of systematics share the
# "FillUpDownHist" (for the methods "userNormHistoSys" or "normHistoSys") and
# "tryAddHistos" function in the Baseclass SystematicBase.
###############################################

class SystematicBase:
    def __init__(self, name="", nominal=None, high=None, low=None,
                 type="", method="", constraint="Gaussian"):
        self.name = name  # Name to give the systematic
        self.type = type  # Is the systematic weights based or tree based?
        self.method = method  # What HistFactory method to use?
        self.nominal = nominal  # What's the nominal tree name or weights list?
        self.high = high  # What is the +1sig tree name or weights list?
        self.low = low  # What is the -1sig tree name or weights list?
        self.sampleList = []
        self.merged = False
        self.nFound = 0
        self.filesHi = {}
        self.filesLo = {}
        self.treeLoName = {}
        self.treeHiName = {}
        self.allowRemapOfSyst = False
        self.differentNominalTreeWeight = False

        if not constraint == "Gaussian" and not (method == "shapeSys" or method == "shapeStat"):
            raise ValueError("Constraints can only be specified for shapeSys")

        self.constraint = constraint

        allowedSys = ["histoSys","overallSys","userOverallSys","overallHistoSys","normHistoSys",
                      "shapeSys","shapeStat","histoSysOneSide","histoSysOneSideSym","normHistoSysOneSide","normHistoSysOneSideSym","userHistoSys","userNormHistoSys",
                      "overallNormHistoSys","overallNormHistoSysOneSide","overallNormHistoSysOneSideSym", "overallNormSys", 
                      "normHistoSysEnvelopeSym", "histoSysEnvelopeSym", "overallNormHistoSysEnvelopeSym" ]

        if not self.method in allowedSys:
            raise Exception("Given method %s is not known; use one of %s"
                             % (self.method, allowedSys))

        log.debug(f"Defining new systematic '{self.name}' of type {self.method}")

    def Clone(self, name=""):
        """ 
        Copy the systematic

        @param name An optional new name. If empty, the current name is used
        """
        newSyst = deepcopy(self)
        if not name == "":
            newSyst.name = name
        return newSyst

    def Reset(self):
        self.nFound = 0
        return

    def mergeSamples(self, sampleList):
        if not self.method == "shapeSys":
            raise TypeError("ERROR: can only merge samples for shapeSys")
        self.merged = True
        self.sampleList = sampleList
        return

    def foundSample(self):
        self.nFound += 1
        return

    def isMerged(self):
        if self.nFound == len(self.sampleList):
            return True
        else:
            return False

    #def setFileList(self, sample, filelist):
        #"""
        #Set file list for this Systematic directly

        #@param sample The Sample to set the files for
        #@param filelist A list of filenames
        #"""
        #self.filesLo[sample] = filelist
        #self.filesHi[sample] = filelist

    #def setFile(self, sample, file):
        #"""
        #Set a file for this Systematic directly
        
        #@param sample The Sample to set the file for
        #@param filelist A filename
        #"""
        #self.filesLo[sample] = [file]
        #self.filesHi[sample] = [file]

    #def setTreeName(self, sampleName, treeName):
        #"""
        #Set name of the tree for a sample
        
        #@param sampleName Name of the sample
        #@param treeName Tree name to set for the sample
        #"""
        #self.treeLoName[sampleName] = treeName
        #self.treeHiName[sampleName] = treeName
        #return

    #def setLoTreeName(self, sampleName, treeName):
        #"""
        #Set name of the tree for a sample for -1 sigma variations only
        
        #@param sampleName Name of the sample
        #@param treeName Tree name to set for the sample
        #"""
        #self.treeLoName[sampleName] = treeName
        #return

    #def setHiTreeName(self, sampleName, treeName):
        #"""
        #Set name of the tree for a sample for +1 sigma variations only
        
        #@param sampleName Name of the sample
        #@param treeName Tree name to set for the sample
        #"""
        #self.treeHiName[sampleName] = treeName
        #return

    #def setHiFileList(self, sample, filelist):
        #"""
        #Set file list for +1 sigma variations only
        
        #@param sampleName Name of the sample
        #@param treeName Tree name to set for the sample
        #"""
        #self.filesHi[sample] = filelist
        #return

    #def setLoFileList(self, sample, filelist):
        #"""
        #Set file list for -1 sigma variations only
        
        #@param sampleName Name of the sample
        #@param treeName Tree name to set for the sample
        #"""
        #self.filesLo[sample] = filelist
        #return

    def FillUpDownHist(self, lowhigh="", regionString="", normString="",
                       normCuts="", abstract=None, topLvl=None, chan=None, sam=None):
        
        _allowed_methods = ["userNormHistoSys", 
                            "overallNormSys", "normHistoSys", 
                            "normHistoSysOneSide", "normHistoSysOneSideSym", 
                            "normHistoSysEnvelopeSym", "overallNormHistoSys", 
                            "overallNormHistoSysEnvelopeSym", "overallNormHistoSysOneSide", "overallNormHistoSysOneSideSym"]
        
        if not (self.method in _allowed_methods and (not sam.noRenormSys)):
            log.debug(f"FillUpDownHist: systematic '{self.name}' for sample '{sam.name}' not remapped - returning")
            return

        histName = "h" + sam.name + self.name + lowhigh + normString + "Norm"
        if histName in list(abstract.hists.keys()):
            log.debug(f"FillUpDownHist: systematic '{self.name}': histogram '{histName}' already exists! Not rebuilding it.")
            return

        if not sam.normRegions: 
            log.error(f"    {self.method} but no normalization regions specified for sample {sam.name}, noRenormSys={sam.noRenormSys}. This is not safe, please fix.")
            normChannels = []
            tl = sam.parentChannel.parentTopLvl
            for ch in tl.channels:
                if (ch.channelName in tl.bkgConstrainChannels) or (ch.channelName in tl.signalChannels):
                    normChannels.append((ch.regionString,ch.variableName))
                    pass
                pass
            sam.setNormRegions(normChannels)
            log.warning("            For now, using all non-validation channels by default: %s" % sam.normRegions)

        normString = ""
        for normReg in sam.normRegions:
            if not isinstance(normReg[0], list):
                c = topLvl.getChannel(normReg[1], [normReg[0]])
            else:
                c = topLvl.getChannel(normReg[1], normReg[0])
            normString += c.regionString
       
        log.debug(f"FillUpDownHist: constructed normString {normString}")

        # Attempt to read from the cache fileout without fallback
        # If it fails, set this silly boolean and still go into the block below
        # Necessary, or we end up with nominal == high == low and removed systematics.

        reread = False
        if abstract.forceNorm==False:
          if not abstract.readFromTree:
            abstract.hists[histName] = None
            abstract.prepare.addHisto(histName, forceNoFallback=True)
            if abstract.hists[histName] == None and abstract.useCacheToTreeFallback: 
                log.warning(f"Will rebuild {histName} from trees")
                reread = True
            elif abstract.hists[histName] != None:
                log.debug(f"FillUpDownHist: systematic '{self.name}': histogram '{histName}' successfully read! Not rebuilding it.")
                return 
        else:
          reread = True

        if not abstract.readFromTree and not reread:
            log.error(f"FillUpDownHist: systematic {self.name}: histogram {histName}: not reading from trees and no fallback enabled. Will not build histogram")
            return
        
        abstract.hists[histName] = TH1D(histName, histName, 1, 0.5, 1.5)

        for normReg in sam.normRegions:
            # Find the sample object associated to each of the normalisation regions
            if not isinstance(normReg[0], list):
                c = topLvl.getChannel(normReg[1], [normReg[0]])
            else:
                c = topLvl.getChannel(normReg[1], normReg[0])

            try:
                s = c.getSample(sam.name)
            except:
                # assume that if no histogram is made,
                # then it is not needed
                continue

            systNorm = s.getSystematic(self.name)

            if "High" in lowhigh:    
                log.verbose("FillUpDownHist(): in high mode")
                s.setCurrentSystematic(self, "high")
            elif "Low" in lowhigh:    
                log.verbose("FillUpDownHist(): in low mode")
                s.setCurrentSystematic(self, "low")
            elif "Nom" in lowhigh:
                log.verbose("FillUpDownHist(): in nominal mode")
                s.setCurrentSystematic(self)
           
            #print self
            #print normReg
            #print s.currentSystematic
            #print systNorm
            #print "treename ", s.treename
            #print "treename suffix ", s.getTreenameSuffix()

            # TODO: fix the use of filesLo, filesHi 

            #continue

            ## if the systematic has a dedicated file
            ## list, use it

            #if 'Low' in lowhigh:
                #if s.name in systNorm.filesLo:
                    #filelist = systNorm.filesLo[s.name]
                #else:
                    ## otherwise - take the sample file list
                    #filelist = s.files
                
                #if s.name in systNorm.treeLoName:
                    #treeName = systNorm.treeLoName[s.name]
                #else:
                    ## otherwise - take the default tree name
                    ## for the sample
                    #if self.type == "tree":
                        #treeName = s.treeName + systNorm.low
                    #else:
                        #treeName = s.treeName
                
                #if self.type == "tree" and (treeName == '' or treeName == systNorm.low):
                    ## checking if the sample tree name should have a prefix, if yes use this                                
                    #if s.prefixTreeName == '':
                        #treeName = s.name + systNorm.low
                    #else:
                        #treeName = s.prefixTreeName + systNorm.low

            #if 'High' in lowhigh:
                #if s.name in systNorm.filesHi:
                    #filelist = systNorm.filesHi[s.name]
                #else:
                    ## otherwise - take the sample file list
                    #filelist = s.files
                
                #if s.name in systNorm.treeHiName:
                    #treeName = systNorm.treeHiName[s.name]
                #else:
                    ## otherwise - take the default tree name
                    ## for the sample
                    #if self.type == "tree":
                        #treeName = s.treeName + systNorm.high
                    #else:
                        #treeName = s.treeName
                
                #if self.type == "tree" and (treeName == '' or treeName == systNorm.high):    
                    ## checking if the sample tree name should have a prefix, if yes use this
                    #if s.prefixTreeName == '':
                        #treeName = s.name + systNorm.high
                    #else:
                        #treeName = s.prefixTreeName + systNorm.high

            #if 'Nom' in lowhigh:
                #filelist = s.files
                ## take the default tree name
                ## for the sample
                #if self.type == "tree":
                    #treeName = s.treeName + systNorm.nominal
                #else:
                    #treeName = s.treeName
                
                ### possibly rename treename
                #if self.type == "tree" and (treeName == '' or treeName == systNorm.nominal):
                    ## checking if the sample tree name should have a prefix, if yes use this
                    #if s.prefixTreeName == '':
                        #treeName = s.name + systNorm.nominal
                    #else:
                        #treeName = s.prefixTreeName + systNorm.nominal                           

            ## weight-based trees assuming up/down are in one tree have identical name for up/low
            ## if our current name does not exist, we assume this one does
            
            #if self.type == "weight" and (not abstract.prepare.checkTree(treeName, filelist)):
                #if s.prefixTreeName == '':
                    #treeName = s.name + abstract.nomName
                #else:
                    #treeName = s.prefixTreeName + abstract.nomName

            log.debug(f"FillUpDownHist(): calling prepare.read() for {s.name}")
            #abstract.prepare.read(treeName, filelist)
            abstract.prepare.read(s.input_files, suffix=s.getTreenameSuffix(), friendTreeName=s.friendTreeName)

            tempHist = TH1D("temp", "temp", 1, 0.5, 1.5)

            _weights = s.weights
            if systNorm.type == "weight":
                if "High" in lowhigh:
                    _weights = s.getSystematic(systNorm.name).high
                elif "Low" in lowhigh:
                    _weights = s.getSystematic(systNorm.name).low
            
            _cut_str = abstract.cutsDict[normReg[0]]
            if s.additionalCuts != "":
                if c.ignoreAdditionalCuts:
                    log.debug(f"Ignoring additional cuts in channel {c.channelName} for sample {s.name}")
                else:
                    log.debug(f"Using additional cuts for sample {s.name}: '{s.additionalCuts}'")
                    if len(_cut_str.strip()) != 0:
                        # ROOT doesn't like "()" as a cut, so we only use the string if it's non-empty
                        _cut_str = f"(({_cut_str}) && ({s.additionalCuts}))"
                    else:
                        log.warning("No region cuts applied; only using the additional ones")
                        _cut_str = copy(s.additionalCuts)
            _weight_str = "{} * {}".format(str(abstract.lumiUnits*abstract.outputLumi/abstract.inputLumi), " * ".join(_weights))

            log.verbose(f"FillUpDownHist(): current chain {abstract.prepare.currentChainName}")
            log.verbose(f"FillUpDownHist(): normalization region {normReg[0]}")
            log.verbose(f"FillUpDownHist(): normalization region cuts {_cut_str}")
            log.verbose(f"FillUpDownHist(): weights: {_weight_str}") 
                
            currentChain = abstract.chains[abstract.prepare.currentChainName]
            try:
                currentChain.Project("temp", _cut_str, f"{_weight_str} * ({_cut_str})" )
            except:
                # if e.g. rootpy is used and this goes wrong, it's a fatal exception otherwise
                pass

            log.verbose(f"FillUpDownHist(): loaded temporary histogram for {self.name} in {normReg[0]} with integral {tempHist.GetSumOfWeights()}")

            abstract.hists[histName].SetBinContent(1, abstract.hists[histName].GetSum() + tempHist.GetSumOfWeights())
            del tempHist

        log.verbose(f"FillUpDownHist(): loaded norm histogram {histName} for {self.name} in {normString} with integral {abstract.hists[histName].GetSum()}")

        return

    def tryAddHistos(self, highorlow="", regionString="", normString="",
                     normCuts="", abstract=None, chan=None, sam=None):
        histName = f"h{sam.name}{self.name}{highorlow}{regionString}_obs_{replaceSymbols(chan.variableName)}"

        log.debug("       adding histo %s" % histName)
        try:
            abstract.prepare.addHisto(histName,
                                      useOverflow=chan.useOverflowBin,
                                      useUnderflow=chan.useUnderflowBin)
        except:
            pass


class TreeWeightSystematic(SystematicBase):

    def __init__(self, name="", nominal=None, high=None, low=None,
                 type="", method="", constraint="Gaussian"):
        SystematicBase.__init__(self, name, nominal, high, low,
                                type, method, constraint)

    def PrepareWAHforWeight(self, regionString="", normString="", normCuts="",
                            abstract=None, topLvl=None, chan=None, sam=None):
        
        log.debug(f"PrepareWAHforWeight() for {self} in {sam.name}")
        
        log.debug(f"PrepareWAHforWeight: removing systematic from {self.name} to be sure {sam.name}")
        sam.removeCurrentSystematic()

        highandlow = ["High_", "Low_"] # ,"Nom_"]
        if self.differentNominalTreeWeight:
            highandlow = ["High_", "Low_", "Nom_"]

        for highorlow in highandlow:
            
            _weights = self.nominal
            if highorlow == "High_":
                _weights = self.high
            elif highorlow == "Low_":
                _weights = self.low

            abstract.prepare.weights = "{} * {}".format(str(abstract.lumiUnits * abstract.outputLumi/abstract.inputLumi), 
                                                        " * ".join(w for w in _weights))

            if abstract.readFromTree or abstract.useCacheToTreeFallback:
                log.debug("PrepareWAHforWeight(): calling prepare.read()")
                abstract.prepare.read(sam.input_files, suffix=sam.getTreenameSuffix(), friendTreeName=sam.friendTreeName)
            
            TreeWeightSystematic.tryAddHistos(self, highorlow, regionString,
                                              normString, normCuts, abstract,
                                              chan, sam)
            
            TreeWeightSystematic.FillUpDownHist(self, highorlow, regionString,
                                                normString, normCuts, abstract,
                                                topLvl, chan, sam)
        return

    def PrepareWAHforTree(self, regionString="", normString="", normCuts="",
                          abstract=None, topLvl=None, chan=None, sam=None):
        highandlow = ["High_", "Low_"]
        if self.differentNominalTreeWeight:
            highandlow = ["High_", "Low_", "Nom_"]

        log.debug(f"PrepareWAHforTree() for {self.name}")

        weightstemp = abstract.prepare.weights
        for highorlow in highandlow:
            abstract.prepare.weights = weightstemp
            for myw in sam.weights:
                if not myw in abstract.prepare.weights:
                    abstract.prepare.weights += " * " + myw

            if abstract.readFromTree or abstract.useCacheToTreeFallback:
                log.debug(f"PrepareWAHforTree(): will read syst {self.name} from trees (or fallback enabled)")
                
                if highorlow == "High_":
                    log.verbose("PrepareWAHforTree(): in high mode")
                    sam.setCurrentSystematic(self, "high")
                elif highorlow == "Low_":
                    log.verbose("PrepareWAHforTree(): in low mode")
                    sam.setCurrentSystematic(self, "low")
                elif highorlow == "Nom_":
                    log.verbose("PrepareWAHforTree(): in nominal mode")
                    sam.setCurrentSystematic(self)
                    
                log.debug(f"PrepareWAHforTree(): calling prepare.read() for {self.name} (sample {sam.name})")
                log.verbose("PrepareWAHforTree(): using the following inputs:")
                for i in sam.input_files:
                    log.verbose(f"{i.treename}{sam.getTreenameSuffix()} from {i.filename}")

                abstract.prepare.read(sam.input_files, suffix=sam.getTreenameSuffix(), friendTreeName=sam.friendTreeName)

            TreeWeightSystematic.tryAddHistos(self, highorlow, regionString,
                                              normString, normCuts, abstract,
                                              chan, sam)
            TreeWeightSystematic.FillUpDownHist(self, highorlow, regionString,
                                                normString, normCuts, abstract,
                                                topLvl, chan, sam)
            abstract.prepare.weights = weightstemp
        return

    def PrepareWeightsAndHistos(self, regionString="", normString="",
                                normCuts="", abstract=None,
                                topLvl=None, chan=None, sam=None):

        log.verbose(f"PrepareWeightsAndHistos for {self.name}")
        if self.type == "weight":
            log.verbose(f"Calling TreeWeightSystematic.PrepareWAHforWeight() for {self.name}") 
            TreeWeightSystematic.PrepareWAHforWeight(self, regionString,
                                                     normString, normCuts,
                                                     abstract, topLvl, chan, sam)
        if self.type == "tree":
            log.verbose(f"Calling TreeWeightSystematic.PrepareWAHforTree() for {self.name}") 
            TreeWeightSystematic.PrepareWAHforTree(self, regionString,
                                                   normString, normCuts,
                                                   abstract, topLvl, chan, sam)
        return


class UserSystematic(SystematicBase):
    def __init__(self, name="", nominal=None, high=None, low=None, type="",
                 method="", constraint="Gaussian"):
        SystematicBase.__init__(self, name, nominal, high, low, type,
                                method, constraint)

    def PrepareWeightsAndHistos(self, regionString="", normString="",
                                normCuts="", abstract=None,
                                topLvl=None, chan=None, sam=None):

        nomName = f"h{sam.name}Nom_{regionString}_obs_{replaceSymbols(chan.variableName)}"
        
        for lowhigh in ["High_","Low_"]:
            lowhighName = f"h{sam.name}{self.name}{lowhigh}{regionString}_obs_{replaceSymbols(chan.variableName)}"
            if abstract.hists[lowhighName] is None:
                if lowhigh == "High_":
                    abstract.hists[lowhighName] = histMgr.buildUserHistoSysFromHist(lowhighName, self.high, abstract.hists[nomName])
                elif lowhigh == "Low_":
                    abstract.hists[lowhighName] = histMgr.buildUserHistoSysFromHist(lowhighName, self.low, abstract.hists[nomName])
        return

    def PrepareGlobalNormalization(self,normString,abstract,topLvl,chan,sam):

        for lowhigh in ["Nom_",self.name+"High_",self.name+"Low_"]:
            histName = f"h{sam.name}{lowhigh}{normString}Norm"
            if not histName in list(abstract.hists.keys()):
                if sam.normRegions:
                    
                    if not abstract.readFromTree:
                        abstract.hists[histName] = None
                        abstract.prepare.addHisto(histName)
                    else:
                        abstract.hists[histName] = TH1D(histName, histName, 1, 0.5, 1.5)
                        totNorm=0.0
                        for normReg in sam.normRegions:
                            nameTmp = "h" + sam.name + lowhigh + normReg[0] + "_obs_" + replaceSymbols(chan.variableName)
                            try:
                                totNorm += abstract.hists[nameTmp].GetSumOfWeights()
                            except:
                                log.warning("could get histogram %s for normalization" % nameTmp)
                        
                        abstract.hists[histName].SetBinContent(1,totNorm)
        return


## This is the control function. The function ensures the backward compability.
## It returns an object
def Systematic(name="", nominal=None, high=None, low=None,
               type="", method="", constraint="Gaussian"):
    types = ["weight", "tree", "user"]
    if type not in types:
        raise Exception(f"Systematic type {type} unknown for {name}")
        
    if type == "weight" or type == "tree":
        return TreeWeightSystematic(name, nominal, high, low,
                                    type, method, constraint)
    else:
        return UserSystematic(name, nominal, high, low,
                                    type, method, constraint)
