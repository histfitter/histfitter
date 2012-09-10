from ROOT import THStack,TLegend,TCanvas,TFile,std,TH1F
from ROOT import ConfigMgr,FitConfig #this module comes from gSystem.Load("libSusyFitter.so")
from prepareHistos import TreePrepare,HistoPrepare
from copy import deepcopy
import os

from ROOT import gROOT

###############################################
#Systematic is a function which returns an object. This object can be a TreeWeightSystematic or a UserSystematic.
#These classes are derived classes and the Baseclass for both of them is the SystematicBase.
#In TreeWeightSystematic the set of the weights differs for the systematic type tree and weight.
#Therefore there exist the function PrepareWAHforWeight or PrepareWAHforTree.
# All three types of systematics share the "FillUpDownHist" (for the methods "userNormHistoSys" or "normHistoSys") and "tryAddHistos" function in the Baseclass SystematicBase.
###############################################

def replaceSymbols(s):
    s = s.replace("/", "").replace("*", "").replace("(", "").replace(")", "")
    return s


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

        if not constraint == "Gaussian" and not method == "shapeSys":
                raise ValueError("Constraints can only be specified for shapeSys")
        self.constraint = constraint
        allowedSys = ["histoSys", "overallSys", "userOverallSys",
                      "overallHistoSys", "normHistoSys", "shapeSys",
                      "histoSysOneSide", "normHistoSysOneSide", "userHistoSys",
                      "userNormHistoSys"]
        if not self.method in allowedSys:
            raise Exception("Given method %s is not known... use one of %s" % (self.method, allowedSys))

    def Clone(self, name=""):
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

    def setFileList(self, sample, filelist):
        """
        Set file list for this Systematic directly
        """
        self.filesLo[sample] = filelist
        self.filesHi[sample] = filelist

    def setFile(self, sample, file):
        """
        Set a file for this Systematic directly
        """
        self.filesLo[sample] = [file]
        self.filesHi[sample] = [file]

    def setTreeName(self, sampleName, treeName):
        self.treeLoName[sampleName] = treeName
        self.treeHiName[sampleName] = treeName
        return

    def setLoTreeName(self, sampleName, treeName):
        self.treeLoName[sampleName] = treeName
        return

    def setHiTreeName(self, sampleName, treeName):
        self.treeHiName[sampleName] = treeName
        return

    def setHiFileList(self, sample, filelist):
        """
        Set file list for this Systematic directly
        """
        self.filesHi[sample] = filelist
        return

    def setLoFileList(self, sample, filelist):
        """
        Set file list for this Systematic directly
        """
        self.filesLo[sample] = filelist
        return

    def FillUpDownHist(self, lowhigh="", regionString="", normString="",
                       normCuts="", abstract=None, chan=None, sam=None):
        if self.method == "userNormHistoSys" or self.method == "normHistoSys":
            if not "h" + sam.name + self.name + lowhigh + normString + "Norm" in abstract.hists.keys():
                if abstract.readFromTree:
                    abstract.hists["h" + sam.name + self.name + lowhigh + normString + "Norm"] = TH1F("h" + sam.name + self.name + lowhigh + normString + "Norm", "h" + sam.name + self.name + lowhigh + normString + "Norm", 1, 0.5, 1.5)
                    abstract.chains[abstract.prepare.currentChainName].Project("h" + sam.name + self.name + lowhigh + normString + "Norm", normCuts, abstract.prepare.weights + " * (" + normCuts + ")")

                else:
                    abstract.hists["h" + sam.name + self.name + lowhigh + normString + "Norm"] = None
                    abstract.prepare.addHisto("h" + sam.name + self.name + lowhigh + normString + "Norm")
        return

    def tryAddHistos(self, highorlow="", regionString="", normString="",
                     normCuts="", abstract=None, chan=None, sam=None):
        if abstract.verbose > 1:
            print "!!!!!! adding histo", "h" + sam.name + self.name + highorlow + regionString + "_obs_" + replaceSymbols(chan.variableName)
        try:
            abstract.prepare.addHisto("h" + sam.name + self.name + highorlow + regionString + "_obs_" + replaceSymbols(chan.variableName), useOverflow=chan.useOverflowBin, useUnderflow=chan.useUnderflowBin)
        except:
            pass


