################################################################
## In principle all you have to setup is defined in this file ##
################################################################

from configManager import configMgr
from ROOT import kBlack,kWhite,kGray,kRed,kPink,kMagenta,kViolet,kBlue,kAzure,kCyan,kTeal,kGreen,kSpring,kYellow,kOrange
from configWriter import TopLevelXML,Measurement,ChannelXML,Sample
from systematic import Systematic

from ROOT import gROOT
gROOT.LoadMacro("./macros/AtlasStyle.C")
import ROOT
ROOT.SetAtlasStyle()

gROOT.ProcessLine("gErrorIgnoreLevel=10001;")
#gROOT.SetBatch(True)
#configMgr.plotHistos = True

rel17=True

useStat=True

# First define HistFactory attributes
configMgr.analysisName = "MyOneLeptonKtScaleFit"

# Scaling calculated by outputLumi / inputLumi
configMgr.inputLumi = 1.917  # Luminosity of input TTree after weighting
configMgr.outputLumi = 1.917   # Luminosity required for output histograms
configMgr.setLumiUnits("fb-1")

if rel17:
    configMgr.inputLumi = 0.001
    configMgr.outputLumi = 4.713 #1.917   # Luminosity required for output histograms
    configMgr.analysisName+="R17" 

configMgr.outputFileName = "results/"+configMgr.analysisName+"_Output.root"

# setting the parameters of the hypothesis test
#configMgr.doHypoTest=False
#configMgr.nTOYs=1000
#configMgr.calculatorType=0
#configMgr.testStatType=3
#configMgr.nPoints=20


# Set the files to read from
if configMgr.readFromTree:
    if rel17:
        configMgr.inputFileNames = []
        #h1l
        configMgr.inputFileNames.append("samples/SusyFitterTree_OneEle_Rel17_BG_Syst.root")
        configMgr.inputFileNames.append("samples/SusyFitterTree_OneMu_Rel17_BG_Syst.root")
        #s1l
        configMgr.inputFileNames.append("samples/SusyFitterTree_OneSoftEle_Rel17_BG_CrossCheck.root")
        configMgr.inputFileNames.append("samples/SusyFitterTree_OneSoftMuo_Rel17_BG_CrossCheck.root")
        #mSUGRA
        configMgr.inputFileNames.append("samples/SusyFitterTree_p832_v4.root")
        #1-step simplified model
        configMgr.inputFileNames.append("samples/SusyFitterTree_p832_GG-One-Step_soft_v0.root")
    else:
        configMgr.inputFileNames = ["samples/SusyFitterTree_OneEle.root","samples/SusyFitterTree_OneMu.root"]
else:
    configMgr.inputFileNames = ["data/"+configMgr.analysisName+".root"]

# Dictionnary of cuts for Tree->hist
configMgr.cutsDict["WR"] = "(AnalysisType==1 || AnalysisType==2) && met>30 && met<120 && mt>40 && mt<80 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc>400"
configMgr.cutsDict["TR"] = "(AnalysisType==1 || AnalysisType==2) && met>30 && met<120 && mt>40 && mt<80 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && meffInc>400"
configMgr.cutsDict["VR"] = "(AnalysisType==1 || AnalysisType==2) && met>120 && met<250 && mt>80 && jet1Pt>80 && jet3Pt>25 && meffInc>400"
configMgr.cutsDict["VR2"] = "(AnalysisType==1 || AnalysisType==2) && met<250 && mt>80 && jet1Pt>80 && jet3Pt>25 && meffInc>400"
configMgr.cutsDict["S3"] = "(AnalysisType==1 || AnalysisType==2) && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25 && jet4Pt<80"
configMgr.cutsDict["S4"] = "(AnalysisType==1 || AnalysisType==2) && met>250 && mt>100 && met/meff4Jet>0.2 && jet4Pt>80"
configMgr.cutsDict["SS"] = "(AnalysisType==1 || AnalysisType==2) && met>250 && mt>100 && jet1Pt>120 && jet2Pt>25"

