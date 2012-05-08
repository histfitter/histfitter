
################################################################
## In principle all you have to setup is defined in this file ##
################################################################

from configManager import configMgr
from ROOT import kBlack,kRed,kBlue,kGreen,kYellow,kWhite,kPink
from configWriter import TopLevelXML,Measurement,ChannelXML,Sample
from systematic import Systematic

# First define HistFactory attributes
configMgr.analysisName = "2lepSusyFitterAnalysis" # Name to give the analysis
configMgr.outputFileName = "results/2lepSusyFitterAnalysisOutput.root"

# Scaling calculated by outputLumi / inputLumi
configMgr.inputLumi = 4.713
configMgr.outputLumi = 4.713
configMgr.setLumiUnits("fb-1")

# My input Trees are already scaled to lumi, so these parameters are meaningless currently
configMgr.inputLumi = 1.0 # Luminosity of input histograms
configMgr.outputLumi = 1.0 # Luminosity required for output histograms


#configMgr.doHypoTest=True
#configMgr.nTOYs=1000
configMgr.calculatorType=2
#configMgr.testStatType=3
#configMgr.nPoints=20

# Set the files to read from
if configMgr.readFromTree:
# I've provided trees for ee, emu, mumu using 4.7fb data and a mixture of mc11b and mc11c MonteCarlo
# ln -s /afs/cern.ch/atlas/groups/susy/1lepton/samples/SusyFitterTree_EleEle_NoSyst_rel17_NoAlpGenTop.root data/SusyFitterTree_EleEle_NoSyst.root etc
#    configMgr.inputFileNames = ["data/SusyFitterTree_EleEle_NoSyst.root","data/SusyFitterTree_EleMu_NoSyst.root","data/SusyFitterTree_MuMu_NoSyst.root"]
    configMgr.inputFileNames = ["data/SusyFitterTree_EleEle.root","data/SusyFitterTree_EleMu.root","data/SusyFitterTree_MuMu.root"]
else:
    configMgr.inputFileNames = ["data/"+configMgr.analysisName+".root"]

# AnalysisType corresponds to ee,mumu,emu as I want to split these channels up

# Map regions to cut strings
configMgr.cutsDict = {"cut0":"met>0.",
                      "cut1":"nJet>0. && jet1Pt > 50",
                      "cut2":"nJet>1. && jet2Pt > 50",
                      "cut3":"nJet>1. && jet2Pt > 50 && met>50",
                       "TR_ee":"(mll<80 || mll>100) && met > 30 && met < 80 && jet2Pt > 30 && nBJet > 0 && AnalysisType==3",
                       "TR_mumu":"(mll<80 || mll>100) && met > 30 && met < 80 && jet2Pt > 30 && nBJet > 0 && AnalysisType==4",
                       "TR_emu":"(mll<80 || mll>100) && met > 30 && met < 80 && jet2Pt > 30 && nBJet > 0 && AnalysisType==5",
#                       "ZR_ee":"mll>75 && mll<105 && jet2Pt > 20 && AnalysisType==3",
#                       "ZR_mumu":"mll>75 && mll<105  && jet2Pt > 20 && AnalysisType==4",
                       "ZR_ee":"mll>75 && mll<105  && AnalysisType==3",
                       "ZR_mumu":"mll>75 && mll<105  && AnalysisType==4",
# The cuts below are softer than the actual SR foreseen, just for testing purposes
                      "SR_ee":"met > 200 && nJet>=2 && jet2Pt > 100 && AnalysisType==3",
                      "SR_mumu":"met > 200 && nJet>=2 && jet2Pt > 100 && AnalysisType==4",
                      "SR_emu":"met > 200 && nJet>=2 && jet2Pt > 100 && AnalysisType==5"
##                      "SR":"met > 300 && nJet>=2 && jet2Pt > 200"
                      }


# List of samples and their plotting colours
#sampleList = ["Top","Z_Np0","Z_Np1","Z_Np2","Z_Np3","Z_Np4","Z_Np5","BG","Data"]
#sampleList = ["BG","Top","Z_Np2","Z_Np3","Z_Np4","Z_Np5","Data"]
#sampleList = ["BG","Top","WZ_Np2","WZ_Np3","WZ_Np4","WZ_Np5","Data"]
#sampleList = ["Top","Z_Np2","Z_Np3","Z_Np4","Z_Np5","Data"]
#configMgr.plotColours = [kGreen,100,97,94,92,59,63,kRed,kBlack]
#configMgr.plotColours = [63,kGreen,100,97,94,92,59,kRed,kBlack]
#configMgr.plotColours = [kGreen,94,92,59,63,kRed,kBlack]

