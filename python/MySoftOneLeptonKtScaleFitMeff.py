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

#gROOT.ProcessLine("gErrorIgnoreLevel=10001;")
#gROOT.SetBatch(False)
#configMgr.plotHistos = True

rel17=True

useStat=True

# First define HistFactory attributes
configMgr.analysisName = "MySoftOneLeptonKtScaleFitMeff"

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
        configMgr.inputFileNames.append("samples/SusyFitterTree_OneEle_Rel17_BG_Syst.root")
        configMgr.inputFileNames.append("samples/SusyFitterTree_OneMu_Rel17_BG_Syst.root")
        configMgr.inputFileNames.append("samples/SusyFitterTree_OneSoftEle_Rel17_BG_CrossCheck.root")
        configMgr.inputFileNames.append("samples/SusyFitterTree_OneSoftMuo_Rel17_BG_CrossCheck.root")
        #configMgr.inputFileNames.append("samples/SusyFitterTree_OneSoftEle_Rel17_mSUGRA_CrossCheck.root")
        #configMgr.inputFileNames.append("samples/SusyFitterTree_OneSoftMuo_Rel17_mSUGRA_CrossCheck.root")
        #configMgr.inputFileNames.append("samples/SusyFitterTree_OneSoftEle_Rel17_simplifiedModel_CrossCheck.root")
        #configMgr.inputFileNames.append("samples/SusyFitterTree_OneSoftMuo_Rel17_simplifiedModel_CrossCheck.root")        
        #configMgr.inputFileNames.append("samples/SusyFitterTree_OneEle_Rel17_mSUGRA.root")
        #configMgr.inputFileNames.append("samples/SusyFitterTree_OneEle_Rel17_mSUGRA.root")
        configMgr.inputFileNames.append("samples/SusyFitterTree_p832_GG-One-Step_soft_v0.root")
        
    else:
        configMgr.inputFileNames = [] #["samples/SusyFitterTree_OneEle.root","samples/SusyFitterTree_OneMu.root"]
else:
    configMgr.inputFileNames = ["data/"+configMgr.analysisName+".root"]

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



#configMgr.cutsDict["VR"] = "lep2Pt<10 && met>120 && met<250 && mt>80 && jet1Pt>80 && jet3Pt>25 && meffInc>400"
#configMgr.cutsDict["VR2"] = "lep2Pt<10 && met<250 && mt>80 && jet1Pt>80 && jet3Pt>25 && meffInc>400"
#configMgr.cutsDict["S3"] = "lep2Pt<10 && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25 && jet4Pt<80"
#configMgr.cutsDict["S3"] = "lep2Pt<10 && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25"# && jet4Pt<80"
#configMgr.cutsDict["S4"] = "lep2Pt<10 && met>250 && mt>100 && met/meff4Jet>0.2 && jet4Pt>80"
#configMgr.cutsDict["SS"] = "lep2Pt<10 && met>250 && mt>100 && jet1Pt>120 && jet2Pt>25"

d=configMgr.cutsDict
configMgr.cutsDict["SRs1lsj"] = d["SS"]+"&& met/meff2Jet>0.3"

# Dictionnary of cuts for Tree->hist in MeV

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
cutsDictMeV["SS"] = "(lep1Pt < 20000 && lep2Pt<10000 && met>250000 && mt>100000 && jet1Pt>130000 && jet2Pt>25000 && AnalysisType==7) || (lep1Pt < 25000 && lep2Pt<10000 && met>250000 && mt>100000 && jet1Pt>130000 && jet2Pt>25000 && AnalysisType==6)"

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

ptMinTopHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ptmin20WeightTop","bTagWeight2Jet")
ptMinTopLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ptmin20WeightTop","bTagWeight2Jet")

ptMinWZHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ptmin20WeightW","bTagWeight2Jet")
ptMinWZLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ptmin20WeightW","bTagWeight2Jet")

bTagHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight2JetHigh")
bTagLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight2JetLow")

