################################################################
## In principle all you have to setup is defined in this file ##
################################################################

from configManager import configMgr
from ROOT import kBlack,kRed,kBlue,kGreen,kYellow,kWhite,kPink,kGray,kMagenta
from configWriter import TopLevelXML,Measurement,ChannelXML,Sample
from systematic import Systematic
from copy import deepcopy
import commands

#from ROOT import gROOT
#gROOT.LoadMacro("./macros/AtlasStyle.C")
#import ROOT
#ROOT.SetAtlasStyle()

def replaceWeight(oldList,oldWeight,newWeight):
    newList = deepcopy(oldList)
    newList[oldList.index(oldWeight)] = newWeight
    return newList

def addWeight(oldList,newWeight):
    newList = deepcopy(oldList)
    newList.append(newWeight)
    return newList

def removeWeight(oldList,oldWeight):
    newList = deepcopy(oldList)
    newList.remove(oldWeight)
    return newList

onLxplus='lx' in commands.getstatusoutput("hostname")[1] or 'vm' in commands.getstatusoutput("hostname")[1]
useHardLepCR=True
useSoftLepCR=True
useDiLepCR=True
useStat=True
fullSyst=True

doValidationSRLoose=True
doValidationSRTight=True
doValidationSlope=True
doValidationDilep=True
doValidationDilepZ=True
doValidationSoftLep=True

doExclusion_GMSB_combined=False
doExclusion_mSUGRA_dilepton_combined=True
doExclusion_GG_onestepCC_x12=False
doExclusion_GG_onestepCC_gridX=False
doExclusion_GG_twostepCC_slepton=False
blindS=False
useXsecUnc=True             # switch off when calucating excluded cross section (colour code in SM plots)
doWptReweighting=False ## deprecated
doSignalOnly=False #Remove all bkgs for signal histo creation step
if configMgr.executeHistFactory:
    doSignalOnly=False
    
if not 'sigSamples' in dir():
        sigSamples=["SU_580_240_0_10_P"]
    #sigSamples=["SM_GG_onestepCC_445_245_45"]
    #    sigSamples=["SM_GG_twostepCC_slepton_415_215_115_15"]
    #    sigSamples=["GMSB_3_2d_50_250_3_10_1_1"]

# First define HistFactory attributes
configMgr.analysisName = "Combined_KFactorFit_5Channel" # Name to give the analysis
configMgr.outputFileName = "results/CombinedKFactorFit_5Channel.root"

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

#Split bdgFiles per channel
bgdFiles_ee = []
bgdFiles_em = []
bgdFiles_mm = []
bgdFiles_e = []
bgdFiles_m = []
bgdFiles_se = []
bgdFiles_sm = []

sigFiles = []
sigFiles_l = []
sigFiles_sl = []

configMgr.histCacheFile = "data/"+configMgr.analysisName+".root"
inputDir="root://eosatlas//eos/atlas/atlascerngroupdisk/phys-susy/histfitter/stronglepton/Paper_v1/"
inputDirSig="root://eosatlas//eos/atlas/atlascerngroupdisk/phys-susy/histfitter/stronglepton/"

if not onLxplus:
    print "INFO : Mainz bleibt Mainz...\n"
else:
    print "INFO : Running on lxplus... \n"

# Set the files to read from
if configMgr.readFromTree:
    if not onLxplus:
        bgdFiles_ee = ["data/SusyFitterTree_EleEle.root"]
        bgdFiles_em = ["data/SusyFitterTree_EleMu.root"]
        bgdFiles_mm = ["data/SusyFitterTree_MuMu.root"]
        bgdFiles_e = ["data/SusyFitterTree_OneEle.root"]
        bgdFiles_m = ["data/SusyFitterTree_OneMu.root"]
        bgdFiles_se = ["data/SusyFitterTree_OneSoftEle_BG_v5.root"]
        bgdFiles_sm = ["data/SusyFitterTree_OneSoftMuo_BG_v5.root"]
    else:
        bgdFiles_ee = [inputDir+"/SusyFitterTree_EleEle.root"]
        bgdFiles_em = [inputDir+"/SusyFitterTree_EleMu.root"]
        bgdFiles_mm = [inputDir+"/SusyFitterTree_MuMu.root"]
        bgdFiles_e = [inputDir+"/SusyFitterTree_OneEle.root"]
        bgdFiles_m = [inputDir+"/SusyFitterTree_OneMu.root"]
        bgdFiles_se = ["/afs/cern.ch/work/h/hyamaguc/public/samples/SusyFitterTree_OneSoftEle_BG_v7.root"]
        bgdFiles_sm = ["/afs/cern.ch/work/h/hyamaguc/public/samples/SusyFitterTree_OneSoftMuo_BG_v7.root"]        

sigfile_MH_v2 =  "/afs/cern.ch/work/h/hyamaguc/public/samples/SusyFitterTree_p832_GGonestep_paper_v2.root"
  
if doExclusion_GMSB_combined:
    if not onLxplus:
        sigFiles+=["data/SusyFitterTree_EleEle_GMSB.root","data/SusyFitterTree_EleMu_GMSB.root","data/SusyFitterTree_MuMu_GMSB.root"]
    else:
        sigFiles+=[inputDirSig+"/SusyFitterTree_EleEle_GMSB.root",inputDirSig+"/SusyFitterTree_EleMu_GMSB.root",inputDirSig+"/SusyFitterTree_MuMu_GMSB.root"]

if doExclusion_mSUGRA_dilepton_combined:
    if not onLxplus:
        sigFiles+=["data/SusyFitterTree_EleEle_mSUGRA.root","data/SusyFitterTree_EleMu_mSUGRA.root","data/SusyFitterTree_MuMu_mSUGRA.root"]
        sigFiles_l+=["data/SusyFitterTree_p832_mSUGRA_paper_v1.root"]
    else:
        sigFiles+=[inputDirSig+"/SusyFitterTree_EleEle_mSUGRA.root",inputDirSig+"/SusyFitterTree_EleMu_mSUGRA.root",inputDirSig+"/SusyFitterTree_MuMu_mSUGRA.root"]
        sigFiles_l+=[inputDirSig+"/SusyFitterTree_p832_mSUGRA_paper_v1.root"]
 
