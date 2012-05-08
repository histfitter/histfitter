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
#configMgr.plotHistos = True


rel17=True

useStat=True

# First define HistFactory attributes
configMgr.analysisName = "MySoftOneLeptonKtScaleFit_split_noSys"

# Scaling calculated by outputLumi / inputLumi
configMgr.inputLumi = 1.917  # Luminosity of input TTree after weighting
configMgr.outputLumi = 1.917   # Luminosity required for output histograms
configMgr.setLumiUnits("fb-1")

if rel17:
    configMgr.inputLumi = 0.001
    configMgr.outputLumi = 4.700 #1.917   # Luminosity required for output histograms
    configMgr.analysisName+="R17" 

configMgr.outputFileName = "results/"+configMgr.analysisName+"_Output.root"

# setting the parameters of the hypothesis test
#configMgr.doHypoTest=False
#configMgr.nTOYs=1000
configMgr.calculatorType=2
configMgr.testStatType=3
configMgr.nPoints=20


# Set the files to read from
if configMgr.readFromTree:
    if rel17:
        configMgr.inputFileNames = []
        #h1l
        configMgr.inputFileNames.append("samples/SusyFitterTree_OneEle_Rel17_BG_Syst.root")
        configMgr.inputFileNames.append("samples/SusyFitterTree_OneMu_Rel17_BG_Syst.root")
        configMgr.inputFileNames.append("samples/SusyFitterTree_OneSoftEle_Rel17_BG_CrossCheck.root")
        configMgr.inputFileNames.append("samples/SusyFitterTree_OneSoftMuo_Rel17_BG_CrossCheck.root")
        #s1l
        #configMgr.inputFileNames.append("samples/SusyFitterTree_OneSoftEle_Rel17_BG_CrossCheck.root")
        #configMgr.inputFileNames.append("samples/SusyFitterTree_OneSoftMuo_Rel17_BG_CrossCheck.root")
        #mSUGRA
        #configMgr.inputFileNames.append("samples/SusyFitterTree_p832_v4.root")
        #configMgr.inputFileNames.append("samples/SusyFitterTree_p832_GG-One-Step_v1.root")
        #1-step simplified model
        configMgr.inputFileNames.append("samples/SusyFitterTree_p832_GG-One-Step_soft_v0.root")
                
    else:
        configMgr.inputFileNames = []
else:
    configMgr.inputFileNames = []


# W and T control regions
#configMgr.cutsDict["SLWR"] = "lep2Pt<10 && met>30 && met<120 && mt>40 && mt<80 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc>400"
configMgr.cutsDict["SLWR"] = "lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB2Jet==0 && jet1Pt>130 && jet2Pt>25  && (AnalysisType==6 || AnalysisType==7) "
#configMgr.cutsDict["SLTR"] = "lep2Pt<10 && met>30 && met<120 && mt>40 && mt<80 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && meffInc>400"
configMgr.cutsDict["SLTR"] = "lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB2Jet>0 && jet1Pt>130 && jet2Pt>25 && (AnalysisType==6 || AnalysisType==7) "

# top and w validation regions
configMgr.cutsDict["SLVR1"] = "lep2Pt<10 && met>30 && met<120 && mt>40 && mt<80 && jet1Pt>80 && jet3Pt>25 && meffInc>400 && (AnalysisType==1 || AnalysisType==2) "
configMgr.cutsDict["SLVR2"] = "lep2Pt<10 && met>180 && met<250 && mt>80 && mt<100 && jet1Pt>130 && jet2Pt>25 && (AnalysisType==6 || AnalysisType==7)"

# soft lepton signal region:
# configMgr.cutsDict["SLSR"] = "lep2Pt<10 && met>250 && mt>100 && jet1Pt>130 && jet2Pt>25 && (AnalysisType==6 || AnalysisType==7)"
configMgr.cutsDict["SS"] = "lep2Pt<10 && met>250 && mt>100 && jet1Pt>130 && jet2Pt>25 && (AnalysisType==6 || AnalysisType==7)"





