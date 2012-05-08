
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
doValidationSlope=True
doDiscoveryS2=False
doDiscoveryS4=False
doDiscovery=False
doDiscoveryTight=False
discoverychannel="ee" # ee, emu, mumu
doExclusion=False
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

# Set the files to read from
if configMgr.readFromTree:
# I've provided trees for ee, emu, mumu using 4.7fb data
# ln -s /afs/cern.ch/atlas/groups/susy/1lepton/samples2/SusyFitterTree_EleEle.root etc
    configMgr.inputFileNames = ["data/SusyFitterTree_EleEle.root","data/SusyFitterTree_EleMu.root","data/SusyFitterTree_MuMu.root","data/SusyFitterTree_OneEle.root","data/SusyFitterTree_OneMu.root"]
    if doExclusion:
        configMgr.inputFileNames+=["data/SusyFitterTree_EleEle_GMSB.root","data/SusyFitterTree_EleMu_GMSB.root","data/SusyFitterTree_MuMu_GMSB.root"]
##        configMgr.inputFileNames+=["data/SusyFitterTree_EleEle_mSUGRA.root","data/SusyFitterTree_EleMu_mSUGRA.root","data/SusyFitterTree_MuMu_mSUGRA.root"]
else:
    configMgr.inputFileNames = ["data/"+configMgr.analysisName+".root"]



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
                      
                      "WREl":"lep2Pt<10 && met>30 && met<120 && mt>40 && mt<80 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc > 400 && AnalysisType==1",
                      "TREl":"lep2Pt<10 && met>30 && met<120 && mt>40 && mt<80 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && meffInc > 400 && AnalysisType==1",
                      "WRMu":"lep2Pt<10 && met>30 && met<120 && mt>40 && mt<80 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc > 400 && AnalysisType==2",
                      "TRMu":"lep2Pt<10 && met>30 && met<120 && mt>40 && mt<80 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && meffInc > 400 && AnalysisType==2",

                      "TRElVR":"lep2Pt<10 && met>30 && met<120 && mt>40 && mt<80 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==1",
                      "TRMuVR":"lep2Pt<10 && met>30 && met<120 && mt>40 && mt<80 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==2",

                      "TRElVR2":"lep2Pt<10 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==1",
                      "TRMuVR2":"lep2Pt<10 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==2", 

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
configMgr.weights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"bTagWeight3Jet")
configMgr.weightsQCD = "qcdWeight"
configMgr.weightsQCDWithB = "qcdBWeight"

xsecSigHighWeights = ("genWeightUp","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"bTagWeight3Jet")
xsecSigLowWeights = ("genWeightDown","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"bTagWeight3Jet")

#ktScaleWHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"ktfacUpWeightW","bTagWeight3Jet")
#ktScaleWLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"ktfacDownWeightW","bTagWeight3Jet")
                    
#ktScaleTopHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"ktfacUpWeightTop","bTagWeight3Jet")
#ktScaleTopLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"ktfacDownWeightTop","bTagWeight3Jet")

#noWPtWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","bTagWeight3Jet")
#noWPtWeightsHigh = ("genWeight","eventWeight","leptonWeight","triggerWeight","(1+(truthWptWeight-1)/2)","bTagWeight3Jet")
#noWPtWeightsLow = ("genWeight","eventWeight","leptonWeight","triggerWeight","(1+(truthWptWeight-1)*1.5)","bTagWeight3Jet")

bTagHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"bTagWeight3JetUp")
bTagLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"bTagWeight3JetDown")

trigHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeightUp",truthWptWeight,"bTagWeight3Jet")
trigLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeightDown",truthWptWeight,"bTagWeight3Jet")

lepHighWeights = ("genWeight","eventWeight","leptonWeightUp","triggerWeight",truthWptWeight,"bTagWeight3Jet")
lepLowWeights = ("genWeight","eventWeight","leptonWeightDown","triggerWeight",truthWptWeight,"bTagWeight3Jet")


                                                                                        
#--------------------
# List of systematics
#--------------------



