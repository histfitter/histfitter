from copy import deepcopy

class Systematic:
    def __init__(self,name="",nominal=None,high=None,low=None,type="",method="",constraint="Gaussian"):
        self.name = name # Name to give the systematic
        self.type = type # Is the systematic weights based or tree based?
        self.method = method # What HistFactory method to use?
        self.nominal = nominal # What is the nominal tree name or weights list?
        self.high = high # What is the +1sig tree name or weights list?
        self.low = low # What is the -1sig tree name or weights list?
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
        allowedSys = ["histoSys","overallSys","userOverallSys","overallHistoSys","normHistoSys","shapeSys","histoSysOneSide","normHistoSysOneSide","userHistoSys","userNormHistoSys"]
        if not self.method in allowedSys:
            raise Exception("Given method %s is not known... use one of %s" % (self.method,allowedSys))

    def Clone(self,name=""):
        newSyst = deepcopy(self)
        if not name == "":
            newSyst.name = name
        return newSyst

    def Reset(self):
        self.nFound = 0
        return

    def mergeSamples(self,sampleList):
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

    def setFileList(self,sample,filelist):
        """
        Set file list for this Systematic directly
        """
        self.filesLo[sample] = filelist
        self.filesHi[sample] = filelist

    def setFile(self,sample,file):
        """
        Set a file for this Systematic directly
        """
        self.filesLo[sample] = [file]
        self.filesHi[sample] = [file]

    def setTreeName(self,sampleName,treeName):
        self.treeLoName[sampleName] = treeName
        self.treeHiName[sampleName] = treeName
        return

    def setLoTreeName(self,sampleName,treeName):
        self.treeLoName[sampleName] = treeName
        return

    def setHiTreeName(self,sampleName,treeName):
        self.treeHiName[sampleName] = treeName
        return

    def setHiFileList(self,sample,filelist):
        """
        Set file list for this Systematic directly
        """
        self.filesHi[sample] = filelist
        return

    def setLoFileList(self,sample,filelist):
        """
        Set file list for this Systematic directly
        """
        self.filesLo[sample] = filelist
        return
    
