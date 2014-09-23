"""
 **********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : Measurement                                                           *
 * Created: November 2012                                                         *
 *                                                                                *
 * Description:                                                                   *
 *      Class to define a measurement (HistFactory object) that contains          *
 *         the POI, special constraints and settings for parameters               *
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
from ROOT import TFile,TMath,RooRandom,TH1,TH1F
from ROOT import kBlack,kWhite,kGray,kRed,kPink,kMagenta,kViolet,kBlue,kAzure,kCyan,kTeal,kGreen,kSpring,kYellow,kOrange,kDashed,kSolid,kDotted

TH1.SetDefaultSumw2(True)

from copy import deepcopy

class Measurement(object):
    """
    Class to define measurements in a fit configuration
    """

    def __init__(self, name, lumi, lumiErr):
        """
        Store configuration, add to top level list of measurements,
        specify lumi parameters and if run in exportOnly mode

        @param name Name of the measurement
        @param lumi Luminosity to use
        @param lumiError Relative error on the luminosity
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
        """
        Copy the measurement to a new one

        @param newName Optional new name; if empty, the current name is used
        """
        if newName == "":
            newName = self.name
        newMeas = deepcopy(self)
        newMeas.name = newName
        return newMeas

    def addPOI(self, poi):
        """
        Add a parameter of interest

        @param poi The parameter to add
        """
        self.poiList.append(poi)

    def addParamSetting(self, paramName, const, val=None):
        """
        Define the settings for a parameter

        @param paramName Name of the parameter
        @param const Boolean that determines whether the parameter is constant or not
        @param val The default value of the parameter
        """
        self.paramSettingDict[paramName] = (const, val)

    def addConstraintTerm(self, paramName, type, relUnc=None):
        """
        Define the constraint term for a parameter

        @param paramName Name of the parameter
        @param type Type of constraint
        @param relUnc Relative uncertainty to add
        """
        self.constraintTermDict[paramName] = (type,relUnc)

    def createHistFactoryObject(self, prefix):
        """
        Create a HistFactory object for this measurement
        
        @param prefix Output prefix to use; will use "./results/<prefix>" to store output files
        """

        m = ROOT.RooStats.HistFactory.Measurement(self.name)
        m.SetOutputFilePrefix("./results/%s" % prefix)
        m.SetPOI(self.poiList[0])
        
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
            measurementString += "    <POI>%s</POI>\n" % poi

        for (param, setting) in self.paramSettingDict. iteritems():
            if setting[0]:
                if not setting[1] is None:
                    measurementString += "    <ParamSetting Const=\"True\" Val=\"%g\">%s</ParamSetting>\n" % (setting[1], param)
                else:
                    measurementString += "    <ParamSetting Const=\"True\">%s</ParamSetting>\n" % param
            else:
                if not setting[1] is None:
                    measurementString += "    <ParamSetting Const=\"False\" Val=\"%g\">%s</ParamSetting>\n" % (setting[1], param)
                else:
                    measurementString += "    <ParamSetting Const=\"False\">%s</ParamSetting>\n" % param

        for (param, constraint) in self.constraintTermDict.iteritems():
            if not constraint[1] is None:
                measurementString += "    <ConstraintTerm Type=\"%s\" RelativeUncertainty=\"%g\">%s</ConstraintTerm>\n" % (constraint[0], constraint[1], param)
            else:
                measurementString += "    <ConstraintTerm Type=\"%s\">%s</ConstraintTerm>\n" % (constraint[0], param)

        measurementString += "  </Measurement>\n\n"

        return measurementString
