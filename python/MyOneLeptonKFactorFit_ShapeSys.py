################################################################
## In principle all you have to setup is defined in this file ##
################################################################

from configManager import configMgr
from ROOT import kBlack,kWhite,kGray,kRed,kPink,kMagenta,kViolet,kBlue,kAzure,kCyan,kTeal,kGreen,kSpring,kYellow,kOrange
from configWriter import TopLevelXML,Measurement,ChannelXML,Sample
from systematic import Systematic

# First define HistFactory attributes
configMgr.analysisName = "MyOneLeptonKFactorFit"
configMgr.outputFileName = "results/MyOneLeptonKFactorFit_Output.root"

# Scaling calculated by outputLumi / inputLumi
configMgr.inputLumi = 4.713  #1.917  # Luminosity of input TTree after weighting
configMgr.outputLumi = 4.713 #1.917   # Luminosity required for output histograms
configMgr.setLumiUnits("fb-1")

# setting the parameters of the hypothesis test
#configMgr.doHypoTest=False
#configMgr.nTOYs=1000
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
configMgr.cutsDict = {"WR":"lep2Pt<10 && met>30 && met<80 && mt>40 && mt<80 && nBJet==0 && jet1Pt>80 && jet3Pt>25 && meffInc>400",
                      "TR":"lep2Pt<10 && met>30 && met<80 && mt>40 && mt<80 && nBJet>0 && jet1Pt>80 && jet3Pt>25 && meffInc>400",
                      "VR":"lep2Pt<10 && met>80 && met<250 && mt>80 && jet1Pt>80 && jet3Pt>25 && meffInc>400",
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
#jes = Systematic("JES","_NoSys","_JESup","_JESdown","tree","overallHistoSys") #use this one for global parameter
#jesWR = Systematic("JW","_NoSys","_JESup","_JESdown","tree","shapeSys")
#jesTR = Systematic("JT","_NoSys","_JESup","_JESdown","tree","shapeSys")
#jesS3 = Systematic("J3","_NoSys","_JESup","_JESdown","tree","shapeSys")
#jesS4 = Systematic("J4","_NoSys","_JESup","_JESdown","tree","shapeSys")

jesWRW = Systematic("JW","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesWRT = Systematic("JW","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesWRB = Systematic("JW","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesWRS = Systematic("JW","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesTRW = Systematic("JT","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesTRT = Systematic("JT","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesTRB = Systematic("JT","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesTRS = Systematic("JT","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS3W = Systematic("J3","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS3T = Systematic("J3","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS3B = Systematic("J3","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS3S = Systematic("J3","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS4W = Systematic("J4","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS4T = Systematic("J4","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS4B = Systematic("J4","_NoSys","_JESup","_JESdown","tree","shapeSys")
jesS4S = Systematic("J4","_NoSys","_JESup","_JESdown","tree","shapeSys")

configMgr.nomName = "_NoSys"
#configMgr.systDict["JES"]=jes

# List of samples and their plotting colours
topSample = Sample("Top",kGreen-5)
topSample.setNormFactor("mu_Top",1.,0.,5.)
topSample0 = Sample("Top_Np0",kGreen-10)
topSample0.setNormFactor("mu_TopNp0",1.,0.2,3.)
topSample1 = Sample("Top_Np1",kGreen-9)
topSample1.setNormFactor("mu_TopNp1",1.,0.2,3.)
topSample2 = Sample("Top_Np2",kGreen-8)
topSample2.setNormFactor("mu_TopNp2",1.,0.2,3.)
topSample3 = Sample("Top_Np3",kGreen-7)
topSample3.setNormFactor("mu_TopNp3",1.,0.2,3.)
topSample4 = Sample("Top_Np4",kGreen-6)
topSample4.setNormFactor("mu_TopNp4",1.,0.2,3.)
topSample5 = Sample("Top_Np5",kGreen-5)
topSample5.setNormFactor("mu_TopNp5",1.,0.2,3.)
wzSample = Sample("WZ",kRed-9)
wzSample.setNormFactor("mu_WZ",1.,0.,5.)
wzSample3 = Sample("WZ_Np3",kRed-10)
wzSample3.setNormFactor("mu_WZNp3",1.,0.2,3.)
wzSample4 = Sample("WZ_Np4",kRed-9)
wzSample4.setNormFactor("mu_WZNp4",1.,0.2,3.)
wzSample5 = Sample("WZ_Np5",kRed-8)
wzSample5.setNormFactor("mu_WZNp5",1.,0.2,3.)
bgSample = Sample("BG",kYellow)
bgSample.setNormFactor("mu_BG",1.,0.,5.)
qcdSample = Sample("QCD",kCyan-2)
qcdSample.setQCD()
#qcdSample2 = Sample("QCD",kBlue)
#qcdSample2.addSystematic(Systematic("qcd",None,1.1,0.9,"user","userOverallSys"))
dataSample = Sample("Data",kBlack)
dataSample.setData()

jesWRW.mergeSamples([wzSample3.name,wzSample4.name,wzSample5.name])
jesWRT.mergeSamples([topSample0.name,topSample1.name,topSample2.name,topSample3.name,topSample4.name,topSample5.name])
jesWRB.mergeSamples([bgSample.name])
jesTRW.mergeSamples([wzSample3.name,wzSample4.name,wzSample5.name])
jesTRT.mergeSamples([topSample0.name,topSample1.name,topSample2.name,topSample3.name,topSample4.name,topSample5.name])
jesTRB.mergeSamples([bgSample.name])
jesS3W.mergeSamples([wzSample3.name,wzSample4.name,wzSample5.name])
jesS3T.mergeSamples([topSample0.name,topSample1.name,topSample2.name,topSample3.name,topSample4.name,topSample5.name])
jesS3B.mergeSamples([bgSample.name])
jesS4W.mergeSamples([wzSample3.name,wzSample4.name,wzSample5.name])
jesS4T.mergeSamples([topSample0.name,topSample1.name,topSample2.name,topSample3.name,topSample4.name,topSample5.name])
jesS4B.mergeSamples([bgSample.name])

#Binnings
nJetBinLow = 3
nJetBinHighTR = 10
nJetBinHighWR = 10

nBJetBinLow = 0
nBJetBinHigh = 4

meffNBins = 6
meffBinLow = 400.
meffBinHigh = 1600.

#Bkg only fit - NpX fit - set QCD const at C++ level
NpX = configMgr.addTopLevelXML("BkgOnlyNpX")
NpX.statErrThreshold=0.4
if rel17:
    NpX.addSamples([topSample,wzSample3,wzSample4,wzSample5,bgSample,qcdSample,dataSample])
    NpX.getSample("Top").addSystematic(topKtScale)
else:
    NpX.addSamples([topSample0,topSample1,topSample2,topSample3,topSample4,topSample5,wzSample3,wzSample4,wzSample5,bgSample,qcdSample,dataSample])
#NpX.addSystematic(jes)
meas=NpX.addMeasurement(name="NormalMeasurement",lumi=1.0,lumiErr=0.037)
meas.addPOI("mu_SIG")
#CRs
nJetW = NpX.addChannel("nJet",["WR"],nJetBinHighWR-nJetBinLow,nJetBinLow,nJetBinHighWR)
nJetW.addSystematic(jesWRW)
nJetW.addSystematic(jesWRT)
nJetW.addSystematic(jesWRB)
nJetT = NpX.addChannel("nJet",["TR"],nJetBinHighTR-nJetBinLow,nJetBinLow,nJetBinHighTR)
nJetT.addSystematic(jesTRW)
nJetT.addSystematic(jesTRT)
nJetT.addSystematic(jesTRB)
NpX.setBkgConstrainChannels([nJetW,nJetT])
#VRs
nJetVR = NpX.addChannel("nJet",["VR"],nJetBinHighTR-nJetBinLow,nJetBinLow,nJetBinHighTR)
nBJetVR = NpX.addChannel("nBJet",["VR"],nBJetBinHigh-nBJetBinLow,nBJetBinLow,nBJetBinHigh)
meffVR = NpX.addChannel("meffInc",["VR"],meffNBins,meffBinLow,meffBinHigh) 
NpX.setValidationChannels([nJetVR,nBJetVR,meffVR]) #These are not necessarily statistically independent



#Exclusion fits (MSUGRA grid)
#sigSamples=["SU_180_360","SU_580_240","SU_740_330","SU_900_420","SU_1300_210"]
sigSamples=["SU_580_240"]
if rel17:
    sigSamples=[]
for sig in sigSamples:
    myTopLvl = configMgr.addTopLevelXMLClone(NpX,"Sig_%s"%sig)
    sigSample = Sample(sig,kPink)
    sigSample.setNormByTheory()
    sigSample.setNormFactor("mu_SIG",0.,0.,5.)
    jesWRS.mergeSamples([sigSample.name])
    jesTRS.mergeSamples([sigSample.name])
    jesS3S.mergeSamples([sigSample.name])
    jesS4S.mergeSamples([sigSample.name])
    myTopLvl.addSamples(sigSample)
    myTopLvl.setSignalSample(sigSample)
    for chan in myTopLvl.channels:
        if chan.name.find("TR") > 0:
            chan.addSystematic(jesTRS)
        elif chan.name.find("WR") > 0:
            chan.addSystematic(jesWRS)
    meff3J = myTopLvl.addChannel("meffInc",["S3"],meffNBins,meffBinLow,meffBinHigh) 
    meff3J.useOverflowBin=True
    meff3J.addSystematic(jesS3W)
    meff3J.addSystematic(jesS3T)
    meff3J.addSystematic(jesS3B)
    meff3J.addSystematic(jesS3S)
    meff4J = myTopLvl.addChannel("meffInc",["S4"],meffNBins,meffBinLow,meffBinHigh)
    meff4J.addSystematic(jesS4W)
    meff4J.addSystematic(jesS4T)
    meff4J.addSystematic(jesS4B)
    meff4J.addSystematic(jesS4S)
    meff4J.useOverflowBin=True
    myTopLvl.setSignalChannels([meff3J,meff4J])