d=configMgr.cutsDict
configMgr.cutsDict["SRs1lsj"] = d["SS"]+"&& met/meff2Jet>0.3"

cutsDictMeV = {}
# W and T control regions
#cutsDictMeV["SLWR"] = "lep2Pt<10000 && met>30000 && met<120000 && mt>40000 && mt<80000 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc>400000"
cutsDictMeV["SLWR"] = "(lep1Pt < 20000 && lep2Pt<10000 && met>180000 && met<250000 && mt>40000 && mt<80000 && nB2Jet==0 && jet1Pt>130000 && jet2Pt>25000  && AnalysisType==7) || (lep1Pt < 25000 && lep2Pt<10000 && met>180000 && met<250000 && mt>40000 && mt<80000 && nB2Jet==0 && jet1Pt>130000 && jet2Pt>25000  && AnalysisType==6)"

cutsDictMeV["SLTR"] = "(lep1Pt < 25000 && lep2Pt<10000 && met>180000 && met<250000 && mt>40000 && mt<80000 && nB2Jet>0 && jet1Pt>130000 && jet2Pt>25000 && AnalysisType==6) || (lep1Pt < 20000 && lep2Pt<10000 && met>180000 && met<250000 && mt>40000 && mt<80000 && nB2Jet>0 && jet1Pt>130000 && jet2Pt>25000 && AnalysisType==7)"

# top and w validation regions
cutsDictMeV["SLVR1"] = "(lep2Pt<10000 && met>30000 && met<120000 && mt>40000 && mt<80000 && jet1Pt>80000 && jet3Pt>25000 && meffInc>400000 && AnalysisType==2) || (lep2Pt<10000 && met>30000 && met<120000 && mt>40000 && mt<80000 && jet1Pt>80000 && jet3Pt>25000 && meffInc>400000 && AnalysisType==1)"
cutsDictMeV["SLVR2"] = "(lep1Pt < 25000 && lep2Pt<10000 && met>180000 && met<250000 && mt>80000 && mt<100000 && jet1Pt>130000 && jet2Pt>25000 && AnalysisType==6) || (lep1Pt < 20000 && lep2Pt<10000 && met>180000 && met<250000 && mt>80000 && mt<100000 && jet1Pt>130000 && jet2Pt>25000 && AnalysisType==7)"

#cutsDictMeV["TVR"] = "lep2Pt<10000 && met>30000 && met<120000 && mt>40000 && mt<80000 && nB3Jet>0 && jet1Pt>80000 && jet3Pt>25000 && meffInc>400000 && (AnalysisType==1 || AnalysisType==2) "

# soft lepton signal region:
cutsDictMeV["SS"] = "((lep1Pt < 20000 && lep2Pt<10000 && met>250000 && mt>100000 && jet1Pt>130000 && jet2Pt>25000 && AnalysisType==7) || (lep1Pt < 25000 && lep2Pt<10000 && met>250000 && mt>100000 && jet1Pt>130000 && jet2Pt>25000 && AnalysisType==6))"

d=cutsDictMeV
cutsDictMeV["SRs1lsj"] = d["SS"]+"&& (met/meff2Jet)>0.3"



# Tuples of nominal weights without and with b-jet selection
configMgr.weights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight2Jet")

xsecSigHighWeights = ("genWeightUp","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight2Jet")
xsecSigLowWeights = ("genWeightDown","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight2Jet")

# For weight-based systematic
ktScaleWHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ktfacUpWeightW","bTagWeight2Jet")
ktScaleWLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ktfacDownWeightW","bTagWeight2Jet")
ktScaleTopHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ktfacUpWeightTop","bTagWeight2Jet")
ktScaleTopLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ktfacDownWeightTop","bTagWeight2Jet")

#ptMinTopLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ptmin20WeightTop","bTagWeight2Jet")

#ptMinWZLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ptmin20WeightW","bTagWeight2Jet")

#noWPtWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","bTagWeight2Jet")

bTagHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight2JetUp")
bTagLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight2JetDown")

trigHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeightUp","truthWptWeight","bTagWeight2Jet")
trigLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeightDown","truthWptWeight","bTagWeight2Jet")

lepHighWeights = ("genWeight","eventWeight","leptonWeightUp","triggerWeight","truthWptWeight","bTagWeight2Jet")
lepLowWeights = ("genWeight","eventWeight","leptonWeightDown","triggerWeight","truthWptWeight","bTagWeight2Jet")

pileupSystWeights = ("genWeight","pileupWeightSyst","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight2Jet")

# QCD weights without and with b-jet selection
configMgr.weightsQCD = "qcdWeight"
configMgr.weightsQCDWithB = "qcdBWeight"

#--------------------
# List of systematics
#--------------------

# KtScale uncertainty as histoSys - two-sided, no additional normalization
topKtScale = Systematic("KtScaleTop",configMgr.weights,ktScaleTopHighWeights,ktScaleTopLowWeights,"weight","normHistoSys")
wzKtScale = Systematic("KtScaleWZ",configMgr.weights,ktScaleWHighWeights,ktScaleWLowWeights,"weight","normHistoSys")

# PtMin uncertainty as userNormHistoSys and userOverallSys - User must specify weights per bin in CR and overall weight in SR
#topPtMin30CR = Systematic("PtMinTopC",configMgr.weights,[1.,1.,1.,1.,1.,1.,1.],[0.91,0.92,0.88,0.85,0.84,0.87,0.83],"user","userNormHistoSys")
#wzPtMin30CR = Systematic("PtMinWZC",configMgr.weights,[1.,1.,1.,1.,1.,1.,1.],[0.82,0.81,0.83,0.89,0.94,0.93,0.92],"user","userNormHistoSys")
#topPtMin30S3 = Systematic("PtMinTop3",configMgr.weights,1.,0.79,"user","userOverallSys")
#wzPtMin30S3 = Systematic("PtMinWZ3",configMgr.weights,1.,0.79,"user","userOverallSys")
#topPtMin30S4 = Systematic("PtMinTop4",configMgr.weights,1.,0.94,"user","userOverallSys")
#wzPtMin30S4 = Systematic("PtMinWZ4",configMgr.weights,1.,1.07,"user","userOverallSys")


# Signal XSec uncertainty as overallSys (pure yeild affect)
#xsecSig = Systematic("XSS",configMgr.weights,xsecSigHighWeights,xsecSigLowWeights,"weight","overallSys")

# Assess the impact of the WPt reweighting as one-sided histoSys
#nowptSLWR = Systematic("WP",configMgr.weights,noWPtWeights,noWPtWeights,"weight","histoSysOneSide")
#nowptSLTR = Systematic("WP",configMgr.weights,noWPtWeights,noWPtWeights,"weight","histoSysOneSide")
#nowptSS = Systematic("WP",configMgr.weights,noWPtWeights,noWPtWeights,"weight","histoSysOneSide")
#nowptSST = Systematic("WP",configMgr.weights,noWPtWeights,noWPtWeights,"weight","histoSysOneSide")

# Trigger weight uncertainty as overallSys
#trigSLWR = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
#trigSLTR = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
#trigSS = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
#trigSST = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")

# Lepton weight uncertainty as overallSys
lepSLWR = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepSLTR = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepSS = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepSST = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")

# Pileup uncertainty as histoSys in each channel by applying weights at 0.9*<mu>
#pileupSLWR = Systematic("PU",configMgr.weights,pileupSystWeights,pileupSystWeights,"weight","histoSysOneSide")
#pileupSLTR = Systematic("PU",configMgr.weights,pileupSystWeights,pileupSystWeights,"weight","histoSysOneSide")
#pileupSS = Systematic("PU",configMgr.weights,pileupSystWeights,pileupSystWeights,"weight","histoSysOneSide")
#pileupSST = Systematic("PU",configMgr.weights,pileupSystWeights,pileupSystWeights,"weight","histoSysOneSide")