## # Tuples of weights 
#configMgr.weights = ("genWeight","eventWeight","leptonWeight","triggerWeight","avgMuWeight","muWeight")
configMgr.weights = ("genWeight","eventWeight","leptonWeight","triggerWeight")

# Example of Q scale systematic
qScaleWHighWeights = ("genWeight","qfacUpWeightW","eventWeight","leptonWeight","triggerWeight")
qScaleWLowWeights = ("genWeight","qfacDownWeightW","eventWeight","leptonWeight","triggerWeight")
qScaleTopHighWeights = ("genWeight","qfacUpWeightTop","eventWeight","leptonWeight","triggerWeight")
qScaleTopLowWeights = ("genWeight","qfacDownWeightTop","eventWeight","leptonWeight","triggerWeight")

# Example of Kt scale systematic
ktScaleWHighWeights = ("genWeight","ktfacUpWeightW","eventWeight","leptonWeight","triggerWeight")
ktScaleWLowWeights = ("genWeight","ktfacDownWeightW","eventWeight","leptonWeight","triggerWeight")
ktScaleTopHighWeights = ("genWeight","ktfacUpWeightTop","eventWeight","leptonWeight","triggerWeight")
ktScaleTopLowWeights = ("genWeight","ktfacDownWeightTop","eventWeight","leptonWeight","triggerWeight")


# List of systematics
configMgr.nomName = "_NoSys"
#cdconfigMgr.systDict = { }
# Systematics will be included in the next iteration
#configMgr.systDict = {"JES":{"isTree":True,"high":"_JESup","low":"_JESdown","isTheory":False}}
                      #"QScaleW":{"isTree":False,"high":qScaleWHighWeights,"low":qScaleWLowWeights,"isTheory":True},
                      #"KtScaleW":{"isTree":False,"high":ktScaleWHighWeights,"low":ktScaleWLowWeights,"isTheory":True}
                      #"QScaleTop":{"isTree":False,"high":qScaleTopHighWeights,"low":qScaleTopLowWeights,"isTheory":True),
                      #"KtScaleTop":{"isTree":False,"high":ktScaleTopHighWeights,"low":ktScaleTopLowWeights,"isTheory":True)}
                      #"bTag":{"isTree":False,"high":bTagHighWeights,"low":bTagLowWeights,"isTheory":False}} # Example of weight-based systematic - not implemented

#Parameters of the Measurement
measName = "BasicMeasurement"
measLumi = 1.
measLumiError = 0.037

# Combined histos, deprecated

# nJetTopRegions = ["TR_ee","TR_emu","TR_mumu"]
# nJetTopNBins = 3
# nJetTopBinLow = 2
# nJetTopBinHigh = 5

# nJetZRegions = ["ZR_ee","ZR_mumu"]
# nJetZNBins = 3
# nJetZBinLow = 2
# nJetZBinHigh = 5

# nJet Binning for Top Control region, useful as soon as Alpgen TTbar available

# nJetTopeeRegions = ["TR_ee"]
# nJetTopeeNBins = 10
# nJetTopeeBinLow = 0
# nJetTopeeBinHigh = 10

# nJetTopemuRegions = ["TR_emu"]
# nJetTopemuNBins = 10
# nJetTopemuBinLow = 0
# nJetTopemuBinHigh = 10

# nJetTopmumuRegions = ["TR_mumu"]
# nJetTopmumuNBins = 10
# nJetTopmumuBinLow = 0
# nJetTopmumuBinHigh = 10

# List of samples and their plotting colours
topSample0 = Sample("Top",kGreen)
topSample0.setNormFactor("mu_Top",1.,0.,5.)
wzSample0 = Sample("WZ_Np0",kRed-10)
wzSample0.setNormFactor("mu_WZNp0",1.,0.,5.)
wzSample1 = Sample("WZ_Np1",kRed-9)
wzSample1.setNormFactor("mu_WZNp1",1.,0.,5.)
wzSample2 = Sample("WZ_Np2",kRed-8)
wzSample2.setNormFactor("mu_WZNp2",1.,0.,5.)
wzSample3 = Sample("WZ_Np3",kRed-7)
wzSample3.setNormFactor("mu_WZNp3",1.,0.,5.)
wzSample4 = Sample("WZ_Np4",kRed-6)
wzSample4.setNormFactor("mu_WZNp4",1.,0.,5.)
wzSample5 = Sample("WZ_Np5",kRed-5)
wzSample5.setNormFactor("mu_WZNp5",1.,0.,5.)
bgSample = Sample("BG",kYellow)
bgSample.setNormFactor("mu_BG",1.,0.,5.)
#qcdSample = Sample("QCD",kBlue)
#qcdSample.setQCD()
dataSample = Sample("Data",kBlack)
dataSample.setData()