# KtScale uncertainty as histoSys - two-sided, no additional normalization
#topKtScale = Systematic("KtScaleTop",configMgr.weights,ktScaleTopHighWeights,ktScaleTopLowWeights,"weight","normHistoSys")
#wzKtScale = Systematic("KtScaleWZ",configMgr.weights,ktScaleWHighWeights,ktScaleWLowWeights,"weight","normHistoSys")

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
bgSample = Sample("BG",kGreen)
bgSample.setNormFactor("mu_BG",1.,0.,5.)
bgSample.setStatConfig(useStat)
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
bkgOnly.addSamples([qcdSample,bgSample,topSample_Np0,topSample_Np1,topSample_Np2,topSample_Np3,topSample_Np4,topSample_Np5,wzSample_Np0,wzSample_Np1,wzSample_Np2,wzSample_Np3,wzSample_Np4,wzSample_Np5,dataSample])

if useStat:
    bkgOnly.statErrThreshold=0.05 #0.03??
else:
    bkgOnly.statErrThreshold=None


#bkgOnly.getSample("Top").addSystematic(topKtScale)
#bkgOnly.getSample("WZ").addSystematic(wzKtScale)


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


##### nJet for Top ####

# ele ele

nJetTopeeChannel=bkgOnly.addChannel("nJet",nJetTopeeRegions,nJetTopeeNBins,nJetTopeeBinLow,nJetTopeeBinHigh)
nJetTopeeChannel.hasB = True
nJetTopeeChannel.hasBQCD = True
nJetTopeeChannel.useOverflowBin = False
nJetTopeeChannel.addSystematic(jesLow)
nJetTopeeChannel.addSystematic(jesMedium)
nJetTopeeChannel.addSystematic(jesHigh)
#[s.mergeSamples([topSample_Np0.name,wzSample_Np0.name,topSample_Np1.name,wzSample_Np1.name,topSample_Np2.name,wzSample_Np2.name,topSample_Np3.name,wzSample_Np3.name,topSample_Np4.name,wzSample_Np4.name,topSample_Np5.name,wzSample_Np5.name,bgSample.name]) for s in nJetTopeeChannel.getSystematic(jesTR.name)]
nJetTopeeChannel.addSystematic(btagTR)
nJetTopeeChannel.addSystematic(lepTR)
if fullSyst:
    nJetTopeeChannel.addSystematic(metcoTR)
    nJetTopeeChannel.addSystematic(metpuTR)
    nJetTopeeChannel.addSystematic(trigTR)
    [nJetTopeeChannel.getSample(sam).addSystematic(lesTR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]
    [nJetTopeeChannel.getSample(sam).addSystematic(lermsTR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]
    [nJetTopeeChannel.getSample(sam).addSystematic(leridTR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]


#  single ele

nJetTopeChannel=bkgOnly.addChannel("nJet",nJetTopeRegions,nJetTopeNBins,nJetTopeBinLow,nJetTopeBinHigh)
nJetTopeChannel.hasB = True
nJetTopeChannel.hasBQCD = True
nJetTopeChannel.useOverflowBin = False
nJetTopeChannel.addSystematic(jesLow)
nJetTopeChannel.addSystematic(jesMedium)
nJetTopeChannel.addSystematic(jesHigh)
#[s.mergeSamples([topSample_Np0.name,wzSample_Np0.name,topSample_Np1.name,wzSample_Np1.name,topSample_Np2.name,wzSample_Np2.name,topSample_Np3.name,wzSample_Np3.name,topSample_Np4.name,wzSample_Np4.name,topSample_Np5.name,wzSample_Np5.name,bgSample.name]) for s in nJetTopeChannel.getSystematic(jesTR.name)]
nJetTopeChannel.addSystematic(btagTR)
nJetTopeChannel.addSystematic(lepTR)
if fullSyst:
    nJetTopeChannel.addSystematic(metcoTR)
    nJetTopeChannel.addSystematic(metpuTR)
    nJetTopeChannel.addSystematic(trigTR)
    [nJetTopeChannel.getSample(sam).addSystematic(lesTR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]
    [nJetTopeChannel.getSample(sam).addSystematic(lermsTR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]
    [nJetTopeChannel.getSample(sam).addSystematic(leridTR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]    


#  ele mu

nJetTopemChannel=bkgOnly.addChannel("nJet",nJetTopemRegions,nJetTopemNBins,nJetTopemBinLow,nJetTopemBinHigh)
nJetTopemChannel.hasB = True
nJetTopemChannel.hasBQCD = True
nJetTopemChannel.useOverflowBin = False
nJetTopemChannel.addSystematic(jesLow)
nJetTopemChannel.addSystematic(jesMedium)
nJetTopemChannel.addSystematic(jesHigh)
#[s.mergeSamples([topSample_Np0.name,wzSample_Np0.name,topSample_Np1.name,wzSample_Np1.name,topSample_Np2.name,wzSample_Np2.name,topSample_Np3.name,wzSample_Np3.name,topSample_Np4.name,wzSample_Np4.name,topSample_Np5.name,wzSample_Np5.name,bgSample.name]) for s in nJetTopemChannel.getSystematic(jesTR.name)]
nJetTopemChannel.addSystematic(btagTR)
nJetTopemChannel.addSystematic(lepTR)
if fullSyst:
    nJetTopemChannel.addSystematic(metcoTR)
    nJetTopemChannel.addSystematic(metpuTR)
    nJetTopemChannel.addSystematic(trigTR)
    [nJetTopemChannel.getSample(sam).addSystematic(lesTR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]
    [nJetTopemChannel.getSample(sam).addSystematic(lermsTR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]
    [nJetTopemChannel.getSample(sam).addSystematic(leridTR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]


# mu mu

nJetTopmmChannel=bkgOnly.addChannel("nJet",nJetTopmmRegions,nJetTopmmNBins,nJetTopmmBinLow,nJetTopmmBinHigh)
nJetTopmmChannel.hasB = True
nJetTopmmChannel.hasBQCD = True
nJetTopmmChannel.useOverflowBin = False
nJetTopmmChannel.addSystematic(jesLow)
nJetTopmmChannel.addSystematic(jesMedium)
nJetTopmmChannel.addSystematic(jesHigh)
#[s.mergeSamples([topSample_Np0.name,wzSample_Np0.name,topSample_Np1.name,wzSample_Np1.name,topSample_Np2.name,wzSample_Np2.name,topSample_Np3.name,wzSample_Np3.name,topSample_Np4.name,wzSample_Np4.name,topSample_Np5.name,wzSample_Np5.name,bgSample.name]) for s in nJetTopmmChannel.getSystematic(jesTR.name)]
nJetTopmmChannel.addSystematic(btagTR)
nJetTopmmChannel.addSystematic(lepTR)
if fullSyst:
    nJetTopmmChannel.addSystematic(metcoTR)
    nJetTopmmChannel.addSystematic(metpuTR)
    nJetTopmmChannel.addSystematic(trigTR)
    [nJetTopmmChannel.getSample(sam).addSystematic(lesTR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]
    [nJetTopmmChannel.getSample(sam).addSystematic(lermsTR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]
    [nJetTopmmChannel.getSample(sam).addSystematic(leridTR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]


# single mu

nJetTopmChannel=bkgOnly.addChannel("nJet",nJetTopmRegions,nJetTopmNBins,nJetTopmBinLow,nJetTopmBinHigh)
nJetTopmChannel.hasB = True
nJetTopmChannel.hasBQCD = True
nJetTopmChannel.useOverflowBin = False
nJetTopmChannel.addSystematic(jesLow)
nJetTopmChannel.addSystematic(jesMedium)
nJetTopmChannel.addSystematic(jesHigh)
#[s.mergeSamples([topSample_Np0.name,wzSample_Np0.name,topSample_Np1.name,wzSample_Np1.name,topSample_Np2.name,wzSample_Np2.name,topSample_Np3.name,wzSample_Np3.name,topSample_Np4.name,wzSample_Np4.name,topSample_Np5.name,wzSample_Np5.name,bgSample.name]) for s in nJetTopmChannel.getSystematic(jesTR.name)]
nJetTopmChannel.addSystematic(btagTR)
nJetTopmChannel.addSystematic(lepTR)
if fullSyst:
    nJetTopmChannel.addSystematic(metcoTR)
    nJetTopmChannel.addSystematic(metpuTR)
    nJetTopmChannel.addSystematic(trigTR)
    [nJetTopmChannel.getSample(sam).addSystematic(lesTR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]
    [nJetTopmChannel.getSample(sam).addSystematic(lermsTR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]
    [nJetTopmChannel.getSample(sam).addSystematic(leridTR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]
    

####### nJet for W/Z  #######
    
# ele ele    

nJetZeeChannel=bkgOnly.addChannel("nJet",nJetZeeRegions,nJetZeeNBins,nJetZeeBinLow,nJetZeeBinHigh)
nJetZeeChannel.hasB = False
nJetZeeChannel.hasBQCD = False
nJetZeeChannel.addSystematic(jesLow)
nJetZeeChannel.addSystematic(jesMedium)
nJetZeeChannel.addSystematic(jesHigh)
#[s.mergeSamples([topSample_Np0.name,wzSample_Np0.name,topSample_Np1.name,wzSample_Np1.name,topSample_Np2.name,wzSample_Np2.name,topSample_Np3.name,wzSample_Np3.name,topSample_Np4.name,wzSample_Np4.name,topSample_Np5.name,wzSample_Np5.name,bgSample.name]) for s in nJetZeeChannel.getSystematic(jesZR.name)]
#nJetZeeChannel.addSystematic(btagZR)
nJetZeeChannel.addSystematic(lepZR)
if fullSyst:
    nJetZeeChannel.addSystematic(metcoZR)
    nJetZeeChannel.addSystematic(metpuZR)
    nJetZeeChannel.addSystematic(trigZR)
    [nJetZeeChannel.getSample(sam).addSystematic(lesZR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]
    [nJetZeeChannel.getSample(sam).addSystematic(lermsZR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]
    [nJetZeeChannel.getSample(sam).addSystematic(leridZR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]


# single ele

nJetZeChannel=bkgOnly.addChannel("nJet",nJetZeRegions,nJetZeNBins,nJetZeBinLow,nJetZeBinHigh)
nJetZeChannel.hasB = False
nJetZeChannel.hasBQCD = False
nJetZeChannel.addSystematic(jesLow)
nJetZeChannel.addSystematic(jesMedium)
nJetZeChannel.addSystematic(jesHigh)
#[s.mergeSamples([topSample_Np0.name,wzSample_Np0.name,topSample_Np1.name,wzSample_Np1.name,topSample_Np2.name,wzSample_Np2.name,topSample_Np3.name,wzSample_Np3.name,topSample_Np4.name,wzSample_Np4.name,topSample_Np5.name,wzSample_Np5.name,bgSample.name]) for s in nJetZeChannel.getSystematic(jesZR.name)]
nJetZeChannel.addSystematic(btagZR)
nJetZeChannel.addSystematic(lepZR)
if fullSyst:
    nJetZeChannel.addSystematic(metcoZR)
    nJetZeChannel.addSystematic(metpuZR)
    nJetZeChannel.addSystematic(trigZR)
    [nJetZeChannel.getSample(sam).addSystematic(lesZR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]
    [nJetZeChannel.getSample(sam).addSystematic(lermsZR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]
    [nJetZeChannel.getSample(sam).addSystematic(leridZR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]    

  
# mu mu

nJetZmmChannel=bkgOnly.addChannel("nJet",nJetZmmRegions,nJetZmmNBins,nJetZmmBinLow,nJetZmmBinHigh)
nJetZmmChannel.hasB = False
nJetZmmChannel.hasBQCD = False
nJetZmmChannel.addSystematic(jesLow)
nJetZmmChannel.addSystematic(jesMedium)
nJetZmmChannel.addSystematic(jesHigh)
#[s.mergeSamples([topSample_Np0.name,wzSample_Np0.name,topSample_Np1.name,wzSample_Np1.name,topSample_Np2.name,wzSample_Np2.name,topSample_Np3.name,wzSample_Np3.name,topSample_Np4.name,wzSample_Np4.name,topSample_Np5.name,wzSample_Np5.name,bgSample.name]) for s in nJetZmmChannel.getSystematic(jesZR.name)]
#nJetZmmChannel.addSystematic(btagZR)
nJetZmmChannel.addSystematic(lepZR)
if fullSyst:
    nJetZmmChannel.addSystematic(metcoZR)
    nJetZmmChannel.addSystematic(metpuZR)
    nJetZmmChannel.addSystematic(trigZR)
    [nJetZmmChannel.getSample(sam).addSystematic(lesZR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]
    [nJetZmmChannel.getSample(sam).addSystematic(lermsZR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]
    [nJetZmmChannel.getSample(sam).addSystematic(leridZR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]


# single mu

nJetZmChannel=bkgOnly.addChannel("nJet",nJetZmRegions,nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
nJetZmChannel.hasB = False
nJetZmChannel.hasBQCD = False
nJetZmChannel.addSystematic(jesLow)
nJetZmChannel.addSystematic(jesMedium)
nJetZmChannel.addSystematic(jesHigh)
#[s.mergeSamples([topSample_Np0.name,wzSample_Np0.name,topSample_Np1.name,wzSample_Np1.name,topSample_Np2.name,wzSample_Np2.name,topSample_Np3.name,wzSample_Np3.name,topSample_Np4.name,wzSample_Np4.name,topSample_Np5.name,wzSample_Np5.name,bgSample.name]) for s in nJetZmChannel.getSystematic(jesZR.name)]
nJetZmChannel.addSystematic(btagZR)
nJetZmChannel.addSystematic(lepZR)
if fullSyst:
    nJetZmChannel.addSystematic(metcoZR)
    nJetZmChannel.addSystematic(metpuZR)
    nJetZmChannel.addSystematic(trigZR)
    [nJetZmChannel.getSample(sam).addSystematic(lesZR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]
    [nJetZmChannel.getSample(sam).addSystematic(lermsZR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]
    [nJetZmChannel.getSample(sam).addSystematic(leridZR) for sam in ["Top_Np0","WZ_Np0","Top_Np1","WZ_Np1","Top_Np2","WZ_Np2","Top_Np3","WZ_Np3","Top_Np4","WZ_Np4","Top_Np5","WZ_Np5","BG"]]    
                                                                            


#ZptZeeChannel=bkgOnly.addChannel("Zpt",ZptZeeRegions,ZptZeeNBins,ZptZeeBinLow,ZptZeeBinHigh)
#ZptZmmChannel=bkgOnly.addChannel("Zpt",ZptZmmRegions,ZptZmmNBins,ZptZmmBinLow,ZptZmmBinHigh)
#ZptZeeChannel.addSystematic(jes)
#ZptZeeChannel.useOverflowBin=True
#ZptZmmChannel.useOverflowBin=True
#bkgOnly.setBkgConstrainChannels([nJetTopeeChannel,nJetZeeChannel,nJetTopeChannel,nJetZeChannel,nJetTopemChannel,nJetTopmmChannel,nJetZmmChannel,nJetTopmChannel,nJetZmChannel])
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

if doValidationSR:

    # S2 using meff
    meff2ee = bkgOnly.addChannel("meffInc",["S2ee"],meffNBins,meffBinLow,meffBinHigh)
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
    meff4ee = bkgOnly.addChannel("meffInc",["S4ee"],meffNBins,meffBinLow,meffBinHigh)
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
    meff2em = bkgOnly.addChannel("meffInc",["S2em"],meffNBins,meffBinLow,meffBinHigh)
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
    meff4em = bkgOnly.addChannel("meffInc",["S4em"],meffNBins,meffBinLow,meffBinHigh)
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
    meff2mm = bkgOnly.addChannel("meffInc",["S2mm"],meffNBins,meffBinLow,meffBinHigh)
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
    meff4mm = bkgOnly.addChannel("meffInc",["S4mm"],meffNBins,meffBinLow,meffBinHigh)
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


    meffS3T_El=bkgOnly.addChannel("meffInc",["SR3jTEl"],1,meffBinLowHL,meffBinHighHL)
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


    meffS3T_Mu=bkgOnly.addChannel("meffInc",["SR3jTMu"],1,meffBinLowHL,meffBinHighHL)
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


    meffS4T_El=bkgOnly.addChannel("meffInc",["SR4jTEl"],1,meffBinLowHL,meffBinHighHL)
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


    meffS4T_Mu=bkgOnly.addChannel("meffInc",["SR4jTMu"],1,meffBinLowHL,meffBinHighHL)
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
            
        

if doValidationSR:
    bkgOnly.setValidationChannels([meff2ee,meff4ee,meff2em,meff4em,meff2mm,meff4mm,meffS3_El,meffS3_Mu,meffS4_El,meffS4_Mu,meffS3T_El,meffS3T_Mu,meffS4T_El,meffS4T_Mu])

if doValidationSlope:
    bkgOnly.setValidationChannels([meffTR_El,meffTR_Mu,metTR_El,metTR_Mu,pt1TR_El,pt1TR_Mu,pt2TR_El,pt2TR_Mu])

