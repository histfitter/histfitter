
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
debugSyst=False
doHardLep=True
doSoftLep=False
useStat=True
doValidation=False
doValidationSR=True
doValidationSlope=False
doValidationDilep=False
doValidationDilepZ=False
doValidationSoftLep=True
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

if not 'sigSamples' in dir():
    sigSamples=["SU_580_240_0_10_P"]
# sigSamples=["GMSB_3_2d_50_250_3_10_1_1"]

#sigSamples=[]


#doExclusion=True
blindS=False
fullSyst=True
useXsecUnc=True             # switch off when calucating excluded cross section (colour code in SM plots)
doWptReweighting=False ## currently buggy

# First define HistFactory attributes
configMgr.analysisName = "Combined_KFactorFit_5Channel_SHORT" # Name to give the analysis
configMgr.outputFileName = "results/Combined_KFactorFit_5Channel_SHORT.root"

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
configMgr.cutsDict = {}
configMgr.cutsDict["TRee"]="(mll<80 || mll>100) && met > 30 && met < 80 && jet2Pt > 50 && nB3Jet > 0 && AnalysisType==3"
configMgr.cutsDict["TRmm"]="(mll<80 || mll>100) && met > 30 && met < 80 && jet2Pt > 50 && nB3Jet > 0 && AnalysisType==4"
configMgr.cutsDict["TRem"]="(mll<80 || mll>100) && met > 30 && met < 80 && jet2Pt > 50 && nB3Jet > 0 && AnalysisType==5"
configMgr.cutsDict["ZRee"]="mll>80 && mll<100  && met < 50 && jet2Pt > 50 && AnalysisType==3"
configMgr.cutsDict["ZRmm"]="mll>80 && mll<100  && met < 50 && jet2Pt > 50 && AnalysisType==4"

configMgr.cutsDict["S2ee"]="met > 300 && nJet>=2 && jet2Pt > 200 && jet4Pt < 50 && AnalysisType==3"
configMgr.cutsDict["S2mm"]="met > 300 && nJet>=2 && jet2Pt > 200 && jet4Pt < 50 && AnalysisType==4"
configMgr.cutsDict["S2em"]="met > 300 && nJet>=2 && jet2Pt > 200 && jet4Pt < 50 && AnalysisType==5"
configMgr.cutsDict["S4ee"]="met > 100 && nJet>=4 && jet4Pt > 50 && met/meff4Jet > 0.2 && meffInc > 650 && AnalysisType==3"
configMgr.cutsDict["S4mm"]="met > 100 && nJet>=4 && jet4Pt > 50 && met/meff4Jet > 0.2 && meffInc > 650 && AnalysisType==4"
configMgr.cutsDict["S4em"]="met > 100 && nJet>=4 && jet4Pt > 50 && met/meff4Jet > 0.2 && meffInc > 650 && AnalysisType==5"

configMgr.cutsDict["VR2ee"]="met > 100 && met < 300 && jet4Pt < 50 && jet2Pt > 50 && AnalysisType==3"
configMgr.cutsDict["VR2em"]="met > 100 && met < 300 && jet4Pt < 50 && jet2Pt > 50 && AnalysisType==5"
configMgr.cutsDict["VR2mm"]="met > 100 && met < 300 && jet4Pt < 50 && jet2Pt > 50 && AnalysisType==4"

configMgr.cutsDict["VR3ee"]="met > 100 && met < 300 && jet4Pt < 50 && jet3Pt > 50 && AnalysisType==3"
configMgr.cutsDict["VR3em"]="met > 100 && met < 300 && jet4Pt < 50 && jet3Pt > 50 && AnalysisType==5"
configMgr.cutsDict["VR3mm"]="met > 100 && met < 300 && jet4Pt < 50 && jet3Pt > 50 && AnalysisType==4"

configMgr.cutsDict["VR4ee"]="met < 100 && jet4Pt > 50 && AnalysisType==3"
configMgr.cutsDict["VR4em"]="met < 100 && jet4Pt > 50  && AnalysisType==5"
configMgr.cutsDict["VR4mm"]="met < 100  && jet4Pt > 50 && AnalysisType==4"

configMgr.cutsDict["VZR2ee"]="met > 50 && met < 100 && jet2Pt > 50 && nB3Jet == 0 && AnalysisType==3"
configMgr.cutsDict["VZR2em"]="met > 50 && met < 100 && jet2Pt > 50 && nB3Jet == 0 && AnalysisType==5"                    
configMgr.cutsDict["VZR2mm"]="met > 50 && met < 100 && jet2Pt > 50 && nB3Jet == 0 && AnalysisType==4"

configMgr.cutsDict["VZR3ee"]="met > 50 && met < 100  && jet3Pt > 50 && nB3Jet == 0 && AnalysisType==3"
configMgr.cutsDict["VZR3em"]="met > 50 && met < 100 && jet3Pt > 50 && nB3Jet == 0 && AnalysisType==5"
configMgr.cutsDict["VZR3mm"]="met > 50 && met < 100 && jet3Pt > 50 && nB3Jet == 0 && AnalysisType==4"