nJetTopeeRegions = ["TR_ee"]
nJetTopeeNBins = 1
nJetTopeeBinLow = 0.5
nJetTopeeBinHigh = 1.5

nJetTopemuRegions = ["TR_emu"]
nJetTopemuNBins = 1
nJetTopemuBinLow = 0.5
nJetTopemuBinHigh = 1.5

nJetTopmumuRegions = ["TR_mumu"]
nJetTopmumuNBins = 1
nJetTopmumuBinLow = 0.5
nJetTopmumuBinHigh = 1.5


nJetZmumuRegions = ["ZR_mumu"]
nJetZmumuNBins = 10
nJetZmumuBinLow = 0
nJetZmumuBinHigh = 10

nJetZeeRegions = ["ZR_ee"]
nJetZeeNBins = 10
nJetZeeBinLow = 0
nJetZeeBinHigh = 10

ZptZmumuRegions = ["ZR_mumu"]
ZptZmumuNBins = 16
ZptZmumuBinLow = 0
ZptZmumuBinHigh = 400

ZptZeeRegions = ["ZR_ee"]
ZptZeeNBins = 16
ZptZeeBinLow = 0
ZptZeeBinHigh = 400


# currently one combined region. I guess this should be split up as well?

meffRegions = ["SR_ee","SR_emu","SR_mumu"]
meffNBins = 1
meffBinLow = 0.5
meffBinHigh = 1.5

#Create TopLevelXML objects
bkgOnly = configMgr.addTopLevelXML("dilepton_bkgonly")
#bkgOnly.statErrThreshold=0.5
bkgOnly.statErrThreshold=None
#bkgOnly.addSamples(sampleList)
#bkgOnly.addSamples([topSample0,topSample1,topSample2,topSample3,topSample4,topSample5,wzSample3,wzSample4,wzSample5,bgSample,qcdSample,dataSample])
bkgOnly.addSamples([topSample0,wzSample0,wzSample1,wzSample2,wzSample3,wzSample4,wzSample5,bgSample,dataSample])
#Add Measurement
meas=bkgOnly.addMeasurement(measName,measLumi,measLumiError)
meas.addPOI("mu_SIG")
# Fix Background 
meas.addParamSetting("mu_BG","const",1.0)
# Fix Lumi, currently seems to be buggy otherwise with this setup
#meas.addParamSetting("Lumi","const",1.0)
# just 1 bin for Top
nJetTopeeChannel=bkgOnly.addChannel("cuts",nJetTopeeRegions,nJetTopeeNBins,nJetTopeeBinLow,nJetTopeeBinHigh)
nJetTopemuChannel=bkgOnly.addChannel("cuts",nJetTopemuRegions,nJetTopemuNBins,nJetTopemuBinLow,nJetTopemuBinHigh)
nJetTopmumuChannel=bkgOnly.addChannel("cuts",nJetTopmumuRegions,nJetTopmumuNBins,nJetTopmumuBinLow,nJetTopmumuBinHigh)
# nJet for Z
nJetZeeChannel=bkgOnly.addChannel("nJet",nJetZeeRegions,nJetZeeNBins,nJetZeeBinLow,nJetZeeBinHigh)
nJetZmumuChannel=bkgOnly.addChannel("nJet",nJetZmumuRegions,nJetZmumuNBins,nJetZmumuBinLow,nJetZmumuBinHigh)
ZptZeeChannel=bkgOnly.addChannel("Zpt",ZptZeeRegions,ZptZeeNBins,ZptZeeBinLow,ZptZeeBinHigh)
ZptZmumuChannel=bkgOnly.addChannel("Zpt",ZptZmumuRegions,ZptZmumuNBins,ZptZmumuBinLow,ZptZmumuBinHigh)
ZptZeeChannel.useOverflowBin=True
ZptZmumuChannel.useOverflowBin=True
bkgOnly.setBkgConstrainChannels([nJetTopeeChannel])
bkgOnly.setBkgConstrainChannels([nJetTopemuChannel])
bkgOnly.setBkgConstrainChannels([nJetTopmumuChannel])
bkgOnly.setBkgConstrainChannels([nJetZeeChannel])
bkgOnly.setBkgConstrainChannels([nJetZmumuChannel])
bkgOnly.setBkgConstrainChannels([ZptZeeChannel])
bkgOnly.setBkgConstrainChannels([ZptZmumuChannel])
# sig="GMSB_3_2d_50_250_3_5_1_1"
# sigSample = Sample(sig,kPink)
# sigSample.setNormByTheory()
# sigSample.setNormFactor("mu_SIG",0.,0.,5.)
# bkgOnly.addSamples(sigSample)
# bkgOnly.setSignalSample(sigSample)
# meffChannel = bkgOnly.addChannel("cuts",meffRegions,meffNBins,meffBinLow,meffBinHigh)
# meffChannel.useOverflowBin=True
# bkgOnly.setSignalChannels(meffChannel)

