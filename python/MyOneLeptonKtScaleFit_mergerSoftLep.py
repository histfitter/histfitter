################################################################
## In principle all you have to setup is defined in this file ##
################################################################

from configManager import configMgr
from ROOT import kBlack,kWhite,kGray,kRed,kPink,kMagenta,kViolet,kBlue,kAzure,kCyan,kTeal,kGreen,kSpring,kYellow,kOrange
from configWriter import TopLevelXML,Measurement,ChannelXML,Sample
from systematic import Systematic
from math import sqrt

from ROOT import gROOT
gROOT.LoadMacro("./macros/AtlasStyle.C")
import ROOT
ROOT.SetAtlasStyle()

#---------------------------------------------------------------------------------------------
# Some flags for overridding normal execution and telling ROOT to shut up... use with caution!
#---------------------------------------------------------------------------------------------
#configMgr.plotHistos = True

#---------------------------------------
# Flags to control which fit is executed
#---------------------------------------
useStat=True
doHardLep=False
doSoftLep=True
doValidation=False
doDiscovery=False
doDiscoveryTight=False
doExclusion=True
fullSyst=False
useISR=True
useXsecUnc=True             # switch off when calucating excluded cross section (colour code in SM plots)
blindSR=False

#-------------------------------
# Parameters for hypothesis test
#-------------------------------
#configMgr.doHypoTest=False
#configMgr.nTOYs=1000
configMgr.calculatorType=2
configMgr.testStatType=3
configMgr.nPoints=20
#--------------------------------
# Now we start to build the model
#--------------------------------

# First define HistFactory attributes
if doSoftLep and not doHardLep:
    configMgr.analysisName = "MyOneLeptonKtScaleFit_SoftLep"
elif not doSoftLep and doHardLep:
    configMgr.analysisName = "MyOneLeptonKtScaleFit_HardLep"
elif doSoftLep and doHardLep:
    configMgr.analysisName = "MyOneLeptonKtScaleFit_CombinedSoftHardLep"
else:
    configMgr.analysisName = "MyOneLeptonKtScaleFit"

# Scaling calculated by outputLumi / inputLumi
configMgr.inputLumi = 0.001 # Luminosity of input TTree after weighting
configMgr.outputLumi = 4.713 # Luminosity required for output histograms
configMgr.setLumiUnits("fb-1")

configMgr.histCacheFile = "data/"+configMgr.analysisName+".root"

configMgr.outputFileName = "results/"+configMgr.analysisName+"_Output.root"

# Set the files to read from
bgdFiles = []
sigFiles = []
if configMgr.readFromTree:
    #h1l
    if doHardLep:
        bgdFiles.append("samples/paper/SusyFitterTree_OneEle.root")
        bgdFiles.append("samples/paper/SusyFitterTree_OneMu.root")
    #s1l
    if doSoftLep:
        bgdFiles.append("samples/paper/SusyFitterTree_OneSoftEle_BG_v3.root")
        bgdFiles.append("samples/paper/SusyFitterTree_OneSoftMuo_BG_v3.root")
    if doHardLep and doExclusion:
        # mSUGRA
        sigFiles.append("samples/paper/SusyFitterTree_p832_mSUGRA_paper_v1.root")
        # 1-step simplified model
        sigFiles.append("samples/paper/SusyFitterTree_p832_GGonestep_paper_v1.root")
            
    if doSoftLep and doExclusion:
        # 1-step simplified model
        sigFiles.append("samples/SusyFitterTree_p832_GG-One-Step_soft_v1.root")
else:
    bgdFiles = ["data/"+configMgr.analysisName+".root"]
#Note: input bgdFiles and sigFiles are now set below

# Dictionnary of cuts for Tree->hist
configMgr.cutsDict["WR"] = "(AnalysisType==1 || AnalysisType==2) && met>30 && met<120 && mt>40 && mt<80 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc>400"
configMgr.cutsDict["TR"] = "(AnalysisType==1 || AnalysisType==2) && met>30 && met<120 && mt>40 && mt<80 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && meffInc>400"
configMgr.cutsDict["SLWR"] = "(lep1Pt < 20 && lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB2Jet==0 && jet1Pt>130 && jet2Pt>25  && AnalysisType==7) || (lep1Pt < 25 && lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB2Jet==0 && jet1Pt>130 && jet2Pt>25  && AnalysisType==6)"
configMgr.cutsDict["SLTR"] = "(lep1Pt < 25 && lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB2Jet>0 && jet1Pt>130 && jet2Pt>25 && AnalysisType==6) || (lep1Pt < 20 && lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB2Jet>0 && jet1Pt>130 && jet2Pt>25 && AnalysisType==7)"

configMgr.cutsDict["VR1"] = "(AnalysisType==1 || AnalysisType==2) && met>120 && met<250 && mt>80 && jet1Pt>80 && jet3Pt>25 && meffInc>400"
configMgr.cutsDict["VR2"] = "(AnalysisType==1 || AnalysisType==2) && met<250 && mt>80 && jet1Pt>80 && jet3Pt>25 && meffInc>400"
#configMgr.cutsDict["SLVR1"] = "(lep2Pt<10 && met>30 && met<120 && mt>40 && mt<80 && jet1Pt>80 && jet3Pt>25 && meffInc>400 && AnalysisType==2) || (lep2Pt<10 && met>30 && met<120 && mt>40 && mt<80 && jet1Pt>80 && jet3Pt>25 && meffInc>400 && AnalysisType==1)"
configMgr.cutsDict["SLVR2"] = "(lep1Pt < 25 && lep2Pt<10 && met>180 && met<250 && mt>80 && mt<100 && jet1Pt>130 && jet2Pt>25 && AnalysisType==6) || (lep1Pt < 20 && lep2Pt<10 && met>180 && met<250 && mt>80 && mt<100 && jet1Pt>130 && jet2Pt>25 && AnalysisType==7)"
configMgr.cutsDict["WVL1"] = "(AnalysisType==1 || AnalysisType==2) && met>120 && met<250 && mt>40 && mt<80 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc>400"
configMgr.cutsDict["TVL1"] = "(AnalysisType==1 || AnalysisType==2) && met>120 && met<250 && mt>40 && mt<80 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && meffInc>400"
configMgr.cutsDict["HMTVL1"] = "(AnalysisType==1 || AnalysisType==2) && met>30 && met<250 && mt>80 && jet1Pt>80 && jet3Pt>25 && meffInc>400"

configMgr.cutsDict["S3"] = "(AnalysisType==1 || AnalysisType==2) && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25 && jet4Pt<80"
configMgr.cutsDict["S4"] = "(AnalysisType==1 || AnalysisType==2) && met>250 && mt>100 && met/meff4Jet>0.2 && jet4Pt>80"
configMgr.cutsDict["SS"] = "((lep1Pt < 20 && lep2Pt<10 && met>250 && mt>100 && jet1Pt>130 && jet2Pt>25 && AnalysisType==7) || (lep1Pt < 25 && lep2Pt<10 && met>250 && mt>100 && jet1Pt>130 && jet2Pt>25 && AnalysisType==6))"

