
################################################################
## In principle all you have to setup is defined in this file ##
################################################################

from configManager import configMgr
from ROOT import kBlack,kWhite,kGray,kRed,kPink,kMagenta,kViolet,kBlue,kAzure,kCyan,kTeal,kGreen,kSpring,kYellow,kOrange
from configWriter import TopLevelXML,Measurement,ChannelXML,Sample
from systematic import Systematic

## First define HistFactory attributes
configMgr.analysisName = "MySimpleChannelAnalysis"
configMgr.outputFileName = "results/MySimpleChannelAnalysisOutput.root"

## Scaling calculated by outputLumi / inputLumi
configMgr.inputLumi = 20.0  # Luminosity of input TTree after weighting
configMgr.outputLumi = 500.0 # Luminosity required for output histograms
configMgr.setLumiUnits("pb-1")

## setting the parameters of the hypothesis test
#configMgr.nTOYs=5000
configMgr.fixSigXSec=True  # fix SigXSec: 0, +/-1sigma 
configMgr.calculatorType=2 # 2=asymptotic calculator, 0=frequentist calculator
configMgr.testStatType=3   # 3=one-sided profile likelihood test statistic (LHC default)
configMgr.nPoints=20       # number of values scanned of signal-strength for upper-limit determination of signal strength.

## Set the cache file
configMgr.histCacheFile = "data/" + configMgr.analysisName+".root"

## Suffix of nominal tree
configMgr.nomName = "_NoSys"

## Map regions to cut strings
configMgr.cutsDict = {"SR":"1.0"}

## Systematics to be applied
jes = Systematic("JES","_NoSys","_JESup","_JESdown","tree","overallSys")
#jes = Systematic("JES",None,1.2,0.8,"user","overallSys")

## List of samples and their plotting colours
allbkgSample = Sample("Bkg",kGreen)
#allbkgSample.setNormFactor("mu_AllBkg",1.,0.,5.)
allbkgSample.addSystematic(jes)
dataSample = Sample("Data",kBlack)
dataSample.setData()

commonSamples = [allbkgSample,dataSample]
configMgr.plotColours = [kGreen,kBlack]

## Parameters of the Measurement
measName = "BasicMeasurement"
measLumi = 1.
measLumiError = 0.039

## Parameters of Channels
cutsRegions = ["SR"]
cutsNBins = 1
cutsBinLow = 0.0
cutsBinHigh = 1.0

## Bkg-only fit
bkgOnly = configMgr.addTopLevelXML("SimpleChannel_BkgOnly")
bkgOnly.statErrThreshold=None #0.5
bkgOnly.addSamples(commonSamples)
#bkgOnly.addSystematic(jes)
meas = bkgOnly.addMeasurement(measName,measLumi,measLumiError)
meas.addPOI("mu_SIG")
cutsChannel = bkgOnly.addChannel("cuts",cutsRegions,cutsNBins,cutsBinLow,cutsBinHigh)

## Discovery fit
#discovery = configMgr.addTopLevelXMLClone(bkgOnly,"SimpleChannel_Discovery")
#discovery.clearSystematics()
#sigSample = Sample("discoveryMode",kBlue)
#sigSample.setNormFactor("mu_SIG",0.5,0.,1.)
#sigSample.setNormByTheory()
#discovery.addSamples(sigSample)
#discovery.setSignalSample(sigSample)

## Exclusion fits (MSUGRA grid)
#sigSamples=["SU_180_360_0_10","SU_580_240_0_10","SU_740_330_0_10","SU_900_420_0_10","SU_1300_210_0_10"]

