from ROOT import TFile,TMath,RooRandom,TH1,TH1F
from ROOT import kBlack,kWhite,kGray,kRed,kPink,kMagenta,kViolet,kBlue,kAzure,kCyan,kTeal,kGreen,kSpring,kYellow,kOrange,kDashed,kSolid,kDotted
from os import system
from math import fabs
import generateToys

TH1.SetDefaultSumw2(True)

from copy import deepcopy,copy
from configManager import configMgr

class TopLevelXML(object):
    """
    Defines the content of a top-level HistFactory xml file
    """

    def __init__(self,name):
        """
        Set the combination mode, store the configuration and open output file
        """
        self.ConstructorInit(name)
        #attributes to below are OK to deepcopy
        self.mode = "comb"
        self.verbose=1
        self.statErrThreshold=None #None means to turn OFF mcStat error
        self.measurements = []
        self.channels = []
        self.sampleList = []
        self.signalSample = None
        self.signalChannels=[]
        self.validationChannels=[]
        self.bkgConstrainChannels=[]
        self.systDict = {}
        self.files = []
        self.treeName = ''
        # Plot cosmetics
        self.dataColor=kBlack
        self.totalPdfColor=kBlue
        self.errorLineColor=kBlue-5
        self.errorLineStyle=kSolid
        self.errorFillColor=kBlue-5
        self.errorFillStyle=3004
        self.setLogy = False
        self.tLegend = None
        
    def Clone(self,newName=""):
        if newName=="":
            newName=self.name
        #copies all properties prior to initialize
        newTLX = deepcopy(self)
        newTLX.ConstructorInit(newName)
        for chan in newTLX.channels:
            chan.ConstructorInit(newTLX.prefix)
        return newTLX

    def ConstructorInit(self,name):
        #shared method between __init__ and Clone
        self.name=name
        self.prefix=configMgr.analysisName+"_"+self.name
        self.xmlFileName = "N/A"
        self.wsFileName = "N/A"
        return

    def __str__(self):
        """
        Convert instance to XML string
        """
        self.writeString = "<!DOCTYPE Combination  SYSTEM 'HistFactorySchema.dtd'>\n\n"
        self.writeString += "<Combination OutputFilePrefix=\"./results/"+self.prefix+"\" Mode=\""+self.mode+"\" >\n\n"
        for chan in self.channels:
            self.writeString += "  <Input>"+chan.xmlFileName+"</Input>\n"
        self.writeString += "\n"     
        for meas in self.measurements:
            self.writeString += str(meas)
        self.writeString += "</Combination>\n"
        return self.writeString


    def initialize(self):
        self.xmlFileName = "config/"+self.prefix+".xml"
        #Note: wsFileName is an educated guess of the workspace file name externally decided by HistFactory.
        self.wsFileName = "results/"+self.prefix+"_combined_"+self.measurements[0].name+"_model.root"
        for sam in self.sampleList:
            if sam.isData: # FIXME (works but ugly)
                self.sampleList.remove(sam)       #Just making sure that Data is the last element of the list
                self.sampleList.append(sam)
                break
        #Consistency checks
        if not self.signalSample == None:
            found = False
            for s in self.sampleList:
                if s.name==self.signalSample:
                    found=True
            if not found:
                for chan in self.channels:
                    for s in chan.sampleList:
                        if s.name == self.signalSample:
                            found = True
                if not found:
                    print "WARNING signal sample %s is not contained in sampleList of TopLvlXML %s or its daughter channels"%(self.signalSample,self.name)
                        
        for chan in self.channels:
            chanName=chan.channelName
            isSR=False
            isCR=False
            isVR=False
            nFound=0
            if self.signalChannels.__contains__(chanName):
                isSR=True
                nFound+=1
            if self.bkgConstrainChannels.__contains__(chanName):
                isCR=True
                nFound+=1
            if self.validationChannels.__contains__(chanName):
                isVR=True
                nFound+=1
            if nFound==0:
                print "WARNING TopLvlXML: %s, Channel: %s --> SR/CR/VR undefined"%(self.name,chanName)
            if nFound>1:
                print "WARNING TopLvlXML: %s, Channel: %s --> SR=%s CR=%s VR=%s is ambiguous"%(self.name,chanName,isSR,isCR,isVR)
            for sample in self.sampleList:
                try:
                    chan.getSample(sample.name)
                except:
                    chan.addSample(sample)
                for syst in sample.systDict.keys():
                    try:
                        chan.getSample(sample.name).getSystematic(syst)
                    except:
                        for s in sample.getSystematic(syst):
                            chan.getSample(sample.name).addSystematic(s)
        return
    
    def close(self):
        """
        Write instance to file and close
        """
        print "Writing file: '%s'"%self.xmlFileName
        if self.verbose > 2:
            print str(self)
            pass
        self.xmlFile = open(self.xmlFileName,"w")
        self.xmlFile.write(str(self))
        self.xmlFile.close()
        for chan in self.channels: 
            chan.close()
            if self.verbose > 2:
                print str(chan)
        return

    def execute(self,option=""):
        """
        Run hist2workspace binary on this file
        """
        cmd ="hist2workspace "
        if len(option):
            cmd += "-"+option

        cmd += self.xmlFileName
        if not (self.verbose > 2):
            cmd += " 1> /dev/null "
        
        print "\nExecuting: '%s'"%cmd
        system(cmd)

        print "Created workspace 'combined' in file '%s'\n"%self.wsFileName
        return

    def addMeasurement(self,name,lumi,lumiErr):
        #verify that this name is not already used
        for meas in self.measurements:
            if meas.name == name:
                raise RuntimeError("Measurement %s already exists in TopLevelXML %s. Please use a different name."%(measObj.name,self.name))
            pass
        #add measurement to the list
        self.measurements.append(Measurement(name,lumi,lumiErr))
        return self.measurements[len(self.measurements)-1]

    def addMeasurementObj(self,obj):
        if not isinstance(obj,Measurement):
            raise RuntimeError("addMeasurement does not support input of type '%s'."%(type(obj)))
        #verify that this name is not already used
        for meas in self.measurements:
            if meas.name == obj.name:
                raise RuntimeError("Measurement %s already exists in TopLevelXML %s. Please use a different name."%(measObj.name,self.name))
            pass
        #add measurement clone to the list
        self.measurements.append(obj.Clone())
        return self.measurements[len(self.measurements)-1]

    def getMeasurement(self,name):
        for m in self.measurements:
            if m.name == name:
                return m
        raise RuntimeError("Measurement %s does not exist in %s"%(name,self.name))    
                
    def addChannel(self,variableName,regions,nBins,binLow,binHigh):
        chanObj = ChannelXML(variableName,regions,self.prefix,nBins,binLow,binHigh,self.statErrThreshold)
        #verify that this name is not already used
        for chan in self.channels:
            if chan.name == chanObj.name:
                raise RuntimeError("Channel %s already exists in TopLevelXML %s. Please use a different name."%(chanObj.name,self.name))
            pass
        for s in self.sampleList:
            chanObj.addSample(s)
        #add channel to the list
        self.channels.append(chanObj)
        return self.channels[len(self.channels)-1]

    def getChannel(self,variableName,regions):
        for chan in self.channels:
            if chan.variableName == variableName and chan.regions == regions:
                return chan
        raise ValueError("No channel with variable name %s and regions %s found" % (variableName,regions))

    def addChannelObj(self,obj):
        if not isinstance(obj,ChannelXML):
            raise RuntimeError("addChannel does not support input of type '%s'."%(type(obj)))
        #verify that this name is not already used
        for chan in self.channels:
            if chan.name == obj.name:
                raise RuntimeError("Channel %s already exists in TopLevelXML %s. Please use a different name."%(chanObj.name,self.name))
            pass
        for s in self.sampleList:
            obj.addSample(s)
        #add channel clone to the list
        self.channels.append(deepcopy(obj))
        return self.channels[len(self.channels)-1]

    def addSamples(self,input):
        if isinstance(input,list):
            sampleList=input
        else:
            sampleList=[input]
            pass
        for s in sampleList:
            if not self.sampleList.__contains__(s):
                self.sampleList.append(s.Clone())
            for c in self.channels:
                hasSample = False
                for cSam in c.sampleList:
                    if s.name == cSam.name:
                        hasSample = True
                if not hasSample:
                    c.addSample(self.getSample(s.name))
        return

    def getSample(self,name):
        for s in self.sampleList:
            if s.name == name:
                return s
        raise Exception("Sample with name %s not found in TopLevel %s"%(name,self.name))

    def setSignalSample(self,sig):
        if isinstance(sig,Sample):
            self.signalSample=sig.name
        elif isinstance(sig,str):
            self.signalSample=sig
        else:
            raise RuntimeError("setSignalSample does not support type %s"%(type(sig)))
        return

    def appendStrChanOrListToList(self,input,targetList):
        #little utility function
        if isinstance(input,list):
            inList=input
        else:
            inList=[input]
            pass
        for i in inList:
            if isinstance(i,ChannelXML):
                chanName=i.channelName
            else:
                chanName=i
                pass
            if not targetList.__contains__(chanName):
                targetList.append(chanName)
                pass
            pass
        return

    def setSignalChannels(self,chans):
        self.appendStrChanOrListToList(chans,self.signalChannels)
        return

    def setBkgConstrainChannels(self,chans):
        self.appendStrChanOrListToList(chans,self.bkgConstrainChannels)
        return

    def setValidationChannels(self,chans): #should be renamed appendValidationChannels !
        self.appendStrChanOrListToList(chans,self.validationChannels)
        return

    def setFileList(self,filelist):
        """
        Set file list for this top level xml.
        This will be used as default for channels that don't specify
        their own file list.
        """
        self.files = filelist

    def setFile(self,file):
        """
        Set file for this top level xml.
        This will be used as default for channels that don't specify
        their own file list.
        """
        self.files = [file]

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

    def addSystematic(self,syst):
        """
        Add a systematic to this object. This will be propagated to all owned samples
        """
        if not syst.name in self.systDict.keys():
            self.systDict[syst.name] = []
        self.systDict[syst.name].append(syst.Clone())
        return

    def getSystematic(self,systName):
        try:
            return self.systDict[systName]
        except KeyError:
            raise KeyError("Could not find systematic %s in topLevel %s" % (systName,self.name))

    def clearSystematics(self):
        self.systDict.clear()
        return

    def removeSystematic(self,name):
        del self.systDict[name]
        return

    def setTreeName(self,treeName):
        self.treeName = treeName
        return

    def propagateTreeName(self,treeName):
        if self.treeName == '':
            self.treeName = treeName
        ## propagate down to channels
        for chan in self.channels:
            chan.propagateTreeName(self.treeName)
            pass
        return
    