d=configMgr.cutsDict
configMgr.cutsDict["SR3jT"] = d["S3"]+"&& meffInc>1200"
configMgr.cutsDict["SR4jT"] = d["S4"]+"&& meffInc>800"
configMgr.cutsDict["SR1sl2j"] = d["SS"]+"&& met/meff2Jet>0.3"


# Tuples of nominal weights without and with b-jet selection
if doHardLep:
    configMgr.weights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight3Jet")
elif doSoftLep:
    configMgr.weights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight2Jet")

# For weight-based systematics
if doHardLep:
    xsecSigHighWeights = ("genWeightUp","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight3Jet")
    xsecSigLowWeights = ("genWeightDown","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight3Jet")
    
    ktScaleWHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ktfacUpWeightW","bTagWeight3Jet")
    ktScaleWLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ktfacDownWeightW","bTagWeight3Jet")
    
    ktScaleTopHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ktfacUpWeightTop","bTagWeight3Jet")
    ktScaleTopLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ktfacDownWeightTop","bTagWeight3Jet")
    
    noWPtWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","bTagWeight3Jet")
    #noWPtWeightsHigh = ("genWeight","eventWeight","leptonWeight","triggerWeight","(1+(truthWptWeight-1)/2)","bTagWeight3Jet")
    #noWPtWeightsLow = ("genWeight","eventWeight","leptonWeight","triggerWeight","(1+(truthWptWeight-1)*1.5)","bTagWeight3Jet")
    
    bTagHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight3JetUp")
    bTagLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight3JetDown")
        
    trigHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeightUp","truthWptWeight","bTagWeight3Jet")
    trigLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeightDown","truthWptWeight","bTagWeight3Jet")
    
    lepHighWeights = ("genWeight","eventWeight","leptonWeightUp","triggerWeight","truthWptWeight","bTagWeight3Jet")
    lepLowWeights = ("genWeight","eventWeight","leptonWeightDown","triggerWeight","truthWptWeight","bTagWeight3Jet")
    
elif doSoftLep:
    xsecSigHighWeights = ("genWeightUp","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight2Jet")
    xsecSigLowWeights = ("genWeightDown","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight2Jet")
    
    ktScaleWHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ktfacUpWeightW","bTagWeight2Jet")
    ktScaleWLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ktfacDownWeightW","bTagWeight2Jet")
    
    ktScaleTopHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ktfacUpWeightTop","bTagWeight2Jet")
    ktScaleTopLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ktfacDownWeightTop","bTagWeight2Jet")
    
    noWPtWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","bTagWeight2Jet")
    #noWPtWeightsHigh = ("genWeight","eventWeight","leptonWeight","triggerWeight","(1+(truthWptWeight-1)/2)","bTagWeight2Jet")
    #noWPtWeightsLow = ("genWeight","eventWeight","leptonWeight","triggerWeight","(1+(truthWptWeight-1)*1.5)","bTagWeight2Jet")
    
    bTagHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight2JetUp")
    bTagLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight2JetDown")
    
    trigHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeightUp","truthWptWeight","bTagWeight2Jet")
    trigLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeightDown","truthWptWeight","bTagWeight2Jet")
    
    lepHighWeights = ("genWeight","eventWeight","leptonWeightUp","triggerWeight","truthWptWeight","bTagWeight2Jet")
    lepLowWeights = ("genWeight","eventWeight","leptonWeightDown","triggerWeight","truthWptWeight","bTagWeight2Jet")
    
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
topPtMin30CR = Systematic("PtMinTopC",configMgr.weights,[1.09,1.08,1.12,1.15,1.16,1.13,1.17],[0.91,0.92,0.88,0.85,0.84,0.87,0.83],"user","userNormHistoSys")
wzPtMin30CR = Systematic("PtMinWZC",configMgr.weights,[1.18,1.19,1.17,1.11,1.06,1.07,1.08],[0.82,0.81,0.83,0.89,0.94,0.93,0.92],"user","userNormHistoSys")
topPtMin30VR = Systematic("PtMinTopV",configMgr.weights,[1.09,1.08,1.12,1.15,1.16,1.13,1.17],[0.91,0.92,0.88,0.85,0.84,0.87,0.83],"user","userNormHistoSys")
wzPtMin30VR = Systematic("PtMinWZV",configMgr.weights,[1.18,1.19,1.17,1.11,1.06,1.07,1.08],[0.82,0.81,0.83,0.89,0.94,0.93,0.92],"user","userNormHistoSys")
topPtMin30WRS = Systematic("PtMinTopSW",configMgr.weights,[1.09,1.06,1.1,1.12,1.13,0.99,1.05,1.34],[0.91,0.94,0.9,0.88,0.87,1.01,0.95,0.66],"user","userNormHistoSys")
wzPtMin30WRS = Systematic("PtMinWZSW",configMgr.weights,[0.98,1.17,1.24,1.28,1.28,1.14,1.23,1.],[1.02,0.83,0.76,0.72,0.72,0.86,0.77,1.],"user","userNormHistoSys")
topPtMin30TRS = Systematic("PtMinTopST",configMgr.weights,[1.09,1.06,1.1,1.12,1.13,0.99,1.05,1.34],[0.91,0.94,0.9,0.88,0.87,1.01,0.95,0.66],"user","userNormHistoSys")
wzPtMin30TRS = Systematic("PtMinWZST",configMgr.weights,[0.98,1.17,1.24,1.28,1.28,1.14,1.23,1.],[1.02,0.83,0.76,0.72,0.72,0.86,0.77,1.],"user","userNormHistoSys")
topPtMin30S3 = Systematic("PtMinTop3",configMgr.weights,1.12,0.88,"user","userOverallSys")
wzPtMin30S3 = Systematic("PtMinWZ3",configMgr.weights,1.19,0.81,"user","userOverallSys")
topPtMin30S4 = Systematic("PtMinTop4",configMgr.weights,1.16,0.84,"user","userOverallSys")
wzPtMin30S4 = Systematic("PtMinWZ4",configMgr.weights,1.08,0.92,"user","userOverallSys")
topPtMin30SS = Systematic("PtMinTopSS",configMgr.weights,1.02,0.98,"user","userOverallSys")
wzPtMin30SS = Systematic("PtMinWZSS",configMgr.weights,1.30,0.70,"user","userOverallSys")
topPtMin30S3T = Systematic("PtMinTop3T",configMgr.weights,1.12,0.88,"user","userOverallSys")
wzPtMin30S3T = Systematic("PtMinWZ3T",configMgr.weights,1.19,0.81,"user","userOverallSys")
topPtMin30S4T = Systematic("PtMinTop4T",configMgr.weights,1.16,0.84,"user","userOverallSys")
wzPtMin30S4T = Systematic("PtMinWZ4T",configMgr.weights,1.08,0.92,"user","userOverallSys")
topPtMin30SS2T = Systematic("PtMinTopS2T",configMgr.weights,1.04,0.96,"user","userOverallSys")
wzPtMin30SS2T = Systematic("PtMinWZS2T",configMgr.weights,1.32,0.68,"user","userOverallSys")

# Signal XSec uncertainty as overallSys (pure yeild affect)
xsecSig = Systematic("XSS",configMgr.weights,xsecSigHighWeights,xsecSigLowWeights,"weight","overallSys")

