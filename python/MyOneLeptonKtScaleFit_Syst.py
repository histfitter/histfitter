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
#gROOT.SetBatch(True)
#configMgr.plotHistos = True

rel17=True

useStat=True

# First define HistFactory attributes
configMgr.analysisName = "MyOneLeptonKtScaleFit"

# Scaling calculated by outputLumi / inputLumi
configMgr.inputLumi = 1.917  # Luminosity of input TTree after weighting
configMgr.outputLumi = 1.917   # Luminosity required for output histograms
configMgr.setLumiUnits("fb-1")

if rel17:
    configMgr.inputLumi = 0.001
    configMgr.outputLumi = 4.713 #1.917   # Luminosity required for output histograms
    configMgr.analysisName+="R17" 

configMgr.outputFileName = "results/"+configMgr.analysisName+"_Output.root"

# setting the parameters of the hypothesis test
#configMgr.doHypoTest=False
#configMgr.nTOYs=1000
#configMgr.calculatorType=0
#configMgr.testStatType=3
#configMgr.nPoints=20

# Set the files to read from
if configMgr.readFromTree:
    if rel17:
        configMgr.inputFileNames = []
        configMgr.inputFileNames.append("samples/SusyFitterTree_OneEle_Rel17_BG_Syst.root")
        configMgr.inputFileNames.append("samples/SusyFitterTree_OneMu_Rel17_BG_Syst.root")
        configMgr.inputFileNames.append("samples/SusyFitterTree_p832_mSUGRA_v3.root")
    else:
        configMgr.inputFileNames = ["samples/SusyFitterTree_OneEle.root","samples/SusyFitterTree_OneMu.root"]
else:
    configMgr.inputFileNames = ["data/"+configMgr.analysisName+".root"]

# Dictionnary of cuts for Tree->hist
configMgr.cutsDict["WR"] = "lep2Pt<10 && met>30 && met<120 && mt>40 && mt<80 && nB3Jet==0 && jet1Pt>80 && jet3Pt>25 && meffInc>400"
configMgr.cutsDict["TR"] = "lep2Pt<10 && met>30 && met<120 && mt>40 && mt<80 && nB3Jet>0 && jet1Pt>80 && jet3Pt>25 && meffInc>400"
configMgr.cutsDict["VR"] = "lep2Pt<10 && met>120 && met<250 && mt>80 && jet1Pt>80 && jet3Pt>25 && meffInc>400"
configMgr.cutsDict["VR2"] = "lep2Pt<10 && met<250 && mt>80 && jet1Pt>80 && jet3Pt>25 && meffInc>400"
configMgr.cutsDict["S3"] = "lep2Pt<10 && met>250 && mt>100 && met/meff3Jet>0.3 && jet1Pt>100 && jet3Pt>25 && jet4Pt<80"
configMgr.cutsDict["S4"] = "lep2Pt<10 && met>250 && mt>100 && met/meff4Jet>0.2 && jet4Pt>80"
configMgr.cutsDict["SS"] = "lep2Pt<10 && met>250 && mt>100 && jet1Pt>120 && jet2Pt>25"

d=configMgr.cutsDict
configMgr.cutsDict["SR3jT"] = d["S3"]+"&& meffInc>1200"
configMgr.cutsDict["SR4jT"] = d["S4"]+"&& meffInc>800"
configMgr.cutsDict["SR1s2j"] = d["SS"]+"&& met/meffInc>0.3"

# Dictionnary of cuts for Tree->hist in MeV
cutsDictMeV = {}
cutsDictMeV["WR"] = "lep2Pt<10000 && met>30000 && met<120000 && mt>40000 && mt<80000 && nB3Jet==0 && jet1Pt>80000 && jet3Pt>25000 && meffInc>400000"
cutsDictMeV["TR"] = "lep2Pt<10000 && met>30000 && met<120000 && mt>40000 && mt<80000 && nB3Jet>0 && jet1Pt>80000 && jet3Pt>25000 && meffInc>400000"
cutsDictMeV["VR"] = "lep2Pt<10000 && met>120000 && met<250000 && mt>80000 && jet1Pt>80000 && jet3Pt>25000 && meffInc>400000"
cutsDictMeV["VR2"] = "lep2Pt<10000 && met<250000 && mt>80000 && jet1Pt>80000 && jet3Pt>25000 && meffInc>400000"
cutsDictMeV["S3"] = "lep2Pt<10000 && met>250000 && mt>100000 && met/meff3Jet>0.3 && jet1Pt>100000 && jet3Pt>25000 && jet4Pt<80000"
cutsDictMeV["S4"] = "lep2Pt<10000 && met>250000 && mt>100000 && met/meff4Jet>0.2 && jet4Pt>80000"
cutsDictMeV["SS"] = "lep2Pt<10000 && met>250000 && mt>100000 && jet1Pt>120000 && jet2Pt>25000"