class Measurement(object):
    """
    Class to define measurements in the top-level xml
    """

    def __init__(self,name,lumi,lumiErr):
        """
        Store configuration, add to top level list of measurements, specify lumi parameters and if run in exportOnly mode
        """
        self.name = name
        self.lumi = lumi
        self.lumiErr = lumiErr
        self.binLow = 0
        self.binHigh = 50
        self.mode = "comb"
        self.exportOnly = "True"
        self.poiList = []
        self.constraintTermDict = {} 
        self.paramSettingDict = {}

    def Clone(self,newName=""):
        if newName=="":
            newName=self.name
        newMeas=deepcopy(self)
        newMeas.name=newName
        return newMeas

    def addPOI(self,poi):
        """
        Add a parameter of interest
        """
        self.poiList.append(poi)
        
    def addParamSetting(self,paramName,const,val=None):
        """
        Define the settings for a parameter
        """
        self.paramSettingDict[paramName] = (const,val)

    def addConstraintTerm(self,paramName,type,relUnc=None):
        """
        Define the constraint term for a parameter
        """
        self.constraintTermDict[paramName] = (type,relUnc)

    def __str__(self):
        """
        Convert instance to an XML string
        """
        measurementString = "  <Measurement Name=\"%s\" Lumi=\"%g\" LumiRelErr=\"%g\" BinLow=\"%d\" BinHigh=\"%d\" Mode=\"%s\" ExportOnly=\"%s\">\n" % (self.name,self.lumi,self.lumiErr,self.binLow,self.binHigh,self.mode,self.exportOnly)
        measurementString += "    <POI>"
        for (iPOI,poi) in enumerate(self.poiList):
            if not iPOI == len(self.poiList) - 1:
                measurementString += "%s " % (poi)
            else:
                measurementString += "%s</POI>\n" % (poi)
        for (param,setting) in self.paramSettingDict.iteritems():
            if setting[0]:
                if not setting[1] == None:
                    measurementString += "    <ParamSetting Const=\"True\" Val=\"%g\">%s</ParamSetting>\n" % (setting[1],param)
                else:
                    measurementString += "    <ParamSetting Const=\"True\">%s</ParamSetting>\n" % (param)
            else:
                if not setting[1] == None: 
                    measurementString += "    <ParamSetting Const=\"False\" Val=\"%g\">%s</ParamSetting>\n" % (setting[1],param)
                else:
                    measurementString += "    <ParamSetting Const=\"False\">%s</ParamSetting>\n" % (param)
        for (param,constraint) in self.constraintTermDict.iteritems():
            if not constraint[1] == None:
                measurementString += "    <ConstraintTerm Type=\"%s\" RelativeUncertainty=\"%g\">%s</ConstraintTerm>\n" % (constraint[0],constraint[1],param)
            else:
                measurementString += "    <ConstraintTerm Type=\"%s\">%s</ConstraintTerm>\n" % (constraint[0],param)
        measurementString += "  </Measurement>\n\n"
        return measurementString