d=configMgr.cutsDict
configMgr.cutsDict["SR3jT"] = d["S3"]+"&& meffInc>1200"
configMgr.cutsDict["SR4jT"] = d["S4"]+"&& meffInc>800"
configMgr.cutsDict["SR1s2j"] = d["SS"]+"&& met/meffInc>0.3"

# Dictionnary of cuts for Tree->hist in MeV
cutsDictMeV = {}
cutsDictMeV["WR"] = "(AnalysisType==1 || AnalysisType==2) && met>30000 && met<120000 && mt>40000 && mt<80000 && nB3Jet==0 && jet1Pt>80000 && jet3Pt>25000 && meffInc>400000"
cutsDictMeV["TR"] = "(AnalysisType==1 || AnalysisType==2) && met>30000 && met<120000 && mt>40000 && mt<80000 && nB3Jet>0 && jet1Pt>80000 && jet3Pt>25000 && meffInc>400000"
cutsDictMeV["VR"] = "(AnalysisType==1 || AnalysisType==2) && met>120000 && met<250000 && mt>80000 && jet1Pt>80000 && jet3Pt>25000 && meffInc>400000"
cutsDictMeV["VR2"] = "(AnalysisType==1 || AnalysisType==2) && met<250000 && mt>80000 && jet1Pt>80000 && jet3Pt>25000 && meffInc>400000"
cutsDictMeV["S3"] = "(AnalysisType==1 || AnalysisType==2) && met>250000 && mt>100000 && met/meff3Jet>0.3 && jet1Pt>100000 && jet3Pt>25000 && jet4Pt<80000"
cutsDictMeV["S4"] = "(AnalysisType==1 || AnalysisType==2) && met>250000 && mt>100000 && met/meff4Jet>0.2 && jet4Pt>80000"
cutsDictMeV["SS"] = "(AnalysisType==1 || AnalysisType==2) && met>250000 && mt>100000 && jet1Pt>120000 && jet2Pt>25000"

d=cutsDictMeV
cutsDictMeV["SR3jT"] = d["S3"]+"&& meffInc>1200000"
cutsDictMeV["SR4jT"] = d["S4"]+"&& meffInc>800000"
cutsDictMeV["SR1s2j"] = d["SS"]+"&& met/meffInc>0.3"

# Tuples of nominal weights without and with b-jet selection
configMgr.weights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight3Jet")

xsecSigHighWeights = ("genWeightUp","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight3Jet")
xsecSigLowWeights = ("genWeightDown","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight3Jet")

# For weight-based systematic
ktScaleWHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ktfacUpWeightW","bTagWeight3Jet")
ktScaleWLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ktfacDownWeightW","bTagWeight3Jet")

ktScaleTopHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ktfacUpWeightTop","bTagWeight3Jet")
ktScaleTopLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ktfacDownWeightTop","bTagWeight3Jet")

ptMinTopLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ptmin30WeightTop","bTagWeight3Jet")

ptMinWZLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ptmin30WeightW","bTagWeight3Jet")

bTagHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight3JetUp")
bTagLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight3JetDown")

pileupSystWeights = ("genWeight","pileupWeightSyst","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight3Jet")

# QCD weights without and with b-jet selection
configMgr.weightsQCD = "qcdWeight"
configMgr.weightsQCDWithB = "qcdBWeight"

#--------------------
# List of systematics
#--------------------

# KtScale uncertainty as histoSys - two-sided, no additional normalization
topKtScale = Systematic("KtScaleTop",configMgr.weights,ktScaleTopHighWeights,ktScaleTopLowWeights,"weight","normHistoSys")
wzKtScale = Systematic("KtScaleWZ",configMgr.weights,ktScaleWHighWeights,ktScaleWLowWeights,"weight","normHistoSys")

# PtMin uncertainty as histoSysLow - one-sided (expect reduction in yield), no additional normalization
topPtMin = Systematic("PtMinTop",configMgr.weights,ptMinTopLowWeights,ptMinTopLowWeights,"weight","normHistoSysOneSide")
wzPtMin = Systematic("PtMinWZ",configMgr.weights,ptMinWZLowWeights,ptMinWZLowWeights,"weight","normHistoSysOneSide")

