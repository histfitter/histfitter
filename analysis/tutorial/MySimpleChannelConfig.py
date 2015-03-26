
################################################################
## In principle all you have to setup is defined in this file ##
################################################################

from configManager import configMgr
from ROOT import kBlack,kWhite,kGray,kRed,kPink,kMagenta,kViolet,kBlue,kAzure,kCyan,kTeal,kGreen,kSpring,kYellow,kOrange
from configWriter import fitConfig,Measurement,Channel,Sample
from systematic import Systematic

## First define HistFactory attributes
configMgr.analysisName = "MySimpleChannelAnalysis"
configMgr.outputFileName = "results/" + configMgr.analysisName +".root"
configMgr.histCacheFile = "data/"+configMgr.analysisName+".root"

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

## set scan range for the upper limit
#configMgr.scanRange = (0., 1.)

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
#allbkgSample.addSystematic(jesWT)
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
bkgOnly = configMgr.addFitConfig("SimpleChannel_BkgOnly")
bkgOnly.statErrThreshold=None #0.5
bkgOnly.addSamples(commonSamples)
bkgOnly.addSystematic(jes)
meas = bkgOnly.addMeasurement(measName,measLumi,measLumiError)
meas.addPOI("mu_SIG")
cutsChannel = bkgOnly.addChannel("cuts",cutsRegions,cutsNBins,cutsBinLow,cutsBinHigh)

## Discovery fit
#discovery = configMgr.adFitConfigClone(bkgOnly,"SimpleChannel_Discovery")
#discovery.clearSystematics()
#sigSample = Sample("discoveryMode",kBlue)
#sigSample.setNormFactor("mu_SIG",0.5,0.,1.)
#sigSample.setNormByTheory()
#discovery.addSamples(sigSample)
#discovery.setSignalSample(sigSample)

