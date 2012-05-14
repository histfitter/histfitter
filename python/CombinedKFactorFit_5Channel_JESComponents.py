
################################################################
## In principle all you have to setup is defined in this file ##
################################################################

from configManager import configMgr
from ROOT import kBlack,kRed,kBlue,kGreen,kYellow,kWhite,kPink,kGray,kMagenta
from configWriter import TopLevelXML,Measurement,ChannelXML,Sample
from systematic import Systematic

#from ROOT import gROOT
#gROOT.LoadMacro("./macros/AtlasStyle.C")
#import ROOT
#ROOT.SetAtlasStyle()

onLxplus=True
doHardLep=True
doSoftLep=False
useStat=True
doValidation=False
doValidationSR=True
doValidationSlope=False
doValidationDilep=False
doValidationDilepZ=False
doDiscoveryS2=False
doDiscoveryS4=False
doDiscovery=False
doDiscoveryTight=False
discoverychannel="ee" # ee, emu, mumu
doExclusion=False
doExclusion_GMSB_combined=False
doExclusion_mSUGRA_dilepton_combined=False
doExclusion_GG_onestepCC_combined=False
doExclusion_GG_twostepCC_slepton=False

doSignalOnly=False #Remove all bkgs for signal histo creation step
#doSignalOnly=True #Remove all bkgs for signal histo creation step
# Need to comment out the following line when running HypoTest.py parallelized
sigSamples=["GMSB_3_2d_50_250_3_10_1_1"]
#sigSamples=[]


#doExclusion=True
blindS=False
fullSyst=True
useXsecUnc=True             # switch off when calucating excluded cross section (colour code in SM plots)
doWptReweighting=False ## currently buggy

# First define HistFactory attributes
configMgr.analysisName = "Combined_KFactorFit_5Channel" # Name to give the analysis
configMgr.outputFileName = "results/Combined_KFactorFit_5Channel.root"

# Scaling calculated by outputLumi / inputLumi
configMgr.inputLumi = 0.001
configMgr.outputLumi = 4.713
configMgr.setLumiUnits("fb-1")


#configMgr.doHypoTest=True
#configMgr.nTOYs=100
#configMgr.calculatorType=0
configMgr.calculatorType=2
configMgr.testStaType=3
configMgr.nPoints=20

bgdFiles = []
sigFiles = []

configMgr.histCacheFile = "data/"+configMgr.analysisName+".root"
inputDir="root://eosatlas//eos/atlas/atlascerngroupdisk/phys-susy/histfitter/stronglepton/Paper_v1/"
inputDirSig="root://eosatlas//eos/atlas/atlascerngroupdisk/phys-susy/histfitter/stronglepton/"

# Set the files to read from
if configMgr.readFromTree:
    if not onLxplus:
        bgdFiles = ["data/SusyFitterTree_OneSoftMuo_BG_v4.root","data/SusyFitterTree_OneSoftEle_BG_v4.root","data/SusyFitterTree_EleEle.root","data/SusyFitterTree_EleMu.root","data/SusyFitterTree_MuMu.root","data/SusyFitterTree_OneEle.root","data/SusyFitterTree_OneMu.root"]
    else:
        bgdFiles = [inputDirSig+"SusyFitterTree_OneSoftMuo_BG_v4.root",inputDirSig+"SusyFitterTree_OneSoftEle_BG_v4.root",inputDir+"/SusyFitterTree_EleEle.root",inputDir+"/SusyFitterTree_EleMu.root",inputDir+"/SusyFitterTree_MuMu.root",inputDir+"/SusyFitterTree_OneEle.root",inputDir+"/SusyFitterTree_OneMu.root"]

if doExclusion_GMSB_combined:
    if not onLxplus:
        sigFiles+=["data/SusyFitterTree_EleEle_GMSB.root","data/SusyFitterTree_EleMu_GMSB.root","data/SusyFitterTree_MuMu_GMSB.root"]
    else:
        sigFiles+=[inputDirSig+"/SusyFitterTree_EleEle_GMSB.root",inputDirSig+"/SusyFitterTree_EleMu_GMSB.root",inputDirSig+"/SusyFitterTree_MuMu_GMSB.root"]

if doExclusion_mSUGRA_dilepton_combined:
    if not onLxplus:
        sigFiles+=["data/SusyFitterTree_EleEle_mSUGRA.root","data/SusyFitterTree_EleMu_mSUGRA.root","data/SusyFitterTree_MuMu_mSUGRA.root"]
    else:
        sigFiles+=[inputDirSig+"/SusyFitterTree_EleEle_mSUGRA.root",inputDirSig+"/SusyFitterTree_EleMu_mSUGRA.root",inputDirSig+"/SusyFitterTree_MuMu_mSUGRA.root"]


if doExclusion_GG_onestepCC_combined:
    if not onLxplus:
        sigFiles+=["data/SusyFitterTree_OneSoftMuo_SM_GG_onestepCC_v3.root","data/SusyFitterTree_OneSoftEle_SM_GG_onestepCC_v3.root"]
    else:
        sigFiles+=[inputDirSig+"/SusyFitterTree_OneSoftMuo_SM_GG_onestepCC_v3.root",inputDirSig+"/SusyFitterTree_OneSoftMuo_SM_GG_onestepCC_v3.root"]



# AnalysisType corresponds to ee,mumu,emu as I want to split these channels up

# Map regions to cut strings
configMgr.cutsDict = {"TRee":"(mll<80 || mll>100) && met > 30 && met < 80 && jet2Pt > 50 && nB3Jet > 0 && AnalysisType==3",
                      "TRmm":"(mll<80 || mll>100) && met > 30 && met < 80 && jet2Pt > 50 && nB3Jet > 0 && AnalysisType==4",
                      "TRem":"(mll<80 || mll>100) && met > 30 && met < 80 && jet2Pt > 50 && nB3Jet > 0 && AnalysisType==5",
                      "ZRee":"mll>80 && mll<100  && met < 50 && jet2Pt > 50 && AnalysisType==3",
                      "ZRmm":"mll>80 && mll<100  && met < 50 && jet2Pt > 50 && AnalysisType==4",

                      "S2ee":"met > 300 && nJet>=2 && jet2Pt > 200 && jet4Pt < 50 && AnalysisType==3",
                      "S2mm":"met > 300 && nJet>=2 && jet2Pt > 200 && jet4Pt < 50 && AnalysisType==4",
                      "S2em":"met > 300 && nJet>=2 && jet2Pt > 200 && jet4Pt < 50 && AnalysisType==5",
                      "S4ee":"met > 100 && nJet>=4 && jet4Pt > 50 && met/meff4Jet > 0.2 && meffInc > 650 && AnalysisType==3",
                      "S4mm":"met > 100 && nJet>=4 && jet4Pt > 50 && met/meff4Jet > 0.2 && meffInc > 650 && AnalysisType==4",
                      "S4em":"met > 100 && nJet>=4 && jet4Pt > 50 && met/meff4Jet > 0.2 && meffInc > 650 && AnalysisType==5",

                      "VR2ee":"met > 100 && met < 300 && jet4Pt < 50 && jet2Pt > 50 && AnalysisType==3",
                      "VR2em":"met > 100 && met < 300 && jet4Pt < 50 && jet2Pt > 50 && AnalysisType==5",
                      "VR2mm":"met > 100 && met < 300 && jet4Pt < 50 && jet2Pt > 50 && AnalysisType==4",

                      "VR3ee":"met > 100 && met < 300 && jet4Pt < 50 && jet3Pt > 50 && AnalysisType==3",
                      "VR3em":"met > 100 && met < 300 && jet4Pt < 50 && jet3Pt > 50 && AnalysisType==5",
                      "VR3mm":"met > 100 && met < 300 && jet4Pt < 50 && jet3Pt > 50 && AnalysisType==4",

                      "VR4ee":"met < 100 && jet4Pt > 50 && AnalysisType==3",
                      "VR4em":"met < 100 && jet4Pt > 50  && AnalysisType==5",
                      "VR4mm":"met < 100  && jet4Pt > 50 && AnalysisType==4",

                      "VZR2ee":"met > 50 && met < 100 && jet2Pt > 50 && nB3Jet == 0 && AnalysisType==3",
                      "VZR2em":"met > 50 && met < 100 && jet2Pt > 50 && nB3Jet == 0 && AnalysisType==5",                    
                      "VZR2mm":"met > 50 && met < 100 && jet2Pt > 50 && nB3Jet == 0 && AnalysisType==4",

                      "VZR3ee":"met > 50 && met < 100  && jet3Pt > 50 && nB3Jet == 0 && AnalysisType==3",
                      "VZR3em":"met > 50 && met < 100 && jet3Pt > 50 && nB3Jet == 0 && AnalysisType==5",
                      "VZR3mm":"met > 50 && met < 100 && jet3Pt > 50 && nB3Jet == 0 && AnalysisType==4",

                      "VZR4ee":"met > 50 && met < 100 & jet4Pt > 50  && nB3Jet == 0 && AnalysisType==3",
                      "VZR4em":"met > 50 && met < 100 & jet4Pt > 50 && nB3Jet == 0 && AnalysisType==5",
                      "VZR4mm":"met > 50 && met < 100 & jet4Pt > 50  && nB3Jet == 0 && AnalysisType==4",

                      "HMTVL1El":"AnalysisType==1 && met>30 && met<250 && mt>80 && jet1Pt>80 && jet3Pt>25 && meffInc>400",
                      "HMTVL1Mu":"AnalysisType==2 && met>30 && met<250 && mt>80 && jet1Pt>80 && jet3Pt>25 && meffInc>400",
                      
                      "WREl":"lep2Pt<10 && met>40 && met<150 && mt>40 && mt<80 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc > 500 && AnalysisType==1",
                      "TREl":"lep2Pt<10 && met>40 && met<150 && mt>40 && mt<80 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && meffInc > 500 && AnalysisType==1",
                      "WRMu":"lep2Pt<10 && met>40 && met<150 && mt>40 && mt<80 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc > 500 && AnalysisType==2",
                      "TRMu":"lep2Pt<10 && met>40 && met<150 && mt>40 && mt<80 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && meffInc > 500 && AnalysisType==2",

                      "TRElVR":"lep2Pt<10 && met>40 && met<150 && mt>40 && mt<80 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==1",
                      "TRMuVR":"lep2Pt<10 && met>40 && met<150 && mt>40 && mt<80 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==2",

                      "TRElVR2":"lep2Pt<10 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==1",
                      "TRMuVR2":"lep2Pt<10 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==2", 

                      "WRElVR":"lep2Pt<10 && met>50 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==1",
                      "WRMuVR":"lep2Pt<10 && met>50 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==2",

                      "S3El":"AnalysisType==1 && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25 && jet4Pt<80",
                      "S4El":"AnalysisType==1 && met>250 && mt>100 && met/meff4Jet>0.2 && jet4Pt>80",

                      "S3Mu":"AnalysisType==2 && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25 && jet4Pt<80",
                      "S4Mu":"AnalysisType==2 && met>250 && mt>100 && met/meff4Jet>0.2 && jet4Pt>80",

                      "SR3jTEl":"AnalysisType==1 && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25 && jet4Pt<80 && meffInc>1200",
                      "SR4jTEl":"AnalysisType==1 && met>250 && mt>100 && met/meff4Jet>0.2 && jet4Pt>80 && meffInc>800",

                      "SR3jTMu":"AnalysisType==2 && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25 && jet4Pt<80 && meffInc>1200",
                      "SR4jTMu":"AnalysisType==2 && met>250 && mt>100 && met/meff4Jet>0.2 && jet4Pt>80 && meffInc>800"
                      

}



## # Tuples of weights 
if doWptReweighting:
    truthWptWeight="truthWptWeight"
else:
    truthWptWeight="1"
configMgr.weights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"truthZpt0GeVWeight","truthZpt50GeVWeight","truthZpt100GeVWeight","truthZpt150GeVWeight","truthZpt200GeVWeight","bTagWeight3Jet")
configMgr.weightsQCD = "qcdWeight"
configMgr.weightsQCDWithB = "qcdBWeight"

xsecSigHighWeights = ("genWeightUp","eventWeight","leptonWeight","triggerWeight","truthZpt0GeVWeight","truthZpt50GeVWeight","truthZpt100GeVWeight","truthZpt150GeVWeight","truthZpt200GeVWeight",truthWptWeight,"bTagWeight3Jet")
xsecSigLowWeights = ("genWeightDown","eventWeight","leptonWeight","triggerWeight","truthZpt0GeVWeight","truthZpt50GeVWeight","truthZpt100GeVWeight","truthZpt150GeVWeight","truthZpt200GeVWeight",truthWptWeight,"bTagWeight3Jet")

#ktScaleWHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"ktfacUpWeightW","bTagWeight3Jet")
#ktScaleWLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"ktfacDownWeightW","bTagWeight3Jet")
                    
#ktScaleTopHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"ktfacUpWeightTop","bTagWeight3Jet")
#ktScaleTopLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"ktfacDownWeightTop","bTagWeight3Jet")

#noWPtWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","bTagWeight3Jet")
#noWPtWeightsHigh = ("genWeight","eventWeight","leptonWeight","triggerWeight","(1+(truthWptWeight-1)/2)","bTagWeight3Jet")
#noWPtWeightsLow = ("genWeight","eventWeight","leptonWeight","triggerWeight","(1+(truthWptWeight-1)*1.5)","bTagWeight3Jet")

bTagHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthZpt0GeVWeight","truthZpt50GeVWeight","truthZpt100GeVWeight","truthZpt150GeVWeight","truthZpt200GeVWeight",truthWptWeight,"bTagWeight3JetUp")
bTagLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthZpt0GeVWeight","truthZpt50GeVWeight","truthZpt100GeVWeight","truthZpt150GeVWeight","truthZpt200GeVWeight",truthWptWeight,"bTagWeight3JetDown")

trigHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeightUp","truthZpt0GeVWeight","truthZpt50GeVWeight","truthZpt100GeVWeight","truthZpt150GeVWeight","truthZpt200GeVWeight",truthWptWeight,"bTagWeight3Jet")
trigLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeightDown","truthZpt0GeVWeight","truthZpt50GeVWeight","truthZpt100GeVWeight","truthZpt150GeVWeight","truthZpt200GeVWeight",truthWptWeight,"bTagWeight3Jet")