# Signal XSec uncertainty as overallSys (pure yeild affect)
xsecSig = Systematic("XSS",configMgr.weights,xsecSigHighWeights,xsecSigLowWeights,"weight","overallSys")

# Pileup uncertainty as histoSys in each channel by applying weights at 0.9*<mu>
pileupWR = Systematic("PU",configMgr.weights,pileupSystWeights,pileupSystWeights,"weight","histoSysOneSide")
pileupTR = Systematic("PU",configMgr.weights,pileupSystWeights,pileupSystWeights,"weight","histoSysOneSide")
pileupS3 = Systematic("PU",configMgr.weights,pileupSystWeights,pileupSystWeights,"weight","histoSysOneSide")
pileupS4 = Systematic("PU",configMgr.weights,pileupSystWeights,pileupSystWeights,"weight","histoSysOneSide")
pileupS3T = Systematic("PU",configMgr.weights,pileupSystWeights,pileupSystWeights,"weight","histoSysOneSide")
pileupS4T = Systematic("PU",configMgr.weights,pileupSystWeights,pileupSystWeights,"weight","histoSysOneSide")

# B-tag uncertainty as overallSys in WR and TR
btagWR = Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","overallSys")
btagTR = Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","overallSys")

# JES uncertainty as shapeSys - one systematic per region (combine WR and TR), merge samples
jesWR = Systematic("JC","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesTR = Systematic("JC","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS3 = Systematic("J3","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS4 = Systematic("J4","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS3T = Systematic("J3T","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS4T = Systematic("J4T","_NoSys","_JESup","_JESdown","tree","shapeSys")

# JER uncertainty as one sided histoSys - Do not apply as data/MC is 1
jerWR = Systematic("JR","_NoSys","_JER","_JER","tree","histoSysOneSide")
jerTR = Systematic("JR","_NoSys","_JER","_JER","tree","histoSysOneSide")
jerS3 = Systematic("JR","_NoSys","_JER","_JER","tree","histoSysOneSide")
jerS4 = Systematic("JR","_NoSys","_JER","_JER","tree","histoSysOneSide")
jerS3T = Systematic("JR3T","_NoSys","_JER","_JER","tree","histoSysOneSide")
jerS4T = Systematic("JR4T","_NoSys","_JER","_JER","tree","histoSysOneSide")

# LES uncertainty as overallSys - one per channel
lesWR = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesTR = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesS3 = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesS4 = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
#lesS3T = Systematic("L3T","_NoSys","_LESup","_LESdown","tree","overallSys")
#lesS4T = Systematic("L4T","_NoSys","_LESup","_LESdown","tree","overallSys")

# LER with muon system as overallSys - one per channel
lermsWR = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsTR = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsS3 = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsS4 = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsS3T = Systematic("LRM3T","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsS4T = Systematic("LRM4T","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")

# LER with inner detector as overallSys - one per channel
leridWR = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridTR = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridS3 = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridS4 = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridS3T = Systematic("LRI3T","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridS4T = Systematic("LRI4T","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")

# MET cell-out uncertainty as overallSys - one per channel
metcoWR = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoTR = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoS3 = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoS4 = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoS3T = Systematic("MC3T","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoS4T = Systematic("MC4T","_NoSys","_METCOup","_METCOdown","tree","overallSys")

# MET pileup uncertainty as overallSys - one per channel
metpuWR = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","overallSys")
metpuTR = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","overallSys")
metpuS3 = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","overallSys")
metpuS4 = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","overallSys")
metpuS3T = Systematic("MP3T","_NoSys","_METPUup","_METPUdown","tree","overallSys")
metpuS4T = Systematic("MP4T","_NoSys","_METPUup","_METPUdown","tree","overallSys")

configMgr.nomName = "_NoSys"

# List of samples and their plotting colours
topSample = Sample("Top",kGreen-9)
topSample.setNormFactor("mu_Top",1.,0.,5.)
topSample.setStatConfig(useStat)
wzSample = Sample("WZ",kAzure+1)
wzSample.setNormFactor("mu_WZ",1.,0.,5.)
wzSample.setStatConfig(useStat)
bgSample = Sample("BG",kYellow-3)
bgSample.setNormFactor("mu_BG",1.,0.,5.)
bgSample.setStatConfig(useStat)
qcdSample = Sample("QCD",kGray+1)
qcdSample.setQCD(True,"histoSys")
qcdSample.setStatConfig(useStat)
dataSample = Sample("Data",kBlack)
dataSample.setData()

#Binnings
nJetBinLow = 3
nJetBinHighTR = 10
nJetBinHighWR = 10

nBJetBinLow = 0
nBJetBinHigh = 4

meffNBins = 6
meffBinLow = 400.
meffBinHigh = 1600.

lepPtNBins = 6
lepPtLow = 20.
lepPtHigh = 600.

srNBins = 1
srBinLow = 0.5
srBinHigh = 1.5

#************
#Bkg only fit
#************

bkt = configMgr.addTopLevelXML("BkgOnlyKt")
if useStat:
    bkt.statErrThreshold=0.1
else:
    bkt.statErrThreshold=None
bkt.addSamples([topSample,wzSample,qcdSample,bgSample,dataSample])

# Systematics to a applied globally within this topLevel
bkt.getSample("Top").addSystematic(topKtScale)
bkt.getSample("WZ").addSystematic(wzKtScale)
bkt.getSample("Top").addSystematic(topPtMin)
bkt.getSample("WZ").addSystematic(wzPtMin)

meas=bkt.addMeasurement(name="NormalMeasurement",lumi=1.0,lumiErr=0.039)
meas.addPOI("mu_SIG")
meas.addParamSetting("mu_BG",True,1)
"""
meas.addConstraintTerm("gamma_J3_bin_4","Gamma")
meas.addConstraintTerm("gamma_J3_bin_5","Gamma")
meas.addConstraintTerm("gamma_J4_bin_0","Gamma")
meas.addConstraintTerm("gamma_J4_bin_1","Gamma")
meas.addConstraintTerm("gamma_J4_bin_2","Gamma")
meas.addConstraintTerm("gamma_J4_bin_3","Gamma")
meas.addConstraintTerm("gamma_J4_bin_4","Gamma")
meas.addConstraintTerm("gamma_J4_bin_5","Gamma")
meas.addConstraintTerm("gamma_JT_bin_5","Gamma")
meas.addConstraintTerm("gamma_JW_bin_6","Gamma")
"""

#---------------------
# Constraining regions
#---------------------

# WR using nJet
nJetW = bkt.addChannel("nJet",["WR"],nJetBinHighWR-nJetBinLow,nJetBinLow,nJetBinHighWR)
nJetW.hasB = True
nJetW.addSystematic(jesWR)
[s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetW.getSystematic(jesWR.name)]
nJetW.addSystematic(btagWR)
[nJetW.getSample(sam).addSystematic(pileupWR) for sam in ["WZ","Top","BG"]]
nJetW.addSystematic(jerWR)
[nJetW.getSample(sam).addSystematic(lesWR) for sam in ["WZ","Top","BG"]]
[nJetW.getSample(sam).addSystematic(lermsWR) for sam in ["WZ","Top","BG"]]
[nJetW.getSample(sam).addSystematic(leridWR) for sam in ["WZ","Top","BG"]]
[nJetW.getSample(sam).addSystematic(metcoWR) for sam in ["WZ","Top","BG"]]
[nJetW.getSample(sam).addSystematic(metpuWR) for sam in ["WZ","Top","BG"]]

# TR using nJet
nJetT = bkt.addChannel("nJet",["TR"],nJetBinHighTR-nJetBinLow,nJetBinLow,nJetBinHighTR)
nJetT.hasB = True
nJetT.addSystematic(jesTR)
[s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetT.getSystematic(jesTR.name)]
nJetT.addSystematic(btagTR)
[nJetT.getSample(sam).addSystematic(pileupTR) for sam in ["WZ","Top","BG"]]
nJetT.addSystematic(jerTR)
[nJetT.getSample(sam).addSystematic(lesTR) for sam in ["WZ","Top","BG"]]
[nJetT.getSample(sam).addSystematic(lermsTR) for sam in ["WZ","Top","BG"]]
[nJetT.getSample(sam).addSystematic(leridTR) for sam in ["WZ","Top","BG"]]
[nJetT.getSample(sam).addSystematic(metcoTR) for sam in ["WZ","Top","BG"]]
[nJetT.getSample(sam).addSystematic(metpuTR) for sam in ["WZ","Top","BG"]]

bkt.setBkgConstrainChannels([nJetW,nJetT])

#-------------------
# Validation regions
#-------------------

# VR using nJet
#nJetVR = bkt.addChannel("nJet",["VR"],nJetBinHighTR-nJetBinLow,nJetBinLow,nJetBinHighTR)

# VR using nBJet
#nBJetVR = bkt.addChannel("nBJet",["VR"],nBJetBinHigh-nBJetBinLow,nBJetBinLow,nBJetBinHigh)

# VR using meff
#meffVR = bkt.addChannel("meffInc",["VR"],meffNBins,meffBinLow,meffBinHigh) 

# VR2 using met
#metVR = bkt.addChannel("met",["VR2"],6,30,250)

#bkt.setValidationChannels([nJetVR,nBJetVR,meffVR,metVR]) #These are not necessarily statistically independent

#---------------
# Signal regions
#---------------

# S3 using meff
#meff3J = bkt.addChannel("meffInc",["S3"],meffNBins,meffBinLow,meffBinHigh)
#meff3J.useOverflowBin=True
#meff3J.addSystematic(jesS3)
#[s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in meff3J.getSystematic(jes3J.name)]
#meff3J.addSystematic(pileupS3)
#meff3J.addSystematic(jerS3)
#meff3J.addSystematic(lesS3)
#meff3J.addSystematic(lermsS3)
#meff3J.addSystematic(leridS3)
#meff3J.addSystematic(metcoS3)
#meff3J.addSystematic(metpuS3)

# S4 using muff
#meff4J = bkt.addChannel("meffInc",["S4"],meffNBins,meffBinLow,meffBinHigh) 
#meff4J.useOverflowBin=True
#meff4J.addSystematic(jesS4)
#[s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in meff4J.getSystematic(jesS4.name)]
#meff4J.addSystematic(pileupS4)
#meff4J.addSystematic(jerS4)
#meff4J.addSystematic(lesS4)
#meff4J.addSystematic(lermsS4)
#meff4J.addSystematic(leridS4)
#meff4J.addSystematic(metcoS4)
#meff4J.addSystematic(metpuS4)

#bkt.setBkgConstrainChannels([nJetW,nJetT,meff3J,meff4J])

#**************
# Discovery fit
#**************

#discovery = configMgr.addTopLevelXMLClone(bkt,"Discovery")

# h1l3jT
#sr3jTChannel = discovery.addChannel("cuts",["SR3jT"],srNBins,srBinLow,srBinHigh)
#sr3jTChannel.addSystematic(jesS3T)
#[s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in sr3jTChannel.getSystematic(jesS3T.name)]
#sr3jTChannel.addDiscoverySamples(["SR3jT"],[1.],[-10.],[10.],[kMagenta])

# h1l4jT
#sr4jTChannel = discovery.addChannel("cuts",["SR4jT"],srNBins,srBinLow,srBinHigh)
#sr4jTChannel.addSystematic(jesS4T)
#[s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in sr4jTChannel.getSystematic(jesS4T.name)]
#sr4jTChannel.addDiscoverySamples(["SR4jT"],[1.],[-10.],[10.],[kMagenta])

# h1l3j
#s3Channel = discovery.addChannel("cuts",["S3"],srNBins,srBinLow,srBinHigh)
#s3Channel.addSystematic(jesS3)
#[s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in s3Channel.getSystematic(jesS3.name)]
#s3Channel.addDiscoverySamples(["S3"],[1.],[-100.],[100.],[kMagenta])

# h1l4j
#s4Channel = discovery.addChannel("cuts",["S4"],srNBins,srBinLow,srBinHigh)
#s4Channel.addSystematic(jesS4)
#[s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in s4Channel.getSystematic(jesS4.name)]
#s4Channel.addDiscoverySamples(["S4"],[1.],[-100.],[100.],[kMagenta])

#discovery.setSignalChannels( [sr3jTChannel,sr4jTChannel, s3Channel, s4Channel])

##srChannel = discovery.addChannel("cuts",["S3","S4"],srNBins,srBinLow,srBinHigh)
##srChannel.addDiscoverySamples(["S3","S4"],[1.,1.],[-10.,-10.],[10.,10.],[kBlue,kBlue])
##srChannel.addSystematic(jesSR)
##srChannel.addDiscoverySamples(["S3","S4"],[1.,1.],[-20.,-20.],[20.,20.],[kBlue,kBlue])
##discovery.setSignalChannels(srChannel)

#-----------------------------
# Exclusion fits (MSUGRA grid)
#-----------------------------
sigSamples=["SU_180_360","SU_580_240","SU_740_330","SU_900_420","SU_1300_210"]
if rel17:
    sigSamples=["SU_580_240_0_10_P"]
for sig in sigSamples:
    myTopLvl = configMgr.addTopLevelXMLClone(bkt,"Sig_%s"%sig)
    #myTopLvl.getMeasurement("NormalMeasurement").addConstraintTerm("XSS","Gamma")

    sigSample = Sample(sig,kPink)
    sigSample.setNormByTheory()
    sigSample.setStatConfig(useStat)
    sigSample.setNormFactor("mu_SIG",1.,0.,5.)
    sigSample.addSystematic(xsecSig)
    #sigSample.setCutsDict(cutsDictMeV)
    #sigSample.setUnit("MeV")
    myTopLvl.addSamples(sigSample)
    myTopLvl.setSignalSample(sigSample)
    
    # Reassign merging for shapeSys
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in myTopLvl.getChannel("nJet",["WR"]).getSystematic(jesWR.name)]
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in myTopLvl.getChannel("nJet",["TR"]).getSystematic(jesTR.name)]

    # h1l3j using meff
    meff3J = myTopLvl.addChannel("meffInc",["S3"],meffNBins,meffBinLow,meffBinHigh) 
    meff3J.useOverflowBin=True
    meff3J.addSystematic(jesS3)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in meff3J.getSystematic(jesS3.name)]
    meff3J.addSystematic(jerS3)
    #meff3J.addSystematic(pileupS3)
    [meff3J.getSample(sam).addSystematic(pileupS3) for sam in ["WZ","Top","BG"]] 
    [meff3J.getSample(sam).addSystematic(lesS3) for sam in ["WZ","Top","BG"]]
    [meff3J.getSample(sam).addSystematic(lermsS3) for sam in ["WZ","Top","BG"]]
    [meff3J.getSample(sam).addSystematic(leridS3) for sam in ["WZ","Top","BG"]]
    [meff3J.getSample(sam).addSystematic(metcoS3) for sam in ["WZ","Top","BG"]]
    [meff3J.getSample(sam).addSystematic(metpuS3) for sam in ["WZ","Top","BG"]]

    # h1l4j using meff
    meff4J = myTopLvl.addChannel("meffInc",["S4"],meffNBins,meffBinLow,meffBinHigh)
    meff4J.useOverflowBin=True
    meff4J.addSystematic(jesS4)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in meff4J.getSystematic(jesS4.name)]
    meff4J.addSystematic(jerS4)
    #meff4J.addSystematic(pileupS4)
    [meff4J.getSample(sam).addSystematic(pileupS4) for sam in ["WZ","Top","BG"]] 
    [meff4J.getSample(sam).addSystematic(lesS4) for sam in ["WZ","Top","BG"]]
    [meff4J.getSample(sam).addSystematic(lermsS4) for sam in ["WZ","Top","BG"]]
    [meff4J.getSample(sam).addSystematic(leridS4) for sam in ["WZ","Top","BG"]]
    [meff4J.getSample(sam).addSystematic(metcoS4) for sam in ["WZ","Top","BG"]]
    [meff4J.getSample(sam).addSystematic(metpuS4) for sam in ["WZ","Top","BG"]]

    myTopLvl.setSignalChannels([meff3J,meff4J])
