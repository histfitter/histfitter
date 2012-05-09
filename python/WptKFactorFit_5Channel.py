
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
doValidationSR=True
doValidationSlope=False
doExclusion=False
blindS=False
fullSyst=True
useXsecUnc=True             # switch off when calucating excluded cross section (colour code in SM plots)
doWptReweighting=False ## currently buggy

# First define HistFactory attributes
configMgr.analysisName = "WptKFactorFit_5Channel" # Name to give the analysis
configMgr.outputFileName = "results/WptKFactorFit_5Channel.root"

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
    configMgr.inputFileNames = ["macros/macros_ysasaki/EleEle.root","macros/macros_ysasaki/EleMu.root","macros/macros_ysasaki/MuMu.root","macros/macros_ysasaki/OneEle.root","macros/macros_ysasaki/OneMu.root"]
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

                      "WRElVR":"lep2Pt<10 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==1",
                      "WRMuVR":"lep2Pt<10 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && AnalysisType==2",

                      "WRElVR2":"lep2Pt<10 && met>30 && mt>40 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc > 400 && AnalysisType==1",
                      "WRMuVR2":"lep2Pt<10 && met>30 && mt>40 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc > 400 && AnalysisType==2",

                      "WREl2":"lep2Pt<10 && met>30 && met<120 && mt>40 && mt<80 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc > 400 && AnalysisType==1",
                      "WRMu2":"lep2Pt<10 && met>30 && met<120 && mt>40 && mt<80 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc > 400 && AnalysisType==2",
                      
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

bTagHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"bTagWeight3JetUp")
bTagLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight",truthWptWeight,"bTagWeight3JetDown")

trigHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeightUp",truthWptWeight,"bTagWeight3Jet")
trigLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeightDown",truthWptWeight,"bTagWeight3Jet")

lepHighWeights = ("genWeight","eventWeight","leptonWeightUp","triggerWeight",truthWptWeight,"bTagWeight3Jet")
lepLowWeights = ("genWeight","eventWeight","leptonWeightDown","triggerWeight",truthWptWeight,"bTagWeight3Jet")


                                                                                       
#--------------------
# List of systematics
#--------------------

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
jesZpt = Systematic("JZpt","_NoSys","_JESup","_JESdown","tree","overallSys")

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


#### SAMPLES #####

# WZ 

wzSample_Np0_DpT0GeV = Sample("WZpT0GeV_Np0",kBlue+0)
wzSample_Np0_DpT0GeV.setNormFactor("mu_WZ_pT0GeV",1.,0.,5.)
wzSample_Np0_DpT0GeV.addNormFactor("mu_WZ_Np0",1.,5.,0.)
wzSample_Np0_DpT0GeV.setStatConfig(useStat)

wzSample_Np0_DpT50GeV = Sample("WZpT50GeV_Np0",kYellow+0)
wzSample_Np0_DpT50GeV.setNormFactor("mu_WZ_pT50GeV",1.,0.,5.)
wzSample_Np0_DpT50GeV.addNormFactor("mu_WZ_Np0",1.,5.,0.)
wzSample_Np0_DpT50GeV.setStatConfig(useStat)

wzSample_Np0_DpT100GeV = Sample("WZpT100GeV_Np0",kBlue+1)
wzSample_Np0_DpT100GeV.setNormFactor("mu_WZ_pT100GeV",1.,0.,5.)
wzSample_Np0_DpT100GeV.addNormFactor("mu_WZ_Np0",1.,5.,0.)
wzSample_Np0_DpT100GeV.setStatConfig(useStat)

wzSample_Np0_DpT150GeV = Sample("WZpT150GeV_Np0",kYellow+1)
wzSample_Np0_DpT150GeV.setNormFactor("mu_WZ_pT150GeV",1.,0.,5.)
wzSample_Np0_DpT150GeV.addNormFactor("mu_WZ_Np0",1.,5.,0.)
wzSample_Np0_DpT150GeV.setStatConfig(useStat)

wzSample_Np0_DpT200GeV = Sample("WZpT200GeV_Np0",kBlue+2)
wzSample_Np0_DpT200GeV.setNormFactor("mu_WZ_pT200GeV",1.,0.,5.)
wzSample_Np0_DpT200GeV.addNormFactor("mu_WZ_Np0",1.,5.,0.)
wzSample_Np0_DpT200GeV.setStatConfig(useStat)

wzSample_Np0_DpT250GeV = Sample("WZpT250GeV_Np0",kYellow+2)
wzSample_Np0_DpT250GeV.setNormFactor("mu_WZ_pT200GeV",1.,0.,5.)
wzSample_Np0_DpT250GeV.addNormFactor("mu_WZ_Np0",1.,5.,0.)
wzSample_Np0_DpT250GeV.setStatConfig(useStat)

wzSample_Np1_DpT0GeV = Sample("WZpT0GeV_Np1",kBlue+0)
wzSample_Np1_DpT0GeV.setNormFactor("mu_WZ_pT0GeV",1.,0.,5.)
wzSample_Np1_DpT0GeV.addNormFactor("mu_WZ_Np1",1.,5.,0.)
wzSample_Np1_DpT0GeV.setStatConfig(useStat)

wzSample_Np1_DpT50GeV = Sample("WZpT50GeV_Np1",kYellow+0)
wzSample_Np1_DpT50GeV.setNormFactor("mu_WZ_pT50GeV",1.,0.,5.)
wzSample_Np1_DpT50GeV.addNormFactor("mu_WZ_Np1",1.,5.,0.)
wzSample_Np1_DpT50GeV.setStatConfig(useStat)

wzSample_Np1_DpT100GeV = Sample("WZpT100GeV_Np1",kBlue+1)
wzSample_Np1_DpT100GeV.setNormFactor("mu_WZ_pT100GeV",1.,0.,5.)
wzSample_Np1_DpT100GeV.addNormFactor("mu_WZ_Np1",1.,5.,0.)
wzSample_Np1_DpT100GeV.setStatConfig(useStat)

