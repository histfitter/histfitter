
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

doHardLep=True
doSoftLep=False
useStat=True
doValidation=False
doValidationSR=False
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
doExclusion_GG_twostepCC_slepton=False
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

# Set the files to read from
if configMgr.readFromTree:
    bgdFiles = ["data/SusyFitterTree_EleEle.root","data/SusyFitterTree_EleMu.root","data/SusyFitterTree_MuMu.root","data/SusyFitterTree_OneEle.root","data/SusyFitterTree_OneMu.root"]
    
if doExclusion_GMSB_combined:
    sigFiles+=["data/SusyFitterTree_EleEle_GMSB.root","data/SusyFitterTree_EleMu_GMSB.root","data/SusyFitterTree_MuMu_GMSB.root"]
if doExclusion_mSUGRA_dilepton_combined:
    sigFiles+=["data/SusyFitterTree_EleEle_mSUGRA.root","data/SusyFitterTree_EleMu_mSUGRA.root","data/SusyFitterTree_MuMu_mSUGRA.root"]
                                
# Need to comment out the following line when running HypoTest.py parallelized
sigSamples=[]
if doExclusion_GMSB_combined:
    sigSamples=["GMSB_3_2d_40_250_3_10_1_1"]
SigList=sigSamples

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

                      "ZReeY":"mll>80 && mll<100  && met < 50 && jet3Pt > 25 && AnalysisType==3 && meffInc > 400",
                      "ZRmmY":"mll>80 && mll<100  && met < 50 && jet3Pt > 25 && AnalysisType==4 && meffInc > 400",

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

                      "WRElVR":"lep2Pt<10 && met>40 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==1",
                      "WRMuVR":"lep2Pt<10 && met>40 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==2",

                      "S3El":"AnalysisType==1 && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25 && jet4Pt<80",
                      "S4El":"AnalysisType==1 && met>250 && mt>100 && met/meff4Jet>0.2 && jet4Pt>80",

                      "S3Mu":"AnalysisType==2 && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25 && jet4Pt<80",
                      "S4Mu":"AnalysisType==2 && met>250 && mt>100 && met/meff4Jet>0.2 && jet4Pt>80",

                      "SR3jTEl":"AnalysisType==1 && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25 && jet4Pt<80 && meffInc>1200",
                      "SR4jTEl":"AnalysisType==1 && met>250 && mt>100 && met/meff4Jet>0.2 && jet4Pt>80 && meffInc>800",

                      "SR3jTMu":"AnalysisType==2 && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25 && jet4Pt<80 && meffInc>1200",
                      "SR4jTMu":"AnalysisType==2 && met>250 && mt>100 && met/meff4Jet>0.2 && jet4Pt>80 && meffInc>800",

                      "SR7jTEl":"AnalysisType==1 && met>180 && mt>120 && jet1Pt>80 && jet7Pt>25 && meffInc>750",             
                      "SR7jTMu":"AnalysisType==2 && met>180 && mt>120 && jet1Pt>80 && jet7Pt>25 && meffInc>750"   
                      

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
#jesVR2 = Systematic("JV2","_NoSys","_JESup","_JESdown","tree","shapeSys")
#jesVR3 = Systematic("JV3","_NoSys","_JESup","_JESdown","tree","shapeSys")
#jesVR4 = Systematic("JV4","_NoSys","_JESup","_JESdown","tree","shapeSys")
#jesVZ2 = Systematic("JZ2","_NoSys","_JESup","_JESdown","tree","shapeSys")
#jesVZ3 = Systematic("JZ3","_NoSys","_JESup","_JESdown","tree","shapeSys")
#jesVZ4 = Systematic("JZ4","_NoSys","_JESup","_JESdown","tree","shapeSys")
#jesS2DL = Systematic("J2DL","_NoSys","_JESup","_JESdown","tree","normHistoSys")
#jesS4DL = Systematic("J4DL","_NoSys","_JESup","_JESdown","tree","normHistoSys")

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

err_WZ_Np0 = Systematic("err_WZ_Np0", configMgr.weights,1.2 ,0.8, "user","userOverallSys")
err_WZ_Np1 = Systematic("err_WZ_Np1", configMgr.weights,1.04 ,0.96, "user","userOverallSys")

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


#--------------------------------------------------------------
# Background fit regions 
#--------------------------------------------------------------