d=cutsDictMeV
cutsDictMeV["SR3jT"] = d["S3"]+"&& meffInc>1200000"
cutsDictMeV["SR4jT"] = d["S4"]+"&& meffInc>800000"
cutsDictMeV["SR1s2j"] = d["SS"]+"&& met/meffInc>0.3"

# Tuples of nominal weights without and with b-jet selection
configMgr.weights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight3Jet")

xsecSigHighWeights = ("genWeightUp","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight3Jet")
xsecSigLowWeights = ("genWeightDown","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight3Jet")

# For weight-based systematic
ktScaleWHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ktfacUpWeightW","bTagWeight3Jet")
ktScaleWLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ktfacDownWeightW","bTagWeight3Jet")

ktScaleTopHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ktfacUpWeightTop","bTagWeight3Jet")
ktScaleTopLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ktfacDownWeightTop","bTagWeight3Jet")

ptMinTopHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ptmin20WeightTop","bTagWeight3Jet")
ptMinTopLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ptmin20WeightTop","bTagWeight3Jet")

ptMinWZHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ptmin20WeightW","bTagWeight3Jet")
ptMinWZLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ptmin20WeightW","bTagWeight3Jet")

pileupSystWeights = ("genWeight","pileupWeightSyst","eventWeight","leptonWeight","triggerWeight","truthWptWeight","ptmin20WeightW","bTagWeight3Jet") # We don't use pileup weighting ...

truthWptSystWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","ptmin20WeightW","bTagWeight3Jet") # Probably not the best way to do this

bTagHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight3JetUp")
bTagLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight3JetDown")

lepEffHighWeights = ("genWeight","eventWeight","leptonWeightUp","triggerWeight","truthWptWeight","bTagWeight3Jet")
lepEffLowWeights = ("genWeight","eventWeight","leptonWeightDown","triggerWeight","truthWptWeight","bTagWeight3Jet")

trigEffHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeightUp","truthWptWeight","bTagWeight3Jet")
trigEffLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeightDown","truthWptWeight","bTagWeight3Jet")

# QCD weights without and with b-jet selection
configMgr.weightsQCD = "qcdWeight"
configMgr.weightsQCDWithB = "qcdBWeight"

# List of systematics
topKtScale = Systematic("KtScaleTop",configMgr.weights,ktScaleTopHighWeights,ktScaleTopLowWeights,"weight","histoSys")
wzKtScale = Systematic("KtScaleWZ",configMgr.weights,ktScaleWHighWeights,ktScaleWLowWeights,"weight","histoSys")

topPtMin = Systematic("PtMinTop",configMgr.weights,ptMinTopHighWeights,ptMinTopLowWeights,"weight","histoSys")
wzPtMin = Systematic("PtMinWZ",configMgr.weights,ptMinWZHighWeights,ptMinWZLowWeights,"weight","histoSys")

xsecSig = Systematic("XSS",configMgr.weights,xsecSigHighWeights,xsecSigLowWeights,"weight","overallSys")

jesWR = Systematic("JW","_NoSys","_JESup","_JESdown","tree","histoSys")
jesTR = Systematic("JT","_NoSys","_JESup","_JESdown","tree","histoSys")
#jesS3 = Systematic("J3","_NoSys","_JESup","_JESdown","tree","histoSys")
#jesS4 = Systematic("J4","_NoSys","_JESup","_JESdown","tree","histoSys")
jesSR = Systematic("JS","_NoSys","_JESup","_JESdown","tree","histoSys")