wzSample_Np1_DpT150GeV = Sample("WZpT150GeV_Np1",kYellow+1)
wzSample_Np1_DpT150GeV.setNormFactor("mu_WZ_pT150GeV",1.,0.,5.)
wzSample_Np1_DpT150GeV.addNormFactor("mu_WZ_Np1",1.,5.,0.)
wzSample_Np1_DpT150GeV.setStatConfig(useStat)

wzSample_Np1_DpT200GeV = Sample("WZpT200GeV_Np1",kBlue+2)
wzSample_Np1_DpT200GeV.setNormFactor("mu_WZ_pT200GeV",1.,0.,5.)
wzSample_Np1_DpT200GeV.addNormFactor("mu_WZ_Np1",1.,5.,0.)
wzSample_Np1_DpT200GeV.setStatConfig(useStat)

wzSample_Np1_DpT250GeV = Sample("WZpT250GeV_Np1",kYellow+2)
wzSample_Np1_DpT250GeV.setNormFactor("mu_WZ_pT200GeV",1.,0.,5.)
wzSample_Np1_DpT250GeV.addNormFactor("mu_WZ_Np1",1.,5.,0.)
wzSample_Np1_DpT250GeV.setStatConfig(useStat)

wzSample_Np2_DpT0GeV = Sample("WZpT0GeV_Np2",kBlue+0)
wzSample_Np2_DpT0GeV.setNormFactor("mu_WZ_pT0GeV",1.,0.,5.)
wzSample_Np2_DpT0GeV.addNormFactor("mu_WZ_Np2",1.,5.,0.)
wzSample_Np2_DpT0GeV.setStatConfig(useStat)

wzSample_Np2_DpT50GeV = Sample("WZpT50GeV_Np2",kYellow+0)
wzSample_Np2_DpT50GeV.setNormFactor("mu_WZ_pT50GeV",1.,0.,5.)
wzSample_Np2_DpT50GeV.addNormFactor("mu_WZ_Np2",1.,5.,0.)
wzSample_Np2_DpT50GeV.setStatConfig(useStat)

wzSample_Np2_DpT100GeV = Sample("WZpT100GeV_Np2",kBlue+1)
wzSample_Np2_DpT100GeV.setNormFactor("mu_WZ_pT100GeV",1.,0.,5.)
wzSample_Np2_DpT100GeV.addNormFactor("mu_WZ_Np2",1.,5.,0.)
wzSample_Np2_DpT100GeV.setStatConfig(useStat)

wzSample_Np2_DpT150GeV = Sample("WZpT150GeV_Np2",kYellow+1)
wzSample_Np2_DpT150GeV.setNormFactor("mu_WZ_pT150GeV",1.,0.,5.)
wzSample_Np2_DpT150GeV.addNormFactor("mu_WZ_Np2",1.,5.,0.)
wzSample_Np2_DpT150GeV.setStatConfig(useStat)

wzSample_Np2_DpT200GeV = Sample("WZpT200GeV_Np2",kBlue+2)
wzSample_Np2_DpT200GeV.setNormFactor("mu_WZ_pT200GeV",1.,0.,5.)
wzSample_Np2_DpT200GeV.addNormFactor("mu_WZ_Np2",1.,5.,0.)
wzSample_Np2_DpT200GeV.setStatConfig(useStat)

wzSample_Np2_DpT250GeV = Sample("WZpT250GeV_Np2",kYellow+2)
wzSample_Np2_DpT250GeV.setNormFactor("mu_WZ_pT200GeV",1.,0.,5.)
wzSample_Np2_DpT250GeV.addNormFactor("mu_WZ_Np2",1.,5.,0.)
wzSample_Np2_DpT250GeV.setStatConfig(useStat)

wzSample_Np3_DpT0GeV = Sample("WZpT0GeV_Np3",kBlue+0)
wzSample_Np3_DpT0GeV.setNormFactor("mu_WZ_pT0GeV",1.,0.,5.)
wzSample_Np3_DpT0GeV.addNormFactor("mu_WZ_Np3",1.,5.,0.)
wzSample_Np3_DpT0GeV.setStatConfig(useStat)

wzSample_Np3_DpT50GeV = Sample("WZpT50GeV_Np3",kYellow+0)
wzSample_Np3_DpT50GeV.setNormFactor("mu_WZ_pT50GeV",1.,0.,5.)
wzSample_Np3_DpT50GeV.addNormFactor("mu_WZ_Np3",1.,5.,0.)
wzSample_Np3_DpT50GeV.setStatConfig(useStat)

wzSample_Np3_DpT100GeV = Sample("WZpT100GeV_Np3",kBlue+1)
wzSample_Np3_DpT100GeV.setNormFactor("mu_WZ_pT100GeV",1.,0.,5.)
wzSample_Np3_DpT100GeV.addNormFactor("mu_WZ_Np3",1.,5.,0.)
wzSample_Np3_DpT100GeV.setStatConfig(useStat)

wzSample_Np3_DpT150GeV = Sample("WZpT150GeV_Np3",kYellow+1)
wzSample_Np3_DpT150GeV.setNormFactor("mu_WZ_pT150GeV",1.,0.,5.)
wzSample_Np3_DpT150GeV.addNormFactor("mu_WZ_Np3",1.,5.,0.)
wzSample_Np3_DpT150GeV.setStatConfig(useStat)

wzSample_Np3_DpT200GeV = Sample("WZpT200GeV_Np3",kBlue+2)
wzSample_Np3_DpT200GeV.setNormFactor("mu_WZ_pT200GeV",1.,0.,5.)
wzSample_Np3_DpT200GeV.addNormFactor("mu_WZ_Np3",1.,5.,0.)
wzSample_Np3_DpT200GeV.setStatConfig(useStat)

wzSample_Np3_DpT250GeV = Sample("WZpT250GeV_Np3",kYellow+2)
wzSample_Np3_DpT250GeV.setNormFactor("mu_WZ_pT200GeV",1.,0.,5.)
wzSample_Np3_DpT250GeV.addNormFactor("mu_WZ_Np3",1.,5.,0.)
wzSample_Np3_DpT250GeV.setStatConfig(useStat)

