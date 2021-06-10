"""
 **********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : Channel                                                               *
 * Created: November 2012                                                         *
 *                                                                                *
 * Description:                                                                   *
 *      Class to define a channel                                                 *
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
from sample import Sample
from logger import Logger
from inputTree import InputTree

import generateToys
import os 

TH1.SetDefaultSumw2(True)

from copy import deepcopy
from configManager import configMgr

from configManager import replaceSymbols

log = Logger('Channel')

class Channel:
    """
    Defines the content of a channel (=region)
    """

    def __init__(self, variableName, regions, prefix, nBins,
                binLow, binHigh, statErrorThreshold=None, hasB=False):
        """
        Store configuration,  set unique channel name from variable,
        define cut region,  binning and open file

        @param variableName The name of the variable to bin in
        @param regions All regions used in the channel
        @param prefix A prefix for XML files for the channel
        @param nBins The number of bins to use
        @param binLow Lower edge of the first bin
        @param binHigh Upper edge of the last bin
        @param statErrorThreshold Threshold for statistical errors
        """

        regions.sort()
        self.regionString = "".join(regions)
        self.variableName = variableName
        self.niceVarName = replaceSymbols(variableName)
        self.name = self.niceVarName + "_" + self.regionString
        self.channelName = self.regionString + "_" + self.niceVarName
        self.ConstructorInit(prefix)  # shared method with Clone or deepcopy
        self.regions = regions
        self.nBins = nBins
        self.binHigh = binHigh
        self.binLow = binLow
        self.sampleList = []
        self.samplesToMerge = []
        self.dataList = []
        self.weights = []
        self.systDict = {}
        self.infoDict = {}
        self.hasBQCD = False
        self.useOverflowBin = False
        self.useUnderflowBin = False
        self.hasStatConfig = False
        self.hasDiscovery = False
        if statErrorThreshold is not None:
            self.hasStatConfig = True
            self.statErrorThreshold = statErrorThreshold
            self.statErrorType = "Gaussian" #"Gaussian" "Poisson"
        self.input_files = set()
        #self.treeName = ''
        self.parentTopLvl = None
        #  Plot cosmetics
        self.minY = None
        self.maxY = None
        self.title = None
        self.titleX = None
        self.titleY = None
        self.logY = None
        self.ATLASLabelX = None
        self.ATLASLabelY = None
        self.ATLASLabelText = None
        self.showLumi = None
        self.lumi = None
        self.lumiX = None
        self.lumiY = None
        self.xErrorSize = None
        self.integerStyle = None
        self.regionLabelX = None
        self.regionLabelY = None
        self.regionLabelText = None
        self.arrowX = None
        self.arrowY = None
        self.arrowEnd = None
        self.arrowAngle = None
        self.arrowWidth = None
        self.arrowColor = None
        self.arrowRatio = None
        self.remapSystChanName = ""
        self.blind = False
        self.text1 = ''
        self.text2 = ''
        self.textsize1 = 0.03
        self.textsize2 = 0.03
        self.ignoreAdditionalCuts = False # ignore any sample-specific cuts in this region


        log.debug(f"Defining new channel '{self.name}'")
        return

    def initialize(self):
        """ Initialize the channel """
        for sample in self.sampleList:
            pass
            # if not sample.isData and not sample.isQCD and not sample.isDiscovery:
            #     for (systName, syst) in self.systDict.items():
            #         try:
            #             sample.getSystematic(systName)
            #         except:
            #             sample.addSystematic(syst)

    def Clone(self, prefix=""):
        """ 
        Clone into a new object

        @param prefix Optional new prefix for the copied channel 
        """

        if prefix == "":
            prefix = self.prefix
        # copies all properties prior to initialize
        newChan = deepcopy(self)
        newChan.ConstructorInit(prefix)
        return newChan

    def ConstructorInit(self, prefix):
        """
        Initialize prefix settings
        
        @param prefix The prefix to use
        """

        self.prefix = prefix
        self.xmlFileName = "config/" + self.prefix + "_" + self.channelName + ".xml"
        
        return

    def addSample(self, sample, index=-1):
        """
        Add Sample object to this channel

        @param sample The sample to add
        @param index The index to use; if -1, append at the end
        """
        if index == -1:
            # don't overwrite the last element but append it
            index = len(self.sampleList) 

        log.verbose(f"addSample: adding sample {sample.name} to channel {self.name}")

        self.sampleList.insert(index, sample.Clone())
        self.sampleList[index].parentChannel = self

        # Add any input files we own to the channel
        log.debug(f"Appending existing {len(self.input_files)} files for channel {self.channelName} to sample {sample.name}")
        for i in self.input_files:
            sample.addInput(i.filename, i.treename)

        if sample.isData or sample.isDiscovery or sample.isQCD:
            return

        if len(self.sampleList[index].weights) == 0:
            self.sampleList[index].weights = deepcopy(self.weights)

        for (systName, syst) in list(self.systDict.items()):
            if not systName in list(self.sampleList[index].systDict.keys()):
                self.sampleList[index].addSystematic(syst)
        return


    def getSample(self, name):
        """
        Get Sample object for this channel

        @param name The name to sample to return
        """
        for s in self.sampleList:
            if s.name == name:
                return s

        raise Exception("Could not find sample with name %s in %s"
                        % (name, [s.name for s in self.sampleList]))

    def hasSample(self, name):
        """
        Check if sample exists for this channel

        @param name The name of the sample to check
        """
        for s in self.sampleList:
            if s.name == name:
                return True

        return False
    
    def removeSample(self, sample):
        """
        Remove a sample from the channel

        @param sample The sample to remove; can be either a sample object or a name
        """

        if isinstance(sample, Sample):
            aSam = sample
        elif isinstance(sample,str):
            aSam = self.getSample(sample)
        else:
            raise ValueError("Channel: sample type %s not supported" % (type(sample)))
        
        try:
            self.sampleList.remove(aSam)
        except:
            log.warning(f"unable to remove sample {aSam.name} from channel {self.name}")
        
        return

    def addInputsToSamples(self, filename):
        # add inputs to the samples, not to ourselves
        for sample in self.sampleList:
            sample.addInput(filename)

    def addInput(self, filename, treename):
        # add an input with a treename
        self.input_files.add(InputTree(filename, treename))
       
        for sample in self.sampleList:
            sample.addInput(filename, treename)

    def addInputs(self, filenames, treename):
        # bulk add a bunch of filenames with the same treename
        for f in filenames:
            self.addInput(f, treename)

    #def setFileList(self, input_files):
        #"""
        #Set file list for this Channel.
        #This will be used as default for samples that don't specify
        #their own file list.

        #@param filelist The list to set
        #"""
        #self.input_files = input_files

    #def setFile(self, file):
        #"""
        #Set file for this Sample directly
        #This will be used as default for samples that don't specify
        #their own file list.

        #@param file The file to set as filelist.
        #"""
        #self.input_files = [file]

    #def propagateInputFiles(self, input_files):
        #"""
        #Propagate our file list downwards to all owned samples. Only sets own file list if not previously given.
        #"""
        ## if we don't have our own file list,  use the one given to us
        #if not self.input_files:
            #self.input_files = input_files
        
        ## propagate our file list downwards
        #for sam in self.sampleList:
            #sam.propagateInputFiles(self.input_files)

    def setWeights(self, weights):
        """
        Set the weights for this channel - overrides previous weights

        Propagate to owned samples
        
        @param weights A list of weights
        """
        self.weights = deepcopy(weights)

        for s in self.sampleList:
            if not s.isData and not s.isQCD and not s.isDiscovery:
                s.setWeights(weights)

        return

    def addWeight(self, weight):
        """
        Add a single weight and propagate

        @param weight Weight to append to the current list of weights
        """
        if not weight in self.weights:
            self.weights.append(weight)
        else:
            raise RuntimeError("Weight %s already defined in channel %s"
                               % (weight, self.name))

        for s in self.sampleList:
            if not s.isData and not s.isQCD and not s.isDiscovery:
                if not weight in s.weights:
                    s.addWeight(weight)

        for syst in list(self.systDict.values()):
            if syst.type == "weight":
                if not weight in syst.high:
                    syst.high.append(weight)
                if not weight in syst.low:
                    syst.low.append(weight)
        return

    def removeWeight(self, weight):
        """
        Remove a single weight and propagate: also remove from all samples

        @param weight Weight to remove
        """
        if weight in self.weights:
            self.weights.remove(weight)

        for s in self.sampleList:
            if not s.isData and not s.isQCD and not s.isDiscovery:
                if weight in s.weights:
                    s.removeWeight(weight)

        for syst in list(self.systDict.values()):
            if syst.type == "weight":
                if weight in syst.high:
                    syst.high.remove(weight)
                if weight in syst.low:
                    syst.low.remove(weight)
        return

    def addDiscoverySamples(self, srList, startValList, minValList,
                            maxValList, colorList):
        """
        Add a sample to be used for discovery fits

        @param srList List of signal regions to use
        @param startValList List of starting values for each of the signal regions
        @param minValList List of minimal values of the parameter used for each of the signal regions
        @param maxValList List of maximal values of the parameter used for each of the signal regions
        @param colorList List of colors to use when plotting each of the signal regions
        """
        self.hasDiscovery = True
        self.parentTopLvl.hasDiscovery = True

        if not self.variableName == "cuts":
            raise TypeError("Discovery sample can only be added "
                            "to a cuts channel")

        for (iSR, sr) in enumerate(srList):
            sigSample = Sample("DiscoveryMode_%s" % sr, colorList[iSR])
            sigSample.setNormFactor("mu_%s" % sr, startValList[iSR],
                                    minValList[iSR], maxValList[iSR])
            sigSample.setDiscovery()
            sigSample.clearSystematics()

            self.addSample(sigSample)
            self.parentTopLvl.setSignalSample(sigSample)

            histoName = f"h{sigSample.name}Nom_{sr}_obs_{self.niceVarName}"
            self.getSample("DiscoveryMode_%s" % sr).setHistoName(histoName)

            configMgr.hists[histoName] = TH1F(histoName, histoName,
                                              len(srList), 0.5,
                                              float(len(srList))+0.5)
            configMgr.hists[histoName].SetBinContent(iSR+1, startValList[iSR])

        return

    def addData(self, dataName):
        """
        Add a prepared data histogram to this channel

        @param dataName The histogram to add
        """
        if len(self.dataList):
            raise IndexError("Channel already has data " + str(self.dataList))
        self.dataList.append((configMgr.histCacheFile, dataName, ""))

    def addPseudoData(self, toyInputHistoList, varName, varLow, varHigh,
                      addInputHistoList, histoPath="", seed=None):
        """
        Add a pseudo data distribution to this channel
        !!! DEPRECATED, MAY NOT WORK !!!

        @deprecated MAY NOT WORK
        """
        if len(self.dataList):
            raise IndexError("Channel already has data " + str(self.dataList))
        histo = generateToys.generate(toyInputHistoList, varName,
                                      varLow, varHigh)
        for iBin in range(histo.GetNbinsX() + 1):
            for inputHisto in addInputHistoList:
                histo.SetBinContent(iBin+1, TMath.Nint(histo.GetBinContent(iBin+1)) + TMath.Nint(inputHisto.GetBinContent(iBin+1)))
        for iBin in range(histo.GetNbinsX() + 1):
            histo.SetBinError(iBin+1, TMath.Sqrt(histo.GetBinContent(iBin+1)))

        self.dataList.append((configMgr.histCacheFile, histo.GetName(), ""))
        return

    def addSystematic(self, syst):
        """
        Add a systematic to this channel.
        This will be propagated to all owned samples; exisiting systematics are not overwritten.

        @param syst The systematic to add
        """
        log.debug(f"Adding systematic '{syst.name}' to channel '{self.name}'")
        if syst.name in list(self.systDict.keys()):
            raise Exception("Attempt to overwrite systematic %s "
                            " in Channel %s" % (syst.name, self.name))
        else:
            self.systDict[syst.name] = syst.Clone()
            for sam in self.sampleList:
                log.debug(f"Adding systematic '{syst.name}' to sample '{sam.name}'")
                sam.addSystematic(syst)
            return

    def getSystematic(self, systName):
        """
        Find the systematic with the given name

        @param systName The name of the systematic to find
        """
        try:
            return self.systDict[systName]
        except KeyError:
            raise KeyError("Could not find systematic %s "
                           "in channel %s" % (systName, self.name))

    #def setTreeName(self, treeName):
        #"""
        #Set the input tree name

        #@param treeName The name to set
        #"""

        #self.treeName = treeName
        #return

    #def propagateTreeName(self, treeName):
        #"""
        #Propagate the name of the tree down to any samples; also sets our own treename
        
        #@param treeName The name to set
        #"""
        
        #if self.treeName == '':
            #self.treeName = treeName
        ###  MAB : Propagate down to samples
        #for sam in self.sampleList:
            #sam.propagateTreeName(self.treeName)
            #pass
        #return

    def isBlinded(self, fitConfig):
        if self.blind or \
           (configMgr.blindSR and (self.channelName in fitConfig.signalChannels)) or \
           (configMgr.blindCR and self.channelName in fitConfig.bkgConstrainChannels) or \
           (configMgr.blindVR and (self.channelName in fitConfig.validationChannels)):
            return True

        return False

    def createHistFactoryObject(self):
        """
        Create a HistFactory object for this Channel
        """

        c = ROOT.RooStats.HistFactory.Channel( self.channelName, configMgr.histCacheFile )
        for d in self.dataList:
            #d should be array of form [inputFile, histoName, histoPath]
            
            histoPath = "" #paths never start with /
            if len(d[2]) > 0:
                histoPath = d[2]
            c.SetData(d[1], d[0], histoPath)

        if self.hasStatConfig:
           c.SetStatErrorConfig(self.statErrorThreshold, self.statErrorType)
        
        for (iSample, sample) in enumerate(self.sampleList):
            if not sample.write:
                continue

            s = sample.createHistFactoryObject()
            c.AddSample(s)

        return c
    
    def __str__(self):
        """
        Convert instance to XML string
        """
        self.writeString = "<!DOCTYPE Channel SYSTEM '"+os.getenv('HISTFITTER')+"/config/HistFactorySchema.dtd'>\n\n"
        self.writeString += "<Channel Name=\"%s\">\n\n" % self.channelName
        for data in self.dataList:
            if len(data[2]):
                self.writeString += f"  <Data HistoName=\"{data[1]}\" InputFile=\"{data[0]}\" HistoPath=\"{data[2]}\" />\n\n"
            else:
                self.writeString += f"  <Data HistoName=\"{data[1]}\" InputFile=\"{data[0]}\" />\n\n"
        if self.hasStatConfig:
            self.writeString += f"  <StatErrorConfig RelErrorThreshold=\"{self.statErrorThreshold:g}\" ConstraintType=\"{self.statErrorType}\"/>\n\n"
        for (iSample, sample) in enumerate(self.sampleList):
            if sample.write:
                self.writeString += str(sample)
        self.writeString += "</Channel>\n"
        return self.writeString

    def writeXML(self):
        """
        Write and close file
        """
        log.info("Writing file: '%s'" % self.xmlFileName)
        self.xmlFile = open(self.xmlFileName, "w")
        self.xmlFile.write(str(self))
        self.xmlFile.close()
        return

    def compareChannelFormat(self, remapChan):
        """
        Compare the format of this channel to another one

        @param remapChan The Channel to compare to
        """

        if self.nBins != remapChan.nBins:
            log.warning(f"Cannot remap histoSys systematics from {remapChan.name} to channel {self.name} as number of bins do not agree: {float(self.nBins):g} versus {float(remapChan.nBins):g}")
            return False

        if abs(self.binLow - remapChan.binLow) > 0.0001:
            log.warning(f"Cannot remap histoSys systematics from {remapChan.name} to channel {self.name} as number of bins do not agree: {float(self.binLow):g} versus {float(remapChan.binLow):g}")
            return False

        if abs(self.binHigh - remapChan.binHigh) > 0.0001:
            log.warning(f"Cannot remap histoSys systematics from {remapChan.name} to channel {self.name} as number of bins do not agree: {float(self.binHigh):g} versus {float(remapChan.binHigh):g}")
            return False

        return True

    @property
    def doBlindingOverwrite(self):
        """ 
        Backwards compatible function for self.blind"
        """
        log.warning("channel.doBlindingOverwrite deprecated in favour of channel.blind")
        return self.blind

    @doBlindingOverwrite.setter
    def doBlindingOverwrite(self, value):
        log.warning("channel.doBlindingOverwrite deprecated in favour of channel.blind")
        self.blind = value