configMgr.cutsDict["VZR4ee"]="met > 50 && met < 100 & jet4Pt > 50  && nB3Jet == 0 && AnalysisType==3"
configMgr.cutsDict["VZR4em"]="met > 50 && met < 100 & jet4Pt > 50 && nB3Jet == 0 && AnalysisType==5"
configMgr.cutsDict["VZR4mm"]="met > 50 && met < 100 & jet4Pt > 50  && nB3Jet == 0 && AnalysisType==4"

configMgr.cutsDict["HMTVL1El"]="AnalysisType==1 && met>30 && met<250 && mt>80 && jet1Pt>80 && jet3Pt>25 && meffInc>400"
configMgr.cutsDict["HMTVL1Mu"]="AnalysisType==2 && met>30 && met<250 && mt>80 && jet1Pt>80 && jet3Pt>25 && meffInc>400"
                      
configMgr.cutsDict["WREl"]="lep2Pt<10 && met>40 && met<150 && mt>40 && mt<80 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc > 500 && AnalysisType==1"
configMgr.cutsDict["TREl"]="lep2Pt<10 && met>40 && met<150 && mt>40 && mt<80 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && meffInc > 500 && AnalysisType==1"
configMgr.cutsDict["WRMu"]="lep2Pt<10 && met>40 && met<150 && mt>40 && mt<80 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc > 500 && AnalysisType==2"
configMgr.cutsDict["TRMu"]="lep2Pt<10 && met>40 && met<150 && mt>40 && mt<80 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && meffInc > 500 && AnalysisType==2"

configMgr.cutsDict["TRElVR"]="lep2Pt<10 && met>40 && met<150 && mt>40 && mt<80 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==1"
configMgr.cutsDict["TRMuVR"]="lep2Pt<10 && met>40 && met<150 && mt>40 && mt<80 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==2"

configMgr.cutsDict["TRElVR2"]="lep2Pt<10 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==1"
configMgr.cutsDict["TRMuVR2"]="lep2Pt<10 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==2" 

configMgr.cutsDict["WRElVR"]="lep2Pt<10 && met>50 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==1"
configMgr.cutsDict["WRMuVR"]="lep2Pt<10 && met>50 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==2"

configMgr.cutsDict["S3El"]="AnalysisType==1 && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25 && jet4Pt<80"
configMgr.cutsDict["S4El"]="AnalysisType==1 && met>250 && mt>100 && met/meff4Jet>0.2 && jet4Pt>80"

configMgr.cutsDict["S3Mu"]="AnalysisType==2 && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25 && jet4Pt<80"
configMgr.cutsDict["S4Mu"]="AnalysisType==2 && met>250 && mt>100 && met/meff4Jet>0.2 && jet4Pt>80"

configMgr.cutsDict["SR3jTEl"]="AnalysisType==1 && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25 && jet4Pt<80 && meffInc>1200"
configMgr.cutsDict["SR4jTEl"]="AnalysisType==1 && met>250 && mt>100 && met/meff4Jet>0.2 && jet4Pt>80 && meffInc>800"

configMgr.cutsDict["SR3jTMu"]="AnalysisType==2 && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25 && jet4Pt<80 && meffInc>1200"
configMgr.cutsDict["SR4jTMu"]="AnalysisType==2 && met>250 && mt>100 && met/meff4Jet>0.2 && jet4Pt>80 && meffInc>800"
configMgr.cutsDict["SR7jTEl"]="AnalysisType==1 && met>180 && mt>120 && jet1Pt>80 && jet7Pt>25 && meffInc>750"
configMgr.cutsDict["SR7jTMu"]="AnalysisType==2 && met>180 && mt>120 && jet1Pt>80 && jet7Pt>25 && meffInc>750"

configMgr.cutsDict["SVEl"]="(lep1Pt<25 && lep2Pt<10 && met>180 && met<250 && mt>80 && mt<100 && jet1Pt>130 && jet2Pt>25 && AnalysisType==6)"
configMgr.cutsDict["SVMu"]="(lep1Pt<20 && lep2Pt<10 && met>180 && met<250 && mt>80 && mt<100 && jet1Pt>130 && jet2Pt>25 && AnalysisType==7)"

configMgr.cutsDict["SVWEl"]="lep1Pt<25 && lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB2Jet==0 && jet1Pt>130 && jet2Pt>25 && AnalysisType==6"
configMgr.cutsDict["SVTEl"]="lep1Pt<25 && lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB2Jet>0 && jet1Pt>130 && jet2Pt>25 && AnalysisType==6"
configMgr.cutsDict["SVWMu"]="lep1Pt<20 && lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB2Jet==0 && jet1Pt>130 && jet2Pt>25 && AnalysisType==7"
configMgr.cutsDict["SVTMu"]="lep1Pt<20 && lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB2Jet>0 && jet1Pt>130 && jet2Pt>25 && AnalysisType==7"

configMgr.cutsDict["SSEl"]="lep1Pt < 25 && lep2Pt<10 && met>250 && mt>100 && jet1Pt>130 && jet2Pt>25 && AnalysisType==6"
configMgr.cutsDict["SSMu"]="lep1Pt < 20 && lep2Pt<10 && met>250 && mt>100 && jet1Pt>130 && jet2Pt>25 && AnalysisType==7"

d=configMgr.cutsDict
configMgr.cutsDict["SS2jElT"] = d["SSEl"]+"&& met/meff2Jet>0.3"
configMgr.cutsDict["SS2jMuT"] = d["SSMu"]+"&& met/meff2Jet>0.3"


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
configMgr.nomName = "_NoSys"

