#!/usr/bin/python
# -*- coding: utf-8 -*-
from ROOT import TFile, TMath, RooRandom, TH1, TH1F
from ROOT import kBlack, kWhite, kGray, kRed, kPink, kMagenta, kViolet, \
    kBlue, kAzure, kCyan, kTeal, kGreen, kSpring, kYellow, kOrange, \
    kDashed, kSolid, kDotted
from os import system
from math import fabs
from measurmt import Measurement
from chanxml import ChannelXML
from smpl import Sample

import generateToys

TH1.SetDefaultSumw2(True)

from copy import deepcopy, copy
from configManager import configMgr


class TopLevelXML(object):

    """
    Defines the content of a top-level HistFactory xml file
    """

    def __init__(self, name):
        """
        Set the combination mode, store the configuration and open output file
        """

        self.ConstructorInit(name)

        # attributes to below are OK to deepcopy

        self.mode = 'comb'
        self.verbose = 1
        self.statErrThreshold = None  # None means to turn OFF mcStat error
        self.measurements = []
        self.channels = []
        self.sampleList = []
        self.signalSample = None
        self.signalChannels = []
        self.validationChannels = []
        self.bkgConstrainChannels = []
        self.systDict = {}
        self.files = []
        self.weights = []
        self.treeName = ''

        # Plot cosmetics

        self.dataColor = kBlack
        self.totalPdfColor = kBlue
        self.errorLineColor = kBlue - 5
        self.errorLineStyle = kSolid
        self.errorFillColor = kBlue - 5
        self.errorFillStyle = 3004
        self.setLogy = False
        self.tLegend = None

    def Clone(self, newName=''):
        if newName == '':
            newName = self.name

        # copies all properties prior to initialize

        newTLX = deepcopy(self)
        newTLX.ConstructorInit(newName)
        for chan in newTLX.channels:
            chan.ConstructorInit(newTLX.prefix)
        return newTLX

    def ConstructorInit(self, name):

        # shared method between __init__ and Clone

        self.name = name
        self.prefix = configMgr.analysisName + '_' + self.name
        self.xmlFileName = 'N/A'
        self.wsFileName = 'N/A'
        return

    def __str__(self):
        """
        Convert instance to XML string
        """

        self.writeString = \
            """<!DOCTYPE Combination  SYSTEM 'HistFactorySchema.dtd'>

"""
        self.writeString += '<Combination OutputFilePrefix="./results/'\
             + self.prefix + '" Mode="' + self.mode + '''" >

'''
        for chan in self.channels:
            self.writeString += '  <Input>' + chan.xmlFileName\
                 + '</Input>\n'
        self.writeString += '\n'
        for meas in self.measurements:
            self.writeString += str(meas)
        self.writeString += '</Combination>\n'
        return self.writeString

    def initialize(self):
        self.xmlFileName = 'config/' + self.prefix + '.xml'

        # Note: wsFileName is an educated guess of the workspace file name externally decided by HistFactory.

        self.wsFileName = 'results/' + self.prefix + '_combined_'\
             + self.measurements[0].name + '_model.root'
        for sam in self.sampleList:
            if sam.isData:  # FIXME (works but ugly)
                self.sampleList.remove(sam)  # Just making sure that Data is the last element of the list
                self.sampleList.append(sam)
                break

        # Consistency checks

        if not self.signalSample == None:
            found = False
            for s in self.sampleList:
                if s.name == self.signalSample:
                    found = True
            if not found:
                for chan in self.channels:
                    for s in chan.sampleList:
                        if s.name == self.signalSample:
                            found = True
                if not found:
                    print 'WARNING signal sample %s is not contained in sampleList of TopLvlXML %s or its daughter channels'\
                         % (self.signalSample, self.name)

        for chan in self.channels:
            chanName = chan.channelName
            isSR = False
            isCR = False
            isVR = False
            nFound = 0
            if self.signalChannels.__contains__(chanName):
                isSR = True
                nFound += 1
            if self.bkgConstrainChannels.__contains__(chanName):
                isCR = True
                nFound += 1
            if self.validationChannels.__contains__(chanName):
                isVR = True
                nFound += 1
            if nFound == 0:
                print 'WARNING TopLvlXML: %s, Channel: %s --> SR/CR/VR undefined'\
                     % (self.name, chanName)
            if nFound > 1:
                print 'WARNING TopLvlXML: %s, Channel: %s --> SR=%s CR=%s VR=%s is ambiguous'\
                     % (self.name, chanName, isSR, isCR, isVR)

            # for sample in self.sampleList:
            #    try:
            #        chan.getSample(sample.name)
            #    except:
            #        chan.addSample(sample)
            #    for (systName,syst) in sample.systDict.items():
            #        try:
            #            chan.getSample(sample.name).getSystematic(systName)
            #        except:
            #            for s in sample.getSystematic(systName):
            #                chan.getSample(sample.name).addSystematic(s)

        return

    def close(self):
        """
        Write instance to file and close
        """

        print "Writing file: '%s'" % self.xmlFileName
        if self.verbose > 2:
            print str(self)
            pass
        self.xmlFile = open(self.xmlFileName, 'w')
        self.xmlFile.write(str(self))
        self.xmlFile.close()
        for chan in self.channels:
            chan.close()
            if self.verbose > 2:
                print str(chan)
        return

    def execute(self, option=''):
        """
        Run hist2workspace binary on this file
        """

        cmd = 'hist2workspace '
        if len(option):
            cmd += '-' + option

        cmd += self.xmlFileName
        if not self.verbose > 2:
            cmd += ' 1> /dev/null '

        print "\nExecuting: '%s'" % cmd
        system(cmd)

        print "Created workspace 'combined' in file '%s'\n"\
             % self.wsFileName
        return

    def addMeasurement(
        self,
        name,
        lumi,
        lumiErr,
        ):

        # verify that this name is not already used

        for meas in self.measurements:
            if meas.name == name:
                raise RuntimeError('Measurement %s already exists in TopLevelXML %s. Please use a different name.'
                                    % (measObj.name, self.name))
            pass

        # add measurement to the list

        self.measurements.append(Measurement(name, lumi, lumiErr))
        return self.measurements[len(self.measurements) - 1]

    def addMeasurementObj(self, obj):
        if not isinstance(obj, Measurement):
            raise RuntimeError("addMeasurement does not support input of type '%s'."
                                % type(obj))

        # verify that this name is not already used

        for meas in self.measurements:
            if meas.name == obj.name:
                raise RuntimeError('Measurement %s already exists in TopLevelXML %s. Please use a different name.'
                                    % (measObj.name, self.name))
            pass

        # add measurement clone to the list

        self.measurements.append(obj.Clone())
        return self.measurements[len(self.measurements) - 1]

    def getMeasurement(self, name):
        """
        Find the measurement object with given name
        """

        for m in self.measurements:
            if m.name == name:
                return m

        raise RuntimeError('Measurement %s does not exist in %s'
                            % (name, self.name))

    def addChannel(
        self,
        variableName,
        regions,
        nBins,
        binLow,
        binHigh,
        ):
        """
        Build a channel object from this TopLevel
        """

        chanObj = ChannelXML(
            variableName,
            regions,
            self.prefix,
            nBins,
            binLow,
            binHigh,
            self.statErrThreshold,
            )

        # Verify that this name is not already used

        for chan in self.channels:
            if chan.name == chanObj.name:
                raise RuntimeError('Channel %s already exists in TopLevelXML %s. Please use a different name.'
                                    % (chanObj.name, self.name))

        # Channel doesn't have weights so add them

        chanObj.setWeights(self.weights)

        # Propagate systematics into channel

        for (systName, syst) in self.systDict.items():
            chanObj.addSystematic(syst)

        # Put samples owned by this TopLevel into the channel

        for s in self.sampleList:
            chanObj.addSample(s.Clone())

        # Add channel to the list

        self.channels.append(chanObj)

        return self.channels[len(self.channels) - 1]

    def addChannelObj(self, obj):
        """
        Add channel as a pre-built object
        """

        if not isinstance(obj, ChannelXML):
            raise RuntimeError("addChannel does not support input of type '%s'."
                                % type(obj))

        # Verify that this name is not already used

        for chan in self.channels:
            if chan.name == obj.name:
                raise RuntimeError('Channel %s already exists in TopLevelXML %s. Please use a different name.'
                                    % (chanObj.name, self.name))

        # Create a copy

        newObj = deepcopy(obj)

        # If the channel doesn't have any weights then add them

        if len(newObj.weights) == 0:
            newObj.weights.setWeights(self.weights)

        # Propagate systematics into channel

        for (systName, syst) in self.systDict.items():
            if not systName in newObj.systDict.keys():
                newObj.addSystematic(syst)

        # Put samples owned by this TopLevel into the channel

        for s in self.sampleList:
            if not s.name in [sam.name for sam in newObj.sampleList]:
                newObj.addSample(s)

        # Add channel clone to the list

        self.channels.append(newObj)
        return self.channels[len(self.channels) - 1]

    def addValidationChannel(
        self,
        variableName,
        regions,
        nBins,
        binLow,
        binHigh,
        ):
        """
        Create a channel and give it a validation flag
        """

        ch = self.addChannel(variableName, regions, nBins, binLow,
                             binHigh)

        self.setValidationChannels(ch)

        return ch

    def getChannel(self, variableName, regions):
        """
        Find the channel with the given variable and regions
        """

        for chan in self.channels:
            if chan.variableName == variableName and chan.regions\
                 == regions:
                return chan

        raise RuntimeError('No channel with variable name %s and regions %s found'
                            % (variableName, regions))

    def addSamples(self, input):
        """
        Add list (or single object) of pre-built samples to this TopLevel
        """

        if isinstance(input, list):
            sampleList = input
        else:
            sampleList = [input]
            pass

        for s in sampleList:

            # If the sample doesn't exist in TopLevel already then add it, else something has gone wrong

            if not s.name in [sam.name for sam in self.sampleList]:

                # Append copy of the sample

                self.sampleList.append(s.Clone())

                # Only apply weights and systematics to MC-derived samples

                if not s.isData and not s.isDiscovery and not s.isQCD:

                    # If the sample doesn't have weights then add them

                    if len(self.sampleList[-1].weights) == 0:
                        self.sampleList[-1].setWeights(self.weights)

                    # Propagate systematics into sample

                    for (systName, syst) in self.systDict.items():
                        if not systName\
                             in self.sampleList[-1].systDict.keys():
                            self.sampleList[-1].addSystematic(syst)
            else:

                raise RuntimeError('Sample %s already defined in TopLevel %s'
                                    % (s.name, self.name))

            # Propagate to channels that are already owned as well

            for c in self.channels:
                hasSample = False
                if not s.name in [sam.name for sam in c.sampleList]:
                    c.addSample(self.getSample(s.name))
        return

    def getSample(self, name):
        """
        Find the sample with the given name
        """

        for s in self.sampleList:
            if s.name == name:
                return s
        raise Exception('Sample with name %s not found in TopLevel %s'
                         % (name, self.name))

    def setWeights(self, weights):
        """
        Set the weights
        
        This overrides all previously defined weights
        """

        self.weights = deepcopy(weights)

        # Propagate to owned channels that do not already have weights

        for c in self.channels:
            if len(c.weights) == 0:
                c.setWeights(weights)

        # Propagate to owned samples that do not already have weights

        for s in self.sampleList:
            if not s.isData and not s.isDiscovery and not s.isQCD:
                if len(s.weights) == 0:
                    s.setWeights(weights)

        return

    def addWeight(self, weight):
        """
        Add a single weight
        """

        if not weight in self.weights:
            self.weights.append(weight)
        else:
            raise RuntimeError('Weight %s already defined in TopLevel'
                                % (weight, self.name))

        # Propagate to owned channels that do not already have this weight

        for c in self.channels:
            if not weight in c.weights:
                c.addWeight(weight)

        # Propagate to owned samples that do not already have this weight

        for s in self.sampleList:
            if not s.isData and not s.isDiscovery and not s.isQCD:
                if not weight in s.weights:
                    s.addWeight(weight)

        # Propagate to owned weight-type systematics that do not already have this weight

        for syst in self.systDict.values():
            if syst.type == 'weight':
                if not weight in syst.high:
                    syst.high.append(weight)
                if not weight in syst.low:
                    syst.low.append(weight)
        return

    def removeWeight(self, weight):
        """
        Remove a single weight
        """

        if weight in self.weights:
            self.weights.remove(weight)
        else:
            raise RuntimeError('Weight %s does not exist in TopLevel %s'
                                % (weight, self.name))

        # Propagate to owned channels

        for c in self.channels:
            if weight in c.weights:
                c.removeWeight(weight)

        # Propagate to owned samples

        for s in self.sampleList:
            if not s.isData and not s.isDiscovery and not s.isQCD:
                if weight in s.weights:
                    s.removeWeight(weight)

        # Propagate to owned weight-type systematics

        for syst in self.systDict.values():
            if syst.type == 'weight':
                if weight in syst.high:
                    syst.high.remove(weight)
                if weight in syst.low:
                    syst.low.remove(weight)
        return

    def setSignalSample(self, sig):
        """
        Flag the signal sample
        """

        if isinstance(sig, Sample):
            self.signalSample = sig.name
        elif isinstance(sig, str):
            self.signalSample = sig
        else:
            raise RuntimeError('setSignalSample does not support type %s'
                                % type(sig))
        return

    def appendStrChanOrListToList(self, input, targetList):

        # little utility function

        if isinstance(input, list):
            inList = input
        else:
            inList = [input]
            pass
        for i in inList:
            if isinstance(i, ChannelXML):
                chanName = i.channelName
            else:
                chanName = i
                pass
            if not targetList.__contains__(chanName):
                targetList.append(chanName)
                pass
            pass
        return

    def setSignalChannels(self, chans):
        """
        Set the channels to be treated as signal (SRs)
        """

        self.appendStrChanOrListToList(chans, self.signalChannels)
        return

    def setBkgConstrainChannels(self, chans):
        """
        Set the channels to be treated as constraining regions (CRs)
        """

        self.appendStrChanOrListToList(chans, self.bkgConstrainChannels)
        return

    def setValidationChannels(self, chans):  # should be renamed appendValidationChannels !
        """
        Set the channels to be treated as validation regions (VRs)
        """

        self.appendStrChanOrListToList(chans, self.validationChannels)
        return

    def setFileList(self, filelist):
        """
        Set file list for this top level xml.
        This will be used as default for channels that don't specify
        their own file list.
        """

        self.files = filelist
        return

    def setFile(self, file):
        """
        Set file for this top level xml.
        This will be used as default for channels that don't specify
        their own file list.
        """

        self.files = [file]
        return

    def propagateFileList(self, fileList):
        """
        Propagate the file list downwards.
        """

        # if we don't have our own file list, use the one given to us

        if self.files == []:
            self.files = fileList

        # propagate our file list downwards

        for ch in self.channels:
            ch.propagateFileList(self.files)
        return

    def addSystematic(self, syst):
        """
        Add a systematic to this object. This will be propagated to all owned samples
        """

        if syst.name in self.systDict.keys():
            raise RuntimeError('Attempt to overwrite systematic %s in TopLevel %s'
                                % (syst.name, self.name))
        else:
            self.systDict[syst.name] = syst.Clone()
            for chan in self.channels:
                chan.addSystematic(syst)
            for sam in self.sampleList:
                if not sam.isData and not sam.isDiscovery\
                     and not sam.isQCD:
                    sam.addSystematic(syst)
            return

    def getSystematic(self, systName):
        """
        Find the systematic with given name
        """

        try:
            return self.systDict[systName]
        except KeyError:
            raise KeyError('Could not find systematic %s in topLevel %s'
                            % (systName, self.name))

    def clearSystematics(self):
        """
        Remove all systematics from this TopLevel
        """

        self.systDict.clear()
        return

    def removeSystematic(self, name):
        """
        Remove a single systematic from this TopLevel
        """

        del self.systDict[name]
        return

    def setTreeName(self, treeName):
        """
        Set the tree name
        """

        self.treeName = treeName
        return

    def propagateTreeName(self, treeName):
        """
        Propagate the tree name
        """

        if self.treeName == '':
            self.treeName = treeName

        # # propagate down to channels

        for chan in self.channels:
            chan.propagateTreeName(self.treeName)
            pass
        return