# QCD weights without and with b-jet selection
configMgr.weightsQCD = "qcdWeight"
configMgr.weightsQCDWithB = "qcdBWeight"

# List of systematics
topKtScale = Systematic("KtScaleTop",configMgr.weights,ktScaleTopHighWeights,ktScaleTopLowWeights,"weight","histoSys")
wzKtScale = Systematic("KtScaleWZ",configMgr.weights,ktScaleWHighWeights,ktScaleWLowWeights,"weight","histoSys")

topPtMin = Systematic("PtMinTop",configMgr.weights,ptMinTopHighWeights,ptMinTopLowWeights,"weight","histoSys")
wzPtMin = Systematic("PtMinWZ",configMgr.weights,ptMinWZHighWeights,ptMinWZLowWeights,"weight","histoSys")

xsecSig = Systematic("XSS",configMgr.weights,xsecSigHighWeights,xsecSigLowWeights,"weight","overallSys")

jesSLWR = Systematic("JSLWR","_NoSys","_JESup","_JESdown","tree","histoSys")
jesSLTR = Systematic("JSLTR","_NoSys","_JESup","_JESdown","tree","histoSys")
jesSLSR = Systematic("JSLSR","_NoSys","_JESup","_JESdown","tree","histoSys")

jesTop = Systematic("JT","_NoSys","_JESup","_JESdown","tree","histoSys")
jesWZ = Systematic("JW","_NoSys","_JESup","_JESdown","tree","histoSys")
jesSig = Systematic("JS","_NoSys","_JESup","_JESdown","tree","histoSys")
jesBG = Systematic("JB","_NoSys","_JESup","_JESdown","tree","histoSys")

jes = Systematic("JES","_NoSys","_JESup","_JESdown","tree","histoSys")

configMgr.nomName = "_NoSys"

# List of samples and their plotting colours
topSample = Sample("Top",kGreen-9)
topSample.setNormFactor("mu_Top",1.,0.,5.)
topSample.setStatConfig(useStat)
topSample.addSystematic(jesTop)
wzSample = Sample("WZ",kAzure+1)
wzSample.setNormFactor("mu_WZ",1.,0.,5.)
wzSample.setStatConfig(useStat)
wzSample.addSystematic(jesWZ)
bgSample = Sample("BG",kYellow-3)
bgSample.setNormFactor("mu_BG",1.,0.,5.)
bgSample.setStatConfig(useStat)
bgSample.addSystematic(jesBG)
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

#------------
#Bkg only fit
#------------

bkt = configMgr.addTopLevelXML("BkgOnlyKt")
if useStat:
    bkt.statErrThreshold=0.03
else:
    bkt.statErrThreshold=None
bkt.addSamples([bgSample,topSample,wzSample,qcdSample,dataSample])
bkt.getSample("Top").addSystematic(topKtScale)
bkt.getSample("WZ").addSystematic(wzKtScale)
#bkt.getSample("Top").addSystematic(topPtMin)
#bkt.getSample("WZ").addSystematic(wzPtMin)

meas=bkt.addMeasurement(name="NormalMeasurement",lumi=1.0,lumiErr=0.039)
meas.addPOI("mu_SIG")
meas.addParamSetting("mu_BG",True,1)
#meas.addConstraintTerm("alpha_XSS","Gamma",0.3)

#CRs
nJetSLW = bkt.addChannel("nJet",["SLWR"],nJetBinHighWR-nJetBinLow,nJetBinLow,nJetBinHighWR)
nJetSLW.hasB = True
#nJetW.addSystematic(jesWR)
nJetSLT = bkt.addChannel("nJet",["SLTR"],nJetBinHighTR-nJetBinLow,nJetBinLow,nJetBinHighTR)
nJetSLT.hasB = True
#nJetT.addSystematic(jesTR)
#bkt.addSystematic(jes)
bkt.setBkgConstrainChannels([nJetSLW,nJetSLT])