wzSample_Np4_DpT0GeV = Sample("WZpT0GeV_Np4",kBlue+0)
wzSample_Np4_DpT0GeV.setNormFactor("mu_WZ_pT0GeV",1.,0.,5.)
wzSample_Np4_DpT0GeV.addNormFactor("mu_WZ_Np4",1.,5.,0.)
wzSample_Np4_DpT0GeV.setStatConfig(useStat)

wzSample_Np4_DpT50GeV = Sample("WZpT50GeV_Np4",kYellow+0)
wzSample_Np4_DpT50GeV.setNormFactor("mu_WZ_pT50GeV",1.,0.,5.)
wzSample_Np4_DpT50GeV.addNormFactor("mu_WZ_Np4",1.,5.,0.)
wzSample_Np4_DpT50GeV.setStatConfig(useStat)

wzSample_Np4_DpT100GeV = Sample("WZpT100GeV_Np4",kBlue+1)
wzSample_Np4_DpT100GeV.setNormFactor("mu_WZ_pT100GeV",1.,0.,5.)
wzSample_Np4_DpT100GeV.addNormFactor("mu_WZ_Np4",1.,5.,0.)
wzSample_Np4_DpT100GeV.setStatConfig(useStat)

wzSample_Np4_DpT150GeV = Sample("WZpT150GeV_Np4",kYellow+1)
wzSample_Np4_DpT150GeV.setNormFactor("mu_WZ_pT150GeV",1.,0.,5.)
wzSample_Np4_DpT150GeV.addNormFactor("mu_WZ_Np4",1.,5.,0.)
wzSample_Np4_DpT150GeV.setStatConfig(useStat)

wzSample_Np4_DpT200GeV = Sample("WZpT200GeV_Np4",kBlue+2)
wzSample_Np4_DpT200GeV.setNormFactor("mu_WZ_pT200GeV",1.,0.,5.)
wzSample_Np4_DpT200GeV.addNormFactor("mu_WZ_Np4",1.,5.,0.)
wzSample_Np4_DpT200GeV.setStatConfig(useStat)

wzSample_Np4_DpT250GeV = Sample("WZpT250GeV_Np4",kYellow+2)
wzSample_Np4_DpT250GeV.setNormFactor("mu_WZ_pT200GeV",1.,0.,5.)
wzSample_Np4_DpT250GeV.addNormFactor("mu_WZ_Np4",1.,5.,0.)
wzSample_Np4_DpT250GeV.setStatConfig(useStat)

wzSample_Np5_DpT0GeV = Sample("WZpT0GeV_Np5",kBlue+0)
wzSample_Np5_DpT0GeV.setNormFactor("mu_WZ_pT0GeV",1.,0.,5.)
wzSample_Np5_DpT0GeV.addNormFactor("mu_WZ_Np5",1.,5.,0.)
wzSample_Np5_DpT0GeV.setStatConfig(useStat)

wzSample_Np5_DpT50GeV = Sample("WZpT50GeV_Np5",kYellow+0)
wzSample_Np5_DpT50GeV.setNormFactor("mu_WZ_pT50GeV",1.,0.,5.)
wzSample_Np5_DpT50GeV.addNormFactor("mu_WZ_Np5",1.,5.,0.)
wzSample_Np5_DpT50GeV.setStatConfig(useStat)

wzSample_Np5_DpT100GeV = Sample("WZpT100GeV_Np5",kBlue+1)
wzSample_Np5_DpT100GeV.setNormFactor("mu_WZ_pT100GeV",1.,0.,5.)
wzSample_Np5_DpT100GeV.addNormFactor("mu_WZ_Np5",1.,5.,0.)
wzSample_Np5_DpT100GeV.setStatConfig(useStat)

wzSample_Np5_DpT150GeV = Sample("WZpT150GeV_Np5",kYellow+1)
wzSample_Np5_DpT150GeV.setNormFactor("mu_WZ_pT150GeV",1.,0.,5.)
wzSample_Np5_DpT150GeV.addNormFactor("mu_WZ_Np5",1.,5.,0.)
wzSample_Np5_DpT150GeV.setStatConfig(useStat)

wzSample_Np5_DpT200GeV = Sample("WZpT200GeV_Np5",kBlue+2)
wzSample_Np5_DpT200GeV.setNormFactor("mu_WZ_pT200GeV",1.,0.,5.)
wzSample_Np5_DpT200GeV.addNormFactor("mu_WZ_Np5",1.,5.,0.)
wzSample_Np5_DpT200GeV.setStatConfig(useStat)

wzSample_Np5_DpT250GeV = Sample("WZpT250GeV_Np5",kYellow+2)
wzSample_Np5_DpT250GeV.setNormFactor("mu_WZ_pT200GeV",1.,0.,5.)
wzSample_Np5_DpT250GeV.addNormFactor("mu_WZ_Np5",1.,5.,0.)
wzSample_Np5_DpT250GeV.setStatConfig(useStat)


## add external errors on the mu_WZ_TrueZpt
#err_pT0GeV = Systematic("err_pT0GeV", configMgr.weights,,, "user","userOverallSys")
#wzSample_Np0_DpT0GeV.addSystematic(err_pT0GeV)
#wzSample_Np1_DpT0GeV.addSystematic(err_pT0GeV)
#wzSample_Np2_DpT0GeV.addSystematic(err_pT0GeV)
#wzSample_Np3_DpT0GeV.addSystematic(err_pT0GeV)
#wzSample_Np4_DpT0GeV.addSystematic(err_pT0GeV)
#wzSample_Np5_DpT0GeV.addSystematic(err_pT0GeV)

err_pT50GeV = Systematic("err_pT50GeV", configMgr.weights,1.048 ,0.952, "user","userOverallSys")
wzSample_Np0_DpT50GeV.addSystematic(err_pT50GeV)
wzSample_Np1_DpT50GeV.addSystematic(err_pT50GeV)
wzSample_Np2_DpT50GeV.addSystematic(err_pT50GeV)
wzSample_Np3_DpT50GeV.addSystematic(err_pT50GeV)
wzSample_Np4_DpT50GeV.addSystematic(err_pT50GeV)
wzSample_Np5_DpT50GeV.addSystematic(err_pT50GeV)