jesCRW = Systematic("JCW","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesCRT = Systematic("JCT","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesCRB = Systematic("JCB","_NoSys","_JESup","_JESdown","tree","shapeSys")

jesCR = Systematic("JC","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS3 = Systematic("J3","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS4 = Systematic("J4","_NoSys","_JESup","_JESdown","tree","shapeSys")

jesS3W = Systematic("J3W","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS3T = Systematic("J3T","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS3B = Systematic("J3B","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS3S = Systematic("J3S","_NoSys","_JESup","_JESdown","tree","shapeSys")

jesS4W = Systematic("J4W","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS4T = Systematic("J4T","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS4B = Systematic("J4B","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS4S = Systematic("J4S","_NoSys","_JESup","_JESdown","tree","shapeSys")

jesTop = Systematic("JT","_NoSys","_JESup","_JESdown","tree","histoSys")
jesWZ = Systematic("JW","_NoSys","_JESup","_JESdown","tree","histoSys")
jesSig = Systematic("JS","_NoSys","_JESup","_JESdown","tree","histoSys")
jesBG = Systematic("JB","_NoSys","_JESup","_JESdown","tree","histoSys")

jes = Systematic("JES","_NoSys","_JESup","_JESdown","tree","histoSys")

pileupWR = Systematic("PIL",configMgr.weights,pileupSystWeights,pileupSystWeights,"weight","histoSys")
pileupTR = Systematic("PIL",configMgr.weights,pileupSystWeights,pileupSystWeights,"weight","histoSys")
pileupS3 = Systematic("PIL",configMgr.weights,pileupSystWeights,pileupSystWeights,"weight","histoSys")
pileupS4 = Systematic("PIL",configMgr.weights,pileupSystWeights,pileupSystWeights,"weight","histoSys")

truthWpt = Systematic("TWP",configMgr.weights,truthWptSystWeights,truthWptSystWeights,"weight","histoSys")

btagW = Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","histoSys")
btagT = Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","histoSys")
btagB = Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","histoSys")

btag = Systematic("BT",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","histoSys")

lepEff = Systematic("LEF",configMgr.weights,lepEffHighWeights,lepEffLowWeights,"weight","histoSys")

#trigEff = Systematic("TEF",configMgr.weights,trigEffHighWeights,trigEffLowWeights,"weight","histoSys")

jerCRB = Systematic("JRCB","_NoSys","_JER","_JER","tree","shapeSys")
jerCRS = Systematic("JRCS","_NoSys","_JER","_JER","tree","shapeSys")
jerS3B = Systematic("JR3B","_NoSys","_JER","_JER","tree","shapeSys")
jerS3S = Systematic("JR3S","_NoSys","_JER","_JER","tree","shapeSys")
jerS4B = Systematic("JR4B","_NoSys","_JER","_JER","tree","shapeSys")
jerS4S = Systematic("JR4S","_NoSys","_JER","_JER","tree","shapeSys")

les = Systematic("LES","_NoSys","_LESup","_LESdown","tree","histoSys")

metco = Systematic("MCO","_NoSys","_METCOup","_METCOdown","tree","histoSys")

metpu = Systematic("MPU","_NoSys","_METPUup","_METPUdown","tree","histoSys")

lerms = Systematic("LMS","_NoSys","_LERMSup","_LERMSdown","tree","histoSys")

lerid = Systematic("LID","_NoSys","_LERIDup","_LERIDdown","tree","histoSys")

configMgr.nomName = "_NoSys"

# List of samples and their plotting colours
topSample = Sample("Top",kGreen-9)
topSample.setNormFactor("mu_Top",1.,0.,5.)
topSample.setStatConfig(useStat)
#topSample.addSystematic(jesTop)
wzSample = Sample("WZ",kAzure+1)
wzSample.setNormFactor("mu_WZ",1.,0.,5.)
wzSample.setStatConfig(useStat)
#wzSample.addSystematic(jesWZ)
bgSample = Sample("BG",kYellow-3)
bgSample.setNormFactor("mu_BG",1.,0.,5.)
bgSample.setStatConfig(useStat)
#bgSample.addSystematic(jesBG)
qcdSample = Sample("QCD",kGray+1)
qcdSample.setQCD(True,"histoSys") #"shapeSys")
qcdSample.setStatConfig(useStat)
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

lepPtNBins = 6
lepPtLow = 20.
lepPtHigh = 600.

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
bkt.addSamples([topSample,wzSample,qcdSample,bgSample,dataSample])
bkt.getSample("Top").addSystematic(topKtScale)
bkt.getSample("WZ").addSystematic(wzKtScale)
#bkt.getSample("Top").addSystematic(topPtMin)
#bkt.getSample("WZ").addSystematic(wzPtMin)
#bkt.addSystematic(pileup)
#bkt.addSystematic(truthWpt)
#bkt.addSystematic(lepEff)
#bkt.addSystematic(trigEff)
#bkt.addSystematic(jer)
#bkt.addSystematic(les)
#bkt.addSystematic(metco)
#bkt.addSystematic(metpu)
#bkt.addSystematic(lerms)
#bkt.addSystematic(lerid)

meas=bkt.addMeasurement(name="NormalMeasurement",lumi=1.0,lumiErr=0.039)
meas.addPOI("mu_SIG")
meas.addParamSetting("mu_BG",True,1)

#meas.addParamSetting("alpha_KtScaleTop",True,0)
#meas.addParamSetting("alpha_KtScaleWZ",True,0)

#CRs
nJetW = bkt.addChannel("nJet",["WR"],nJetBinHighWR-nJetBinLow,nJetBinLow,nJetBinHighWR)
nJetW.hasB = True
nJetW.getSample("WZ").addSystematic(btagW)
nJetW.getSample("Top").addSystematic(btagT)
nJetW.getSample("BG").addSystematic(btagB)
#nJetW.addSystematic(btag)
nJetW.addSystematic(jesCR)
nJetW.getSample("WZ").addSystematic(pileupWR)
nJetW.getSample("Top").addSystematic(pileupWR)
nJetW.getSample("BG").addSystematic(pileupWR)
#nJetW.getSample("WZ").addSystematic(jesCRW)
#nJetW.getSample("Top").addSystematic(jesCRT)
#nJetW.getSample("BG").addSystematic(jesCRB)
nJetT = bkt.addChannel("nJet",["TR"],nJetBinHighTR-nJetBinLow,nJetBinLow,nJetBinHighTR)
nJetT.hasB = True
nJetT.getSample("WZ").addSystematic(btagW)
nJetT.getSample("Top").addSystematic(btagT)
nJetT.getSample("BG").addSystematic(btagB)
#nJetT.addSystematic(btag)
nJetT.addSystematic(jesCR)
nJetT.getSample("WZ").addSystematic(pileupTR)
nJetT.getSample("Top").addSystematic(pileupTR)
nJetT.getSample("BG").addSystematic(pileupTR)
#nJetT.getSample("WZ").addSystematic(jesCRW)
#nJetT.getSample("Top").addSystematic(jesCRT)
#nJetT.getSample("BG").addSystematic(jesCRB)
#nJetT.addSystematic(jesTR)
#bkt.addSystematic(jes)
bkt.setBkgConstrainChannels([nJetW,nJetT])

##VRs
#nJetVR = bkt.addChannel("nJet",["VR"],nJetBinHighTR-nJetBinLow,nJetBinLow,nJetBinHighTR)
#nBJetVR = bkt.addChannel("nBJet",["VR"],nBJetBinHigh-nBJetBinLow,nBJetBinLow,nBJetBinHigh)
#meffVR = bkt.addChannel("meffInc",["VR"],meffNBins,meffBinLow,meffBinHigh) 
#metVR = bkt.addChannel("met",["VR2"],6,30,250)
#bkt.setValidationChannels([nJetVR,nBJetVR,meffVR,metVR]) #These are not necessarily statistically independent

#SRs
#meff3J = bkt.addChannel("meffInc",["S3"],meffNBins,meffBinLow,meffBinHigh)
#meff3J.addSystematic(jesS3)
#meff3J.useOverflowBin=True
#meff4J = bkt.addChannel("meffInc",["S4"],meffNBins,meffBinLow,meffBinHigh) 
#meff4J.addSystematic(jesS4)
#meff4J.useOverflowBin=True
#bkt.setBkgConstrainChannels([nJetW,nJetT,meff3J,meff4J])

## #--------------
## # Discovery fit
## #--------------
## discovery = configMgr.addTopLevelXMLClone(bkt,"Discovery")
## sr3jTChannel = discovery.addChannel("cuts",["SR3jT"],srNBins,srBinLow,srBinHigh)
## sr4jTChannel = discovery.addChannel("cuts",["SR4jT"],srNBins,srBinLow,srBinHigh)
## s3Channel = discovery.addChannel("cuts",["S3"],srNBins,srBinLow,srBinHigh)
## s4Channel = discovery.addChannel("cuts",["S4"],srNBins,srBinLow,srBinHigh)
## ## sr3jTChannel.addSystematic(jesSR)
## ## sr4jTChannel.addSystematic(jesSR)
## ## s3Channel.addSystematic(jesSR)
## ## s4Channel.addSystematic(jesSR)
## sr3jTChannel.addDiscoverySamples(["SR3jT"],[1.],[-10.],[10.],[kMagenta])
## sr4jTChannel.addDiscoverySamples(["SR4jT"],[1.],[-10.],[10.],[kMagenta])
## s3Channel.addDiscoverySamples(["S3"],[1.],[-100.],[100.],[kMagenta])
## s4Channel.addDiscoverySamples(["S4"],[1.],[-100.],[100.],[kMagenta])
## discovery.setSignalChannels( [sr3jTChannel,sr4jTChannel, s3Channel, s4Channel])
## #srChannel.addDiscoverySamples(["S3","S4"],[1.,1.],[-10.,-10.],[10.,10.],[kBlue,kBlue])
## #srChannel = discovery.addChannel("cuts",["S3","S4"],srNBins,srBinLow,srBinHigh)
## #srChannel.addSystematic(jesSR)
## #srChannel.addDiscoverySamples(["S3","S4"],[1.,1.],[-20.,-20.],[20.,20.],[kBlue,kBlue])
## #discovery.setSignalChannels(srChannel)

#-----------------------------
# Exclusion fits (MSUGRA grid)
#-----------------------------

sigSamples=["SU_180_360","SU_580_240","SU_740_330","SU_900_420","SU_1300_210"]
if rel17:
    sigSamples=["SU_580_240_0_10_P"]
for sig in sigSamples:
    myTopLvl = configMgr.addTopLevelXMLClone(bkt,"Sig_%s"%sig)
    #measSig = myTopLvl.getMeasurement("NormalMeasurement").addConstraintTerm("XSS","Gamma",0.3)
    sigSample = Sample(sig,kPink)
    sigSample.setNormByTheory()
    sigSample.setStatConfig(useStat)
    sigSample.setNormFactor("mu_SIG",1.,0.,5.)
    #sigSample.addSystematic(jesSig)
    sigSample.addSystematic(xsecSig)
    sigSample.setCutsDict(cutsDictMeV)
    sigSample.setUnit("MeV")
    myTopLvl.addSamples(sigSample)
    myTopLvl.setSignalSample(sigSample)
    meff3J = myTopLvl.addChannel("meffInc",["S3"],meffNBins,meffBinLow,meffBinHigh) 
    meff3J.useOverflowBin=True
    #meff3J.getSample(sig).addSystematic(jesS3S)
    #meff3J.getSample("WZ").addSystematic(jesS3W)
    #meff3J.getSample("Top").addSystematic(jesS3T)
    #meff3J.getSample("BG").addSystematic(jesS3B)
    meff3J.addSystematic(jesS3)
    meff3J.getSample("WZ").addSystematic(pileupS3)
    meff3J.getSample("Top").addSystematic(pileupS3)
    meff3J.getSample("BG").addSystematic(pileupS3)
    meff4J = myTopLvl.addChannel("meffInc",["S4"],meffNBins,meffBinLow,meffBinHigh)
    meff4J.useOverflowBin=True
    #meff4J.getSample(sig).addSystematic(jesS4S)
    #meff4J.getSample("WZ").addSystematic(jesS4W)
    #meff4J.getSample("Top").addSystematic(jesS4T)
    #meff4J.getSample("BG").addSystematic(jesS4B)
    meff4J.addSystematic(jesS4)
    meff4J.getSample("WZ").addSystematic(pileupS4)
    meff4J.getSample("Top").addSystematic(pileupS4)
    meff4J.getSample("BG").addSystematic(pileupS4)
    myTopLvl.setSignalChannels([meff3J,meff4J])
