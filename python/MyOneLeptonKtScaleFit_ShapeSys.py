################################################################
## In principle all you have to setup is defined in this file ##
################################################################

from configManager import configMgr
from ROOT import kBlack,kWhite,kGray,kRed,kPink,kMagenta,kViolet,kBlue,kAzure,kCyan,kTeal,kGreen,kSpring,kYellow,kOrange
from configWriter import TopLevelXML,Measurement,ChannelXML,Sample
from systematic import Systematic

# First define HistFactory attributes
configMgr.analysisName = "MyOneLeptonKtScaleFit"
configMgr.outputFileName = "results/"+configMgr.analysisName+"_Output.root"

# Scaling calculated by outputLumi / inputLumi
configMgr.inputLumi = 4.713  #1.917  # Luminosity of input TTree after weighting
configMgr.outputLumi = 4.713 #1.917   # Luminosity required for output histograms
configMgr.setLumiUnits("fb-1")

# setting the parameters of the hypothesis test
#configMgr.doHypoTest=False
configMgr.nTOYs=1000
configMgr.calculatorType=0
configMgr.testStatType=3
configMgr.nPoints=20

rel17=False

# Set the files to read from
if configMgr.readFromTree:
    if rel17:
        configMgr.inputFileNames = ["data/SusyFitterTree_OneEle_Rel17.root","data/SusyFitterTree_OneMu_Rel17.root"]
    else:
        configMgr.inputFileNames = ["data/SusyFitterTree_OneEle.root","data/SusyFitterTree_OneMu.root"]
else:
    configMgr.inputFileNames = ["data/"+configMgr.analysisName+".root"]

# Dictionnary of cuts for Tree->hist
configMgr.cutsDict = {"WR":"lep2Pt<10 && met>30 && met<120 && mt>40 && mt<80 && nBJet==0 && jet1Pt>80 && jet3Pt>25 && meffInc>400",
                      "TR":"lep2Pt<10 && met>30 && met<120 && mt>40 && mt<80 && nBJet>0 && jet1Pt>80 && jet3Pt>25 && meffInc>400",
                      "VR":"lep2Pt<10 && met>120 && met<250 && mt>80 && jet1Pt>80 && jet3Pt>25 && meffInc>400",
                      "S3":"lep2Pt<10 && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25 && jet4Pt<80",
                      "S4":"lep2Pt<10 && met>250 && mt>100 && met/meff4Jet>0.2 && jet4Pt>80",
                      }
d=configMgr.cutsDict
configMgr.cutsDict["SR3jT"] = d["S3"]+"&& meffInc>1200"
configMgr.cutsDict["SR4jT"] = d["S4"]+"&& meffInc>800"


# Tuples of nominal weights without and with b-jet selection
configMgr.weights = ("genWeight","bTagWeight3Jet") # last weight must be btag weight

# For weight-based systematic
ktScaleWHighWeights = ("genWeight","ktfacUpWeightW","bTagWeight3Jet") 
ktScaleWLowWeights = ("genWeight","ktfacDownWeightW","bTagWeight3Jet")
ktScaleTopHighWeights = ("genWeight","ktfacUpWeightTop","bTagWeight3Jet") 
ktScaleTopLowWeights = ("genWeight","ktfacDownWeightTop","bTagWeight3Jet") 
bTagHighWeights = ("genWeight","bTagWeight3JetHigh") 
bTagLowWeights = ("genWeight","bTagWeight3JetLow")

# QCD weights without and with b-jet selection
configMgr.weightsQCD = "qcdWeight"
configMgr.weightsQCDWithB = "qcdBWeight"

# List of systematics
topKtScale = Systematic("KtScaleTop",configMgr.weights,ktScaleTopHighWeights,ktScaleTopLowWeights,"weight","normHistoSys")
wzKtScale = Systematic("KtScaleWZ",configMgr.weights,ktScaleWHighWeights,ktScaleTopLowWeights,"weight","normHistoSys")

jesWR = Systematic("JW","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesTR = Systematic("JT","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS3 = Systematic("J3","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS4 = Systematic("J4","_NoSys","_JESup","_JESdown","tree","shapeSys")

configMgr.nomName = "_NoSys"

# List of samples and their plotting colours
topSample = Sample("Top",kGreen-5)
topSample.setNormFactor("mu_Top",1.,0.,5.)
wzSample = Sample("WZ",kRed-9)
wzSample.setNormFactor("mu_WZ",1.,0.,5.)
qcdSample = Sample("QCD",kCyan-2)
qcdSample.setQCD()
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

#Bkg only fit - KtScale fit
bkt = configMgr.addTopLevelXML("BkgOnlyKt")
bkt.statErrThreshold=0.4
bkt.addSamples([topSample,wzSample,qcdSample,dataSample])
bkt.getSample("Top").addSystematic(topKtScale)
bkt.getSample("WZ").addSystematic(wzKtScale)
meas=bkt.addMeasurement(name="NormalMeasurement",lumi=1.0,lumiErr=0.037)
meas.addPOI("mu_SIG")
#CRs
nJetW = bkt.addChannel("nJet",["WR"],nJetBinHighWR-nJetBinLow,nJetBinLow,nJetBinHighWR)
nJetW.addSystematic(jesWR)
nJetT = bkt.addChannel("nJet",["TR"],nJetBinHighTR-nJetBinLow,nJetBinLow,nJetBinHighTR)
nJetT.addSystematic(jesTR)
bkt.setBkgConstrainChannels([nJetW,nJetT])
#VRs
nJetVR = bkt.addChannel("nJet",["VR"],nJetBinHighTR-nJetBinLow,nJetBinLow,nJetBinHighTR)
nBJetVR = bkt.addChannel("nBJet",["VR"],nBJetBinHigh-nBJetBinLow,nBJetBinLow,nBJetBinHigh)
meffVR = bkt.addChannel("meffInc",["VR"],meffNBins,meffBinLow,meffBinHigh) 
bkt.setValidationChannels([nJetVR,nBJetVR,meffVR]) #These are not necessarily statistically independent

#Exclusion fits (MSUGRA grid)
sigSamples=["SU_180_360","SU_580_240","SU_740_330","SU_900_420","SU_1300_210"]
sigSamples=["SU_580_240"]
if rel17:
    sigSamples=[]
for sig in sigSamples:
    myTopLvl = configMgr.addTopLevelXMLClone(bkt,"Sig_%s"%sig)
    sigSample = Sample(sig,kPink)
    sigSample.setNormByTheory()
    sigSample.setNormFactor("mu_SIG",0.,0.,5.)
    myTopLvl.addSamples(sigSample)
    myTopLvl.setSignalSample(sigSample)
    meff3J = myTopLvl.addChannel("meffInc",["S3"],meffNBins,meffBinLow,meffBinHigh) 
    meff3J.useOverflowBin=True
    meff3J.addSystematic(jesS3)
    meff4J = myTopLvl.addChannel("meffInc",["S4"],meffNBins,meffBinLow,meffBinHigh)
    meff4J.useOverflowBin=True
    meff4J.addSystematic(jesS4)
    myTopLvl.setSignalChannels([meff3J,meff4J])