err_pT100GeV = Systematic("err_pT100GeV", configMgr.weights,1.064,0.936, "user","userOverallSys")
wzSample_Np0_DpT100GeV.addSystematic(err_pT100GeV)
wzSample_Np1_DpT100GeV.addSystematic(err_pT100GeV)
wzSample_Np2_DpT100GeV.addSystematic(err_pT100GeV)
wzSample_Np3_DpT100GeV.addSystematic(err_pT100GeV)
wzSample_Np4_DpT100GeV.addSystematic(err_pT100GeV)
wzSample_Np5_DpT100GeV.addSystematic(err_pT100GeV)

err_pT150GeV = Systematic("err_pT150GeV", configMgr.weights,1.083 ,0.917, "user","userOverallSys")
wzSample_Np0_DpT150GeV.addSystematic(err_pT150GeV)
wzSample_Np1_DpT150GeV.addSystematic(err_pT150GeV)
wzSample_Np2_DpT150GeV.addSystematic(err_pT150GeV)
wzSample_Np3_DpT150GeV.addSystematic(err_pT150GeV)
wzSample_Np4_DpT150GeV.addSystematic(err_pT150GeV)
wzSample_Np5_DpT150GeV.addSystematic(err_pT150GeV)

err_pT200GeV = Systematic("err_pT200GeV", configMgr.weights,1.102,0.898, "user","userOverallSys")
wzSample_Np0_DpT200GeV.addSystematic(err_pT200GeV)
wzSample_Np1_DpT200GeV.addSystematic(err_pT200GeV)
wzSample_Np2_DpT200GeV.addSystematic(err_pT200GeV)
wzSample_Np3_DpT200GeV.addSystematic(err_pT200GeV)
wzSample_Np4_DpT200GeV.addSystematic(err_pT200GeV)
wzSample_Np5_DpT200GeV.addSystematic(err_pT200GeV)

wzSample_Np0_DpT250GeV.addSystematic(err_pT200GeV)
wzSample_Np1_DpT250GeV.addSystematic(err_pT200GeV)
wzSample_Np2_DpT250GeV.addSystematic(err_pT200GeV)
wzSample_Np3_DpT250GeV.addSystematic(err_pT200GeV)
wzSample_Np4_DpT250GeV.addSystematic(err_pT200GeV)
wzSample_Np5_DpT250GeV.addSystematic(err_pT200GeV)



# TOP

topSample_Np0 = Sample("Top_Np0",100)
topSample_Np0.setNormFactor("mu_Top_Np0",1.,0.,5.)
topSample_Np0.setStatConfig(useStat)

topSample_Np1 = Sample("Top_Np1",97)
topSample_Np1.setNormFactor("mu_Top_Np1",1.,0.,5.)
topSample_Np1.setStatConfig(useStat)

topSample_Np2 = Sample("Top_Np2",94)
topSample_Np2.setNormFactor("mu_Top_Np2",1.,0.,5.)
topSample_Np2.setStatConfig(useStat)

topSample_Np3 = Sample("Top_Np3",91)
topSample_Np3.setNormFactor("mu_Top_Np3",1.,0.,5.)
topSample_Np3.setStatConfig(useStat)

topSample_Np4 = Sample("Top_Np4",91)
topSample_Np4.setNormFactor("mu_Top_Np3",1.,0.,5.)
topSample_Np4.setStatConfig(useStat)

topSample_Np5 = Sample("Top_Np5",91)
topSample_Np5.setNormFactor("mu_Top_Np3",1.,0.,5.)
topSample_Np5.setStatConfig(useStat) 


# DATA, QCD and BG

bgSample = Sample("BG",kGreen)
bgSample.setNormFactor("mu_BG",1.,0.,5.)
bgSample.setStatConfig(useStat)
qcdSample = Sample("QCD",kGray+1)
qcdSample.setQCD(True,"histoSys")
qcdSample.setStatConfig(useStat)
dataSample = Sample("Data",kBlack)
dataSample.setData()

WZList = ["WZpT0GeV_Np0","WZpT50GeV_Np0","WZpT100GeV_Np0","WZpT150GeV_Np0","WZpT200GeV_Np0","WZpT250GeV_Np0","WZpT0GeV_Np1","WZpT50GeV_Np1","WZpT100GeV_Np1","WZpT150GeV_Np1","WZpT200GeV_Np1","WZpT250GeV_Np1","WZpT0GeV_Np2","WZpT50GeV_Np2","WZpT100GeV_Np2","WZpT150GeV_Np2","WZpT200GeV_Np2","WZpT250GeV_Np2","WZpT0GeV_Np3","WZpT50GeV_Np3","WZpT100GeV_Np3","WZpT150GeV_Np3","WZpT200GeV_Np3","WZpT250GeV_Np3","WZpT0GeV_Np4","WZpT50GeV_Np4","WZpT100GeV_Np4","WZpT150GeV_Np4","WZpT200GeV_Np4","WZpT250GeV_Np4","WZpT0GeV_Np5","WZpT50GeV_Np5","WZpT100GeV_Np5","WZpT150GeV_Np5","WZpT200GeV_Np5","WZpT250GeV_Np5"]

BGList = WZList + ["Top_Np0","Top_Np1","Top_Np2","Top_Np3","Top_Np4","Top_Np5","BG"]



###### REGIONS AND BINNINGS ###########

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

srNBins = 1
srBinLow = 0.5
srBinHigh = 1.5

WpTBinN      = 14
WpTBinLow    = 0.
WpTBinHigh   = 700.

ZpTBinN      = 10
ZpTBinLow    = 0.1
ZpTBinHigh   = 500.1

               
#Create TopLevelXML objects

