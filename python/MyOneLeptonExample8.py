################################################################
## In principle all you have to setup is defined in this file ##
################################################################

from configManager import configMgr
from ROOT import kBlack,kRed,kBlue,kGreen,kYellow,kWhite
from configWriter import TopLevelXML,Measurement,ChannelXML,Sample
from systematic import Systematic

# First define HistFactory attributes
configMgr.analysisName = "MySusyFitterAnalysis"
configMgr.outputFileName = "results/MySusyFitterAnalysisOutput.root"

# Scaling calculated by outputLumi / inputLumi
configMgr.inputLumi = 1.234  # Luminosity of input TTree after weighting
configMgr.outputLumi = 1.234 # Luminosity required for output histograms
configMgr.setLumiUnits("pb-1")

# setting the parameters of the hypothesis test
#configMgr.doHypoTest=False
#configMgr.nTOYs=1000
configMgr.calculatorType=0
configMgr.testStatType=3

# Set the files to read from
if configMgr.readFromTree:
    configMgr.inputFileNames = ["data/susyElectronWithScale.root","data/susyMuonWithScale.root"]
else:
    configMgr.inputFileNames = ["data/"+configMgr.analysisName+".root"]

# Suffix of nominal tree
configMgr.nomName = "_NoSys"

# Tuples of nominal weights
configMgr.weights = ("genWeight","eventWeight","leptonWeight","triggerWeight","avgMuWeight","bTagWeight3Jet") # last weight must be btag weight

# Map regions to cut strings
configMgr.cutsDict = {"WR":"met > 80 && met < 130 && mt > 40 && mt < 80 && nBJet == 0 && meff3Jet > 400 && nJet >= 3 && jet1Pt > 60.",
                      "TR":"met > 80 && met < 130 && mt > 40 && mt < 80 && nBJet > 0 && meff3Jet > 400 && nJet >= 3 && jet1Pt > 60.",
                      "SR":"met > 175 && mt > 100 && meff3Jet > 400 && nJet >= 3 && jet1Pt > 60.",
                      "XRwtq":"met > 50 && met < 80 && mt > 40 && mt < 80 && meff3Jet > 400 && nJet >= 3 && jet1Pt > 60.",
                      "XRwz":"met > 50 && met < 80 && mt > 80 && mt < 120 && meff3Jet > 400 && nJet >= 3 && jet1Pt > 60.",
                      "XRtt":"met > 80 && met < 130 && mt > 80 && mt < 120 && meff3Jet > 400 && nJet >= 3 && jet1Pt > 60.",
                      "XRtll1":"met > 50 && met < 80 && mt > 120 && mt < 160 && meff3Jet > 400 && nJet >= 3 && jet1Pt > 60.",
                      "XRtll2":"met > 80 && met < 130 && mt > 120 && mt < 160 && meff3Jet > 400 && nJet >= 3 && jet1Pt > 60.",
                      "XRqcd1":"met > 90 && met < 130 && mt < 40 && meff3Jet > 400 && nJet >= 3 && jet1Pt > 60.",
                      "XRqcd2":"met > 130 && met < 200 && mt < 40 && meff3Jet > 400 && nJet >= 3 && jet1Pt > 60.",
                      "XRLshape":"met > 130 && met < 200 && mt > 40 && mt < 160 && !(met > 170 && mt > 100) && meff3Jet > 400 && nJet >= 3 && jet1Pt > 60."}

#More cuts
d=configMgr.cutsDict
configMgr.cutsDict['XRqcd1XRqcd2'] = "("+d['XRqcd1']+")||("+d['XRqcd2']+")"
configMgr.cutsDict['XRtll1XRwzXRwtq'] = "("+d['XRtll1']+")||("+d['XRwz']+")||("+d['XRwtq']+")"

# Example of Kt scale systematic
ktScaleWHighWeights = ("genWeight","ktfacUpWeightW","eventWeight","leptonWeight","triggerWeight","avgMuWeight","bTagWeight3Jet") 
ktScaleWLowWeights = ("genWeight","ktfacDownWeightW","eventWeight","leptonWeight","triggerWeight","avgMuWeight","bTagWeight3Jet")
ktScaleTopHighWeights = ("genWeight","ktfacUpWeightTop","eventWeight","leptonWeight","triggerWeight","avgMuWeight","bTagWeight3Jet") 
ktScaleTopLowWeights = ("genWeight","ktfacDownWeightTop","eventWeight","leptonWeight","triggerWeight","avgMuWeight","bTagWeight3Jet") 

# Example of btag systematic
bTagHighWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","avgMuWeight","bTagWeight3JetHigh") 
bTagLowWeights = ("genWeight","eventWeight","leptonWeight","triggerWeight","avgMuWeight","bTagWeight3JetLow")

