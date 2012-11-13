import ROOT
from ROOT import TFile,TMath,RooRandom,TH1,TH1F
from ROOT import kBlack,kWhite,kGray,kRed,kPink,kMagenta,kViolet,kBlue,kAzure,kCyan,kTeal,kGreen,kSpring,kYellow,kOrange,kDashed,kSolid,kDotted
from os import system
from math import fabs
from channel import Channel
from sample import Sample


import generateToys

TH1.SetDefaultSumw2(True)

from copy import deepcopy,copy
from configManager import configMgr


class Measurement(object):
    """
    Class to define measurements in the top-level xml
    """

    def __init__(self, name, lumi, lumiErr):
        """
        Store configuration, add to top level list of measurements,
        specify lumi parameters and if run in exportOnly mode
        """
        self.name = name
        self.lumi = lumi
        self.lumiErr = lumiErr
        self.binLow = 0
        self.binHigh = 50
        self.mode = "comb"
        self.exportOnly = True
        self.poiList = []
        self.constraintTermDict = {}
        self.paramSettingDict = {}

    def Clone(self, newName=""):
        if newName == "":
            newName = self.name
        newMeas = deepcopy(self)
        newMeas.name = newName
        return newMeas

    def addPOI(self, poi):
        """
        Add a parameter of interest
        """
        self.poiList.append(poi)

    def addParamSetting(self, paramName, const, val=None):
        """
        Define the settings for a parameter
        """
        self.paramSettingDict[paramName] = (const, val)

    def addConstraintTerm(self,paramName,type,relUnc=None):
        """
        Define the constraint term for a parameter
        """
        self.constraintTermDict[paramName] = (type,relUnc)

    def createHistFactoryObject(self, prefix):
        m = ROOT.RooStats.HistFactory.Measurement(self.name)
        m.SetOutputFilePrefix( "./results/"+prefix )
        m.SetPOI( (self.poiList)[0] )
        
        m.SetLumi(self.lumi)
        m.SetLumiRelErr(self.lumiErr)
        m.SetExportOnly(self.exportOnly)

        m.SetBinLow(self.binLow)
        m.SetBinHigh(self.binHigh)

        for (param, setting) in self.paramSettingDict.iteritems():
            #setting is array [const, value]
            if not setting[0]: 
                continue #means this param is not const
                
            m.AddConstantParam(param)
            if setting[1]:
                m.SetParamValue(param, setting[1])

        for (syst, constraint) in self.constraintTermDict.iteritems():
            #constraint is array [type, relUnc]; latter only allowed for Gamma and LogNormal
            if constraint[0] == "Gamma":
                if constraint[1] is not None:
                    m.AddGammaSyst(syst, constraint[1])
                else:
                    m.AddGammaSyst(syst)
            elif constraint[0] == "LogNormal":
                if constraint[1] is not None:
                    m.AddLogNormSyst(syst, constraint[1])
                else:
                    m.AddLogNormSyst(syst)
            elif constraint[0] == "Uniform":
                m.AddUniformSyst(syst)    
            elif constraint[0] == "NoConstraint":
                m.AddNoSyst(syst)
       
        return m

    def __str__(self):
        """
        Convert instance to an XML string
        """
        measurementString = "  <Measurement Name=\"%s\" Lumi=\"%g\" LumiRelErr=\"%g\" BinLow=\"%d\" BinHigh=\"%d\" ExportOnly=\"%s\">\n" % (self.name,self.lumi,self.lumiErr,self.binLow,self.binHigh,str(self.exportOnly))
        for (iPOI, poi) in enumerate(self. poiList):
            measurementString += "    <POI>%s</POI>\n" % (poi)
        for (param, setting) in self.paramSettingDict. iteritems():
            if setting[0]:
                if not setting[1] == None:
                    measurementString += "    <ParamSetting Const=\"True\" Val=\"%g\">%s</ParamSetting>\n" % (setting[1], param)
                else:
                    measurementString += "    <ParamSetting Const=\"True\">%s</ParamSetting>\n" % (param)
            else:
                if not setting[1] == None:
                    measurementString += "    <ParamSetting Const=\"False\" Val=\"%g\">%s</ParamSetting>\n" % (setting[1], param)
                else:
                    measurementString += "    <ParamSetting Const=\"False\">%s</ParamSetting>\n" % (param)
        for (param, constraint) in self.constraintTermDict.iteritems():
            if not constraint[1] == None:
                measurementString += "    <ConstraintTerm Type=\"%s\" RelativeUncertainty=\"%g\">%s</ConstraintTerm>\n" % (constraint[0], constraint[1], param)
            else:
                measurementString += "    <ConstraintTerm Type=\"%s\">%s</ConstraintTerm>\n" % (constraint[0], param)
        measurementString += "  </Measurement>\n\n"
        return measurementString