bkgOnly = configMgr.addTopLevelXML("bkgonly")
bkgOnly.addSamples([qcdSample,bgSample,topSample_Np0,topSample_Np1,topSample_Np2,topSample_Np3,topSample_Np4,topSample_Np5,dataSample,wzSample_Np0_DpT0GeV,wzSample_Np0_DpT50GeV,wzSample_Np0_DpT100GeV,wzSample_Np0_DpT150GeV,wzSample_Np0_DpT200GeV,wzSample_Np0_DpT250GeV,wzSample_Np1_DpT0GeV,wzSample_Np1_DpT50GeV,wzSample_Np1_DpT100GeV,wzSample_Np1_DpT150GeV,wzSample_Np1_DpT200GeV,wzSample_Np1_DpT250GeV,wzSample_Np2_DpT0GeV,wzSample_Np2_DpT50GeV,wzSample_Np2_DpT100GeV,wzSample_Np2_DpT150GeV,wzSample_Np2_DpT200GeV,wzSample_Np2_DpT250GeV,wzSample_Np3_DpT0GeV,wzSample_Np3_DpT50GeV,wzSample_Np3_DpT100GeV,wzSample_Np3_DpT150GeV,wzSample_Np3_DpT200GeV,wzSample_Np3_DpT250GeV,wzSample_Np4_DpT0GeV,wzSample_Np4_DpT50GeV,wzSample_Np4_DpT100GeV,wzSample_Np4_DpT150GeV,wzSample_Np4_DpT200GeV,wzSample_Np4_DpT250GeV,wzSample_Np5_DpT0GeV,wzSample_Np5_DpT50GeV,wzSample_Np5_DpT100GeV,wzSample_Np5_DpT150GeV,wzSample_Np5_DpT200GeV,wzSample_Np5_DpT250GeV])

if useStat:
    bkgOnly.statErrThreshold=0.05 #0.03??
else:
    bkgOnly.statErrThreshold=None


#Add Measurement
meas=bkgOnly.addMeasurement(measName,measLumi,measLumiError)
meas.addPOI("mu_SIG")

# Fix Background and low WZ parton multiplicities
meas.addParamSetting("mu_BG","const",1.0)
meas.addParamSetting("mu_WZ_Np0","const",1.0)
meas.addParamSetting("mu_WZ_Np1","const",1.0)


# Fix Normfacors on mu_WZ_TrueZPt as determined by yuichi
meas.addParamSetting("mu_WZ_pT0GeV","NOT const",1.00)
meas.addParamSetting("mu_WZ_pT50GeV","NOT const",0.893)
meas.addParamSetting("mu_WZ_pT100GeV","NOT const",0.866)
meas.addParamSetting("mu_WZ_pT150GeV","NOT const",0.737)
meas.addParamSetting("mu_WZ_pT200GeV","NOT const",0.772)


## Fix Uncertainties from the true WZ Pt fit

#meas.addParamSetting("alpha_err_pT0GeV","const",0)
#meas.addParamSetting("alpha_err_pT50GeV","const",0)
#meas.addParamSetting("alpha_err_pT100GeV","const",0)
#meas.addParamSetting("alpha_err_pT150GeV","const",0)
#meas.addParamSetting("alpha_err_pT200GeV","const",0)

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
nJetTopeeChannel.addSystematic(btagTR)
nJetTopeeChannel.addSystematic(lepTR)
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
if fullSyst:
    nJetTopmChannel.addSystematic(metcoTR)
    nJetTopmChannel.addSystematic(metpuTR)
    nJetTopmChannel.addSystematic(trigTR)
    [nJetTopmChannel.getSample(sam).addSystematic(lesTR) for sam in BGList]
    [nJetTopmChannel.getSample(sam).addSystematic(lermsTR) for sam in BGList]
    [nJetTopmChannel.getSample(sam).addSystematic(leridTR) for sam in BGList]
    

####### nJet for W #######
    
# single ele

nJetZeChannel=bkgOnly.addChannel("nJet",nJetZeRegions,nJetZeNBins,nJetZeBinLow,nJetZeBinHigh)
nJetZeChannel.hasB = False
nJetZeChannel.hasBQCD = False
nJetZeChannel.addSystematic(jesLow)
nJetZeChannel.addSystematic(jesMedium)
nJetZeChannel.addSystematic(jesHigh)
nJetZeChannel.addSystematic(btagZR)
nJetZeChannel.addSystematic(lepZR)
if fullSyst:
    nJetZeChannel.addSystematic(metcoZR)
    nJetZeChannel.addSystematic(metpuZR)
    nJetZeChannel.addSystematic(trigZR)
    [nJetZeChannel.getSample(sam).addSystematic(lesZR) for sam in BGList]
    [nJetZeChannel.getSample(sam).addSystematic(lermsZR) for sam in BGList]
    [nJetZeChannel.getSample(sam).addSystematic(leridZR) for sam in BGList]    

    
# single Mu

nJetZmChannel = bkgOnly.addChannel("nJet",["WRMu"],nJetZeNBins,nJetZeBinLow,nJetZeBinHigh)
nJetZmChannel.hasB = True
nJetZmChannel.hasBQCD = True
    
nJetZmChannel.addSystematic(btagZR)
nJetZmChannel.addSystematic(jesLow)
nJetZmChannel.addSystematic(jesMedium)
nJetZmChannel.addSystematic(jesHigh)
nJetZmChannel.addSystematic(lepZR)

if fullSyst:
    nJetZmChannel.addSystematic(metcoZR)
    nJetZmChannel.addSystematic(metpuZR)
    nJetZmChannel.addSystematic(trigZR)
    [nJetZmChannel.getSample(sam).addSystematic(lesZR)    for sam in BGList]
    [nJetZmChannel.getSample(sam).addSystematic(lermsZR)  for sam in BGList]
    [nJetZmChannel.getSample(sam).addSystematic(leridZR)  for sam in BGList]
        

####### nJet for Z  #######

## ele ele       

nJetee = bkgOnly.addChannel("nJet",["ZRee"],nJetTopemNBins,nJetTopemBinLow,nJetTopemBinHigh)

nJetee.addSystematic(jesLow)
nJetee.addSystematic(jesMedium)
nJetee.addSystematic(jesHigh)
nJetee.addSystematic(lepZR)

if fullSyst:
    nJetee.addSystematic(metcoZR)
    nJetee.addSystematic(metpuZR)
    nJetee.addSystematic(trigZR)
    [nJetee.getSample(sam).addSystematic(lesZR)    for sam in BGList]
    [nJetee.getSample(sam).addSystematic(lermsZR)  for sam in BGList]
    [nJetee.getSample(sam).addSystematic(leridZR)  for sam in BGList]

  

## mu mu      

