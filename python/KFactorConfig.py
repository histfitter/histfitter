
################################################################
## In principle all you have to setup is defined in this file ##
################################################################

from configManager import configMgr
from ROOT import kBlack,kRed,kBlue,kGreen,kYellow,kWhite
from configWriter import TopLevelXML,Measurement,ChannelXML

# First define HistFactory attributes
configMgr.analysisName = "KFactorFit" # Name to give the analysis

# Scaling calculated by outputLumi / inputLumi
configMgr.inputLumi = 0.001 # Luminosity of input histograms
configMgr.outputLumi = 0.001 # Luminosity required for output histograms

configMgr.outputFileName = "results/KFactorFitAnalysisOutput.root"


# setting the parameters of the hypothesis test
#configMgr.doHypoTest=True
#configMgr.nTOYs=100
#configMgr.calculatorType=0
#configMgr.testStatType=3

# Set the files to read from
if configMgr.readFromTree:
    configMgr.inputFileNames = []
else:
    configMgr.inputFileNames = ["data/KFactorFit.root"]


# List of samples and their plotting colours
#sampleList = ["top","w","Data"]
sampleList = ["top_Np0","top_Np1","top_Np2","top_Np3","top_Np4","top_Np5","w_Np3","w_Np4","w_Np5","qcd","bg","signal","Data"]
#configMgr.plotColours = [kGreen,kRed,kYellow,kBlue,kBlack]
#Configmgr.plotColours = [kGreen,kRed,kYellow,kBlack]
#configMgr.plotColours = [kGreen,kRed,kBlack]
configMgr.plotColours = [100,97,94,92,88,85,59,63,67,71,3,17,8,kBlack]

# List of systematics
configMgr.nomName = "" #"_NoSys"
#configMgr.systDict = {}
configMgr.systDict = {"JES":{"isTree":False,"high":"_JESup","low":"_JESdown","isTheory":False}}
                      #"QScaleW":{"isTree":False,"high":qScaleWHighWeights,"low":qScaleWLowWeights,"isTheory":True},
                      #"KtScaleW":{"isTree":False,"high":ktScaleWHighWeights,"low":ktScaleWLowWeights,"isTheory":True},
                      #"QScaleTop":{"isTree":False,"high":qScaleTopHighWeights,"low":qScaleTopLowWeights,"isTheory":True),
                      #"KtScaleTop":{"isTree":False,"high":ktScaleTopHighWeights,"low":ktScaleTopLowWeights,"isTheory":True)}
                      #"Theory":{"isTree":False,"high":theoryHighWeights,"low":theoryLowWeights,"isTheory":True)}
                      #"bTag":{"isTree":False,"high":bTagHighWeights,"low":bTagLowWeights,"isTheory":False}} # Example of weight-based systematic - not implemented

#this is only a place-holder currently with no effect. Feature will be implemented soon.
#configMgr.signalChannels=["meffChannel"]
#configMgr.validationChannels=["cutsChannel"]
#configMgr.bkgConstrainChannels=["cutsBChannel"]
#

#Parameters of the Measurement
measName = "BasicMeasurement"
measLumi = 1.
measLumiError = 0.037

NjetRegion = ["Njet"]
NjetNBins = 80
NjetBinLow = 1.
NjetBinHigh = 81.

#Create TopLevelXML objects
myTopLvl = configMgr.addTopLevelXML("KFactorFit")
#myTopLvl.statErrThreshold=0.5
myTopLvl.statErrThreshold=None
myTopLvl.addSamples(sampleList)
myTopLvl.setSignalSample("signal")
#Add Measurement
meas=myTopLvl.addMeasurement(measName,measLumi,measLumiError)
meas.addPOI("mu_SIG")
#meas.addConstraintTerm("mu_top_Np0","NoConstraint",1)
#meas.addConstraintTerm("mu_top_Np1","NoConstraint",1)
#meas.addConstraintTerm("mu_top_Np2","NoConstraint",1)
#meas.addConstraintTerm("mu_top_Np3","NoConstraint",1)
#meas.addConstraintTerm("mu_w_Np3","NoConstraint",1)
#meas.addConstraintTerm("mu_w_Np4","NoConstraint",1)
#meas.addConstraintTerm("mu_w_Np5","NoConstraint",1)
#meas.addConstraintTerm("mu_bg","NoConstraint",1)
#meas.addConstraintTerm("mu_qcd","NoConstraint",1)
OneEleChannel = myTopLvl.addChannel("OneEle",NjetRegion,NjetNBins,NjetBinLow,NjetBinHigh)
OneMuChannel = myTopLvl.addChannel("OneMu",NjetRegion,NjetNBins,NjetBinLow,NjetBinHigh)
EleEleChannel = myTopLvl.addChannel("EleEle",NjetRegion,NjetNBins,NjetBinLow,NjetBinHigh)
EleMuChannel = myTopLvl.addChannel("EleMu",NjetRegion,NjetNBins,NjetBinLow,NjetBinHigh)
MuMuChannel = myTopLvl.addChannel("MuMu",NjetRegion,NjetNBins,NjetBinLow,NjetBinHigh)
#  LocalWords:  Configmgr