if doExclusion_GG_onestepCC_x12:
    if not onLxplus:
        sigFiles+=["data/SusyFitterTree_EleEle_SM_GG_onestepCC.root","data/SusyFitterTree_MuMu_SM_GG_onestepCC.root","data/SusyFitterTree_EleMu_SM_GG_onestepCC.root"]
        sigFiles_l+=[sigfile_MH_v2] 
        sigFiles_sl+=["data/SusyFitterTree_OneSoftMuo_SM_GG_onestepCC_v3.root","data/SusyFitterTree_OneSoftEle_SM_GG_onestepCC_v3.root"]
    else:
        sigFiles+=[inputDirSig+"/SusyFitterTree_EleEle_SM_GG_onestepCC.root",inputDirSig+"/SusyFitterTree_MuMu_SM_GG_onestepCC.root",inputDirSig+"/SusyFitterTree_EleMu_SM_GG_onestepCC.root"]
        sigFiles_l+=[sigfile_MH_v2] #inputDirSig+"/SusyFitterTree_p832_GGonestepLSP60_paper_v1.root"
        sigFiles_sl+=[inputDirSig+"/SusyFitterTree_OneSoftMuo_SM_GG_onestepCC_v3.root",inputDirSig+"/SusyFitterTree_OneSoftEle_SM_GG_onestepCC_v3.root"]
          
if doExclusion_GG_onestepCC_gridX:
    if not onLxplus:
        sigFiles+=["data/SusyFitterTree_EleEle_SM_GG_onestepCC.root","data/SusyFitterTree_MuMu_SM_GG_onestepCC.root","data/SusyFitterTree_EleMu_SM_GG_onestepCC.root"]
        sigFiles_l+=["data/SusyFitterTree_p832_GGonestepLSP60_paper_v1.root"]
        sigFiles_sl+=["data/SusyFitterTree_OneSoftMuo_SM_GG_onestepCC_LSP60_v3.root","data/SusyFitterTree_OneSoftEle_SM_GG_onestepCC_LSP60_v3.root"]
    else:
        sigFiles+=[inputDirSig+"/SusyFitterTree_EleEle_SM_GG_onestepCC.root",inputDirSig+"/SusyFitterTree_MuMu_SM_GG_onestepCC.root",inputDirSig+"/SusyFitterTree_EleMu_SM_GG_onestepCC.root"]
        sigFiles_l+=[inputDirSig+"/SusyFitterTree_p832_GGonestepLSP60_paper_v1.root"]
        sigFiles_sl+=[inputDirSig+"/SusyFitterTree_OneSoftMuo_SM_GG_onestepCC_LSP60_v3.root",inputDirSig+"/SusyFitterTree_OneSoftEle_SM_GG_onestepCC_LSP60_v3.root"]

if doExclusion_GG_twostepCC_slepton:
    if not onLxplus:
        sigFiles+=["data/SusyFitterTree_EleEle_SM_GG_twostepCC_slepton.root","data/SusyFitterTree_EleMu_SM_GG_twostepCC_slepton.root","data/SusyFitterTree_MuMu_SM_GG_twostepCC_slepton.root"]
    else:
        sigFiles+=[inputDirSig+"/SusyFitterTree_EleEle_SM_GG_twostepCC_slepton.root",inputDirSig+"/SusyFitterTree_EleMu_SM_GG_twostepCC_slepton.root",inputDirSig+"/SusyFitterTree_MuMu_SM_GG_twostepCC_slepton.root"]

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

configMgr.cutsDict["WRElVR"]="lep2Pt<10 && met>50 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc > 500 && AnalysisType==1"
configMgr.cutsDict["WRMuVR"]="lep2Pt<10 && met>50 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc > 500 && AnalysisType==2"

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

configMgr.cutsDict["SVWEl"]="lep1Pt<25 && lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB3Jet==0 && jet1Pt>130 && jet2Pt>25 && AnalysisType==6"
configMgr.cutsDict["SVTEl"]="lep1Pt<25 && lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB3Jet>0 && jet1Pt>130 && jet2Pt>25 && AnalysisType==6"
configMgr.cutsDict["SVWMu"]="lep1Pt<20 && lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB3Jet==0 && jet1Pt>130 && jet2Pt>25 && AnalysisType==7"
configMgr.cutsDict["SVTMu"]="lep1Pt<20 && lep2Pt<10 && met>180 && met<250 && mt>40 && mt<80 && nB3Jet>0 && jet1Pt>130 && jet2Pt>25 && AnalysisType==7"

configMgr.cutsDict["SSEl"]="lep1Pt < 25 && lep2Pt<10 && met>250 && mt>100 && jet1Pt>130 && jet2Pt>25 && AnalysisType==6"
configMgr.cutsDict["SSMu"]="lep1Pt < 20 && lep2Pt<10 && met>250 && mt>100 && jet1Pt>130 && jet2Pt>25 && AnalysisType==7"

d=configMgr.cutsDict
configMgr.cutsDict["SSElT"] = d["SSEl"]+"&& met/meff2Jet>0.3"
configMgr.cutsDict["SSMuT"] = d["SSMu"]+"&& met/meff2Jet>0.3"
#To allow 1-bin and multi-bins channels based on same cuts
configMgr.cutsDict["S2eeT"] = d["S2ee"] 
configMgr.cutsDict["S2emT"] = d["S2em"] 
configMgr.cutsDict["S2mmT"] = d["S2mm"] 
configMgr.cutsDict["S4eeT"] = d["S4ee"] 
configMgr.cutsDict["S4emT"] = d["S4em"] 
configMgr.cutsDict["S4mmT"] = d["S4mm"] 

## Lists of weights 
if doWptReweighting:
    truthWptWeight="truthWptWeight"
else:
    truthWptWeight="1"