# ToDo: Add (meaningful) validation regions


#Exclusion fits (currently SU4 only, will include GMSB "soon")

#sigSamples=["SU4"]
sigSamples=[
#    "GMSB_3_2d_20_250_3_2_1_1",	
    "GMSB_3_2d_20_250_3_5_1_1",	
    "GMSB_3_2d_20_250_3_10_1_1",	
    "GMSB_3_2d_20_250_3_15_1_1",	
    "GMSB_3_2d_20_250_3_20_1_1",	
    "GMSB_3_2d_20_250_3_27_1_1",	
    "GMSB_3_2d_30_250_3_2_1_1",	
    "GMSB_3_2d_30_250_3_5_1_1",	
    "GMSB_3_2d_30_250_3_10_1_1",	
    "GMSB_3_2d_30_250_3_15_1_1",	
    "GMSB_3_2d_30_250_3_20_1_1",	
    "GMSB_3_2d_30_250_3_30_1_1",	
    "GMSB_3_2d_30_250_3_36_1_1",	
    "GMSB_3_2d_35_250_3_2_1_1",	
    "GMSB_3_2d_35_250_3_5_1_1",	
    "GMSB_3_2d_35_250_3_10_1_1",	
    "GMSB_3_2d_35_250_3_15_1_1",	
    "GMSB_3_2d_35_250_3_20_1_1",	
    "GMSB_3_2d_35_250_3_25_1_1",	
    "GMSB_3_2d_35_250_3_30_1_1",	
    "GMSB_3_2d_35_250_3_35_1_1",	
    "GMSB_3_2d_35_250_3_40_1_1",	
    "GMSB_3_2d_35_250_3_42_1_1",	
    "GMSB_3_2d_40_250_3_2_1_1",	
    "GMSB_3_2d_40_250_3_5_1_1",	
    "GMSB_3_2d_40_250_3_10_1_1",	
    "GMSB_3_2d_40_250_3_15_1_1",	
    "GMSB_3_2d_40_250_3_20_1_1",	
    "GMSB_3_2d_40_250_3_25_1_1",	
    "GMSB_3_2d_40_250_3_30_1_1",	
    "GMSB_3_2d_40_250_3_36_1_1",	
    "GMSB_3_2d_40_250_3_40_1_1",	
    "GMSB_3_2d_40_250_3_46_1_1",	
    "GMSB_3_2d_45_250_3_2_1_1",	
    "GMSB_3_2d_45_250_3_5_1_1",	
    "GMSB_3_2d_45_250_3_15_1_1",	
    "GMSB_3_2d_45_250_3_20_1_1",	
    "GMSB_3_2d_45_250_3_25_1_1",	
    "GMSB_3_2d_45_250_3_30_1_1",	
    "GMSB_3_2d_45_250_3_35_1_1",	
    "GMSB_3_2d_45_250_3_40_1_1",	
    "GMSB_3_2d_45_250_3_50_1_1",	
    "GMSB_3_2d_50_250_3_2_1_1",	
    "GMSB_3_2d_50_250_3_5_1_1",	
    "GMSB_3_2d_50_250_3_10_1_1",	
    "GMSB_3_2d_50_250_3_15_1_1",	
    "GMSB_3_2d_50_250_3_20_1_1",	
    "GMSB_3_2d_50_250_3_30_1_1",	
    "GMSB_3_2d_50_250_3_40_1_1",	
    "GMSB_3_2d_50_250_3_50_1_1",	
    "GMSB_3_2d_60_250_3_2_1_1",	
    "GMSB_3_2d_60_250_3_5_1_1",	
    "GMSB_3_2d_60_250_3_10_1_1",	
    "GMSB_3_2d_60_250_3_15_1_1",	
    "GMSB_3_2d_60_250_3_20_1_1",	
    "GMSB_3_2d_60_250_3_30_1_1",	
    "GMSB_3_2d_60_250_3_40_1_1",	
    "GMSB_3_2d_60_250_3_50_1_1",	
    "GMSB_3_2d_70_250_3_2_1_1",	
    "GMSB_3_2d_70_250_3_5_1_1",	
    "GMSB_3_2d_70_250_3_10_1_1",	
    "GMSB_3_2d_70_250_3_15_1_1",	
    "GMSB_3_2d_70_250_3_20_1_1",	
    "GMSB_3_2d_70_250_3_30_1_1",	
    "GMSB_3_2d_70_250_3_40_1_1",	
    "GMSB_3_2d_70_250_3_50_1_1",	
    "GMSB_3_2d_80_250_3_2_1_1",	
    "GMSB_3_2d_80_250_3_5_1_1",	
    "GMSB_3_2d_80_250_3_10_1_1",	
    "GMSB_3_2d_80_250_3_15_1_1",	
    "GMSB_3_2d_80_250_3_20_1_1",	
    "GMSB_3_2d_80_250_3_30_1_1",	
    "GMSB_3_2d_80_250_3_40_1_1",	
    "GMSB_3_2d_80_250_3_50_1_1"	
    ]