# Assess the impact of the WPt reweighting as one-sided histoSys
nowpt = Systematic("WP",configMgr.weights,noWPtWeights,noWPtWeights,"weight","histoSys")
#nowpt = Systematic("WP",configMgr.weights,noWPtWeightsHigh,noWPtWeightsLow,"weight","histoSys")
#nowptWR = Systematic("WP",configMgr.weights,noWPtWeights,noWPtWeights,"weight","histoSysOneSide")
#nowptTR = Systematic("WP",configMgr.weights,noWPtWeights,noWPtWeights,"weight","histoSysOneSide")
#nowptSWR = Systematic("WP",configMgr.weights,noWPtWeights,noWPtWeights,"weight","histoSysOneSide")
#nowptSTR = Systematic("WP",configMgr.weights,noWPtWeights,noWPtWeights,"weight","histoSysOneSide")
#nowptVR = Systematic("WP",configMgr.weights,noWPtWeights,noWPtWeights,"weight","histoSysOneSide")
#nowptS3 = Systematic("WP",configMgr.weights,noWPtWeights,noWPtWeights,"weight","histoSysOneSide")
#nowptS4 = Systematic("WP",configMgr.weights,noWPtWeights,noWPtWeights,"weight","histoSysOneSide")
#nowptSS = Systematic("WP",configMgr.weights,noWPtWeights,noWPtWeights,"weight","histoSysOneSide")
#nowptS3T = Systematic("WP",configMgr.weights,noWPtWeights,noWPtWeights,"weight","histoSysOneSide")
##nowptS4T = Systematic("WP",configMgr.weights,noWPtWeights,noWPtWeights,"weight","histoSysOneSide")
#nowptSS2T = Systematic("WP",configMgr.weights,noWPtWeights,noWPtWeights,"weight","histoSysOneSide")

# Trigger weight uncertainty as overallSys
trigWR = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigTR = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigSWR = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigSTR = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigVR = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigS3 = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigS4 = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigSS = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigS3T = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigS4T = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigSS2T = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")

# Lepton weight uncertainty as overallSys
lepWR = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepTR = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepSWR = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepSTR = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepVR = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepS3 = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepS4 = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepSS = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepS3T = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepS4T = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepSS2T = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")

# B-tag uncertainty as overallSys in WR and TR
btagWR = Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","overallSys")
btagTR = Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","overallSys")
btagSWR = Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","overallSys")
btagSTR = Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","overallSys")