BGList=["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]

##### nJet for Top ####

# ele ele

nJetTopeeChannel=bkgOnly.addChannel("nJet",nJetTopeeRegions,nJetTopeeNBins,nJetTopeeBinLow,nJetTopeeBinHigh)
nJetTopeeChannel.hasB = True
nJetTopeeChannel.hasBQCD = True
nJetTopeeChannel.useOverflowBin = False
[nJetTopeeChannel.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
[nJetTopeeChannel.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
[nJetTopeeChannel.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
[nJetTopeeChannel.getSample(sam).addSystematic(btagTR) for sam in SigList+BGList+["QCD"]]
[nJetTopeeChannel.getSample(sam).addSystematic(lepTR) for sam in SigList+BGList+["QCD"]]
[nJetTopeeChannel.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
[nJetTopeeChannel.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
[nJetTopeeChannel.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
[nJetTopeeChannel.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
[nJetTopeeChannel.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]
if fullSyst:
    [nJetTopeeChannel.getSample(sam).addSystematic(metcoTR) for sam in SigList+BGList+["QCD"]]
    [nJetTopeeChannel.getSample(sam).addSystematic(metpuTR) for sam in SigList+BGList+["QCD"]]
    [nJetTopeeChannel.getSample(sam).addSystematic(trigTR) for sam in SigList+BGList+["QCD"]]
    [nJetTopeeChannel.getSample(sam).addSystematic(lesTR) for sam in SigList+BGList+["QCD"]]
    [nJetTopeeChannel.getSample(sam).addSystematic(lermsTR) for sam in SigList+BGList]
    [nJetTopeeChannel.getSample(sam).addSystematic(leridTR) for sam in SigList+BGList]


#  single ele

nJetTopeChannel=bkgOnly.addChannel("nJet",nJetTopeRegions,nJetTopeNBins,nJetTopeBinLow,nJetTopeBinHigh)
nJetTopeChannel.hasB = True
nJetTopeChannel.hasBQCD = True
nJetTopeChannel.useOverflowBin = False
[nJetTopeChannel.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
[nJetTopeChannel.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
[nJetTopeChannel.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
[nJetTopeChannel.getSample(sam).addSystematic(btagTR) for sam in SigList+BGList+["QCD"]]
[nJetTopeChannel.getSample(sam).addSystematic(lepTR) for sam in SigList+BGList+["QCD"]]
[nJetTopeChannel.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
[nJetTopeChannel.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
[nJetTopeChannel.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
[nJetTopeChannel.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
[nJetTopeChannel.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]
if fullSyst:
    [nJetTopeChannel.getSample(sam).addSystematic(metcoTR) for sam in SigList+BGList+["QCD"]]
    [nJetTopeChannel.getSample(sam).addSystematic(metpuTR) for sam in SigList+BGList+["QCD"]]
    [nJetTopeChannel.getSample(sam).addSystematic(trigTR) for sam in SigList+BGList+["QCD"]]
    [nJetTopeChannel.getSample(sam).addSystematic(lesTR) for sam in SigList+BGList]
    [nJetTopeChannel.getSample(sam).addSystematic(lermsTR) for sam in SigList+BGList]
    [nJetTopeChannel.getSample(sam).addSystematic(leridTR) for sam in SigList+BGList]    


#  ele mu

nJetTopemChannel=bkgOnly.addChannel("nJet",nJetTopemRegions,nJetTopemNBins,nJetTopemBinLow,nJetTopemBinHigh)
nJetTopemChannel.hasB = True
nJetTopemChannel.hasBQCD = True
nJetTopemChannel.useOverflowBin = False
[nJetTopemChannel.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
[nJetTopemChannel.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
[nJetTopemChannel.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
[nJetTopemChannel.getSample(sam).addSystematic(btagTR) for sam in SigList+BGList+["QCD"]]
[nJetTopemChannel.getSample(sam).addSystematic(lepTR) for sam in SigList+BGList+["QCD"]]
[nJetTopemChannel.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
[nJetTopemChannel.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
[nJetTopemChannel.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
[nJetTopemChannel.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
[nJetTopemChannel.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]
if fullSyst:
    [nJetTopemChannel.getSample(sam).addSystematic(metcoTR) for sam in SigList+BGList+["QCD"]]
    [nJetTopemChannel.getSample(sam).addSystematic(metpuTR) for sam in SigList+BGList+["QCD"]]
    [nJetTopemChannel.getSample(sam).addSystematic(trigTR) for sam in SigList+BGList+["QCD"]]
    [nJetTopemChannel.getSample(sam).addSystematic(lesTR) for sam in SigList+BGList]
    [nJetTopemChannel.getSample(sam).addSystematic(lermsTR) for sam in SigList+BGList]
    [nJetTopemChannel.getSample(sam).addSystematic(leridTR) for sam in SigList+BGList]


# mu mu

nJetTopmmChannel=bkgOnly.addChannel("nJet",nJetTopmmRegions,nJetTopmmNBins,nJetTopmmBinLow,nJetTopmmBinHigh)
nJetTopmmChannel.hasB = True
nJetTopmmChannel.hasBQCD = True
nJetTopmmChannel.useOverflowBin = False
[nJetTopmmChannel.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
[nJetTopmmChannel.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
[nJetTopmmChannel.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
[nJetTopmmChannel.getSample(sam).addSystematic(btagTR) for sam in SigList+BGList+["QCD"]]
[nJetTopmmChannel.getSample(sam).addSystematic(lepTR) for sam in SigList+BGList+["QCD"]]
[nJetTopmmChannel.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
[nJetTopmmChannel.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
[nJetTopmmChannel.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
[nJetTopmmChannel.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
[nJetTopmmChannel.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]
if fullSyst:
    [nJetTopmmChannel.getSample(sam).addSystematic(metcoTR) for sam in SigList+BGList+["QCD"]]
    [nJetTopmmChannel.getSample(sam).addSystematic(metpuTR) for sam in SigList+BGList+["QCD"]]
    [nJetTopmmChannel.getSample(sam).addSystematic(trigTR) for sam in SigList+BGList+["QCD"]]
    [nJetTopmmChannel.getSample(sam).addSystematic(lesTR) for sam in SigList+BGList]
    [nJetTopmmChannel.getSample(sam).addSystematic(lermsTR) for sam in SigList+BGList]
    [nJetTopmmChannel.getSample(sam).addSystematic(leridTR) for sam in SigList+BGList]


# single mu

nJetTopmChannel=bkgOnly.addChannel("nJet",nJetTopmRegions,nJetTopmNBins,nJetTopmBinLow,nJetTopmBinHigh)
nJetTopmChannel.hasB = True
nJetTopmChannel.hasBQCD = True
nJetTopmChannel.useOverflowBin = False
[nJetTopmChannel.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
[nJetTopmChannel.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
[nJetTopmChannel.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
[nJetTopmChannel.getSample(sam).addSystematic(btagTR) for sam in SigList+BGList+["QCD"]]
[nJetTopmChannel.getSample(sam).addSystematic(lepTR) for sam in SigList+BGList+["QCD"]]
[nJetTopmChannel.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
[nJetTopmChannel.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
[nJetTopmChannel.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
[nJetTopmChannel.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
[nJetTopmChannel.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]
if fullSyst:
    [nJetTopmChannel.getSample(sam).addSystematic(metcoTR) for sam in SigList+BGList+["QCD"]]
    [nJetTopmChannel.getSample(sam).addSystematic(metpuTR) for sam in SigList+BGList+["QCD"]]
    [nJetTopmChannel.getSample(sam).addSystematic(trigTR) for sam in SigList+BGList+["QCD"]]
    [nJetTopmChannel.getSample(sam).addSystematic(lesTR) for sam in SigList+BGList]
    [nJetTopmChannel.getSample(sam).addSystematic(lermsTR) for sam in SigList+BGList]
    [nJetTopmChannel.getSample(sam).addSystematic(leridTR) for sam in SigList+BGList]
    

####### nJet for W/Z  #######
    
# ele ele    

nJetZeeChannel=bkgOnly.addChannel("nJet",nJetZeeRegions,nJetZeeNBins,nJetZeeBinLow,nJetZeeBinHigh)
nJetZeeChannel.hasB = False
nJetZeeChannel.hasBQCD = False
[nJetZeeChannel.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
[nJetZeeChannel.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
[nJetZeeChannel.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
[nJetZeeChannel.getSample(sam).addSystematic(lepZR) for sam in SigList+BGList+["QCD"]]
[nJetZeeChannel.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
[nJetZeeChannel.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
[nJetZeeChannel.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
[nJetZeeChannel.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
[nJetZeeChannel.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]
if fullSyst:
    [nJetZeeChannel.getSample(sam).addSystematic(metcoZR) for sam in SigList+BGList+["QCD"]]
    [nJetZeeChannel.getSample(sam).addSystematic(metpuZR) for sam in SigList+BGList+["QCD"]]
    [nJetZeeChannel.getSample(sam).addSystematic(trigZR) for sam in SigList+BGList+["QCD"]]
    [nJetZeeChannel.getSample(sam).addSystematic(lesZR) for sam in SigList+BGList]
    [nJetZeeChannel.getSample(sam).addSystematic(lermsZR) for sam in SigList+BGList]
    [nJetZeeChannel.getSample(sam).addSystematic(leridZR) for sam in SigList+BGList]


# single ele

nJetZeChannel=bkgOnly.addChannel("nJet",nJetZeRegions,nJetZeNBins,nJetZeBinLow,nJetZeBinHigh)
nJetZeChannel.hasB = True
nJetZeChannel.hasBQCD = False
[nJetZeChannel.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
[nJetZeChannel.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
[nJetZeChannel.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
[nJetZeChannel.getSample(sam).addSystematic(btagZR) for sam in SigList+BGList+["QCD"]]
[nJetZeChannel.getSample(sam).addSystematic(lepZR) for sam in SigList+BGList+["QCD"]]
[nJetZeChannel.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
[nJetZeChannel.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
[nJetZeChannel.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
[nJetZeChannel.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
[nJetZeChannel.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]
if fullSyst:
    [nJetZeChannel.getSample(sam).addSystematic(metcoZR) for sam in SigList+BGList+["QCD"]]
    [nJetZeChannel.getSample(sam).addSystematic(metpuZR) for sam in SigList+BGList+["QCD"]]
    [nJetZeChannel.getSample(sam).addSystematic(trigZR) for sam in SigList+BGList+["QCD"]]
    [nJetZeChannel.getSample(sam).addSystematic(lesZR) for sam in SigList+BGList]
    [nJetZeChannel.getSample(sam).addSystematic(lermsZR) for sam in SigList+BGList]
    [nJetZeChannel.getSample(sam).addSystematic(leridZR) for sam in SigList+BGList]    

  
# mu mu

nJetZmmChannel=bkgOnly.addChannel("nJet",nJetZmmRegions,nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
nJetZmmChannel.hasB = False
nJetZmmChannel.hasBQCD = False
[nJetZmmChannel.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
[nJetZmmChannel.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
[nJetZmmChannel.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
[nJetZmmChannel.getSample(sam).addSystematic(lepZR) for sam in SigList+BGList+["QCD"]]
[nJetZmmChannel.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
[nJetZmmChannel.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
[nJetZmmChannel.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
[nJetZmmChannel.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
[nJetZmmChannel.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]
if fullSyst:
    [nJetZmmChannel.getSample(sam).addSystematic(metcoZR) for sam in SigList+BGList+["QCD"]]
    [nJetZmmChannel.getSample(sam).addSystematic(metpuZR) for sam in SigList+BGList+["QCD"]]
    [nJetZmmChannel.getSample(sam).addSystematic(trigZR) for sam in SigList+BGList+["QCD"]]
    [nJetZmmChannel.getSample(sam).addSystematic(lesZR) for sam in SigList+BGList]
    [nJetZmmChannel.getSample(sam).addSystematic(lermsZR) for sam in SigList+BGList]
    [nJetZmmChannel.getSample(sam).addSystematic(leridZR) for sam in SigList+BGList]


# single mu

nJetZmChannel=bkgOnly.addChannel("nJet",nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
nJetZmChannel.hasB = True
nJetZmChannel.hasBQCD = False
[nJetZmChannel.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
[nJetZmChannel.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
[nJetZmChannel.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
[nJetZmChannel.getSample(sam).addSystematic(btagZR) for sam in SigList+BGList+["QCD"]]
[nJetZmChannel.getSample(sam).addSystematic(lepZR) for sam in SigList+BGList+["QCD"]]
[nJetZmChannel.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
[nJetZmChannel.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
[nJetZmChannel.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
[nJetZmChannel.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
[nJetZmChannel.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]
if fullSyst:
    [nJetZmChannel.getSample(sam).addSystematic(metcoZR) for sam in SigList+BGList+["QCD"]]
    [nJetZmChannel.getSample(sam).addSystematic(metpuZR) for sam in SigList+BGList+["QCD"]]
    [nJetZmChannel.getSample(sam).addSystematic(trigZR) for sam in SigList+BGList+["QCD"]]
    [nJetZmChannel.getSample(sam).addSystematic(lesZR) for sam in SigList+BGList]
    [nJetZmChannel.getSample(sam).addSystematic(lermsZR) for sam in SigList+BGList]
    [nJetZmChannel.getSample(sam).addSystematic(leridZR) for sam in SigList+BGList]    
                                                                            

bkgOnly.setBkgConstrainChannels([nJetTopeeChannel,nJetZeeChannel,nJetTopeChannel,nJetZeChannel,nJetTopemChannel,nJetTopmmChannel,nJetZmmChannel,nJetTopmChannel,nJetZmChannel])




#-------------------------------------------------
# Signal regions - only do this if background only, add as validation regions! 
#-------------------------------------------------

meffNBins = 1
#    meffBinLow = 400.
meffBinLow = 0.
meffBinHigh = 1600.

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
    [meffTR_El.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffTR_El.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffTR_El.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffTR_El.getSample(sam).addSystematic(lepTR) for sam in SigList+BGList+["QCD"]]
    [meffTR_El.getSample(sam).addSystematic(btagTR) for sam in SigList+BGList+["QCD"]]
    [meffTR_El.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffTR_El.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffTR_El.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffTR_El.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffTR_El.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffTR_El.getSample(sam).addSystematic(metcoTR) for sam in SigList+BGList+["QCD"]]
        [meffTR_El.getSample(sam).addSystematic(metpuTR) for sam in SigList+BGList+["QCD"]]
        [meffTR_El.getSample(sam).addSystematic(trigTR) for sam in SigList+BGList+["QCD"]]
        [meffTR_El.getSample(sam).addSystematic(lesTR) for sam in SigList+BGList]
        [meffTR_El.getSample(sam).addSystematic(lermsTR) for sam in SigList+BGList]
        [meffTR_El.getSample(sam).addSystematic(leridTR) for sam in SigList+BGList]

    meffTR_Mu=bkgOnly.addChannel("meffInc",["TRMuVR"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffTR_Mu.hasB = True
    meffTR_Mu.hasBQCD = True
    meffTR_Mu.useOverflowBin = True
    [meffTR_Mu.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffTR_Mu.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffTR_Mu.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffTR_Mu.getSample(sam).addSystematic(lepTR) for sam in SigList+BGList+["QCD"]]
    [meffTR_Mu.getSample(sam).addSystematic(btagTR) for sam in SigList+BGList+["QCD"]]
    [meffTR_Mu.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffTR_Mu.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffTR_Mu.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffTR_Mu.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffTR_Mu.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]
    if fullSyst:
        [meffTR_Mu.getSample(sam).addSystematic(metcoTR) for sam in SigList+BGList+["QCD"]]
        [meffTR_Mu.getSample(sam).addSystematic(metpuTR) for sam in SigList+BGList+["QCD"]]
        [meffTR_Mu.getSample(sam).addSystematic(trigTR) for sam in SigList+BGList+["QCD"]]
        [meffTR_Mu.getSample(sam).addSystematic(lesTR) for sam in SigList+BGList]
        [meffTR_Mu.getSample(sam).addSystematic(lermsTR) for sam in SigList+BGList]
        [meffTR_Mu.getSample(sam).addSystematic(leridTR) for sam in SigList+BGList]

        

    metTR_El=bkgOnly.addChannel("met",["TRElVR2"],metNBinsTR,metBinLowTR,metBinHighTR)
    metTR_El.hasB = True
    metTR_El.hasBQCD = True
    metTR_El.useOverflowBin = True
    [metTR_El.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [metTR_El.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [metTR_El.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [metTR_El.getSample(sam).addSystematic(lepTR) for sam in SigList+BGList+["QCD"]]
    [metTR_El.getSample(sam).addSystematic(btagTR) for sam in SigList+BGList+["QCD"]]
    [metTR_El.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [metTR_El.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [metTR_El.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [metTR_El.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [metTR_El.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [metTR_El.getSample(sam).addSystematic(metcoTR) for sam in SigList+BGList+["QCD"]]
        [metTR_El.getSample(sam).addSystematic(metpuTR) for sam in SigList+BGList+["QCD"]]
        [metTR_El.getSample(sam).addSystematic(trigTR) for sam in SigList+BGList+["QCD"]]
        [metTR_El.getSample(sam).addSystematic(lesTR) for sam in SigList+BGList]
        [metTR_El.getSample(sam).addSystematic(lermsTR) for sam in SigList+BGList]
        [metTR_El.getSample(sam).addSystematic(leridTR) for sam in SigList+BGList]


    metTR_Mu=bkgOnly.addChannel("met",["TRMuVR2"],metNBinsTR,metBinLowTR,metBinHighTR)
    metTR_Mu.hasB = True
    metTR_Mu.hasBQCD = True
    metTR_Mu.useOverflowBin = True
    [metTR_Mu.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [metTR_Mu.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [metTR_Mu.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [metTR_Mu.getSample(sam).addSystematic(lepTR) for sam in SigList+BGList+["QCD"]]
    [metTR_Mu.getSample(sam).addSystematic(btagTR) for sam in SigList+BGList+["QCD"]]
    [metTR_Mu.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [metTR_Mu.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [metTR_Mu.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [metTR_Mu.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [metTR_Mu.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [metTR_Mu.getSample(sam).addSystematic(metcoTR) for sam in SigList+BGList+["QCD"]]
        [metTR_Mu.getSample(sam).addSystematic(metpuTR) for sam in SigList+BGList+["QCD"]]
        [metTR_Mu.getSample(sam).addSystematic(trigTR) for sam in SigList+BGList+["QCD"]]
        [metTR_Mu.getSample(sam).addSystematic(lesTR) for sam in SigList+BGList]
        [metTR_Mu.getSample(sam).addSystematic(lermsTR) for sam in SigList+BGList]
        [metTR_Mu.getSample(sam).addSystematic(leridTR) for sam in SigList+BGList]


    pt1TR_El=bkgOnly.addChannel("jet1Pt",["TRElVR"],pt1NBinsTR,pt1BinLowTR,pt1BinHighTR)
    pt1TR_El.hasB = True
    pt1TR_El.hasBQCD = True
    pt1TR_El.useOverflowBin = True
    [pt1TR_El.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [pt1TR_El.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [pt1TR_El.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [pt1TR_El.getSample(sam).addSystematic(lepTR) for sam in SigList+BGList+["QCD"]]
    [pt1TR_El.getSample(sam).addSystematic(btagTR) for sam in SigList+BGList+["QCD"]]
    [pt1TR_El.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [pt1TR_El.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [pt1TR_El.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [pt1TR_El.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [pt1TR_El.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [pt1TR_El.getSample(sam).addSystematic(metcoTR) for sam in SigList+BGList+["QCD"]]
        [pt1TR_El.getSample(sam).addSystematic(metpuTR) for sam in SigList+BGList+["QCD"]]
        [pt1TR_El.getSample(sam).addSystematic(trigTR) for sam in SigList+BGList+["QCD"]]
        [pt1TR_El.getSample(sam).addSystematic(lesTR) for sam in SigList+BGList]
        [pt1TR_El.getSample(sam).addSystematic(lermsTR) for sam in SigList+BGList]
        [pt1TR_El.getSample(sam).addSystematic(leridTR) for sam in SigList+BGList]


    pt1TR_Mu=bkgOnly.addChannel("jet1Pt",["TRMuVR"],pt1NBinsTR,pt1BinLowTR,pt1BinHighTR)
    pt1TR_Mu.hasB = True
    pt1TR_Mu.hasBQCD = True
    pt1TR_Mu.useOverflowBin = True
    [pt1TR_Mu.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [pt1TR_Mu.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [pt1TR_Mu.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [pt1TR_Mu.getSample(sam).addSystematic(lepTR) for sam in SigList+BGList+["QCD"]]
    [pt1TR_Mu.getSample(sam).addSystematic(btagTR) for sam in SigList+BGList+["QCD"]]
    [pt1TR_Mu.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [pt1TR_Mu.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [pt1TR_Mu.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [pt1TR_Mu.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [pt1TR_Mu.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [pt1TR_Mu.getSample(sam).addSystematic(metcoTR) for sam in SigList+BGList+["QCD"]]
        [pt1TR_Mu.getSample(sam).addSystematic(metpuTR) for sam in SigList+BGList+["QCD"]]
        [pt1TR_Mu.getSample(sam).addSystematic(trigTR) for sam in SigList+BGList+["QCD"]]
        [pt1TR_Mu.getSample(sam).addSystematic(lesTR) for sam in SigList+BGList]
        [pt1TR_Mu.getSample(sam).addSystematic(lermsTR) for sam in SigList+BGList]
        [pt1TR_Mu.getSample(sam).addSystematic(leridTR) for sam in SigList+BGList]

        
        
    pt2TR_El=bkgOnly.addChannel("jet2Pt",["TRElVR"],pt2NBinsTR,pt2BinLowTR,pt2BinHighTR)
    pt2TR_El.hasB = True
    pt2TR_El.hasBQCD = True
    pt2TR_El.useOverflowBin = True
    [pt2TR_El.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [pt2TR_El.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [pt2TR_El.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [pt2TR_El.getSample(sam).addSystematic(lepTR) for sam in SigList+BGList+["QCD"]]
    [pt2TR_El.getSample(sam).addSystematic(btagTR) for sam in SigList+BGList+["QCD"]]
    [pt2TR_El.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [pt2TR_El.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [pt2TR_El.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [pt2TR_El.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [pt2TR_El.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [pt2TR_El.getSample(sam).addSystematic(metcoTR) for sam in SigList+BGList+["QCD"]]
        [pt2TR_El.getSample(sam).addSystematic(metpuTR) for sam in SigList+BGList+["QCD"]]
        [pt2TR_El.getSample(sam).addSystematic(trigTR) for sam in SigList+BGList+["QCD"]]
        [pt2TR_El.getSample(sam).addSystematic(lesTR) for sam in SigList+BGList]
        [pt2TR_El.getSample(sam).addSystematic(lermsTR) for sam in SigList+BGList]
        [pt2TR_El.getSample(sam).addSystematic(leridTR) for sam in SigList+BGList]


    pt2TR_Mu=bkgOnly.addChannel("jet2Pt",["TRMuVR"],pt2NBinsTR,pt2BinLowTR,pt2BinHighTR)
    pt2TR_Mu.hasB = True
    pt2TR_Mu.hasBQCD = True
    pt2TR_Mu.useOverflowBin = True
    [pt2TR_Mu.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [pt2TR_Mu.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [pt2TR_Mu.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [pt2TR_Mu.getSample(sam).addSystematic(lepTR) for sam in SigList+BGList+["QCD"]]
    [pt2TR_Mu.getSample(sam).addSystematic(btagTR) for sam in SigList+BGList+["QCD"]]
    [pt2TR_Mu.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [pt2TR_Mu.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [pt2TR_Mu.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [pt2TR_Mu.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [pt2TR_Mu.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [pt2TR_Mu.getSample(sam).addSystematic(metcoTR) for sam in SigList+BGList+["QCD"]]
        [pt2TR_Mu.getSample(sam).addSystematic(metpuTR) for sam in SigList+BGList+["QCD"]]
        [pt2TR_Mu.getSample(sam).addSystematic(trigTR) for sam in SigList+BGList+["QCD"]]
        [pt2TR_Mu.getSample(sam).addSystematic(lesTR) for sam in SigList+BGList]
        [pt2TR_Mu.getSample(sam).addSystematic(lermsTR) for sam in SigList+BGList]
        [pt2TR_Mu.getSample(sam).addSystematic(leridTR) for sam in SigList+BGList] 

    wptWR_El=bkgOnly.addChannel("Wpt",["WRElVR"],metNBinsTR,metBinLowTR,metBinHighTR)
    wptWR_El.hasB = True
    wptWR_El.hasBQCD = False
    wptWR_El.useOverflowBin = True
    [wptWR_El.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [wptWR_El.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [wptWR_El.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [wptWR_El.getSample(sam).addSystematic(lepTR) for sam in SigList+BGList+["QCD"]]
    [wptWR_El.getSample(sam).addSystematic(btagTR) for sam in SigList+BGList+["QCD"]]
    [wptWR_El.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [wptWR_El.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [wptWR_El.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [wptWR_El.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [wptWR_El.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [wptWR_El.getSample(sam).addSystematic(metcoTR) for sam in SigList+BGList+["QCD"]]
        [wptWR_El.getSample(sam).addSystematic(metpuTR) for sam in SigList+BGList+["QCD"]]
        [wptWR_El.getSample(sam).addSystematic(trigTR) for sam in SigList+BGList+["QCD"]]
        [wptWR_El.getSample(sam).addSystematic(lesTR) for sam in SigList+BGList]
        [wptWR_El.getSample(sam).addSystematic(lermsTR) for sam in SigList+BGList]
        [wptWR_El.getSample(sam).addSystematic(leridTR) for sam in SigList+BGList]


    wptWR_Mu=bkgOnly.addChannel("Wpt",["WRMuVR"],metNBinsTR,metBinLowTR,metBinHighTR)
    wptWR_Mu.hasB = True
    wptWR_Mu.hasBQCD = False
    wptWR_Mu.useOverflowBin = True
    [wptWR_Mu.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [wptWR_Mu.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [wptWR_Mu.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [wptWR_Mu.getSample(sam).addSystematic(lepTR) for sam in SigList+BGList+["QCD"]]
    [wptWR_Mu.getSample(sam).addSystematic(btagTR) for sam in SigList+BGList+["QCD"]]
    [wptWR_Mu.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [wptWR_Mu.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [wptWR_Mu.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [wptWR_Mu.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [wptWR_Mu.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [wptWR_Mu.getSample(sam).addSystematic(metcoTR) for sam in SigList+BGList+["QCD"]]
        [wptWR_Mu.getSample(sam).addSystematic(metpuTR) for sam in SigList+BGList+["QCD"]]
        [wptWR_Mu.getSample(sam).addSystematic(trigTR) for sam in SigList+BGList+["QCD"]]
        [wptWR_Mu.getSample(sam).addSystematic(lesTR) for sam in SigList+BGList]
        [wptWR_Mu.getSample(sam).addSystematic(lermsTR) for sam in SigList+BGList]
        [wptWR_Mu.getSample(sam).addSystematic(leridTR) for sam in SigList+BGList]


    metWR_El=bkgOnly.addChannel("met",["WRElVR"],metNBinsTR,metBinLowTR,metBinHighTR)
    metWR_El.hasB = True
    metWR_El.hasBQCD = False
    metWR_El.useOverflowBin = True
    [metWR_El.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [metWR_El.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [metWR_El.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [metWR_El.getSample(sam).addSystematic(lepTR) for sam in SigList+BGList+["QCD"]]
    [metWR_El.getSample(sam).addSystematic(btagTR) for sam in SigList+BGList+["QCD"]]
    [metWR_El.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [metWR_El.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [metWR_El.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [metWR_El.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [metWR_El.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [metWR_El.getSample(sam).addSystematic(metcoTR) for sam in SigList+BGList+["QCD"]]
        [metWR_El.getSample(sam).addSystematic(metpuTR) for sam in SigList+BGList+["QCD"]]
        [metWR_El.getSample(sam).addSystematic(trigTR) for sam in SigList+BGList+["QCD"]]
        [metWR_El.getSample(sam).addSystematic(lesTR) for sam in SigList+BGList]
        [metWR_El.getSample(sam).addSystematic(lermsTR) for sam in SigList+BGList]
        [metWR_El.getSample(sam).addSystematic(leridTR) for sam in SigList+BGList]


    metWR_Mu=bkgOnly.addChannel("met",["WRMuVR"],metNBinsTR,metBinLowTR,metBinHighTR)
    metWR_Mu.hasB = True
    metWR_Mu.hasBQCD = False
    metWR_Mu.useOverflowBin = True
    [metWR_Mu.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [metWR_Mu.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [metWR_Mu.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [metWR_Mu.getSample(sam).addSystematic(lepTR) for sam in SigList+BGList+["QCD"]]
    [metWR_Mu.getSample(sam).addSystematic(btagTR) for sam in SigList+BGList+["QCD"]]
    [metWR_Mu.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [metWR_Mu.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [metWR_Mu.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [metWR_Mu.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [metWR_Mu.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [metWR_Mu.getSample(sam).addSystematic(metcoTR) for sam in SigList+BGList+["QCD"]]
        [metWR_Mu.getSample(sam).addSystematic(metpuTR) for sam in SigList+BGList+["QCD"]]
        [metWR_Mu.getSample(sam).addSystematic(trigTR) for sam in SigList+BGList+["QCD"]]
        [metWR_Mu.getSample(sam).addSystematic(lesTR) for sam in SigList+BGList]
        [metWR_Mu.getSample(sam).addSystematic(lermsTR) for sam in SigList+BGList]
        [metWR_Mu.getSample(sam).addSystematic(leridTR) for sam in SigList+BGList]       

    ZptZR_ee=bkgOnly.addChannel("Zpt",["ZRee"],metNBinsTR,metBinLowTR,metBinHighTR)
    ZptZR_ee.hasB = False
    ZptZR_ee.hasBQCD = False
    ZptZR_ee.useOverflowBin = True
    [ZptZR_ee.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [ZptZR_ee.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [ZptZR_ee.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [ZptZR_ee.getSample(sam).addSystematic(lepTR) for sam in SigList+BGList+["QCD"]]
    [ZptZR_ee.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [ZptZR_ee.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [ZptZR_ee.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [ZptZR_ee.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [ZptZR_ee.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [ZptZR_ee.getSample(sam).addSystematic(metcoTR) for sam in SigList+BGList+["QCD"]]
        [ZptZR_ee.getSample(sam).addSystematic(metpuTR) for sam in SigList+BGList+["QCD"]]
        [ZptZR_ee.getSample(sam).addSystematic(trigTR) for sam in SigList+BGList+["QCD"]]
        [ZptZR_ee.getSample(sam).addSystematic(lesTR) for sam in SigList+BGList]
        [ZptZR_ee.getSample(sam).addSystematic(lermsTR) for sam in SigList+BGList]
        [ZptZR_ee.getSample(sam).addSystematic(leridTR) for sam in SigList+BGList]

    ZptZRY_ee=bkgOnly.addChannel("Zpt",["ZReeY"],metNBinsTR,metBinLowTR,metBinHighTR)
    ZptZRY_ee.hasB = False
    ZptZRY_ee.hasBQCD = False
    ZptZRY_ee.useOverflowBin = True
    [ZptZRY_ee.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [ZptZRY_ee.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [ZptZRY_ee.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [ZptZRY_ee.getSample(sam).addSystematic(lepTR) for sam in SigList+BGList+["QCD"]]
    [ZptZRY_ee.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [ZptZRY_ee.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [ZptZRY_ee.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [ZptZRY_ee.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [ZptZRY_ee.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [ZptZRY_ee.getSample(sam).addSystematic(metcoTR) for sam in SigList+BGList+["QCD"]]
        [ZptZRY_ee.getSample(sam).addSystematic(metpuTR) for sam in SigList+BGList+["QCD"]]
        [ZptZRY_ee.getSample(sam).addSystematic(trigTR) for sam in SigList+BGList+["QCD"]]
        [ZptZRY_ee.getSample(sam).addSystematic(lesTR) for sam in SigList+BGList]
        [ZptZRY_ee.getSample(sam).addSystematic(lermsTR) for sam in SigList+BGList]
        [ZptZRY_ee.getSample(sam).addSystematic(leridTR) for sam in SigList+BGList]    


    ZptZR_mm=bkgOnly.addChannel("Zpt",["ZRmm"],metNBinsTR,metBinLowTR,metBinHighTR)
    ZptZR_mm.hasB = False
    ZptZR_mm.hasBQCD = False
    ZptZR_mm.useOverflowBin = True
    [ZptZR_mm.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [ZptZR_mm.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [ZptZR_mm.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [ZptZR_mm.getSample(sam).addSystematic(lepTR) for sam in SigList+BGList+["QCD"]]
    [ZptZR_mm.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [ZptZR_mm.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [ZptZR_mm.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [ZptZR_mm.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [ZptZR_mm.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [ZptZR_mwm.getSample(sam).addSystematic(metcoTR) for sam in SigList+BGList+["QCD"]]
        [ZptZR_mm.getSample(sam).addSystematic(metpuTR) for sam in SigList+BGList+["QCD"]]
        [ZptZR_mm.getSample(sam).addSystematic(trigTR) for sam in SigList+BGList+["QCD"]]
        [ZptZR_mm.getSample(sam).addSystematic(lesTR) for sam in SigList+BGList]
        [ZptZR_mm.getSample(sam).addSystematic(lermsTR) for sam in SigList+BGList]
        [ZptZR_mm.getSample(sam).addSystematic(leridTR) for sam in SigList+BGList]

    ZptZRY_mm=bkgOnly.addChannel("Zpt",["ZRmmY"],metNBinsTR,metBinLowTR,metBinHighTR)
    ZptZRY_mm.hasB = False
    ZptZRY_mm.hasBQCD = False
    ZptZRY_mm.useOverflowBin = True
    [ZptZRY_mm.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [ZptZRY_mm.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [ZptZRY_mm.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [ZptZRY_mm.getSample(sam).addSystematic(lepTR) for sam in SigList+BGList+["QCD"]]
    [ZptZRY_mm.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [ZptZRY_mm.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [ZptZRY_mm.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [ZptZRY_mm.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [ZptZRY_mm.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [ZptZRY_mm.getSample(sam).addSystematic(metcoTR) for sam in SigList+BGList+["QCD"]]
        [ZptZRY_mm.getSample(sam).addSystematic(metpuTR) for sam in SigList+BGList+["QCD"]]
        [ZptZRY_mm.getSample(sam).addSystematic(trigTR) for sam in SigList+BGList+["QCD"]]
        [ZptZRY_mm.getSample(sam).addSystematic(lesTR) for sam in SigList+BGList]
        [ZptZRY_mm.getSample(sam).addSystematic(lermsTR) for sam in SigList+BGList]
        [ZptZRY_mm.getSample(sam).addSystematic(leridTR) for sam in SigList+BGList]    


if doValidationSR:

    # S2 using meff
    meff2ee = bkgOnly.addChannel("meffInc",["S2ee"],meffNBins,meffBinLow,meffBinHigh)
    meff2ee.useOverflowBin=True
    [meff2ee.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meff2ee.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meff2ee.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]  
    #[s.mergeSamples([topSample_Np0.name,wzSample_Np0.name,topSample_Np1.name,wzSample_Np1.name,topSample_Np2.name,wzSample_Np2.name,topSample_Np3.name,wzSample_Np3.name,topSample_Np4.name,wzSample_Np4.name,topSample_Np5.name,wzSample_Np5.name,bgSample.name]) for s in meff2ee.getSystematic(jesS2DL.name)]
    [meff2ee.getSample(sam).addSystematic(lepS2DL) for sam in SigList+BGList+["QCD"]]
    [meff2ee.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meff2ee.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meff2ee.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meff2ee.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meff2ee.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]
    
    if fullSyst:
        [meff2ee.getSample(sam).addSystematic(metcoS2DL) for sam in SigList+BGList+["QCD"]]
        [meff2ee.getSample(sam).addSystematic(metpuS2DL) for sam in SigList+BGList+["QCD"]]
        [meff2ee.getSample(sam).addSystematic(trigS2DL) for sam in SigList+BGList+["QCD"]]
        [meff2ee.getSample(sam).addSystematic(lesS2DL) for sam in SigList+BGList]
        [meff2ee.getSample(sam).addSystematic(lermsS2DL) for sam in SigList+BGList]
        [meff2ee.getSample(sam).addSystematic(leridS2DL) for sam in SigList+BGList]

    # S4 using meff
    meff4ee = bkgOnly.addChannel("meffInc",["S4ee"],meffNBins,meffBinLow,meffBinHigh)
    meff4ee.useOverflowBin=True
    [meff4ee.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meff4ee.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meff4ee.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]  
    #[s.mergeSamples([topSample_Np0.name,wzSample_Np0.name,topSample_Np1.name,wzSample_Np1.name,topSample_Np2.name,wzSample_Np2.name,topSample_Np3.name,wzSample_Np3.name,topSample_Np4.name,wzSample_Np4.name,topSample_Np5.name,wzSample_Np5.name,bgSample.name]) for s in meff4ee.getSystematic(jesS4DL.name)]
    [meff4ee.getSample(sam).addSystematic(lepS4DL) for sam in SigList+BGList+["QCD"]]
    [meff4ee.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meff4ee.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meff4ee.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meff4ee.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meff4ee.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]
    
    if fullSyst:
        [meff4ee.getSample(sam).addSystematic(metcoS4DL) for sam in SigList+BGList+["QCD"]]
        [meff4ee.getSample(sam).addSystematic(metpuS4DL) for sam in SigList+BGList+["QCD"]]
        [meff4ee.getSample(sam).addSystematic(trigS4DL) for sam in SigList+BGList+["QCD"]]
        [meff4ee.getSample(sam).addSystematic(lesS4DL) for sam in SigList+BGList]
        [meff4ee.getSample(sam).addSystematic(lermsS4DL) for sam in SigList+BGList]
        [meff4ee.getSample(sam).addSystematic(leridS4DL) for sam in SigList+BGList]

    # S2 using meff
    meff2em = bkgOnly.addChannel("meffInc",["S2em"],meffNBins,meffBinLow,meffBinHigh)
    meff2em.useOverflowBin=True
    [meff2em.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meff2em.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meff2em.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]] 
    #[s.mergeSamples([topSample_Np0.name,wzSample_Np0.name,topSample_Np1.name,wzSample_Np1.name,topSample_Np2.name,wzSample_Np2.name,topSample_Np3.name,wzSample_Np3.name,topSample_Np4.name,wzSample_Np4.name,topSample_Np5.name,wzSample_Np5.name,bgSample.name]) for s in meff2em.getSystematic(jesS2DL.name)]
    [meff2em.getSample(sam).addSystematic(lepS2DL) for sam in SigList+BGList+["QCD"]]
    [meff2em.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meff2em.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meff2em.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meff2em.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meff2em.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meff2em.getSample(sam).addSystematic(metcoS2DL) for sam in SigList+BGList+["QCD"]]
        [meff2em.getSample(sam).addSystematic(metpuS2DL) for sam in SigList+BGList+["QCD"]]
        [meff2em.getSample(sam).addSystematic(trigS2DL) for sam in SigList+BGList+["QCD"]]
        [meff2em.getSample(sam).addSystematic(lesS2DL) for sam in SigList+BGList]
        [meff2em.getSample(sam).addSystematic(lermsS2DL) for sam in SigList+BGList]
        [meff2em.getSample(sam).addSystematic(leridS2DL) for sam in SigList+BGList]

    # S4 using meff
    meff4em = bkgOnly.addChannel("meffInc",["S4em"],meffNBins,meffBinLow,meffBinHigh)
    meff4em.useOverflowBin=True
    [meff4em.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meff4em.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meff4em.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]] 
    #[s.mergeSamples([topSample_Np0.name,wzSample_Np0.name,topSample_Np1.name,wzSample_Np1.name,topSample_Np2.name,wzSample_Np2.name,topSample_Np3.name,wzSample_Np3.name,topSample_Np4.name,wzSample_Np4.name,topSample_Np5.name,wzSample_Np5.name,bgSample.name]) for s in meff4em.getSystematic(jesS4DL.name)]
    [meff4em.getSample(sam).addSystematic(lepS4DL) for sam in SigList+BGList+["QCD"]]
    [meff4em.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meff4em.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meff4em.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meff4em.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meff4em.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meff4em.getSample(sam).addSystematic(metcoS4DL) for sam in SigList+BGList+["QCD"]]
        [meff4em.getSample(sam).addSystematic(metpuS4DL) for sam in SigList+BGList+["QCD"]]
        [meff4em.getSample(sam).addSystematic(trigS4DL) for sam in SigList+BGList+["QCD"]]
        [meff4em.getSample(sam).addSystematic(lesS4DL) for sam in SigList+BGList]
        [meff4em.getSample(sam).addSystematic(lermsS4DL) for sam in SigList+BGList]
        [meff4em.getSample(sam).addSystematic(leridS4DL) for sam in SigList+BGList]

    # S2 using meff
    meff2mm = bkgOnly.addChannel("meffInc",["S2mm"],meffNBins,meffBinLow,meffBinHigh)
    meff2mm.useOverflowBin=True
    [meff2mm.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meff2mm.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meff2mm.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]] 
    #[s.mergeSamples([topSample_Np0.name,wzSample_Np0.name,topSample_Np1.name,wzSample_Np1.name,topSample_Np2.name,wzSample_Np2.name,topSample_Np3.name,wzSample_Np3.name,topSample_Np4.name,wzSample_Np4.name,topSample_Np5.name,wzSample_Np5.name,bgSample.name]) for s in meff2mm.getSystematic(jesS2DL.name)]
    [meff2mm.getSample(sam).addSystematic(lepS2DL) for sam in SigList+BGList+["QCD"]]
    [meff2em.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meff2mm.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meff2mm.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meff2mm.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meff2mm.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meff2mm.getSample(sam).addSystematic(metcoS2DL) for sam in SigList+BGList+["QCD"]]
        [meff2mm.getSample(sam).addSystematic(metpuS2DL) for sam in SigList+BGList+["QCD"]]
        [meff2mm.getSample(sam).addSystematic(trigS2DL) for sam in SigList+BGList+["QCD"]]
        [meff2mm.getSample(sam).addSystematic(lesS2DL) for sam in SigList+BGList]
        [meff2mm.getSample(sam).addSystematic(lermsS2DL) for sam in SigList+BGList]
        [meff2mm.getSample(sam).addSystematic(leridS2DL) for sam in SigList+BGList]

    # S4 using meff
    meff4mm = bkgOnly.addChannel("meffInc",["S4mm"],meffNBins,meffBinLow,meffBinHigh)
    meff4mm.useOverflowBin=True
    [meff4mm.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meff4mm.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meff4mm.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]    
    #[s.mergeSamples([topSample_Np0.name,wzSample_Np0.name,topSample_Np1.name,wzSample_Np1.name,topSample_Np2.name,wzSample_Np2.name,topSample_Np3.name,wzSample_Np3.name,topSample_Np4.name,wzSample_Np4.name,topSample_Np5.name,wzSample_Np5.name,bgSample.name]) for s in meff4mm.getSystematic(jesS4DL.name)]
    [meff4mm.getSample(sam).addSystematic(lepS4DL) for sam in SigList+BGList+["QCD"]]
    [meff4mm.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meff4mm.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meff4mm.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meff4mm.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meff4mm.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meff4mm.getSample(sam).addSystematic(metcoS4DL) for sam in SigList+BGList+["QCD"]]
        [meff4mm.getSample(sam).addSystematic(metpuS4DL) for sam in SigList+BGList+["QCD"]]
        [meff4mm.getSample(sam).addSystematic(trigS4DL) for sam in SigList+BGList+["QCD"]]
        [meff4mm.getSample(sam).addSystematic(lesS4DL) for sam in SigList+BGList]
        [meff4mm.getSample(sam).addSystematic(lermsS4DL) for sam in SigList+BGList]
        [meff4mm.getSample(sam).addSystematic(leridS4DL) for sam in SigList+BGList]

# HARD LEPTON SRS

    meffS3_El=bkgOnly.addChannel("meffInc",["S3El"],meffNBinsHL,meffBinLowHL,meffBinHighHL)
    meffS3_El.useOverflowBin = True
    [meffS3_El.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffS3_El.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffS3_El.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffS3_El.getSample(sam).addSystematic(lepS3) for sam in SigList+BGList+["QCD"]]
    [meffS3_El.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffS3_El.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffS3_El.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffS3_El.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffS3_El.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffS3_El.getSample(sam).addSystematic(metcoS3) for sam in SigList+BGList+["QCD"]]
        [meffS3_El.getSample(sam).addSystematic(metpuS3) for sam in SigList+BGList+["QCD"]]
        [meffS3_El.getSample(sam).addSystematic(trigS3) for sam in SigList+BGList+["QCD"]]
        [meffS3_El.getSample(sam).addSystematic(lesS3) for sam in SigList+BGList]
        [meffS3_El.getSample(sam).addSystematic(lermsS3) for sam in SigList+BGList]
        [meffS3_El.getSample(sam).addSystematic(leridS3) for sam in SigList+BGList]


    meffS3_Mu=bkgOnly.addChannel("meffInc",["S3Mu"],meffNBinsHL,meffBinLowHL,meffBinHighHL)
    meffS3_Mu.useOverflowBin = True
    [meffS3_Mu.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffS3_Mu.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffS3_Mu.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffS3_Mu.getSample(sam).addSystematic(lepS3) for sam in SigList+BGList+["QCD"]]
    [meffS3_Mu.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffS3_Mu.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffS3_Mu.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffS3_Mu.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffS3_Mu.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffS3_Mu.getSample(sam).addSystematic(metcoS3) for sam in SigList+BGList+["QCD"]]
        [meffS3_Mu.getSample(sam).addSystematic(metpuS3) for sam in SigList+BGList+["QCD"]]
        [meffS3_Mu.getSample(sam).addSystematic(trigS3) for sam in SigList+BGList+["QCD"]]
        [meffS3_Mu.getSample(sam).addSystematic(lesS3) for sam in SigList+BGList]
        [meffS3_Mu.getSample(sam).addSystematic(lermsS3) for sam in SigList+BGList]
        [meffS3_Mu.getSample(sam).addSystematic(leridS3) for sam in SigList+BGList]   


    meffS4_El=bkgOnly.addChannel("meffInc",["S4El"],meffNBinsHL,meffBinLowHL,meffBinHighHL)
    meffS4_El.useOverflowBin = True
    [meffS4_El.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffS4_El.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffS4_El.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]] 
    [meffS4_El.getSample(sam).addSystematic(lepS4) for sam in SigList+BGList+["QCD"]]
    [meffS4_El.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffS4_El.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffS4_El.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffS4_El.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffS4_El.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffS4_El.getSample(sam).addSystematic(metcoS4) for sam in SigList+BGList+["QCD"]]
        [meffS4_El.getSample(sam).addSystematic(metpuS4) for sam in SigList+BGList+["QCD"]]
        [meffS4_El.getSample(sam).addSystematic(trigS4) for sam in SigList+BGList+["QCD"]]
        [meffS4_El.getSample(sam).addSystematic(lesS4) for sam in SigList+BGList]
        [meffS4_El.getSample(sam).addSystematic(lermsS4) for sam in SigList+BGList]
        [meffS4_El.getSample(sam).addSystematic(leridS4) for sam in SigList+BGList]


    meffS4_Mu=bkgOnly.addChannel("meffInc",["S4Mu"],meffNBinsHL,meffBinLowHL,meffBinHighHL)
    meffS4_Mu.useOverflowBin = True
    [meffS4_Mu.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffS4_Mu.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffS4_Mu.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]] 
    [meffS4_Mu.getSample(sam).addSystematic(lepS4) for sam in SigList+BGList+["QCD"]]

    [meffS4_Mu.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffS4_Mu.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffS4_Mu.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffS4_Mu.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffS4_Mu.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]
    if fullSyst:
        [meffS4_Mu.getSample(sam).addSystematic(metcoS4) for sam in SigList+BGList+["QCD"]]
        [meffS4_Mu.getSample(sam).addSystematic(metpuS4) for sam in SigList+BGList+["QCD"]]
        [meffS4_Mu.getSample(sam).addSystematic(trigS4) for sam in SigList+BGList+["QCD"]]
        [meffS4_Mu.getSample(sam).addSystematic(lesS4) for sam in SigList+BGList]
        [meffS4_Mu.getSample(sam).addSystematic(lermsS4) for sam in SigList+BGList]
        [meffS4_Mu.getSample(sam).addSystematic(leridS4) for sam in SigList+BGList]


    meffS3T_El=bkgOnly.addChannel("meffInc",["SR3jTEl"],1,1200,meffBinHighHL)
    meffS3T_El.useOverflowBin = True
    [meffS3T_El.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffS3T_El.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffS3T_El.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffS3T_El.getSample(sam).addSystematic(lepS3T) for sam in SigList+BGList+["QCD"]]
    [meffS3T_El.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffS3T_El.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffS3T_El.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffS3T_El.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffS3T_El.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffS3T_El.getSample(sam).addSystematic(metcoS3T) for sam in SigList+BGList+["QCD"]]
        [meffS3T_El.getSample(sam).addSystematic(metpuS3T) for sam in SigList+BGList+["QCD"]]
        [meffS3T_El.getSample(sam).addSystematic(trigS3T) for sam in SigList+BGList+["QCD"]]
        [meffS3T_El.getSample(sam).addSystematic(lesS3T) for sam in SigList+BGList]
        [meffS3T_El.getSample(sam).addSystematic(lermsS3T) for sam in SigList+BGList]
        [meffS3T_El.getSample(sam).addSystematic(leridS3T) for sam in SigList+BGList]


    meffS3T_Mu=bkgOnly.addChannel("meffInc",["SR3jTMu"],1,1200,meffBinHighHL)
    meffS3T_Mu.useOverflowBin = True
    [meffS3T_Mu.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffS3T_Mu.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffS3T_Mu.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffS3T_Mu.getSample(sam).addSystematic(lepS3T) for sam in SigList+BGList+["QCD"]]
    [meffS3T_Mu.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffS3T_Mu.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffS3T_Mu.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffS3T_Mu.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffS3T_Mu.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffS3T_Mu.getSample(sam).addSystematic(metcoS3T) for sam in SigList+BGList+["QCD"]]
        [meffS3T_Mu.getSample(sam).addSystematic(metpuS3T) for sam in SigList+BGList+["QCD"]]
        [meffS3T_Mu.getSample(sam).addSystematic(trigS3T) for sam in SigList+BGList+["QCD"]]
        [meffS3T_Mu.getSample(sam).addSystematic(lesS3T) for sam in SigList+BGList]
        [meffS3T_Mu.getSample(sam).addSystematic(lermsS3T) for sam in SigList+BGList]
        [meffS3T_Mu.getSample(sam).addSystematic(leridS3T) for sam in SigList+BGList]   


    meffS4T_El=bkgOnly.addChannel("meffInc",["SR4jTEl"],1,800,meffBinHighHL)
    meffS4T_El.useOverflowBin = True
    [meffS4T_El.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffS4T_El.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffS4T_El.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffS4T_El.getSample(sam).addSystematic(lepS4T) for sam in SigList+BGList+["QCD"]]
    [meffS4T_El.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffS4T_El.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffS4T_El.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffS4T_El.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffS4T_El.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffS4T_El.getSample(sam).addSystematic(metcoS4T) for sam in SigList+BGList+["QCD"]]
        [meffS4T_El.getSample(sam).addSystematic(metpuS4T) for sam in SigList+BGList+["QCD"]]
        [meffS4T_El.getSample(sam).addSystematic(trigS4T) for sam in SigList+BGList+["QCD"]]
        [meffS4T_El.getSample(sam).addSystematic(lesS4T) for sam in SigList+BGList]
        [meffS4T_El.getSample(sam).addSystematic(lermsS4T) for sam in SigList+BGList]
        [meffS4T_El.getSample(sam).addSystematic(leridS4T) for sam in SigList+BGList]


    meffS4T_Mu=bkgOnly.addChannel("meffInc",["SR4jTMu"],1,800,meffBinHighHL)
    meffS4T_Mu.useOverflowBin = True
    [meffS4T_Mu.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffS4T_Mu.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffS4T_Mu.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffS4T_Mu.getSample(sam).addSystematic(lepS4T) for sam in SigList+BGList+["QCD"]]
    [meffS4T_Mu.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffS4T_Mu.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffS4T_Mu.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffS4T_Mu.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffS4T_Mu.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffS4T_Mu.getSample(sam).addSystematic(metcoS4T) for sam in SigList+BGList+["QCD"]]
        [meffS4T_Mu.getSample(sam).addSystematic(metpuS4T) for sam in SigList+BGList+["QCD"]]
        [meffS4T_Mu.getSample(sam).addSystematic(trigS4T) for sam in SigList+BGList+["QCD"]]
        [meffS4T_Mu.getSample(sam).addSystematic(lesS4T) for sam in SigList+BGList]
        [meffS4T_Mu.getSample(sam).addSystematic(lermsS4T) for sam in SigList+BGList]
        [meffS4T_Mu.getSample(sam).addSystematic(leridS4T) for sam in SigList+BGList]

    meffS7T_El=bkgOnly.addChannel("meffInc",["SR7jTEl"],1,750,meffBinHighHL)
    meffS7T_El.useOverflowBin = True
    [meffS7T_El.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffS7T_El.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffS7T_El.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffS7T_El.getSample(sam).addSystematic(lepS4T) for sam in SigList+BGList+["QCD"]]
    [meffS7T_El.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffS7T_El.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffS7T_El.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffS7T_El.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffS7T_El.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffS7T_El.getSample(sam).addSystematic(metcoS4T) for sam in SigList+BGList+["QCD"]]
        [meffS7T_El.getSample(sam).addSystematic(metpuS4T) for sam in SigList+BGList+["QCD"]]
        [meffS7T_El.getSample(sam).addSystematic(trigS4T) for sam in SigList+BGList+["QCD"]]
        [meffS7T_El.getSample(sam).addSystematic(lesS4T) for sam in SigList+BGList]
        [meffS7T_El.getSample(sam).addSystematic(lermsS4T) for sam in SigList+BGList]
        [meffS7T_El.getSample(sam).addSystematic(leridS4T) for sam in SigList+BGList]


    meffS7T_Mu=bkgOnly.addChannel("meffInc",["SR7jTMu"],1,750,meffBinHighHL)
    meffS7T_Mu.useOverflowBin = True
    [meffS7T_Mu.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffS7T_Mu.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffS7T_Mu.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffS7T_Mu.getSample(sam).addSystematic(lepS4T) for sam in SigList+BGList+["QCD"]]
    [meffS7T_Mu.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffS7T_Mu.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffS7T_Mu.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffS7T_Mu.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffS7T_Mu.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffS7T_Mu.getSample(sam).addSystematic(metcoS4T) for sam in SigList+BGList+["QCD"]]
        [meffS7T_Mu.getSample(sam).addSystematic(metpuS4T) for sam in SigList+BGList+["QCD"]]
        [meffS7T_Mu.getSample(sam).addSystematic(trigS4T) for sam in SigList+BGList+["QCD"]]
        [meffS7T_Mu.getSample(sam).addSystematic(lesS4T) for sam in SigList+BGList]
        [meffS7T_Mu.getSample(sam).addSystematic(lermsS4T) for sam in SigList+BGList]
        [meffS7T_Mu.getSample(sam).addSystematic(leridS4T) for sam in SigList+BGList]
            
if doValidationDilep:


    ## check impact of kfactor fit on several distributions

    meffVR4_ee=bkgOnly.addChannel("meffInc",["VR4ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR4_ee.useOverflowBin = True
    [meffVR4_ee.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffVR4_ee.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffVR4_ee.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffVR4_ee.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [meffVR4_ee.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffVR4_ee.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffVR4_ee.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffVR4_ee.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffVR4_ee.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffVR4_ee.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [meffVR4_ee.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [meffVR4_ee.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [meffVR4_ee.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [meffVR4_ee.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [meffVR4_ee.getSample(sam).addSystematic(leridVR) for sam in BGList]

    meffVR4_em=bkgOnly.addChannel("meffInc",["VR4em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR4_em.useOverflowBin = True
    [meffVR4_em.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffVR4_em.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffVR4_em.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffVR4_em.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [meffVR4_em.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffVR4_em.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffVR4_em.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffVR4_em.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffVR4_em.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffVR4_em.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [meffVR4_em.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [meffVR4_em.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [meffVR4_em.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [meffVR4_em.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [meffVR4_em.getSample(sam).addSystematic(leridVR) for sam in BGList]

    meffVR4_mm=bkgOnly.addChannel("meffInc",["VR4mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR4_mm.useOverflowBin = True
    [meffVR4_mm.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffVR4_mm.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffVR4_mm.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffVR4_mm.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [meffVR4_mm.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffVR4_mm.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffVR4_mm.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffVR4_mm.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffVR4_mm.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffVR4_mm.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [meffVR4_mm.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [meffVR4_mm.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [meffVR4_mm.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [meffVR4_mm.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [meffVR4_mm.getSample(sam).addSystematic(leridVR) for sam in BGList]

    nJetVR4_ee=bkgOnly.addChannel("nJet",["VR4ee"],nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
    nJetVR4_ee.useOverflowBin = True
    [nJetVR4_ee.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [nJetVR4_ee.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [nJetVR4_ee.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [nJetVR4_ee.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [nJetVR4_ee.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [nJetVR4_ee.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [nJetVR4_ee.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [nJetVR4_ee.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [nJetVR4_ee.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [nJetVR4_ee.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [nJetVR4_ee.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [nJetVR4_ee.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [nJetVR4_ee.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [nJetVR4_ee.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [nJetVR4_ee.getSample(sam).addSystematic(leridVR) for sam in BGList]

    nJetVR4_em=bkgOnly.addChannel("nJet",["VR4em"],nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
    nJetVR4_em.useOverflowBin = True
    [nJetVR4_em.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [nJetVR4_em.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [nJetVR4_em.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [nJetVR4_em.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [nJetVR4_em.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [nJetVR4_em.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [nJetVR4_em.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [nJetVR4_em.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [nJetVR4_em.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [nJetVR4_em.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [nJetVR4_em.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [nJetVR4_em.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [nJetVR4_em.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [nJetVR4_em.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [nJetVR4_em.getSample(sam).addSystematic(leridVR) for sam in BGList]

    nJetVR4_mm=bkgOnly.addChannel("nJet",["VR4mm"],nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
    nJetVR4_mm.useOverflowBin = True
    [nJetVR4_mm.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [nJetVR4_mm.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [nJetVR4_mm.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [nJetVR4_mm.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [nJetVR4_mm.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [nJetVR4_mm.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [nJetVR4_mm.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [nJetVR4_mm.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [nJetVR4_mm.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [nJetVR4_mm.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [nJetVR4_mm.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [nJetVR4_mm.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [nJetVR4_mm.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [nJetVR4_mm.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [nJetVR4_mm.getSample(sam).addSystematic(leridVR) for sam in BGList]

    meffVR2_ee=bkgOnly.addChannel("meffInc",["VR2ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR2_ee.useOverflowBin = True
    [meffVR2_ee.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffVR2_ee.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffVR2_ee.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffVR2_ee.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [meffVR2_ee.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffVR2_ee.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffVR2_ee.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffVR2_ee.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffVR2_ee.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffVR2_ee.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [meffVR2_ee.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [meffVR2_ee.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [meffVR2_ee.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [meffVR2_ee.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [meffVR2_ee.getSample(sam).addSystematic(leridVR) for sam in BGList]

    meffVR2_em=bkgOnly.addChannel("meffInc",["VR2em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR2_em.useOverflowBin = True
    [meffVR2_em.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffVR2_em.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffVR2_em.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffVR2_em.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [meffVR2_em.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffVR2_em.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffVR2_em.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffVR2_em.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffVR2_em.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffVR2_em.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [meffVR2_em.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [meffVR2_em.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [meffVR2_em.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [meffVR2_em.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [meffVR2_em.getSample(sam).addSystematic(leridVR) for sam in BGList]

    meffVR2_mm=bkgOnly.addChannel("meffInc",["VR2mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR2_mm.useOverflowBin = True
    [meffVR2_mm.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffVR2_mm.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffVR2_mm.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffVR2_mm.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [meffVR2_mm.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffVR2_mm.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffVR2_mm.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffVR2_mm.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffVR2_mm.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffVR2_mm.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [meffVR2_mm.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [meffVR2_mm.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [meffVR2_mm.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [meffVR2_mm.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [meffVR2_mm.getSample(sam).addSystematic(leridVR) for sam in BGList]

    nJetVR2_ee=bkgOnly.addChannel("nJet",["VR2ee"],nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
    nJetVR2_ee.useOverflowBin = True
    [nJetVR2_ee.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [nJetVR2_ee.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [nJetVR2_ee.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [nJetVR2_ee.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [nJetVR2_ee.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [nJetVR2_ee.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [nJetVR2_ee.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [nJetVR2_ee.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [nJetVR2_ee.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [nJetVR2_ee.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [nJetVR2_ee.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [nJetVR2_ee.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [nJetVR2_ee.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [nJetVR2_ee.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [nJetVR2_ee.getSample(sam).addSystematic(leridVR) for sam in BGList]

    nJetVR2_em=bkgOnly.addChannel("nJet",["VR2em"],nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
    nJetVR2_em.useOverflowBin = True
    [nJetVR2_em.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [nJetVR2_em.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [nJetVR2_em.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [nJetVR2_em.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [nJetVR2_em.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [nJetVR2_em.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [nJetVR2_em.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [nJetVR2_em.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [nJetVR2_em.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [nJetVR2_em.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [nJetVR2_em.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [nJetVR2_em.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [nJetVR2_em.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [nJetVR2_em.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [nJetVR2_em.getSample(sam).addSystematic(leridVR) for sam in BGList]

    nJetVR2_mm=bkgOnly.addChannel("nJet",["VR2mm"],nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
    nJetVR2_mm.useOverflowBin = True
    [nJetVR2_mm.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [nJetVR2_mm.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [nJetVR2_mm.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [nJetVR2_mm.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [nJetVR2_mm.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [nJetVR2_mm.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [nJetVR2_mm.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [nJetVR2_mm.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [nJetVR2_mm.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [nJetVR2_mm.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [nJetVR2_mm.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [nJetVR2_mm.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [nJetVR2_mm.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [nJetVR2_mm.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [nJetVR2_mm.getSample(sam).addSystematic(leridVR) for sam in BGList]

    meffVR3_ee=bkgOnly.addChannel("meffInc",["VR3ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR3_ee.useOverflowBin = True
    [meffVR3_ee.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffVR3_ee.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffVR3_ee.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffVR3_ee.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [meffVR3_ee.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffVR3_ee.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffVR3_ee.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffVR3_ee.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffVR3_ee.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffVR3_ee.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [meffVR3_ee.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [meffVR3_ee.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [meffVR3_ee.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [meffVR3_ee.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [meffVR3_ee.getSample(sam).addSystematic(leridVR) for sam in BGList]

    meffVR3_em=bkgOnly.addChannel("meffInc",["VR3em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR3_em.useOverflowBin = True
    [meffVR3_em.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffVR3_em.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffVR3_em.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffVR3_em.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [meffVR3_em.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffVR3_em.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffVR3_em.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffVR3_em.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffVR3_em.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffVR3_em.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [meffVR3_em.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [meffVR3_em.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [meffVR3_em.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [meffVR3_em.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [meffVR3_em.getSample(sam).addSystematic(leridVR) for sam in BGList]

    meffVR3_mm=bkgOnly.addChannel("meffInc",["VR3mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR3_mm.useOverflowBin = True
    [meffVR3_mm.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffVR3_mm.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffVR3_mm.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffVR3_mm.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [meffVR3_mm.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffVR3_mm.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffVR3_mm.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffVR3_mm.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffVR3_mm.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffVR3_mm.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [meffVR3_mm.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [meffVR3_mm.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [meffVR3_mm.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [meffVR3_mm.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [meffVR3_mm.getSample(sam).addSystematic(leridVR) for sam in BGList]

    nJetVR3_ee=bkgOnly.addChannel("nJet",["VR3ee"],nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
    nJetVR3_ee.useOverflowBin = True
    [nJetVR3_ee.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [nJetVR3_ee.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [nJetVR3_ee.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [nJetVR3_ee.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [nJetVR3_ee.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [nJetVR3_ee.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [nJetVR3_ee.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [nJetVR3_ee.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [nJetVR3_ee.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [nJetVR3_ee.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [nJetVR3_ee.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [nJetVR3_ee.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [nJetVR3_ee.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [nJetVR3_ee.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [nJetVR3_ee.getSample(sam).addSystematic(leridVR) for sam in BGList]

    nJetVR3_em=bkgOnly.addChannel("nJet",["VR3em"],nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
    nJetVR3_em.useOverflowBin = True
    [nJetVR3_em.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [nJetVR3_em.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [nJetVR3_em.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [nJetVR3_em.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [nJetVR3_em.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [nJetVR3_em.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [nJetVR3_em.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [nJetVR3_em.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [nJetVR3_em.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [nJetVR3_em.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [nJetVR3_em.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [nJetVR3_em.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [nJetVR3_em.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [nJetVR3_em.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [nJetVR3_em.getSample(sam).addSystematic(leridVR) for sam in BGList]

    nJetVR3_mm=bkgOnly.addChannel("nJet",["VR3mm"],nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
    nJetVR3_mm.useOverflowBin = True
    [nJetVR3_mm.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [nJetVR3_mm.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [nJetVR3_mm.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [nJetVR3_mm.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [nJetVR3_mm.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [nJetVR3_mm.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [nJetVR3_mm.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [nJetVR3_mm.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [nJetVR3_mm.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [nJetVR3_mm.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [nJetVR3_mm.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [nJetVR3_mm.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [nJetVR3_mm.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [nJetVR3_mm.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [nJetVR3_mm.getSample(sam).addSystematic(leridVR) for sam in BGList]


if doValidationDilepZ:


    ## check impact of kfactor fit on several distributions

    meffVZR4_ee=bkgOnly.addChannel("meffInc",["VZR4ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVZR4_ee.hasB = True
    meffVZR4_ee.hasBQCD = True
    meffVZR4_ee.useOverflowBin = True
    [meffVZR4_ee.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffVZR4_ee.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffVZR4_ee.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffVZR4_ee.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [meffVZR4_ee.getSample(sam).addSystematic(btagVR) for sam in BGList+["QCD"]]
    [meffVZR4_ee.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffVZR4_ee.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffVZR4_ee.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffVZR4_ee.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffVZR4_ee.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffVZR4_ee.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [meffVZR4_ee.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [meffVZR4_ee.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [meffVZR4_ee.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [meffVZR4_ee.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [meffVZR4_ee.getSample(sam).addSystematic(leridVR) for sam in BGList]

    meffVZR4_em=bkgOnly.addChannel("meffInc",["VZR4em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVZR4_em.hasB = True
    meffVZR4_em.hasBQCD = True
    meffVZR4_em.useOverflowBin = True
    [meffVZR4_em.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffVZR4_em.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffVZR4_em.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffVZR4_em.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [meffVZR4_em.getSample(sam).addSystematic(btagVR) for sam in BGList+["QCD"]]
    [meffVZR4_em.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffVZR4_em.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffVZR4_em.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffVZR4_em.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffVZR4_em.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffVZR4_em.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [meffVZR4_em.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [meffVZR4_em.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [meffVZR4_em.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [meffVZR4_em.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [meffVZR4_em.getSample(sam).addSystematic(leridVR) for sam in BGList]

    meffVZR4_mm=bkgOnly.addChannel("meffInc",["VZR4mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVZR4_mm.hasB = True
    meffVZR4_mm.hasBQCD = True
    meffVZR4_mm.useOverflowBin = True
    [meffVZR4_mm.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffVZR4_mm.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffVZR4_mm.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffVZR4_mm.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [meffVZR4_mm.getSample(sam).addSystematic(btagVR) for sam in BGList+["QCD"]]
    [meffVZR4_mm.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffVZR4_mm.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffVZR4_mm.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffVZR4_mm.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffVZR4_mm.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffVZR4_mm.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [meffVZR4_mm.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [meffVZR4_mm.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [meffVZR4_mm.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [meffVZR4_mm.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [meffVZR4_mm.getSample(sam).addSystematic(leridVR) for sam in BGList]

    nJetVZR4_ee=bkgOnly.addChannel("nJet",["VZR4ee"],nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
    nJetVZR4_ee.hasB = True
    nJetVZR4_ee.hasBQCD = True
    nJetVZR4_ee.useOverflowBin = True
    [nJetVZR4_ee.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [nJetVZR4_ee.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [nJetVZR4_ee.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [nJetVZR4_ee.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [nJetVZR4_ee.getSample(sam).addSystematic(btagVR) for sam in BGList+["QCD"]]
    [nJetVZR4_ee.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [nJetVZR4_ee.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [nJetVZR4_ee.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [nJetVZR4_ee.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [nJetVZR4_ee.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [nJetVZR4_ee.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [nJetVZR4_ee.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [nJetVZR4_ee.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [nJetVZR4_ee.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [nJetVZR4_ee.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [nJetVZR4_ee.getSample(sam).addSystematic(leridVR) for sam in BGList]

    nJetVZR4_em=bkgOnly.addChannel("nJet",["VZR4em"],nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
    nJetVZR4_em.hasB = True
    nJetVZR4_em.hasBQCD = True
    nJetVZR4_em.useOverflowBin = True
    [nJetVZR4_em.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [nJetVZR4_em.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [nJetVZR4_em.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [nJetVZR4_em.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [nJetVZR4_em.getSample(sam).addSystematic(btagVR) for sam in BGList+["QCD"]]
    [nJetVZR4_em.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [nJetVZR4_em.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [nJetVZR4_em.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [nJetVZR4_em.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [nJetVZR4_em.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [nJetVZR4_em.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [nJetVZR4_em.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [nJetVZR4_em.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [nJetVZR4_em.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [nJetVZR4_em.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [nJetVZR4_em.getSample(sam).addSystematic(leridVR) for sam in BGList]

    nJetVZR4_mm=bkgOnly.addChannel("nJet",["VZR4mm"],nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
    nJetVZR4_mm.hasB = True
    nJetVZR4_mm.hasBQCD = True
    nJetVZR4_mm.useOverflowBin = True
    [nJetVZR4_mm.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [nJetVZR4_mm.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [nJetVZR4_mm.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [nJetVZR4_mm.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [nJetVZR4_mm.getSample(sam).addSystematic(btagVR) for sam in BGList+["QCD"]]
    [nJetVZR4_mm.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [nJetVZR4_mm.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [nJetVZR4_mm.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [nJetVZR4_mm.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [nJetVZR4_mm.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [nJetVZR4_mm.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [nJetVZR4_mm.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [nJetVZR4_mm.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [nJetVZR4_mm.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [nJetVZR4_mm.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [nJetVZR4_mm.getSample(sam).addSystematic(leridVR) for sam in BGList]

    meffVZR2_ee=bkgOnly.addChannel("meffInc",["VZR2ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVZR2_ee.hasB = True
    meffVZR2_ee.hasBQCD = True
    meffVZR2_ee.useOverflowBin = True
    [meffVZR2_ee.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffVZR2_ee.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffVZR2_ee.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffVZR2_ee.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [meffVZR2_ee.getSample(sam).addSystematic(btagVR) for sam in BGList+["QCD"]]
    [meffVZR2_ee.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffVZR2_ee.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffVZR2_ee.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffVZR2_ee.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffVZR2_ee.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffVZR2_ee.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [meffVZR2_ee.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [meffVZR2_ee.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [meffVZR2_ee.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [meffVZR2_ee.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [meffVZR2_ee.getSample(sam).addSystematic(leridVR) for sam in BGList]

    meffVZR2_em=bkgOnly.addChannel("meffInc",["VZR2em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVZR2_em.hasB = True
    meffVZR2_em.hasBQCD = True
    meffVZR2_em.useOverflowBin = True
    [meffVZR2_em.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffVZR2_em.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffVZR2_em.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffVZR2_em.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [meffVZR2_em.getSample(sam).addSystematic(btagVR) for sam in BGList+["QCD"]]
    [meffVZR2_em.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffVZR2_em.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffVZR2_em.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffVZR2_em.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffVZR2_em.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffVZR2_em.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [meffVZR2_em.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [meffVZR2_em.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [meffVZR2_em.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [meffVZR2_em.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [meffVZR2_em.getSample(sam).addSystematic(leridVR) for sam in BGList]

    meffVZR2_mm=bkgOnly.addChannel("meffInc",["VZR2mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVZR2_mm.hasB = True
    meffVZR2_mm.hasBQCD = True
    meffVZR2_mm.useOverflowBin = True
    [meffVZR2_mm.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffVZR2_mm.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffVZR2_mm.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffVZR2_mm.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [meffVZR2_mm.getSample(sam).addSystematic(btagVR) for sam in BGList+["QCD"]]
    [meffVZR2_mm.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffVZR2_mm.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffVZR2_mm.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffVZR2_mm.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffVZR2_mm.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffVZR2_mm.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [meffVZR2_mm.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [meffVZR2_mm.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [meffVZR2_mm.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [meffVZR2_mm.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [meffVZR2_mm.getSample(sam).addSystematic(leridVR) for sam in BGList]

    nJetVZR2_ee=bkgOnly.addChannel("nJet",["VZR2ee"],nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
    nJetVZR2_ee.hasB = True
    nJetVZR2_ee.hasBQCD = True
    nJetVZR2_ee.useOverflowBin = True
    [nJetVZR2_ee.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [nJetVZR2_ee.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [nJetVZR2_ee.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [nJetVZR2_ee.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [nJetVZR2_ee.getSample(sam).addSystematic(btagVR) for sam in BGList+["QCD"]]
    [nJetVZR2_ee.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [nJetVZR2_ee.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [nJetVZR2_ee.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [nJetVZR2_ee.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [nJetVZR2_ee.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [nJetVZR2_ee.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [nJetVZR2_ee.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [nJetVZR2_ee.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [nJetVZR2_ee.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [nJetVZR2_ee.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [nJetVZR2_ee.getSample(sam).addSystematic(leridVR) for sam in BGList]

    nJetVZR2_em=bkgOnly.addChannel("nJet",["VZR2em"],nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
    nJetVZR2_em.hasB = True
    nJetVZR2_em.hasBQCD = True
    nJetVZR2_em.useOverflowBin = True
    [nJetVZR2_em.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [nJetVZR2_em.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [nJetVZR2_em.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [nJetVZR2_em.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [nJetVZR2_em.getSample(sam).addSystematic(btagVR) for sam in BGList+["QCD"]]
    [nJetVZR2_em.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [nJetVZR2_em.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [nJetVZR2_em.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [nJetVZR2_em.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [nJetVZR2_em.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [nJetVZR2_em.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [nJetVZR2_em.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [nJetVZR2_em.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [nJetVZR2_em.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [nJetVZR2_em.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [nJetVZR2_em.getSample(sam).addSystematic(leridVR) for sam in BGList]

    nJetVZR2_mm=bkgOnly.addChannel("nJet",["VZR2mm"],nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
    nJetVZR2_mm.hasB = True
    nJetVZR2_mm.hasBQCD = True
    nJetVZR2_mm.useOverflowBin = True
    [nJetVZR2_mm.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [nJetVZR2_mm.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [nJetVZR2_mm.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [nJetVZR2_mm.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [nJetVZR2_mm.getSample(sam).addSystematic(btagVR) for sam in BGList+["QCD"]]
    [nJetVZR2_mm.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [nJetVZR2_mm.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [nJetVZR2_mm.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [nJetVZR2_mm.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [nJetVZR2_mm.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [nJetVZR2_mm.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [nJetVZR2_mm.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [nJetVZR2_mm.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [nJetVZR2_mm.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [nJetVZR2_mm.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [nJetVZR2_mm.getSample(sam).addSystematic(leridVR) for sam in BGList]

    meffVZR3_ee=bkgOnly.addChannel("meffInc",["VZR3ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVZR3_ee.hasB = True
    meffVZR3_ee.hasBQCD = True
    meffVZR3_ee.useOverflowBin = True
    [meffVZR3_ee.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffVZR3_ee.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffVZR3_ee.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffVZR3_ee.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [meffVZR3_ee.getSample(sam).addSystematic(btagVR) for sam in BGList+["QCD"]]
    [meffVZR3_ee.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffVZR3_ee.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffVZR3_ee.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffVZR3_ee.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffVZR3_ee.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffVZR3_ee.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [meffVZR3_ee.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [meffVZR3_ee.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [meffVZR3_ee.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [meffVZR3_ee.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [meffVZR3_ee.getSample(sam).addSystematic(leridVR) for sam in BGList]

    meffVZR3_em=bkgOnly.addChannel("meffInc",["VZR3em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVZR3_em.hasB = True
    meffVZR3_em.hasBQCD = True
    meffVZR3_em.useOverflowBin = True
    [meffVZR3_em.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffVZR3_em.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffVZR3_em.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffVZR3_em.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [meffVZR3_em.getSample(sam).addSystematic(btagVR) for sam in BGList+["QCD"]]
    [meffVZR3_em.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffVZR3_em.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffVZR3_em.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffVZR3_em.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffVZR3_em.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffVZR3_em.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [meffVZR3_em.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [meffVZR3_em.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [meffVZR3_em.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [meffVZR3_em.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [meffVZR3_em.getSample(sam).addSystematic(leridVR) for sam in BGList]

    meffVZR3_mm=bkgOnly.addChannel("meffInc",["VZR3mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVZR3_mm.hasB = True
    meffVZR3_mm.hasBQCD = True
    meffVZR3_mm.useOverflowBin = True
    [meffVZR3_mm.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [meffVZR3_mm.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [meffVZR3_mm.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [meffVZR3_mm.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [meffVZR3_mm.getSample(sam).addSystematic(btagVR) for sam in BGList+["QCD"]]
    [meffVZR3_mm.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [meffVZR3_mm.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [meffVZR3_mm.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [meffVZR3_mm.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [meffVZR3_mm.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [meffVZR3_mm.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [meffVZR3_mm.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [meffVZR3_mm.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [meffVZR3_mm.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [meffVZR3_mm.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [meffVZR3_mm.getSample(sam).addSystematic(leridVR) for sam in BGList]

    nJetVZR3_ee=bkgOnly.addChannel("nJet",["VZR3ee"],nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
    nJetVZR3_ee.hasB = True
    nJetVZR3_ee.hasBQCD = True
    nJetVZR3_ee.useOverflowBin = True
    [nJetVZR3_ee.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [nJetVZR3_ee.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [nJetVZR3_ee.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [nJetVZR3_ee.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [nJetVZR3_ee.getSample(sam).addSystematic(btagVR) for sam in BGList+["QCD"]]
    [nJetVZR3_ee.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [nJetVZR3_ee.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [nJetVZR3_ee.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [nJetVZR3_ee.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [nJetVZR3_ee.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [nJetVZR3_ee.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [nJetVZR3_ee.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [nJetVZR3_ee.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [nJetVZR3_ee.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [nJetVZR3_ee.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [nJetVZR3_ee.getSample(sam).addSystematic(leridVR) for sam in BGList]

    nJetVZR3_em=bkgOnly.addChannel("nJet",["VZR3em"],nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
    nJetVZR3_em.hasB = True
    nJetVZR3_em.hasBQCD = True
    nJetVZR3_em.useOverflowBin = True
    [nJetVZR3_em.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [nJetVZR3_em.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [nJetVZR3_em.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [nJetVZR3_em.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [nJetVZR3_em.getSample(sam).addSystematic(btagVR) for sam in BGList+["QCD"]]
    [nJetVZR3_em.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [nJetVZR3_em.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [nJetVZR3_em.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [nJetVZR3_em.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [nJetVZR3_em.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [nJetVZR3_em.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [nJetVZR3_em.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [nJetVZR3_em.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [nJetVZR3_em.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [nJetVZR3_em.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [nJetVZR3_em.getSample(sam).addSystematic(leridVR) for sam in BGList]

    nJetVZR3_mm=bkgOnly.addChannel("nJet",["VZR3mm"],nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
    nJetVZR3_mm.hasB = True
    nJetVZR3_mm.hasBQCD = True
    nJetVZR3_mm.useOverflowBin = True
    [nJetVZR3_mm.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
    [nJetVZR3_mm.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
    [nJetVZR3_mm.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
    [nJetVZR3_mm.getSample(sam).addSystematic(lepVR) for sam in BGList+["QCD"]]
    [nJetVZR3_mm.getSample(sam).addSystematic(btagVR) for sam in BGList+["QCD"]]
    [nJetVZR3_mm.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
    [nJetVZR3_mm.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
    [nJetVZR3_mm.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
    [nJetVZR3_mm.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
    [nJetVZR3_mm.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

    if fullSyst:
        [nJetVZR3_mm.getSample(sam).addSystematic(metcoVR) for sam in BGList+["QCD"]]
        [nJetVZR3_mm.getSample(sam).addSystematic(metpuVR) for sam in BGList+["QCD"]]
        [nJetVZR3_mm.getSample(sam).addSystematic(trigVR) for sam in BGList+["QCD"]]
        [nJetVZR3_mm.getSample(sam).addSystematic(lesVR) for sam in BGList]
        [nJetVZR3_mm.getSample(sam).addSystematic(lermsVR) for sam in BGList]
        [nJetVZR3_mm.getSample(sam).addSystematic(leridVR) for sam in BGList]


if doValidationSR:
    bkgOnly.setValidationChannels([meff2ee,meff4ee,meff2em,meff4em,meff2mm,meff4mm,meffS3_El,meffS3_Mu,meffS4_El,meffS4_Mu,meffS3T_El,meffS3T_Mu,meffS4T_El,meffS4T_Mu,meffS7T_El,meffS7T_Mu])

if doValidationSlope:
    bkgOnly.setValidationChannels([meffTR_El,meffTR_Mu,metTR_El,metTR_Mu,pt1TR_El,pt1TR_Mu,pt2TR_El,pt2TR_Mu,wptWR_El,wptWR_Mu,metWR_El,metWR_Mu,ZptZR_ee,ZptZR_mm,ZptZRY_ee,ZptZRY_mm])

if doValidationDilep:
    bkgOnly.setValidationChannels([meffVR4_ee,meffVR4_em,meffVR4_mm,nJetVR4_ee,nJetVR4_em,nJetVR4_mm,meffVR2_ee,meffVR2_em,meffVR2_mm,nJetVR2_ee,nJetVR2_em,nJetVR2_mm,meffVR3_ee,meffVR3_em,meffVR3_mm,nJetVR3_ee,nJetVR3_em,nJetVR3_mm])

if doValidationDilepZ:
    bkgOnly.setValidationChannels([meffVZR4_ee,meffVZR4_em,meffVZR4_mm,nJetVZR4_ee,nJetVZR4_em,nJetVZR4_mm,meffVZR2_ee,meffVZR2_em,meffVZR2_mm,nJetVZR2_ee,nJetVZR2_em,nJetVZR2_mm,meffVZR3_ee,meffVZR3_em,meffVZR3_mm,nJetVZR3_ee,nJetVZR3_em,nJetVZR3_mm])

#-------------------------------------------------
# Exclusion fit
#-------------------------------------------------

if doExclusion_GMSB_combined or doExclusion_mSUGRA_dilepton_combined or doExclusion_GG_twostepCC_slepton:

        S2Channel_ee = myTopLvl.addChannel("meffInc",["S2ee"],meffNBins,meffBinLow,meffBinHigh)
        S2Channel_ee.useOverflowBin=True
        
        [S2Channel_ee.getSample(sam).addSystematic(lepS2DL) for sam in SigList+BGList+["QCD"]]
        [S2Channel_ee.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
        [S2Channel_ee.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
        [S2Channel_ee.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
        [S2Channel_ee.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
        [S2Channel_ee.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

        if fullSyst:
            [S2Channel_ee.getSample(sam).addSystematic(metcoS2DL) for sam in SigList+BGList+["QCD"]]
            [S2Channel_ee.getSample(sam).addSystematic(metpuS2DL) for sam in SigList+BGList+["QCD"]]
            [S2Channel_ee.getSample(sam).addSystematic(trigS2DL) for sam in SigList+BGList+["QCD"]]
            [S2Channel_ee.getSample(sam).addSystematic(lesS2DL) for sam in SigList+BGList]
            [S2Channel_ee.getSample(sam).addSystematic(lermsS2DL) for sam in SigList+BGList]
            [S2Channel_ee.getSample(sam).addSystematic(leridS2DL) for sam in SigList+BGList]
            [S2Channel_ee.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
            [S2Channel_ee.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
            [S2Channel_ee.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
            
        S2Channel_em = myTopLvl.addChannel("meffInc",["S2em"],meffNBins,meffBinLow,meffBinHigh)
        S2Channel_em.useOverflowBin=True

        [S2Channel_em.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
        [S2Channel_em.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
        [S2Channel_em.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
        [S2Channel_em.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
        [S2Channel_em.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

        [S2Channel_em.getSample(sam).addSystematic(lepS2DL) for sam in SigList+BGList+["QCD"]]
        if fullSyst:
            [S2Channel_em.getSample(sam).addSystematic(metcoS2DL) for sam in SigList+BGList+["QCD"]]
            [S2Channel_em.getSample(sam).addSystematic(metpuS2DL) for sam in SigList+BGList+["QCD"]]
            [S2Channel_em.getSample(sam).addSystematic(trigS2DL) for sam in SigList+BGList+["QCD"]]
            [S2Channel_em.getSample(sam).addSystematic(lesS2DL) for sam in SigList+BGList]
            [S2Channel_em.getSample(sam).addSystematic(lermsS2DL) for sam in SigList+BGList]
            [S2Channel_em.getSample(sam).addSystematic(leridS2DL) for sam in SigList+BGList]
            [S2Channel_em.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
            [S2Channel_em.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
            [S2Channel_em.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]

        S2Channel_mm = myTopLvl.addChannel("meffInc",["S2mm"],meffNBins,meffBinLow,meffBinHigh)
        S2Channel_mm.useOverflowBin=True

        [S2Channel_mm.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
        [S2Channel_mm.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
        [S2Channel_mm.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
        [S2Channel_mm.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
        [S2Channel_mm.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]
        
        [S2Channel_mm.getSample(sam).addSystematic(lepS4DL) for sam in SigList+BGList+["QCD"]]
        if fullSyst:
            [S2Channel_mm.getSample(sam).addSystematic(metcoS2DL) for sam in SigList+BGList+["QCD"]]
            [S2Channel_mm.getSample(sam).addSystematic(metpuS2DL) for sam in SigList+BGList+["QCD"]]
            [S2Channel_mm.getSample(sam).addSystematic(trigS2DL) for sam in SigList+BGList+["QCD"]]
            [S2Channel_mm.getSample(sam).addSystematic(lesS2DL) for sam in SigList+BGList]
            [S2Channel_mm.getSample(sam).addSystematic(lermsS2DL) for sam in SigList+BGList]
            [S2Channel_mm.getSample(sam).addSystematic(leridS2DL) for sam in SigList+BGList]
            [S2Channel_mm.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
            [S2Channel_mm.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
            [S2Channel_mm.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]


    
        S4Channel_ee = myTopLvl.addChannel("meffInc",["S4ee"],meffNBins,meffBinLow,meffBinHigh)
        S4Channel_ee.useOverflowBin=True
        
        [S4Channel_ee.getSample(sam).addSystematic(lepS4DL) for sam in SigList+BGList+["QCD"]]
        [S4Channel_ee.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
        [S4Channel_ee.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
        [S4Channel_ee.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
        [S4Channel_ee.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
        [S4Channel_ee.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

        if fullSyst:
            [S4Channel_ee.getSample(sam).addSystematic(metcoS4DL) for sam in SigList+BGList+["QCD"]]
            [S4Channel_ee.getSample(sam).addSystematic(metpuS4DL) for sam in SigList+BGList+["QCD"]]
            [S4Channel_ee.getSample(sam).addSystematic(trigS4DL) for sam in SigList+BGList+["QCD"]]
            [S4Channel_ee.getSample(sam).addSystematic(lesS4DL) for sam in SigList+BGList]
            [S4Channel_ee.getSample(sam).addSystematic(lermsS4DL) for sam in SigList+BGList]
            [S4Channel_ee.getSample(sam).addSystematic(leridS4DL) for sam in SigList+BGList]
            [S4Channel_ee.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
            [S4Channel_ee.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
            [S4Channel_ee.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]
            
        S4Channel_em = myTopLvl.addChannel("meffInc",["S4em"],meffNBins,meffBinLow,meffBinHigh)
        S4Channel_em.useOverflowBin=True

        [S4Channel_em.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
        [S4Channel_em.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
        [S4Channel_em.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
        [S4Channel_em.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
        [S4Channel_em.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]

        [S4Channel_em.getSample(sam).addSystematic(lepS4DL) for sam in SigList+BGList+["QCD"]]
        if fullSyst:
            [S4Channel_em.getSample(sam).addSystematic(metcoS4DL) for sam in SigList+BGList+["QCD"]]
            [S4Channel_em.getSample(sam).addSystematic(metpuS4DL) for sam in SigList+BGList+["QCD"]]
            [S4Channel_em.getSample(sam).addSystematic(trigS4DL) for sam in SigList+BGList+["QCD"]]
            [S4Channel_em.getSample(sam).addSystematic(lesS4DL) for sam in SigList+BGList]
            [S4Channel_em.getSample(sam).addSystematic(lermsS4DL) for sam in SigList+BGList]
            [S4Channel_em.getSample(sam).addSystematic(leridS4DL) for sam in SigList+BGList]
            [S4Channel_em.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
            [S4Channel_em.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
            [S4Channel_em.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]

        S4Channel_mm = myTopLvl.addChannel("meffInc",["S4mm"],meffNBins,meffBinLow,meffBinHigh)
        S4Channel_mm.useOverflowBin=True

        [S4Channel_mm.getSample(sam).addSystematic(zpT0GeV) for sam in BGList+["QCD"]]
        [S4Channel_mm.getSample(sam).addSystematic(zpT50GeV) for sam in BGList+["QCD"]]
        [S4Channel_mm.getSample(sam).addSystematic(zpT100GeV) for sam in BGList+["QCD"]]
        [S4Channel_mm.getSample(sam).addSystematic(zpT150GeV) for sam in BGList+["QCD"]]
        [S4Channel_mm.getSample(sam).addSystematic(zpT200GeV) for sam in BGList+["QCD"]]
        
        [S4Channel_mm.getSample(sam).addSystematic(lepS4DL) for sam in SigList+BGList+["QCD"]]
        if fullSyst:
            [S4Channel_mm.getSample(sam).addSystematic(metcoS4DL) for sam in SigList+BGList+["QCD"]]
            [S4Channel_mm.getSample(sam).addSystematic(metpuS4DL) for sam in SigList+BGList+["QCD"]]
            [S4Channel_mm.getSample(sam).addSystematic(trigS4DL) for sam in SigList+BGList+["QCD"]]
            [S4Channel_mm.getSample(sam).addSystematic(lesS4DL) for sam in SigList+BGList]
            [S4Channel_mm.getSample(sam).addSystematic(lermsS4DL) for sam in SigList+BGList]
            [S4Channel_mm.getSample(sam).addSystematic(leridS4DL) for sam in SigList+BGList]
            [S4Channel_mm.getSample(sam).addSystematic(jesLow) for sam in BGList+["QCD"]]
            [S4Channel_mm.getSample(sam).addSystematic(jesMedium) for sam in BGList+["QCD"]]
            [S4Channel_mm.getSample(sam).addSystematic(jesHigh) for sam in BGList+["QCD"]]

        # Add signal jes systematics for signal to all channels:
        for channel in myTopLvl.channels:
            [channel.getSample(sam).addSystematic(jesSignal) for sam in SigList]


        ## Which SRs for which Scenario?

        if doExclusion_GMSB_combined:
            myTopLvl.setSignalChannels([S2Channel_ee,S2Channel_em,S2Channel_mm])       
        elif doExclusion_mSUGRA_dilepton_combined:
            myTopLvl.setSignalChannels([S2Channel_ee,S2Channel_em,S2Channel_mm,S4Channel_ee,S4Channel_em,S4Channel_mm])
        ## Which SRs for SM???
        elif doExclusion_GG_twostepCC_slepton:
            myTopLvl.setSignalChannels([S4Channel_ee,S4Channel_em,S4Channel_mm])


#  LocalWords:  fullSyst