#sigSamples=[    "GMSB_3_2d_50_250_3_5_1_1" ]
# sigSamples=[
#     "GMSB_3_2d_30_250_3_2_1_1",	
#     "GMSB_3_2d_30_250_3_5_1_1",	
#     "GMSB_3_2d_30_250_3_10_1_1",	
#     "GMSB_3_2d_30_250_3_15_1_1",	
#     "GMSB_3_2d_30_250_3_20_1_1",	
#     "GMSB_3_2d_30_250_3_30_1_1",	
#     "GMSB_3_2d_30_250_3_36_1_1",	
#     "GMSB_3_2d_40_250_3_2_1_1",	
#     "GMSB_3_2d_40_250_3_5_1_1",	
#     "GMSB_3_2d_40_250_3_10_1_1",	
#     "GMSB_3_2d_40_250_3_15_1_1",	
#     "GMSB_3_2d_40_250_3_20_1_1",	
#     "GMSB_3_2d_40_250_3_25_1_1",	
#     "GMSB_3_2d_40_250_3_30_1_1",	
#     "GMSB_3_2d_40_250_3_36_1_1",	
#     "GMSB_3_2d_40_250_3_40_1_1",	
#     "GMSB_3_2d_40_250_3_46_1_1",	
#     "GMSB_3_2d_50_250_3_2_1_1",	
#     "GMSB_3_2d_50_250_3_5_1_1",	
#     "GMSB_3_2d_50_250_3_10_1_1",	
#     "GMSB_3_2d_50_250_3_15_1_1",	
#     "GMSB_3_2d_50_250_3_20_1_1",	
#     "GMSB_3_2d_50_250_3_30_1_1",	
#     "GMSB_3_2d_50_250_3_40_1_1",	
#     "GMSB_3_2d_50_250_3_50_1_1",	
    
#     ]
#sigSamples=[    "GMSB_3_2d_50_250_3_5_1_1" ]
#sigSamples=[    ]

for sig in sigSamples:
    myTopLvl = configMgr.addTopLevelXMLClone(bkgOnly,"dilepton_%s"%sig)
    sigSample = Sample(sig,kPink)
    sigSample.setNormByTheory()
    sigSample.setNormFactor("mu_SIG",0.,0.,5.)
    myTopLvl.addSamples(sigSample)
    myTopLvl.setSignalSample(sigSample)
    meffChannel = myTopLvl.addChannel("cuts",meffRegions,meffNBins,meffBinLow,meffBinHigh)
    meffChannel.useOverflowBin=True
    myTopLvl.setSignalChannels(meffChannel)
    