lepHighWeights = ("genWeight","eventWeight","leptonWeightUp","triggerWeight","truthZpt0GeVWeight","truthZpt50GeVWeight","truthZpt100GeVWeight","truthZpt150GeVWeight","truthZpt200GeVWeight",truthWptWeight,"bTagWeight3Jet")
lepLowWeights = ("genWeight","eventWeight","leptonWeightDown","triggerWeight","truthZpt0GeVWeight","truthZpt50GeVWeight","truthZpt100GeVWeight","truthZpt150GeVWeight","truthZpt200GeVWeight",truthWptWeight,"bTagWeight3Jet")

## True Zpt reweighting

pT0GeVHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"truthZpt50GeVWeight","truthZpt100GeVWeight","truthZpt150GeVWeight","truthZpt200GeVWeight","truthZpt0GeVWeightUp","bTagWeight3Jet")
pT0GeVLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"truthZpt50GeVWeight","truthZpt100GeVWeight","truthZpt150GeVWeight","truthZpt200GeVWeight","truthZpt0GeVWeightDown","bTagWeight3Jet")

pT50GeVHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"truthZpt0GeVWeight","truthZpt100GeVWeight","truthZpt150GeVWeight","truthZpt200GeVWeight","truthZpt50GeVWeightUp","bTagWeight3Jet")
pT50GeVLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"truthZpt0GeVWeight","truthZpt100GeVWeight","truthZpt150GeVWeight","truthZpt200GeVWeight","truthZpt50GeVWeightDown","bTagWeight3Jet")

pT100GeVHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"truthZpt0GeVWeight","truthZpt50GeVWeight","truthZpt150GeVWeight","truthZpt200GeVWeight","truthZpt100GeVWeightUp","bTagWeight3Jet")
pT100GeVLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"truthZpt0GeVWeight","truthZpt50GeVWeight","truthZpt150GeVWeight","truthZpt200GeVWeight","truthZpt100GeVWeightDown","bTagWeight3Jet")

pT150GeVHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"truthZpt0GeVWeight","truthZpt50GeVWeight","truthZpt100GeVWeight","truthZpt200GeVWeight","truthZpt150GeVWeightUp","bTagWeight3Jet")
pT150GeVLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"truthZpt0GeVWeight","truthZpt50GeVWeight","truthZpt100GeVWeight","truthZpt200GeVWeight","truthZpt150GeVWeightDown","bTagWeight3Jet")

pT200GeVHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"truthZpt0GeVWeight","truthZpt50GeVWeight","truthZpt100GeVWeight","truthZpt150GeVWeight","truthZpt200GeVWeightUp","bTagWeight3Jet")
pT200GeVLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"truthZpt0GeVWeight","truthZpt50GeVWeight","truthZpt100GeVWeight","truthZpt150GeVWeight","truthZpt200GeVWeightDown","bTagWeight3Jet")


## HF uncertainty on V+Jets

hfHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"truthZpt0GeVWeight","truthZpt50GeVWeight","truthZpt100GeVWeight","truthZpt150GeVWeight","truthZpt200GeVWeight","hfWeightUp","bTagWeight3Jet")
hfLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"truthZpt0GeVWeight","truthZpt50GeVWeight","truthZpt100GeVWeight","truthZpt150GeVWeight","truthZpt200GeVWeight","hfWeightDown","bTagWeight3Jet")
                                                                                        
#--------------------
# List of systematics
#--------------------



# KtScale uncertainty as histoSys - two-sided, no additional normalization
#topKtScale = Systematic("KtScaleTop",configMgr.weights,ktScaleTopHighWeights,ktScaleTopLowWeights,"weight","normHistoSys")
#wzKtScale = Systematic("KtScaleWZ",configMgr.weights,ktScaleWHighWeights,ktScaleWLowWeights,"weight","normHistoSys")

# Additional Uncrtainty from the Zpt fit
zpT0GeV = Systematic("Zpt0GeV",configMgr.weights,pT0GeVHighWeights,pT0GeVLowWeights,"weight","overallSys")
zpT50GeV = Systematic("Zpt50GeV",configMgr.weights,pT50GeVHighWeights,pT50GeVLowWeights,"weight","overallSys")
zpT100GeV = Systematic("Zpt100GeV",configMgr.weights,pT100GeVHighWeights,pT100GeVLowWeights,"weight","overallSys")
zpT150GeV = Systematic("Zpt150GeV",configMgr.weights,pT150GeVHighWeights,pT150GeVLowWeights,"weight","overallSys")
zpT200GeV = Systematic("Zpt200GeV",configMgr.weights,pT200GeVHighWeights,pT200GeVLowWeights,"weight","overallSys")

#  HF uncertainty on V+Jets
hf = Systematic("HF",configMgr.weights,hfHighWeights,hfLowWeights,"weight","overallSys")

# Signal XSec uncertainty as overallSys (pure yeild affect)
xsecSig = Systematic("XSS",configMgr.weights,xsecSigHighWeights,xsecSigLowWeights,"weight","overallSys")


# Trigger weight uncertainty as overallSys
trigZR = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigTR = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigVR = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigS3 = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigS4 = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigS3T = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigS4T = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigS4DL = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")
trigS2DL = Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")


# Lepton weight uncertainty as overallSys
lepZR = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepTR = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepVR = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepS3 = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepS4 = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepS3T = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepS4T = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepS2DL = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")
lepS4DL = Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")

# B-tag uncertainty as overallSys in TR
btagZR = Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","overallSys")
btagTR = Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","overallSys")
btagVR = Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","overallSys")
btagS = Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","overallSys")

# JES uncertainty as shapeSys - one systematic per region (combine WR and TR), merge samples

jesLow = Systematic("JLow","_NoSys","_JESLowup","_JESLowdown","tree","histoSys")
jesMedium = Systematic("JMedium","_NoSys","_JESMediumup","_JESMediumdown","tree","histoSys")
jesHigh = Systematic("JHigh","_NoSys","_JESHighup","_JESHighdown","tree","histoSys")
jesSignal = Systematic("JSig","_NoSys","_JESup","_JESdown","tree","histoSys")


#jesWRLow = Systematic("JWRLow","_NoSys","_JESLowup","_JESLowdown","tree","normHistoSys")
#jesWRMedium = Systematic("JWRMedium","_NoSys","_JESMediumup","_JESMediumdown","tree","normHistoSys")
#jesWRHigh = Systematic("JWRHigh","_NoSys","_JESHighup","_JESHighdown","tree","normHistoSys")

#jesTRLow = Systematic("JTRLow","_NoSys","_JESLowup","_JESLowdown","tree","normHistoSys")
#jesTRMedium = Systematic("JTRMedium","_NoSys","_JESMediumup","_JESMediumdown","tree","normHistoSys")
#jesTRHigh = Systematic("JTRHigh","_NoSys","_JESHighup","_JESHighdown","tree","normHistoSys")

#jesCRLow = Systematic("JCRLow","_NoSys","_JESLowup","_JESLowdown","tree","normHistoSys")
#jesCRMedium = Systematic("JCRMedium","_NoSys","_JESMediumup","_JESMediumdown","tree","normHistoSys")
#jesCRHigh = Systematic("JCRHigh","_NoSys","_JESHighup","_JESHighdown","tree","normHistoSys")

#jesS3Low = Systematic("JS3Low","_NoSys","_JESLowup","_JESLowdown","tree","normHistoSys")
#jesS3Medium = Systematic("JS3Medium","_NoSys","_JESMediumup","_JESMediumdown","tree","normHistoSys")
#jesS3High = Systematic("JS3High","_NoSys","_JESHighup","_JESHighdown","tree","normHistoSys")

#jesS3TLow = Systematic("JS3TLow","_NoSys","_JESLowup","_JESLowdown","tree","normHistoSys")
#jesS3TMedium = Systematic("JS3TMedium","_NoSys","_JESMediumup","_JESMediumdown","tree","normHistoSys")
#jesS3THigh = Systematic("JS3THigh","_NoSys","_JESHighup","_JESHighdown","tree","normHistoSys")

#jesS4Low = Systematic("JS4Low","_NoSys","_JESLowup","_JESLowdown","tree","normHistoSys")
#jesS4Medium = Systematic("JS4Medium","_NoSys","_JESMediumup","_JESMediumdown","tree","normHistoSys")
#jesS4High = Systematic("JS4High","_NoSys","_JESHighup","_JESHighdown","tree","normHistoSys")

#jesS4TLow = Systematic("JS4TLow","_NoSys","_JESLowup","_JESLowdown","tree","normHistoSys")
#jesS4TMedium = Systematic("JS4TMedium","_NoSys","_JESMediumup","_JESMediumdown","tree","normHistoSys")
#jesS4THigh = Systematic("JS4THigh","_NoSys","_JESHighup","_JESHighdown","tree","normHistoSys")