class ChannelXML(object):
    """
    Defines the content of a channel HistFactory xml file
    """

    def __init__(self,variableName,regions,prefix,nBins,binLow,binHigh,statErrorThreshold=None,hasB=False):
        """
        Store configuration, set unique channel name from variable, define cut region, binning and open file
        """
        regions.sort()
        self.regionString = "".join(regions)
        self.variableName = variableName
        self.name = self.variableName.replace("/","")+"_"+self.regionString
        self.channelName = self.regionString+"_"+variableName.replace("/","")
        self.ConstructorInit(prefix) #shared method with Clone or deepcopy
        self.regions = regions
        self.nBins = nBins
        self.binHigh = binHigh
        self.binLow = binLow
        self.sampleList = []
        self.dataList = []
        self.systDict = {}
        self.infoDict = {}
        self.hasB = hasB
        self.hasBQCD = False
        self.useOverflowBin=False
        self.useUnderflowBin=False
        self.hasStatConfig = False
        self.hasDiscovery = False
        if not statErrorThreshold == None:
            self.hasStatConfig = True
            self.statErrorThreshold = statErrorThreshold
            self.statErrorType = "Poisson"
        self.files = []
        self.treeName = ''
        # Plot cosmetics
        self.minY = None
        self.maxY = None
        self.titleX = None
        self.titleY = None
        self.logY = None
        self.ATLASLabelX = None
        self.ATLASLabelY = None
        self.ATLASLabelText = None
        self.showLumi = None
        return

    def initialize(self):
        for sample in self.sampleList:
            for syst in self.systDict.keys():
                try:
                    sample.getSystematic(syst)
                except:
                    for s in self.systDict[syst]:
                        sample.addSystematic(s)

    def Clone(self,prefix=""):
        if prefix=="":
            prefix=self.prefix
        #copies all properties prior to initialize
        newChan = deepcopy(self)
        newchan.ConstructorInit(prefix)
        return newChan

    def ConstructorInit(self,prefix):
        self.prefix=prefix
        self.xmlFileName = "config/"+self.prefix+"_"+self.channelName+".xml"
        return
    
    def addSample(self,sample):
        """
        Add Sample object to this channel
        """
        self.sampleList.append(sample.Clone())

    def getSample(self,name):
        """
        Get Sample object for this channel
        """
        for s in self.sampleList:
            if s.name == name:
                return s
        raise Exception("Could not find sample with name %s in %s"%(name,self.sampleList))

    def setFileList(self,filelist):
        """
        Set file list for this Channel.
        This will be used as default for samples that don't specify
        their own file list.
        """
        self.files = filelist

    def setFile(self,file):
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
        # if we don't have our own file list, use the one given to us
        if self.files == []:
                self.files = fileList
        # propagate our file list downwards
        for sam in self.sampleList:
                sam.propagateFileList(self.files)

    def addDiscoverySamples(self,srList,startValList,minValList,maxValList,colorList):
        """
        Add a sample to be used for discovery fits
        """
        self.hasDiscovery = True
        if not self.variableName == "cuts":
            raise TypeError("Discovery sample can only be added to a cuts channel")
        for (iSR,sr) in enumerate(srList):
            sigSample = Sample("DiscoveryMode_%s"%(sr),colorList[iSR])
            sigSample.setNormFactor("mu_%s"%(sr),startValList[iSR],minValList[iSR],maxValList[iSR])
            sigSample.setDiscovery()
            sigSample.clearSystematics()
            self.addSample(sigSample)
            histoName = "h"+sigSample.name+"Nom_"+sr+"_obs_"+self.variableName.replace("/","")
            self.getSample("DiscoveryMode_%s"%(sr)).setHistoName(histoName)
            configMgr.hists[histoName] = TH1F(histoName,histoName,len(srList),0.,float(len(srList)))
            configMgr.hists[histoName].SetBinContent(iSR+1,startValList[iSR])

    def addData(self,dataName):
        """
        Add a prepared data histogram to this channel
        """
        if len(self.dataList):
            raise IndexError("Channel already has data "+str(self.dataList))
        self.dataList.append((configMgr.histCacheFile,dataName,""))

    def addPseudoData(self,toyInputHistoList,varName,varLow,varHigh,addInputHistoList,histoPath="",seed=None):
        """
        Add a pseudo data distribution to this channel

        !!! DEPRECATED, MAY NOT WORK !!!
        """
        if not seed == None:
            RooRandom.randomGenerator().SetSeed(seed)
        if len(self.dataList):
            raise IndexError("Channel already has data "+str(self.dataList))
        histo = generateToys.generate(toyInputHistoList,varName,varLow,varHigh)
        for iBin in xrange(histo.GetNbinsX()+1):
            for inputHisto in addInputHistoList:
                histo.SetBinContent(iBin+1,TMath.Nint(histo.GetBinContent(iBin+1))+TMath.Nint(inputHisto.GetBinContent(iBin+1)))
        for iBin in xrange(histo.GetNbinsX()+1):
            histo.SetBinError(iBin+1,TMath.Sqrt(histo.GetBinContent(iBin+1)))

        self.dataList.append((configMgr.histCacheFile,histo.GetName(),""))
        return
    
    def addSystematic(self,syst):
        """
        Add a systematic to this channel. This will be propagated to all owned samples
        """
        if not syst.name in self.systDict.keys():
            self.systDict[syst.name] = []
        self.systDict[syst.name].append(syst.Clone())
        return

    def getSystematic(self,systName):
        try:
            return self.systDict[systName]
        except KeyError:
            raise KeyError("Could not find systematic %s in topLevel %s" % (systName,self.name))

    def __str__(self):
        """
        Convert instance to XML string
        """
        self.writeString = "<!DOCTYPE Channel  SYSTEM 'HistFactorySchema.dtd'>\n\n"
        self.writeString += "<Channel Name=\"%s\">\n\n" % (self.channelName)
        for data in self.dataList:
            if len(data[2]):
                self.writeString += "  <Data HistoName=\"%s\" InputFile=\"%s\" HistoPath=\"%s\" />\n\n" % (data[1],data[0],data[2])
            else:
                self.writeString += "  <Data HistoName=\"%s\" InputFile=\"%s\" />\n\n" % (data[1],data[0])
        if self.hasStatConfig:
            self.writeString += "  <StatErrorConfig RelErrorThreshold=\"%g\" ConstraintType=\"%s\"/>\n\n" % (self.statErrorThreshold,self.statErrorType)
        for (iSample,sample) in enumerate(self.sampleList):
            if sample.write:
                self.writeString += str(sample)
        self.writeString += "</Channel>\n"
        return self.writeString

    def close(self):
        """
        Write and close file
        """
        print "Writing file: '%s'"%self.xmlFileName
        self.xmlFile = open(self.xmlFileName,"w")
        self.xmlFile.write(str(self))
        self.xmlFile.close()
        return

    def setTreeName(self,treeName):
        self.treeName = treeName
        return

    def propagateTreeName(self,treeName):
        if self.treeName == '':
            self.treeName = treeName
        ## MAB : Propagate down to samples
        for sam in self.sampleList:
            sam.propagateTreeName(self.treeName)
            pass
        return