## #SLVR1s
## nJetSLVR1 = bkt.addChannel("nJet",["SLVR1"],nJetBinHighTR-nJetBinLow,nJetBinLow,nJetBinHighTR)
## nBJetSLVR1 = bkt.addChannel("nBJet",["SLVR1"],nBJetBinHigh-nBJetBinLow,nBJetBinLow,nBJetBinHigh)
## meffSLVR1 = bkt.addChannel("meff2Jet",["SLVR1"],meffNBins,meffBinLow,meffBinHigh) 
## metSLVR1 = bkt.addChannel("met",["SLVR1"],6,30,250)
## #metMeffSLVR1 = bkt.addChannel("met/meff2Jet",["SLVR1"],10,0.0,1.0)
## bkt.setValidationChannels([nJetSLVR1,nBJetSLVR1,meffSLVR1,metSLVR1]) #These are not necessarily statistically independent

## #SLVR2s
## nJetSLVR2 = bkt.addChannel("nJet",["SLVR2"],nJetBinHighTR-nJetBinLow,nJetBinLow,nJetBinHighTR)
## nBJetSLVR2 = bkt.addChannel("nBJet",["SLVR2"],nBJetBinHigh-nBJetBinLow,nBJetBinLow,nBJetBinHigh)
## meffSLVR2 = bkt.addChannel("meff2Jet",["SLVR2"],meffNBins,meffBinLow,meffBinHigh) 
## metSLVR2 = bkt.addChannel("met",["SLVR2"],6,200,250)
## #metMeffSLVR2 = bkt.addChannel("met/meff2Jet",["SLVR2"],10,0.0,1.0)
## bkt.setValidationChannels([nJetSLVR2,nBJetSLVR2,meffSLVR2,metSLVR2]) #These are not necessarily statistically independent

"""
#SRs
metSLSR = bkt.addChannel("met",["SLSR"],metNBins,metBinLow,metBinHigh)
metSLSR.addSystematic(jesSLSR)
metSLSR.useOverflowBin=True
bkt.setBkgConstrainChannels([nJetSLW,nJetSLT,metSLSR])


#--------------
# Discovery fit
#--------------
discovery = configMgr.addTopLevelXMLClone(bkt,"Discovery")
SLSRChannel = discovery.addChannel("cuts",["SLSR"],srNBins,srBinLow,srBinHigh)
##sr3jTChannel.addSystematic(jesSLSR)
## sr4jTChannel.addSystematic(jesSR)
## s3Channel.addSystematic(jesSR)
## s4Channel.addSystematic(jesSR)
SLSRChannel.addDiscoverySamples(["SLSR"],[1.],[-10.],[10.],[kMagenta])
discovery.setSignalChannels( [SLSRChannel])
#srChannel.addDiscoverySamples(["S3","S4"],[1.,1.],[-10.,-10.],[10.,10.],[kBlue,kBlue])
#srChannel = discovery.addChannel("cuts",["S3","S4"],srNBins,srBinLow,srBinHigh)
#srChannel.addSystematic(jesSR)
#srChannel.addDiscoverySamples(["S3","S4"],[1.,1.],[-20.,-20.],[20.,20.],[kBlue,kBlue])
#discovery.setSignalChannels(srChannel)




#discovery = configMgr.addTopLevelXMLClone(bkt,"Discovery")
#srChannel = discovery.addChannel("cuts",["SLSR"],srNBins,srBinLow,srBinHigh)
#srChannel.addSystematic(jesSLSR)
#srChannel.addDiscoverySamples(["SLSR"],[1.,1.],[-20.,-20.],[20.,20.],[kBlue,kBlue])
#discovery.setSignalChannels(srChannel)
"""
#-----------------------------
# Exclusion fits (MSUGRA grid)
#-----------------------------