nJetmm = bkgOnly.addChannel("nJet",["ZRmm"],nJetTopemNBins,nJetTopemBinLow,nJetTopemBinHigh)

nJetmm.addSystematic(jesLow)
nJetmm.addSystematic(jesMedium)
nJetmm.addSystematic(jesHigh)
nJetmm.addSystematic(lepZR)

if fullSyst:
    nJetmm.addSystematic(metcoZR)
    nJetmm.addSystematic(metpuZR)
    nJetmm.addSystematic(trigZR)
    [nJetmm.getSample(sam).addSystematic(lesZR)    for sam in BGList]
    [nJetmm.getSample(sam).addSystematic(lermsZR)  for sam in BGList]
    [nJetmm.getSample(sam).addSystematic(leridZR)  for sam in BGList]
    
bkgOnly.setBkgConstrainChannels([nJetTopeeChannel,nJetTopeChannel,nJetZeChannel,nJetTopemChannel,nJetTopmmChannel,nJetTopmChannel,nJetZmChannel,nJetee,nJetmm])


########## VALIDATION REGIONS #####################

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

        

#    metTR_El=bkgOnly.addChannel("met",["TRElVR2"],metNBinsTR,metBinLowTR,metBinHighTR)
#    metTR_El.hasB = True
#    metTR_El.hasBQCD = True
#    metTR_El.useOverflowBin = True
#    metTR_El.addSystematic(jesLow)
#    metTR_El.addSystematic(jesMedium)
#    metTR_El.addSystematic(jesHigh)
#    metTR_El.addSystematic(lepTR)
#    metTR_El.addSystematic(btagTR)
#    if fullSyst:
#        metTR_El.addSystematic(metcoTR)
#        metTR_El.addSystematic(metpuTR)
#        metTR_El.addSystematic(trigTR)
#        metTR_El.addSystematic(lesTR)
#        metTR_El.addSystematic(lermsTR)
#        metTR_El.addSystematic(leridTR)