# B-tag uncertainty as overallSys in SLWR and SLTR
btagSLWR = Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","overallSys")
btagSLTR = Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","overallSys")

# JES uncertainty as shapeSys - one systematic per region (combine SLWR and SLTR), merge samples
jesSLWR = Systematic("JW","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesSLTR = Systematic("JT","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesSS = Systematic("JS","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesSST = Systematic("JST","_NoSys","_JESup","_JESdown","tree","shapeSys")


# JER uncertainty as one sided histoSys - Do not apply as data/MC is 1
#jerSLWR = Systematic("JR","_NoSys","_JER","_JER","tree","histoSysOneSide")
#jerSLTR = Systematic("JR","_NoSys","_JER","_JER","tree","histoSysOneSide")
#jerSS = Systematic("JR","_NoSys","_JER","_JER","tree","histoSysOneSide")
#jerSST = Systematic("JRST","_NoSys","_JER","_JER","tree","histoSysOneSide")

# LES uncertainty as overallSys - one per channel
#lesSLWR = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
#lesSLTR = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
#lesSS = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")

# LER with muon system as overallSys - one per channel
#lermsSLWR = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
#lermsSLTR = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
#lermsSS = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
#lermsSST = Systematic("LRMST","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")

# LER with inner detector as overallSys - one per channel
#leridSLWR = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
#leridSLTR = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
#leridSS = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
#leridSST = Systematic("LRIST","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")

# MET cell-out uncertainty as overallSys - one per channel
#metcoSLWR = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
#metcoSLTR = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
#metcoSS = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
#metcoSST = Systematic("MCST","_NoSys","_METCOup","_METCOdown","tree","overallSys")

# MET pileup uncertainty as overallSys - one per channel
#metpuSLWR = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","overallSys")
#metpuSLTR = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","overallSys")
#metpuSS = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","overallSys")
#metpuSST = Systematic("MPST","_NoSys","_METPUup","_METPUdown","tree","overallSys")

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
nJetBinLow = 2
nJetBinHighTR = 10
nJetBinHighWR = 10

nBJetBinLow = 0

nBJetBinHigh = 4

meffNBins = 6
meffBinLow = 400.
meffBinHigh = 1600.

metNBins = 6
metBinLow = 250.
metBinHigh = 500.

lepPtNBins = 6
lepPtLow = 7.
lepPtHigh = 25.

srNBins = 1
srBinLow = 0.5
srBinHigh = 1.5

#************
#Bkg only fit
#************

bkt = configMgr.addTopLevelXML("BkgOnlyKt")
if useStat:
    bkt.statErrThreshold=0.03
else:
    bkt.statErrThreshold=None
bkt.addSamples([topSample,wzSample,qcdSample,bgSample,dataSample])

# Systematics to a applied globally within this topLevel
bkt.getSample("Top").addSystematic(topKtScale)
bkt.getSample("WZ").addSystematic(wzKtScale)
#bkt.getSample("Top").addSystematic(topPtMin)
#bkt.getSample("WZ").addSystematic(wzPtMin)

meas=bkt.addMeasurement(name="NormalMeasurement",lumi=1.0,lumiErr=0.039)
meas.addPOI("mu_SIG")
meas.addParamSetting("mu_BG",True,1)
    
#meas.addParamSetting("Lumi",True,1.)
#meas.addParamSetting("alpha_XSS",True,1.)
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
nJetSLW = bkt.addChannel("nJet",["SLWR"],nJetBinHighWR-nJetBinLow,nJetBinLow,nJetBinHighWR)
nJetSLW.hasB = True
#nJetW.getSample("WZ").addSystematic(wzPtMin30CR)
#nJetW.getSample("Top").addSystematic(topPtMin30CR)
nJetSLW.addSystematic(jesSLWR)

[s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetSLW.getSystematic(jesSLWR.name)]
nJetSLW.addSystematic(btagSLWR)
#[nJetSLW.getSample(sam).addSystematic(pileupSLWR) for sam in ["WZ","Top","BG"]]
#nJetSLW.addSystematic(jerSLWR)
#nJetW.addSystematic(nowptWR)
nJetSLW.addSystematic(lepSLWR)
#nJetSLW.addSystematic(trigSLWR)
#[nJetSLW.getSample(sam).addSystematic(lesSLWR) for sam in ["WZ","Top","BG"]]
#[nJetSLW.getSample(sam).addSystematic(lermsSLWR) for sam in ["WZ","Top","BG"]]
#[nJetSLW.getSample(sam).addSystematic(leridSLWR) for sam in ["WZ","Top","BG"]]
#[nJetSLW.getSample(sam).addSystematic(metcoSLWR) for sam in ["WZ","Top","BG"]]
#[nJetSLW.getSample(sam).addSystematic(metpuSLWR) for sam in ["WZ","Top","BG"]]

# SLTR using nJet
nJetSLT = bkt.addChannel("nJet",["SLTR"],nJetBinHighTR-nJetBinLow,nJetBinLow,nJetBinHighTR)
nJetSLT.hasB = True
#nJetT.getSample("WZ").addSystematic(wzPtMin30CR)
#nJetT.getSample("Top").addSystematic(topPtMin30CR)
nJetSLT.addSystematic(jesSLTR)

[s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetSLT.getSystematic(jesSLTR.name)]
nJetSLT.addSystematic(btagSLTR)
#[nJetSLT.getSample(sam).addSystematic(pileupSLTR) for sam in ["WZ","Top","BG"]]
#nJetSLT.addSystematic(jerSLTR)
#nJetT.addSystematic(nowptTR)
nJetSLT.addSystematic(lepSLTR)
#nJetSLT.addSystematic(trigSLTR)
#[nJetSLT.getSample(sam).addSystematic(lesSLTR) for sam in ["WZ","Top","BG"]]
#[nJetSLT.getSample(sam).addSystematic(lermsSLTR) for sam in ["WZ","Top","BG"]]
#[nJetSLT.getSample(sam).addSystematic(leridSLTR) for sam in ["WZ","Top","BG"]]
#[nJetSLT.getSample(sam).addSystematic(metcoSLTR) for sam in ["WZ","Top","BG"]]
#[nJetSLT.getSample(sam).addSystematic(metpuSLTR) for sam in ["WZ","Top","BG"]]

bkt.setBkgConstrainChannels([nJetSLW,nJetSLT])

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
    #sigSamples=["SU_580_240_0_10_P"]
    #sigSamples=['SM_GG_onestepCC_1025_545_65']#,'SM_GG_onestepCC_1025_625_225', 'SM_GG_onestepCC_1025_705_385', 'SM_GG_onestepCC_1025_785_545', 'SM_GG_onestepCC_1025_865_705', 'SM_GG_onestepCC_1025_945_865', 'SM_GG_onestepCC_1037_1024_1012', 'SM_GG_onestepCC_1065_1025_985', 'SM_GG_onestepCC_1065_545_25', 'SM_GG_onestepCC_1065_625_185', 'SM_GG_onestepCC_1065_705_345', 'SM_GG_onestepCC_1065_785_505', 'SM_GG_onestepCC_1065_865_665', 'SM_GG_onestepCC_1065_945_825', 'SM_GG_onestepCC_1105_1025_945', 'SM_GG_onestepCC_1105_625_145', 'SM_GG_onestepCC_1105_705_305', 'SM_GG_onestepCC_1105_785_465', 'SM_GG_onestepCC_1105_865_625', 'SM_GG_onestepCC_1105_945_785', 'SM_GG_onestepCC_1117_1104_1092', 'SM_GG_onestepCC_1145_1025_905', 'SM_GG_onestepCC_1145_1105_1065', 'SM_GG_onestepCC_1145_625_105', 'SM_GG_onestepCC_1145_705_265', 'SM_GG_onestepCC_1145_785_425', 'SM_GG_onestepCC_1145_865_585', 'SM_GG_onestepCC_1145_945_745', 'SM_GG_onestepCC_1185_1025_865', 'SM_GG_onestepCC_1185_1105_1025', 'SM_GG_onestepCC_1185_625_65', 'SM_GG_onestepCC_1185_705_225', 'SM_GG_onestepCC_1185_785_385', 'SM_GG_onestepCC_1185_865_545', 'SM_GG_onestepCC_1185_945_705', 'SM_GG_onestepCC_205_125_45', 'SM_GG_onestepCC_225_185_145', 'SM_GG_onestepCC_227_214_202', 'SM_GG_onestepCC_235_155_75', 'SM_GG_onestepCC_245_125_5', 'SM_GG_onestepCC_255_215_175', 'SM_GG_onestepCC_257_244_232', 'SM_GG_onestepCC_265_185_105', 'SM_GG_onestepCC_275_155_35', 'SM_GG_onestepCC_285_245_205', 'SM_GG_onestepCC_287_274_262', 'SM_GG_onestepCC_295_215_135', 'SM_GG_onestepCC_305_185_65', 'SM_GG_onestepCC_315_275_235', 'SM_GG_onestepCC_317_304_292', 'SM_GG_onestepCC_325_245_165', 'SM_GG_onestepCC_335_215_95', 'SM_GG_onestepCC_345_185_25', 'SM_GG_onestepCC_345_305_265', 'SM_GG_onestepCC_355_275_195', 'SM_GG_onestepCC_365_245_125', 'SM_GG_onestepCC_375_215_55', 'SM_GG_onestepCC_385_305_225', 'SM_GG_onestepCC_395_275_155', 'SM_GG_onestepCC_397_384_372', 'SM_GG_onestepCC_405_245_85', 'SM_GG_onestepCC_415_215_15', 'SM_GG_onestepCC_425_305_185', 'SM_GG_onestepCC_425_385_345', 'SM_GG_onestepCC_435_275_115', 'SM_GG_onestepCC_445_245_45', 'SM_GG_onestepCC_465_305_145', 'SM_GG_onestepCC_465_385_305', 'SM_GG_onestepCC_475_275_75', 'SM_GG_onestepCC_477_464_452', 'SM_GG_onestepCC_485_245_5', 'SM_GG_onestepCC_505_305_105', 'SM_GG_onestepCC_505_385_265', 'SM_GG_onestepCC_505_465_425', 'SM_GG_onestepCC_515_275_35', 'SM_GG_onestepCC_545_305_65', 'SM_GG_onestepCC_545_385_225', 'SM_GG_onestepCC_545_465_385', 'SM_GG_onestepCC_557_544_532', 'SM_GG_onestepCC_585_305_25', 'SM_GG_onestepCC_585_385_185', 'SM_GG_onestepCC_585_465_345', 'SM_GG_onestepCC_585_545_505', 'SM_GG_onestepCC_625_385_145', 'SM_GG_onestepCC_625_465_305', 'SM_GG_onestepCC_625_545_465', 'SM_GG_onestepCC_637_624_612', 'SM_GG_onestepCC_665_385_105', 'SM_GG_onestepCC_665_465_265', 'SM_GG_onestepCC_665_545_425', 'SM_GG_onestepCC_665_625_585', 'SM_GG_onestepCC_705_385_65', 'SM_GG_onestepCC_705_465_225', 'SM_GG_onestepCC_705_545_385', 'SM_GG_onestepCC_705_625_545', 'SM_GG_onestepCC_717_704_692', 'SM_GG_onestepCC_745_385_25', 'SM_GG_onestepCC_745_465_185', 'SM_GG_onestepCC_745_545_345', 'SM_GG_onestepCC_745_625_505', 'SM_GG_onestepCC_745_705_665', 'SM_GG_onestepCC_785_465_145', 'SM_GG_onestepCC_785_545_305', 'SM_GG_onestepCC_785_625_465', 'SM_GG_onestepCC_785_705_625', 'SM_GG_onestepCC_797_784_772', 'SM_GG_onestepCC_825_465_105', 'SM_GG_onestepCC_825_545_265', 'SM_GG_onestepCC_825_625_425', 'SM_GG_onestepCC_825_705_585', 'SM_GG_onestepCC_825_785_745', 'SM_GG_onestepCC_865_465_65', 'SM_GG_onestepCC_865_545_225', 'SM_GG_onestepCC_865_625_385', 'SM_GG_onestepCC_865_705_545', 'SM_GG_onestepCC_865_785_705', 'SM_GG_onestepCC_877_864_852', 'SM_GG_onestepCC_905_465_25', 'SM_GG_onestepCC_905_545_185', 'SM_GG_onestepCC_905_625_345', 'SM_GG_onestepCC_905_705_505', 'SM_GG_onestepCC_905_785_665', 'SM_GG_onestepCC_905_865_825', 'SM_GG_onestepCC_945_545_145', 'SM_GG_onestepCC_945_625_305', 'SM_GG_onestepCC_945_705_465', 'SM_GG_onestepCC_945_785_625', 'SM_GG_onestepCC_945_865_785', 'SM_GG_onestepCC_957_944_932', 'SM_GG_onestepCC_985_545_105', 'SM_GG_onestepCC_985_625_265', 'SM_GG_onestepCC_985_705_425', 'SM_GG_onestepCC_985_785_585', 'SM_GG_onestepCC_985_865_745', 'SM_GG_onestepCC_985_945_905']
    #XYZXYZXYZ
    #sigSamples=['SM_GG_onestepCC_1025_545_65']
for sig in sigSamples:
    myTopLvl = configMgr.addTopLevelXMLClone(bkt,"Sig_%s"%sig)

    sigSample = Sample(sig,kPink)
    sigSample.setNormByTheory()
    sigSample.setStatConfig(useStat)
    sigSample.setNormFactor("mu_SIG",1.,0.,2500000000.)
    #sigSample.addSystematic(xsecSig)
    sigSample.setCutsDict(cutsDictMeV)
    sigSample.setUnit("MeV")
    myTopLvl.addSamples(sigSample)
    myTopLvl.setSignalSample(sigSample)
    
    # Reassign merging for shapeSys
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in myTopLvl.getChannel("nJet",["SLWR"]).getSystematic(jesSLWR.name)]
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in myTopLvl.getChannel("nJet",["SLTR"]).getSystematic(jesSLTR.name)]

    # h1l3j using meff
    meff3J = myTopLvl.addChannel("met/meff2Jet",["SS"],6,0.1,0.7) # change binning
    meff3J.useOverflowBin=True
#    meff3J.getSample("WZ").addSystematic(wzPtMin30S3)
#    meff3J.getSample("Top").addSystematic(topPtMin30S3)
    meff3J.addSystematic(jesSS)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in meff3J.getSystematic(jesSS.name)]
    #meff3J.addSystematic(jerSS)
    #meff3J.addSystematic(nowptS3)
    meff3J.addSystematic(lepSS)
    #meff3J.addSystematic(trigSS)
    #[meff3J.getSample(sam).addSystematic(pileupSS) for sam in ["WZ","Top","BG"]] 
    #[meff3J.getSample(sam).addSystematic(lesSS) for sam in ["WZ","Top","BG"]]
    #[meff3J.getSample(sam).addSystematic(lermsSS) for sam in ["WZ","Top","BG"]]
    #[meff3J.getSample(sam).addSystematic(leridSS) for sam in ["WZ","Top","BG"]]
    #[meff3J.getSample(sam).addSystematic(metcoSS) for sam in ["WZ","Top","BG"]]
    #[meff3J.getSample(sam).addSystematic(metpuSS) for sam in ["WZ","Top","BG"]]
    myTopLvl.setSignalChannels([meff3J])
