import ROOT
from ROOT import TFile, TMath, RooRandom, TH1, TH1F
from ROOT import kBlack, kWhite, kGray, kRed, kPink, kMagenta, kViolet, kBlue, kAzure, kCyan, kTeal, kGreen, kSpring, kYellow, kOrange, kDashed, kSolid, kDotted
from sample import Sample
from logger import Logger

import generateToys

TH1.SetDefaultSumw2(True)

from copy import deepcopy
from configManager import configMgr

log = Logger('Channel')

class Channel(object):
    """
    Defines the content of a channel HistFactory xml file
    """

    def __init__(self, variableName, regions, prefix, nBins,
                binLow, binHigh, statErrorThreshold=None, hasB=False):
        """
        Store configuration,  set unique channel name from variable,
        define cut region,  binning and open file
        """
        regions.sort()
        self.regionString = "".join(regions)
        self.variableName = variableName
        self.name = self.variableName.replace("/", "") + "_" + self.regionString
        self.channelName = self.regionString + "_" + variableName.replace("/", "")
        self.ConstructorInit(prefix)  # shared method with Clone or deepcopy
        self.regions = regions
        self.nBins = nBins
        self.binHigh = binHigh
        self.binLow = binLow
        self.sampleList = []
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
        self.files = []
        self.treeName = ''
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
        self.remapSystChanName = ""
        self.doBlindingOverwrite = False
        return

    def initialize(self):
        for sample in self.sampleList:
            pass
            # if not sample.isData and not sample.isQCD and not sample.isDiscovery:
            #     for (systName, syst) in self.systDict.items():
            #         try:
            #             sample.getSystematic(systName)
            #         except:
            #             sample.addSystematic(syst)

    def Clone(self, prefix=""):
        if prefix == "":
            prefix = self.prefix
        # copies all properties prior to initialize
        newChan = deepcopy(self)
        newChan.ConstructorInit(prefix)
        return newChan

    def ConstructorInit(self, prefix):
        self.prefix = prefix
        self.xmlFileName = "config/" + self.prefix + "_" + self.channelName + ".xml"
        return

    def addSample(self, sample, index=-1):
        """
        Add Sample object to this channel
        """
        if index == -1:
            index = len(self.sampleList)  # = end of list

        self.sampleList.insert(index, sample.Clone())
        self.sampleList[index].parentChannel = self

        if sample.isData or sample.isDiscovery or sample.isQCD:
            return

        if len(self.sampleList[index].weights) == 0:
            self.sampleList[index].weights = deepcopy(self.weights)

        for (systName, syst) in self.systDict.items():
            if not systName in self.sampleList[-1].systDict.keys():
                self.sampleList[index].addSystematic(syst)
        return


    def getSample(self, name):
        """
        Get Sample object for this channel
        """
        for s in self.sampleList:
            if s.name == name:
                return s

        raise Exception("Could not find sample with name %s in %s"
                        % (name, self.sampleList))


    def hasSample(self, name):
        """
        Get Sample object for this channel
        """
        for s in self.sampleList:
            if s.name == name:
                return True

        return False
    

    def removeSample(self, sample):
        if isinstance(sample, Sample):
            aSam = sample
        elif isinstance(sample,str):
            aSam = self.getSample(sample)
        else:
            raise ValueError("Channel: sample type %s not supported" % (type(sample)))
        
        try:
            self.sampleList.remove(aSam)
        except:
            log.warning("unable to remove sample %s from channel %s" % (aSam.name, self.name))
        
        return

    def setFileList(self, filelist):
        """
        Set file list for this Channel.
        This will be used as default for samples that don't specify
        their own file list.
        """
        self.files = filelist

    def setFile(self, file):
        """
        Set file for this Sample directly
        This will be used as default for samples that don't specify
        their own file list.
        """
        self.files = [file]

    def propagateFileList(self, fileList):
        """
        Propagate the file list downwards.
        """
        #  if we don't have our own file list,  use the one given to us
        if not self.files:
            self.files = fileList
        #  propagate our file list downwards
        for sam in self.sampleList:
                sam.propagateFileList(self.files)

    def setWeights(self, weights):
        """
        Set the weights for this channel - overrides previous weights

        Propagate to owned samples
        """
        self.weights = deepcopy(weights)

        for s in self.sampleList:
            if not s.isData and not s.isQCD and not s.isDiscovery:
                s.setWeights(weights)

        return

    def addWeight(self, weight):
        """
        Add a single weight and propagate
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

        for syst in self.systDict.values():
            if syst.type == "weight":
                if not weight in syst.high:
                    syst.high.append(weight)
                if not weight in syst.low:
                    syst.low.append(weight)
        return

    def removeWeight(self, weight):
        """
        Remove a single weight and propagate
        """
        if weight in self.weights:
            self.weights.remove(weight)

        for s in self.sampleList:
            if not s.isData and not s.isQCD and not s.isDiscovery:
                if weight in s.weights:
                    s.removeWeight(weight)

        for syst in self.systDict.values():
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

            histoName = "h%sNom_%s_obs_%s" % (sigSample.name, sr, self.variableName.replace("/", ""))
            self.getSample("DiscoveryMode_%s" % sr).setHistoName(histoName)

            configMgr.hists[histoName] = TH1F(histoName, histoName,
                                              len(srList), 0.0,
                                              float(len(srList)))
            configMgr.hists[histoName].SetBinContent(iSR+1, startValList[iSR])

        return

    def addData(self, dataName):
        """
        Add a prepared data histogram to this channel
        """
        if len(self.dataList):
            raise IndexError("Channel already has data " + str(self.dataList))
        self.dataList.append((configMgr.histCacheFile, dataName, ""))

    def addPseudoData(self, toyInputHistoList, varName, varLow, varHigh,
                      addInputHistoList, histoPath="", seed=None):
        """
        Add a pseudo data distribution to this channel

        !!! DEPRECATED, MAY NOT WORK !!!
        """
        if len(self.dataList):
            raise IndexError("Channel already has data " + str(self.dataList))
        histo = generateToys.generate(toyInputHistoList, varName,
                                      varLow, varHigh)
        for iBin in xrange(histo.GetNbinsX() + 1):
            for inputHisto in addInputHistoList:
                histo.SetBinContent(iBin+1, TMath.Nint(histo.GetBinContent(iBin+1)) + TMath.Nint(inputHisto.GetBinContent(iBin+1)))
        for iBin in xrange(histo.GetNbinsX() + 1):
            histo.SetBinError(iBin+1, TMath.Sqrt(histo.GetBinContent(iBin+1)))

        self.dataList.append((configMgr.histCacheFile, histo.GetName(), ""))
        return

    def addSystematic(self, syst):
        """
        Add a systematic to this channel.
        This will be propagated to all owned samples
        """
        if syst.name in self.systDict.keys():
            raise Exception("Attempt to overwrite systematic %s "
                            " in Channel %s" % (syst.name, self.name))
        else:
            self.systDict[syst.name] = syst.Clone()
            for sam in self.sampleList:
                sam.addSystematic(syst)
            return

    def getSystematic(self, systName):
        """
        Find the systematic with the given name
        """
        try:
            return self.systDict[systName]
        except KeyError:
            raise KeyError("Could not find systematic %s "
                           "in topLevel %s" % (systName, self.name))

    def setTreeName(self, treeName):
        self.treeName = treeName
        return

    def propagateTreeName(self, treeName):
        if self.treeName == '':
            self.treeName = treeName
        ##  MAB : Propagate down to samples
        for sam in self.sampleList:
            sam.propagateTreeName(self.treeName)
            pass
        return

    def createHistFactoryObject(self):
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
        self.writeString = "<!DOCTYPE Channel SYSTEM '../HistFactorySchema.dtd'>\n\n"
        self.writeString += "<Channel Name=\"%s\">\n\n" % self.channelName
        for data in self.dataList:
            if len(data[2]):
                self.writeString += "  <Data HistoName=\"%s\" InputFile=\"%s\" HistoPath=\"%s\" />\n\n" % (data[1], data[0], data[2])
            else:
                self.writeString += "  <Data HistoName=\"%s\" InputFile=\"%s\" />\n\n" % (data[1], data[0])
        if self.hasStatConfig:
            self.writeString += "  <StatErrorConfig RelErrorThreshold=\"%g\" ConstraintType=\"%s\"/>\n\n" % (self.statErrorThreshold, self.statErrorType)
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