# Signal XSec uncertainty as overallSys (pure yeild affect)
xsecSig = Systematic("XSS",configMgr.weights,xsecSigHighWeights,xsecSigLowWeights,"weight","overallSys")

# JES uncertainty as shapeSys - one systematic per region (combine WR and TR), merge samples
jesSignal = Systematic("JSig","_NoSys","_JESup","_JESdown","tree","histoSys")

basicChanSyst = []
basicChanSyst.append(Systematic("JLow","_NoSys","_JESLowup","_JESLowdown","tree","histoSys")) # JES uncertainty - for low pt jets
basicChanSyst.append(Systematic("JMedium","_NoSys","_JESMediumup","_JESMediumdown","tree","histoSys")) # JES uncertainty - for medium pt jets
basicChanSyst.append(Systematic("JHigh","_NoSys","_JESHighup","_JESHighdown","tree","histoSys")) # JES uncertainty - for high pt jets
basicChanSyst.append(Systematic("MC","_NoSys","_METCOup","_METCOdown","tree","overallSys")) # MET cell-out uncertainty - one per channel
             

fullChanSyst = []
fullChanSyst.append(Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")) # Lepton weight uncertainty
fullChanSyst.append(Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")) # MET pileup uncertainty - one per channel
fullChanSyst.append(Systematic("TE",configMgr.weights,trigHighWeights,trigLowWeights,"weight","overallSys")) # Trigger weight uncertainty
fullChanSyst.append(Systematic("LES","_NoSys","_LESup","_LESdown","tree","overallSys")) # LES uncertainty - one per channel
fullChanSyst.append(Systematic("LRM","_NoSys","_LERMSup","_LERMSdown","tree","overallSys")) # LER with muon system - one per channel
fullChanSyst.append(Systematic("LRI","_NoSys","_LERIDup","_LERIDdown","tree","overallSys")) # LER with inner detector - one per channel

btagChanSyst = [Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","overallSys")]


# List of samples and their plotting colours
AlpGenSamples=[]
topSample_Np0 = Sample("Top_Np0",100)
topSample_Np0.setNormFactor("mu_Top_Np0",1.,0.,5.)
AlpGenSamples.append(topSample_Np0)
wzSample_Np0 = Sample("WZ_Np0",55)
wzSample_Np0.setNormFactor("mu_WZ_Np0",1.,0.,5.)
AlpGenSamples.append(wzSample_Np0)
topSample_Np1 = Sample("Top_Np1",97)
topSample_Np1.setNormFactor("mu_Top_Np1",1.,0.,5.)
AlpGenSamples.append(topSample_Np1)
wzSample_Np1 = Sample("WZ_Np1",58)
wzSample_Np1.setNormFactor("mu_WZ_Np1",1.,0.,5.)
AlpGenSamples.append(wzSample_Np1)
topSample_Np2 = Sample("Top_Np2",94)
topSample_Np2.setNormFactor("mu_Top_Np2",1.,0.,5.)
AlpGenSamples.append(topSample_Np2)
wzSample_Np2 = Sample("WZ_Np2",61)
wzSample_Np2.setNormFactor("mu_WZ_Np2",1.,0.,5.)
AlpGenSamples.append(wzSample_Np2)
topSample_Np3 = Sample("Top_Np3",91)
topSample_Np3.setNormFactor("mu_Top_Np3",1.,0.,5.)
AlpGenSamples.append(topSample_Np3)
wzSample_Np3 = Sample("WZ_Np3",64)
wzSample_Np3.setNormFactor("mu_WZ_Np3",1.,0.,5.)
AlpGenSamples.append(wzSample_Np3)
topSample_Np4 = Sample("Top_Np4",91)
topSample_Np4.setNormFactor("mu_Top_Np3",1.,0.,5.)
AlpGenSamples.append(topSample_Np4)
wzSample_Np4 = Sample("WZ_Np4",67)
wzSample_Np4.setNormFactor("mu_WZ_Np4",1.,0.,5.)
AlpGenSamples.append(wzSample_Np4)
topSample_Np5 = Sample("Top_Np5",91)
topSample_Np5.setNormFactor("mu_Top_Np3",1.,0.,5.)
AlpGenSamples.append(topSample_Np5) 
wzSample_Np5 = Sample("WZ_Np5",70)
wzSample_Np5.setNormFactor("mu_WZ_Np5",1.,0.,5.)
AlpGenSamples.append(wzSample_Np5)

for sam in AlpGenSamples:
    sam.setStatConfig(useStat)
    sam.addSystematic(Systematic("Zpt50GeV",configMgr.weights,pT50GeVHighWeights,pT50GeVLowWeights,"weight","overallSys"))
    sam.addSystematic(Systematic("Zpt100GeV",configMgr.weights,pT100GeVHighWeights,pT100GeVLowWeights,"weight","overallSys"))
    sam.addSystematic(Systematic("Zpt150GeV",configMgr.weights,pT150GeVHighWeights,pT150GeVLowWeights,"weight","overallSys"))
    sam.addSystematic(Systematic("Zpt200GeV",configMgr.weights,pT200GeVHighWeights,pT200GeVLowWeights,"weight","overallSys"))

### Additional scale uncertainty on WZ Np0 and WZ Np1
wzSample_Np0.addSystematic(Systematic("err_WZ_Np0", configMgr.weights,1.06 ,0.96, "user","userOverallSys"))
wzSample_Np1.addSystematic(Systematic("err_WZ_Np1", configMgr.weights,1.06 ,0.83, "user","userOverallSys"))

### Additional uncertainty on the V+HF samples
hf = Systematic("HF",configMgr.weights,hfHighWeights,hfLowWeights,"weight","histoSys")
wzSample_Np0.addSystematic(hf)
wzSample_Np1.addSystematic(hf)
wzSample_Np2.addSystematic(hf)
wzSample_Np3.addSystematic(hf)
wzSample_Np4.addSystematic(hf)


bgSample = Sample("BG",kGreen)
bgSample.setStatConfig(useStat)
### Additional uncertainty on BG
bgSample.addSystematic(Systematic("err_BG", configMgr.weights,1.2 ,0.8, "user","userOverallSys"))

qcdSample = Sample("QCD",kGray+1)
qcdSample.setQCD(True,"histoSys")
qcdSample.setStatConfig(useStat)
dataSample = Sample("Data",kBlack)
dataSample.setData()

# nJet Binning for Top Control region
nJetTopeeNBins = 8
nJetTopeeBinLow = 2
nJetTopeeBinHigh = 10

nJetTopeNBins = 8
nJetTopeBinLow = 3
nJetTopeBinHigh = 10

nJetTopemNBins = 8
nJetTopemBinLow = 2
nJetTopemBinHigh = 10

nJetTopmmNBins = 8
nJetTopmmBinLow = 2
nJetTopmmBinHigh = 10

nJetTopmNBins = 8
nJetTopmBinLow = 3
nJetTopmBinHigh = 10

# nJet Binning for W Control region
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

                
bgdsamples=[qcdSample,bgSample,dataSample]
for sam in AlpGenSamples:
    bgdsamples.append(sam)

if doSignalOnly:
    bgdsamples=[]

for sam in bgdsamples:
    sam.setFileList(bgdFiles)


#Create TopLevelXML objects
bkgOnly = configMgr.addTopLevelXML("bkgonly")
bkgOnly.addSamples(bgdsamples)
if useStat:
    bkgOnly.statErrThreshold=0.05 
else:
    bkgOnly.statErrThreshold=None


#Add Measurement
meas=bkgOnly.addMeasurement("BasicMeasurement",lumi=1.0,lumiErr=0.037)
meas.addPOI("mu_SIG")

# Fix Background 
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
nJetTopeeChannel=bkgOnly.addChannel("nJet",["TRee"],nJetTopeeNBins,nJetTopeeBinLow,nJetTopeeBinHigh)
#  single ele
nJetTopeChannel=bkgOnly.addChannel("nJet",["TREl"],nJetTopeNBins,nJetTopeBinLow,nJetTopeBinHigh)
#  ele mu
nJetTopemChannel=bkgOnly.addChannel("nJet",["TRem"],nJetTopemNBins,nJetTopemBinLow,nJetTopemBinHigh)
# mu mu
nJetTopmmChannel=bkgOnly.addChannel("nJet",["TRmm"],nJetTopmmNBins,nJetTopmmBinLow,nJetTopmmBinHigh)
# single mu
nJetTopmChannel=bkgOnly.addChannel("nJet",["TRMu"],nJetTopmNBins,nJetTopmBinLow,nJetTopmBinHigh)

topChannels = [nJetTopeeChannel, nJetTopeChannel, nJetTopemChannel,nJetTopmmChannel,nJetTopmChannel]

# add systematics
for chan in topChannels:
    chan.hasB = True
    chan.hasBQCD = True
    chan.useOverflowBin = False
    for syst in basicChanSyst + btagChanSyst:
        chan.addSystematic(syst)
        if debugSyst:
            print " channel = ", chan.name, " adding systematic = ", syst.name
    # only additional Full Systematics
    if fullSyst:
        for syst in fullChanSyst:
            chan.addSystematic(syst)
            if debugSyst:
                print " channel = ", chan.name, " adding Full systematic = ", syst.name
                
        
####### nJet for W/Z  #######
    
# ele ele    
nJetZeeChannel=bkgOnly.addChannel("nJet",nJetZeeRegions,nJetZeeNBins,nJetZeeBinLow,nJetZeeBinHigh)
nJetZeeChannel.hasB = False
nJetZeeChannel.hasBQCD = False
# single ele
nJetZeChannel=bkgOnly.addChannel("nJet",nJetZeRegions,nJetZeNBins,nJetZeBinLow,nJetZeBinHigh)
nJetZeChannel.hasB = True
nJetZeChannel.hasBQCD = False
[nJetZeChannel.addSystematic(syst) for syst in btagChanSyst]
# mu mu
nJetZmmChannel=bkgOnly.addChannel("nJet",nJetZmmRegions,nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
nJetZmmChannel.hasB = False
nJetZmmChannel.hasBQCD = False
# single mu
nJetZmChannel=bkgOnly.addChannel("nJet",nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
nJetZmChannel.hasB = True
nJetZmChannel.hasBQCD = False
[nJetZmChannel.addSystematic(syst) for syst in btagChanSyst]
                                                               
WZChannels = [nJetZeeChannel, nJetZeChannel, nJetZmmChannel, nJetZmChannel]

# add systematics
for chan in WZChannels:
    chan.useOverflowBin = False
    for syst in basicChanSyst:
        chan.addSystematic(syst)
        if debugSyst:
            print " channel = ", chan.name, " adding systematic = ", syst.name
    # only additional Full Systematics
    if fullSyst:
        for syst in fullChanSyst:
            chan.addSystematic(syst)
            if debugSyst:
                print " channel = ", chan.name, " adding Full systematic = ", syst.name
                
        
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
    # check impact of kfactor fit on several distributions
    #TR
    meffTR_El=bkgOnly.addChannel("meffInc",["TRElVR"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    metTR_El=bkgOnly.addChannel("met",["TRElVR2"],metNBinsTR,metBinLowTR,metBinHighTR)
    metTR_Mu=bkgOnly.addChannel("met",["TRMuVR2"],metNBinsTR,metBinLowTR,metBinHighTR)
    pt1TR_El=bkgOnly.addChannel("jet1Pt",["TRElVR"],pt1NBinsTR,pt1BinLowTR,pt1BinHighTR)
    pt1TR_Mu=bkgOnly.addChannel("jet1Pt",["TRMuVR"],pt1NBinsTR,pt1BinLowTR,pt1BinHighTR)
    pt2TR_El=bkgOnly.addChannel("jet2Pt",["TRElVR"],pt2NBinsTR,pt2BinLowTR,pt2BinHighTR)
    pt2TR_Mu=bkgOnly.addChannel("jet2Pt",["TRMuVR"],pt2NBinsTR,pt2BinLowTR,pt2BinHighTR)
    
    validationSlopeTRChannels = [meffTR_El, meffTR_Mu, metTR_El, metTR_Mu, pt1TR_El , pt1TR_Mu , pt2TR_El , pt2TR_Mu]
    
    # add systematics
    for chan in validationSlopeTRChannels:
        chan.hasB = True
        chan.hasBQCD = True
        chan.useOverflowBin = True
        for syst in commonChanSyst + commonSamSyst + btagChanSyst:
            chan.addSystematic(syst)
            if debugSyst:
                print " channel = ", chan.name, " adding systematic = ", syst.name
        # only additional Full Systematics
        if fullSyst:
            for syst in fullChanSyst + fullSamSyst:
                chan.addSystematic(syst)
                if debugSyst:
                    print " channel = ", chan.name, " adding Full systematic = ", syst.name             
                    
    # WR
    wptWR_El=bkgOnly.addChannel("Wpt",["WRElVR"],metNBinsTR,metBinLowTR,metBinHighTR)
    wptWR_Mu=bkgOnly.addChannel("Wpt",["WRMuVR"],metNBinsTR,metBinLowTR,metBinHighTR)
    metWR_El=bkgOnly.addChannel("met",["WRElVR"],metNBinsTR,metBinLowTR,metBinHighTR)
    metWR_Mu=bkgOnly.addChannel("met",["WRMuVR"],metNBinsTR,metBinLowTR,metBinHighTR)
    
    validationSlopeWRChannels = [wptWR_El, wptWR_Mu, metWR_El, metWR_Mu]
    
    # add systematics
    for chan in validationSlopeWRChannels:
        chan.hasB = True
        chan.hasBQCD = False
        chan.useOverflowBin = True
        for syst in commonChanSyst + commonSamSyst + btagChanSyst:
            chan.addSystematic(syst)
            if debugSyst:
                print " channel = ", chan.name, " adding systematic = ", syst.name
        # only additional Full Systematics
        if fullSyst:
            for syst in fullChanSyst + fullSamSyst:
                chan.addSystematic(syst)
                if debugSyst:
                    print " channel = ", chan.name, " adding Full systematic = ", syst.name             

    #ZR
    ZptZR_ee=bkgOnly.addChannel("Zpt",["ZRee"],metNBinsTR,metBinLowTR,metBinHighTR)
    ZptZR_mm=bkgOnly.addChannel("Zpt",["ZRmm"],metNBinsTR,metBinLowTR,metBinHighTR)
    
    validationSlopeWRChannels = [ZptZR_ee, ZptZR_mm]
    
    # add systematics
    for chan in validationSlopeZRChannels:
        chan.hasB = False
        chan.hasBQCD = False
        chan.useOverflowBin = True
        for syst in commonChanSyst + commonSamSyst:
            chan.addSystematic(syst)
            if debugSyst:
                print " channel = ", chan.name, " adding systematic = ", syst.name
        # only additional Full Systematics
        if fullSyst:
            for syst in fullChanSyst + fullSamSyst:
                chan.addSystematic(syst)
                if debugSyst:
                    print " channel = ", chan.name, " adding Full systematic = ", syst.name             

if doValidationSR:
    # S2 using meff
    meff2ee = bkgOnly.addChannel("meffInc",["S2ee"],meffNBinsS2,meffBinLowS2,meffBinHighS2)
    # S4 using meff
    meff4ee = bkgOnly.addChannel("meffInc",["S4ee"],meffNBinsS4,meffBinLowS4,meffBinHighS4)
    # S2 using meff
    meff2em = bkgOnly.addChannel("meffInc",["S2em"],meffNBinsS2,meffBinLowS2,meffBinHighS2)
    # S4 using meff
    meff4em = bkgOnly.addChannel("meffInc",["S4em"],meffNBinsS4,meffBinLowS4,meffBinHighS4)
    # S2 using meff
    meff2mm = bkgOnly.addChannel("meffInc",["S2mm"],meffNBinsS2,meffBinLowS2,meffBinHighS2)
    # S4 using meff
    meff4mm = bkgOnly.addChannel("meffInc",["S4mm"],meffNBinsS4,meffBinLowS4,meffBinHighS4)
    # HARD LEPTON SRS
    meffS3_El=bkgOnly.addChannel("meffInc",["S3El"],meffNBinsHL,meffBinLowHL,meffBinHighHL)
    meffS3_Mu=bkgOnly.addChannel("meffInc",["S3Mu"],meffNBinsHL,meffBinLowHL,meffBinHighHL)
    meffS4_El=bkgOnly.addChannel("meffInc",["S4El"],meffNBinsHL,meffBinLowHL,meffBinHighHL)
    meffS4_Mu=bkgOnly.addChannel("meffInc",["S4Mu"],meffNBinsHL,meffBinLowHL,meffBinHighHL)
    meffS3T_El=bkgOnly.addChannel("meffInc",["SR3jTEl"],1,1200,meffBinHighHL)
    meffS3T_Mu=bkgOnly.addChannel("meffInc",["SR3jTMu"],1,1200,meffBinHighHL)
    meffS4T_El=bkgOnly.addChannel("meffInc",["SR4jTEl"],1,800,meffBinHighHL)
    meffS4T_Mu=bkgOnly.addChannel("meffInc",["SR4jTMu"],1,800,meffBinHighHL)
    # SOFT LEPTON SRS
    mmSSEl = bkt.addChannel("met/meff2Jet",["SSEl"],6,0.1,0.7)
    mmSSMu = bkt.addChannel("met/meff2Jet",["SSMu"],6,0.1,0.7)
    mmSSElT = bkt.addChannel("met/meff2Jet",["SSElT"],4,0.3,0.7)
    mmSSMuT = bkt.addChannel("met/meff2Jet",["SSMuT"],4,0.3,0.7)

    validationSRChannels = [meff2ee, meff4ee, meff2em, meff4em, meff2mm, meff4mm, meffS3_El, meffS3_Mu, meffS4_El, meffS4_Mu, meffS3T_El, meffS3T_Mu, meffS4T_El, meffS4T_Mu, mmSSEl, mmSSMu, mmSSElT, mmSSMuT]                                                    
    # add systematics
    for chan in validationSRChannels:
        chan.useOverflowBin = True
        for syst in commonChanSyst + commonSamSyst:
            chan.addSystematic(syst)
            if debugSyst:
                print " channel = ", chan.name, " adding systematic = ", syst.name
        # only additional Full Systematics
        if fullSyst:
            for syst in fullChanSyst + fullSamSyst:
                chan.addSystematic(syst)
                if debugSyst:
                    print " channel = ", chan.name, " adding Full systematic = ", syst.name             









          
if doValidationDilep:
    meffVR4_ee=bkgOnly.addChannel("meffInc",["VR4ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR4_em=bkgOnly.addChannel("meffInc",["VR4em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR4_mm=bkgOnly.addChannel("meffInc",["VR4mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    nJetVR4_ee=bkgOnly.addChannel("nJet",["VR4ee"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetVR4_em=bkgOnly.addChannel("nJet",["VR4em"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetVR4_mm=bkgOnly.addChannel("nJet",["VR4mm"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    meffVR2_ee=bkgOnly.addChannel("meffInc",["VR2ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR2_em=bkgOnly.addChannel("meffInc",["VR2em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR2_mm=bkgOnly.addChannel("meffInc",["VR2mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    nJetVR2_ee=bkgOnly.addChannel("nJet",["VR2ee"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetVR2_em=bkgOnly.addChannel("nJet",["VR2em"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetVR2_mm=bkgOnly.addChannel("nJet",["VR2mm"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    meffVR3_ee=bkgOnly.addChannel("meffInc",["VR3ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR3_em=bkgOnly.addChannel("meffInc",["VR3em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR3_mm=bkgOnly.addChannel("meffInc",["VR3mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    nJetVR3_ee=bkgOnly.addChannel("nJet",["VR3ee"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetVR3_em=bkgOnly.addChannel("nJet",["VR3em"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetVR3_mm=bkgOnly.addChannel("nJet",["VR3mm"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)

    validation2LepChannels = [meffVR2_ee, meffVR2_em, meffVR2_mm, nJetVR2_ee, nJetVR2_em, nJetVR2_mm,
                              meffVR3_ee, meffVR3_em, meffVR3_mm, nJetVR3_ee, nJetVR3_em, nJetVR3_mm,
                              meffVR4_ee, meffVR4_em, meffVR4_mm, nJetVR4_ee, nJetVR4_em, nJetVR4_mm]
    
    # add systematics
    for chan in validation2LepChannels:
        chan.useOverflowBin = True
        for syst in commonChanSyst + commonSamSyst:
            chan.addSystematic(syst)
            if debugSyst:
                print " channel = ", chan.name, " adding systematic = ", syst.name
        # only additional Full Systematics
        if fullSyst:
            for syst in fullChanSyst + fullSamSyst:
                chan.addSystematic(syst)
                if debugSyst:
                    print " channel = ", chan.name, " adding Full systematic = ", syst.name             

    
if doValidationDilepZ:
    meffZVR4_ee=bkgOnly.addChannel("meffInc",["ZVR4ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffZVR4_em=bkgOnly.addChannel("meffInc",["ZVR4em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffZVR4_mm=bkgOnly.addChannel("meffInc",["ZVR4mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    nJetZVR4_ee=bkgOnly.addChannel("nJet",["ZVR4ee"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetZVR4_em=bkgOnly.addChannel("nJet",["ZVR4em"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetZVR4_mm=bkgOnly.addChannel("nJet",["ZVR4mm"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    meffZVR2_ee=bkgOnly.addChannel("meffInc",["ZVR2ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffZVR2_em=bkgOnly.addChannel("meffInc",["ZVR2em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffZVR2_mm=bkgOnly.addChannel("meffInc",["ZVR2mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    nJetZVR2_ee=bkgOnly.addChannel("nJet",["ZVR2ee"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetZVR2_em=bkgOnly.addChannel("nJet",["ZVR2em"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetZVR2_mm=bkgOnly.addChannel("nJet",["ZVR2mm"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    meffZVR3_ee=bkgOnly.addChannel("meffInc",["ZVR3ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffZVR3_em=bkgOnly.addChannel("meffInc",["ZVR3em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffZVR3_mm=bkgOnly.addChannel("meffInc",["ZVR3mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    nJetZVR3_ee=bkgOnly.addChannel("nJet",["ZVR3ee"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetZVR3_em=bkgOnly.addChannel("nJet",["ZVR3em"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    nJetZVR3_mm=bkgOnly.addChannel("nJet",["ZVR3mm"],nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
    
    validation2LepZChannels = [meffZVR2_ee, meffZVR2_em, meffZVR2_mm, nJetZVR2_ee, nJetZVR2_em, nJetZVR2_mm,
                              meffZVR3_ee, meffZVR3_em, meffZVR3_mm, nJetZVR3_ee, nJetZVR3_em, nJetZVR3_mm,
                              meffZVR4_ee, meffZVR4_em, meffZVR4_mm, nJetZVR4_ee, nJetZVR4_em, nJetZVR4_mm]
    
    # add systematics
    for chan in validation2LepChannels:
        chan.hasB = True
        chan.hasBQCD = True
        chan.useOverflowBin = True
        for syst in commonChanSyst + commonSamSyst + btagChanSyst:
            chan.addSystematic(syst)
            if debugSyst:
                print " channel = ", chan.name, " adding systematic = ", syst.name
        # only additional Full Systematics
        if fullSyst:
            for syst in fullChanSyst + fullSamSyst:
                chan.addSystematic(syst)
                if debugSyst:
                    print " channel = ", chan.name, " adding Full systematic = ", syst.name             
    

if doValidationSoftLep:
    mmSVEl = bkt.addChannel("met/meff2Jet",["SVEl"],6,0.1,0.7)
    mmSVMu = bkt.addChannel("met/meff2Jet",["SVMu"],6,0.1,0.7)
    mmSVWEl = bkt.addChannel("met/meff2Jet",["SVWEl"],6,0.1,0.7)
    mmSVWMu = bkt.addChannel("met/meff2Jet",["SVWMu"],6,0.1,0.7)
    mmSVTEl = bkt.addChannel("met/meff2Jet",["SVTEl"],6,0.1,0.7)
    mmSVTMu = bkt.addChannel("met/meff2Jet",["SVTMu"],6,0.1,0.7)

    bkgOnly.setValidationChannels([mmSVEl, mmSVMu, mmSVTEl, mmSVTMu, mmSVWEl, mmSVWMu])

    validationSoftLepChannels = [mmSVEl, mmSVMu]
    validationSoftLepBtagChannels =  [mmSVTEl, mmSVTMu]
    validationSoftLepBvetoChannels =  [mmSVWEl, mmSVWMu]
   
    # add systematics
    for chan in validationSoftLepChannels:
        chan.useOverflowBin = True
        for syst in commonChanSyst + commonSamSyst:
            chan.addSystematic(syst)
            if debugSyst:
                print " channel = ", chan.name, " adding systematic = ", syst.name
        # only additional Full Systematics
        if fullSyst:
            for syst in fullChanSyst + fullSamSyst:
                chan.addSystematic(syst)
                if debugSyst:
                    print " channel = ", chan.name, " adding Full systematic = ", syst.name             

    # add systematics
    for chan in validationSoftLepBtagChannels:
        chan.hasB = True
        chan.hasBQCD = True
        chan.useOverflowBin = True
        for syst in commonChanSyst + commonSamSyst + btagChanSyst:
            chan.addSystematic(syst)
            if debugSyst:
                print " channel = ", chan.name, " adding systematic = ", syst.name
        # only additional Full Systematics
        if fullSyst:
            for syst in fullChanSyst + fullSamSyst:
                chan.addSystematic(syst)
                if debugSyst:
                    print " channel = ", chan.name, " adding Full systematic = ", syst.name             

    # add systematics
    for chan in validationSoftLepBvetoChannels:
        chan.hasB = True
        chan.hasBQCD = False
        chan.useOverflowBin = True
        for syst in commonChanSyst + commonSamSyst + btagChanSyst:
            chan.addSystematic(syst)
            if debugSyst:
                print " channel = ", chan.name, " adding systematic = ", syst.name
        # only additional Full Systematics
        if fullSyst:
            for syst in fullChanSyst + fullSamSyst:
                chan.addSystematic(syst)
                if debugSyst:
                    print " channel = ", chan.name, " adding Full systematic = ", syst.name
                    pass
                pass
            pass
        pass
    pass


if doValidationSR:
    bkgOnly.setValidationChannels(validationSRChannels)

if doValidationSlope:
    bkgOnly.setValidationChannels([meffTR_El,meffTR_Mu,metTR_El,metTR_Mu,pt1TR_El,pt1TR_Mu,pt2TR_El,pt2TR_Mu,wptWR_El,wptWR_Mu,metWR_El,metWR_Mu,ZptZR_ee,ZptZR_mm])

if doValidationDilep:
    bkgOnly.setValidationChannels([meffVR4_ee,meffVR4_em,meffVR4_mm,nJetVR4_ee,nJetVR4_em,nJetVR4_mm,meffVR2_ee,meffVR2_em,meffVR2_mm,nJetVR2_ee,nJetVR2_em,nJetVR2_mm,meffVR3_ee,meffVR3_em,meffVR3_mm,nJetVR3_ee,nJetVR3_em,nJetVR3_mm])

if doValidationDilepZ:
    bkgOnly.setValidationChannels([meffZVR4_ee,meffZVR4_em,meffZVR4_mm,nJetZVR4_ee,nJetZVR4_em,nJetZVR4_mm,meffZVR2_ee,meffZVR2_em,meffZVR2_mm,nJetZVR2_ee,nJetZVR2_em,nJetZVR2_mm,meffZVR3_ee,meffZVR3_em,meffZVR3_mm,nJetZVR3_ee,nJetZVR3_em,nJetZVR3_mm])
    pass

if doValidationSoftLep:
    bkgOnly.setValidationChannels(validationSoftLepChannels + validationSoftLepBtagChannels + validationSoftLepBvetoChannels )


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
        S2Channel_em = myTopLvl.addChannel("meffInc",["S2em"],meffNBinsS2,meffBinLowS2,meffBinHighS2)
        S2Channel_mm = myTopLvl.addChannel("meffInc",["S2mm"],meffNBinsS2,meffBinLowS2,meffBinHighS2)
        S4Channel_ee = myTopLvl.addChannel("meffInc",["S4ee"],meffNBinsS4,meffBinLowS4,meffBinHighS4)
        S4Channel_em = myTopLvl.addChannel("meffInc",["S4em"],meffNBinsS4,meffBinLowS4,meffBinHighS4)
        S4Channel_mm = myTopLvl.addChannel("meffInc",["S4mm"],meffNBinsS4,meffBinLowS4,meffBinHighS4)

        SRChannels = [nJetZeeChannel, nJetZeChannel, nJetZmmChannel, nJetZmChannel]
        
        # add systematics
        for chan in SRChannels:
            chan.useOverflowBin = True
            chan.getSample(sig).addSystematic(jesSignal)
            for syst in sigCommonChanSyst:
                chan.addSystematic(syst)
                if debugSyst:
                    print " channel = ", chan.name, " adding systematic = ", syst.name
            # only BGList sample systematics     
            for syst in sigCommonBGSamSyst:
                for sam in BGList:
                    chan.getSample(sam).addSystematic(syst)
                    if debugSyst:
                        print " channel = ", chan.name, " sample = ", chan.getSample(sam).name, " adding systematic = ", syst.name
            # only additional Full Systematics
            if fullSyst:
                for syst in sigFullChanSyst:
                    chan.addSystematic(syst)
                    if debugSyst:
                        print " channel = ", chan.name, " adding Full systematic = ", syst.name
            # only BGList sample additional Full systematics     
            for syst in sigFullBGSamSyst:
                for sam in BGList:
                    chan.getSample(sam).addSystematic(syst)
                    if debugSyst:
                        print " channel = ", chan.name, " sample = ", chan.getSample(sam).name, " adding Full systematic = ", syst.name
            # only BGList+SigList sample additional Full systematics     
            for syst in sigFullSamSyst:
                for sam in BGList+SigList:
                    chan.getSample(sam).addSystematic(syst)
                    if debugSyst:
                        print " channel = ", chan.name, " sample = ", chan.getSample(sam).name, " adding Full systematic = ", syst.name
             

        ## Which SRs for which Scenario?

        if doExclusion_GMSB_combined:
            myTopLvl.setSignalChannels([S2Channel_ee,S2Channel_em,S2Channel_mm])       
        elif doExclusion_mSUGRA_dilepton_combined:
            myTopLvl.setSignalChannels([S2Channel_ee,S2Channel_em,S2Channel_mm,S4Channel_ee,S4Channel_em,S4Channel_mm])
        ## Which SRs for SM???
        elif doExclusion_GG_twostepCC_slepton:
            myTopLvl.setSignalChannels([S4Channel_ee,S4Channel_em,S4Channel_mm])


#  LocalWords:  jesSignal