#    metTR_Mu=bkgOnly.addChannel("met",["TRMuVR2"],metNBinsTR,metBinLowTR,metBinHighTR)
#    metTR_Mu.hasB = True
#    metTR_Mu.hasBQCD = True
#    metTR_Mu.useOverflowBin = True
#    metTR_Mu.addSystematic(jesLow)
#    metTR_Mu.addSystematic(jesMedium)
#    metTR_Mu.addSystematic(jesHigh)
#    metTR_Mu.addSystematic(lepTR)
#    metTR_Mu.addSystematic(btagTR)
#    if fullSyst:
#        metTR_Mu.addSystematic(metcoTR)
#        metTR_Mu.addSystematic(metpuTR)
#        metTR_Mu.addSystematic(trigTR)
#        metTR_Mu.addSystematic(lesTR)
#        metTR_Mu.addSystematic(lermsTR)
#        metTR_Mu.addSystematic(leridTR)


 #   pt1TR_El=bkgOnly.addChannel("jet1Pt",["TRElVR"],pt1NBinsTR,pt1BinLowTR,pt1BinHighTR)
 #   pt1TR_El.hasB = True
 #   pt1TR_El.hasBQCD = True
 #   pt1TR_El.useOverflowBin = True
 #   pt1TR_El.addSystematic(jesLow)
 #   pt1TR_El.addSystematic(jesMedium)
 #   pt1TR_El.addSystematic(jesHigh)
 #   pt1TR_El.addSystematic(lepTR)
 #   pt1TR_El.addSystematic(btagTR)
 #   if fullSyst:
 #       pt1TR_El.addSystematic(metcoTR)
 #       pt1TR_El.addSystematic(metpuTR)
 #       pt1TR_El.addSystematic(trigTR)
 #       pt1TR_El.addSystematic(lesTR)
 #       pt1TR_El.addSystematic(lermsTR)
 #       pt1TR_El.addSystematic(leridTR)


 #   pt1TR_Mu=bkgOnly.addChannel("jet1Pt",["TRMuVR"],pt1NBinsTR,pt1BinLowTR,pt1BinHighTR)
 #   pt1TR_Mu.hasB = True
 #   pt1TR_Mu.hasBQCD = True
 #   pt1TR_Mu.useOverflowBin = True
 #   pt1TR_Mu.addSystematic(jesLow)
 #   pt1TR_Mu.addSystematic(jesMedium)
 #   pt1TR_Mu.addSystematic(jesHigh)
 #   pt1TR_Mu.addSystematic(lepTR)
 #   pt1TR_Mu.addSystematic(btagTR)
 #   if fullSyst:
 #       pt1TR_Mu.addSystematic(metcoTR)
 #       pt1TR_Mu.addSystematic(metpuTR)
 #       pt1TR_Mu.addSystematic(trigTR)
 #       pt1TR_Mu.addSystematic(lesTR)
 #       pt1TR_Mu.addSystematic(lermsTR)
 #       pt1TR_Mu.addSystematic(leridTR)

        
        
 #   pt2TR_El=bkgOnly.addChannel("jet2Pt",["TRElVR"],pt2NBinsTR,pt2BinLowTR,pt2BinHighTR)
 #   pt2TR_El.hasB = True
 #   pt2TR_El.hasBQCD = True
 #   pt2TR_El.useOverflowBin = True
 #   pt2TR_El.addSystematic(jesLow)
 #   pt2TR_El.addSystematic(jesMedium)
 #   pt2TR_El.addSystematic(jesHigh)
 #   pt2TR_El.addSystematic(lepTR)
 #   pt2TR_El.addSystematic(btagTR)
 #   if fullSyst:
 #       pt2TR_El.addSystematic(metcoTR)
 #       pt2TR_El.addSystematic(metpuTR)
 #       pt2TR_El.addSystematic(trigTR)
 #       pt2TR_El.addSystematic(lesTR)
 #       pt2TR_El.addSystematic(lermsTR)
 #       pt2TR_El.addSystematic(leridTR)


 #   pt2TR_Mu=bkgOnly.addChannel("jet2Pt",["TRMuVR"],pt2NBinsTR,pt2BinLowTR,pt2BinHighTR)
 #   pt2TR_Mu.hasB = True
 #   pt2TR_Mu.hasBQCD = True
 #   pt2TR_Mu.useOverflowBin = True
 #   pt2TR_Mu.addSystematic(jesLow)
 #   pt2TR_Mu.addSystematic(jesMedium)
 #   pt2TR_Mu.addSystematic(jesHigh)
 #   pt2TR_Mu.addSystematic(lepTR)
 #   pt2TR_Mu.addSystematic(btagTR)
 #   if fullSyst:
 #       pt2TR_Mu.addSystematic(metcoTR)
 #       pt2TR_Mu.addSystematic(metpuTR)
 #       pt2TR_Mu.addSystematic(trigTR)
 #       pt2TR_Mu.addSystematic(lesTR)
 #       pt2TR_Mu.addSystematic(lermsTR)
 #       pt2TR_Mu.addSystematic(leridTR)


    metWR_El=bkgOnly.addChannel("met",["WRElVR"],metNBinsTR,metBinLowTR,metBinHighTR)
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


    wptWR_El=bkgOnly.addChannel("Wpt",["WRElVR"],metNBinsTR,metBinLowTR,metBinHighTR)
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


 #   lep1ptWR_El=bkgOnly.addChannel("lep1Pt",["WRElVR"],metNBinsTR,metBinLowTR,metBinHighTR)
 #   lep1ptWR_El.useOverflowBin = True
 #   lep1ptWR_El.addSystematic(jesLow)
 #   lep1ptWR_El.addSystematic(jesMedium)
 #   lep1ptWR_El.addSystematic(jesHigh)
 #   lep1ptWR_El.addSystematic(lepTR)
 #   lep1ptWR_El.addSystematic(btagTR)
 #   if fullSyst:
 #       lep1ptWR_El.addSystematic(metcoTR)
 #       lep1ptWR_El.addSystematic(metpuTR)
 #       lep1ptWR_El.addSystematic(trigTR)
 #       lep1ptWR_El.addSystematic(lesTR)
 #       lep1ptWR_El.addSystematic(lermsTR)
 #       lep1ptWR_El.addSystematic(leridTR)


 #   lep1ptWR_Mu=bkgOnly.addChannel("lep1Pt",["WRMuVR"],metNBinsTR,metBinLowTR,metBinHighTR)
 #   lep1ptWR_Mu.useOverflowBin = True
 #   lep1ptWR_Mu.addSystematic(jesLow)
 #   lep1ptWR_Mu.addSystematic(jesMedium)
 #   lep1ptWR_Mu.addSystematic(jesHigh)
 #   lep1ptWR_Mu.addSystematic(lepTR)
 #   lep1ptWR_Mu.addSystematic(btagTR)
 #   if fullSyst:
 #       lep1ptWR_Mu.addSystematic(metcoTR)
 #       lep1ptWR_Mu.addSystematic(metpuTR)
 #       lep1ptWR_Mu.addSystematic(trigTR)
 #       lep1ptWR_Mu.addSystematic(lesTR)
 #       lep1ptWR_Mu.addSystematic(lermsTR)
 #       lep1ptWR_Mu.addSystematic(leridTR)                    


 #   metWR2_El=bkgOnly.addChannel("met",["WRElVR2"],metNBinsTR,metBinLowTR,metBinHighTR)
 #   metWR2_El.useOverflowBin = True
 #   metWR2_El.addSystematic(jesLow)
 #   metWR2_El.addSystematic(jesMedium)
 #   metWR2_El.addSystematic(jesHigh)
 #   metWR2_El.addSystematic(lepTR)
 #   metWR2_El.addSystematic(btagTR)
 #   if fullSyst:
 #       metWR2_El.addSystematic(metcoTR)
 #       metWR2_El.addSystematic(metpuTR)
 #       metWR2_El.addSystematic(trigTR)
 #       metWR2_El.addSystematic(lesTR)
 #       metWR2_El.addSystematic(lermsTR)
 #       metWR2_El.addSystematic(leridTR)


 #   metWR2_Mu=bkgOnly.addChannel("met",["WRMuVR2"],metNBinsTR,metBinLowTR,metBinHighTR)
 #   metWR2_Mu.useOverflowBin = True
  #  metWR2_Mu.addSystematic(jesLow)
 #   metWR2_Mu.addSystematic(jesMedium)
 #   metWR2_Mu.addSystematic(jesHigh)
 #   metWR2_Mu.addSystematic(lepTR)
 #   metWR2_Mu.addSystematic(btagTR)
 #   if fullSyst:
 #       metWR2_Mu.addSystematic(metcoTR)
 #       metWR2_Mu.addSystematic(metpuTR)
 #       metWR2_Mu.addSystematic(trigTR)
 #       metWR2_Mu.addSystematic(lesTR)
 #       metWR2_Mu.addSystematic(lermsTR)
 #       metWR2_Mu.addSystematic(leridTR)       


 #   wptWR2_El=bkgOnly.addChannel("Wpt",["WRElVR2"],metNBinsTR,metBinLowTR,metBinHighTR)
 #   wptWR2_El.useOverflowBin = True
 #   wptWR2_El.addSystematic(jesLow)
 #   wptWR2_El.addSystematic(jesMedium)
 #   wptWR2_El.addSystematic(jesHigh)
 #   wptWR2_El.addSystematic(lepTR)
 #   wptWR2_El.addSystematic(btagTR)
 #   if fullSyst:
 #       wptWR2_El.addSystematic(metcoTR)
 #       wptWR2_El.addSystematic(metpuTR)
 #       wptWR2_El.addSystematic(trigTR)
 #       wptWR2_El.addSystematic(lesTR)
 #       wptWR2_El.addSystematic(lermsTR)
 #       wptWR2_El.addSystematic(leridTR)