sigSamples = ["SU_900_1000_1500_0_10"] ##,"SU_900_1100_1500_0_10","SU_900_1200_1500_0_10","SU_900_950_1500_0_10","SU_900_1050_1500_0_10","SU_900_1150_1500_0_10","SU_150_800_1500_0_10","SU_150_900_1500_0_10","SU_150_1000_1500_0_10","SU_150_1100_1500_0_10","SU_150_1200_1500_0_10","SU_150_850_1500_0_10","SU_150_950_1500_0_10","SU_150_1050_1500_0_10","SU_150_1150_1500_0_10","SU_1030_1050_1500_0_10","SU_300_800_1500_0_10","SU_300_900_1500_0_10","SU_300_1000_1500_0_10","SU_300_1100_1500_0_10","SU_300_1200_1500_0_10","SU_300_850_1500_0_10","SU_300_950_1500_0_10","SU_300_1050_1500_0_10","SU_300_1150_1500_0_10","SU_450_1050_1500_0_10","SU_450_1150_1500_0_10","SU_450_900_1500_0_10","SU_450_850_1500_0_10","SU_450_950_1500_0_10","SU_1040_1050_1500_0_10","SU_790_800_1500_0_10","SU_1050_1200_1500_0_10","SU_1050_1100_1500_0_10","SU_1050_1150_1500_0_10","SU_930_950_1500_0_10","SU_1190_1200_1500_0_10","SU_940_950_1500_0_10","SU_50_1050_1500_0_10","SU_50_900_1500_0_10","SU_50_850_1500_0_10","SU_50_1150_1500_0_10","SU_50_950_1500_0_10","SU_830_850_1500_0_10","SU_1090_1100_1500_0_10","SU_840_850_1500_0_10","SU_600_800_1500_0_10","SU_600_900_1500_0_10","SU_600_1000_1500_0_10","SU_600_1100_1500_0_10","SU_600_1200_1500_0_10","SU_600_850_1500_0_10","SU_600_950_1500_0_10","SU_600_1050_1500_0_10","SU_600_1150_1500_0_10","SU_990_1000_1500_0_10","SU_100_800_1500_0_10","SU_100_900_1500_0_10","SU_100_1000_1500_0_10","SU_100_1100_1500_0_10","SU_100_1200_1500_0_10","SU_100_850_1500_0_10","SU_100_950_1500_0_10","SU_100_1050_1500_0_10","SU_100_1150_1500_0_10","SU_1130_1150_1500_0_10","SU_750_800_1500_0_10","SU_750_900_1500_0_10","SU_750_1000_1500_0_10","SU_750_1100_1500_0_10","SU_750_1200_1500_0_10","SU_750_850_1500_0_10","SU_750_950_1500_0_10","SU_750_1050_1500_0_10","SU_750_1150_1500_0_10","SU_1140_1150_1500_0_10","SU_890_900_1500_0_10"]

