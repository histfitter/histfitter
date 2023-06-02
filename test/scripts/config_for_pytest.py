## Config for CI testing

from configManager import configMgr
from ROOT import kBlack,kWhite,kGray,kRed,kPink,kMagenta,kViolet,kBlue,kAzure,kCyan,kTeal,kGreen,kSpring,kYellow,kOrange
from ROOT import TColor
from configWriter import fitConfig,Measurement,Channel,Sample
from systematic import Systematic
import ROOT,os

from inspect import getframeinfo, currentframe

# Speed up processing 
gROOT.SetBatch(True)


########## Flags ##############
# default values which might be overridden by command line args below

includeOverflowBin = True
useStat    = True
useToys = False
manualBackupCache = None


input_file = "test_tree.root"

nominal_tree_name = "_NoSys"

parser = argparse.ArgumentParser(description="HistFitter Testing")
parser.add_argument('--useToys', action="store_true")
parser.add_argument('--manualBackupCache')


if configMgr.userArg != "":
    args = parser.parse_args( configMgr.userArg.split() )

    useToys    = args.useToys
    manualBackupCache = args.manualBackupCache

# name for analysis, used in a lot of directory and filenames
anaName = "hf_test"

configMgr.analysisName = anaName
analysisNameBase = anaName

#configMgr.doExclusion=True # True=exclusion, False=discovery
configMgr.nTOYs = 500
configMgr.calculatorType = 0 if useToys else 2 # 2=asymptotic calculator, 0=frequentist calculator
configMgr.testStatType = 3   # 3=one-sided profile likelihood test statistic (LHC default)
configMgr.nPoints = 20       # number of values scanned of signal-strength for upper-limit determination of signal strength.
configMgr.scanRange = (0., 2.)

if useToys:
    configMgr.nPoints = 10


ROOT.Math.MinimizerOptions.SetDefaultStrategy(0)


configMgr.fixSigXSec=True  # fix SigXSec: 0, +/-1sigma
configMgr.blindSR=False #our VR is put in as an SR

# Make sure the directories we want to use exist! 
try: os.mkdir('data/'+analysisNameBase )
except: pass
try: os.mkdir('results/'+configMgr.analysisName )
except: pass

##############
configMgr.useHistBackupCacheFile = True # enable the use of an alternate data file
if manualBackupCache is None:
    configMgr.useCacheToTreeFallback = True
    configMgr.histBackupCacheFile =  "data/" + analysisNameBase + "/histCache.root"
else:
    configMgr.useCacheToTreeFallback = False
    configMgr.histBackupCacheFile =  manualBackupCache
    configMgr.forceNorm = False # If we don't disable this, HF tries to build the Norm histograms from the trees anyways, even if useCacheToTreeFallback is set to Fale

configMgr.outputFileName = "results/" + configMgr.analysisName  + "/Output.root"
configMgr.histCacheFile = "data/" + analysisNameBase + "/histCache.root"


if myFitType==FitType.Discovery:
    configMgr.histBackupCacheFile =  "data/" + analysisNameBase + "/histCache_disc.root" # the data file of your previous fit (= the backup cache file)
    configMgr.outputFileName = "results/" + configMgr.analysisName  + "/Output_disc.root"
    configMgr.histCacheFile = "data/" + analysisNameBase + "/histCache_disc.root"


if not configMgr.readFromTree:
    inputHistFile = ROOT.TFile(configMgr.histBackupCacheFile)
    if inputHistFile.IsOpen():
        print(f"Loading histograms from {inputHistFile}" )
        for h in inputHistFile.GetListOfKeys():
            name = h.GetName()
            configMgr.hists[ h.GetName() ] = inputHistFile.Get( name )





######## Event Weights and Cuts
configMgr.weights = ["weight"]
configMgr.cutsDict = {"SR":"m>100.",
                      "SR_disc":"m>150.",
                      "CR":"m<100."}

configMgr.outputLumi = configMgr.inputLumi = 140.1

####### Setup Data and Background Samples ############
bkg1Sample = Sample("bkg1",TColor.GetColor('#fe9929')) 
bkg1Sample.setStatConfig(useStat)
bkg1Sample.setSuffixTreeName("_nom")
bkg1Sample.addInputs( [input_file] )
bkg1Sample.setNormByTheory(True)

bkg2Sample = Sample("bkg2", TColor.GetColor('#9ecae1')) 
bkg2Sample.setStatConfig(useStat)
bkg2Sample.setSuffixTreeName("_nom")
bkg2Sample.addInputs( [input_file] )
bkg2Sample.setNormByTheory(False)
bkg2Sample.setNormFactor("mu_bkg",1.,0.,10.)
bkg2Sample.setNormRegions([('CR', 'm')])


dataSample = Sample("data", kBlack)
dataSample.addInputs( [input_file] )
dataSample.setData()

sigSample = Sample("signal", kRed)
sigSample.addInputs( [input_file] )
sigSample.setNormByTheory(True)
sigSample.setNormFactor("mu_SIG",1.,0,100)

