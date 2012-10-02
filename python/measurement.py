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

    def addConstraintTerm(self, paramName, type, relUnc=None):
        """
        Define the constraint term for a parameter
        """
        self.constraintTermDict[paramName] = (type, relUnc)