#sigSamples = [
##  "SU_900_1250_1500_0_10",
#  "SU_900_1000_1500_0_10",
##   "SU_900_1100_1500_0_10",
##   "SU_900_1200_1500_0_10",
##   "SU_900_1300_1500_0_10",
##   "SU_900_950_1500_0_10",
##   "SU_900_1050_1500_0_10",
##   "SU_900_1150_1500_0_10",
##   "SU_790_800_1500_0_10",
##   "SU_1030_1050_1500_0_10",
##   "SU_300_800_1500_0_10",
##   "SU_300_1250_1500_0_10",
##   "SU_300_900_1500_0_10",
##   "SU_300_1000_1500_0_10",
##   "SU_300_1100_1500_0_10",
##   "SU_300_1200_1500_0_10",
##   "SU_300_850_1500_0_10",
##   "SU_300_1300_1500_0_10",
##   "SU_300_950_1500_0_10",
##   "SU_300_1050_1500_0_10",
##   "SU_300_1150_1500_0_10",
##   "SU_450_1250_1500_0_10",
##   "SU_450_900_1500_0_10",
##   "SU_450_850_1500_0_10",
##   "SU_450_1300_1500_0_10",
##   "SU_450_950_1500_0_10",
##   "SU_450_1050_1500_0_10",
##   "SU_450_1150_1500_0_10",
##   "SU_1040_1050_1500_0_10",
##   "SU_150_800_1500_0_10",
##   "SU_150_1250_1500_0_10",
##   "SU_150_900_1500_0_10",
##   "SU_150_1000_1500_0_10",
##   "SU_150_1100_1500_0_10",
##   "SU_150_1200_1500_0_10",
##   "SU_150_850_1500_0_10",
##   "SU_150_1300_1500_0_10",
##   "SU_150_950_1500_0_10",
##   "SU_150_1050_1500_0_10",
##   "SU_150_1150_1500_0_10",
##   "SU_1050_1200_1500_0_10",
##   "SU_1050_1100_1500_0_10",
##   "SU_1050_1250_1500_0_10",
##   "SU_1050_1300_1500_0_10",
##   "SU_1050_1150_1500_0_10",
##   "SU_930_950_1500_0_10",
##   "SU_1190_1200_1500_0_10",
##   "SU_940_950_1500_0_10",
##   "SU_50_1250_1500_0_10",
##   "SU_50_900_1500_0_10",
##   "SU_50_850_1500_0_10",
##   "SU_50_1300_1500_0_10",
##   "SU_50_950_1500_0_10",
##   "SU_50_1050_1500_0_10",
##   "SU_50_1150_1500_0_10",
##   "SU_830_850_1500_0_10",
##   "SU_1090_1100_1500_0_10",
##   "SU_840_850_1500_0_10",
##   "SU_600_800_1500_0_10",
##   "SU_600_1250_1500_0_10",
##   "SU_600_900_1500_0_10",
##   "SU_600_1000_1500_0_10",
##   "SU_600_1100_1500_0_10",
##   "SU_600_1200_1500_0_10",
##   "SU_600_850_1500_0_10",
##   "SU_600_1300_1500_0_10",
##   "SU_600_950_1500_0_10",
##   "SU_600_1050_1500_0_10",
##   "SU_600_1150_1500_0_10",
##   "SU_990_1000_1500_0_10",
##   "SU_100_800_1500_0_10",
##   "SU_100_1250_1500_0_10",
##   "SU_100_900_1500_0_10",
##   "SU_100_1000_1500_0_10",
##   "SU_100_1100_1500_0_10",
##   "SU_100_1200_1500_0_10",
##   "SU_100_850_1500_0_10",
##   "SU_100_1300_1500_0_10",
##   "SU_100_950_1500_0_10",
##   "SU_100_1050_1500_0_10",
##   "SU_100_1150_1500_0_10",
##   "SU_1130_1150_1500_0_10",
##   "SU_750_800_1500_0_10",
##   "SU_750_1250_1500_0_10",
##   "SU_750_900_1500_0_10",
##   "SU_750_1000_1500_0_10",
##   "SU_750_1100_1500_0_10",
##   "SU_750_1200_1500_0_10",
##   "SU_750_850_1500_0_10",
##   "SU_750_1300_1500_0_10",
##   "SU_750_950_1500_0_10",
##   "SU_750_1050_1500_0_10",
##   "SU_750_1150_1500_0_10",
##   "SU_1140_1150_1500_0_10",
##   "SU_890_900_1500_0_10",
##]


for sig in sigSamples:
    myTopLvl = configMgr.addTopLevelXMLClone(bkgOnly,"SimpleChannel_%s"%sig)
    #myTopLvl.removeSystematic(jes)
    sigSample = Sample(sig,kBlue)
    sigSample.setNormFactor("mu_SIG",0.5,0.,1.)
    sigXSSyst = Systematic("SigXSec",None,None,None,"user","overallSys")
    sigSample.addSystematic(sigXSSyst)
    #sigSample.addSystematic(jesSig)
    sigSample.setNormByTheory()
    myTopLvl.addSamples(sigSample)
    myTopLvl.setSignalSample(sigSample)