# JES uncertainty as shapeSys - one systematic per region (combine WR and TR), merge samples
jesWR = Systematic("JC","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesTR = Systematic("JC","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesSWR = Systematic("JSC","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesSTR = Systematic("JSC","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVRnJet = Systematic("JVJ","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVRnBJet = Systematic("JVB","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVRmet = Systematic("JVE","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVRmeff = Systematic("JVM","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVRSTR = Systematic("JVST","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVRSWR = Systematic("JVSW","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVR1SnJet = Systematic("JVS1J","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVR1SnBJet = Systematic("JVS1B","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVR1Smeff = Systematic("JVS1M","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVR1Smetmeff = Systematic("JVS1MM","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVR1Smet = Systematic("JVS1E","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVR2SnJet = Systematic("JVS2J","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVR2SnBJet = Systematic("JVS2B","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVR2Smeff = Systematic("JVS2M","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVR2Smetmeff = Systematic("JVS2MM","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVR2Smet = Systematic("JVS2E","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesWVL1meff = Systematic("JVWM","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesWVL1nJet = Systematic("JVWJ","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesTVL1meff = Systematic("JVTM","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesTVL1nJet = Systematic("JVTJ","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesHMTVL1meff = Systematic("JVHM","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesHMTVL1met = Systematic("JVHE","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesHMTVL1nJet = Systematic("JVHJ","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesHMTVL1nBJet = Systematic("JVHB","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS3 = Systematic("J3","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS4 = Systematic("J4","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesSS = Systematic("JSS","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS3T = Systematic("J3T","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS4T = Systematic("J4T","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesSS2T = Systematic("JS2T","_NoSys","_JESup","_JESdown","tree","shapeSys")

# LES uncertainty as overallSys - one per channel
lesWR = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesTR = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesSWR = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesSTR = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesVR = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesS3 = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesS4 = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesSS = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesS3T = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesS4T = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesSS2T = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")

# LER with muon system as overallSys - one per channel
lermsWR = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsTR = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsSWR = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsSTR = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsVR = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsS3 = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsS4 = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsSS = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsS3T = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsS4T = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsSS2T = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")

# LER with inner detector as overallSys - one per channel
leridWR = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridTR = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridSWR = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridSTR = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridVR = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridS3 = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridS4 = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridSS = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridS3T = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridS4T = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridSS2T = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")

# MET cell-out uncertainty as overallSys - one per channel
metcoWR = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoTR = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoSWR = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoSTR = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoVR = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoS3 = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoS4 = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoSS = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoS3T = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoS4T = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoSS2T = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")

# MET pileup uncertainty as overallSys - one per channel
metpuWR = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuTR = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuSWR = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuSTR = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuVR = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuS3 = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuS4 = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuSS = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuS3T = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuS4T = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuSS2T = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")

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

for sam in [topSample, wzSample, bgSample, qcdSample, dataSample]:
        sam.setFileList(bgdFiles)

#Binnings
nJetBinLowHard = 3
nJetBinLowSoft = 2
nJetBinHighTR = 10
nJetBinHighWR = 10


nBJetBinLow = 0
nBJetBinHigh = 4

meffNBins = 6
meffBinLow = 400.
meffBinHigh = 1600.

meffNBinsSR4 = 4
meffBinLowSR4 = 800.
meffBinHighSR4 = 1600.

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
    bkt.statErrThreshold=0.05 #0.03??
else:
    bkt.statErrThreshold=None
bkt.addSamples([topSample,wzSample,qcdSample,bgSample,dataSample])

# Systematics to a applied globally within this topLevel
bkt.getSample("Top").addSystematic(topKtScale)
bkt.getSample("WZ").addSystematic(wzKtScale)
bkt.getSample("WZ").addSystematic(nowpt)

meas=bkt.addMeasurement(name="NormalMeasurement",lumi=1.0,lumiErr=0.039)
meas.addPOI("mu_SIG")
meas.addParamSetting("mu_BG",True,1)

## MB : set ptmin to constant in CRs right now ... unstable otherwise
meas.addParamSetting("alpha_PtMinTopC",True,1)
meas.addParamSetting("alpha_PtMinWZC",True,1)


#-------------------------------------------------
# Constraining regions - statistically independent
#-------------------------------------------------

# WR using nJet - hard lep
if doHardLep:
    nJetW = bkt.addChannel("nJet",["WR"],nJetBinHighWR-nJetBinLowHard,nJetBinLowHard,nJetBinHighWR)
    nJetW.useOverflowBin = False
    nJetW.hasB = True
    nJetW.hasBQCD = False
    
    nJetW.addSystematic(jesWR)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetW.getSystematic(jesWR.name)]
    nJetW.addSystematic(btagWR)
    nJetW.addSystematic(metcoWR)
    nJetW.addSystematic(metpuWR)
    nJetW.getSample("WZ").addSystematic(wzPtMin30CR)
    nJetW.getSample("Top").addSystematic(topPtMin30CR)
 
    if fullSyst:
        nJetW.addSystematic(lepWR)
        nJetW.addSystematic(trigWR)
        [nJetW.getSample(sam).addSystematic(lesWR) for sam in ["WZ","Top","BG"]]
        [nJetW.getSample(sam).addSystematic(lermsWR) for sam in ["WZ","Top","BG"]]
        [nJetW.getSample(sam).addSystematic(leridWR) for sam in ["WZ","Top","BG"]]

# TR using nJet
if doHardLep:
    nJetT = bkt.addChannel("nJet",["TR"],nJetBinHighTR-nJetBinLowHard,nJetBinLowHard,nJetBinHighTR)
    nJetT.useOverflowBin = False
    nJetT.hasB = True
    nJetT.hasBQCD = True

    nJetT.addSystematic(jesTR)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetT.getSystematic(jesTR.name)]
    nJetT.addSystematic(btagTR)
    nJetT.addSystematic(metcoTR)
    nJetT.addSystematic(metpuTR)
    nJetT.getSample("WZ").addSystematic(wzPtMin30CR)
    nJetT.getSample("Top").addSystematic(topPtMin30CR)
 
    if fullSyst:
        nJetT.addSystematic(lepTR)
        nJetT.addSystematic(trigTR)
        [nJetT.getSample(sam).addSystematic(lesTR) for sam in ["WZ","Top","BG"]]
        [nJetT.getSample(sam).addSystematic(lermsTR) for sam in ["WZ","Top","BG"]]
        [nJetT.getSample(sam).addSystematic(leridTR) for sam in ["WZ","Top","BG"]]

# Soft WR using nJet
if doSoftLep and not doHardLep:
    nJetWS = bkt.addChannel("nJet",["SLWR"],nJetBinHighWR-nJetBinLowSoft,nJetBinLowSoft,nJetBinHighWR)
    nJetWS.hasB = True
    nJetWS.hasBQCD = False
    nJetWS.useOverflowBin = False
    nJetWS.addSystematic(jesSWR)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetWS.getSystematic(jesSWR.name)]
    nJetWS.addSystematic(btagSWR)
    nJetWS.addSystematic(metcoSWR)
    nJetWS.addSystematic(metpuSWR)
    nJetWS.getSample("WZ").addSystematic(wzPtMin30WRS)
    nJetWS.getSample("Top").addSystematic(topPtMin30WRS)
    if fullSyst:
        nJetWS.addSystematic(lepSWR)
        nJetWS.addSystematic(trigSWR)
        [nJetWS.getSample(sam).addSystematic(lesSWR) for sam in ["WZ","Top","BG"]]
        [nJetWS.getSample(sam).addSystematic(lermsSWR) for sam in ["WZ","Top","BG"]]
        [nJetWS.getSample(sam).addSystematic(leridSWR) for sam in ["WZ","Top","BG"]]

# Soft TR using nJet
if doSoftLep and not doHardLep:
    nJetTS = bkt.addChannel("nJet",["SLTR"],nJetBinHighTR-nJetBinLowSoft,nJetBinLowSoft,nJetBinHighTR)
    nJetTS.hasB = True
    nJetTS.hasBQCD = True
    nJetTS.useOverflowBin = False    
    nJetTS.addSystematic(jesSTR)
    [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetTS.getSystematic(jesSTR.name)]
    nJetTS.addSystematic(btagSTR)
    nJetTS.addSystematic(metcoSTR)
    nJetTS.addSystematic(metpuSTR)
    nJetTS.getSample("WZ").addSystematic(wzPtMin30TRS)
    nJetTS.getSample("Top").addSystematic(topPtMin30TRS)
    if fullSyst:
        nJetTS.addSystematic(lepSTR)
        nJetTS.addSystematic(trigSTR)
        [nJetTS.getSample(sam).addSystematic(lesSTR) for sam in ["WZ","Top","BG"]]
        [nJetTS.getSample(sam).addSystematic(lermsSTR) for sam in ["WZ","Top","BG"]]
        [nJetTS.getSample(sam).addSystematic(leridSTR) for sam in ["WZ","Top","BG"]]

if doHardLep:
    bkt.setBkgConstrainChannels([nJetW,nJetT])

if doSoftLep and not doHardLep:
    bkt.setBkgConstrainChannels([nJetWS,nJetTS])

#--------------------------------------------------------------
# Validation regions - not necessarily statistically independent
#--------------------------------------------------------------

if doValidation:
    if doHardLep:
        # WVL1: meff
        meffWVL1 = bkt.addChannel("meffInc",["WVL1"],meffNBins,meffBinLow,meffBinHigh)
        meffWVL1.hasB = True
        meffWVL1.hasBQCD = False
        meffWVL1.addSystematic(jesWVL1meff)
        [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in meffWVL1.getSystematic(jesWVL1meff.name)]
        meffWVL1.addSystematic(metcoVR)
        meffWVL1.addSystematic(metpuVR)
        if fullSyst:
            meffWVL1.addSystematic(trigVR)
            meffWVL1.addSystematic(lepVR)
            [meffWVL1.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
            [meffWVL1.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
            [meffWVL1.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]

        # TVL1: meff
        meffTVL1 = bkt.addChannel("meffInc",["TVL1"],meffNBins,meffBinLow,meffBinHigh) 
        meffTVL1.hasB = True
        meffTVL1.hasBQCD = True
        meffTVL1.addSystematic(jesTVL1meff)
        [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in meffTVL1.getSystematic(jesTVL1meff.name)]
        meffTVL1.addSystematic(metcoVR)
        meffTVL1.addSystematic(metpuVR)            
        if fullSyst:
            meffTVL1.addSystematic(trigVR)
            meffTVL1.addSystematic(lepVR)
            [meffTVL1.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
            [meffTVL1.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
            [meffTVL1.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]

        # HMTVL1: meff
        meffHMTVL1 = bkt.addChannel("meffInc",["HMTVL1"],meffNBins,meffBinLow,meffBinHigh) 
        meffHMTVL1.addSystematic(jesHMTVL1meff)
        [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in meffHMTVL1.getSystematic(jesHMTVL1meff.name)]
        meffHMTVL1.addSystematic(metcoVR)
        meffHMTVL1.addSystematic(metpuVR)
        if fullSyst:
            meffHMTVL1.addSystematic(trigVR)
            meffHMTVL1.addSystematic(lepVR)
            [meffHMTVL1.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
            [meffHMTVL1.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
            [meffHMTVL1.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]


        # FOR BKT ONLY FIT, WE ALSO NOW INCLUDE THE SIGNAL REGIONS AS VALIDATION REGIONS
        # S3 using meff
        meff3J = bkt.addChannel("meffInc",["S3"],meffNBins,meffBinLow,meffBinHigh)
        meff3J.useOverflowBin=True
        meff3J.addSystematic(jesS3)
        [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in meff3J.getSystematic(jesS3.name)]
        meff3J.addSystematic(metcoS3)
        meff3J.addSystematic(metpuS3)
        meff3J.getSample("WZ").addSystematic(wzPtMin30S3)
        meff3J.getSample("Top").addSystematic(topPtMin30S3)
        if fullSyst:
            meff3J.addSystematic(trigS3)
            meff3J.addSystematic(lepS3)
            meff3J.addSystematic(lesS3)
            meff3J.addSystematic(lermsS3)
            meff3J.addSystematic(leridS3)

        
        # S4 using meff
        meff4J = bkt.addChannel("meffInc",["S4"],meffNBins,meffBinLow,meffBinHigh) 
        meff4J.useOverflowBin=True
        meff4J.addSystematic(jesS4)
        [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in meff4J.getSystematic(jesS4.name)]
        meff4J.addSystematic(metcoS4)
        meff4J.addSystematic(metpuS4)
        meff4J.getSample("WZ").addSystematic(wzPtMin30S4)
        meff4J.getSample("Top").addSystematic(topPtMin30S4)
        if fullSyst:
            meff4J.addSystematic(trigS4)
            meff4J.addSystematic(lepS4)
            meff4J.addSystematic(lesS4)
            meff4J.addSystematic(lermsS4)
            meff4J.addSystematic(leridS4)

        # h1l3jT
        sr3jTChannel = bkt.addChannel("cuts",["SR3jT"],srNBins,srBinLow,srBinHigh)
        sr3jTChannel.addSystematic(jesS3T)
        [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in sr3jTChannel.getSystematic(jesS3T.name)]
        [sr3jTChannel.getSample(sam).addSystematic(metcoS3T) for sam in ["WZ","Top","BG"]]
        [sr3jTChannel.getSample(sam).addSystematic(metpuS3T) for sam in ["WZ","Top","BG"]]
        sr3jTChannel.getSample("WZ").addSystematic(wzPtMin30S3T)
        sr3jTChannel.getSample("Top").addSystematic(topPtMin30S3T)        
        if fullSyst:
            [sr3jTChannel.getSample(sam).addSystematic(trigS3T) for sam in ["WZ","Top","BG"]]
            [sr3jTChannel.getSample(sam).addSystematic(lepS3T) for sam in ["WZ","Top","BG"]]
            [sr3jTChannel.getSample(sam).addSystematic(lesS3T) for sam in ["WZ","Top","BG"]]
            [sr3jTChannel.getSample(sam).addSystematic(lermsS3T) for sam in ["WZ","Top","BG"]]
            [sr3jTChannel.getSample(sam).addSystematic(leridS3T) for sam in ["WZ","Top","BG"]]
            
        # h1l4jT
        sr4jTChannel = bkt.addChannel("cuts",["SR4jT"],srNBins,srBinLow,srBinHigh)
        sr4jTChannel.addSystematic(jesS4T)
        [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in sr4jTChannel.getSystematic(jesS4T.name)]
        [sr4jTChannel.getSample(sam).addSystematic(metcoS4T) for sam in ["WZ","Top","BG"]]
        [sr4jTChannel.getSample(sam).addSystematic(metpuS4T) for sam in ["WZ","Top","BG"]]        
        sr4jTChannel.getSample("WZ").addSystematic(wzPtMin30S4T)
        sr4jTChannel.getSample("Top").addSystematic(topPtMin30S4T)        
        if fullSyst:
            [sr4jTChannel.getSample(sam).addSystematic(trigS4T) for sam in ["WZ","Top","BG"]]
            [sr4jTChannel.getSample(sam).addSystematic(lepS4T) for sam in ["WZ","Top","BG"]]
            [sr4jTChannel.getSample(sam).addSystematic(lesS4T) for sam in ["WZ","Top","BG"]]
            [sr4jTChannel.getSample(sam).addSystematic(lermsS4T) for sam in ["WZ","Top","BG"]]
            [sr4jTChannel.getSample(sam).addSystematic(leridS4T) for sam in ["WZ","Top","BG"]]

            
    if doSoftLep and doHardLep:
        # soft lepton CRs are validation if using hard lep CRs
        mmSLTR = bkt.addChannel("met/meff2Jet",["SLTR"],6,0.1,0.7)
        mmSLTR.addSystematic(jesVRSTR)
        [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in mmSLTR.getSystematic(jesVRSTR.name)]
        mmSLTR.addSystematic(btagSTR)
        mmSLTR.addSystematic(metcoVR)
        mmSLTR.addSystematic(metpuVR)
        mmSLTR.getSample("WZ").addSystematic(wzPtMin30VR)
        mmSLTR.getSample("Top").addSystematic(topPtMin30VR)            
        if fullSyst:
            mmSLTR.addSystematic(trigVR)
            mmSLTR.addSystematic(lepVR)
            [mmSLTR.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
            [mmSLTR.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
            [mmSLTR.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]

        mmSLWR = bkt.addChannel("met/meff2Jet",["SLWR"],6,0.1,0.7)
        mmSLWR.addSystematic(jesVRSWR)
        [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in mmSLWR.getSystematic(jesVRSWR.name)]
        mmSLWR.addSystematic(btagSWR)
        mmSLWR.addSystematic(metcoVR)
        mmSLWR.addSystematic(metpuVR)
        mmSLWR.getSample("WZ").addSystematic(wzPtMin30VR)
        mmSLWR.getSample("Top").addSystematic(topPtMin30VR)
        if fullSyst:
            mmSLWR.addSystematic(trigVR)
            mmSLWR.addSystematic(lepVR)
            [mmSLWR.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
            [mmSLWR.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
            [mmSLWR.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]

    if doSoftLep:
        # s1l2jT
        srs1l2jTChannel = bkt.addChannel("cuts",["SR1sl2j"],srNBins,srBinLow,srBinHigh)
        srs1l2jTChannel.addSystematic(jesSS2T)
        [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in srs1l2jTChannel.getSystematic(jesSS2T.name)]
        [srs1l2jTChannel.getSample(sam).addSystematic(metcoSS2T) for sam in ["WZ","Top","BG"]]
        [srs1l2jTChannel.getSample(sam).addSystematic(metpuSS2T) for sam in ["WZ","Top","BG"]]
        srs1l2jTChannel.getSample("WZ").addSystematic(wzPtMin30SS2T)
        srs1l2jTChannel.getSample("Top").addSystematic(topPtMin30SS2T)        
        if fullSyst:
            [srs1l2jTChannel.getSample(sam).addSystematic(trigSS2T) for sam in ["WZ","Top","BG"]]
            [srs1l2jTChannel.getSample(sam).addSystematic(lepSS2T) for sam in ["WZ","Top","BG"]]
            [srs1l2jTChannel.getSample(sam).addSystematic(lesSS2T) for sam in ["WZ","Top","BG"]]
            [srs1l2jTChannel.getSample(sam).addSystematic(lermsSS2T) for sam in ["WZ","Top","BG"]]
            [srs1l2jTChannel.getSample(sam).addSystematic(leridSS2T) for sam in ["WZ","Top","BG"]]


        # additional VRs if using soft lep CRs
        nJetSLVR2 = bkt.addChannel("nJet",["SLVR2"],nJetBinHighTR-nJetBinLowSoft,nJetBinLowSoft,nJetBinHighTR)
        nJetSLVR2.addSystematic(jesVR2SnJet)
        [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nJetSLVR2.getSystematic(jesVR2SnJet.name)]
        nJetSLVR2.addSystematic(metcoVR)
        nJetSLVR2.addSystematic(metpuVR)
        if fullSyst:
            nJetSLVR2.addSystematic(trigVR)
            nJetSLVR2.addSystematic(lepVR)
            [nJetSLVR2.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
            [nJetSLVR2.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
            [nJetSLVR2.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]

        nBJetSLVR2 = bkt.addChannel("nBJet",["SLVR2"],nBJetBinHigh-nBJetBinLow,nBJetBinLow,nBJetBinHigh)
        nBJetSLVR2.addSystematic(jesVR2SnBJet)
        [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in nBJetSLVR2.getSystematic(jesVR2SnBJet.name)]
        nBJetSLVR2.addSystematic(metcoVR)
        nBJetSLVR2.addSystematic(metpuVR)
        if fullSyst:
            nBJetSLVR2.addSystematic(trigVR)
            nBJetSLVR2.addSystematic(lepVR)
            [nBJetSLVR2.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
            [nBJetSLVR2.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
            [nBJetSLVR2.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]

        meffSLVR2 = bkt.addChannel("meffInc",["SLVR2"],meffNBins,meffBinLow,meffBinHigh)
        meffSLVR2.addSystematic(jesVR2Smeff)
        [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in meffSLVR2.getSystematic(jesVR2Smeff.name)]
        meffSLVR2.addSystematic(metcoVR)
        meffSLVR2.addSystematic(metpuVR)
        if fullSyst:
            meffSLVR2.addSystematic(trigVR)
            meffSLVR2.addSystematic(lepVR)
            [meffSLVR2.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
            [meffSLVR2.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
            [meffSLVR2.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]

        metmeffSLVR2 = bkt.addChannel("met/meff2Jet",["SLVR2"],6,0.1,0.7)
        metmeffSLVR2.addSystematic(jesVR2Smetmeff)
        [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in metmeffSLVR2.getSystematic(jesVR2Smetmeff.name)]
        metmeffSLVR2.addSystematic(metcoVR)
        metmeffSLVR2.addSystematic(metpuVR)
        if fullSyst:
            metmeffSLVR2.addSystematic(trigVR)
            metmeffSLVR2.addSystematic(lepVR)
            [metmeffSLVR2.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
            [metmeffSLVR2.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
            [metmeffSLVR2.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]

        metSLVR2 = bkt.addChannel("met",["SLVR2"],7,180,250)
        metSLVR2.addSystematic(jesVR2Smet)
        [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in metSLVR2.getSystematic(jesVR2Smet.name)]
        metSLVR2.addSystematic(metcoVR)
        metSLVR2.addSystematic(metpuVR)            
        if fullSyst:
            metSLVR2.addSystematic(trigVR)
            metSLVR2.addSystematic(lepVR)
            [metSLVR2.getSample(sam).addSystematic(lesVR) for sam in ["WZ","Top","BG"]]
            [metSLVR2.getSample(sam).addSystematic(lermsVR) for sam in ["WZ","Top","BG"]]
            [metSLVR2.getSample(sam).addSystematic(leridVR) for sam in ["WZ","Top","BG"]]

        #signal region treated as validation region for this case
        mm2J = bkt.addChannel("met/meff2Jet",["SS"],6,0.1,0.7)
        mm2J.useOverflowBin=True
        mm2J.addSystematic(jesSS)
        [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in mm2J.getSystematic(jesSS.name)]
        mm2J.addSystematic(metcoSS)
        mm2J.addSystematic(metpuSS)
        mm2J.getSample("WZ").addSystematic(wzPtMin30SS)
        mm2J.getSample("Top").addSystematic(topPtMin30SS)        
        if fullSyst:
            mm2J.addSystematic(trigSS)
            mm2J.addSystematic(lepSS)
            mm2J.addSystematic(lesSS)
            mm2J.addSystematic(lermsSS)
            mm2J.addSystematic(leridSS)
        
    if doHardLep and doSoftLep:    
        bkt.setValidationChannels([mmSLTR,mmSLWR]) #Note: "set" means "append" here... FIXME

    if doHardLep:
        bkt.setValidationChannels([meffWVL1,meffTVL1,meffHMTVL1,meff3J,meff4J,sr3jTChannel,sr4jTChannel])
        
    if doSoftLep:
        bkt.setValidationChannels([nJetSLVR2,metSLVR2,meffSLVR2,nBJetSLVR2,metmeffSLVR2,mm2J,srs1l2jTChannel])
        

## #-------------------------------------------------
## # Signal regions - only do this if background only
## #-------------------------------------------------

## if not doDiscovery and not doDiscoveryTight and not doExclusion and not blindSR:
##     if doHardLep:


#**************
# Discovery fit
#**************

if doDiscovery or doDiscoveryTight:
    discovery = configMgr.addTopLevelXMLClone(bkt,"Discovery")
    
    if doHardLep:
        if doDiscoveryTight:
            # h1l3jT
            if doValidation:
                sr3jTChannel = discovery.getChannel("cuts",["SR3jT"])
                iPop=discovery.validationChannels.index("SR3jT_cuts")
                discovery.validationChannels.pop(iPop)
            else:
                sr3jTChannel = discovery.addChannel("cuts",["SR3jT"],srNBins,srBinLow,srBinHigh)
                sr3jTChannel.addSystematic(jesS3T)
                [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in sr3jTChannel.getSystematic(jesS3T.name)]
                [sr3jTChannel.getSample(sam).addSystematic(metcoS3T) for sam in ["WZ","Top","BG"]]
                [sr3jTChannel.getSample(sam).addSystematic(metpuS3T) for sam in ["WZ","Top","BG"]]
                sr3jTChannel.getSample("WZ").addSystematic(wzPtMin30S3T)
                sr3jTChannel.getSample("Top").addSystematic(topPtMin30S3T)   
                if fullSyst:
                    [sr3jTChannel.getSample(sam).addSystematic(trigS3T) for sam in ["WZ","Top","BG"]]
                    [sr3jTChannel.getSample(sam).addSystematic(lepS3T) for sam in ["WZ","Top","BG"]]
                    [sr3jTChannel.getSample(sam).addSystematic(lesS3T) for sam in ["WZ","Top","BG"]]
                    [sr3jTChannel.getSample(sam).addSystematic(lermsS3T) for sam in ["WZ","Top","BG"]]
                    [sr3jTChannel.getSample(sam).addSystematic(leridS3T) for sam in ["WZ","Top","BG"]]
                    pass
                pass
            sr3jTChannel.addDiscoverySamples(["SR3jT"],[1.],[0.],[100.],[kMagenta])

            # h1l4jT
            if doValidation:
                sr4jTChannel = discovery.getChannel("cuts",["SR4jT"])
                iPop=discovery.validationChannels.index("SR4jT_cuts")
                discovery.validationChannels.pop(iPop)
            else:
                sr4jTChannel = discovery.addChannel("cuts",["SR4jT"],srNBins,srBinLow,srBinHigh)
                sr4jTChannel.addSystematic(jesS4T)
                [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in sr4jTChannel.getSystematic(jesS4T.name)]
                [sr4jTChannel.getSample(sam).addSystematic(metcoS4T) for sam in ["WZ","Top","BG"]]
                [sr4jTChannel.getSample(sam).addSystematic(metpuS4T) for sam in ["WZ","Top","BG"]]        
                sr4jTChannel.getSample("WZ").addSystematic(wzPtMin30S4T)
                sr4jTChannel.getSample("Top").addSystematic(topPtMin30S4T)
                if fullSyst:
                    [sr4jTChannel.getSample(sam).addSystematic(trigS4T) for sam in ["WZ","Top","BG"]]
                    [sr4jTChannel.getSample(sam).addSystematic(lepS4T) for sam in ["WZ","Top","BG"]]
                    [sr4jTChannel.getSample(sam).addSystematic(lesS4T) for sam in ["WZ","Top","BG"]]
                    [sr4jTChannel.getSample(sam).addSystematic(lermsS4T) for sam in ["WZ","Top","BG"]]
                    [sr4jTChannel.getSample(sam).addSystematic(leridS4T) for sam in ["WZ","Top","BG"]]
                    pass
                pass
            sr4jTChannel.addDiscoverySamples(["SR4jT"],[1.],[0.],[100.],[kMagenta])
            
        else:
            # S3
            s3Channel = discovery.addChannel("cuts",["S3"],srNBins,srBinLow,srBinHigh)
            s3Channel.addSystematic(jesS3)
            [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in s3Channel.getSystematic(jesS3.name)]
            [s3Channel.getSample(sam).addSystematic(metcoS3) for sam in ["WZ","Top","BG"]]
            [s3Channel.getSample(sam).addSystematic(metpuS3) for sam in ["WZ","Top","BG"]]        
            s3Channel.getSample("WZ").addSystematic(wzPtMin30S3)
            s3Channel.getSample("Top").addSystematic(topPtMin30S3)   
            if fullSyst:
                [s3Channel.getSample(sam).addSystematic(trigS3) for sam in ["WZ","Top","BG"]]
                [s3Channel.getSample(sam).addSystematic(lepS3) for sam in ["WZ","Top","BG"]]
                [s3Channel.getSample(sam).addSystematic(lesS3) for sam in ["WZ","Top","BG"]]
                [s3Channel.getSample(sam).addSystematic(lermsS3) for sam in ["WZ","Top","BG"]]
                [s3Channel.getSample(sam).addSystematic(leridS3) for sam in ["WZ","Top","BG"]]
            s3Channel.addDiscoverySamples(["S3"],[1.],[0.],[100.],[kMagenta])

            # S4
            s4Channel = discovery.addChannel("cuts",["S4"],srNBins,srBinLow,srBinHigh)
            s4Channel.addSystematic(jesS4)
            [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in s4Channel.getSystematic(jesS4.name)]
            [s4Channel.getSample(sam).addSystematic(metcoS4) for sam in ["WZ","Top","BG"]]
            [s4Channel.getSample(sam).addSystematic(metpuS4) for sam in ["WZ","Top","BG"]]        
            s4Channel.getSample("WZ").addSystematic(wzPtMin30S4)
            s4Channel.getSample("Top").addSystematic(topPtMin30S4)
            if fullSyst:
                [s4Channel.getSample(sam).addSystematic(trigS4) for sam in ["WZ","Top","BG"]]
                [s4Channel.getSample(sam).addSystematic(lepS4) for sam in ["WZ","Top","BG"]]
                [s4Channel.getSample(sam).addSystematic(lesS4) for sam in ["WZ","Top","BG"]]
                [s4Channel.getSample(sam).addSystematic(lermsS4) for sam in ["WZ","Top","BG"]]
                [s4Channel.getSample(sam).addSystematic(leridS4) for sam in ["WZ","Top","BG"]]
            s4Channel.addDiscoverySamples(["S4"],[1.],[0.],[100.],[kMagenta])


    if doSoftLep:
        if doDiscoveryTight:
            # s1l2jT
            srs1l2jTChannel = discovery.addChannel("cuts",["SR1sl2j"],srNBins,srBinLow,srBinHigh)
            srs1l2jTChannel.addSystematic(jesSS2T)
            [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in srs1l2jTChannel.getSystematic(jesSS2T.name)]
            [srs1l2jTChannel.getSample(sam).addSystematic(metcoSS2T) for sam in ["WZ","Top","BG"]]
            [srs1l2jTChannel.getSample(sam).addSystematic(metpuSS2T) for sam in ["WZ","Top","BG"]]
            srs1l2jTChannel.getSample("WZ").addSystematic(wzPtMin30SS2T)
            srs1l2jTChannel.getSample("Top").addSystematic(topPtMin30SS2T) 
            if fullSyst:
                [srs1l2jTChannel.getSample(sam).addSystematic(trigSS2T) for sam in ["WZ","Top","BG"]]
                [srs1l2jTChannel.getSample(sam).addSystematic(lepSS2T) for sam in ["WZ","Top","BG"]]
                [srs1l2jTChannel.getSample(sam).addSystematic(lesSS2T) for sam in ["WZ","Top","BG"]]
                [srs1l2jTChannel.getSample(sam).addSystematic(lermsSS2T) for sam in ["WZ","Top","BG"]]
                [srs1l2jTChannel.getSample(sam).addSystematic(leridSS2T) for sam in ["WZ","Top","BG"]]
            srs1l2jTChannel.addDiscoverySamples(["SR1sl2j"],[1.],[0.],[100.],[kMagenta])

        else:
            # s1l2jT
            ssChannel = discovery.addChannel("cuts",["SS"],srNBins,srBinLow,srBinHigh)
            ssChannel.addSystematic(jesSS)
            [s.mergeSamples([topSample.name,wzSample.name,bgSample.name]) for s in ssChannel.getSystematic(jesSS.name)]
            [ssChannel.getSample(sam).addSystematic(metcoSS) for sam in ["WZ","Top","BG"]]
            [ssChannel.getSample(sam).addSystematic(metpuSS) for sam in ["WZ","Top","BG"]]
            ssChannel.getSample("WZ").addSystematic(wzPtMin30SS)
            ssChannel.getSample("Top").addSystematic(topPtMin30SS) 
            if fullSyst:
                [ssChannel.getSample(sam).addSystematic(trigSS) for sam in ["WZ","Top","BG"]]
                [ssChannel.getSample(sam).addSystematic(lepSS) for sam in ["WZ","Top","BG"]]
                [ssChannel.getSample(sam).addSystematic(lesSS) for sam in ["WZ","Top","BG"]]
                [ssChannel.getSample(sam).addSystematic(lermsSS) for sam in ["WZ","Top","BG"]]
                [ssChannel.getSample(sam).addSystematic(leridSS) for sam in ["WZ","Top","BG"]]
            ssChannel.addDiscoverySamples(["SS"],[1.],[0.],[100.],[kMagenta])

    if doHardLep and doSoftLep:
        if doDiscoveryTight:
            discovery.setSignalChannels([sr3jTChannel,sr4jTChannel,srs1l2jTChannel])
        else:
            discovery.setSignalChannels([s3Channel,s4Channel,ssChannel])
    elif doHardLep:
        if doDiscoveryTight:
            discovery.setSignalChannels([sr3jTChannel,sr4jTChannel])
        else:
            discovery.setSignalChannels([s3Channel,s4Channel])
    elif doSoftLep:
        if doDiscoveryTight:
            discovery.setSignalChannels([srs1l2jTChannel])
        else:
            discovery.setSignalChannels([ssChannel])



#-----------------------------
# Exclusion fits (MSUGRA grid)
#-----------------------------
if doExclusion:
    sigSamples=["SU_580_240_0_10_P"]
    if doSoftLep:
        sigSamples=["SM_GG_onestepCC_425_385_345"]
                        
    for sig in sigSamples:
        myTopLvl = configMgr.addTopLevelXMLClone(bkt,"Sig_%s"%sig)

        if useISR and sig.startswith("SM"):
            errisr = 0.
            mgl = int(sig.split('_')[3])
            mlsp = int(sig.split('_')[4])
            mdiff = mgl - mlsp
            
            norm = sqrt(0.25**2 + 0.10**2) # these are the max. showering parameter variations we found (variations recommended for pythia 2011 tunes)
            
            if mgl<300: norm += (1.-(mgl-200)/100.)*0.25
            if mdiff<300: errisr = (1.-(mdiff/300.))*norm # the uncertainty grows towards the mass diagonal, and when mgl gets smaller.

            isrHighWeights = ("genWeight",str(1+errisr),"eventWeight","leptonWeight","triggerWeightUp","truthWptWeight","bTagWeight3Jet")
            isrLowWeights = ("genWeight",str(1-errisr),"eventWeight","leptonWeight","triggerWeightDown","truthWptWeight","bTagWeight3Jet")

            isrUnc = Systematic("ISR",configMgr.weights,isrHighWeights,isrLowWeights,"weight","overallSys")
            
        sigSample = Sample(sig,kPink)
        sigSample.setFileList(sigFiles)
        sigSample.setNormByTheory()
        sigSample.setStatConfig(useStat)
        sigSample.setNormFactor("mu_SIG",1.,0.,5.)
        
        if useISR and useXsecUnc and sig.startswith("SM"):
            sigSample.addSystematic(isrUnc)
            sigSample.addSystematic(xsecSig)
        elif useISR and not useXsecUnc and sig.startswith("SM"):
            sigSample.addSystematic(isrUnc)
        elif useXsecUnc:
            sigSample.addSystematic(xsecSig)
            
        myTopLvl.addSamples(sigSample)
        myTopLvl.setSignalSample(sigSample)
    
        # Reassign merging for shapeSys
        if doHardLep:
            [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in myTopLvl.getChannel("nJet",["WR"]).getSystematic(jesWR.name)]
            [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in myTopLvl.getChannel("nJet",["TR"]).getSystematic(jesTR.name)]
        else:
            [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in myTopLvl.getChannel("nJet",["SLWR"]).getSystematic(jesSWR.name)]
            [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in myTopLvl.getChannel("nJet",["SLTR"]).getSystematic(jesSTR.name)]

        if doHardLep:   
            # h1l3j using meff
            if doValidation:
                meff3J = myTopLvl.getChannel("meffInc",["S3"])
                iPop=myTopLvl.validationChannels.index("S3_meffInc")
                myTopLvl.validationChannels.pop(iPop)
            else:
                meff3J = myTopLvl.addChannel("meffInc",["S3"],meffNBins,meffBinLow,meffBinHigh) 
                meff3J.useOverflowBin=True
                meff3J.addSystematic(jesS3)
                [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in meff3J.getSystematic(jesS3.name)]
                meff3J.addSystematic(metcoS3)
                meff3J.addSystematic(metpuS3)
                meff3J.getSample("WZ").addSystematic(wzPtMin30S3)
                meff3J.getSample("Top").addSystematic(topPtMin30S3)
                if fullSyst:
                    meff3J.addSystematic(trigS3)
                    meff3J.addSystematic(lepS3)
                    [meff3J.getSample(sam).addSystematic(lesS3) for sam in ["WZ","Top","BG"]]
                    [meff3J.getSample(sam).addSystematic(lermsS3) for sam in ["WZ","Top","BG"]]
                    [meff3J.getSample(sam).addSystematic(leridS3) for sam in ["WZ","Top","BG"]]
        
            # h1l4j using meff
            if doValidation:
                meff4J = myTopLvl.getChannel("meffInc",["S4"])
                iPop=myTopLvl.validationChannels.index("S4_meffInc")
                myTopLvl.validationChannels.pop(iPop)
            else:
                meff4J = myTopLvl.addChannel("meffInc",["S4"],meffNBinsSR4,meffBinLowSR4,meffBinHighSR4)
                meff4J.useOverflowBin=True
                meff4J.addSystematic(jesS4)
                [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in meff4J.getSystematic(jesS4.name)]
                meff4J.addSystematic(metcoS4)
                meff4J.addSystematic(metpuS4)
                meff4J.getSample("WZ").addSystematic(wzPtMin30S4)
                meff4J.getSample("Top").addSystematic(topPtMin30S4)
                if fullSyst:
                    meff4J.addSystematic(trigS4)
                    meff4J.addSystematic(lepS4)
                    [meff4J.getSample(sam).addSystematic(lesS4) for sam in ["WZ","Top","BG"]]
                    [meff4J.getSample(sam).addSystematic(lermsS4) for sam in ["WZ","Top","BG"]]
                    [meff4J.getSample(sam).addSystematic(leridS4) for sam in ["WZ","Top","BG"]]

        if doSoftLep:    
            # s1l2j using met/meff
            if doValidation:
                mm2J = myTopLvl.getChannel("met/meff2Jet",["SS"])
                iPop=myTopLvl.validationChannels.index("SS_metmeff2Jet")
                myTopLvl.validationChannels.pop(iPop)
            else:
                mm2J = myTopLvl.addChannel("met/meff2Jet",["SS"],5,0.2,0.7)
                mm2J.useOverflowBin=True
                mm2J.addSystematic(jesSS)
                [s.mergeSamples([topSample.name,wzSample.name,bgSample.name,sigSample.name]) for s in mm2J.getSystematic(jesSS.name)]
                mm2J.addSystematic(metcoSS)
                mm2J.addSystematic(metpuSS)
                mm2J.getSample("WZ").addSystematic(wzPtMin30SS)
                mm2J.getSample("Top").addSystematic(topPtMin30SS)
                if fullSyst:
                    mm2J.addSystematic(trigSS)
                    mm2J.addSystematic(lepSS)
                    [mm2J.getSample(sam).addSystematic(lesSS) for sam in ["WZ","Top","BG"]]
                    [mm2J.getSample(sam).addSystematic(lermsSS) for sam in ["WZ","Top","BG"]]
                    [mm2J.getSample(sam).addSystematic(leridSS) for sam in ["WZ","Top","BG"]]
                    pass
                pass

        if doHardLep:  #Note "set" means "append" here... FIXME
            myTopLvl.setSignalChannels([meff3J,meff4J])
        if doSoftLep:
            myTopLvl.setSignalChannels([mm2J])