#    wptWR2_Mu=bkgOnly.addChannel("Wpt",["WRMuVR2"],metNBinsTR,metBinLowTR,metBinHighTR)
#    wptWR2_Mu.useOverflowBin = True
#    wptWR2_Mu.addSystematic(jesLow)
#    wptWR2_Mu.addSystematic(jesMedium)
#    wptWR2_Mu.addSystematic(jesHigh)
#    wptWR2_Mu.addSystematic(lepTR)
#    wptWR2_Mu.addSystematic(btagTR)
#    if fullSyst:
#        wptWR2_Mu.addSystematic(metcoTR)
#        wptWR2_Mu.addSystematic(metpuTR)
#        wptWR2_Mu.addSystematic(trigTR)
 #       wptWR2_Mu.addSystematic(lesTR)
 #       wptWR2_Mu.addSystematic(lermsTR)
#        wptWR2_Mu.addSystematic(leridTR)


 #   lep1ptWR2_El=bkgOnly.addChannel("lep1Pt",["WRElVR2"],metNBinsTR,metBinLowTR,metBinHighTR)
 #   lep1ptWR2_El.useOverflowBin = True
 #   lep1ptWR2_El.addSystematic(jesLow)
 #   lep1ptWR2_El.addSystematic(jesMedium)
 #   lep1ptWR2_El.addSystematic(jesHigh)
 #   lep1ptWR2_El.addSystematic(lepTR)
 #   lep1ptWR2_El.addSystematic(btagTR)
  #  if fullSyst:
  #      lep1ptWR2_El.addSystematic(metcoTR)
 #       lep1ptWR2_El.addSystematic(metpuTR)
 #       lep1ptWR2_El.addSystematic(trigTR)
 #       lep1ptWR2_El.addSystematic(lesTR)
 #       lep1ptWR2_El.addSystematic(lermsTR)
 #       lep1ptWR2_El.addSystematic(leridTR)


  #  lep1ptWR2_Mu=bkgOnly.addChannel("lep1Pt",["WRMuVR2"],metNBinsTR,metBinLowTR,metBinHighTR)
  #  lep1ptWR2_Mu.useOverflowBin = True
  #  lep1ptWR2_Mu.addSystematic(jesLow)
  #  lep1ptWR2_Mu.addSystematic(jesMedium)
  #  lep1ptWR2_Mu.addSystematic(jesHigh)
  #  lep1ptWR2_Mu.addSystematic(lepTR)
  #  lep1ptWR2_Mu.addSystematic(btagTR)
  #  if fullSyst:
  #      lep1ptWR2_Mu.addSystematic(metcoTR)
  #      lep1ptWR2_Mu.addSystematic(metpuTR)
  #      lep1ptWR2_Mu.addSystematic(trigTR)
  #      lep1ptWR2_Mu.addSystematic(lesTR)
  #      lep1ptWR2_Mu.addSystematic(lermsTR)
  #      lep1ptWR2_Mu.addSystematic(leridTR)


  #  njetWR2_Mu=bkgOnly.addChannel("nJet",["WRMu2"],nJetZmNBins,nJetZmBinLow,nJetZmBinHigh)
  #  njetWR2_Mu.useOverflowBin = True
  #  njetWR2_Mu.addSystematic(jesLow)
  #  njetWR2_Mu.addSystematic(jesMedium)
  #  njetWR2_Mu.addSystematic(jesHigh)
  #  njetWR2_Mu.addSystematic(lepTR)
  #  njetWR2_Mu.addSystematic(btagTR)
  #  if fullSyst:
  #      njetWR2_Mu.addSystematic(metcoTR)
  #      njetWR2_Mu.addSystematic(metpuTR)
  #      njetWR2_Mu.addSystematic(trigTR)
  #      njetWR2_Mu.addSystematic(lesTR)
  #      njetWR2_Mu.addSystematic(lermsTR)
  #      njetWR2_Mu.addSystematic(leridTR)       


  #  wptWR2_El=bkgOnly.addChannel("Wpt",["WREl2"],WpTBinN,WpTBinLow,WpTBinHigh)
  #  wptWR2_El.useOverflowBin = True
  #  wptWR2_El.addSystematic(jesLow)
  #  wptWR2_El.addSystematic(jesMedium)
  #  wptWR2_El.addSystematic(jesHigh)
  #  wptWR2_El.addSystematic(lepTR)
  #  wptWR2_El.addSystematic(btagTR)
  #  if fullSyst:
  #      wptWR2_El.addSystematic(metcoTR)
  #      wptWR2_El.addSystematic(metpuTR)
  #      wptWR2_El.addSystematic(trigTR)
  #      wptWR2_El.addSystematic(lesTR)
  #      wptWR2_El.addSystematic(lermsTR)
  #      wptWR2_El.addSystematic(leridTR)  


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



if doValidationSR:   

    # S2 using meff
    meff2ee = bkgOnly.addChannel("meffInc",["S2ee"],meffNBins,meffBinLow,meffBinHigh)
    meff2ee.useOverflowBin=True
    meff2ee.addSystematic(jesLow)
    meff2ee.addSystematic(jesMedium)
    meff2ee.addSystematic(jesHigh)     
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
            
        
if doValidationSR and not doValidationSlope:
    bkgOnly.setValidationChannels([meff2ee,meff4ee,meff2em,meff4em,meff2mm,meff4mm,meffS3_El,meffS3_Mu,meffS4_El,meffS4_Mu,meffS3T_El,meffS3T_Mu,meffS4T_El,meffS4T_Mu])

if doValidationSlope and not doValidationSR:
    bkgOnly.setValidationChannels([meffTR_El,meffTR_Mu,metWR_El,metWR_Mu,wptWR_El,wptWR_Mu])    

if doValidationSlope and doValidationSR:
    bkgOnly.setValidationChannels([meffTR_El,meffTR_Mu,metTR_El,metTR_Mu,pt1TR_El,pt1TR_Mu,pt2TR_El,pt2TR_Mu,metWR_El,metWR_Mu,wptWR_El,wptWR_Mu,lep1ptWR_El,lep1ptWR_Mu,metWR2_El,metWR2_Mu,wptWR2_El,wptWR2_Mu,lep1ptWR2_El,lep1ptWR2_Mu,njetWR2_Mu,wptWR2_El,meff2ee,meff4ee,meff2em,meff4em,meff2mm,meff4mm,meffS3_El,meffS3_Mu,meffS4_El,meffS4_Mu,meffS3T_El,meffS3T_Mu,meffS4T_El,meffS4T_Mu])    



