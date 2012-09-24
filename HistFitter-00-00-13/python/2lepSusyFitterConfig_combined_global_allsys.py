
################################################################
## In principle all you have to setup is defined in this file ##
################################################################

from configManager import configMgr
from ROOT import kBlack,kRed,kBlue,kGreen,kYellow,kWhite,kPink,kGray,kMagenta
from configWriter import TopLevelXML,Measurement,ChannelXML,Sample
from systematic import Systematic

from ROOT import gROOT
gROOT.LoadMacro("./macros/AtlasStyle.C")
import ROOT
ROOT.SetAtlasStyle()

useStat=True
doValidation=True
doDiscoverySR2=False
doDiscoverySR4=False
discoverychannel="ee" # ee, emu, mumu
doExclusion=False
#doExclusion=True
blindSR=False
moreSyst=True
fullSyst=True
useXsecUnc=True             # switch off when calucating excluded cross section (colour code in SM plots)
doWptReweighting=False ## currently buggy

# First define HistFactory attributes
configMgr.analysisName = "2lepSusyFitterAnalysis_combined_global_allsys" # Name to give the analysis
configMgr.outputFileName = "results/2lepSusyFitterAnalysisOutput_combined_global_allsys.root"

# Scaling calculated by outputLumi / inputLumi
configMgr.inputLumi = 0.001
configMgr.outputLumi = 4.713
configMgr.setLumiUnits("fb-1")


#configMgr.doHypoTest=True
#configMgr.nTOYs=100
#configMgr.calculatorType=0
configMgr.calculatorType=2
#configMgr.testStaType=3
#configMgr.nPoints=20

# Set the files to read from
if configMgr.readFromTree:
# I've provided trees for ee, emu, mumu using 4.7fb data
# ln -s /afs/cern.ch/atlas/groups/susy/1lepton/samples2/SusyFitterTree_EleEle.root etc
    configMgr.inputFileNames = ["data/SusyFitterTree_EleEle.root","data/SusyFitterTree_EleMu.root","data/SusyFitterTree_MuMu.root"]
    if doExclusion:
        configMgr.inputFileNames+=["data/SusyFitterTree_EleEle_GMSB.root","data/SusyFitterTree_EleMu_GMSB.root","data/SusyFitterTree_MuMu_GMSB.root"]
##        configMgr.inputFileNames+=["data/SusyFitterTree_EleEle_mSUGRA.root","data/SusyFitterTree_EleMu_mSUGRA.root","data/SusyFitterTree_MuMu_mSUGRA.root"]
else:
    configMgr.inputFileNames = ["data/"+configMgr.analysisName+".root"]



# AnalysisType corresponds to ee,mumu,emu as I want to split these channels up

# Map regions to cut strings
configMgr.cutsDict = {"TR_ee":"(mll<80 || mll>100) && met > 30 && met < 80 && jet2Pt > 50 && nB3Jet > 0 && AnalysisType==3",
                      "TR_mumu":"(mll<80 || mll>100) && met > 30 && met < 80 && jet2Pt > 50 && nB3Jet > 0 && AnalysisType==4",
                      "TR_emu":"(mll<80 || mll>100) && met > 30 && met < 80 && jet2Pt > 50 && nB3Jet > 0 && AnalysisType==5",
                      "ZR_ee":"mll>80 && mll<100  && met < 50 && jet2Pt > 50 && AnalysisType==3",
                      "ZR_mumu":"mll>80 && mll<100  && met < 50 && jet2Pt > 50 && AnalysisType==4",

                      "SR2_ee":"met > 300 && nJet>=2 && jet2Pt > 200 && jet4Pt < 50 && AnalysisType==3",
                      "SR2_mumu":"met > 300 && nJet>=2 && jet2Pt > 200 && jet4Pt < 50 && AnalysisType==4",
                      "SR2_emu":"met > 300 && nJet>=2 && jet2Pt > 200 && jet4Pt < 50 && AnalysisType==5",
                      "SR4_ee":"met > 100 && nJet>=4 && jet4Pt > 50 && met/meff4Jet > 0.2 && meffInc > 650 && AnalysisType==3",
                      "SR4_mumu":"met > 100 && nJet>=4 && jet4Pt > 50 && met/meff4Jet > 0.2 && meffInc > 650 && AnalysisType==4",
                      "SR4_emu":"met > 100 && nJet>=4 && jet4Pt > 50 && met/meff4Jet > 0.2 && meffInc > 650 && AnalysisType==5",

                      "VR2_ee":"met > 100 && met < 300 && jet4Pt < 50 && jet2Pt > 50 && AnalysisType==3",
                      "VR2_emu":"met > 100 && met < 300 && jet4Pt < 50 && jet2Pt > 50 && AnalysisType==5",
                      "VR2_mumu":"met > 100 && met < 300 && jet4Pt < 50 && jet2Pt > 50 && AnalysisType==4",

                      "VR3_ee":"met > 100 && met < 300 && jet4Pt < 50 && jet3Pt > 50 && AnalysisType==3",
                      "VR3_emu":"met > 100 && met < 300 && jet4Pt < 50 && jet3Pt > 50 && AnalysisType==5",
                      "VR3_mumu":"met > 100 && met < 300 && jet4Pt < 50 && jet3Pt > 50 && AnalysisType==4",

                      "VR4_ee":"met < 100 && jet4Pt > 50 && AnalysisType==3",
                      "VR4_emu":"met < 100 && jet4Pt > 50  && AnalysisType==5",
                      "VR4_mumu":"met < 100  && jet4Pt > 50 && AnalysisType==4",

                      "VZR2_ee":"met > 50 && met < 100 && jet2Pt > 50 && nB3Jet == 0 && AnalysisType==3",
                      "VZR2_emu":"met > 50 && met < 100 && jet2Pt > 50 && nB3Jet == 0 && AnalysisType==5",                    
                      "VZR2_mumu":"met > 50 && met < 100 && jet2Pt > 50 && nB3Jet == 0 && AnalysisType==4",

                      "VZR3_ee":"met > 50 && met < 100  && jet3Pt > 50 && nB3Jet == 0 && AnalysisType==3",
                      "VZR3_emu":"met > 50 && met < 100 && jet3Pt > 50 && nB3Jet == 0 && AnalysisType==5",
                      "VZR3_mumu":"met > 50 && met < 100 && jet3Pt > 50 && nB3Jet == 0 && AnalysisType==4",

                      "VZR4_ee":"met > 50 && met < 100 & jet4Pt > 50  && nB3Jet == 0 && AnalysisType==3",
                      "VZR4_emu":"met > 50 && met < 100 & jet4Pt > 50 && nB3Jet == 0 && AnalysisType==5",
                      "VZR4_mumu":"met > 50 && met < 100 & jet4Pt > 50  && nB3Jet == 0 && AnalysisType==4"
}


## # Tuples of weights 
if doWptReweighting:
    truthWptWeight="truthWptWeight"
else:
    truthWptWeight="1"
configMgr.weights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"bTagWeight2Jet")
configMgr.weightsQCD = "qcdWeight"
configMgr.weightsQCDWithB = "qcdBWeight"

xsecSigHighWeights = ("genWeightUp","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"bTagWeight2Jet")
xsecSigLowWeights = ("genWeightDown","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"bTagWeight2Jet")

ktScaleWHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"ktfacUpWeightW","bTagWeight2Jet")
ktScaleWLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"ktfacDownWeightW","bTagWeight2Jet")
                    
ktScaleTopHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"ktfacUpWeightTop","bTagWeight2Jet")
ktScaleTopLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"ktfacDownWeightTop","bTagWeight2Jet")

#noWPtWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","bTagWeight2Jet")
#noWPtWeightsHigh = ("genWeight","eventWeight","leptonWeight","triggerWeight","(1+(truthWptWeight-1)/2)","bTagWeight2Jet")
#noWPtWeightsLow = ("genWeight","eventWeight","leptonWeight","triggerWeight","(1+(truthWptWeight-1)*1.5)","bTagWeight2Jet")

bTagHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"bTagWeight2JetUp")
bTagLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"bTagWeight2JetDown")

trigHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeightUp",truthWptWeight,"bTagWeight2Jet")
trigLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeightDown",truthWptWeight,"bTagWeight2Jet")

lepHighWeights = ("genWeight","eventWeight","leptonWeightUp","triggerWeight",truthWptWeight,"bTagWeight2Jet")
lepLowWeights = ("genWeight","eventWeight","leptonWeightDown","triggerWeight",truthWptWeight,"bTagWeight2Jet")
                                                                                        
#--------------------
# List of systematics
#--------------------

# KtScale uncertainty as histoSys - two-sided, no additional normalization
topKtScale = Systematic("KtScaleTop",configMgr.weights,ktScaleTopHighWeights,ktScaleTopLowWeights,"weight","normHistoSys")
wzKtScale = Systematic("KtScaleWZ",configMgr.weights,ktScaleWHighWeights,ktScaleWLowWeights,"weight","normHistoSys")

# Signal XSec uncertainty as overallSys (pure yeild affect)
xsecSig = Systematic("XSS",configMgr.weights,xsecSigHighWeights,xsecSigLowWeights,"weight","overallSys")


# Trigger weight uncertainty as overallSys
trigZR = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigTR = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigVR = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigSR2 = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigSR4 = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")

# Lepton weight uncertainty as overallSys
lepZR = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepTR = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepVR = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepSR2 = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepSR4 = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")

# B-tag uncertainty as overallSys in TR
#btagZR = Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","overallSys")
btagTR = Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","overallSys")
btagVR = Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","overallSys")
btagSR = Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","overallSys")

