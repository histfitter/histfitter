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
        self.constraint=constraint
        allowedSys = ["histoSys","overallSys","userOverallSys","overallHistoSys","normHistoSys",
                      "shapeSys","histoSysOneSide","normHistoSysOneSide","normHistoSysOneSideSym","userHistoSys","userNormHistoSys",
                      "overallNormHistoSys","overallNormHistoSysOneSide","overallNormHistoSysOneSideSym" ]
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


    def FillUpDownHist(self,lowhigh="",regionString="",normString="",normCuts="",abstract= None,chan=None,sam=None):

        if self.method == "userNormHistoSys" or self.method == "normHistoSys" or self.method == "normHistoSysOneSide" or self.method == "normHistoSysOneSideSym" or self.method == "overallNormHistoSys" or self.method == "overallNormHistoSysOneSide" or self.method == "overallNormHistoSysOneSideSym":
            if not "h"+sam.name+self.name+lowhigh+normString+"Norm" in abstract.hists.keys():
                if sam.normRegions:
                    normString = ""
                    for normReg in sam.normRegions:
                        if not type(normReg[0]) == "list":
                            normList = []
                            normList.append(normReg[0])
                            c = topLvl.getChannel(normReg[1],normList)
                        else:
                            c = topLvl.getChannel(normReg[1],normReg[0])
                        normString += c.regionString

                    if abstract.readFromTree:
                        abstract.hists["h"+sam.name+self.name+lowhigh+normString+"Norm"] = TH1F("h"+sam.name+self.name+lowhigh+normString+"Norm","h"+sam.name+self.name+lowhigh+normString+"Norm",1,0.5,1.5)

                        for normReg in sam.normRegions:
                            if not type(normReg[0]) == "list":
                                normList = []
                                normList.append(normReg[0])
                                c = topLvl.getChannel(normReg[1],normList)
                            else:
                                c = topLvl.getChannel(normReg[1],normReg[0])

                            try:
                                s = c.getSample(sam.name)
                            except:
                                # assume that if no histogram is made, then it is not needed  
                                continue
                                        
                            systNorm = s.getSystematic(self.name)

                            # if the systematic has a dedicated file list - use it
                            if s.name in systNorm.filesHi:
                                filelist = systNorm.filesHi[s.name]
                            else:
                                # otherwise - take the sample file list
                                filelist = s.files
                            if s.name in systNorm.treeHiName:
                                treeName = systNorm.treeHiName[s.name]
                            else:
                                # otherwise - take the default tree name for the sample
                                if self.type == "tree":
                                    treeName = s.treeName + systNorm.high # NM
                                else:
                                    treeName = s.treeName
                            if treeName=='' or treeName==systNorm.high:
                                treeName = s.name+systNorm.high

                            if abstract.verbose > 2:      
                                print "s.name",s.name
                                print "sam.name",sam.name    
                                print "systNorm high",systNorm.high    
                                print "treeName",treeName

                            abstract.prepare.read(treeName, filelist)

                            tempHist = TH1F("temp","temp",1,0.5,1.5)

                            if systNorm.type == "tree":
                                if abstract.verbose > 2:
                                    print "normalization region","".join(normReg[0])
                                    print "normalization cuts",abstract.cutsDict["".join(normReg[0])]
                                    print "current chain",abstract.prepare.currentChainName
                                    print "projecting string",str(abstract.lumiUnits*abstract.outputLumi/abstract.inputLumi)+" * "+"*".join(s.weights)+" * ("+abstract.cutsDict["".join(normReg[0])]+")"
                                abstract.chains[abstract.prepare.currentChainName].Project("temp",abstract.cutsDict["".join(normReg[0])],str(abstract.lumiUnits*abstract.outputLumi/abstract.inputLumi)+" * "+"*".join(s.weights)+" * ("+abstract.cutsDict["".join(normReg[0])]+")")
                                abstract.hists["h"+sam.name+systNorm.name+lowhigh+normString+"Norm"].SetBinContent(1,abstract.hists["h"+sam.name+systNorm.name+lowhigh+normString+"Norm"].GetSum()+tempHist.GetSumOfWeights())
                            elif systNorm.type == "weight":
                                if abstract.verbose > 2:
                                    print "normalization region","".join(normReg[0])
                                    print "normalization cuts",abstract.cutsDict["".join(normReg[0])]
                                    print "current chain",abstract.prepare.currentChainName
                                    print "projecting string",str(abstract.lumiUnits*abstract.outputLumi/abstract.inputLumi)+" * "+"*".join(s.weights)+" * ("+abstract.cutsDict["".join(normReg[0])]+")"
                                abstract.chains[abstract.prepare.currentChainName].Project("temp",abstract.cutsDict["".join(normReg[0])],str(abstract.lumiUnits*abstract.outputLumi/abstract.inputLumi)+" * "+"*".join(s.systDict[systNorm.name].high)+" * ("+abstract.cutsDict["".join(normReg[0])]+")")
                                abstract.hists["h"+s.name+systNorm.name+lowhigh+normString+"Norm"].SetBinContent(1,abstract.hists["h"+s.name+systNorm.name+lowhigh+normString+"Norm"].GetSum()+tempHist.GetSumOfWeights())
                            del tempHist
                    else:
                        abstract.hists["h"+sam.name+self.name+lowhigh+normString+"Norm"] = None
                        abstract.prepare.addHisto("h"+sam.name+self.name+lowhigh+normString+"Norm")
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