#jesZR = Systematic("JZ","_NoSys","_JESup","_JESdown","tree","normHistoSys")
#jesTR = Systematic("JC","_NoSys","_JESup","_JESdown","tree","normHistoSys")
#jesS3 = Systematic("J3","_NoSys","_JESup","_JESdown","tree","normHistoSys")
#jesS4 = Systematic("J4","_NoSys","_JESup","_JESdown","tree","normHistoSys")
#jesS3T = Systematic("J3T","_NoSys","_JESup","_JESdown","tree","normHistoSys")
#jesS4T = Systematic("J4T","_NoSys","_JESup","_JESdown","tree","normHistoSys")
jesVR2 = Systematic("JV2","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVR3 = Systematic("JV3","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVR4 = Systematic("JV4","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVZ2 = Systematic("JZ2","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVZ3 = Systematic("JZ3","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesVZ4 = Systematic("JZ4","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS2DL = Systematic("J2DL","_NoSys","_JESup","_JESdown","tree","normHistoSys")
jesS4DL = Systematic("J4DL","_NoSys","_JESup","_JESdown","tree","normHistoSys")

# LES uncertainty as overallSys - one per channel
lesZR = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesTR = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesVR = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesS3 = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesS4 = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesS3T = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesS4T = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesS2DL = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")
lesS4DL = Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")


# LER with muon system as overallSys - one per channel
lermsZR = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsTR = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsVR = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsS3 = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsS4 = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsS3T = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsS4T = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsS2DL = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")
lermsS4DL = Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")

# LER with inner detector as overallSys - one per channel
leridZR = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridTR = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridVR = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridS3 = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridS4 = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridS3T = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridS4T = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridS2DL = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")
leridS4DL = Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")

# MET cell-out uncertainty as overallSys - one per channel
metcoZR = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoTR = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoVR = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoS3 = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoS4 = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoS3T = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoS4T = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoS2DL = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")
metcoS4DL = Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")

# MET pileup uncertainty as overallSys - one per channel
# CHANGED TO HISTOSYS TO BE CONSISTENT WITH 1LEP
metpuZR = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuTR = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuVR = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuS3 = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuS4 = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuS3T = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuS4T = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuS2DL = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")
metpuS4DL = Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")

# List of systematics
configMgr.nomName = "_NoSys"

#Parameters of the Measurement
measName = "BasicMeasurement"
measLumi = 1.
measLumiError = 0.037

# nJet Binning for Top Control region

nJetTopeeRegions = ["TRee"]
nJetTopeeNBins = 8
nJetTopeeBinLow = 2
nJetTopeeBinHigh = 10

nJetTopeRegions = ["TREl"]
nJetTopeNBins = 8
nJetTopeBinLow = 3
nJetTopeBinHigh = 10

nJetTopemRegions = ["TRem"]
nJetTopemNBins = 8
nJetTopemBinLow = 2
nJetTopemBinHigh = 10

nJetTopmmRegions = ["TRmm"]
nJetTopmmNBins = 8
nJetTopmmBinLow = 2
nJetTopmmBinHigh = 10

nJetTopmRegions = ["TRMu"]
nJetTopmNBins = 8
nJetTopmBinLow = 3
nJetTopmBinHigh = 10

# List of samples and their plotting colours
topSample_Np0 = Sample("Top_Np0",100)
topSample_Np0.setNormFactor("mu_Top_Np0",1.,0.,5.)
topSample_Np0.setStatConfig(useStat)
wzSample_Np0 = Sample("WZ_Np0",55)
wzSample_Np0.setNormFactor("mu_WZ_Np0",1.,0.,5.)
wzSample_Np0.setStatConfig(useStat)
topSample_Np1 = Sample("Top_Np1",97)
topSample_Np1.setNormFactor("mu_Top_Np1",1.,0.,5.)
topSample_Np1.setStatConfig(useStat)
wzSample_Np1 = Sample("WZ_Np1",58)
wzSample_Np1.setNormFactor("mu_WZ_Np1",1.,0.,5.)
wzSample_Np1.setStatConfig(useStat)
topSample_Np2 = Sample("Top_Np2",94)
topSample_Np2.setNormFactor("mu_Top_Np2",1.,0.,5.)
topSample_Np2.setStatConfig(useStat)
wzSample_Np2 = Sample("WZ_Np2",61)
wzSample_Np2.setNormFactor("mu_WZ_Np2",1.,0.,5.)
wzSample_Np2.setStatConfig(useStat)
topSample_Np3 = Sample("Top_Np3",91)
topSample_Np3.setNormFactor("mu_Top_Np3",1.,0.,5.)
topSample_Np3.setStatConfig(useStat)
wzSample_Np3 = Sample("WZ_Np3",64)
wzSample_Np3.setNormFactor("mu_WZ_Np3",1.,0.,5.)
wzSample_Np3.setStatConfig(useStat)
topSample_Np4 = Sample("Top_Np4",91)
topSample_Np4.setNormFactor("mu_Top_Np3",1.,0.,5.)
topSample_Np4.setStatConfig(useStat)
wzSample_Np4 = Sample("WZ_Np4",67)
wzSample_Np4.setNormFactor("mu_WZ_Np4",1.,0.,5.)
wzSample_Np4.setStatConfig(useStat)
topSample_Np5 = Sample("Top_Np5",91)
topSample_Np5.setNormFactor("mu_Top_Np3",1.,0.,5.)
topSample_Np5.setStatConfig(useStat) 
wzSample_Np5 = Sample("WZ_Np5",70)
wzSample_Np5.setNormFactor("mu_WZ_Np5",1.,0.,5.)
wzSample_Np5.setStatConfig(useStat)

### Additional scale uncertainty on WZ Np0 and WZ Np1

err_WZ_Np0 = Systematic("err_WZ_Np0", configMgr.weights,1.06 ,0.96, "user","userOverallSys")
err_WZ_Np1 = Systematic("err_WZ_Np1", configMgr.weights,1.06 ,0.83, "user","userOverallSys")

wzSample_Np0.addSystematic(err_WZ_Np0)
wzSample_Np1.addSystematic(err_WZ_Np1)

### Additional uncertainty on the V+HF samples

wzSample_Np0.addSystematic(hf)
wzSample_Np1.addSystematic(hf)
wzSample_Np2.addSystematic(hf)
wzSample_Np3.addSystematic(hf)
wzSample_Np4.addSystematic(hf)


bgSample = Sample("BG",kGreen)
bgSample.setNormFactor("mu_BG",1.,0.,5.)
bgSample.setStatConfig(useStat)

### Additional uncertainty on mu_BG

err_BG = Systematic("err_BG", configMgr.weights,1.2 ,0.8, "user","userOverallSys")
bgSample.addSystematic(err_BG)

qcdSample = Sample("QCD",kGray+1)
qcdSample.setQCD(True,"histoSys")
qcdSample.setStatConfig(useStat)
dataSample = Sample("Data",kBlack)
dataSample.setData()

nJetZmmRegions = ["ZRmm"]
nJetZmmNBins = 8
nJetZmmBinLow = 2
nJetZmmBinHigh = 10

nJetZmRegions = ["WRMu"]
nJetZmNBins = 8
nJetZmBinLow = 3
nJetZmBinHigh = 10

nJetZeeRegions = ["ZRee"]
nJetZeeNBins = 8
nJetZeeBinLow = 2
nJetZeeBinHigh = 10

nJetZeRegions = ["WREl"]
nJetZeNBins = 8
nJetZeBinLow = 3
nJetZeBinHigh = 10

ZptZmmRegions = ["ZRmm"]
ZptZmmNBins = 50
ZptZmmBinLow = 0
ZptZmmBinHigh = 1000

ZptZeeRegions = ["ZRee"]
ZptZeeNBins = 50
ZptZeeBinLow = 0
ZptZeeBinHigh = 1000

srNBins = 1
srBinLow = 0.5
srBinHigh = 1.5

                
#Create TopLevelXML objects
bkgOnly = configMgr.addTopLevelXML("bkgonly")
bgdsamples=[qcdSample,bgSample,topSample_Np0,topSample_Np1,topSample_Np2,topSample_Np3,topSample_Np4,topSample_Np5,wzSample_Np0,wzSample_Np1,wzSample_Np2,wzSample_Np3,wzSample_Np4,wzSample_Np5,dataSample]

if doSignalOnly:
    bgdsamples=[]

for sam in bgdsamples:
    sam.setFileList(bgdFiles)

bkgOnly.addSamples(bgdsamples)

if useStat:
    bkgOnly.statErrThreshold=0.05 #0.03??
else:
    bkgOnly.statErrThreshold=None


#Add Measurement
meas=bkgOnly.addMeasurement(measName,measLumi,measLumiError)
meas.addPOI("mu_SIG")

# Fix Background 
meas.addParamSetting("mu_BG","const",1.0)
meas.addParamSetting("mu_WZ_Np0","const",1.0)
meas.addParamSetting("mu_WZ_Np1","const",1.0)


#--------------------------------------------------------------
# Background fit regions 
#--------------------------------------------------------------

BGList=["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]

if doSignalOnly:
    BGList=[]


##### nJet for Top ####

# ele ele

nJetTopeeChannel=bkgOnly.addChannel("nJet",nJetTopeeRegions,nJetTopeeNBins,nJetTopeeBinLow,nJetTopeeBinHigh)
nJetTopeeChannel.hasB = True
nJetTopeeChannel.hasBQCD = True
nJetTopeeChannel.useOverflowBin = False
nJetTopeeChannel.addSystematic(jesLow)
nJetTopeeChannel.addSystematic(jesMedium)
nJetTopeeChannel.addSystematic(jesHigh)
nJetTopeeChannel.addSystematic(btagTR)
nJetTopeeChannel.addSystematic(lepTR)
#[nJetTopeeChannel.getSample(sam).addSystematic(zpT0GeV) for sam in BGList]
[nJetTopeeChannel.getSample(sam).addSystematic(zpT50GeV) for sam in BGList]
[nJetTopeeChannel.getSample(sam).addSystematic(zpT100GeV) for sam in BGList]
[nJetTopeeChannel.getSample(sam).addSystematic(zpT150GeV) for sam in BGList]
[nJetTopeeChannel.getSample(sam).addSystematic(zpT200GeV) for sam in BGList]
if fullSyst:
    nJetTopeeChannel.addSystematic(metcoTR)
    nJetTopeeChannel.addSystematic(metpuTR)
    nJetTopeeChannel.addSystematic(trigTR)
    [nJetTopeeChannel.getSample(sam).addSystematic(lesTR) for sam in BGList]
    [nJetTopeeChannel.getSample(sam).addSystematic(lermsTR) for sam in BGList]
    [nJetTopeeChannel.getSample(sam).addSystematic(leridTR) for sam in BGList]


#  single ele

nJetTopeChannel=bkgOnly.addChannel("nJet",nJetTopeRegions,nJetTopeNBins,nJetTopeBinLow,nJetTopeBinHigh)
nJetTopeChannel.hasB = True
nJetTopeChannel.hasBQCD = True
nJetTopeChannel.useOverflowBin = False
nJetTopeChannel.addSystematic(jesLow)
nJetTopeChannel.addSystematic(jesMedium)
nJetTopeChannel.addSystematic(jesHigh)
nJetTopeChannel.addSystematic(btagTR)
nJetTopeChannel.addSystematic(lepTR)
#[nJetTopeChannel.getSample(sam).addSystematic(zpT0GeV) for sam in BGList]
[nJetTopeChannel.getSample(sam).addSystematic(zpT50GeV) for sam in BGList]
[nJetTopeChannel.getSample(sam).addSystematic(zpT100GeV) for sam in BGList]
[nJetTopeChannel.getSample(sam).addSystematic(zpT150GeV) for sam in BGList]
[nJetTopeChannel.getSample(sam).addSystematic(zpT200GeV) for sam in BGList]
if fullSyst:
    nJetTopeChannel.addSystematic(metcoTR)
    nJetTopeChannel.addSystematic(metpuTR)
    nJetTopeChannel.addSystematic(trigTR)
    [nJetTopeChannel.getSample(sam).addSystematic(lesTR) for sam in BGList]
    [nJetTopeChannel.getSample(sam).addSystematic(lermsTR) for sam in BGList]
    [nJetTopeChannel.getSample(sam).addSystematic(leridTR) for sam in BGList]    


#  ele mu

nJetTopemChannel=bkgOnly.addChannel("nJet",nJetTopemRegions,nJetTopemNBins,nJetTopemBinLow,nJetTopemBinHigh)
nJetTopemChannel.hasB = True
nJetTopemChannel.hasBQCD = True
nJetTopemChannel.useOverflowBin = False
nJetTopemChannel.addSystematic(jesLow)
nJetTopemChannel.addSystematic(jesMedium)
nJetTopemChannel.addSystematic(jesHigh)
nJetTopemChannel.addSystematic(btagTR)
nJetTopemChannel.addSystematic(lepTR)
#[nJetTopemChannel.getSample(sam).addSystematic(zpT0GeV) for sam in BGList]
[nJetTopemChannel.getSample(sam).addSystematic(zpT50GeV) for sam in BGList]
[nJetTopemChannel.getSample(sam).addSystematic(zpT100GeV) for sam in BGList]
[nJetTopemChannel.getSample(sam).addSystematic(zpT150GeV) for sam in BGList]
[nJetTopemChannel.getSample(sam).addSystematic(zpT200GeV) for sam in BGList]
if fullSyst:
    nJetTopemChannel.addSystematic(metcoTR)
    nJetTopemChannel.addSystematic(metpuTR)
    nJetTopemChannel.addSystematic(trigTR)
    [nJetTopemChannel.getSample(sam).addSystematic(lesTR) for sam in BGList]
    [nJetTopemChannel.getSample(sam).addSystematic(lermsTR) for sam in BGList]
    [nJetTopemChannel.getSample(sam).addSystematic(leridTR) for sam in BGList]


# mu mu

nJetTopmmChannel=bkgOnly.addChannel("nJet",nJetTopmmRegions,nJetTopmmNBins,nJetTopmmBinLow,nJetTopmmBinHigh)
nJetTopmmChannel.hasB = True
nJetTopmmChannel.hasBQCD = True
nJetTopmmChannel.useOverflowBin = False
nJetTopmmChannel.addSystematic(jesLow)
nJetTopmmChannel.addSystematic(jesMedium)
nJetTopmmChannel.addSystematic(jesHigh)
nJetTopmmChannel.addSystematic(btagTR)
nJetTopmmChannel.addSystematic(lepTR)
#[nJetTopmmChannel.getSample(sam).addSystematic(zpT0GeV) for sam in BGList]
[nJetTopmmChannel.getSample(sam).addSystematic(zpT50GeV) for sam in BGList]
[nJetTopmmChannel.getSample(sam).addSystematic(zpT100GeV) for sam in BGList]
[nJetTopmmChannel.getSample(sam).addSystematic(zpT150GeV) for sam in BGList]
[nJetTopmmChannel.getSample(sam).addSystematic(zpT200GeV) for sam in BGList]
if fullSyst:
    nJetTopmmChannel.addSystematic(metcoTR)
    nJetTopmmChannel.addSystematic(metpuTR)
    nJetTopmmChannel.addSystematic(trigTR)
    [nJetTopmmChannel.getSample(sam).addSystematic(lesTR) for sam in BGList]
    [nJetTopmmChannel.getSample(sam).addSystematic(lermsTR) for sam in BGList]
    [nJetTopmmChannel.getSample(sam).addSystematic(leridTR) for sam in BGList]


# single mu

nJetTopmChannel=bkgOnly.addChannel("nJet",nJetTopmRegions,nJetTopmNBins,nJetTopmBinLow,nJetTopmBinHigh)
nJetTopmChannel.hasB = True
nJetTopmChannel.hasBQCD = True
nJetTopmChannel.useOverflowBin = False
nJetTopmChannel.addSystematic(jesLow)
nJetTopmChannel.addSystematic(jesMedium)
nJetTopmChannel.addSystematic(jesHigh)
nJetTopmChannel.addSystematic(btagTR)
nJetTopmChannel.addSystematic(lepTR)
#[nJetTopmChannel.getSample(sam).addSystematic(zpT0GeV) for sam in BGList]
[nJetTopmChannel.getSample(sam).addSystematic(zpT50GeV) for sam in BGList]
[nJetTopmChannel.getSample(sam).addSystematic(zpT100GeV) for sam in BGList]
[nJetTopmChannel.getSample(sam).addSystematic(zpT150GeV) for sam in BGList]
[nJetTopmChannel.getSample(sam).addSystematic(zpT200GeV) for sam in BGList]
if fullSyst:
    nJetTopmChannel.addSystematic(metcoTR)
    nJetTopmChannel.addSystematic(metpuTR)
    nJetTopmChannel.addSystematic(trigTR)
    [nJetTopmChannel.getSample(sam).addSystematic(lesTR) for sam in BGList]
    [nJetTopmChannel.getSample(sam).addSystematic(lermsTR) for sam in BGList]
    [nJetTopmChannel.getSample(sam).addSystematic(leridTR) for sam in BGList]
    

####### nJet for W/Z  #######
    
# ele ele    

nJetZeeChannel=bkgOnly.addChannel("nJet",nJetZeeRegions,nJetZeeNBins,nJetZeeBinLow,nJetZeeBinHigh)
nJetZeeChannel.hasB = False
nJetZeeChannel.hasBQCD = False
nJetZeeChannel.addSystematic(jesLow)
nJetZeeChannel.addSystematic(jesMedium)
nJetZeeChannel.addSystematic(jesHigh)
nJetZeeChannel.addSystematic(lepZR)
#[nJetZeeChannel.getSample(sam).addSystematic(zpT0GeV) for sam in BGList]
[nJetZeeChannel.getSample(sam).addSystematic(zpT50GeV) for sam in BGList]
[nJetZeeChannel.getSample(sam).addSystematic(zpT100GeV) for sam in BGList]
[nJetZeeChannel.getSample(sam).addSystematic(zpT150GeV) for sam in BGList]
[nJetZeeChannel.getSample(sam).addSystematic(zpT200GeV) for sam in BGList]
if fullSyst:
    nJetZeeChannel.addSystematic(metcoZR)
    nJetZeeChannel.addSystematic(metpuZR)
    nJetZeeChannel.addSystematic(trigZR)
    [nJetZeeChannel.getSample(sam).addSystematic(lesZR) for sam in BGList]
    [nJetZeeChannel.getSample(sam).addSystematic(lermsZR) for sam in BGList]
    [nJetZeeChannel.getSample(sam).addSystematic(leridZR) for sam in BGList]


# single ele

nJetZeChannel=bkgOnly.addChannel("nJet",nJetZeRegions,nJetZeNBins,nJetZeBinLow,nJetZeBinHigh)
nJetZeChannel.hasB = False
nJetZeChannel.hasBQCD = False
nJetZeChannel.addSystematic(jesLow)
nJetZeChannel.addSystematic(jesMedium)
nJetZeChannel.addSystematic(jesHigh)
nJetZeChannel.addSystematic(btagZR)
nJetZeChannel.addSystematic(lepZR)
#[nJetZeChannel.getSample(sam).addSystematic(zpT0GeV) for sam in BGList]
[nJetZeChannel.getSample(sam).addSystematic(zpT50GeV) for sam in BGList]
[nJetZeChannel.getSample(sam).addSystematic(zpT100GeV) for sam in BGList]
[nJetZeChannel.getSample(sam).addSystematic(zpT150GeV) for sam in BGList]
[nJetZeChannel.getSample(sam).addSystematic(zpT200GeV) for sam in BGList]
if fullSyst:
    nJetZeChannel.addSystematic(metcoZR)
    nJetZeChannel.addSystematic(metpuZR)
    nJetZeChannel.addSystematic(trigZR)
    [nJetZeChannel.getSample(sam).addSystematic(lesZR) for sam in BGList]
    [nJetZeChannel.getSample(sam).addSystematic(lermsZR) for sam in BGList]
    [nJetZeChannel.getSample(sam).addSystematic(leridZR) for sam in BGList]    

  
# mu mu

nJetZmmChannel=bkgOnly.addChannel("nJet",nJetZmmRegions,nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
nJetZmmChannel.hasB = False
nJetZmmChannel.hasBQCD = False
nJetZmmChannel.addSystematic(jesLow)
nJetZmmChannel.addSystematic(jesMedium)
nJetZmmChannel.addSystematic(jesHigh)
nJetZmmChannel.addSystematic(lepZR)
#[nJetZmmChannel.getSample(sam).addSystematic(zpT0GeV) for sam in BGList]
[nJetZmmChannel.getSample(sam).addSystematic(zpT50GeV) for sam in BGList]
[nJetZmmChannel.getSample(sam).addSystematic(zpT100GeV) for sam in BGList]
[nJetZmmChannel.getSample(sam).addSystematic(zpT150GeV) for sam in BGList]
[nJetZmmChannel.getSample(sam).addSystematic(zpT200GeV) for sam in BGList]
if fullSyst:
    nJetZmmChannel.addSystematic(metcoZR)
    nJetZmmChannel.addSystematic(metpuZR)
    nJetZmmChannel.addSystematic(trigZR)
    [nJetZmmChannel.getSample(sam).addSystematic(lesZR) for sam in BGList]
    [nJetZmmChannel.getSample(sam).addSystematic(lermsZR) for sam in BGList]
    [nJetZmmChannel.getSample(sam).addSystematic(leridZR) for sam in BGList]


# single mu

nJetZmChannel=bkgOnly.addChannel("nJet",nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
nJetZmChannel.hasB = True
nJetZmChannel.hasBQCD = False
nJetZmChannel.addSystematic(jesLow)
nJetZmChannel.addSystematic(jesMedium)
nJetZmChannel.addSystematic(jesHigh)
nJetZmChannel.addSystematic(btagZR)
nJetZmChannel.addSystematic(lepZR)
#[nJetZmChannel.getSample(sam).addSystematic(zpT0GeV) for sam in BGList]
[nJetZmChannel.getSample(sam).addSystematic(zpT50GeV) for sam in BGList]
[nJetZmChannel.getSample(sam).addSystematic(zpT100GeV) for sam in BGList]
[nJetZmChannel.getSample(sam).addSystematic(zpT150GeV) for sam in BGList]
[nJetZmChannel.getSample(sam).addSystematic(zpT200GeV) for sam in BGList]
if fullSyst:
    nJetZmChannel.addSystematic(metcoZR)
    nJetZmChannel.addSystematic(metpuZR)
    nJetZmChannel.addSystematic(trigZR)
    [nJetZmChannel.getSample(sam).addSystematic(lesZR) for sam in BGList]
    [nJetZmChannel.getSample(sam).addSystematic(lermsZR) for sam in BGList]
    [nJetZmChannel.getSample(sam).addSystematic(leridZR) for sam in BGList]    
                                                                            

bkgOnly.setBkgConstrainChannels([nJetTopeeChannel,nJetZeeChannel,nJetTopeChannel,nJetZeChannel,nJetTopemChannel,nJetTopmmChannel,nJetZmmChannel,nJetTopmChannel,nJetZmChannel])




#-------------------------------------------------
# Signal regions - only do this if background only, add as validation regions! 
#-------------------------------------------------

# meffNBins = 1
# #    meffBinLow = 400.
# meffBinLow = 0.
# meffBinHigh = 1600.

meffNBinsS2 = 5
meffBinLowS2 = 700.
meffBinHighS2 = 1700.

meffNBinsS4 = 5
meffBinLowS4 = 600.
meffBinHighS4 = 1600.

meffNBinsHL = 6
meffBinLowHL = 400.
#meffBinLow = 0.
meffBinHighHL = 1600.


meffNBinsTR = 20
meffBinLowTR = 0.
#meffBinLow = 0.
meffBinHighTR = 2000.


metNBinsTR = 40
metBinLowTR = 0.
#meffBinLow = 0.
metBinHighTR = 800.


pt1NBinsTR = 40
pt1BinLowTR = 0.
#meffBinLow = 0.
pt1BinHighTR = 800.


pt2NBinsTR = 40
pt2BinLowTR = 0.
#meffBinLow = 0.
pt2BinHighTR = 800.

if doValidationSlope:


    ## check impact of kfactor fit on several distributions

    meffTR_El=bkgOnly.addChannel("meffInc",["TRElVR"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffTR_El.hasB = True
    meffTR_El.hasBQCD = True
    meffTR_El.useOverflowBin = True
    meffTR_El.addSystematic(jesLow)
    meffTR_El.addSystematic(jesMedium)
    meffTR_El.addSystematic(jesHigh)
    meffTR_El.addSystematic(lepTR)
    meffTR_El.addSystematic(btagTR)
    if fullSyst:
        meffTR_El.addSystematic(metcoTR)
        meffTR_El.addSystematic(metpuTR)
        meffTR_El.addSystematic(trigTR)
        meffTR_El.addSystematic(lesTR)
        meffTR_El.addSystematic(lermsTR)
        meffTR_El.addSystematic(leridTR)

    meffTR_Mu=bkgOnly.addChannel("meffInc",["TRMuVR"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffTR_Mu.hasB = True
    meffTR_Mu.hasBQCD = True
    meffTR_Mu.useOverflowBin = True
    meffTR_Mu.addSystematic(jesLow)
    meffTR_Mu.addSystematic(jesMedium)
    meffTR_Mu.addSystematic(jesHigh)
    meffTR_Mu.addSystematic(lepTR)
    meffTR_Mu.addSystematic(btagTR)
    if fullSyst:
        meffTR_Mu.addSystematic(metcoTR)
        meffTR_Mu.addSystematic(metpuTR)
        meffTR_Mu.addSystematic(trigTR)
        meffTR_Mu.addSystematic(lesTR)
        meffTR_Mu.addSystematic(lermsTR)
        meffTR_Mu.addSystematic(leridTR)

        

    metTR_El=bkgOnly.addChannel("met",["TRElVR2"],metNBinsTR,metBinLowTR,metBinHighTR)
    metTR_El.hasB = True
    metTR_El.hasBQCD = True
    metTR_El.useOverflowBin = True
    metTR_El.addSystematic(jesLow)
    metTR_El.addSystematic(jesMedium)
    metTR_El.addSystematic(jesHigh)
    metTR_El.addSystematic(lepTR)
    metTR_El.addSystematic(btagTR)
    if fullSyst:
        metTR_El.addSystematic(metcoTR)
        metTR_El.addSystematic(metpuTR)
        metTR_El.addSystematic(trigTR)
        metTR_El.addSystematic(lesTR)
        metTR_El.addSystematic(lermsTR)
        metTR_El.addSystematic(leridTR)


    metTR_Mu=bkgOnly.addChannel("met",["TRMuVR2"],metNBinsTR,metBinLowTR,metBinHighTR)
    metTR_Mu.hasB = True
    metTR_Mu.hasBQCD = True
    metTR_Mu.useOverflowBin = True
    metTR_Mu.addSystematic(jesLow)
    metTR_Mu.addSystematic(jesMedium)
    metTR_Mu.addSystematic(jesHigh)
    metTR_Mu.addSystematic(lepTR)
    metTR_Mu.addSystematic(btagTR)
    if fullSyst:
        metTR_Mu.addSystematic(metcoTR)
        metTR_Mu.addSystematic(metpuTR)
        metTR_Mu.addSystematic(trigTR)
        metTR_Mu.addSystematic(lesTR)
        metTR_Mu.addSystematic(lermsTR)
        metTR_Mu.addSystematic(leridTR)


    pt1TR_El=bkgOnly.addChannel("jet1Pt",["TRElVR"],pt1NBinsTR,pt1BinLowTR,pt1BinHighTR)
    pt1TR_El.hasB = True
    pt1TR_El.hasBQCD = True
    pt1TR_El.useOverflowBin = True
    pt1TR_El.addSystematic(jesLow)
    pt1TR_El.addSystematic(jesMedium)
    pt1TR_El.addSystematic(jesHigh)
    pt1TR_El.addSystematic(lepTR)
    pt1TR_El.addSystematic(btagTR)
    if fullSyst:
        pt1TR_El.addSystematic(metcoTR)
        pt1TR_El.addSystematic(metpuTR)
        pt1TR_El.addSystematic(trigTR)
        pt1TR_El.addSystematic(lesTR)
        pt1TR_El.addSystematic(lermsTR)
        pt1TR_El.addSystematic(leridTR)


    pt1TR_Mu=bkgOnly.addChannel("jet1Pt",["TRMuVR"],pt1NBinsTR,pt1BinLowTR,pt1BinHighTR)
    pt1TR_Mu.hasB = True
    pt1TR_Mu.hasBQCD = True
    pt1TR_Mu.useOverflowBin = True
    pt1TR_Mu.addSystematic(jesLow)
    pt1TR_Mu.addSystematic(jesMedium)
    pt1TR_Mu.addSystematic(jesHigh)
    pt1TR_Mu.addSystematic(lepTR)
    pt1TR_Mu.addSystematic(btagTR)
    if fullSyst:
        pt1TR_Mu.addSystematic(metcoTR)
        pt1TR_Mu.addSystematic(metpuTR)
        pt1TR_Mu.addSystematic(trigTR)
        pt1TR_Mu.addSystematic(lesTR)
        pt1TR_Mu.addSystematic(lermsTR)
        pt1TR_Mu.addSystematic(leridTR)

        
        
    pt2TR_El=bkgOnly.addChannel("jet2Pt",["TRElVR"],pt2NBinsTR,pt2BinLowTR,pt2BinHighTR)
    pt2TR_El.hasB = True
    pt2TR_El.hasBQCD = True
    pt2TR_El.useOverflowBin = True
    pt2TR_El.addSystematic(jesLow)
    pt2TR_El.addSystematic(jesMedium)
    pt2TR_El.addSystematic(jesHigh)
    pt2TR_El.addSystematic(lepTR)
    pt2TR_El.addSystematic(btagTR)
    if fullSyst:
        pt2TR_El.addSystematic(metcoTR)
        pt2TR_El.addSystematic(metpuTR)
        pt2TR_El.addSystematic(trigTR)
        pt2TR_El.addSystematic(lesTR)
        pt2TR_El.addSystematic(lermsTR)
        pt2TR_El.addSystematic(leridTR)


    pt2TR_Mu=bkgOnly.addChannel("jet2Pt",["TRMuVR"],pt2NBinsTR,pt2BinLowTR,pt2BinHighTR)
    pt2TR_Mu.hasB = True
    pt2TR_Mu.hasBQCD = True
    pt2TR_Mu.useOverflowBin = True
    pt2TR_Mu.addSystematic(jesLow)
    pt2TR_Mu.addSystematic(jesMedium)
    pt2TR_Mu.addSystematic(jesHigh)
    pt2TR_Mu.addSystematic(lepTR)
    pt2TR_Mu.addSystematic(btagTR)
    if fullSyst:
        pt2TR_Mu.addSystematic(metcoTR)
        pt2TR_Mu.addSystematic(metpuTR)
        pt2TR_Mu.addSystematic(trigTR)
        pt2TR_Mu.addSystematic(lesTR)
        pt2TR_Mu.addSystematic(lermsTR)
        pt2TR_Mu.addSystematic(leridTR) 

    wptWR_El=bkgOnly.addChannel("Wpt",["WRElVR"],metNBinsTR,metBinLowTR,metBinHighTR)
    wptWR_El.hasB = True
    wptWR_El.hasBQCD = False
    wptWR_El.useOverflowBin = True
    wptWR_El.addSystematic(jesLow)
    wptWR_El.addSystematic(jesMedium)
    wptWR_El.addSystematic(jesHigh)
    wptWR_El.addSystematic(lepTR)
    wptWR_El.addSystematic(btagTR)
    if fullSyst:
        wptWR_El.addSystematic(metcoTR)
        wptWR_El.addSystematic(metpuTR)
        wptWR_El.addSystematic(trigTR)
        wptWR_El.addSystematic(lesTR)
        wptWR_El.addSystematic(lermsTR)
        wptWR_El.addSystematic(leridTR)


    wptWR_Mu=bkgOnly.addChannel("Wpt",["WRMuVR"],metNBinsTR,metBinLowTR,metBinHighTR)
    wptWR_Mu.hasB = True
    wptWR_Mu.hasBQCD = False
    wptWR_Mu.useOverflowBin = True
    wptWR_Mu.addSystematic(jesLow)
    wptWR_Mu.addSystematic(jesMedium)
    wptWR_Mu.addSystematic(jesHigh)
    wptWR_Mu.addSystematic(lepTR)
    wptWR_Mu.addSystematic(btagTR)
    if fullSyst:
        wptWR_Mu.addSystematic(metcoTR)
        wptWR_Mu.addSystematic(metpuTR)
        wptWR_Mu.addSystematic(trigTR)
        wptWR_Mu.addSystematic(lesTR)
        wptWR_Mu.addSystematic(lermsTR)
        wptWR_Mu.addSystematic(leridTR)


    metWR_El=bkgOnly.addChannel("met",["WRElVR"],metNBinsTR,metBinLowTR,metBinHighTR)
    metWR_El.hasB = True
    metWR_El.hasBQCD = False
    metWR_El.useOverflowBin = True
    metWR_El.addSystematic(jesLow)
    metWR_El.addSystematic(jesMedium)
    metWR_El.addSystematic(jesHigh)
    metWR_El.addSystematic(lepTR)
    metWR_El.addSystematic(btagTR)
    if fullSyst:
        metWR_El.addSystematic(metcoTR)
        metWR_El.addSystematic(metpuTR)
        metWR_El.addSystematic(trigTR)
        metWR_El.addSystematic(lesTR)
        metWR_El.addSystematic(lermsTR)
        metWR_El.addSystematic(leridTR)


    metWR_Mu=bkgOnly.addChannel("met",["WRMuVR"],metNBinsTR,metBinLowTR,metBinHighTR)
    metWR_Mu.hasB = True
    metWR_Mu.hasBQCD = False
    metWR_Mu.useOverflowBin = True
    metWR_Mu.addSystematic(jesLow)
    metWR_Mu.addSystematic(jesMedium)
    metWR_Mu.addSystematic(jesHigh)
    metWR_Mu.addSystematic(lepTR)
    metWR_Mu.addSystematic(btagTR)
    if fullSyst:
        metWR_Mu.addSystematic(metcoTR)
        metWR_Mu.addSystematic(metpuTR)
        metWR_Mu.addSystematic(trigTR)
        metWR_Mu.addSystematic(lesTR)
        metWR_Mu.addSystematic(lermsTR)
        metWR_Mu.addSystematic(leridTR)       

    ZptZR_ee=bkgOnly.addChannel("Zpt",["ZRee"],metNBinsTR,metBinLowTR,metBinHighTR)
    ZptZR_ee.hasB = False
    ZptZR_ee.hasBQCD = False
    ZptZR_ee.useOverflowBin = True
    ZptZR_ee.addSystematic(jesLow)
    ZptZR_ee.addSystematic(jesMedium)
    ZptZR_ee.addSystematic(jesHigh)
    ZptZR_ee.addSystematic(lepTR)
    ZptZR_ee.addSystematic(btagTR)
    if fullSyst:
        ZptZR_ee.addSystematic(metcoTR)
        ZptZR_ee.addSystematic(metpuTR)
        ZptZR_ee.addSystematic(trigTR)
        ZptZR_ee.addSystematic(lesTR)
        ZptZR_ee.addSystematic(lermsTR)
        ZptZR_ee.addSystematic(leridTR)


    ZptZR_mm=bkgOnly.addChannel("Zpt",["ZRmm"],metNBinsTR,metBinLowTR,metBinHighTR)
    ZptZR_mm.hasB = False
    ZptZR_mm.hasBQCD = False
    ZptZR_mm.useOverflowBin = True
    ZptZR_mm.addSystematic(jesLow)
    ZptZR_mm.addSystematic(jesMedium)
    ZptZR_mm.addSystematic(jesHigh)
    ZptZR_mm.addSystematic(lepTR)
    ZptZR_mm.addSystematic(btagTR)
    if fullSyst:
        ZptZR_mm.addSystematic(metcoTR)
        ZptZR_mm.addSystematic(metpuTR)
        ZptZR_mm.addSystematic(trigTR)
        ZptZR_mm.addSystematic(lesTR)
        ZptZR_mm.addSystematic(lermsTR)
        ZptZR_mm.addSystematic(leridTR)


if doValidationSR:

    # S2 using meff
    meff2ee = bkgOnly.addChannel("meffInc",["S2ee"],meffNBinsS2,meffBinLowS2,meffBinHighS2)
    meff2ee.useOverflowBin=True
    meff2ee.addSystematic(jesLow)
    meff2ee.addSystematic(jesMedium)
    meff2ee.addSystematic(jesHigh)  
    #[s.mergeSamples([topSample_Np0.name,wzSample_Np0.name,topSample_Np1.name,wzSample_Np1.name,topSample_Np2.name,wzSample_Np2.name,topSample_Np3.name,wzSample_Np3.name,topSample_Np4.name,wzSample_Np4.name,topSample_Np5.name,wzSample_Np5.name,bgSample.name]) for s in meff2ee.getSystematic(jesS2DL.name)]
    meff2ee.addSystematic(lepS2DL)
    
    if fullSyst:
        meff2ee.addSystematic(metcoS2DL)
        meff2ee.addSystematic(metpuS2DL)
        meff2ee.addSystematic(trigS2DL)
        meff2ee.addSystematic(lesS2DL)
        meff2ee.addSystematic(lermsS2DL)
        meff2ee.addSystematic(leridS2DL)

    # S4 using meff
    meff4ee = bkgOnly.addChannel("meffInc",["S4ee"],meffNBinsS4,meffBinLowS4,meffBinHighS4)
    meff4ee.useOverflowBin=True
    meff4ee.addSystematic(jesLow)
    meff4ee.addSystematic(jesMedium)
    meff4ee.addSystematic(jesHigh)  
    #[s.mergeSamples([topSample_Np0.name,wzSample_Np0.name,topSample_Np1.name,wzSample_Np1.name,topSample_Np2.name,wzSample_Np2.name,topSample_Np3.name,wzSample_Np3.name,topSample_Np4.name,wzSample_Np4.name,topSample_Np5.name,wzSample_Np5.name,bgSample.name]) for s in meff4ee.getSystematic(jesS4DL.name)]
    meff4ee.addSystematic(lepS4DL)
    
    if fullSyst:
        meff4ee.addSystematic(metcoS4DL)
        meff4ee.addSystematic(metpuS4DL)
        meff4ee.addSystematic(trigS4DL)
        meff4ee.addSystematic(lesS4DL)
        meff4ee.addSystematic(lermsS4DL)
        meff4ee.addSystematic(leridS4DL)

    # S2 using meff
    meff2em = bkgOnly.addChannel("meffInc",["S2em"],meffNBinsS2,meffBinLowS2,meffBinHighS2)
    meff2em.useOverflowBin=True
    meff2em.addSystematic(jesLow)
    meff2em.addSystematic(jesMedium)
    meff2em.addSystematic(jesHigh) 
    #[s.mergeSamples([topSample_Np0.name,wzSample_Np0.name,topSample_Np1.name,wzSample_Np1.name,topSample_Np2.name,wzSample_Np2.name,topSample_Np3.name,wzSample_Np3.name,topSample_Np4.name,wzSample_Np4.name,topSample_Np5.name,wzSample_Np5.name,bgSample.name]) for s in meff2em.getSystematic(jesS2DL.name)]
    meff2em.addSystematic(lepS2DL)
    
    if fullSyst:
        meff2em.addSystematic(metcoS2DL)
        meff2em.addSystematic(metpuS2DL)
        meff2em.addSystematic(trigS2DL)
        meff2em.addSystematic(lesS2DL)
        meff2em.addSystematic(lermsS2DL)
        meff2em.addSystematic(leridS2DL)

    # S4 using meff
    meff4em = bkgOnly.addChannel("meffInc",["S4em"],meffNBinsS4,meffBinLowS4,meffBinHighS4)
    meff4em.useOverflowBin=True
    meff4em.addSystematic(jesLow)
    meff4em.addSystematic(jesMedium)
    meff4em.addSystematic(jesHigh) 
    #[s.mergeSamples([topSample_Np0.name,wzSample_Np0.name,topSample_Np1.name,wzSample_Np1.name,topSample_Np2.name,wzSample_Np2.name,topSample_Np3.name,wzSample_Np3.name,topSample_Np4.name,wzSample_Np4.name,topSample_Np5.name,wzSample_Np5.name,bgSample.name]) for s in meff4em.getSystematic(jesS4DL.name)]
    meff4em.addSystematic(lepS4DL)
    
    if fullSyst:
        meff4em.addSystematic(metcoS4DL)
        meff4em.addSystematic(metpuS4DL)
        meff4em.addSystematic(trigS4DL)
        meff4em.addSystematic(lesS4DL)
        meff4em.addSystematic(lermsS4DL)
        meff4em.addSystematic(leridS4DL)

    # S2 using meff
    meff2mm = bkgOnly.addChannel("meffInc",["S2mm"],meffNBinsS2,meffBinLowS2,meffBinHighS2)
    meff2mm.useOverflowBin=True
    meff2mm.addSystematic(jesLow)
    meff2mm.addSystematic(jesMedium)
    meff2mm.addSystematic(jesHigh) 
    #[s.mergeSamples([topSample_Np0.name,wzSample_Np0.name,topSample_Np1.name,wzSample_Np1.name,topSample_Np2.name,wzSample_Np2.name,topSample_Np3.name,wzSample_Np3.name,topSample_Np4.name,wzSample_Np4.name,topSample_Np5.name,wzSample_Np5.name,bgSample.name]) for s in meff2mm.getSystematic(jesS2DL.name)]
    meff2mm.addSystematic(lepS2DL)
    
    if fullSyst:
        meff2mm.addSystematic(metcoS2DL)
        meff2mm.addSystematic(metpuS2DL)
        meff2mm.addSystematic(trigS2DL)
        meff2mm.addSystematic(lesS2DL)
        meff2mm.addSystematic(lermsS2DL)
        meff2mm.addSystematic(leridS2DL)

    # S4 using meff
    meff4mm = bkgOnly.addChannel("meffInc",["S4mm"],meffNBinsS4,meffBinLowS4,meffBinHighS4)
    meff4mm.useOverflowBin=True
    meff4mm.addSystematic(jesLow)
    meff4mm.addSystematic(jesMedium)
    meff4mm.addSystematic(jesHigh)    
    #[s.mergeSamples([topSample_Np0.name,wzSample_Np0.name,topSample_Np1.name,wzSample_Np1.name,topSample_Np2.name,wzSample_Np2.name,topSample_Np3.name,wzSample_Np3.name,topSample_Np4.name,wzSample_Np4.name,topSample_Np5.name,wzSample_Np5.name,bgSample.name]) for s in meff4mm.getSystematic(jesS4DL.name)]
    meff4mm.addSystematic(lepS4DL)
    
    if fullSyst:
        meff4mm.addSystematic(metcoS4DL)
        meff4mm.addSystematic(metpuS4DL)
        meff4mm.addSystematic(trigS4DL)
        meff4mm.addSystematic(lesS4DL)
        meff4mm.addSystematic(lermsS4DL)
        meff4mm.addSystematic(leridS4DL)

# HARD LEPTON SRS

    meffS3_El=bkgOnly.addChannel("meffInc",["S3El"],meffNBinsHL,meffBinLowHL,meffBinHighHL)
    meffS3_El.useOverflowBin = True
    meffS3_El.addSystematic(jesLow)
    meffS3_El.addSystematic(jesMedium)
    meffS3_El.addSystematic(jesHigh)
    meffS3_El.addSystematic(lepS3)
    if fullSyst:
        meffS3_El.addSystematic(metcoS3)
        meffS3_El.addSystematic(metpuS3)
        meffS3_El.addSystematic(trigS3)
        meffS3_El.addSystematic(lesS3)
        meffS3_El.addSystematic(lermsS3)
        meffS3_El.addSystematic(leridS3)


    meffS3_Mu=bkgOnly.addChannel("meffInc",["S3Mu"],meffNBinsHL,meffBinLowHL,meffBinHighHL)
    meffS3_Mu.useOverflowBin = True
    meffS3_Mu.addSystematic(jesLow)
    meffS3_Mu.addSystematic(jesMedium)
    meffS3_Mu.addSystematic(jesHigh)
    meffS3_Mu.addSystematic(lepS3)
    if fullSyst:
        meffS3_Mu.addSystematic(metcoS3)
        meffS3_Mu.addSystematic(metpuS3)
        meffS3_Mu.addSystematic(trigS3)
        meffS3_Mu.addSystematic(lesS3)
        meffS3_Mu.addSystematic(lermsS3)
        meffS3_Mu.addSystematic(leridS3)   


    meffS4_El=bkgOnly.addChannel("meffInc",["S4El"],meffNBinsHL,meffBinLowHL,meffBinHighHL)
    meffS4_El.useOverflowBin = True
    meffS4_El.addSystematic(jesLow)
    meffS4_El.addSystematic(jesMedium)
    meffS4_El.addSystematic(jesHigh) 
    meffS4_El.addSystematic(lepS4)
    if fullSyst:
        meffS4_El.addSystematic(metcoS4)
        meffS4_El.addSystematic(metpuS4)
        meffS4_El.addSystematic(trigS4)
        meffS4_El.addSystematic(lesS4)
        meffS4_El.addSystematic(lermsS4)
        meffS4_El.addSystematic(leridS4)


    meffS4_Mu=bkgOnly.addChannel("meffInc",["S4Mu"],meffNBinsHL,meffBinLowHL,meffBinHighHL)
    meffS4_Mu.useOverflowBin = True
    meffS4_Mu.addSystematic(jesLow)
    meffS4_Mu.addSystematic(jesMedium)
    meffS4_Mu.addSystematic(jesHigh) 
    meffS4_Mu.addSystematic(lepS4)
    if fullSyst:
        meffS4_Mu.addSystematic(metcoS4)
        meffS4_Mu.addSystematic(metpuS4)
        meffS4_Mu.addSystematic(trigS4)
        meffS4_Mu.addSystematic(lesS4)
        meffS4_Mu.addSystematic(lermsS4)
        meffS4_Mu.addSystematic(leridS4)


    meffS3T_El=bkgOnly.addChannel("meffInc",["SR3jTEl"],1,1200,meffBinHighHL)
    meffS3T_El.useOverflowBin = True
    meffS3T_El.addSystematic(jesLow)
    meffS3T_El.addSystematic(jesMedium)
    meffS3T_El.addSystematic(jesHigh)
    meffS3T_El.addSystematic(lepS3T)
    if fullSyst:
        meffS3T_El.addSystematic(metcoS3T)
        meffS3T_El.addSystematic(metpuS3T)
        meffS3T_El.addSystematic(trigS3T)
        meffS3T_El.addSystematic(lesS3T)
        meffS3T_El.addSystematic(lermsS3T)
        meffS3T_El.addSystematic(leridS3T)


    meffS3T_Mu=bkgOnly.addChannel("meffInc",["SR3jTMu"],1,1200,meffBinHighHL)
    meffS3T_Mu.useOverflowBin = True
    meffS3T_Mu.addSystematic(jesLow)
    meffS3T_Mu.addSystematic(jesMedium)
    meffS3T_Mu.addSystematic(jesHigh)
    meffS3T_Mu.addSystematic(lepS3T)
    if fullSyst:
        meffS3T_Mu.addSystematic(metcoS3T)
        meffS3T_Mu.addSystematic(metpuS3T)
        meffS3T_Mu.addSystematic(trigS3T)
        meffS3T_Mu.addSystematic(lesS3T)
        meffS3T_Mu.addSystematic(lermsS3T)
        meffS3T_Mu.addSystematic(leridS3T)   


    meffS4T_El=bkgOnly.addChannel("meffInc",["SR4jTEl"],1,800,meffBinHighHL)
    meffS4T_El.useOverflowBin = True
    meffS4T_El.addSystematic(jesLow)
    meffS4T_El.addSystematic(jesMedium)
    meffS4T_El.addSystematic(jesHigh)
    meffS4T_El.addSystematic(lepS4T)
    if fullSyst:
        meffS4T_El.addSystematic(metcoS4T)
        meffS4T_El.addSystematic(metpuS4T)
        meffS4T_El.addSystematic(trigS4T)
        meffS4T_El.addSystematic(lesS4T)
        meffS4T_El.addSystematic(lermsS4T)
        meffS4T_El.addSystematic(leridS4T)


    meffS4T_Mu=bkgOnly.addChannel("meffInc",["SR4jTMu"],1,800,meffBinHighHL)
    meffS4T_Mu.useOverflowBin = True
    meffS4T_Mu.addSystematic(jesLow)
    meffS4T_Mu.addSystematic(jesMedium)
    meffS4T_Mu.addSystematic(jesHigh)
    meffS4T_Mu.addSystematic(lepS4T)
    if fullSyst:
        meffS4T_Mu.addSystematic(metcoS4T)
        meffS4T_Mu.addSystematic(metpuS4T)
        meffS4T_Mu.addSystematic(trigS4T)
        meffS4T_Mu.addSystematic(lesS4T)
        meffS4T_Mu.addSystematic(lermsS4T)
        meffS4T_Mu.addSystematic(leridS4T)
            
if doValidationDilep:


    ## check impact of kfactor fit on several distributions

    meffVR_ee=bkgOnly.addChannel("meffInc",["VRee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR_ee.hasB = True
    meffVR_ee.hasBQCD = True
    meffVR_ee.useOverflowBin = True
    meffVR_ee.addSystematic(jesLow)
    meffVR_ee.addSystematic(jesMedium)
    meffVR_ee.addSystematic(jesHigh)
    meffVR_ee.addSystematic(lepTR)
    meffVR_ee.addSystematic(btagTR)
    if fullSyst:
        meffVR_ee.addSystematic(metcoTR)
        meffVR_ee.addSystematic(metpuTR)
        meffVR_ee.addSystematic(trigTR)
        meffVR_ee.addSystematic(lesTR)
        meffVR_ee.addSystematic(lermsTR)
        meffVR_ee.addSystematic(leridTR)

    meffVR_em=bkgOnly.addChannel("meffInc",["VRem"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR_em.hasB = True
    meffVR_em.hasBQCD = True
    meffVR_em.useOverflowBin = True
    meffVR_em.addSystematic(jesLow)
    meffVR_em.addSystematic(jesMedium)
    meffVR_em.addSystematic(jesHigh)
    meffVR_em.addSystematic(lepTR)
    meffVR_em.addSystematic(btagTR)
    if fullSyst:
        meffVR_em.addSystematic(metcoTR)
        meffVR_em.addSystematic(metpuTR)
        meffVR_em.addSystematic(trigTR)
        meffVR_em.addSystematic(lesTR)
        meffVR_em.addSystematic(lermsTR)
        meffVR_em.addSystematic(leridTR)

    meffVR_mm=bkgOnly.addChannel("meffInc",["VRmm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR_mm.hasB = True
    meffVR_mm.hasBQCD = True
    meffVR_mm.useOverflowBin = True
    meffVR_mm.addSystematic(jesLow)
    meffVR_mm.addSystematic(jesMedium)
    meffVR_mm.addSystematic(jesHigh)
    meffVR_mm.addSystematic(lepTR)
    meffVR_mm.addSystematic(btagTR)
    if fullSyst:
        meffVR_mm.addSystematic(metcoTR)
        meffVR_mm.addSystematic(metpuTR)
        meffVR_mm.addSystematic(trigTR)
        meffVR_mm.addSystematic(lesTR)
        meffVR_mm.addSystematic(lermsTR)
        meffVR_mm.addSystematic(leridTR)

    nJetVR_ee=bkgOnly.addChannel("nJet",["VRee"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetVR_ee.hasB = True
    nJetVR_ee.hasBQCD = True
    nJetVR_ee.useOverflowBin = True
    nJetVR_ee.addSystematic(jesLow)
    nJetVR_ee.addSystematic(jesMedium)
    nJetVR_ee.addSystematic(jesHigh)
    nJetVR_ee.addSystematic(lepTR)
    nJetVR_ee.addSystematic(btagTR)
    if fullSyst:
        nJetVR_ee.addSystematic(metcoTR)
        nJetVR_ee.addSystematic(metpuTR)
        nJetVR_ee.addSystematic(trigTR)
        nJetVR_ee.addSystematic(lesTR)
        nJetVR_ee.addSystematic(lermsTR)
        nJetVR_ee.addSystematic(leridTR)

    nJetVR_em=bkgOnly.addChannel("nJet",["VRem"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetVR_em.hasB = True
    nJetVR_em.hasBQCD = True
    nJetVR_em.useOverflowBin = True
    nJetVR_em.addSystematic(jesLow)
    nJetVR_em.addSystematic(jesMedium)
    nJetVR_em.addSystematic(jesHigh)
    nJetVR_em.addSystematic(lepTR)
    nJetVR_em.addSystematic(btagTR)
    if fullSyst:
        nJetVR_em.addSystematic(metcoTR)
        nJetVR_em.addSystematic(metpuTR)
        nJetVR_em.addSystematic(trigTR)
        nJetVR_em.addSystematic(lesTR)
        nJetVR_em.addSystematic(lermsTR)
        nJetVR_em.addSystematic(leridTR)

    nJetVR_mm=bkgOnly.addChannel("nJet",["VRmm"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetVR_mm.hasB = True
    nJetVR_mm.hasBQCD = True
    nJetVR_mm.useOverflowBin = True
    nJetVR_mm.addSystematic(jesLow)
    nJetVR_mm.addSystematic(jesMedium)
    nJetVR_mm.addSystematic(jesHigh)
    nJetVR_mm.addSystematic(lepTR)
    nJetVR_mm.addSystematic(btagTR)
    if fullSyst:
        nJetVR_mm.addSystematic(metcoTR)
        nJetVR_mm.addSystematic(metpuTR)
        nJetVR_mm.addSystematic(trigTR)
        nJetVR_mm.addSystematic(lesTR)
        nJetVR_mm.addSystematic(lermsTR)
        nJetVR_mm.addSystematic(leridTR)

    meffVR2_ee=bkgOnly.addChannel("meffInc",["VR2ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR2_ee.hasB = True
    meffVR2_ee.hasBQCD = True
    meffVR2_ee.useOverflowBin = True
    meffVR2_ee.addSystematic(jesLow)
    meffVR2_ee.addSystematic(jesMedium)
    meffVR2_ee.addSystematic(jesHigh)
    meffVR2_ee.addSystematic(lepTR)
    meffVR2_ee.addSystematic(btagTR)
    if fullSyst:
        meffVR2_ee.addSystematic(metcoTR)
        meffVR2_ee.addSystematic(metpuTR)
        meffVR2_ee.addSystematic(trigTR)
        meffVR2_ee.addSystematic(lesTR)
        meffVR2_ee.addSystematic(lermsTR)
        meffVR2_ee.addSystematic(leridTR)

    meffVR2_em=bkgOnly.addChannel("meffInc",["VR2em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR2_em.hasB = True
    meffVR2_em.hasBQCD = True
    meffVR2_em.useOverflowBin = True
    meffVR2_em.addSystematic(jesLow)
    meffVR2_em.addSystematic(jesMedium)
    meffVR2_em.addSystematic(jesHigh)
    meffVR2_em.addSystematic(lepTR)
    meffVR2_em.addSystematic(btagTR)
    if fullSyst:
        meffVR2_em.addSystematic(metcoTR)
        meffVR2_em.addSystematic(metpuTR)
        meffVR2_em.addSystematic(trigTR)
        meffVR2_em.addSystematic(lesTR)
        meffVR2_em.addSystematic(lermsTR)
        meffVR2_em.addSystematic(leridTR)

    meffVR2_mm=bkgOnly.addChannel("meffInc",["VR2mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR2_mm.hasB = True
    meffVR2_mm.hasBQCD = True
    meffVR2_mm.useOverflowBin = True
    meffVR2_mm.addSystematic(jesLow)
    meffVR2_mm.addSystematic(jesMedium)
    meffVR2_mm.addSystematic(jesHigh)
    meffVR2_mm.addSystematic(lepTR)
    meffVR2_mm.addSystematic(btagTR)
    if fullSyst:
        meffVR2_mm.addSystematic(metcoTR)
        meffVR2_mm.addSystematic(metpuTR)
        meffVR2_mm.addSystematic(trigTR)
        meffVR2_mm.addSystematic(lesTR)
        meffVR2_mm.addSystematic(lermsTR)
        meffVR2_mm.addSystematic(leridTR)

    nJetVR2_ee=bkgOnly.addChannel("nJet",["VR2ee"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetVR2_ee.hasB = True
    nJetVR2_ee.hasBQCD = True
    nJetVR2_ee.useOverflowBin = True
    nJetVR2_ee.addSystematic(jesLow)
    nJetVR2_ee.addSystematic(jesMedium)
    nJetVR2_ee.addSystematic(jesHigh)
    nJetVR2_ee.addSystematic(lepTR)
    nJetVR2_ee.addSystematic(btagTR)
    if fullSyst:
        nJetVR2_ee.addSystematic(metcoTR)
        nJetVR2_ee.addSystematic(metpuTR)
        nJetVR2_ee.addSystematic(trigTR)
        nJetVR2_ee.addSystematic(lesTR)
        nJetVR2_ee.addSystematic(lermsTR)
        nJetVR2_ee.addSystematic(leridTR)

    nJetVR2_em=bkgOnly.addChannel("nJet",["VR2em"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetVR2_em.hasB = True
    nJetVR2_em.hasBQCD = True
    nJetVR2_em.useOverflowBin = True
    nJetVR2_em.addSystematic(jesLow)
    nJetVR2_em.addSystematic(jesMedium)
    nJetVR2_em.addSystematic(jesHigh)
    nJetVR2_em.addSystematic(lepTR)
    nJetVR2_em.addSystematic(btagTR)
    if fullSyst:
        nJetVR2_em.addSystematic(metcoTR)
        nJetVR2_em.addSystematic(metpuTR)
        nJetVR2_em.addSystematic(trigTR)
        nJetVR2_em.addSystematic(lesTR)
        nJetVR2_em.addSystematic(lermsTR)
        nJetVR2_em.addSystematic(leridTR)

    nJetVR2_mm=bkgOnly.addChannel("nJet",["VR2mm"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetVR2_mm.hasB = True
    nJetVR2_mm.hasBQCD = True
    nJetVR2_mm.useOverflowBin = True
    nJetVR2_mm.addSystematic(jesLow)
    nJetVR2_mm.addSystematic(jesMedium)
    nJetVR2_mm.addSystematic(jesHigh)
    nJetVR2_mm.addSystematic(lepTR)
    nJetVR2_mm.addSystematic(btagTR)
    if fullSyst:
        nJetVR2_mm.addSystematic(metcoTR)
        nJetVR2_mm.addSystematic(metpuTR)
        nJetVR2_mm.addSystematic(trigTR)
        nJetVR2_mm.addSystematic(lesTR)
        nJetVR2_mm.addSystematic(lermsTR)
        nJetVR2_mm.addSystematic(leridTR)

    meffVR3_ee=bkgOnly.addChannel("meffInc",["VR3ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR3_ee.hasB = True
    meffVR3_ee.hasBQCD = True
    meffVR3_ee.useOverflowBin = True
    meffVR3_ee.addSystematic(jesLow)
    meffVR3_ee.addSystematic(jesMedium)
    meffVR3_ee.addSystematic(jesHigh)
    meffVR3_ee.addSystematic(lepTR)
    meffVR3_ee.addSystematic(btagTR)
    if fullSyst:
        meffVR3_ee.addSystematic(metcoTR)
        meffVR3_ee.addSystematic(metpuTR)
        meffVR3_ee.addSystematic(trigTR)
        meffVR3_ee.addSystematic(lesTR)
        meffVR3_ee.addSystematic(lermsTR)
        meffVR3_ee.addSystematic(leridTR)

    meffVR3_em=bkgOnly.addChannel("meffInc",["VR3em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR3_em.hasB = True
    meffVR3_em.hasBQCD = True
    meffVR3_em.useOverflowBin = True
    meffVR3_em.addSystematic(jesLow)
    meffVR3_em.addSystematic(jesMedium)
    meffVR3_em.addSystematic(jesHigh)
    meffVR3_em.addSystematic(lepTR)
    meffVR3_em.addSystematic(btagTR)
    if fullSyst:
        meffVR3_em.addSystematic(metcoTR)
        meffVR3_em.addSystematic(metpuTR)
        meffVR3_em.addSystematic(trigTR)
        meffVR3_em.addSystematic(lesTR)
        meffVR3_em.addSystematic(lermsTR)
        meffVR3_em.addSystematic(leridTR)

    meffVR3_mm=bkgOnly.addChannel("meffInc",["VR3mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR3_mm.hasB = True
    meffVR3_mm.hasBQCD = True
    meffVR3_mm.useOverflowBin = True
    meffVR3_mm.addSystematic(jesLow)
    meffVR3_mm.addSystematic(jesMedium)
    meffVR3_mm.addSystematic(jesHigh)
    meffVR3_mm.addSystematic(lepTR)
    meffVR3_mm.addSystematic(btagTR)
    if fullSyst:
        meffVR3_mm.addSystematic(metcoTR)
        meffVR3_mm.addSystematic(metpuTR)
        meffVR3_mm.addSystematic(trigTR)
        meffVR3_mm.addSystematic(lesTR)
        meffVR3_mm.addSystematic(lermsTR)
        meffVR3_mm.addSystematic(leridTR)

    nJetVR3_ee=bkgOnly.addChannel("nJet",["VR3ee"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetVR3_ee.hasB = True
    nJetVR3_ee.hasBQCD = True
    nJetVR3_ee.useOverflowBin = True
    nJetVR3_ee.addSystematic(jesLow)
    nJetVR3_ee.addSystematic(jesMedium)
    nJetVR3_ee.addSystematic(jesHigh)
    nJetVR3_ee.addSystematic(lepTR)
    nJetVR3_ee.addSystematic(btagTR)
    if fullSyst:
        nJetVR3_ee.addSystematic(metcoTR)
        nJetVR3_ee.addSystematic(metpuTR)
        nJetVR3_ee.addSystematic(trigTR)
        nJetVR3_ee.addSystematic(lesTR)
        nJetVR3_ee.addSystematic(lermsTR)
        nJetVR3_ee.addSystematic(leridTR)

    nJetVR3_em=bkgOnly.addChannel("nJet",["VR3em"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetVR3_em.hasB = True
    nJetVR3_em.hasBQCD = True
    nJetVR3_em.useOverflowBin = True
    nJetVR3_em.addSystematic(jesLow)
    nJetVR3_em.addSystematic(jesMedium)
    nJetVR3_em.addSystematic(jesHigh)
    nJetVR3_em.addSystematic(lepTR)
    nJetVR3_em.addSystematic(btagTR)
    if fullSyst:
        nJetVR3_em.addSystematic(metcoTR)
        nJetVR3_em.addSystematic(metpuTR)
        nJetVR3_em.addSystematic(trigTR)
        nJetVR3_em.addSystematic(lesTR)
        nJetVR3_em.addSystematic(lermsTR)
        nJetVR3_em.addSystematic(leridTR)

    nJetVR3_mm=bkgOnly.addChannel("nJet",["VR3mm"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetVR3_mm.hasB = True
    nJetVR3_mm.hasBQCD = True
    nJetVR3_mm.useOverflowBin = True
    nJetVR3_mm.addSystematic(jesLow)
    nJetVR3_mm.addSystematic(jesMedium)
    nJetVR3_mm.addSystematic(jesHigh)
    nJetVR3_mm.addSystematic(lepTR)
    nJetVR3_mm.addSystematic(btagTR)
    if fullSyst:
        nJetVR3_mm.addSystematic(metcoTR)
        nJetVR3_mm.addSystematic(metpuTR)
        nJetVR3_mm.addSystematic(trigTR)
        nJetVR3_mm.addSystematic(lesTR)
        nJetVR3_mm.addSystematic(lermsTR)
        nJetVR3_mm.addSystematic(leridTR)


if doValidationDilepZ:


    ## check impact of kfactor fit on several distributions

    meffZVR_ee=bkgOnly.addChannel("meffInc",["ZVRee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffZVR_ee.hasB = True
    meffZVR_ee.hasBQCD = True
    meffZVR_ee.useOverflowBin = True
    meffZVR_ee.addSystematic(jesLow)
    meffZVR_ee.addSystematic(jesMedium)
    meffZVR_ee.addSystematic(jesHigh)
    meffZVR_ee.addSystematic(lepTR)
    meffZVR_ee.addSystematic(btagTR)
    if fullSyst:
        meffZVR_ee.addSystematic(metcoTR)
        meffZVR_ee.addSystematic(metpuTR)
        meffZVR_ee.addSystematic(trigTR)
        meffZVR_ee.addSystematic(lesTR)
        meffZVR_ee.addSystematic(lermsTR)
        meffZVR_ee.addSystematic(leridTR)

    meffZVR_em=bkgOnly.addChannel("meffInc",["ZVRem"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffZVR_em.hasB = True
    meffZVR_em.hasBQCD = True
    meffZVR_em.useOverflowBin = True
    meffZVR_em.addSystematic(jesLow)
    meffZVR_em.addSystematic(jesMedium)
    meffZVR_em.addSystematic(jesHigh)
    meffZVR_em.addSystematic(lepTR)
    meffZVR_em.addSystematic(btagTR)
    if fullSyst:
        meffZVR_em.addSystematic(metcoTR)
        meffZVR_em.addSystematic(metpuTR)
        meffZVR_em.addSystematic(trigTR)
        meffZVR_em.addSystematic(lesTR)
        meffZVR_em.addSystematic(lermsTR)
        meffZVR_em.addSystematic(leridTR)

    meffZVR_mm=bkgOnly.addChannel("meffInc",["ZVRmm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffZVR_mm.hasB = True
    meffZVR_mm.hasBQCD = True
    meffZVR_mm.useOverflowBin = True
    meffZVR_mm.addSystematic(jesLow)
    meffZVR_mm.addSystematic(jesMedium)
    meffZVR_mm.addSystematic(jesHigh)
    meffZVR_mm.addSystematic(lepTR)
    meffZVR_mm.addSystematic(btagTR)
    if fullSyst:
        meffZVR_mm.addSystematic(metcoTR)
        meffZVR_mm.addSystematic(metpuTR)
        meffZVR_mm.addSystematic(trigTR)
        meffZVR_mm.addSystematic(lesTR)
        meffZVR_mm.addSystematic(lermsTR)
        meffZVR_mm.addSystematic(leridTR)

    nJetZVR_ee=bkgOnly.addChannel("nJet",["ZVRee"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetZVR_ee.hasB = True
    nJetZVR_ee.hasBQCD = True
    nJetZVR_ee.useOverflowBin = True
    nJetZVR_ee.addSystematic(jesLow)
    nJetZVR_ee.addSystematic(jesMedium)
    nJetZVR_ee.addSystematic(jesHigh)
    nJetZVR_ee.addSystematic(lepTR)
    nJetZVR_ee.addSystematic(btagTR)
    if fullSyst:
        nJetZVR_ee.addSystematic(metcoTR)
        nJetZVR_ee.addSystematic(metpuTR)
        nJetZVR_ee.addSystematic(trigTR)
        nJetZVR_ee.addSystematic(lesTR)
        nJetZVR_ee.addSystematic(lermsTR)
        nJetZVR_ee.addSystematic(leridTR)

    nJetZVR_em=bkgOnly.addChannel("nJet",["ZVRem"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetZVR_em.hasB = True
    nJetZVR_em.hasBQCD = True
    nJetZVR_em.useOverflowBin = True
    nJetZVR_em.addSystematic(jesLow)
    nJetZVR_em.addSystematic(jesMedium)
    nJetZVR_em.addSystematic(jesHigh)
    nJetZVR_em.addSystematic(lepTR)
    nJetZVR_em.addSystematic(btagTR)
    if fullSyst:
        nJetZVR_em.addSystematic(metcoTR)
        nJetZVR_em.addSystematic(metpuTR)
        nJetZVR_em.addSystematic(trigTR)
        nJetZVR_em.addSystematic(lesTR)
        nJetZVR_em.addSystematic(lermsTR)
        nJetZVR_em.addSystematic(leridTR)

    nJetZVR_mm=bkgOnly.addChannel("nJet",["ZVRmm"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetZVR_mm.hasB = True
    nJetZVR_mm.hasBQCD = True
    nJetZVR_mm.useOverflowBin = True
    nJetZVR_mm.addSystematic(jesLow)
    nJetZVR_mm.addSystematic(jesMedium)
    nJetZVR_mm.addSystematic(jesHigh)
    nJetZVR_mm.addSystematic(lepTR)
    nJetZVR_mm.addSystematic(btagTR)
    if fullSyst:
        nJetZVR_mm.addSystematic(metcoTR)
        nJetZVR_mm.addSystematic(metpuTR)
        nJetZVR_mm.addSystematic(trigTR)
        nJetZVR_mm.addSystematic(lesTR)
        nJetZVR_mm.addSystematic(lermsTR)
        nJetZVR_mm.addSystematic(leridTR)

    meffZVR2_ee=bkgOnly.addChannel("meffInc",["ZVR2ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffZVR2_ee.hasB = True
    meffZVR2_ee.hasBQCD = True
    meffZVR2_ee.useOverflowBin = True
    meffZVR2_ee.addSystematic(jesLow)
    meffZVR2_ee.addSystematic(jesMedium)
    meffZVR2_ee.addSystematic(jesHigh)
    meffZVR2_ee.addSystematic(lepTR)
    meffZVR2_ee.addSystematic(btagTR)
    if fullSyst:
        meffZVR2_ee.addSystematic(metcoTR)
        meffZVR2_ee.addSystematic(metpuTR)
        meffZVR2_ee.addSystematic(trigTR)
        meffZVR2_ee.addSystematic(lesTR)
        meffZVR2_ee.addSystematic(lermsTR)
        meffZVR2_ee.addSystematic(leridTR)

    meffZVR2_em=bkgOnly.addChannel("meffInc",["ZVR2em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffZVR2_em.hasB = True
    meffZVR2_em.hasBQCD = True
    meffZVR2_em.useOverflowBin = True
    meffZVR2_em.addSystematic(jesLow)
    meffZVR2_em.addSystematic(jesMedium)
    meffZVR2_em.addSystematic(jesHigh)
    meffZVR2_em.addSystematic(lepTR)
    meffZVR2_em.addSystematic(btagTR)
    if fullSyst:
        meffZVR2_em.addSystematic(metcoTR)
        meffZVR2_em.addSystematic(metpuTR)
        meffZVR2_em.addSystematic(trigTR)
        meffZVR2_em.addSystematic(lesTR)
        meffZVR2_em.addSystematic(lermsTR)
        meffZVR2_em.addSystematic(leridTR)

    meffZVR2_mm=bkgOnly.addChannel("meffInc",["ZVR2mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffZVR2_mm.hasB = True
    meffZVR2_mm.hasBQCD = True
    meffZVR2_mm.useOverflowBin = True
    meffZVR2_mm.addSystematic(jesLow)
    meffZVR2_mm.addSystematic(jesMedium)
    meffZVR2_mm.addSystematic(jesHigh)
    meffZVR2_mm.addSystematic(lepTR)
    meffZVR2_mm.addSystematic(btagTR)
    if fullSyst:
        meffZVR2_mm.addSystematic(metcoTR)
        meffZVR2_mm.addSystematic(metpuTR)
        meffZVR2_mm.addSystematic(trigTR)
        meffZVR2_mm.addSystematic(lesTR)
        meffZVR2_mm.addSystematic(lermsTR)
        meffZVR2_mm.addSystematic(leridTR)

    nJetZVR2_ee=bkgOnly.addChannel("nJet",["ZVR2ee"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetZVR2_ee.hasB = True
    nJetZVR2_ee.hasBQCD = True
    nJetZVR2_ee.useOverflowBin = True
    nJetZVR2_ee.addSystematic(jesLow)
    nJetZVR2_ee.addSystematic(jesMedium)
    nJetZVR2_ee.addSystematic(jesHigh)
    nJetZVR2_ee.addSystematic(lepTR)
    nJetZVR2_ee.addSystematic(btagTR)
    if fullSyst:
        nJetZVR2_ee.addSystematic(metcoTR)
        nJetZVR2_ee.addSystematic(metpuTR)
        nJetZVR2_ee.addSystematic(trigTR)
        nJetZVR2_ee.addSystematic(lesTR)
        nJetZVR2_ee.addSystematic(lermsTR)
        nJetZVR2_ee.addSystematic(leridTR)

    nJetZVR2_em=bkgOnly.addChannel("nJet",["ZVR2em"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetZVR2_em.hasB = True
    nJetZVR2_em.hasBQCD = True
    nJetZVR2_em.useOverflowBin = True
    nJetZVR2_em.addSystematic(jesLow)
    nJetZVR2_em.addSystematic(jesMedium)
    nJetZVR2_em.addSystematic(jesHigh)
    nJetZVR2_em.addSystematic(lepTR)
    nJetZVR2_em.addSystematic(btagTR)
    if fullSyst:
        nJetZVR2_em.addSystematic(metcoTR)
        nJetZVR2_em.addSystematic(metpuTR)
        nJetZVR2_em.addSystematic(trigTR)
        nJetZVR2_em.addSystematic(lesTR)
        nJetZVR2_em.addSystematic(lermsTR)
        nJetZVR2_em.addSystematic(leridTR)

    nJetZVR2_mm=bkgOnly.addChannel("nJet",["ZVR2mm"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetZVR2_mm.hasB = True
    nJetZVR2_mm.hasBQCD = True
    nJetZVR2_mm.useOverflowBin = True
    nJetZVR2_mm.addSystematic(jesLow)
    nJetZVR2_mm.addSystematic(jesMedium)
    nJetZVR2_mm.addSystematic(jesHigh)
    nJetZVR2_mm.addSystematic(lepTR)
    nJetZVR2_mm.addSystematic(btagTR)
    if fullSyst:
        nJetZVR2_mm.addSystematic(metcoTR)
        nJetZVR2_mm.addSystematic(metpuTR)
        nJetZVR2_mm.addSystematic(trigTR)
        nJetZVR2_mm.addSystematic(lesTR)
        nJetZVR2_mm.addSystematic(lermsTR)
        nJetZVR2_mm.addSystematic(leridTR)

    meffZVR3_ee=bkgOnly.addChannel("meffInc",["ZVR3ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffZVR3_ee.hasB = True
    meffZVR3_ee.hasBQCD = True
    meffZVR3_ee.useOverflowBin = True
    meffZVR3_ee.addSystematic(jesLow)
    meffZVR3_ee.addSystematic(jesMedium)
    meffZVR3_ee.addSystematic(jesHigh)
    meffZVR3_ee.addSystematic(lepTR)
    meffZVR3_ee.addSystematic(btagTR)
    if fullSyst:
        meffZVR3_ee.addSystematic(metcoTR)
        meffZVR3_ee.addSystematic(metpuTR)
        meffZVR3_ee.addSystematic(trigTR)
        meffZVR3_ee.addSystematic(lesTR)
        meffZVR3_ee.addSystematic(lermsTR)
        meffZVR3_ee.addSystematic(leridTR)

    meffZVR3_em=bkgOnly.addChannel("meffInc",["ZVR3em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffZVR3_em.hasB = True
    meffZVR3_em.hasBQCD = True
    meffZVR3_em.useOverflowBin = True
    meffZVR3_em.addSystematic(jesLow)
    meffZVR3_em.addSystematic(jesMedium)
    meffZVR3_em.addSystematic(jesHigh)
    meffZVR3_em.addSystematic(lepTR)
    meffZVR3_em.addSystematic(btagTR)
    if fullSyst:
        meffZVR3_em.addSystematic(metcoTR)
        meffZVR3_em.addSystematic(metpuTR)
        meffZVR3_em.addSystematic(trigTR)
        meffZVR3_em.addSystematic(lesTR)
        meffZVR3_em.addSystematic(lermsTR)
        meffZVR3_em.addSystematic(leridTR)

    meffZVR3_mm=bkgOnly.addChannel("meffInc",["ZVR3mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffZVR3_mm.hasB = True
    meffZVR3_mm.hasBQCD = True
    meffZVR3_mm.useOverflowBin = True
    meffZVR3_mm.addSystematic(jesLow)
    meffZVR3_mm.addSystematic(jesMedium)
    meffZVR3_mm.addSystematic(jesHigh)
    meffZVR3_mm.addSystematic(lepTR)
    meffZVR3_mm.addSystematic(btagTR)
    if fullSyst:
        meffZVR3_mm.addSystematic(metcoTR)
        meffZVR3_mm.addSystematic(metpuTR)
        meffZVR3_mm.addSystematic(trigTR)
        meffZVR3_mm.addSystematic(lesTR)
        meffZVR3_mm.addSystematic(lermsTR)
        meffZVR3_mm.addSystematic(leridTR)

    nJetZVR3_ee=bkgOnly.addChannel("nJet",["ZVR3ee"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetZVR3_ee.hasB = True
    nJetZVR3_ee.hasBQCD = True
    nJetZVR3_ee.useOverflowBin = True
    nJetZVR3_ee.addSystematic(jesLow)
    nJetZVR3_ee.addSystematic(jesMedium)
    nJetZVR3_ee.addSystematic(jesHigh)
    nJetZVR3_ee.addSystematic(lepTR)
    nJetZVR3_ee.addSystematic(btagTR)
    if fullSyst:
        nJetZVR3_ee.addSystematic(metcoTR)
        nJetZVR3_ee.addSystematic(metpuTR)
        nJetZVR3_ee.addSystematic(trigTR)
        nJetZVR3_ee.addSystematic(lesTR)
        nJetZVR3_ee.addSystematic(lermsTR)
        nJetZVR3_ee.addSystematic(leridTR)

    nJetZVR3_em=bkgOnly.addChannel("nJet",["ZVR3em"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetZVR3_em.hasB = True
    nJetZVR3_em.hasBQCD = True
    nJetZVR3_em.useOverflowBin = True
    nJetZVR3_em.addSystematic(jesLow)
    nJetZVR3_em.addSystematic(jesMedium)
    nJetZVR3_em.addSystematic(jesHigh)
    nJetZVR3_em.addSystematic(lepTR)
    nJetZVR3_em.addSystematic(btagTR)
    if fullSyst:
        nJetZVR3_em.addSystematic(metcoTR)
        nJetZVR3_em.addSystematic(metpuTR)
        nJetZVR3_em.addSystematic(trigTR)
        nJetZVR3_em.addSystematic(lesTR)
        nJetZVR3_em.addSystematic(lermsTR)
        nJetZVR3_em.addSystematic(leridTR)

    nJetZVR3_mm=bkgOnly.addChannel("nJet",["ZVR3mm"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetZVR3_mm.hasB = True
    nJetZVR3_mm.hasBQCD = True
    nJetZVR3_mm.useOverflowBin = True
    nJetZVR3_mm.addSystematic(jesLow)
    nJetZVR3_mm.addSystematic(jesMedium)
    nJetZVR3_mm.addSystematic(jesHigh)
    nJetZVR3_mm.addSystematic(lepTR)
    nJetZVR3_mm.addSystematic(btagTR)
    if fullSyst:
        nJetZVR3_mm.addSystematic(metcoTR)
        nJetZVR3_mm.addSystematic(metpuTR)
        nJetZVR3_mm.addSystematic(trigTR)
        nJetZVR3_mm.addSystematic(lesTR)
        nJetZVR3_mm.addSystematic(lermsTR)
        nJetZVR3_mm.addSystematic(leridTR)


        

if doValidationSR:
    bkgOnly.setValidationChannels([meff2ee,meff4ee,meff2em,meff4em,meff2mm,meff4mm,meffS3_El,meffS3_Mu,meffS4_El,meffS4_Mu,meffS3T_El,meffS3T_Mu,meffS4T_El,meffS4T_Mu])

if doValidationSlope:
    bkgOnly.setValidationChannels([meffTR_El,meffTR_Mu,metTR_El,metTR_Mu,pt1TR_El,pt1TR_Mu,pt2TR_El,pt2TR_Mu,wptWR_El,wptWR_Mu,metWR_El,metWR_Mu,ZptZR_ee,ZptZR_mm])

if doValidationDilep:
    bkgOnly.setValidationChannels([meffVR_ee,meffVR_em,meffVR_mm,nJetVR_ee,nJetVR_em,nJetVR_mm,meffVR2_ee,meffVR2_em,meffVR2_mm,nJetVR2_ee,nJetVR2_em,nJetVR2_mm,meffVR3_ee,meffVR3_em,meffVR3_mm,nJetVR3_ee,nJetVR3_em,nJetVR3_mm])

if doValidationDilepZ:
    bkgOnly.setValidationChannels([meffZVR_ee,meffZVR_em,meffZVR_mm,nJetZVR_ee,nJetZVR_em,nJetZVR_mm,meffZVR2_ee,meffZVR2_em,meffZVR2_mm,nJetZVR2_ee,nJetZVR2_em,nJetZVR2_mm,meffZVR3_ee,meffZVR3_em,meffZVR3_mm,nJetZVR3_ee,nJetZVR3_em,nJetZVR3_mm])

#-------------------------------------------------
# Exclusion fit
#-------------------------------------------------


if doExclusion_GMSB_combined or doExclusion_mSUGRA_dilepton_combined or doExclusion_GG_twostepCC_slepton:
       
    for sig in sigSamples:
        myTopLvl = bkgOnly
        myTopLvl.name="dilepton_%s"%sig
        myTopLvl.prefix=configMgr.analysisName+"_"+"dilepton_%s"%sig
        
##        myTopLvl = configMgr.addTopLevelXMLClone(bkgOnly,"dilepton_%s"%sig)
        sigSample = Sample(sig,kPink)
        sigSample.setFileList(sigFiles)
        sigSample.setNormByTheory()
        sigSample.setNormFactor("mu_SIG",0.,0.,5.)
        sigSample.setStatConfig(useStat)

        if useXsecUnc:
            sigSample.addSystematic(xsecSig)
        myTopLvl.addSamples(sigSample)
        myTopLvl.setSignalSample(sigSample)

        SigList=[sig]

        S2Channel_ee = myTopLvl.addChannel("meffInc",["S2ee"],meffNBinsS2,meffBinLowS2,meffBinHighS2)
        S2Channel_ee.useOverflowBin=True
        
        S2Channel_ee.getSample(sig).addSystematic(jesSignal)

        [S2Channel_ee.getSample(sam).addSystematic(zpT50GeV) for sam in BGList]
        [S2Channel_ee.getSample(sam).addSystematic(zpT100GeV) for sam in BGList]
        [S2Channel_ee.getSample(sam).addSystematic(zpT150GeV) for sam in BGList]
        [S2Channel_ee.getSample(sam).addSystematic(zpT200GeV) for sam in BGList]
       
        S2Channel_ee.addSystematic(lepS2DL)
        if fullSyst:
            S2Channel_ee.addSystematic(metcoS2DL)
            S2Channel_ee.addSystematic(metpuS2DL)
            S2Channel_ee.addSystematic(trigS2DL)
            [S2Channel_ee.getSample(sam).addSystematic(lesS2DL) for sam in SigList+BGList]
            [S2Channel_ee.getSample(sam).addSystematic(lermsS2DL) for sam in SigList+BGList]
            [S2Channel_ee.getSample(sam).addSystematic(leridS2DL) for sam in SigList+BGList]
            [S2Channel_ee.getSample(sam).addSystematic(jesLow) for sam in BGList]
            [S2Channel_ee.getSample(sam).addSystematic(jesMedium) for sam in BGList]
            [S2Channel_ee.getSample(sam).addSystematic(jesHigh) for sam in BGList]
            
        S2Channel_em = myTopLvl.addChannel("meffInc",["S2em"],meffNBinsS2,meffBinLowS2,meffBinHighS2)
        S2Channel_em.useOverflowBin=True

        S2Channel_em.getSample(sig).addSystematic(jesSignal)
        [S2Channel_em.getSample(sam).addSystematic(zpT50GeV) for sam in BGList]
        [S2Channel_em.getSample(sam).addSystematic(zpT100GeV) for sam in BGList]
        [S2Channel_em.getSample(sam).addSystematic(zpT150GeV) for sam in BGList]
        [S2Channel_em.getSample(sam).addSystematic(zpT200GeV) for sam in BGList]      
       
        S2Channel_em.addSystematic(lepS2DL)
        if fullSyst:
            S2Channel_em.addSystematic(metcoS2DL)
            S2Channel_em.addSystematic(metpuS2DL)
            S2Channel_em.addSystematic(trigS2DL)
            [S2Channel_em.getSample(sam).addSystematic(lesS2DL) for sam in SigList+BGList]
            [S2Channel_em.getSample(sam).addSystematic(lermsS2DL) for sam in SigList+BGList]
            [S2Channel_em.getSample(sam).addSystematic(leridS2DL) for sam in SigList+BGList]
            [S2Channel_em.getSample(sam).addSystematic(jesLow) for sam in BGList]
            [S2Channel_em.getSample(sam).addSystematic(jesMedium) for sam in BGList]
            [S2Channel_em.getSample(sam).addSystematic(jesHigh) for sam in BGList]

        S2Channel_mm = myTopLvl.addChannel("meffInc",["S2mm"],meffNBinsS2,meffBinLowS2,meffBinHighS2)
        S2Channel_mm.useOverflowBin=True

        S2Channel_mm.getSample(sig).addSystematic(jesSignal)
        [S2Channel_mm.getSample(sam).addSystematic(zpT50GeV) for sam in BGList]
        [S2Channel_mm.getSample(sam).addSystematic(zpT100GeV) for sam in BGList]
        [S2Channel_mm.getSample(sam).addSystematic(zpT150GeV) for sam in BGList]
        [S2Channel_mm.getSample(sam).addSystematic(zpT200GeV) for sam in BGList]
    
       
        S2Channel_mm.addSystematic(lepS4DL)
        if fullSyst:
            S2Channel_mm.addSystematic(metcoS2DL)
            S2Channel_mm.addSystematic(metpuS2DL)
            S2Channel_mm.addSystematic(trigS2DL)
            [S2Channel_mm.getSample(sam).addSystematic(lesS2DL) for sam in SigList+BGList]
            [S2Channel_mm.getSample(sam).addSystematic(lermsS2DL) for sam in SigList+BGList]
            [S2Channel_mm.getSample(sam).addSystematic(leridS2DL) for sam in SigList+BGList]
            [S2Channel_mm.getSample(sam).addSystematic(jesLow) for sam in BGList]
            [S2Channel_mm.getSample(sam).addSystematic(jesMedium) for sam in BGList]
            [S2Channel_mm.getSample(sam).addSystematic(jesHigh) for sam in BGList]

    
        S4Channel_ee = myTopLvl.addChannel("meffInc",["S4ee"],meffNBinsS4,meffBinLowS4,meffBinHighS4)
        S4Channel_ee.useOverflowBin=True
        
        S4Channel_ee.getSample(sig).addSystematic(jesSignal)
       
        [S4Channel_ee.getSample(sam).addSystematic(zpT50GeV) for sam in BGList]
        [S4Channel_ee.getSample(sam).addSystematic(zpT100GeV) for sam in BGList]
        [S4Channel_ee.getSample(sam).addSystematic(zpT150GeV) for sam in BGList]
        [S4Channel_ee.getSample(sam).addSystematic(zpT200GeV) for sam in BGList]

        S4Channel_ee.addSystematic(lepS4DL)
        if fullSyst:
            S4Channel_ee.addSystematic(metcoS4DL)
            S4Channel_ee.addSystematic(metpuS4DL)
            S4Channel_ee.addSystematic(trigS4DL)
            [S4Channel_ee.getSample(sam).addSystematic(lesS4DL) for sam in SigList+BGList]
            [S4Channel_ee.getSample(sam).addSystematic(lermsS4DL) for sam in SigList+BGList]
            [S4Channel_ee.getSample(sam).addSystematic(leridS4DL) for sam in SigList+BGList]
            [S4Channel_ee.getSample(sam).addSystematic(jesLow) for sam in BGList]
            [S4Channel_ee.getSample(sam).addSystematic(jesMedium) for sam in BGList]
            [S4Channel_ee.getSample(sam).addSystematic(jesHigh) for sam in BGList]
    
        S4Channel_em = myTopLvl.addChannel("meffInc",["S4em"],meffNBinsS4,meffBinLowS4,meffBinHighS4)
        S4Channel_em.useOverflowBin=True

        S4Channel_em.getSample(sig).addSystematic(jesSignal)

        [S4Channel_em.getSample(sam).addSystematic(zpT50GeV) for sam in BGList]
        [S4Channel_em.getSample(sam).addSystematic(zpT100GeV) for sam in BGList]
        [S4Channel_em.getSample(sam).addSystematic(zpT150GeV) for sam in BGList]
        [S4Channel_em.getSample(sam).addSystematic(zpT200GeV) for sam in BGList]
        
        S4Channel_em.addSystematic(lepS4DL)
        if fullSyst:
            S4Channel_em.addSystematic(metcoS4DL)
            S4Channel_em.addSystematic(metpuS4DL)
            S4Channel_em.addSystematic(trigS4DL)
            [S4Channel_em.getSample(sam).addSystematic(lesS4DL) for sam in SigList+BGList]
            [S4Channel_em.getSample(sam).addSystematic(lermsS4DL) for sam in SigList+BGList]
            [S4Channel_em.getSample(sam).addSystematic(leridS4DL) for sam in SigList+BGList]
            [S4Channel_em.getSample(sam).addSystematic(jesLow) for sam in BGList]
            [S4Channel_em.getSample(sam).addSystematic(jesMedium) for sam in BGList]
            [S4Channel_em.getSample(sam).addSystematic(jesHigh) for sam in BGList]

        S4Channel_mm = myTopLvl.addChannel("meffInc",["S4mm"],meffNBinsS4,meffBinLowS4,meffBinHighS4)
        S4Channel_mm.useOverflowBin=True

        S4Channel_mm.getSample(sig).addSystematic(jesSignal)

        [S4Channel_mm.getSample(sam).addSystematic(zpT50GeV) for sam in BGList]
        [S4Channel_mm.getSample(sam).addSystematic(zpT100GeV) for sam in BGList]
        [S4Channel_mm.getSample(sam).addSystematic(zpT150GeV) for sam in BGList]
        [S4Channel_mm.getSample(sam).addSystematic(zpT200GeV) for sam in BGList]
        
        S4Channel_mm.addSystematic(lepS4DL)
        if fullSyst:
            S4Channel_mm.addSystematic(metcoS4DL)
            S4Channel_mm.addSystematic(metpuS4DL)
            S4Channel_mm.addSystematic(trigS4DL)
            [S4Channel_mm.getSample(sam).addSystematic(lesS4DL) for sam in SigList+BGList]
            [S4Channel_mm.getSample(sam).addSystematic(lermsS4DL) for sam in SigList+BGList]
            [S4Channel_mm.getSample(sam).addSystematic(leridS4DL) for sam in SigList+BGList]
            [S4Channel_mm.getSample(sam).addSystematic(jesLow) for sam in BGList]
            [S4Channel_mm.getSample(sam).addSystematic(jesMedium) for sam in BGList]
            [S4Channel_mm.getSample(sam).addSystematic(jesHigh) for sam in BGList]


        ## Which SRs for which Scenario?

        if doExclusion_GMSB_combined:
            myTopLvl.setSignalChannels([S2Channel_ee,S2Channel_em,S2Channel_mm])       
        elif doExclusion_mSUGRA_dilepton_combined:
            myTopLvl.setSignalChannels([S2Channel_ee,S2Channel_em,S2Channel_mm,S4Channel_ee,S4Channel_em,S4Channel_mm])
        ## Which SRs for SM???
        elif doExclusion_GG_twostepCC_slepton:
            myTopLvl.setSignalChannels([S4Channel_ee,S4Channel_em,S4Channel_mm])


#  LocalWords:  jesSignal