# JES uncertainty as shapeSys - one systematic per region (combine WR and TR), merge samples
jesZR = Systematic("JZC","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesTR = Systematic("JTC","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesSR2 = Systematic("J2","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesSR4 = Systematic("J4","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVR2 = Systematic("JVR2","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVR3 = Systematic("JVR3","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVR4 = Systematic("JVR4","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVZR2 = Systematic("JVZR2","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVZR3 = Systematic("JVZR3","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVZR4 = Systematic("JVZR4","_NoSys","_JESup","_JESdown","tree","shapeSys")

# LES uncertainty as overallSys - one per channel
lesZR = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesTR = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesVR = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesSR2 = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesSR4 = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")

# LER with muon system as overallSys - one per channel
lermsZR = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsTR = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsVR = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsSR2 = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsSR4 = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")

# LER with inner detector as overallSys - one per channel
leridZR = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridTR = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridVR = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridSR2 = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridSR4 = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")

# MET cell-out uncertainty as overallSys - one per channel
metcoZR = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoTR = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoVR = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoSR2 = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoSR4 = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")

# MET pileup uncertainty as overallSys - one per channel
# CHANGED TO HISTOSYS TO BE CONSISTENT WITH 1LEP
metpuZR = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuTR = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuVR = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuSR2 = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuSR4 = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")


# List of systematics
configMgr.nomName = "_NoSys"

#Parameters of the Measurement
measName = "BasicMeasurement"
measLumi = 1.
measLumiError = 0.037

# nJet Binning for Top Control region

nJetTopeeRegions = ["TR_ee"]
nJetTopeeNBins = 8
nJetTopeeBinLow = 2
nJetTopeeBinHigh = 10

nJetTopemuRegions = ["TR_emu"]
nJetTopemuNBins = 8
nJetTopemuBinLow = 2
nJetTopemuBinHigh = 10

nJetTopmumuRegions = ["TR_mumu"]
nJetTopmumuNBins = 8
nJetTopmumuBinLow = 2
nJetTopmumuBinHigh = 10

# List of samples and their plotting colours
topSample = Sample("Top",kGreen)
topSample.setNormFactor("mu_Top",1.,0.,5.)
topSample.setStatConfig(useStat)
wzSample = Sample("WZ",kRed)
wzSample.setNormFactor("mu_WZ",1.,0.,5.)
wzSample.setStatConfig(useStat)
bgSample = Sample("BG",kYellow)
bgSample.setNormFactor("mu_BG",1.,0.,5.)
bgSample.setStatConfig(useStat)
qcdSample = Sample("QCD",kGray+1)
qcdSample.setQCD(True,"histoSys")
qcdSample.setStatConfig(useStat)
dataSample = Sample("Data",kBlack)
dataSample.setData()

nJetZmumuRegions = ["ZR_mumu"]
nJetZmumuNBins = 8
nJetZmumuBinLow = 2
nJetZmumuBinHigh = 10

nJetZeeRegions = ["ZR_ee"]
nJetZeeNBins = 8
nJetZeeBinLow = 2
nJetZeeBinHigh = 10

ZptZmumuRegions = ["ZR_mumu"]
ZptZmumuNBins = 50
ZptZmumuBinLow = 0
ZptZmumuBinHigh = 1000

ZptZeeRegions = ["ZR_ee"]
ZptZeeNBins = 50
ZptZeeBinLow = 0
ZptZeeBinHigh = 1000

srNBins = 1
srBinLow = 0.5
srBinHigh = 1.5

                
#Create TopLevelXML objects
bkgOnly = configMgr.addTopLevelXML("dilepton_bkgonly")
bkgOnly.addSamples([qcdSample,bgSample,topSample,wzSample,dataSample])

if useStat:
    bkgOnly.statErrThreshold=0.05 #0.03??
else:
    bkgOnly.statErrThreshold=None


bkgOnly.getSample("Top").addSystematic(topKtScale)
bkgOnly.getSample("WZ").addSystematic(wzKtScale)


#Add Measurement
meas=bkgOnly.addMeasurement(measName,measLumi,measLumiError)
meas.addPOI("mu_SIG")

# Fix Background 
meas.addParamSetting("mu_BG","const",1.0)
# nJet for Top
nJetTopeeChannel=bkgOnly.addChannel("nJet",nJetTopeeRegions,nJetTopeeNBins,nJetTopeeBinLow,nJetTopeeBinHigh)
nJetTopeeChannel.hasB = True
nJetTopeeChannel.hasBQCD = True
nJetTopeeChannel.useOverflowBin = False
nJetTopeeChannel.addSystematic(jesTR)
[s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetTopeeChannel.getSystematic(jesTR.name)]
if moreSyst:
    nJetTopeeChannel.addSystematic(btagTR)
    nJetTopeeChannel.addSystematic(lepTR)
if fullSyst:
    nJetTopeeChannel.addSystematic(metcoTR)
    nJetTopeeChannel.addSystematic(metpuTR)
    nJetTopeeChannel.addSystematic(trigTR)
    [nJetTopeeChannel.getSample(sam).addSystematic(lesTR) for sam in ["WZ","Top","BG"]]
    [nJetTopeeChannel.getSample(sam).addSystematic(lermsTR) for sam in ["WZ","Top","BG"]]
    [nJetTopeeChannel.getSample(sam).addSystematic(leridTR) for sam in ["WZ","Top","BG"]]

# nJet for Z
nJetZeeChannel=bkgOnly.addChannel("nJet",nJetZeeRegions,nJetZeeNBins,nJetZeeBinLow,nJetZeeBinHigh)
nJetZeeChannel.hasB = False
nJetZeeChannel.hasBQCD = False
nJetZeeChannel.addSystematic(jesZR)
[s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetZeeChannel.getSystematic(jesZR.name)]
if moreSyst:
##nJetZeeChannel.addSystematic(btagZR)
    nJetZeeChannel.addSystematic(lepZR)
if fullSyst:
    nJetZeeChannel.addSystematic(metcoZR)
    nJetZeeChannel.addSystematic(metpuZR)
    nJetZeeChannel.addSystematic(trigZR)
    [nJetZeeChannel.getSample(sam).addSystematic(lesZR) for sam in ["WZ","Top","BG"]]
    [nJetZeeChannel.getSample(sam).addSystematic(lermsZR) for sam in ["WZ","Top","BG"]]
    [nJetZeeChannel.getSample(sam).addSystematic(leridZR) for sam in ["WZ","Top","BG"]]

nJetTopemuChannel=bkgOnly.addChannel("nJet",nJetTopemuRegions,nJetTopemuNBins,nJetTopemuBinLow,nJetTopemuBinHigh)
nJetTopemuChannel.hasB = True
nJetTopemuChannel.hasBQCD = True
nJetTopemuChannel.useOverflowBin = False
nJetTopemuChannel.addSystematic(jesTR)
[s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetTopemuChannel.getSystematic(jesTR.name)]
if moreSyst:
    nJetTopemuChannel.addSystematic(btagTR)
    nJetTopemuChannel.addSystematic(lepTR)
if fullSyst:
    nJetTopemuChannel.addSystematic(metcoTR)
    nJetTopemuChannel.addSystematic(metpuTR)
    nJetTopemuChannel.addSystematic(trigTR)
    [nJetTopemuChannel.getSample(sam).addSystematic(lesTR) for sam in ["WZ","Top","BG"]]
    [nJetTopemuChannel.getSample(sam).addSystematic(lermsTR) for sam in ["WZ","Top","BG"]]
    [nJetTopemuChannel.getSample(sam).addSystematic(leridTR) for sam in ["WZ","Top","BG"]]

nJetTopmumuChannel=bkgOnly.addChannel("nJet",nJetTopmumuRegions,nJetTopmumuNBins,nJetTopmumuBinLow,nJetTopmumuBinHigh)
nJetTopmumuChannel.hasB = True
nJetTopmumuChannel.hasBQCD = True
nJetTopmumuChannel.useOverflowBin = False
nJetTopmumuChannel.addSystematic(jesTR)
[s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetTopmumuChannel.getSystematic(jesTR.name)]
if moreSyst:
    nJetTopmumuChannel.addSystematic(btagTR)
    nJetTopmumuChannel.addSystematic(lepTR)
if fullSyst:
    nJetTopmumuChannel.addSystematic(metcoTR)
    nJetTopmumuChannel.addSystematic(metpuTR)
    nJetTopmumuChannel.addSystematic(trigTR)
    [nJetTopmumuChannel.getSample(sam).addSystematic(lesTR) for sam in ["WZ","Top","BG"]]
    [nJetTopmumuChannel.getSample(sam).addSystematic(lermsTR) for sam in ["WZ","Top","BG"]]
    [nJetTopmumuChannel.getSample(sam).addSystematic(leridTR) for sam in ["WZ","Top","BG"]]

# nJet for Z
nJetZmumuChannel=bkgOnly.addChannel("nJet",nJetZmumuRegions,nJetZmumuNBins,nJetZmumuBinLow,nJetZmumuBinHigh)
nJetZmumuChannel.hasB = False
nJetZmumuChannel.hasBQCD = False
nJetZmumuChannel.addSystematic(jesZR)
[s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetZmumuChannel.getSystematic(jesZR.name)]
if moreSyst:
##nJetZmumuChannel.addSystematic(btagZR)
    nJetZmumuChannel.addSystematic(lepZR)
if fullSyst:
    nJetZmumuChannel.addSystematic(metcoZR)
    nJetZmumuChannel.addSystematic(metpuZR)
    nJetZmumuChannel.addSystematic(trigZR)
    [nJetZmumuChannel.getSample(sam).addSystematic(lesZR) for sam in ["WZ","Top","BG"]]
    [nJetZmumuChannel.getSample(sam).addSystematic(lermsZR) for sam in ["WZ","Top","BG"]]
    [nJetZmumuChannel.getSample(sam).addSystematic(leridZR) for sam in ["WZ","Top","BG"]]
                                                                            


#ZptZeeChannel=bkgOnly.addChannel("Zpt",ZptZeeRegions,ZptZeeNBins,ZptZeeBinLow,ZptZeeBinHigh)
#ZptZmumuChannel=bkgOnly.addChannel("Zpt",ZptZmumuRegions,ZptZmumuNBins,ZptZmumuBinLow,ZptZmumuBinHigh)
#ZptZeeChannel.addSystematic(jes)
#ZptZeeChannel.useOverflowBin=True
#ZptZmumuChannel.useOverflowBin=True
bkgOnly.setBkgConstrainChannels([nJetTopeeChannel,nJetZeeChannel,nJetTopemuChannel,nJetTopmumuChannel,nJetZmumuChannel])

#--------------------------------------------------------------
# Validation regions - not necessarily statistically independent
#--------------------------------------------------------------

if doValidation:
    
    ZptZeeChannel=bkgOnly.addChannel("Zpt",ZptZeeRegions,ZptZeeNBins,ZptZeeBinLow,ZptZeeBinHigh)    
    ZptZeeChannel.hasB = False
    ZptZeeChannel.hasBQCD = False
    ZptZeeChannel.addSystematic(jesZR)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in ZptZeeChannel.getSystematic(jesZR.name)]
    if moreSyst:
        ZptZeeChannel.addSystematic(lepZR)
    if fullSyst:
        ZptZeeChannel.addSystematic(metcoZR)
        ZptZeeChannel.addSystematic(metpuZR)
        ZptZeeChannel.addSystematic(trigZR)
        [ZptZeeChannel.getSample(sam).addSystematic(lesZR) for sam in ["WZ","Top","BG"]]
        [ZptZeeChannel.getSample(sam).addSystematic(lermsZR) for sam in ["WZ","Top","BG"]]
        [ZptZeeChannel.getSample(sam).addSystematic(leridZR) for sam in ["WZ","Top","BG"]]

    ZptZmumuChannel=bkgOnly.addChannel("Zpt",ZptZmumuRegions,ZptZmumuNBins,ZptZmumuBinLow,ZptZmumuBinHigh)    
    ZptZmumuChannel.hasB = False
    ZptZmumuChannel.hasBQCD = False
    ZptZmumuChannel.addSystematic(jesZR)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in ZptZmumuChannel.getSystematic(jesZR.name)]
    if moreSyst:
        ZptZmumuChannel.addSystematic(lepZR)
    if fullSyst:
        ZptZmumuChannel.addSystematic(metcoZR)
        ZptZmumuChannel.addSystematic(metpuZR)
        ZptZmumuChannel.addSystematic(trigZR)
        [ZptZmumuChannel.getSample(sam).addSystematic(lesZR) for sam in ["WZ","Top","BG"]]
        [ZptZmumuChannel.getSample(sam).addSystematic(lermsZR) for sam in ["WZ","Top","BG"]]
        [ZptZmumuChannel.getSample(sam).addSystematic(leridZR) for sam in ["WZ","Top","BG"]]

    nJetVR2eeChannel=bkgOnly.addChannel("nJet",["VR2_ee"],nJetTopeeNBins,nJetTopeeBinLow,nJetTopeeBinHigh)
    nJetVR2eeChannel.hasB = False
    nJetVR2eeChannel.hasBQCD = False
    nJetVR2eeChannel.useOverflowBin = True
    nJetVR2eeChannel.addSystematic(jesVR2)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetVR2eeChannel.getSystematic(jesVR2.name)]
    if moreSyst:
        nJetVR2eeChannel.addSystematic(lepVR)
    if fullSyst:
        nJetVR2eeChannel.addSystematic(metcoVR)
        nJetVR2eeChannel.addSystematic(metpuVR)
        nJetVR2eeChannel.addSystematic(trigVR)
        [nJetVR2eeChannel.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
        [nJetVR2eeChannel.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
        [nJetVR2eeChannel.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]


##    nJetVZR2eeChannel=bkgOnly.addChannel("mll",["VZR2_ee"],40,0,400)
    nJetVZR2eeChannel=bkgOnly.addChannel("nJet",["VZR2_ee"],nJetTopeeNBins,nJetTopeeBinLow,nJetTopeeBinHigh)
    nJetVZR2eeChannel.hasB = True
    nJetVZR2eeChannel.hasBQCD = False
    nJetVZR2eeChannel.useOverflowBin = True
    nJetVZR2eeChannel.addSystematic(jesVZR2)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetVZR2eeChannel.getSystematic(jesVZR2.name)]
    if moreSyst:
        nJetVZR2eeChannel.addSystematic(btagVR)
        nJetVZR2eeChannel.addSystematic(lepVR)
    if fullSyst:
        nJetVZR2eeChannel.addSystematic(metcoVR)
        nJetVZR2eeChannel.addSystematic(metpuVR)
        nJetVZR2eeChannel.addSystematic(trigVR)
        [nJetVZR2eeChannel.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
        [nJetVZR2eeChannel.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
        [nJetVZR2eeChannel.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]


    nJetVR3eeChannel=bkgOnly.addChannel("nJet",["VR3_ee"],nJetTopeeNBins,nJetTopeeBinLow,nJetTopeeBinHigh)
    nJetVR3eeChannel.hasB = False
    nJetVR3eeChannel.hasBQCD = False
    nJetVR3eeChannel.useOverflowBin = True
    nJetVR3eeChannel.addSystematic(jesVR3)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetVR3eeChannel.getSystematic(jesVR3.name)]
    if moreSyst:
        nJetVR3eeChannel.addSystematic(btagVR)
        nJetVR3eeChannel.addSystematic(lepVR)
    if fullSyst:
        nJetVR3eeChannel.addSystematic(metcoVR)
        nJetVR3eeChannel.addSystematic(metpuVR)
        nJetVR3eeChannel.addSystematic(trigVR)
        [nJetVR3eeChannel.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
        [nJetVR3eeChannel.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
        [nJetVR3eeChannel.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]



##    nJetVZR3eeChannel=bkgOnly.addChannel("mll",["VZR3_ee"],40,0,400)
    nJetVZR3eeChannel=bkgOnly.addChannel("nJet",["VZR3_ee"],nJetTopeeNBins,nJetTopeeBinLow,nJetTopeeBinHigh)
    nJetVZR3eeChannel.hasB = True
    nJetVZR3eeChannel.hasBQCD = False
    nJetVZR3eeChannel.useOverflowBin = True
    nJetVZR3eeChannel.addSystematic(jesVZR3)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetVZR3eeChannel.getSystematic(jesVZR3.name)]
    if moreSyst:
        nJetVZR3eeChannel.addSystematic(btagVR)
        nJetVZR3eeChannel.addSystematic(lepVR)
    if fullSyst:
        nJetVZR3eeChannel.addSystematic(metcoVR)
        nJetVZR3eeChannel.addSystematic(metpuVR)
        nJetVZR3eeChannel.addSystematic(trigVR)
        [nJetVZR3eeChannel.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
        [nJetVZR3eeChannel.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
        [nJetVZR3eeChannel.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]

    nJetVR4eeChannel=bkgOnly.addChannel("nJet",["VR4_ee"],nJetTopeeNBins,nJetTopeeBinLow,nJetTopeeBinHigh)
    nJetVR4eeChannel.hasB = False
    nJetVR4eeChannel.hasBQCD = False
    nJetVR4eeChannel.useOverflowBin = True
    nJetVR4eeChannel.addSystematic(jesVR4)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetVR4eeChannel.getSystematic(jesVR4.name)]
    if moreSyst:
        nJetVR4eeChannel.addSystematic(btagVR)
        nJetVR4eeChannel.addSystematic(lepVR)
    if fullSyst:
        nJetVR4eeChannel.addSystematic(metcoVR)
        nJetVR4eeChannel.addSystematic(metpuVR)
        nJetVR4eeChannel.addSystematic(trigVR)
        [nJetVR4eeChannel.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
        [nJetVR4eeChannel.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
        [nJetVR4eeChannel.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]



##    nJetVZR4eeChannel=bkgOnly.addChannel("mll",["VZR4_ee"],40,0,400)
    nJetVZR4eeChannel=bkgOnly.addChannel("nJet",["VZR4_ee"],nJetTopeeNBins,nJetTopeeBinLow,nJetTopeeBinHigh)
    nJetVZR4eeChannel.hasB = True
    nJetVZR4eeChannel.hasBQCD = False
    nJetVZR4eeChannel.useOverflowBin = True
    nJetVZR4eeChannel.addSystematic(jesVZR4)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetVZR4eeChannel.getSystematic(jesVZR4.name)]
    if moreSyst:
        nJetVZR4eeChannel.addSystematic(btagVR)
        nJetVZR4eeChannel.addSystematic(lepVR)
    if fullSyst:
        nJetVZR4eeChannel.addSystematic(metcoVR)
        nJetVZR4eeChannel.addSystematic(metpuVR)
        nJetVZR4eeChannel.addSystematic(trigVR)
        [nJetVZR4eeChannel.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
        [nJetVZR4eeChannel.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
        [nJetVZR4eeChannel.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]


    nJetVR2emuChannel=bkgOnly.addChannel("nJet",["VR2_emu"],nJetTopemuNBins,nJetTopemuBinLow,nJetTopemuBinHigh)
    nJetVR2emuChannel.hasB = False
    nJetVR2emuChannel.hasBQCD = False
    nJetVR2emuChannel.useOverflowBin = True
    nJetVR2emuChannel.addSystematic(jesVR2)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetVR2emuChannel.getSystematic(jesVR2.name)]
    if moreSyst:
        nJetVR2emuChannel.addSystematic(lepVR)
    if fullSyst:
        nJetVR2emuChannel.addSystematic(metcoVR)
        nJetVR2emuChannel.addSystematic(metpuVR)
        nJetVR2emuChannel.addSystematic(trigVR)
        [nJetVR2emuChannel.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
        [nJetVR2emuChannel.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
        [nJetVR2emuChannel.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]



##    nJetVZR2emuChannel=bkgOnly.addChannel("mll",["VZR2_emu"],40,0,400)
    nJetVZR2emuChannel=bkgOnly.addChannel("nJet",["VZR2_emu"],nJetTopeeNBins,nJetTopeeBinLow,nJetTopeeBinHigh)
    nJetVZR2emuChannel.hasB = True
    nJetVZR2emuChannel.hasBQCD = False
    nJetVZR2emuChannel.useOverflowBin = True
    nJetVZR2emuChannel.addSystematic(jesVZR2)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetVZR2emuChannel.getSystematic(jesVZR2.name)]
    if moreSyst:
        nJetVZR2emuChannel.addSystematic(btagVR)
        nJetVZR2emuChannel.addSystematic(lepVR)
    if fullSyst:
        nJetVZR2emuChannel.addSystematic(metcoVR)
        nJetVZR2emuChannel.addSystematic(metpuVR)
        nJetVZR2emuChannel.addSystematic(trigVR)
        [nJetVZR2emuChannel.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
        [nJetVZR2emuChannel.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
        [nJetVZR2emuChannel.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]


    nJetVR3emuChannel=bkgOnly.addChannel("nJet",["VR3_emu"],nJetTopemuNBins,nJetTopemuBinLow,nJetTopemuBinHigh)
    nJetVR3emuChannel.hasB = False
    nJetVR3emuChannel.hasBQCD = False
    nJetVR3emuChannel.useOverflowBin = True
    nJetVR3emuChannel.addSystematic(jesVR3)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetVR3emuChannel.getSystematic(jesVR3.name)]
    if moreSyst:
        nJetVR3emuChannel.addSystematic(btagVR)
        nJetVR3emuChannel.addSystematic(lepVR)
    if fullSyst:
        nJetVR3emuChannel.addSystematic(metcoVR)
        nJetVR3emuChannel.addSystematic(metpuVR)
        nJetVR3emuChannel.addSystematic(trigVR)
        [nJetVR3emuChannel.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
        [nJetVR3emuChannel.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
        [nJetVR3emuChannel.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]


##    nJetVZR3emuChannel=bkgOnly.addChannel("mll",["VZR3_emu"],40,0,400)
    nJetVZR3emuChannel=bkgOnly.addChannel("nJet",["VZR3_emu"],nJetTopeeNBins,nJetTopeeBinLow,nJetTopeeBinHigh)
    nJetVZR3emuChannel.hasB = True
    nJetVZR3emuChannel.hasBQCD = False
    nJetVZR3emuChannel.useOverflowBin = True
    nJetVZR3emuChannel.addSystematic(jesVZR3)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetVZR3emuChannel.getSystematic(jesVZR3.name)]
    if moreSyst:
        nJetVZR3emuChannel.addSystematic(btagVR)
        nJetVZR3emuChannel.addSystematic(lepVR)
    if fullSyst:
        nJetVZR3emuChannel.addSystematic(metcoVR)
        nJetVZR3emuChannel.addSystematic(metpuVR)
        nJetVZR3emuChannel.addSystematic(trigVR)
        [nJetVZR3emuChannel.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
        [nJetVZR3emuChannel.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
        [nJetVZR3emuChannel.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]

    nJetVR4emuChannel=bkgOnly.addChannel("nJet",["VR4_emu"],nJetTopemuNBins,nJetTopemuBinLow,nJetTopemuBinHigh)
    nJetVR4emuChannel.hasB = False
    nJetVR4emuChannel.hasBQCD = False
    nJetVR4emuChannel.useOverflowBin = True
    nJetVR4emuChannel.addSystematic(jesVR4)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetVR4emuChannel.getSystematic(jesVR4.name)]
    if moreSyst:
        nJetVR4emuChannel.addSystematic(btagVR)
        nJetVR4emuChannel.addSystematic(lepVR)
    if fullSyst:
        nJetVR4emuChannel.addSystematic(metcoVR)
        nJetVR4emuChannel.addSystematic(metpuVR)
        nJetVR4emuChannel.addSystematic(trigVR)
        [nJetVR4emuChannel.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
        [nJetVR4emuChannel.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
        [nJetVR4emuChannel.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]


##    nJetVZR4emuChannel=bkgOnly.addChannel("mll",["VZR4_emu"],40,0,400)
    nJetVZR4emuChannel=bkgOnly.addChannel("nJet",["VZR4_emu"],nJetTopeeNBins,nJetTopeeBinLow,nJetTopeeBinHigh)
    nJetVZR4emuChannel.hasB = True
    nJetVZR4emuChannel.hasBQCD = False
    nJetVZR4emuChannel.useOverflowBin = True
    nJetVZR4emuChannel.addSystematic(jesVZR4)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetVZR4emuChannel.getSystematic(jesVZR4.name)]
    if moreSyst:
        nJetVZR4emuChannel.addSystematic(btagVR)
        nJetVZR4emuChannel.addSystematic(lepVR)
    if fullSyst:
        nJetVZR4emuChannel.addSystematic(metcoVR)
        nJetVZR4emuChannel.addSystematic(metpuVR)
        nJetVZR4emuChannel.addSystematic(trigVR)
        [nJetVZR4emuChannel.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
        [nJetVZR4emuChannel.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
        [nJetVZR4emuChannel.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]

    nJetVR2mumuChannel=bkgOnly.addChannel("nJet",["VR2_mumu"],nJetTopmumuNBins,nJetTopmumuBinLow,nJetTopmumuBinHigh)
    nJetVR2mumuChannel.hasB = False
    nJetVR2mumuChannel.hasBQCD = False
    nJetVR2mumuChannel.useOverflowBin = True
    nJetVR2mumuChannel.addSystematic(jesVR2)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetVR2mumuChannel.getSystematic(jesVR2.name)]
    if moreSyst:
        nJetVR2mumuChannel.addSystematic(btagVR)
        nJetVR2mumuChannel.addSystematic(lepVR)
    if fullSyst:
        nJetVR2mumuChannel.addSystematic(metcoVR)
        nJetVR2mumuChannel.addSystematic(metpuVR)
        nJetVR2mumuChannel.addSystematic(trigVR)
        [nJetVR2mumuChannel.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
        [nJetVR2mumuChannel.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
        [nJetVR2mumuChannel.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]



##    nJetVZR2mumuChannel=bkgOnly.addChannel("mll",["VZR2_mumu"],40,0,400)
    nJetVZR2mumuChannel=bkgOnly.addChannel("nJet",["VZR2_mumu"],nJetTopeeNBins,nJetTopeeBinLow,nJetTopeeBinHigh)
    nJetVZR2mumuChannel.hasB = True
    nJetVZR2mumuChannel.hasBQCD = False
    nJetVZR2mumuChannel.useOverflowBin = True
    nJetVZR2mumuChannel.addSystematic(jesVZR2)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetVZR2mumuChannel.getSystematic(jesVZR2.name)]
    if moreSyst:
        nJetVZR2mumuChannel.addSystematic(btagVR)
        nJetVZR2mumuChannel.addSystematic(lepVR)
    if fullSyst:
        nJetVZR2mumuChannel.addSystematic(metcoVR)
        nJetVZR2mumuChannel.addSystematic(metpuVR)
        nJetVZR2mumuChannel.addSystematic(trigVR)
        [nJetVZR2mumuChannel.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
        [nJetVZR2mumuChannel.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
        [nJetVZR2mumuChannel.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]


    nJetVR3mumuChannel=bkgOnly.addChannel("nJet",["VR3_mumu"],nJetTopmumuNBins,nJetTopmumuBinLow,nJetTopmumuBinHigh)
    nJetVR3mumuChannel.hasB = False
    nJetVR3mumuChannel.hasBQCD = False
    nJetVR3mumuChannel.useOverflowBin = True
    nJetVR3mumuChannel.addSystematic(jesVR3)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetVR3mumuChannel.getSystematic(jesVR3.name)]
    if moreSyst:
        nJetVR3mumuChannel.addSystematic(btagVR)
        nJetVR3mumuChannel.addSystematic(lepVR)
    if fullSyst:
        nJetVR3mumuChannel.addSystematic(metcoVR)
        nJetVR3mumuChannel.addSystematic(metpuVR)
        nJetVR3mumuChannel.addSystematic(trigVR)
        [nJetVR3mumuChannel.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
        [nJetVR3mumuChannel.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
        [nJetVR3mumuChannel.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]



##    nJetVZR3mumuChannel=bkgOnly.addChannel("mll",["VZR3_mumu"],40,0,400)
    nJetVZR3mumuChannel=bkgOnly.addChannel("nJet",["VZR3_mumu"],nJetTopeeNBins,nJetTopeeBinLow,nJetTopeeBinHigh)
    nJetVZR3mumuChannel.hasB = True
    nJetVZR3mumuChannel.hasBQCD = True
    nJetVZR3mumuChannel.useOverflowBin = True
    nJetVZR3mumuChannel.addSystematic(jesVZR3)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetVZR3mumuChannel.getSystematic(jesVZR3.name)]
    if moreSyst:
        nJetVZR3mumuChannel.addSystematic(btagVR)
        nJetVZR3mumuChannel.addSystematic(lepVR)
    if fullSyst:
        nJetVZR3mumuChannel.addSystematic(metcoVR)
        nJetVZR3mumuChannel.addSystematic(metpuVR)
        nJetVZR3mumuChannel.addSystematic(trigVR)
        [nJetVZR3mumuChannel.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
        [nJetVZR3mumuChannel.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
        [nJetVZR3mumuChannel.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]


    nJetVR4mumuChannel=bkgOnly.addChannel("nJet",["VR4_mumu"],nJetTopmumuNBins,nJetTopmumuBinLow,nJetTopmumuBinHigh)
    nJetVR4mumuChannel.hasB = False
    nJetVR4mumuChannel.hasBQCD = False
    nJetVR4mumuChannel.useOverflowBin = True
    nJetVR4mumuChannel.addSystematic(jesVR4)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetVR4mumuChannel.getSystematic(jesVR4.name)]
    if moreSyst:
        nJetVR4mumuChannel.addSystematic(btagVR)
        nJetVR4mumuChannel.addSystematic(lepVR)
    if fullSyst:
        nJetVR4mumuChannel.addSystematic(metcoVR)
        nJetVR4mumuChannel.addSystematic(metpuVR)
        nJetVR4mumuChannel.addSystematic(trigVR)
        [nJetVR4mumuChannel.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
        [nJetVR4mumuChannel.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
        [nJetVR4mumuChannel.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]



##    nJetVZR4mumuChannel=bkgOnly.addChannel("mll",["VZR4_mumu"],40,0,400)
    nJetVZR4mumuChannel=bkgOnly.addChannel("nJet",["VZR4_mumu"],nJetTopeeNBins,nJetTopeeBinLow,nJetTopeeBinHigh)
    nJetVZR4mumuChannel.hasB = True
    nJetVZR4mumuChannel.hasBQCD = True
    nJetVZR4mumuChannel.useOverflowBin = True
    nJetVZR4mumuChannel.addSystematic(jesVZR4)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetVZR4mumuChannel.getSystematic(jesVZR4.name)]
    if moreSyst:
        nJetVZR4mumuChannel.addSystematic(btagVR)
        nJetVZR4mumuChannel.addSystematic(lepVR)
    if fullSyst:
        nJetVZR4mumuChannel.addSystematic(metcoVR)
        nJetVZR4mumuChannel.addSystematic(metpuVR)
        nJetVZR4mumuChannel.addSystematic(trigVR)
        [nJetVZR4mumuChannel.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
        [nJetVZR4mumuChannel.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
        [nJetVZR4mumuChannel.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]




    bkgOnly.setValidationChannels([ZptZeeChannel,ZptZmumuChannel,nJetVR2eeChannel,nJetVZR2eeChannel,nJetVR3eeChannel,nJetVZR3eeChannel,nJetVR4eeChannel,nJetVZR4eeChannel,nJetVR2emuChannel,nJetVZR2emuChannel,nJetVR3emuChannel,nJetVZR3emuChannel,nJetVR4emuChannel,nJetVZR4emuChannel,nJetVR2mumuChannel,nJetVZR2mumuChannel,nJetVR3mumuChannel,nJetVZR3mumuChannel,nJetVR4mumuChannel,nJetVZR4mumuChannel])



#-------------------------------------------------
# Signal regions - only do this if background only, add as validation regions! 
#-------------------------------------------------

meffNBins = 1
#    meffBinLow = 400.
meffBinLow = 0.
meffBinHigh = 1600.


if not doDiscoverySR2 and not doDiscoverySR4  and not doExclusion and not blindSR:



    # S2 using meff
    meff2ee = bkgOnly.addChannel("meffInc",["SR2_ee"],meffNBins,meffBinLow,meffBinHigh)
    meff2ee.useOverflowBin=True
    meff2ee.addSystematic(jesSR2)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in meff2ee.getSystematic(jesSR2.name)]
    if moreSyst:
        meff2ee.addSystematic(lepSR2)
    
    if fullSyst:
        meff2ee.addSystematic(metcoSR2)
        meff2ee.addSystematic(metpuSR2)
        meff2ee.addSystematic(trigSR2)
        meff2ee.addSystematic(lesSR2)
        meff2ee.addSystematic(lermsSR2)
        meff2ee.addSystematic(leridSR2)

    # S4 using meff
    meff4ee = bkgOnly.addChannel("meffInc",["SR4_ee"],meffNBins,meffBinLow,meffBinHigh)
    meff4ee.useOverflowBin=True
    meff4ee.addSystematic(jesSR4)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in meff4ee.getSystematic(jesSR4.name)]
    if moreSyst:
        meff4ee.addSystematic(lepSR4)
    
    if fullSyst:
        meff4ee.addSystematic(metcoSR4)
        meff4ee.addSystematic(metpuSR4)
        meff4ee.addSystematic(trigSR4)
        meff4ee.addSystematic(lesSR4)
        meff4ee.addSystematic(lermsSR4)
        meff4ee.addSystematic(leridSR4)

    # S2 using meff
    meff2emu = bkgOnly.addChannel("meffInc",["SR2_emu"],meffNBins,meffBinLow,meffBinHigh)
    meff2emu.useOverflowBin=True
    meff2emu.addSystematic(jesSR2)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in meff2emu.getSystematic(jesSR2.name)]
    if moreSyst:
        meff2emu.addSystematic(lepSR2)
    
    if fullSyst:
        meff2emu.addSystematic(metcoSR2)
        meff2emu.addSystematic(metpuSR2)
        meff2emu.addSystematic(trigSR2)
        meff2emu.addSystematic(lesSR2)
        meff2emu.addSystematic(lermsSR2)
        meff2emu.addSystematic(leridSR2)

    # S4 using meff
    meff4emu = bkgOnly.addChannel("meffInc",["SR4_emu"],meffNBins,meffBinLow,meffBinHigh)
    meff4emu.useOverflowBin=True
    meff4emu.addSystematic(jesSR4)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in meff4emu.getSystematic(jesSR4.name)]
    if moreSyst:
        meff4emu.addSystematic(lepSR4)
    
    if fullSyst:
        meff4emu.addSystematic(metcoSR4)
        meff4emu.addSystematic(metpuSR4)
        meff4emu.addSystematic(trigSR4)
        meff4emu.addSystematic(lesSR4)
        meff4emu.addSystematic(lermsSR4)
        meff4emu.addSystematic(leridSR4)

    # S2 using meff
    meff2mumu = bkgOnly.addChannel("meffInc",["SR2_mumu"],meffNBins,meffBinLow,meffBinHigh)
    meff2mumu.useOverflowBin=True
    meff2mumu.addSystematic(jesSR2)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in meff2mumu.getSystematic(jesSR2.name)]
    if moreSyst:
        meff2mumu.addSystematic(lepSR2)
    
    if fullSyst:
        meff2mumu.addSystematic(metcoSR2)
        meff2mumu.addSystematic(metpuSR2)
        meff2mumu.addSystematic(trigSR2)
        meff2mumu.addSystematic(lesSR2)
        meff2mumu.addSystematic(lermsSR2)
        meff2mumu.addSystematic(leridSR2)

    # S4 using meff
    meff4mumu = bkgOnly.addChannel("meffInc",["SR4_mumu"],meffNBins,meffBinLow,meffBinHigh)
    meff4mumu.useOverflowBin=True
    meff4mumu.addSystematic(jesSR4)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in meff4mumu.getSystematic(jesSR4.name)]
    if moreSyst:
        meff4mumu.addSystematic(lepSR4)
    
    if fullSyst:
        meff4mumu.addSystematic(metcoSR4)
        meff4mumu.addSystematic(metpuSR4)
        meff4mumu.addSystematic(trigSR4)
        meff4mumu.addSystematic(lesSR4)
        meff4mumu.addSystematic(lermsSR4)
        meff4mumu.addSystematic(leridSR4)


    bkgOnly.setValidationChannels([meff2ee,meff4ee,meff2emu,meff4emu,meff2mumu,meff4mumu])

if doDiscoverySR2:
    discovery = configMgr.addTopLevelXMLClone(bkgOnly,"DiscoverySR2"+discoverychannel)
    sr2Channelee = discovery.addChannel("cuts",["SR2_ee"],srNBins,srBinLow,srBinHigh)
    sr2Channelee.addSystematic(jesSR2)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in sr2Channelee.getSystematic(jesSR2.name)]
    if moreSyst:
        [sr2Channelee.getSample(sam).addSystematic(lepSR2) for sam in ["WZ","Top","BG"]]
    
    if fullSyst:
        [sr2Channelee.getSample(sam).addSystematic(metcoSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelee.getSample(sam).addSystematic(metpuSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelee.getSample(sam).addSystematic(trigSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelee.getSample(sam).addSystematic(lesSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelee.getSample(sam).addSystematic(lermsSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelee.getSample(sam).addSystematic(leridSR2) for sam in ["WZ","Top","BG"]]
        sr2Channelee.addDiscoverySamples(["SR2_ee"],[1.],[-100.],[100.],[kMagenta])

    sr4Channelee = discovery.addChannel("cuts",["SR4_ee"],srNBins,srBinLow,srBinHigh)
    sr4Channelee.addSystematic(jesSR4)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in sr4Channelee.getSystematic(jesSR4.name)]
    if moreSyst:
        [sr4Channelee.getSample(sam).addSystematic(lepSR4) for sam in ["WZ","Top","BG"]]
    
    if fullSyst:
        [sr4Channelee.getSample(sam).addSystematic(metcoSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelee.getSample(sam).addSystematic(metpuSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelee.getSample(sam).addSystematic(trigSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelee.getSample(sam).addSystematic(lesSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelee.getSample(sam).addSystematic(lermsSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelee.getSample(sam).addSystematic(leridSR4) for sam in ["WZ","Top","BG"]]
        sr4Channelee.addDiscoverySamples(["SR4_ee"],[1.],[-100.],[100.],[kMagenta])

    sr2Channelemu = discovery.addChannel("cuts",["SR2_emu"],srNBins,srBinLow,srBinHigh)
    sr2Channelemu.addSystematic(jesSR2)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in sr2Channelemu.getSystematic(jesSR2.name)]
    if moreSyst:
        [sr2Channelemu.getSample(sam).addSystematic(lepSR2) for sam in ["WZ","Top","BG"]]
    
    if fullSyst:
        [sr2Channelemu.getSample(sam).addSystematic(metcoSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelemu.getSample(sam).addSystematic(metpuSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelemu.getSample(sam).addSystematic(trigSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelemu.getSample(sam).addSystematic(lesSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelemu.getSample(sam).addSystematic(lermsSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelemu.getSample(sam).addSystematic(leridSR2) for sam in ["WZ","Top","BG"]]
        sr2Channelemu.addDiscoverySamples(["SR2_emu"],[1.],[-100.],[100.],[kMagenta])

    sr4Channelemu = discovery.addChannel("cuts",["SR4_emu"],srNBins,srBinLow,srBinHigh)
    sr4Channelemu.addSystematic(jesSR4)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in sr4Channelemu.getSystematic(jesSR4.name)]
    if moreSyst:
        [sr4Channelemu.getSample(sam).addSystematic(lepSR4) for sam in ["WZ","Top","BG"]]
    
    if fullSyst:
        [sr4Channelemu.getSample(sam).addSystematic(metcoSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelemu.getSample(sam).addSystematic(metpuSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelemu.getSample(sam).addSystematic(trigSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelemu.getSample(sam).addSystematic(lesSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelemu.getSample(sam).addSystematic(lermsSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelemu.getSample(sam).addSystematic(leridSR4) for sam in ["WZ","Top","BG"]]
        sr4Channelemu.addDiscoverySamples(["SR4_emu"],[1.],[-100.],[100.],[kMagenta])


    sr2Channelmumu = discovery.addChannel("cuts",["SR2_mumu"],srNBins,srBinLow,srBinHigh)
    sr2Channelmumu.addSystematic(jesSR2)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in sr2Channelmumu.getSystematic(jesSR2.name)]
    if moreSyst:
        [sr2Channelmumu.getSample(sam).addSystematic(lepSR2) for sam in ["WZ","Top","BG"]]
    
    if fullSyst:
        [sr2Channelmumu.getSample(sam).addSystematic(metcoSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelmumu.getSample(sam).addSystematic(metpuSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelmumu.getSample(sam).addSystematic(trigSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelmumu.getSample(sam).addSystematic(lesSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelmumu.getSample(sam).addSystematic(lermsSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelmumu.getSample(sam).addSystematic(leridSR2) for sam in ["WZ","Top","BG"]]
        sr2Channelmumu.addDiscoverySamples(["SR2_mumu"],[1.],[-100.],[100.],[kMagenta])

    sr4Channelmumu = discovery.addChannel("cuts",["SR4_mumu"],srNBins,srBinLow,srBinHigh)
    sr4Channelmumu.addSystematic(jesSR4)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in sr4Channelmumu.getSystematic(jesSR4.name)]
    if moreSyst:
        [sr4Channelmumu.getSample(sam).addSystematic(lepSR4) for sam in ["WZ","Top","BG"]]
    
    if fullSyst:
        [sr4Channelmumu.getSample(sam).addSystematic(metcoSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelmumu.getSample(sam).addSystematic(metpuSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelmumu.getSample(sam).addSystematic(trigSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelmumu.getSample(sam).addSystematic(lesSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelmumu.getSample(sam).addSystematic(lermsSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelmumu.getSample(sam).addSystematic(leridSR4) for sam in ["WZ","Top","BG"]]
        sr4Channelmumu.addDiscoverySamples(["SR4_mumu"],[1.],[-100.],[100.],[kMagenta])


    discovery.setSignalChannels([sr2Channelee,sr4Channelee,sr2Channelemu,sr4Channelemu,sr2Channelmumu,sr4Channelmumu])
    measD=discovery.addMeasurement(name="DiscoveryMeasurement",lumi=1.0,lumiErr=0.039)

    measD.addParamSetting("mu_BG",True,1)
    measD.addPOI("mu_SR2_"+discoverychannel)

if doDiscoverySR4:
    discovery = configMgr.addTopLevelXMLClone(bkgOnly,"DiscoverySR4"+discoverychannel)
    sr2Channelee = discovery.addChannel("cuts",["SR2_ee"],srNBins,srBinLow,srBinHigh)
    sr2Channelee.addSystematic(jesSR2)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in sr2Channelee.getSystematic(jesSR2.name)]
    if moreSyst:
        [sr2Channelee.getSample(sam).addSystematic(lepSR2) for sam in ["WZ","Top","BG"]]
    
    if fullSyst:
        [sr2Channelee.getSample(sam).addSystematic(metcoSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelee.getSample(sam).addSystematic(metpuSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelee.getSample(sam).addSystematic(trigSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelee.getSample(sam).addSystematic(lesSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelee.getSample(sam).addSystematic(lermsSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelee.getSample(sam).addSystematic(leridSR2) for sam in ["WZ","Top","BG"]]
        sr2Channelee.addDiscoverySamples(["SR2_ee"],[1.],[-100.],[100.],[kMagenta])

    sr4Channelee = discovery.addChannel("cuts",["SR4_ee"],srNBins,srBinLow,srBinHigh)
    sr4Channelee.addSystematic(jesSR4)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in sr4Channelee.getSystematic(jesSR4.name)]
    if moreSyst:
        [sr4Channelee.getSample(sam).addSystematic(lepSR4) for sam in ["WZ","Top","BG"]]
    
    if fullSyst:
        [sr4Channelee.getSample(sam).addSystematic(metcoSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelee.getSample(sam).addSystematic(metpuSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelee.getSample(sam).addSystematic(trigSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelee.getSample(sam).addSystematic(lesSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelee.getSample(sam).addSystematic(lermsSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelee.getSample(sam).addSystematic(leridSR4) for sam in ["WZ","Top","BG"]]
        sr4Channelee.addDiscoverySamples(["SR4_ee"],[1.],[-100.],[100.],[kMagenta])
    sr2Channelemu = discovery.addChannel("cuts",["SR2_emu"],srNBins,srBinLow,srBinHigh)
    sr2Channelemu.addSystematic(jesSR2)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in sr2Channelemu.getSystematic(jesSR2.name)]
    if moreSyst:
        [sr2Channelemu.getSample(sam).addSystematic(lepSR2) for sam in ["WZ","Top","BG"]]
    
    if fullSyst:
        [sr2Channelemu.getSample(sam).addSystematic(metcoSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelemu.getSample(sam).addSystematic(metpuSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelemu.getSample(sam).addSystematic(trigSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelemu.getSample(sam).addSystematic(lesSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelemu.getSample(sam).addSystematic(lermsSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelemu.getSample(sam).addSystematic(leridSR2) for sam in ["WZ","Top","BG"]]
        sr2Channelemu.addDiscoverySamples(["SR2_emu"],[1.],[-100.],[100.],[kMagenta])

    sr4Channelemu = discovery.addChannel("cuts",["SR4_emu"],srNBins,srBinLow,srBinHigh)
    sr4Channelemu.addSystematic(jesSR4)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in sr4Channelemu.getSystematic(jesSR4.name)]
    if moreSyst:
        [sr4Channelemu.getSample(sam).addSystematic(lepSR4) for sam in ["WZ","Top","BG"]]
    
    if fullSyst:
        [sr4Channelemu.getSample(sam).addSystematic(metcoSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelemu.getSample(sam).addSystematic(metpuSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelemu.getSample(sam).addSystematic(trigSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelemu.getSample(sam).addSystematic(lesSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelemu.getSample(sam).addSystematic(lermsSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelemu.getSample(sam).addSystematic(leridSR4) for sam in ["WZ","Top","BG"]]
        sr4Channelemu.addDiscoverySamples(["SR4_emu"],[1.],[-100.],[100.],[kMagenta])


    sr2Channelmumu = discovery.addChannel("cuts",["SR2_mumu"],srNBins,srBinLow,srBinHigh)
    sr2Channelmumu.addSystematic(jesSR2)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in sr2Channelmumu.getSystematic(jesSR2.name)]
    if moreSyst:
        [sr2Channelmumu.getSample(sam).addSystematic(lepSR2) for sam in ["WZ","Top","BG"]]
    
    if fullSyst:
        [sr2Channelmumu.getSample(sam).addSystematic(metcoSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelmumu.getSample(sam).addSystematic(metpuSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelmumu.getSample(sam).addSystematic(trigSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelmumu.getSample(sam).addSystematic(lesSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelmumu.getSample(sam).addSystematic(lermsSR2) for sam in ["WZ","Top","BG"]]
        [sr2Channelmumu.getSample(sam).addSystematic(leridSR2) for sam in ["WZ","Top","BG"]]
        sr2Channelmumu.addDiscoverySamples(["SR2_mumu"],[1.],[-100.],[100.],[kMagenta])

    sr4Channelmumu = discovery.addChannel("cuts",["SR4_mumu"],srNBins,srBinLow,srBinHigh)
    sr4Channelmumu.addSystematic(jesSR4)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in sr4Channelmumu.getSystematic(jesSR4.name)]
    if moreSyst:
        [sr4Channelmumu.getSample(sam).addSystematic(lepSR4) for sam in ["WZ","Top","BG"]]
    
    if fullSyst:
        [sr4Channelmumu.getSample(sam).addSystematic(metcoSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelmumu.getSample(sam).addSystematic(metpuSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelmumu.getSample(sam).addSystematic(trigSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelmumu.getSample(sam).addSystematic(lesSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelmumu.getSample(sam).addSystematic(lermsSR4) for sam in ["WZ","Top","BG"]]
        [sr4Channelmumu.getSample(sam).addSystematic(leridSR4) for sam in ["WZ","Top","BG"]]
        sr4Channelmumu.addDiscoverySamples(["SR4_mumu"],[1.],[-100.],[100.],[kMagenta])


    discovery.setSignalChannels([sr2Channelee,sr4Channelee,sr2Channelemu,sr4Channelemu,sr2Channelmumu,sr4Channelmumu])
    measD=discovery.addMeasurement(name="DiscoveryMeasurement",lumi=1.0,lumiErr=0.039)
    measD.addParamSetting("mu_BG",True,1)
    measD.addPOI("mu_SR4_"+discoverychannel)


#-----------------------------
# Exclusion fits (MSUGRA grid)
#-----------------------------

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
#     "GMSB_3_2d_35_250_3_2_1_1",	
#     "GMSB_3_2d_35_250_3_5_1_1",	
#     "GMSB_3_2d_35_250_3_10_1_1",	
#     "GMSB_3_2d_35_250_3_15_1_1",	
#     "GMSB_3_2d_35_250_3_20_1_1",	
#     "GMSB_3_2d_35_250_3_25_1_1",	
#     "GMSB_3_2d_35_250_3_30_1_1",	
#     "GMSB_3_2d_35_250_3_35_1_1",	
#     "GMSB_3_2d_35_250_3_40_1_1",	
#     "GMSB_3_2d_35_250_3_42_1_1"
#     ]
#sigSamples=[]

#sigSamples=['SU_100_120_0_10_P', 'SU_100_150_0_10_P', 'SU_100_180_0_10_P', 'SU_100_210_0_10_P', 'SU_100_240_0_10_P', 'SU_100_300_0_10_P', 'SU_100_330_0_10_P', 'SU_100_360_0_10_P', 'SU_100_390_0_10_P', 'SU_100_420_0_10_P', 'SU_100_450_0_10_P', 'SU_100_480_0_10_P', 'SU_100_510_0_10_P', 'SU_100_540_0_10_P', 'SU_100_60_0_10_P', 'SU_100_90_0_10_P', 'SU_1060_120_0_10_P', 'SU_1060_150_0_10_P', 'SU_1060_180_0_10_P', 'SU_1060_210_0_10_P', 'SU_1060_240_0_10_P', 'SU_1060_270_0_10_P', 'SU_1060_300_0_10_P', 'SU_1060_30_0_10_P', 'SU_1060_330_0_10_P', 'SU_1060_360_0_10_P', 'SU_1060_390_0_10_P', 'SU_1060_420_0_10_P', 'SU_1060_450_0_10_P', 'SU_1060_480_0_10_P', 'SU_1060_510_0_10_P', 'SU_1060_540_0_10_P', 'SU_1060_570_0_10_P', 'SU_1060_600_0_10_P', 'SU_1060_60_0_10_P', 'SU_1060_90_0_10_P', 'SU_1140_120_0_10_P', 'SU_1140_150_0_10_P', 'SU_1140_180_0_10_P', 'SU_1140_210_0_10_P', 'SU_1140_240_0_10_P', 'SU_1140_270_0_10_P', 'SU_1140_300_0_10_P', 'SU_1140_30_0_10_P', 'SU_1140_330_0_10_P', 'SU_1140_360_0_10_P', 'SU_1140_390_0_10_P', 'SU_1140_420_0_10_P', 'SU_1140_450_0_10_P', 'SU_1140_480_0_10_P', 'SU_1140_510_0_10_P', 'SU_1140_540_0_10_P', 'SU_1140_570_0_10_P', 'SU_1140_600_0_10_P', 'SU_1140_60_0_10_P', 'SU_1140_90_0_10_P', 'SU_1220_120_0_10_P', 'SU_1220_150_0_10_P', 'SU_1220_180_0_10_P', 'SU_1220_210_0_10_P', 'SU_1220_240_0_10_P', 'SU_1220_270_0_10_P', 'SU_1220_300_0_10_P', 'SU_1220_30_0_10_P', 'SU_1220_330_0_10_P', 'SU_1220_360_0_10_P', 'SU_1220_390_0_10_P', 'SU_1220_420_0_10_P', 'SU_1220_450_0_10_P', 'SU_1220_480_0_10_P', 'SU_1220_510_0_10_P', 'SU_1220_540_0_10_P', 'SU_1220_570_0_10_P', 'SU_1220_600_0_10_P', 'SU_1220_60_0_10_P', 'SU_1220_90_0_10_P', 'SU_1300_120_0_10_P', 'SU_1300_150_0_10_P', 'SU_1300_180_0_10_P', 'SU_1300_210_0_10_P', 'SU_1300_240_0_10_P', 'SU_1300_270_0_10_P', 'SU_1300_300_0_10_P', 'SU_1300_30_0_10_P', 'SU_1300_330_0_10_P', 'SU_1300_360_0_10_P', 'SU_1300_390_0_10_P', 'SU_1300_420_0_10_P', 'SU_1300_450_0_10_P', 'SU_1300_480_0_10_P', 'SU_1300_510_0_10_P', 'SU_1300_540_0_10_P', 'SU_1300_570_0_10_P', 'SU_1300_600_0_10_P', 'SU_1300_60_0_10_P', 'SU_1300_90_0_10_P', 'SU_1380_120_0_10_P', 'SU_1380_150_0_10_P', 'SU_1380_180_0_10_P', 'SU_1380_210_0_10_P', 'SU_1380_240_0_10_P', 'SU_1380_270_0_10_P', 'SU_1380_300_0_10_P', 'SU_1380_330_0_10_P', 'SU_1380_360_0_10_P', 'SU_1380_390_0_10_P', 'SU_1380_420_0_10_P', 'SU_1380_450_0_10_P', 'SU_1380_480_0_10_P', 'SU_1380_510_0_10_P', 'SU_1380_540_0_10_P', 'SU_1380_570_0_10_P', 'SU_1380_600_0_10_P', 'SU_1380_60_0_10_P', 'SU_1380_90_0_10_P', 'SU_1460_120_0_10_P', 'SU_1460_150_0_10_P', 'SU_1460_180_0_10_P', 'SU_1460_210_0_10_P', 'SU_1460_240_0_10_P', 'SU_1460_270_0_10_P', 'SU_1460_300_0_10_P', 'SU_1460_330_0_10_P', 'SU_1460_360_0_10_P', 'SU_1460_390_0_10_P', 'SU_1460_420_0_10_P', 'SU_1460_450_0_10_P', 'SU_1460_480_0_10_P', 'SU_1460_510_0_10_P', 'SU_1460_540_0_10_P', 'SU_1460_570_0_10_P', 'SU_1460_600_0_10_P', 'SU_1460_60_0_10_P', 'SU_1460_90_0_10_P', 'SU_180_120_0_10_P', 'SU_180_150_0_10_P', 'SU_180_180_0_10_P', 'SU_180_210_0_10_P', 'SU_180_240_0_10_P', 'SU_180_270_0_10_P', 'SU_180_300_0_10_P', 'SU_180_330_0_10_P', 'SU_180_360_0_10_P', 'SU_180_390_0_10_P', 'SU_180_420_0_10_P', 'SU_180_450_0_10_P', 'SU_180_480_0_10_P', 'SU_180_510_0_10_P', 'SU_180_540_0_10_P', 'SU_180_570_0_10_P', 'SU_180_600_0_10_P', 'SU_180_60_0_10_P', 'SU_180_90_0_10_P', 'SU_1960_120_0_10_P', 'SU_1960_150_0_10_P', 'SU_1960_180_0_10_P', 'SU_1960_210_0_10_P', 'SU_1960_240_0_10_P', 'SU_1960_270_0_10_P', 'SU_1960_300_0_10_P', 'SU_1960_330_0_10_P', 'SU_1960_360_0_10_P', 'SU_1960_390_0_10_P', 'SU_1960_420_0_10_P', 'SU_1960_450_0_10_P', 'SU_1960_480_0_10_P', 'SU_1960_510_0_10_P', 'SU_1960_540_0_10_P', 'SU_1960_570_0_10_P', 'SU_1960_600_0_10_P', 'SU_1960_90_0_10_P', 'SU_2460_150_0_10_P', 'SU_2460_180_0_10_P', 'SU_2460_210_0_10_P', 'SU_2460_240_0_10_P', 'SU_2460_270_0_10_P', 'SU_2460_300_0_10_P', 'SU_2460_330_0_10_P', 'SU_2460_360_0_10_P', 'SU_2460_390_0_10_P', 'SU_2460_420_0_10_P', 'SU_2460_450_0_10_P', 'SU_2460_480_0_10_P', 'SU_2460_510_0_10_P', 'SU_2460_540_0_10_P', 'SU_2460_570_0_10_P', 'SU_2460_600_0_10_P', 'SU_260_120_0_10_P', 'SU_260_150_0_10_P', 'SU_260_180_0_10_P', 'SU_260_210_0_10_P', 'SU_260_240_0_10_P', 'SU_260_270_0_10_P', 'SU_260_300_0_10_P', 'SU_260_330_0_10_P', 'SU_260_360_0_10_P', 'SU_260_390_0_10_P', 'SU_260_420_0_10_P', 'SU_260_450_0_10_P', 'SU_260_480_0_10_P', 'SU_260_510_0_10_P', 'SU_260_540_0_10_P', 'SU_260_570_0_10_P', 'SU_260_600_0_10_P', 'SU_260_60_0_10_P', 'SU_260_90_0_10_P', 'SU_2960_210_0_10_P', 'SU_2960_240_0_10_P', 'SU_2960_270_0_10_P', 'SU_2960_300_0_10_P', 'SU_2960_330_0_10_P', 'SU_2960_360_0_10_P', 'SU_2960_390_0_10_P', 'SU_2960_420_0_10_P', 'SU_2960_450_0_10_P', 'SU_2960_480_0_10_P', 'SU_2960_510_0_10_P', 'SU_2960_540_0_10_P', 'SU_2960_570_0_10_P', 'SU_2960_600_0_10_P', 'SU_340_120_0_10_P', 'SU_340_150_0_10_P', 'SU_340_180_0_10_P', 'SU_340_210_0_10_P', 'SU_340_240_0_10_P', 'SU_340_270_0_10_P', 'SU_340_300_0_10_P', 'SU_340_330_0_10_P', 'SU_340_360_0_10_P', 'SU_340_390_0_10_P', 'SU_340_420_0_10_P', 'SU_340_450_0_10_P', 'SU_340_480_0_10_P', 'SU_340_510_0_10_P', 'SU_340_540_0_10_P', 'SU_340_570_0_10_P', 'SU_340_600_0_10_P', 'SU_340_60_0_10_P', 'SU_340_90_0_10_P', 'SU_420_120_0_10_P', 'SU_420_150_0_10_P', 'SU_420_180_0_10_P', 'SU_420_210_0_10_P', 'SU_420_240_0_10_P', 'SU_420_270_0_10_P', 'SU_420_300_0_10_P', 'SU_420_330_0_10_P', 'SU_420_360_0_10_P', 'SU_420_390_0_10_P', 'SU_420_420_0_10_P', 'SU_420_450_0_10_P', 'SU_420_480_0_10_P', 'SU_420_510_0_10_P', 'SU_420_540_0_10_P', 'SU_420_570_0_10_P', 'SU_420_600_0_10_P', 'SU_420_60_0_10_P', 'SU_420_90_0_10_P', 'SU_500_120_0_10_P', 'SU_500_150_0_10_P', 'SU_500_180_0_10_P', 'SU_500_210_0_10_P', 'SU_500_240_0_10_P', 'SU_500_270_0_10_P', 'SU_500_300_0_10_P', 'SU_500_30_0_10_P', 'SU_500_330_0_10_P', 'SU_500_360_0_10_P', 'SU_500_390_0_10_P', 'SU_500_420_0_10_P', 'SU_500_450_0_10_P', 'SU_500_480_0_10_P', 'SU_500_510_0_10_P', 'SU_500_540_0_10_P', 'SU_500_570_0_10_P', 'SU_500_600_0_10_P', 'SU_500_60_0_10_P', 'SU_500_90_0_10_P', 'SU_580_120_0_10_P', 'SU_580_150_0_10_P', 'SU_580_180_0_10_P', 'SU_580_210_0_10_P', 'SU_580_240_0_10_P', 'SU_580_270_0_10_P', 'SU_580_300_0_10_P', 'SU_580_30_0_10_P', 'SU_580_330_0_10_P', 'SU_580_360_0_10_P', 'SU_580_390_0_10_P', 'SU_580_420_0_10_P', 'SU_580_450_0_10_P', 'SU_580_480_0_10_P', 'SU_580_510_0_10_P', 'SU_580_540_0_10_P', 'SU_580_570_0_10_P', 'SU_580_600_0_10_P', 'SU_580_60_0_10_P', 'SU_580_90_0_10_P', 'SU_660_120_0_10_P', 'SU_660_150_0_10_P', 'SU_660_180_0_10_P', 'SU_660_210_0_10_P', 'SU_660_240_0_10_P', 'SU_660_270_0_10_P', 'SU_660_300_0_10_P', 'SU_660_30_0_10_P', 'SU_660_330_0_10_P', 'SU_660_360_0_10_P', 'SU_660_390_0_10_P', 'SU_660_420_0_10_P', 'SU_660_450_0_10_P', 'SU_660_480_0_10_P', 'SU_660_510_0_10_P', 'SU_660_540_0_10_P', 'SU_660_570_0_10_P', 'SU_660_600_0_10_P', 'SU_660_60_0_10_P', 'SU_660_90_0_10_P', 'SU_740_120_0_10_P', 'SU_740_150_0_10_P', 'SU_740_180_0_10_P', 'SU_740_210_0_10_P', 'SU_740_240_0_10_P', 'SU_740_270_0_10_P', 'SU_740_300_0_10_P', 'SU_740_30_0_10_P', 'SU_740_330_0_10_P', 'SU_740_360_0_10_P', 'SU_740_390_0_10_P', 'SU_740_420_0_10_P', 'SU_740_450_0_10_P', 'SU_740_480_0_10_P', 'SU_740_510_0_10_P', 'SU_740_540_0_10_P', 'SU_740_570_0_10_P', 'SU_740_600_0_10_P', 'SU_740_60_0_10_P', 'SU_740_90_0_10_P', 'SU_820_120_0_10_P', 'SU_820_150_0_10_P', 'SU_820_180_0_10_P', 'SU_820_210_0_10_P', 'SU_820_240_0_10_P', 'SU_820_270_0_10_P', 'SU_820_300_0_10_P', 'SU_820_30_0_10_P', 'SU_820_330_0_10_P', 'SU_820_360_0_10_P', 'SU_820_390_0_10_P', 'SU_820_420_0_10_P', 'SU_820_450_0_10_P', 'SU_820_480_0_10_P', 'SU_820_510_0_10_P', 'SU_820_540_0_10_P', 'SU_820_570_0_10_P', 'SU_820_600_0_10_P', 'SU_820_60_0_10_P', 'SU_820_90_0_10_P', 'SU_900_120_0_10_P', 'SU_900_150_0_10_P', 'SU_900_180_0_10_P', 'SU_900_210_0_10_P', 'SU_900_240_0_10_P', 'SU_900_270_0_10_P', 'SU_900_300_0_10_P', 'SU_900_30_0_10_P', 'SU_900_330_0_10_P', 'SU_900_360_0_10_P', 'SU_900_390_0_10_P', 'SU_900_420_0_10_P', 'SU_900_450_0_10_P', 'SU_900_480_0_10_P', 'SU_900_510_0_10_P', 'SU_900_540_0_10_P', 'SU_900_570_0_10_P', 'SU_900_600_0_10_P', 'SU_900_60_0_10_P', 'SU_900_90_0_10_P', 'SU_980_120_0_10_P', 'SU_980_150_0_10_P', 'SU_980_180_0_10_P', 'SU_980_210_0_10_P', 'SU_980_240_0_10_P', 'SU_980_270_0_10_P', 'SU_980_300_0_10_P', 'SU_980_30_0_10_P', 'SU_980_330_0_10_P', 'SU_980_360_0_10_P', 'SU_980_390_0_10_P', 'SU_980_420_0_10_P', 'SU_980_450_0_10_P', 'SU_980_480_0_10_P', 'SU_980_510_0_10_P', 'SU_980_540_0_10_P', 'SU_980_570_0_10_P', 'SU_980_600_0_10_P', 'SU_980_60_0_10_P', 'SU_980_90_0_10_P']

if not doExclusion:
    sigSamples=[]

for sig in sigSamples:
    myTopLvl = configMgr.addTopLevelXMLClone(bkgOnly,"dilepton_%s"%sig)
    sigSample = Sample(sig,kPink)
    sigSample.setNormByTheory()
    sigSample.setNormFactor("mu_SIG",0.,0.,5.)
    if useXsecUnc:
        sigSample.addSystematic(xsecSig)
    myTopLvl.addSamples(sigSample)
    myTopLvl.setSignalSample(sigSample)

    # Reassign merging for shapeSys
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in myTopLvl.getChannel("nJet",["ZR_ee"]).getSystematic(jesZR.name)]
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in myTopLvl.getChannel("nJet",["ZR_mumu"]).getSystematic(jesZR.name)]
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in myTopLvl.getChannel("nJet",["TR_ee"]).getSystematic(jesTR.name)]
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in myTopLvl.getChannel("nJet",["TR_emu"]).getSystematic(jesTR.name)]
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in myTopLvl.getChannel("nJet",["TR_mumu"]).getSystematic(jesTR.name)]

    meffChannel_ee = myTopLvl.addChannel("meffInc",["SR2_ee"],meffNBins,meffBinLow,meffBinHigh)
    meffChannel_ee.useOverflowBin=True
    meffChannel_ee.addSystematic(jesSR2)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in meffChannel_ee.getSystematic(jesSR2.name)]
    if moreSyst:
        meffChannel_ee.addSystematic(metcoSR2)
        meffChannel_ee.addSystematic(metpuSR2)
    if fullSyst:
        meffChannel_ee.addSystematic(trigSR2)
        meffChannel_ee.addSystematic(lepSR2)
        [meffChannel_ee.getSample(sam).addSystematic(lesSR2) for sam in ["WZ","Top","BG"]]
        [meffChannel_ee.getSample(sam).addSystematic(lermsSR2) for sam in ["WZ","Top","BG"]]
        [meffChannel_ee.getSample(sam).addSystematic(leridSR2) for sam in ["WZ","Top","BG"]]


    meffChannel_emu = myTopLvl.addChannel("meffInc",["SR2_emu"],meffNBins,meffBinLow,meffBinHigh)
    meffChannel_emu.useOverflowBin=True
    meffChannel_emu.addSystematic(jesSR2)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in meffChannel_emu.getSystematic(jesSR2.name)]
    if moreSyst:
        meffChannel_emu.addSystematic(metcoSR2)
        meffChannel_emu.addSystematic(metpuSR2)
    if fullSyst:
        meffChannel_emu.addSystematic(trigSR2)
        meffChannel_emu.addSystematic(lepSR2)
        [meffChannel_emu.getSample(sam).addSystematic(lesSR2) for sam in ["WZ","Top","BG"]]
        [meffChannel_emu.getSample(sam).addSystematic(lermsSR2) for sam in ["WZ","Top","BG"]]
        [meffChannel_emu.getSample(sam).addSystematic(leridSR2) for sam in ["WZ","Top","BG"]]
    

    meffChannel_mumu = myTopLvl.addChannel("meffInc",["SR2_mumu"],meffNBins,meffBinLow,meffBinHigh)
    meffChannel_mumu.useOverflowBin=True
    meffChannel_mumu.addSystematic(jesSR2)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in meffChannel_mumu.getSystematic(jesSR2.name)]
    if moreSyst:
        meffChannel_mumu.addSystematic(metcoSR2)
        meffChannel_mumu.addSystematic(metpuSR2)
    if fullSyst:
        meffChannel_mumu.addSystematic(trigSR2)
        meffChannel_mumu.addSystematic(lepSR2)
        [meffChannel_mumu.getSample(sam).addSystematic(lesSR2) for sam in ["WZ","Top","BG"]]
        [meffChannel_mumu.getSample(sam).addSystematic(lermsSR2) for sam in ["WZ","Top","BG"]]
        [meffChannel_mumu.getSample(sam).addSystematic(leridSR2) for sam in ["WZ","Top","BG"]]


    myTopLvl.setSignalChannels([meffChannel_ee,meffChannel_emu,meffChannel_mumu])
    