if rel17:
    sigSamples=["SM_GG_onestepCC_425_385_345"]

    #sigSamples=['SM_GG_onestepCC_1025_545_65', 'SM_GG_onestepCC_1025_625_225', 'SM_GG_onestepCC_1025_705_385', 'SM_GG_onestepCC_1025_785_545', 'SM_GG_onestepCC_1025_865_705', 'SM_GG_onestepCC_1025_945_865', 'SM_GG_onestepCC_1037_1024_1012', 'SM_GG_onestepCC_1065_1025_985', 'SM_GG_onestepCC_1065_545_25', 'SM_GG_onestepCC_1065_625_185', 'SM_GG_onestepCC_1065_705_345', 'SM_GG_onestepCC_1065_785_505', 'SM_GG_onestepCC_1065_865_665', 'SM_GG_onestepCC_1065_945_825', 'SM_GG_onestepCC_1105_1025_945', 'SM_GG_onestepCC_1105_625_145', 'SM_GG_onestepCC_1105_705_305', 'SM_GG_onestepCC_1105_785_465', 'SM_GG_onestepCC_1105_865_625', 'SM_GG_onestepCC_1105_945_785', 'SM_GG_onestepCC_1117_1104_1092', 'SM_GG_onestepCC_1145_1025_905', 'SM_GG_onestepCC_1145_1105_1065', 'SM_GG_onestepCC_1145_625_105', 'SM_GG_onestepCC_1145_705_265', 'SM_GG_onestepCC_1145_785_425', 'SM_GG_onestepCC_1145_865_585', 'SM_GG_onestepCC_1145_945_745', 'SM_GG_onestepCC_1185_1025_865', 'SM_GG_onestepCC_1185_1105_1025', 'SM_GG_onestepCC_1185_625_65', 'SM_GG_onestepCC_1185_705_225', 'SM_GG_onestepCC_1185_785_385', 'SM_GG_onestepCC_1185_865_545', 'SM_GG_onestepCC_1185_945_705', 'SM_GG_onestepCC_205_125_45', 'SM_GG_onestepCC_225_185_145', 'SM_GG_onestepCC_227_214_202', 'SM_GG_onestepCC_235_155_75', 'SM_GG_onestepCC_245_125_5', 'SM_GG_onestepCC_255_215_175', 'SM_GG_onestepCC_257_244_232', 'SM_GG_onestepCC_265_185_105', 'SM_GG_onestepCC_275_155_35', 'SM_GG_onestepCC_285_245_205', 'SM_GG_onestepCC_287_274_262', 'SM_GG_onestepCC_295_215_135', 'SM_GG_onestepCC_305_185_65', 'SM_GG_onestepCC_315_275_235', 'SM_GG_onestepCC_317_304_292', 'SM_GG_onestepCC_325_245_165', 'SM_GG_onestepCC_335_215_95', 'SM_GG_onestepCC_345_185_25', 'SM_GG_onestepCC_345_305_265', 'SM_GG_onestepCC_355_275_195', 'SM_GG_onestepCC_365_245_125', 'SM_GG_onestepCC_375_215_55', 'SM_GG_onestepCC_385_305_225', 'SM_GG_onestepCC_395_275_155', 'SM_GG_onestepCC_397_384_372', 'SM_GG_onestepCC_405_245_85', 'SM_GG_onestepCC_415_215_15', 'SM_GG_onestepCC_425_305_185', 'SM_GG_onestepCC_425_385_345', 'SM_GG_onestepCC_435_275_115', 'SM_GG_onestepCC_445_245_45', 'SM_GG_onestepCC_465_305_145', 'SM_GG_onestepCC_465_385_305', 'SM_GG_onestepCC_475_275_75', 'SM_GG_onestepCC_477_464_452', 'SM_GG_onestepCC_485_245_5', 'SM_GG_onestepCC_505_305_105', 'SM_GG_onestepCC_505_385_265', 'SM_GG_onestepCC_505_465_425', 'SM_GG_onestepCC_515_275_35', 'SM_GG_onestepCC_545_305_65', 'SM_GG_onestepCC_545_385_225', 'SM_GG_onestepCC_545_465_385', 'SM_GG_onestepCC_557_544_532', 'SM_GG_onestepCC_585_305_25', 'SM_GG_onestepCC_585_385_185', 'SM_GG_onestepCC_585_465_345', 'SM_GG_onestepCC_585_545_505', 'SM_GG_onestepCC_625_385_145', 'SM_GG_onestepCC_625_465_305', 'SM_GG_onestepCC_625_545_465', 'SM_GG_onestepCC_637_624_612', 'SM_GG_onestepCC_665_385_105', 'SM_GG_onestepCC_665_465_265', 'SM_GG_onestepCC_665_545_425', 'SM_GG_onestepCC_665_625_585', 'SM_GG_onestepCC_705_385_65', 'SM_GG_onestepCC_705_465_225', 'SM_GG_onestepCC_705_545_385', 'SM_GG_onestepCC_705_625_545', 'SM_GG_onestepCC_717_704_692', 'SM_GG_onestepCC_745_385_25', 'SM_GG_onestepCC_745_465_185', 'SM_GG_onestepCC_745_545_345', 'SM_GG_onestepCC_745_625_505', 'SM_GG_onestepCC_745_705_665', 'SM_GG_onestepCC_785_465_145', 'SM_GG_onestepCC_785_545_305', 'SM_GG_onestepCC_785_625_465', 'SM_GG_onestepCC_785_705_625', 'SM_GG_onestepCC_797_784_772', 'SM_GG_onestepCC_825_465_105', 'SM_GG_onestepCC_825_545_265', 'SM_GG_onestepCC_825_625_425', 'SM_GG_onestepCC_825_705_585', 'SM_GG_onestepCC_825_785_745', 'SM_GG_onestepCC_865_465_65', 'SM_GG_onestepCC_865_545_225', 'SM_GG_onestepCC_865_625_385', 'SM_GG_onestepCC_865_705_545', 'SM_GG_onestepCC_865_785_705', 'SM_GG_onestepCC_877_864_852', 'SM_GG_onestepCC_905_465_25', 'SM_GG_onestepCC_905_545_185', 'SM_GG_onestepCC_905_625_345', 'SM_GG_onestepCC_905_705_505', 'SM_GG_onestepCC_905_785_665', 'SM_GG_onestepCC_905_865_825', 'SM_GG_onestepCC_945_545_145', 'SM_GG_onestepCC_945_625_305', 'SM_GG_onestepCC_945_705_465', 'SM_GG_onestepCC_945_785_625', 'SM_GG_onestepCC_945_865_785', 'SM_GG_onestepCC_957_944_932', 'SM_GG_onestepCC_985_545_105', 'SM_GG_onestepCC_985_625_265', 'SM_GG_onestepCC_985_705_425', 'SM_GG_onestepCC_985_785_585', 'SM_GG_onestepCC_985_865_745', 'SM_GG_onestepCC_985_945_905']
    
for sig in sigSamples:
    myTopLvl = configMgr.addTopLevelXMLClone(bkt,"Sig_%s"%sig)
    measSig = myTopLvl.getMeasurement("NormalMeasurement").addConstraintTerm("XSS","Gamma",0.3)   
    sigSample = Sample(sig,kPink)
    sigSample.setNormByTheory()
    sigSample.setStatConfig(useStat)
    sigSample.setNormFactor("mu_SIG",1.,0.,5.)
    sigSample.addSystematic(jesSig)
    sigSample.addSystematic(xsecSig)
    sigSample.setCutsDict(cutsDictMeV)
    sigSample.setUnit("MeV")
    myTopLvl.addSamples(sigSample)
    myTopLvl.setSignalSample(sigSample)
    metOverMeff = myTopLvl.addChannel("meff2Jet",["SRs1lsj"],meffNBins,meffBinLow,meffBinHigh) 
    metOverMeff.useOverflowBin=True
    #me.addSystematic(jesS3)
    myTopLvl.setSignalChannels([metOverMeff])