weights = ["genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight, \
           "truthZpt0GeVWeight", "truthZpt50GeVWeight","truthZpt100GeVWeight","truthZpt150GeVWeight", \
           "truthZpt200GeVWeight","bTagWeight3Jet"]

configMgr.weights = weights
configMgr.weightsQCD = "qcdWeight"
configMgr.weightsQCDWithB = "qcdBWeight"

xsecSigHighWeights = replaceWeight(weights,"genWeight","genWeightUp")
xsecSigLowWeights = replaceWeight(weights,"genWeight","genWeightDown")

#ktScaleWHighWeights = addWeight(weights,"ktfacUpWeightW")
#ktScaleWHighWeights = addWeight(weights,"ktfacDownWeightW")

#ktScaleWHighWeights = addWeight(weights,"ktfacUpWeightTop")
#ktScaleWHighWeights = addWeight(weights,"ktfacDownWeightTop")
                    
bTagHighWeights = replaceWeight(weights,"bTagWeight3Jet","bTagWeight3JetUp")
bTagLowWeights = replaceWeight(weights,"bTagWeight3Jet","bTagWeight3JetDown")

trigHighWeights = replaceWeight(weights,"triggerWeight","triggerWeightUp")
trigLowWeights = replaceWeight(weights,"triggerWeight","triggerWeightDown")

lepHighWeights = replaceWeight(weights,"leptonWeight","leptonWeightUp")
lepLowWeights = replaceWeight(weights,"leptonWeight","leptonWeightDown")

## True Zpt reweighting

pT0GeVHighWeights = replaceWeight(weights,"truthZpt0GeVWeight","truthZpt0GeVWeightUp")
pT0GeVLowWeights = replaceWeight(weights,"truthZpt0GeVWeight","truthZpt0GeVWeightDown")

pT50GeVHighWeights = replaceWeight(weights,"truthZpt50GeVWeight","truthZpt50GeVWeightUp")
pT50GeVLowWeights = replaceWeight(weights,"truthZpt50GeVWeight","truthZpt50GeVWeightDown")

pT100GeVHighWeights = replaceWeight(weights,"truthZpt100GeVWeight","truthZpt100GeVWeightUp")
pT100GeVLowWeights = replaceWeight(weights,"truthZpt100GeVWeight","truthZpt100GeVWeightDown")

pT150GeVHighWeights = replaceWeight(weights,"truthZpt150GeVWeight","truthZpt150GeVWeightUp")
pT150GeVLowWeights = replaceWeight(weights,"truthZpt150GeVWeight","truthZpt150GeVWeightDown")

pT200GeVHighWeights = replaceWeight(weights,"truthZpt200GeVWeight","truthZpt200GeVWeightUp")
pT200GeVLowWeights = replaceWeight(weights,"truthZpt200GeVWeight","truthZpt200GeVWeightDown")

## HF uncertainty on V+Jets

hfHighWeights = addWeight(weights,"hfWeightUp")
hfLowWeights = addWeight(weights,"hfWeightDown")
                                                                                        
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
basicChanSyst.append(Systematic("MP","_NoSys","_METPUup","_METPUdown","tree","histoSys")) # MET pileup uncertainty - one per channel
             
fullChanSyst = []
#fullChanSyst.append(Systematic("LE",configMgr.weights,lepHighWeights,lepLowWeights,"weight","overallSys")) # Lepton weight uncertainty
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

AlpGenSamples.sort(key=lambda x: x.name)

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

#List of bkg samples
bgdsamples=[bgSample]
for sam in AlpGenSamples:
    bgdsamples.append(sam)

#QCD and data samples
qcdSample = Sample("QCD",kGray+1)
qcdSample.setQCD(True,"histoSys")
qcdSample.setStatConfig(useStat)

dataSample = Sample("Data",kBlack)
dataSample.setData()

# nJet Binning for Top Control region
nJetTopeeBinLow = 2
nJetTopeeBinHigh = 10

nJetTopeBinLow = 3
nJetTopeBinHigh = 10

nJetTopseBinLow = 2
nJetTopseBinHigh = 8

nJetTopemBinLow = 2
nJetTopemBinHigh = 10

nJetTopmmBinLow = 2
nJetTopmmBinHigh = 10

nJetTopmBinLow = 3
nJetTopmBinHigh = 10

nJetTopsmBinLow = 2
nJetTopsmBinHigh = 8

# nJet Binning for W Control region
nJetZmmRegions = ["ZRmm"]
nJetZmmBinLow = 2
nJetZmmBinHigh = 10

nJetZmRegions = ["WRMu"]
nJetZmBinLow = 3
nJetZmBinHigh = 10

nJetZsmRegions = ["SVWMu"]
nJetZsmBinLow = 2
nJetZsmBinHigh = 8

nJetZeeRegions = ["ZRee"]
nJetZeeBinLow = 2
nJetZeeBinHigh = 10

nJetZeRegions = ["WREl"]
nJetZeBinLow = 3
nJetZeBinHigh = 10

nJetZseRegions = ["SVWEl"]
nJetZseBinLow = 2
nJetZseBinHigh = 8

ZptZmmRegions = ["ZRmm"]
ZptZmmNBins = 40
ZptZmmBinLow = 0
ZptZmmBinHigh = 1000

ZptZeeRegions = ["ZRee"]
ZptZeeNBins = 40
ZptZeeBinLow = 0
ZptZeeBinHigh = 1000

srNBins = 1
srBinLow = 0.5
srBinHigh = 1.5


#--------------------------------------------------------------
# Background-only fit 
#--------------------------------------------------------------
bkgOnly = configMgr.addTopLevelXML("bkgonly")
if not doSignalOnly:
    bkgOnly.addSamples([qcdSample])
    bkgOnly.addSamples(bgdsamples)
    bkgOnly.addSamples([dataSample])
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

#Add common systematics
for syst in basicChanSyst:
    print syst.name
    bkgOnly.addSystematic(syst)
if fullSyst:
    for syst in fullChanSyst:
        print syst.name
        bkgOnly.addSystematic(syst)


##### nJet for Top ####

topChannels = []

if useDiLepCR:
    # ele ele
    nJetTopeeChannel=bkgOnly.addChannel("nJet",["TRee"],(nJetTopeeBinHigh-nJetTopeeBinLow),nJetTopeeBinLow,nJetTopeeBinHigh)
    nJetTopeeChannel.setFileList(bgdFiles_ee)
    #  ele mu
    nJetTopemChannel=bkgOnly.addChannel("nJet",["TRem"],(nJetTopemBinHigh-nJetTopemBinLow),nJetTopemBinLow,nJetTopemBinHigh)
    nJetTopemChannel.setFileList(bgdFiles_em)
    # mu mu
    nJetTopmmChannel=bkgOnly.addChannel("nJet",["TRmm"],(nJetTopmmBinHigh-nJetTopmmBinLow),nJetTopmmBinLow,nJetTopmmBinHigh)
    nJetTopmmChannel.setFileList(bgdFiles_mm)
    
    topChannels += [nJetTopeeChannel,nJetTopemChannel,nJetTopmmChannel]

if useHardLepCR:
    #  single ele
    nJetTopeChannel=bkgOnly.addChannel("nJet",["TREl"],(nJetTopeBinHigh-nJetTopeBinLow),nJetTopeBinLow,nJetTopeBinHigh)
    nJetTopeChannel.setFileList(bgdFiles_e)
    # single mu
    nJetTopmChannel=bkgOnly.addChannel("nJet",["TRMu"],(nJetTopmBinHigh-nJetTopmBinLow),nJetTopmBinLow,nJetTopmBinHigh)
    nJetTopmChannel.setFileList(bgdFiles_m)

    topChannels += [nJetTopeChannel,nJetTopmChannel]

if useSoftLepCR:
    #  single soft ele
    nJetTopseChannel=bkgOnly.addChannel("nJet",["SVTEl"],(nJetTopseBinHigh-nJetTopseBinLow),nJetTopseBinLow,nJetTopseBinHigh)
    nJetTopseChannel.setFileList(bgdFiles_se)
    # soft single mu
    nJetTopsmChannel=bkgOnly.addChannel("nJet",["SVTMu"],(nJetTopsmBinHigh-nJetTopsmBinLow),nJetTopsmBinLow,nJetTopsmBinHigh)
    nJetTopsmChannel.setFileList(bgdFiles_sm)

    topChannels += [nJetTopseChannel,nJetTopsmChannel]


# add systematics
for chan in topChannels:
    chan.hasBQCD = True
    chan.useOverflowBin = False
    for syst in btagChanSyst:
        chan.addSystematic(syst)

        
####### nJet for W/Z  #######


WZChannels = []

if useDiLepCR:
    # ele ele    
    nJetZeeChannel=bkgOnly.addChannel("nJet",nJetZeeRegions,(nJetZeeBinHigh-nJetZeeBinLow),nJetZeeBinLow,nJetZeeBinHigh)
    nJetZeeChannel.setFileList(bgdFiles_ee)
    nJetZeeChannel.hasBQCD = False
    nJetZeeChannel.removeWeight("bTagWeight3Jet")
    # mu mu
    nJetZmmChannel=bkgOnly.addChannel("nJet",nJetZmmRegions,(nJetZmmBinHigh-nJetZmmBinLow),nJetZmmBinLow,nJetZmmBinHigh)
    nJetZmmChannel.setFileList(bgdFiles_mm)
    nJetZmmChannel.hasBQCD = False
    nJetZmmChannel.removeWeight("bTagWeight3Jet")

    WZChannels += [nJetZmmChannel,nJetZeeChannel]
    

if useHardLepCR:
    # single ele
    nJetZeChannel=bkgOnly.addChannel("nJet",nJetZeRegions,(nJetZeBinHigh-nJetZeBinLow),nJetZeBinLow,nJetZeBinHigh)
    nJetZeChannel.setFileList(bgdFiles_e)
    nJetZeChannel.hasBQCD = False
    [nJetZeChannel.addSystematic(syst) for syst in btagChanSyst]
    # single mu
    nJetZmChannel=bkgOnly.addChannel("nJet",nJetZmRegions,(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh)
    nJetZmChannel.setFileList(bgdFiles_m)
    nJetZmChannel.hasBQCD = False
    [nJetZmChannel.addSystematic(syst) for syst in btagChanSyst]

    WZChannels += [nJetZmChannel,nJetZeChannel]


if useSoftLepCR:    
    # single soft mu
    nJetZsmChannel=bkgOnly.addChannel("nJet",nJetZsmRegions,(nJetZsmBinHigh-nJetZsmBinLow),nJetZsmBinLow,nJetZsmBinHigh)
    nJetZsmChannel.setFileList(bgdFiles_sm)
    nJetZsmChannel.hasB = True
    nJetZsmChannel.hasBQCD = False
    [nJetZsmChannel.addSystematic(syst) for syst in btagChanSyst]
    # single soft ele
    nJetZseChannel=bkgOnly.addChannel("nJet",nJetZseRegions,(nJetZseBinHigh-nJetZseBinLow),nJetZseBinLow,nJetZseBinHigh)
    nJetZseChannel.setFileList(bgdFiles_se)
    nJetZseChannel.hasB = True
    nJetZseChannel.hasBQCD = False
    [nJetZseChannel.addSystematic(syst) for syst in btagChanSyst]

    WZChannels += [nJetZsmChannel,nJetZseChannel]


# Additional settings
for chan in WZChannels:
    chan.hasBQCD = False    
    chan.useOverflowBin = False
        
bkgOnly.setBkgConstrainChannels(WZChannels+topChannels)


#-------------------------------------------------
# Signal regions - only do this if background only, add as validation regions! 
#-------------------------------------------------

# meffNBins = 1
# #    meffBinLow = 400.
# meffBinLow = 0.
# meffBinHigh = 1600.

#Hard 1 lepton SR binning
meffNBins1lS3 = 6
meffBinLow1lS3 = 400.
meffBinHigh1lS3 = 1600.

meffNBins1lS4 = 4
meffBinLow1lS4 = 800.
meffBinHigh1lS4 = 1600.

#Dilepton SR binning
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
    meffTR_El=bkgOnly.addValidationChannel("meffInc",["TRElVR"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffTR_Mu=bkgOnly.addValidationChannel("meffInc",["TRMuVR"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    metTR_El=bkgOnly.addValidationChannel("met",["TRElVR2"],metNBinsTR,metBinLowTR,metBinHighTR)
    metTR_Mu=bkgOnly.addValidationChannel("met",["TRMuVR2"],metNBinsTR,metBinLowTR,metBinHighTR)
    pt1TR_El=bkgOnly.addValidationChannel("jet1Pt",["TRElVR"],pt1NBinsTR,pt1BinLowTR,pt1BinHighTR)
    pt1TR_Mu=bkgOnly.addValidationChannel("jet1Pt",["TRMuVR"],pt1NBinsTR,pt1BinLowTR,pt1BinHighTR)
    pt2TR_El=bkgOnly.addValidationChannel("jet2Pt",["TRElVR"],pt2NBinsTR,pt2BinLowTR,pt2BinHighTR)
    pt2TR_Mu=bkgOnly.addValidationChannel("jet2Pt",["TRMuVR"],pt2NBinsTR,pt2BinLowTR,pt2BinHighTR)

    validationSlopeTRChannels = [meffTR_El,meffTR_Mu,metTR_El,metTR_Mu,pt1TR_El,pt1TR_Mu,pt2TR_El,pt2TR_Mu]
    
    # add systematics
    for chan in validationSlopeTRChannels:
        if chan.name.find("El")>-1:
            chan.setFileList(bgdFiles_e)
        else:
            chan.setFileList(bgdFiles_m)
        chan.hasBQCD = True
        chan.useOverflowBin = True
        for syst in btagChanSyst:
            chan.addSystematic(syst)
                    
    # WR
    wptWR_El=bkgOnly.addValidationChannel("Wpt",["WRElVR"],metNBinsTR,metBinLowTR,metBinHighTR)
    wptWR_Mu=bkgOnly.addValidationChannel("Wpt",["WRMuVR"],metNBinsTR,metBinLowTR,metBinHighTR)
    metWR_El=bkgOnly.addValidationChannel("met",["WRElVR"],metNBinsTR,metBinLowTR,metBinHighTR)
    metWR_Mu=bkgOnly.addValidationChannel("met",["WRMuVR"],metNBinsTR,metBinLowTR,metBinHighTR)
    
    validationSlopeWRChannels = [wptWR_El, wptWR_Mu, metWR_El, metWR_Mu]
    
    # add systematics
    for chan in validationSlopeWRChannels:
        if chan.name.find("El")>-1:
            chan.setFileList(bgdFiles_e)
        else:
            chan.setFileList(bgdFiles_m)
        chan.hasBQCD = False
        chan.useOverflowBin = True
        for syst in btagChanSyst:
            chan.addSystematic(syst)

    #ZR
    ZptZR_ee=bkgOnly.addValidationChannel("Zpt",["ZRee"],metNBinsTR,metBinLowTR,metBinHighTR)
    ZptZR_mm=bkgOnly.addValidationChannel("Zpt",["ZRmm"],metNBinsTR,metBinLowTR,metBinHighTR)
    
    validationSlopeZRChannels = [ZptZR_ee, ZptZR_mm]
    
    # add systematics
    for chan in validationSlopeZRChannels:
        if chan.name.find("ee")>-1:
            chan.setFileList(bgdFiles_ee)
        else:
            chan.setFileList(bgdFiles_mm)
        chan.removeWeight("bTagWeight3Jet")
        chan.hasBQCD = False
        chan.useOverflowBin = True

if doValidationSRLoose:
    #DILEPTONS
    meff2ee = bkgOnly.addValidationChannel("meffInc",["S2ee"],meffNBinsS2,meffBinLowS2,meffBinHighS2)
    meff2ee.setFileList(bgdFiles_ee)
    meff4ee = bkgOnly.addValidationChannel("meffInc",["S4ee"],meffNBinsS4,meffBinLowS4,meffBinHighS4)
    meff4ee.setFileList(bgdFiles_ee)
    meff2em = bkgOnly.addValidationChannel("meffInc",["S2em"],meffNBinsS2,meffBinLowS2,meffBinHighS2)
    meff2em.setFileList(bgdFiles_em)
    meff4em = bkgOnly.addValidationChannel("meffInc",["S4em"],meffNBinsS4,meffBinLowS4,meffBinHighS4)
    meff4em.setFileList(bgdFiles_em)
    meff2mm = bkgOnly.addValidationChannel("meffInc",["S2mm"],meffNBinsS2,meffBinLowS2,meffBinHighS2)
    meff2mm.setFileList(bgdFiles_mm)
    meff4mm = bkgOnly.addValidationChannel("meffInc",["S4mm"],meffNBinsS4,meffBinLowS4,meffBinHighS4)
    meff4mm.setFileList(bgdFiles_mm)
    # HARD LEPTON SRS
    meffS3_El=bkgOnly.addValidationChannel("meffInc",["S3El"],meffNBinsHL,meffBinLowHL,meffBinHighHL)
    meffS3_El.setFileList(bgdFiles_e)
    meffS3_Mu=bkgOnly.addValidationChannel("meffInc",["S3Mu"],meffNBinsHL,meffBinLowHL,meffBinHighHL)
    meffS3_Mu.setFileList(bgdFiles_m)
    meffS4_El=bkgOnly.addValidationChannel("meffInc",["S4El"],meffNBinsHL,meffBinLowHL,meffBinHighHL)
    meffS4_El.setFileList(bgdFiles_e)
    meffS4_Mu=bkgOnly.addValidationChannel("meffInc",["S4Mu"],meffNBinsHL,meffBinLowHL,meffBinHighHL)
    meffS4_Mu.setFileList(bgdFiles_m)
    # SOFT LEPTON SRS
    mmSSEl = bkgOnly.addValidationChannel("met/meff2Jet",["SSEl"],6,0.1,0.7)
    mmSSEl.setFileList(bgdFiles_se)
    mmSSMu = bkgOnly.addValidationChannel("met/meff2Jet",["SSMu"],6,0.1,0.7)
    mmSSMu.setFileList(bgdFiles_sm)

    validationSRChannels = [meff2ee, meff4ee, meff2em, meff4em, meff2mm, meff4mm, meffS3_El, meffS3_Mu, meffS4_El, meffS4_Mu, mmSSEl, mmSSMu]
    for chan in validationSRChannels:
        chan.useOverflowBin = True
        chan.removeWeight("bTagWeight3Jet")

if doValidationSRTight:
    #DILEPTONS
    meff2ee = bkgOnly.addValidationChannel("meffInc",["S2eeT"],1,meffBinLowS2,meffBinHighS2)
    meff2ee.setFileList(bgdFiles_ee)
    meff4ee = bkgOnly.addValidationChannel("meffInc",["S4eeT"],1,meffBinLowS4,meffBinHighS4)
    meff4ee.setFileList(bgdFiles_ee)
    meff2em = bkgOnly.addValidationChannel("meffInc",["S2emT"],1,meffBinLowS2,meffBinHighS2)
    meff2em.setFileList(bgdFiles_em)
    meff4em = bkgOnly.addValidationChannel("meffInc",["S4emT"],1,meffBinLowS4,meffBinHighS4)
    meff4em.setFileList(bgdFiles_em)
    meff2mm = bkgOnly.addValidationChannel("meffInc",["S2mmT"],1,meffBinLowS2,meffBinHighS2)
    meff2mm.setFileList(bgdFiles_mm)
    meff4mm = bkgOnly.addValidationChannel("meffInc",["S4mmT"],1,meffBinLowS4,meffBinHighS4)
    meff4mm.setFileList(bgdFiles_mm)
    
    # HARD LEPTON SRS
    meffS3T_El=bkgOnly.addValidationChannel("meffInc",["SR3jTEl"],1,1200,meffBinHighHL)
    meffS3T_El.setFileList(bgdFiles_e)
    meffS3T_Mu=bkgOnly.addValidationChannel("meffInc",["SR3jTMu"],1,1200,meffBinHighHL)
    meffS3T_Mu.setFileList(bgdFiles_m)
    meffS4T_El=bkgOnly.addValidationChannel("meffInc",["SR4jTEl"],1,800,meffBinHighHL)
    meffS4T_El.setFileList(bgdFiles_e)
    meffS4T_Mu=bkgOnly.addValidationChannel("meffInc",["SR4jTMu"],1,800,meffBinHighHL)
    meffS4T_Mu.setFileList(bgdFiles_m)
    # MULTIJETS SRS
    meffS7T_El=bkgOnly.addValidationChannel("meffInc",["SR7jTEl"],1,750,meffBinHighHL)
    meffS7T_El.setFileList(bgdFiles_e)
    meffS7T_Mu=bkgOnly.addValidationChannel("meffInc",["SR7jTMu"],1,750,meffBinHighHL)
    meffS7T_Mu.setFileList(bgdFiles_m)
    # SOFT LEPTON SRS
    mmSSElT = bkgOnly.addValidationChannel("met/meff2Jet",["SSElT"],1,0.3,0.7)
    mmSSElT.setFileList(bgdFiles_se)
    mmSSMuT = bkgOnly.addValidationChannel("met/meff2Jet",["SSMuT"],1,0.3,0.7)
    mmSSMuT.setFileList(bgdFiles_sm)

    validationSRChannels = [meff2ee, meff4ee, meff2em, meff4em, meff2mm, meff4mm, meffS3T_El, meffS3T_Mu, meffS4T_El, meffS4T_Mu, mmSSElT, mmSSMuT,meffS7T_El,meffS7T_Mu]                                                    
    for chan in validationSRChannels:
        chan.useOverflowBin = True
        chan.removeWeight("bTagWeight3Jet")


if doValidationDilep:
    meffVR4_ee=bkgOnly.addValidationChannel("meffInc",["VR4ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR4_em=bkgOnly.addValidationChannel("meffInc",["VR4em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR4_mm=bkgOnly.addValidationChannel("meffInc",["VR4mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    nJetVR4_ee=bkgOnly.addValidationChannel("nJet",["VR4ee"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh)
    nJetVR4_em=bkgOnly.addValidationChannel("nJet",["VR4em"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh)
    nJetVR4_mm=bkgOnly.addValidationChannel("nJet",["VR4mm"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh)
    meffVR2_ee=bkgOnly.addValidationChannel("meffInc",["VR2ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR2_em=bkgOnly.addValidationChannel("meffInc",["VR2em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR2_mm=bkgOnly.addValidationChannel("meffInc",["VR2mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    nJetVR2_ee=bkgOnly.addValidationChannel("nJet",["VR2ee"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh)
    nJetVR2_em=bkgOnly.addValidationChannel("nJet",["VR2em"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh)
    nJetVR2_mm=bkgOnly.addValidationChannel("nJet",["VR2mm"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh)
    meffVR3_ee=bkgOnly.addValidationChannel("meffInc",["VR3ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR3_em=bkgOnly.addValidationChannel("meffInc",["VR3em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffVR3_mm=bkgOnly.addValidationChannel("meffInc",["VR3mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    nJetVR3_ee=bkgOnly.addValidationChannel("nJet",["VR3ee"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh)
    nJetVR3_em=bkgOnly.addValidationChannel("nJet",["VR3em"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh)
    nJetVR3_mm=bkgOnly.addValidationChannel("nJet",["VR3mm"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh)

    validation2LepChannels = [meffVR2_ee, meffVR2_em, meffVR2_mm, nJetVR2_ee, nJetVR2_em, nJetVR2_mm,
                              meffVR3_ee, meffVR3_em, meffVR3_mm, nJetVR3_ee, nJetVR3_em, nJetVR3_mm,
                              meffVR4_ee, meffVR4_em, meffVR4_mm, nJetVR4_ee, nJetVR4_em, nJetVR4_mm]
    
    # add systematics
    for chan in validation2LepChannels:
        chan.useOverflowBin = True
        chan.removeWeight("bTagWeight3Jet")
        if chan.name.endswith("ee"):
            chan.setFileList(bgdFiles_ee)
        elif chan.name.endswith("em"):
            chan.setFileList(bgdFiles_em)
        elif chan.name.endswith("mm"):
            chan.setFileList(bgdFiles_mm)
        else:
            raise RuntimeError("Unexpected channel name: %s"%(chan.name))

    
if doValidationDilepZ:
    meffZVR4_ee=bkgOnly.addValidationChannel("meffInc",["VZR4ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffZVR4_em=bkgOnly.addValidationChannel("meffInc",["VZR4em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffZVR4_mm=bkgOnly.addValidationChannel("meffInc",["VZR4mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    nJetZVR4_ee=bkgOnly.addValidationChannel("nJet",["VZR4ee"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh)
    nJetZVR4_em=bkgOnly.addValidationChannel("nJet",["VZR4em"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh)
    nJetZVR4_mm=bkgOnly.addValidationChannel("nJet",["VZR4mm"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh)
    meffZVR2_ee=bkgOnly.addValidationChannel("meffInc",["VZR2ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffZVR2_em=bkgOnly.addValidationChannel("meffInc",["VZR2em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffZVR2_mm=bkgOnly.addValidationChannel("meffInc",["VZR2mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    nJetZVR2_ee=bkgOnly.addValidationChannel("nJet",["VZR2ee"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh)
    nJetZVR2_em=bkgOnly.addValidationChannel("nJet",["VZR2em"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh)
    nJetZVR2_mm=bkgOnly.addValidationChannel("nJet",["VZR2mm"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh)
    meffZVR3_ee=bkgOnly.addValidationChannel("meffInc",["VZR3ee"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffZVR3_em=bkgOnly.addValidationChannel("meffInc",["VZR3em"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    meffZVR3_mm=bkgOnly.addValidationChannel("meffInc",["VZR3mm"],meffNBinsTR,meffBinLowTR,meffBinHighTR)
    nJetZVR3_ee=bkgOnly.addValidationChannel("nJet",["VZR3ee"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh)
    nJetZVR3_em=bkgOnly.addValidationChannel("nJet",["VZR3em"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh)
    nJetZVR3_mm=bkgOnly.addValidationChannel("nJet",["VZR3mm"],(nJetZmBinHigh-nJetZmBinLow),nJetZmBinLow,nJetZmBinHigh)
    
    validation2LepZChannels = [meffZVR2_ee, meffZVR2_em, meffZVR2_mm, nJetZVR2_ee, nJetZVR2_em, nJetZVR2_mm,
                              meffZVR3_ee, meffZVR3_em, meffZVR3_mm, nJetZVR3_ee, nJetZVR3_em, nJetZVR3_mm,
                              meffZVR4_ee, meffZVR4_em, meffZVR4_mm, nJetZVR4_ee, nJetZVR4_em, nJetZVR4_mm]
    
    # add systematics
    for chan in validation2LepZChannels:
        chan.hasBQCD = False
        chan.useOverflowBin = True
        if chan.name.endswith("ee"):
            chan.setFileList(bgdFiles_ee)
        elif chan.name.endswith("em"):
            chan.setFileList(bgdFiles_em)
        elif chan.name.endswith("mm"):
            chan.setFileList(bgdFiles_mm)
        else:
            raise RuntimeError("Unexpected channel name: %s"%(chan.name))
    

if doValidationSoftLep:
    mmSVEl = bkgOnly.addValidationChannel("nJet",["SVEl"],(nJetZsmBinHigh-nJetZsmBinLow),nJetZsmBinLow,nJetZsmBinHigh)
    mmSVMu = bkgOnly.addValidationChannel("nJet",["SVMu"],(nJetZsmBinHigh-nJetZsmBinLow),nJetZsmBinLow,nJetZsmBinHigh)
    softLepValChannels = [mmSVEl,mmSVMu]
    if not useSoftLepCR:
        mmSVWEl = bkgOnly.addValidationChannel("nJet",["SVWEl"],(nJetZsmBinHigh-nJetZsmBinLow),nJetZsmBinLow,nJetZsmBinHigh)
        mmSVWMu = bkgOnly.addValidationChannel("nJet",["SVWMu"],(nJetZsmBinHigh-nJetZsmBinLow),nJetZsmBinLow,nJetZsmBinHigh)
        mmSVTEl = bkgOnly.addValidationChannel("nJet",["SVTEl"],(nJetZsmBinHigh-nJetZsmBinLow),nJetZsmBinLow,nJetZsmBinHigh)
        mmSVTMu = bkgOnly.addValidationChannel("nJet",["SVTMu"],(nJetZsmBinHigh-nJetZsmBinLow),nJetZsmBinLow,nJetZsmBinHigh)
        softLepValChannels += [mmSVWEl,mmSVWMu,mmSVTEl,mmSVTMu]
        
    bkgOnly.setValidationChannels(softLepValChannels)

    validationSoftLepChannels = [mmSVEl, mmSVMu]
    validationSoftLepBtagChannels =  []
    validationSoftLepBvetoChannels =  []


    # add systematics
    for chan in validationSoftLepChannels:
        chan.useOverflowBin = True
        chan.removeWeight("bTagWeight3Jet")

    if not useSoftLepCR:

        validationSoftLepBtagChannels =  [mmSVTEl, mmSVTMu]
        validationSoftLepBvetoChannels =  [mmSVWEl, mmSVWMu]

        # add systematics
        for chan in validationSoftLepBtagChannels:
            chan.hasBQCD = True
            chan.useOverflowBin = True
            for syst in btagChanSyst:
                chan.addSystematic(syst)

        # add systematics
        for chan in validationSoftLepBvetoChannels:
            chan.hasBQCD = False
            chan.useOverflowBin = True
            for syst in btagChanSyst:
                chan.addSystematic(syst)

    for chan in validationSoftLepChannels+validationSoftLepBtagChannels+validationSoftLepBvetoChannels:
        if chan.name.find("El")>-1:
            chan.setFileList(bgdFiles_se)
        else:
            chan.setFileList(bgdFiles_sm)


#-------------------------------------------------
# Exclusion fit
#-------------------------------------------------

if doExclusion_GMSB_combined or doExclusion_mSUGRA_dilepton_combined or doExclusion_GG_twostepCC_slepton or doExclusion_GG_onestepCC_x12 or doExclusion_GG_onestepCC_gridX:


    for sig in sigSamples:
        myTopLvl = configMgr.addTopLevelXMLClone(bkgOnly,"Sig_%s"%sig)

        sigSample = Sample(sig,kPink)
        sigSample.setFileList(sigFiles)
        sigSample.setNormByTheory()
        sigSample.setNormFactor("mu_SIG",1.,0.,5.)

        #signal-specific uncertainties
        sigSample.setStatConfig(useStat)
        sigSample.addSystematic(jesSignal)
        if useXsecUnc:
            sigSample.addSystematic(xsecSig)
        if sig.startswith("SM"):
            from SystematicsUtils import getISRSyst
            isrSyst = getISRSyst(sig)
            sigSample.addSystematic(isrSyst)

        myTopLvl.addSamples(sigSample)
        myTopLvl.setSignalSample(sigSample)

        
        SRs=["S3El","S3Mu","S4El","S4Mu","S2ee","S2em","S2mm","S4ee","S4em","S4mm"]
        if doExclusion_GMSB_combined:
            SRs=["S2ee","S2em","S2mm"]
        elif doExclusion_mSUGRA_dilepton_combined:
               SRs=["S3El","S3Mu","S4El","S4Mu","S2ee","S2em","S2mm","S4ee","S4em","S4mm"]
            #  SRs=["S2ee","S2em","S2mm","S4ee","S4em","S4mm"]
        elif doExclusion_GG_twostepCC_slepton:
            SRs=["S4ee","S4em","S4mm"]
        elif doExclusion_GG_onestepCC_x12:
            SRs=["S3El","S3Mu","S4El","S4Mu","SSEl","SSMu"] # only hard lepton so far
        elif doExclusion_GG_onestepCC_gridX:
            SRs=["S3El","S3Mu","S4El","S4Mu"] # only hard lepton so far
            
        if doValidationSRLoose:
            for sr in SRs:
                #don't re-create already existing channel, but unset as Validation and set as Signal channel
                ch = myTopLvl.getChannel("meffInc",[sr])
                iPop=myTopLvl.validationChannels.index(sr+"_meffInc")
                myTopLvl.validationChannels.pop(iPop)
                myTopLvl.setSignalChannels(ch)
                ch.getSample(sig).removeSystematic("JHigh")
                ch.getSample(sig).removeSystematic("JMedium")
                ch.getSample(sig).removeSystematic("JLow")

        else:


            
            for sr in SRs:
                if sr=="S3El" or sr=="S3Mu":
                    ch = myTopLvl.addChannel("meffInc",[sr],meffNBins1lS3,meffBinLow1lS3,meffBinHigh1lS3)
                elif sr=="S4El" or sr=="S4Mu":
                    ch = myTopLvl.addChannel("meffInc",[sr],meffNBins1lS4,meffBinLow1lS4,meffBinHigh1lS4)
                elif sr=="S2ee" or sr=="S2em" or sr=="S2mm":
                    ch = myTopLvl.addChannel("meffInc",[sr],meffNBinsS2,meffBinLowS2,meffBinHighS2)
                elif sr=="S4ee" or sr=="S4em" or sr=="S4mm":
                    ch = myTopLvl.addChannel("meffInc",[sr],meffNBinsS4,meffBinLowS4,meffBinHighS4)
                elif sr=="SSEl" or sr=="SSMu":
                    ch = myTopLvl.addChannel("met/meff2Jet",[sr],6,0.1,0.7)
                    
                else:
                    raise RuntimeError("Unexpected signal region %s"%sr)
                
                ch.useOverflowBin=True
                ch.removeWeight("bTagWeight3Jet")

                if (ch.name.find("S3El")>-1 or ch.name.find("S4El")>-1):
                    ch.setFileList(bgdFiles_e)
                elif ch.name.find("SSEl")>-1:
                    ch.setFileList(bgdFiles_se)
                elif (ch.name.find("S3Mu")>-1 or ch.name.find("S4Mu")>-1):
                    ch.setFileList(bgdFiles_m)
                elif ch.name.find("SSMu")>-1:
                    ch.setFileList(bgdFiles_sm)
                elif ch.name.find("ee")>-1:
                    ch.setFileList(bgdFiles_ee)
                elif ch.name.find("em")>-1:
                    ch.setFileList(bgdFiles_em)
                elif ch.name.find("mm")>-1:
                    ch.setFileList(bgdFiles_mm)
                    
                                    
                myTopLvl.setSignalChannels(ch)        
                ch.getSample(sig).removeSystematic("JHigh")
                ch.getSample(sig).removeSystematic("JMedium")
                ch.getSample(sig).removeSystematic("JLow")
        

        for (iChan,chan) in enumerate(myTopLvl.channels):
            if chan.name.find("El")>-1:
                if not chan.name.find("SS")>-1 :
                    chan.getSample(sig).setFileList(sigFiles_l)
                else:
                    chan.getSample(sig).setFileList(sigFiles_sl)
                if fullSyst:
                    chan.getSample(sig).removeSystematic("LES")
                    chan.getSample(sig).removeSystematic("LRM")
                    chan.getSample(sig).removeSystematic("LRI")                
            elif chan.name.find("Mu")>-1:
                if not chan.name.find("SS")>-1 :
                    chan.getSample(sig).setFileList(sigFiles_l)
                else:
                    chan.getSample(sig).setFileList(sigFiles_sl)
                if fullSyst:
                    chan.getSample(sig).removeSystematic("LES")
                    chan.getSample(sig).removeSystematic("LRM")
                    chan.getSample(sig).removeSystematic("LRI")       
            elif chan.name.find("ee")>-1:
                chan.getSample(sig).setFileList(sigFiles)
            elif chan.name.find("em")>-1:
                chan.getSample(sig).setFileList(sigFiles)
            elif chan.name.find("mm")>-1:
                chan.getSample(sig).setFileList(sigFiles)
                