## Exclusion fits (MSUGRA grid)
#sigSamples=["SU_180_360_0_10","SU_580_240_0_10","SU_740_330_0_10","SU_900_420_0_10","SU_1300_210_0_10"]
sigSamples = ["SU_680_310_0_10","SU_440_145_0_10","SU_200_160_0_10","SU_440_340_0_10","SU_440_100_0_10","SU_120_130_0_10","SU_600_280_0_10","SU_320_115_0_10","SU_360_175_0_10","SU_920_310_0_10","SU_280_205_0_10","SU_1080_340_0_10","SU_40_280_0_10","SU_760_160_0_10","SU_200_115_0_10","SU_280_280_0_10","SU_40_160_0_10","SU_520_280_0_10","SU_120_220_0_10","SU_680_220_0_10","SU_40_115_0_10","SU_920_190_0_10","SU_320_130_0_10","SU_440_280_0_10","SU_360_100_0_10","SU_120_160_0_10","SU_1080_190_0_10","SU_840_250_0_10","SU_120_100_0_10","SU_120_340_0_10","SU_840_280_0_10","SU_80_115_0_10","SU_840_130_0_10","SU_320_175_0_10","SU_120_205_0_10","SU_520_100_0_10","SU_400_130_0_10","SU_360_310_0_10","SU_160_115_0_10","SU_1000_310_0_10","SU_40_220_0_10","SU_440_130_0_10","SU_1000_190_0_10","SU_80_220_0_10","SU_840_160_0_10","SU_120_145_0_10","SU_440_175_0_10","SU_360_280_0_10","SU_320_145_0_10","SU_400_160_0_10","SU_1000_340_0_10","SU_600_310_0_10","SU_320_190_0_10","SU_840_310_0_10","SU_200_220_0_10","SU_440_205_0_10","SU_360_205_0_10","SU_120_280_0_10","SU_1080_130_0_10","SU_160_145_0_10","SU_520_250_0_10","SU_840_100_0_10","SU_160_220_0_10","SU_120_190_0_10","SU_40_205_0_10","SU_280_250_0_10","SU_80_145_0_10","SU_200_175_0_10","SU_840_190_0_10","SU_240_145_0_10","SU_160_205_0_10","SU_400_115_0_10","SU_440_250_0_10","SU_600_340_0_10","SU_80_100_0_10","SU_520_190_0_10","SU_1160_190_0_10","SU_80_130_0_10","SU_400_190_0_10","SU_400_175_0_10","SU_600_130_0_10","SU_1080_100_0_10","SU_200_340_0_10","SU_1160_310_0_10","SU_440_160_0_10","SU_240_220_0_10","SU_200_100_0_10","SU_240_130_0_10","SU_360_130_0_10","SU_1000_250_0_10","SU_920_130_0_10","SU_240_190_0_10","SU_520_340_0_10","SU_40_175_0_10","SU_240_100_0_10","SU_400_145_0_10","SU_40_145_0_10","SU_240_205_0_10","SU_1080_280_0_10","SU_600_250_0_10","SU_360_145_0_10","SU_520_130_0_10","SU_1000_130_0_10","SU_440_310_0_10","SU_600_160_0_10","SU_920_280_0_10","SU_760_280_0_10","SU_280_190_0_10","SU_280_175_0_10","SU_120_310_0_10","SU_440_220_0_10","SU_1000_220_0_10","SU_1160_250_0_10","SU_400_205_0_10","SU_160_160_0_10","SU_1000_280_0_10","SU_1000_160_0_10","SU_400_100_0_10","SU_760_190_0_10","SU_680_160_0_10","SU_840_220_0_10","SU_360_340_0_10","SU_1080_220_0_10","SU_360_250_0_10","SU_760_130_0_10","SU_440_115_0_10","SU_240_160_0_10","SU_200_310_0_10","SU_200_145_0_10","SU_600_220_0_10","SU_280_130_0_10","SU_520_220_0_10","SU_1080_160_0_10","SU_40_190_0_10","SU_1160_160_0_10","SU_280_310_0_10","SU_920_160_0_10","SU_80_190_0_10","SU_40_310_0_10","SU_1160_130_0_10","SU_40_250_0_10","SU_40_100_0_10","SU_400_220_0_10","SU_40_340_0_10","SU_1000_100_0_10","SU_120_175_0_10","SU_280_220_0_10","SU_760_340_0_10","SU_240_115_0_10","SU_440_190_0_10","SU_1160_340_0_10","SU_600_100_0_10","SU_200_250_0_10","SU_280_145_0_10","SU_200_190_0_10","SU_200_205_0_10","SU_760_250_0_10","SU_120_250_0_10","SU_80_175_0_10","SU_40_130_0_10","SU_920_250_0_10","SU_80_160_0_10","SU_240_175_0_10","SU_280_100_0_10","SU_1080_310_0_10","SU_920_340_0_10","SU_120_115_0_10","SU_1160_100_0_10","SU_280_340_0_10","SU_1160_220_0_10","SU_200_130_0_10","SU_160_175_0_10","SU_360_220_0_10"]

#if not 'sigSamples' in dir():
#    sigSamples=["SU_680_310_0_10"]


for sig in sigSamples:
    myTopLvl = configMgr.addFitConfigClone(bkgOnly,"SimpleChannel_%s"%sig)
    #myTopLvl.removeSystematic(jes)
    sigSample = Sample(sig,kBlue)
    sigSample.setNormFactor("mu_SIG",0.5,0.,1.)
    sigXSSyst = Systematic("SigXSec",configMgr.weights,1.1,0.9,"user","overallSys")
    sigSample.addSystematic(sigXSSyst)
    #sigSample.addSystematic(jesSig)
    sigSample.setNormByTheory()
    myTopLvl.addSamples(sigSample)
    myTopLvl.setSignalSample(sigSample)
    ch = myTopLvl.getChannel("cuts",cutsRegions)
    myTopLvl.setSignalChannels(ch)