class TreeWeightSystematic(SystematicBase):
    def __init__(self, name="", nominal=None, high=None, low=None,
                 type="", method="", constraint="Gaussian"):
        SystematicBase.__init__(self, name, nominal, high, low,
                                type, method, constraint)

    def PrepareWAHforWeight(self, regionString="", normString="", normCuts="",
                            abstract=None, chan=None, sam=None):
        highandlow = ["High_", "Low_"]
        weightstemp = abstract.prepare.weights
        for highorlow in highandlow:
            abstract.prepare.weights = weightstemp

            if highorlow == "High_":
                for myw in self.high:
                    if abstract.prepare.weights.find(myw) == -1:
                        abstract.prepare.weights += " * " + myw
            else:
                for myw in self.low:
                    if abstract.prepare.weights.find(myw) == -1:
                        abstract.prepare.weights += " * " + myw

            if abstract.readFromTree:
                treeName = sam.treeName
                if treeName == '':
                    treeName = sam.name + abstract.nomName
                abstract.prepare.read(treeName, sam.files)

            TreeWeightSystematic.tryAddHistos(self, highorlow, regionString,
                                              normString, normCuts, abstract,
                                              chan, sam)
            TreeWeightSystematic.FillUpDownHist(self, highorlow, regionString,
                                                normString, normCuts, abstract,
                                                chan, sam)
            abstract.prepare.weights = weightstemp
        return

    def PrepareWAHforTree(self, regionString="", normString="", normCuts="",
                          abstract=None, chan=None, sam=None):
        highandlow = ["High_", "Low_"]
        weightstemp = abstract.prepare.weights
        for highorlow in highandlow:
            abstract.prepare.weights = weightstemp
            for myw in sam.weights:
                if abstract.prepare.weights.find(myw) == -1:
                    abstract.prepare.weights += " * " + myw

            if abstract.readFromTree:
                if highorlow == "High_":
                    if sam.name in self.filesHi:
                        filelist = self.filesHi[sam.name]
                    else:
                        filelist = sam.files

                    if sam.name in self.treeHiName:
                        treeName = self.treeHiName[sam.name]
                    else:
                        treeName = sam.treeName + self.high

                    if treeName == '' or treeName == self.high:
                        treeName = sam.name + self.high

                    abstract.prepare.read(treeName, filelist)
                else:
                    if sam.name in self.filesLo:
                        filelist = self.filesLo[sam.name]
                    else:
                        filelist = sam.files

                    if sam.name in self.treeLoName:
                        treeName = self.treeLoName[sam.name]
                    else:
                        treeName = sam.treeName + self.low

                    if treeName == '' or treeName == self.low:
                        treeName = sam.name + self.low
                    abstract.prepare.read(treeName, filelist)

            TreeWeightSystematic.tryAddHistos(self, highorlow, regionString,
                                              normString, normCuts, abstract,
                                              chan, sam)
            TreeWeightSystematic.FillUpDownHist(self, highorlow, regionString,
                                                normString, normCuts, abstract,
                                                chan, sam)
            abstract.prepare.weights = weightstemp
        return

    def PrepareWeightsAndHistos(self, regionString="", normString="",
                                normCuts="", abstract=None,
                                chan=None, sam=None):
        if self.type == "weight":
            TreeWeightSystematic.PrepareWAHforWeight(self, regionString,
                                                     normString, normCuts,
                                                     abstract, chan, sam)
        if self.type == "tree":
            TreeWeightSystematic.PrepareWAHforTree(self, regionString,
                                                   normString, normCuts,
                                                   abstract, chan, sam)
        return


class UserSystematic(SystematicBase):
    def __init__(self, name="", nominal=None, high=None, low=None, type="",
                 method="", constraint="Gaussian"):
        SystematicBase.__init__(self, name, nominal, high, low, type,
                                method, constraint)

    def PrepareWeightsAndHistos(self, regionString="", normString="",
                                normCuts="", abstract=None,
                                chan=None, sam=None):
        highandlow = ["High_", "Low_"]
        weightstemp = abstract.prepare.weights
        for highorlow in highandlow:
            abstract.prepare.weights = weightstemp
            abstract.prepare.weights += " * " + " * ".join(sam.weights)

            if abstract.readFromTree:
                treeName = sam.treeName
                if treeName == '':
                    treeName = sam.name + abstract.nomName
                abstract.prepare.read(treeName, sam.files)
            else:
                UserSystematic.tryAddHistos(self, highorlow, regionString,
                                            normString, normCuts, abstract,
                                            chan, sam)

            UserSystematic.FillUpDownHist(self, highandlow, regionString,
                                          normString, normCuts, abstract,
                                          chan, sam)
        return


## This is the control function. The function ensures the backward compability. It returns an object
def Systematic(name="", nominal=None, high=None, low=None,
               type="", method="", constraint="Gaussian"):
    if type == "weight" or type == "tree" or type == "user":
        if type == "weight" or type == "tree":
            return TreeWeightSystematic(name, nominal, high, low,
                                        type, method, constraint)
        else:
            return UserSystematic(name, nominal, high, low,
                                        type, method, constraint)
    else:
        raise Exception("type unknown")