# Systematics to be applied
#topKtScale = Systematic("KtScaleTop",configMgr.weights,ktScaleTopHighWeights,ktScaleTopLowWeights,"weight","normHistoSys")
#wzKtScale = Systematic("KtScaleWZ",configMgr.weights,ktScaleWHighWeights,ktScaleTopLowWeights,"weight","normHistoSys")
#jes = Systematic("JES","_NoSys","_JESup","_JESdown","tree","overallHistoSys")
jes = Systematic("JES","_NoSys","_JESup","_JESdown","tree","shapeSys")
btag = Systematic("BTag",configMgr.weights,bTagHighWeights,bTagLowWeights,"weight","shapeSys")

# Global systematics
configMgr.systDict["JES"] = jes

# List of samples and their plotting colours
topSample = Sample("Top")
#topSample.addSystematic(topKtScale)
topSample.setNormFactor("mu_Top",1.,0.,5.)
wzSample = Sample("WZ")
#wzSample.addSystematic(wzKtScale)
wzSample.setNormFactor("mu_WZ",1.,0.,5.)
qcdSample = Sample("QCD")
qcdSample.setQCD()
dataSample = Sample("Data")
dataSample.setData()
commonSamples = [topSample,wzSample,dataSample,qcdSample]
configMgr.plotColours = [kGreen,kRed,kYellow,kBlack,kBlue]

# QCD weights without and with b-jet selection
configMgr.weightsQCD = "qcdWeight"
configMgr.weightsQCDWithB = "qcdBWeight"

#Parameters of the Measurement
measName = "BasicMeasurement"
measLumi = 1.
measLumiError = 0.037

#Parameters of Channels
cutsRegions = ["XRtt","XRtll2"]
cutsNBins = 1
cutsBinLow = 0.5
cutsBinHigh = 1.5

cutsBRegions = ["WR","TR"]
cutsBNBins = 1
cutsBBinLow = 0.5
cutsBBinHigh = 1.5

nJetRegions = ["XRLshape"]
nJetNBins = 5
nJetBinLow = 3.
nJetBinHigh = 8.

metRegions = ["XRqcd1XRqcd2"]
metNBins = 11
metBinLow = 90.
metBinHigh = 200.

mtRegions = ["XRtll1XRwzXRwtq"]
mtNBins = 6
mtBinLow = 40.
mtBinHigh = 160.

meffRegions = ["SR"]
meffNBins = 5
meffBinLow = 400.
meffBinHigh = 1400.

#Bkg only fit
bkgOnly = configMgr.addTopLevelXML("Example8_BkgOnly")
bkgOnly.statErrThreshold=None #0.5
bkgOnly.addSamples(commonSamples)
meas = bkgOnly.addMeasurement(measName,measLumi,measLumiError)
meas.addPOI("mu_SIG")
cutsChannel = bkgOnly.addChannel("cuts",cutsRegions,cutsNBins,cutsBinLow,cutsBinHigh)
cutsBChannel = bkgOnly.addChannel("cuts",cutsBRegions,cutsBNBins,cutsBBinLow,cutsBBinHigh)
cutsBChannel.hasB=True
cutsBChannel.addSystematic(btag)
nJetChannel = bkgOnly.addChannel("nJet",nJetRegions,nJetNBins,nJetBinLow,nJetBinHigh)
metChannel  = bkgOnly.addChannel("met",metRegions,metNBins,metBinLow,metBinHigh) 
mtChannel   = bkgOnly.addChannel("mt",mtRegions,mtNBins,mtBinLow,mtBinHigh)
bkgOnly.setBkgConstrainChannels([cutsBChannel,nJetChannel,metChannel,mtChannel])
bkgOnly.setValidationChannels(cutsChannel)

#Discovery fit
discovery = configMgr.addTopLevelXMLClone(bkgOnly,"Example8_Discovery")
sigSample = Sample("discoveryMode")
sigSample.setNormFactor("mu_SIG",0.5,0.,1.)
sigSample.setNormByTheory()
discovery.addSamples(sigSample)
discovery.setSignalSample(sigSample)
meffChannel = discovery.addChannel("meff3Jet",meffRegions,meffNBins,meffBinLow,meffBinHigh)
meffChannel.useOverflowBin=True
discovery.setSignalChannels(meffChannel)

#Exclusion fits (MSUGRA grid)
sigSamples=["SU_180_360_0_10","SU_580_240_0_10","SU_740_330_0_10","SU_900_420_0_10","SU_1300_210_0_10"]
for sig in sigSamples:
    myTopLvl = configMgr.addTopLevelXMLClone(bkgOnly,"Example8_%s"%sig)
    sigSample = Sample(sig)
    sigSample.setNormFactor("mu_SIG",0.5,0.,1.)
    sigXSSyst = Systematic("SigXSec",None,1.1,0.9,"user","userOverallSys")
    sigSample.addSystematic(sigXSSyst)
    sigSample.setNormByTheory()
    myTopLvl.addSamples(sigSample)
    myTopLvl.setSignalSample(sigSample)
    meffChannel = myTopLvl.addChannel("meff3Jet",meffRegions,meffNBins,meffBinLow,meffBinHigh) 
    meffChannel.useOverflowBin=True
    myTopLvl.setSignalChannels(meffChannel)