######### Systematics
bkg1Sample.addSystematic( Systematic('weight_histoSys', configMgr.weights, ['weight','sys_weight1'], ['weight','1./sys_weight1'], 'weight', 'histoSys') )
bkg1Sample.addSystematic( Systematic('weight_overallSys', configMgr.weights, ['weight','sys_weight2'], ['weight','1./sys_weight2'], 'weight', 'overallSys') )
bkg1Sample.addSystematic( Systematic('weight_overallHistoSys', configMgr.weights, ['weight','sys_weight3'], ['weight','1./sys_weight3'], 'weight', 'overallHistoSys') )
bkg1Sample.addSystematic( Systematic('weight_histoSysOneSide', configMgr.weights, ['weight', 'sys_weight4'], ['weight', 'sys_weight4'], 'weight', 'histoSysOneSide') )
bkg1Sample.addSystematic( Systematic('weight_histoSysOneSideSym', configMgr.weights, ['weight', 'sys_weight5'], ['weight', 'sys_weight5'], 'weight', 'histoSysOneSideSym') )
bkg1Sample.addSystematic( Systematic('weight_histoSysEnvelopeSym', configMgr.weights, ['weight', 'sys_weight6'], ['weight', '1/sys_weight6'], 'weight', 'histoSysEnvelopeSym') )
bkg1Sample.addSystematic( Systematic('user_overallSys', '', 1.05, 0.95, 'user', 'userOverallSys') )
bkg1Sample.addSystematic( Systematic('user_histoSys', '', 1.05, 0.95, 'user', 'userHistoSys') )

bkg2Sample.addSystematic( Systematic('weight_overallNormSys', configMgr.weights, ['weight', 'sys_weight1'], ['weight', '1./sys_weight1'], 'weight', 'overallNormSys') )
bkg2Sample.addSystematic( Systematic('weight_normHistoSys', configMgr.weights, ['weight', 'sys_weight2'], ['weight', '1./sys_weight2'], 'weight', 'normHistoSys') )
bkg2Sample.addSystematic( Systematic('weight_normHistoSysOneSide', configMgr.weights, ['weight', 'sys_weight3'], ['weight', 'sys_weight3'], 'weight', 'normHistoSysOneSide') )
bkg2Sample.addSystematic( Systematic('weight_normHistoSysEnvelopeSym', configMgr.weights, ['weight', 'sys_weight4'], ['weight', '1./sys_weight4'], 'weight', 'normHistoSysEnvelopeSym') )
bkg2Sample.addSystematic( Systematic('weight_overallNormHistoSysEnvelopeSym', configMgr.weights, ['weight', 'sys_weight5'], ['weight', '1./sys_weight5'], 'weight', 'overallNormHistoSysEnvelopeSym') )
bkg2Sample.addSystematic( Systematic('tree_normHistoSysOneSideSym', '', '_sys', '_sys', 'tree', 'normHistoSysOneSideSym') )
bkg2Sample.addSystematic( Systematic('user_normHistoSys', '', 1.05, 0.95, 'user', 'userNormHistoSys') )

sigSample.addSystematic( Systematic('flat_sys', '', 1.10, 0.90, 'user', 'userOverallSys') )

########## Fit Config Base ##########
bkgName = "BkgOnly"
cfg_fit = configMgr.addFitConfig(bkgName)
if useStat:
    cfg_fit.statErrThreshold=0.03 
else:
    cfg_fit.statErrThreshold=None

######## Add samples
cfg_fit.addSamples([bkg1Sample, bkg2Sample, dataSample])  

##################
# Signal region
SRs = list()
if myFitType==FitType.Discovery:
    SR = cfg_fit.addChannel('cuts',["SR_disc"],1,0.5,1.5)
else:
    SR = cfg_fit.addChannel('m',["SR"],2,100,200)
SRs.append(SR)

# Don't include overflow
for sr in SRs:
    sr.useOverflowBin = False
    sr.showLumi = True

cfg_fit.addSignalChannels(SRs)
    
######################
## Control Regions
CRs = list()
CR = cfg_fit.addChannel('m',["CR"],1,50,100)
CR.showLumi = True
bkg2Sample.setNormRegions(["CR","m"])
CRs.append(CR)

for cr in CRs:
    cr.useOverflowBin = False
    
cfg_fit.addBkgConstrainChannels(CRs)

####### Setup Fits ###########

measName = "BasicMeasurement"
measLumi = 1.
measLumiError = 0.017 

meas = cfg_fit.addMeasurement(measName,measLumi,measLumiError)
#meas.addParamSetting("Lumi",True,1)

if myFitType==FitType.Discovery:
    meas.addPOI("mu_Discovery")
else:
    meas.addPOI("mu_SIG")





######## Exclusion Fit #############
if myFitType==FitType.Exclusion:

    sigConfig = configMgr.addFitConfigClone(cfg_fit,"Sig_excl")
    sigConfig.addSamples(sigSample)
    sigConfig.setSignalSample(sigSample)
    # Remove background fit
    configMgr.removeFitConfig(bkgName)

######## Discovery Fit #############
elif myFitType==FitType.Discovery:
    for sr in SRs:
        sr.addDiscoverySamples(["Discovery"],[1.],[0.],[1000.],[kRed])
                    
    discovery = configMgr.addFitConfigClone(cfg_fit,"Discovery")

    # set disc sample as signal
    for sr in SRs:
        for sample in sr.sampleList:
            if "disc" in sample.name.lower():
                discovery.setSignalSample(sample)

    if len(SRs) > 1:
        print('Warning, discovery setup with multiple SRs')

    discovery.addSignalChannels(SRs) 

    # Remove background fit
    configMgr.removeFitConfig(bkgName)

    
######## Background Only Fit #############
else:
    pass