class Sample(object):
    """
    Defines a Sample in a channel XML file
    """

    def __init__(self,name,color=1):
        """
        Store configuration, set sample name, and if to normalize by theory

        Scales histograms to luminosity set in configuration
        """
        self.name = name
        self.color = color
        self.isData = False
        self.isQCD = False
        self.isDiscovery = False
        self.write = True
        self.normByTheory = False
        self.statConfig = False
        self.histoSystList = []
        self.shapeSystList = []
        self.overallSystList = []
        self.shapeFactorList = []
        self.systList = []
        self.systDict = {}
        self.normFactor = []
        self.qcdSyst = None
        self.unit = "GeV"
        self.cutsDict = {}
        self.files = []
        self.treeName = ''
        self.weight = 1.0

    def buildHisto(self,binValues,region,var):
        """
        Allow user to give bin values eg. for checking stats in papers
        """
        try:
            self.binValues[(region,var)] = binValues
        except AttributeError:
            self.binValues = {}
            self.binValues[(region,var)] = binValues
        if not self.isData:
            self.histoName = "h"+self.name+"Nom_"+region+"_obs_"+var
        else:
            self.histoName = "h"+self.name+"_"+region+"_obs_"+var
        configMgr.hists[self.histoName] = TH1F(self.histoName,self.histoName,len(self.binValues[(region,var)]),0.,float(len(self.binValues[(region,var)])))
        for (iBin,val) in enumerate(self.binValues[(region,var)]):
            configMgr.hists[self.histoName].SetBinContent(iBin+1,val)

    def buildStatErrors(self,binStatErrors,region,var):
        """
        Allow user to give bin stat errors eg. for checking stats in papers
        """
        try:
            self.binStatErrors[(region,var)] = binStatErrors
        except AttributeError:
            self.binStatErrors = {}
            self.binStatErrors[(region,var)] = binStatErrors
        if not len(self.binStatErrors[(region,var)]) == len(self.binValues[(region,var)]):
            raise Exception("Length of errors list in region %s and variable %s does not match the nominal histogram!" % (region,var))
        if not self.isData:
            self.histoName = "h"+self.name+"Nom_"+region+"_obs_"+var
        else:
            self.histoName = "h"+self.name+"_"+region+"_obs_"+var
        for (iBin,err) in enumerate(self.binStatErrors[(region,var)]):
            try:
                configMgr.hists[self.histoName].SetBinError(iBin+1,err)        
            except:
                raise Exception("Errors specified without building histogram!")

    def Clone(self):
        newInst = deepcopy(self)
        for (key,val) in self.systDict.items():
            newInst.systDict[key] = val
        return newInst

    def setUnit(self,unit):
        self.unit = unit
        return

    def setCutsDict(self,cutsDict):
        self.cutsDict = cutsDict
        return

    def setData(self,isData=True):
        self.isData = isData
        return

    def setWeight(self,weight=1.0):
        self.weight = weight
        return
        
    def setQCD(self,isQCD=True,qcdSyst="uncorr"):
        self.isQCD = isQCD
        self.qcdSyst = qcdSyst
        return

    def setDiscovery(self,isDiscovery=True):
        self.isDiscovery = isDiscovery
        return

    def setNormByTheory(self,normByTheory=True):
        self.normByTheory = normByTheory
        return

    def setStatConfig(self,statConfig):
        self.statConfig = statConfig
        return

    def setWrite(self,write=True):
        self.write = write
        return

    def setHistoName(self,histoName):
        """
        Set the name of the nominal histogram for this sample
        """
        self.histoName = histoName
        return

    def setTreeName(self,treeName):
        self.treeName = treeName
        return

    def propagateTreeName(self,treeName):
        if self.treeName == '':
            self.treeName = treeName
        ### MAB: Propagate treeName down to systematics of sample
        #for (systName,systList) in self.systDict.items():
        #    for syst in systList:
        #        syst.propagateTreeName(self.treeName)
        #        pass
        return

    def addHistoSys(self,systName,nomName,highName,lowName,includeOverallSys,normalizeSys,symmetrize=True,oneSide=False,samName="",normString=""):
        """
        Add a HistoSys entry using the nominal, high and low histograms, set if to include OverallSys

        If includeOverallSys then extract scale factors

        If normalizeSys then normalize shapes to nominal
        """

        if normalizeSys:
            highIntegral = configMgr.hists["h"+samName+systName+"High_"+normString+"Norm"].Integral()
            lowIntegral = configMgr.hists["h"+samName+systName+"Low_"+normString+"Norm"].Integral()
            nomIntegral = configMgr.hists["h"+samName+"Nom_"+normString+"Norm"].Integral()

            try:
                high = highIntegral / nomIntegral
                low = lowIntegral / nomIntegral
            except ZeroDivisionError:
                print "ERROR: generating HistoSys for %s syst=%s nom=%g high=%g low=%g remove from fit." % (nomName,systName,nomIntegral,highIntegral,lowIntegral)
                return

            configMgr.hists[highName+"Norm"] = configMgr.hists[highName].Clone(highName+"Norm")
            configMgr.hists[lowName+"Norm"] = configMgr.hists[lowName].Clone(lowName+"Norm")

            try:
                configMgr.hists[highName+"Norm"].Scale(1./high)
                configMgr.hists[lowName+"Norm"].Scale(1./low)

            except ZeroDivisionError:
                print "ERROR: generating HistoSys for %s syst=%s nom=%g high=%g low=%g remove from fit." % (nomName,systName,nomIntegral,highIntegral,lowIntegral)
                return
            if oneSide:
                if configMgr.hists[highName].Integral() > configMgr.hists[nomName].Integral():                
                    self.histoSystList.append((systName,highName+"Norm",nomName,configMgr.histCacheFile,"","","",""))
                else:
                    self.histoSystList.append((systName,nomName,lowName+"Norm",configMgr.histCacheFile,"","","",""))
            else:
                self.histoSystList.append((systName,highName+"Norm",lowName+"Norm",configMgr.histCacheFile,"","","",""))
        elif includeOverallSys:
            nomIntegral = configMgr.hists[nomName].Integral()
            lowIntegral = configMgr.hists[lowName].Integral()
            highIntegral = configMgr.hists[highName].Integral()
            try:
                high = highIntegral / nomIntegral
                low = lowIntegral / nomIntegral
            except ZeroDivisionError:
                print "ERROR: generating HistoSys for %s syst=%s nom=%g high=%g low=%g remove from fit." % (nomName,systName,nomIntegral,highIntegral,lowIntegral)
                return

            configMgr.hists[highName+"Norm"] = configMgr.hists[highName].Clone(highName+"Norm")
            configMgr.hists[lowName+"Norm"] = configMgr.hists[lowName].Clone(lowName+"Norm")
            try:
                configMgr.hists[highName+"Norm"].Scale(1./high)
                configMgr.hists[lowName+"Norm"].Scale(1./low)
            except ZeroDivisionError:
                print "ERROR: generating HistoSys for %s syst=%s nom=%g high=%g low=%g keeping in fit (offending histogram should be empty)." % (nomName,systName,nomIntegral,highIntegral,lowIntegral)
            if high<1.0 and low<1.0:
                print "WARNING addHistoSys: high=%f is < 1.0 in %s. Taking symmetric value from low %f %f"%(high,systName,low,2.-low)
                high = 2.-low
            if low>1.0 and high>1.0:
                print "WARNING addHistoSys: low=%f is > 1.0 in %s. Taking symmetric value from high %f %f"%(low,systName,high,2.-high)
                low = 2.-high
            if low<0.:
                print "WARNING addHistoSys: low=%f < 0.0 in %s. Setting low=0.0."%(low,systName)
                low = 0.

            self.histoSystList.append((systName,highName+"Norm",lowName+"Norm",configMgr.histCacheFile,"","","",""))
            self.addOverallSys(systName,high,low)
        else:
            if symmetrize:
                nomIntegral = configMgr.hists[nomName].Integral()
                lowIntegral = configMgr.hists[lowName].Integral()
                highIntegral = configMgr.hists[highName].Integral()
                try:
                    high = highIntegral / nomIntegral
                    low = lowIntegral / nomIntegral
                except ZeroDivisionError:
                    print "ERROR: generating HistoSys for %s syst=%s nom=%g high=%g low=%g remove from fit." % (nomName,systName,nomIntegral,highIntegral,lowIntegral)
                    return
                if high<1.0 and low<1.0:
                    print "WARNING addHistoSys: high=%f is < 1.0 in %s. Taking symmetric value from low %f %f"%(high,systName,low,2.-low)
                    configMgr.hists[highName+"Norm"] = configMgr.hists[highName].Clone(highName+"Norm")
                    try:
                        configMgr.hists[highName+"Norm"].Scale((2.-low)/high)
                    except ZeroDivisionError:
                        print "ERROR: generating HistoSys for %s syst=%s nom=%g high=%g low=%g remove from fit." % (nomName,systName,nomIntegral,highIntegral,lowIntegral)
                        return
                    self.histoSystList.append((systName,highName+"Norm",lowName,configMgr.histCacheFile,"","","",""))
                    if not systName in configMgr.systDict.keys():
                        self.systList.append(systName)
                    return
                if low>1.0 and high>1.0:
                    print "WARNING addHistoSys: low=%f is > 1.0 in %s. Taking symmetric value from high %f %f"%(low,systName,high,2.-high)
                    configMgr.hists[lowName+"Norm"] = configMgr.hists[lowName].Clone(lowName+"Norm")
                    try:
                        configMgr.hists[lowName+"Norm"].Scale((2.-high)/low)
                    except ZeroDivisionError:
                        print "ERROR: generating HistoSys for %s syst=%s nom=%g high=%g low=%g remove from fit." % (nomName,systName,nomIntegral,highIntegral,lowIntegral)
                        return
                    self.histoSystList.append((systName,highName,lowName+"Norm",configMgr.histCacheFile,"","","",""))
                    if not systName in configMgr.systDict.keys():
                        self.systList.append(systName)
                    return
                if low<0.:
                    print "WARNING addHistoSys: low=%f is < 0.0 in %s. Setting negative bins to 0.0."%(low,systName)
                    configMgr.hists[lowName+"Norm"] = configMgr.hists[lowName].Clone(lowName+"Norm")
                    for iBin in xrange(1,configMgr.hists[lowName+"Norm"].GetNbinsX()+1):
                        if configMgr.hists[lowName+"Norm"].GetBinContent(iBin) < 0.:
                            configMgr.hists[lowName+"Norm"].SetBinContent(iBin,0.)
                    self.histoSystList.append((systName,highName,lowName+"Norm",configMgr.histCacheFile,"","","",""))
                    if not systName in configMgr.systDict.keys():
                        self.systList.append(systName)
                        return
                self.histoSystList.append((systName,highName,lowName,configMgr.histCacheFile,"","","",""))
                return
            elif oneSide:
                if configMgr.hists[highName].Integral() > configMgr.hists[nomName].Integral():
                    self.histoSystList.append((systName,highName,nomName,configMgr.histCacheFile,"","","",""))
                #elif configMgr.hists[lowName].Integral() < configMgr.hists[nomName].Integral():
                else:    
                    self.histoSystList.append((systName,nomName,lowName,configMgr.histCacheFile,"","","",""))
                return    
            else:
                self.histoSystList.append((systName,highName,lowName,configMgr.histCacheFile,"","","",""))
                return
        if not systName in configMgr.systDict.keys():
            self.systList.append(systName)


    def addShapeSys(self,systName,nomName,highName,lowName,constraintType="Gaussian"):
        """
        Add a ShapeSys entry using the nominal, high and low histograms
        """
        overallSystHigh = 1.
        overallSystLow = 1.

        configMgr.hists[highName+"Norm"] = configMgr.hists[highName].Clone(highName+"Norm")
        configMgr.hists[lowName+"Norm"]  = configMgr.hists[lowName].Clone(lowName+"Norm")
        configMgr.hists[nomName+"Norm"]  = configMgr.hists[nomName].Clone(nomName+"Norm")

        highIntegral = configMgr.hists[highName].Integral()
        lowIntegral  = configMgr.hists[lowName].Integral()
        nomIntegral  = configMgr.hists[nomName].Integral()

        for iBin in xrange(configMgr.hists[highName+"Norm"].GetNbinsX()+1):
            try:
                configMgr.hists[highName+"Norm"].SetBinContent(iBin, fabs((configMgr.hists[highName+"Norm"].GetBinContent(iBin) / configMgr.hists[nomName].GetBinContent(iBin)) - 1.0) )
                configMgr.hists[highName+"Norm"].SetBinError(iBin,0.)
            except ZeroDivisionError:
                configMgr.hists[highName+"Norm"].SetBinContent(iBin,0.)
                configMgr.hists[highName+"Norm"].SetBinError(iBin,0.)
        for iBin in xrange(configMgr.hists[lowName+"Norm"].GetNbinsX()+1):
            try:
                configMgr.hists[lowName+"Norm"].SetBinContent(iBin, fabs((configMgr.hists[lowName+"Norm"].GetBinContent(iBin) / configMgr.hists[nomName].GetBinContent(iBin)) - 1.0) )
                configMgr.hists[lowName+"Norm"].SetBinError(iBin,0.)
            except ZeroDivisionError:
                configMgr.hists[lowName+"Norm"].SetBinContent(iBin,0.)
                configMgr.hists[lowName+"Norm"].SetBinError(iBin,0.)

        for iBin in xrange(configMgr.hists[nomName+"Norm"].GetNbinsX()+1):
            try:
                configMgr.hists[nomName+"Norm"].SetBinContent(iBin, max( configMgr.hists[highName+"Norm"].GetBinContent(iBin), configMgr.hists[lowName+"Norm"].GetBinContent(iBin) )   )
                if configMgr.verbose > 1:
                    print "!!!!!! shapeSys %s bin %g value %g" % (systName,iBin,configMgr.hists[nomName+"Norm"].GetBinContent(iBin))
                configMgr.hists[nomName+"Norm"].SetBinError(iBin,0.)
            except ZeroDivisionError:
                configMgr.hists[nomName+"Norm"].SetBinContent(iBin,0.)
                configMgr.hists[nomName+"Norm"].SetBinError(iBin,0.)
        
        if not systName in configMgr.systDict.keys():
            self.systList.append(systName)
        return


    def addOverallSys(self,systName,high,low):
        """
        Add an OverallSys entry using the high and low values
        """
        #if high==1.0 and low==1.0:
        #    print "WARNING addOverallSys: high==1.0 and low==1.0... Skipping!"
        #    return

        if high<1.0 and low<1.0:
            highOld=high
            high = 2.0 - low
            print "WARNING addOverallSys: high=%f is < 1.0 in %s. Taking symmetric value from low %f %f"%(highOld,systName,low,high)
            
        if low>1.0 and high>1.0:
            lowOld=low
            low = 2.0 - high
            print "WARNING addOverallSys: low=%f is > 1.0 in %s. Taking symmetric value from high %f %f"%(lowOld,systName,low,high)

        if low<0.0:
            print "WARNING addOverallSys: low=%f is < 0.0 in %s. Setting to low=0.0."%(low,systName)
            low = 0.0

        #low = 1./(2.-low)    

        self.overallSystList.append((systName,high,low))
        if not systName in configMgr.systDict.keys():
            self.systList.append(systName)
        return

    def addNormFactor(self,name,val,high,low,const=False):
        """
        Add a normlization factor
        """
        self.normFactor.append( (name,val,high,low,str(const)) )
        if not name in configMgr.normList:
            configMgr.normList.append(name)
        return

    def setNormFactor(self,name,val,low,high,const=False):
        """
        Set normalization factor
        """
        self.normFactor = []
        self.normFactor.append( (name,val,high,low,str(const)) )
        if not name in configMgr.normList:
            configMgr.normList.append(name)
        return

    def setFileList(self,filelist):
        """
        Set file list for this Sample directly
        """
        self.files = filelist

    def setFile(self,file):
        """
        Set file for this Sample directly
        """
        self.files = [file]

    def propagateFileList(self, fileList):
        """
        Propagate the file list downwards.
        """
        # if we don't have our own file list, use the one given to us
        if self.files == []:
                self.files = fileList
        # we are the leaves of the configmgr->toplevelxml->channel->sample tree,
        # so no propagation necessary

    def addShapeFactor(self,name):
        """
        Bin-by-bin factors to build histogram eg. for data-driven estimates
        """
        self.shapeFactorList.append(name)

    def addSystematic(self,syst):
        """
        Add a systematic to this Sample directly
        """
        if not syst.name in self.systDict.keys():
            self.systDict[syst.name] = []
        self.systDict[syst.name].append(syst)
        return

    def getSystematic(self,systName):
        try:
            return self.systDict[systName]
        except KeyError:
            raise KeyError("Could not find systematic %s in topLevel %s" % (systName,self.name))

    def removeSystematic(self,name):
        """
        Remove a systematic
        """
        del self.systDict[name]

    def clearSystematics(self):
        """
        Remove a systematic
        """
        self.systDict.clear()
        
    def __str__(self):
        """
        Convert instance to XML string
        """
        self.sampleString = "  <Sample Name=\"%s\" HistoName=\"%s\" InputFile=\"%s\" NormalizeByTheory=\"%s\">\n" %(self.name,self.histoName,configMgr.histCacheFile,self.normByTheory)
        if self.statConfig:
            self.sampleString += "    <StatError Activate=\"%s\"/>\n" % (self.statConfig)
        for histoSyst in self.histoSystList:
            self.sampleString += "    <HistoSys Name=\"%s\" HistoNameHigh=\"%s\" HistoNameLow=\"%s\" />\n" % (histoSyst[0],histoSyst[1],histoSyst[2])
        for shapeSyst in self.shapeSystList:
            self.sampleString += "    <ShapeSys Name=\"%s\" HistoName=\"%s\" ConstraintType=\"%s\"/>\n" % (shapeSyst[0],shapeSyst[1],shapeSyst[2])
        for overallSyst in self.overallSystList:
            self.sampleString += "    <OverallSys Name=\"%s\" High=\"%g\" Low=\"%g\" />\n" % (overallSyst[0],overallSyst[1],overallSyst[2])
        for shapeFact in self.shapeFactorList:
            self.sampleString += "    <ShapeFactor Name=\"%s\" />\n" % (shapeFact)
        if len(self.normFactor)>0:
            for normFactor in self.normFactor:
                self.sampleString += "    <NormFactor Name=\"%s\" Val=\"%g\" High=\"%g\" Low=\"%g\" Const=\"%s\" />\n" % (normFactor[0],normFactor[1],normFactor[2],normFactor[3],normFactor[4])
                pass
        self.sampleString += "  </Sample>\n\n"
        return self.sampleString
