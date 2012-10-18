from ROOT import TFile,TMath,RooRandom,TH1,TH1F
from ROOT import kBlack,kWhite,kGray,kRed,kPink,kMagenta,kViolet,kBlue,kAzure,kCyan,kTeal,kGreen,kSpring,kYellow,kOrange,kDashed,kSolid,kDotted
from os import system
from math import fabs
from chanxml import ChannelXML
from smpl import Sample


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
        self.exportOnly = "True"
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

    def __str__(self):
        """
        Convert instance to an XML string
        """
        measurementString = "  <Measurement Name=\"%s\" Lumi=\"%g\" LumiRelErr=\"%g\" BinLow=\"%d\" BinHigh=\"%d\" ExportOnly=\"%s\">\n" % (self.name,self.lumi,self.lumiErr,self.binLow,self.binHigh,self.exportOnly)
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
