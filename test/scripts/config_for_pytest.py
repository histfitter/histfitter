## Config for CI testing

################################################################
## In principle all you have to setup is defined in this file ##
################################################################


### Usage examples

## Run from scratch background-only
# HistFitter.py -t -w -f -D "before,after" analysis/strong_2l2j.py  -u"--doSRHigh"

## Run an exclusion fit after having run bkg only
# HistFitter.py -w -f -F excl -D "before,after" analysis/strong_2l2j.py -g GG_N2_SLN1_2200_300 -u"--doSRHigh"

# signal names used with -g must match filename before _merged_processed.root
# e.g. GG_N2_SLN1_2200_300 or GG_N2_ZN1_1900_300, GG_N2_ZN1_1600_1300


from configManager import configMgr
from ROOT import kBlack,kWhite,kGray,kRed,kPink,kMagenta,kViolet,kBlue,kAzure,kCyan,kTeal,kGreen,kSpring,kYellow,kOrange
from ROOT import TColor
from configWriter import fitConfig,Measurement,Channel,Sample
from systematic import Systematic
import math,ROOT,os

from inspect import getframeinfo, currentframe

# Speed up processing 
gROOT.SetBatch(True)


########## Flags ##############
# default values which might be overridden by command line args below

includeOverflowBin = True
useStat    = True
useExpSys  = True
useThrSys  = True
useToys = False


input_file = "test_tree.root"
discovery_key = ''

nominal_tree_name = "_NoSys"

parser = argparse.ArgumentParser(description="HistFitter Testing")
parser.add_argument('--useToys', action="store_true")


if configMgr.userArg != "":
    args = parser.parse_args( configMgr.userArg.split() )

    useToys    = args.useToys

# name for analysis, used in a lot of directory and filenames
anaName = "hf_test"

configMgr.analysisName = anaName
analysisNameBase = anaName

#configMgr.doExclusion=True # True=exclusion, False=discovery
configMgr.nTOYs = 500
configMgr.calculatorType = 0 if useToys else 2 # 2=asymptotic calculator, 0=frequentist calculator
configMgr.testStatType = 3   # 3=one-sided profile likelihood test statistic (LHC default)
configMgr.nPoints = 20       # number of values scanned of signal-strength for upper-limit determination of signal strength.
#configMgr.scanRange = (0., 50.)

if useToys:
    configMgr.nPoints = 10
    configMgr.scanRange = (0., 2.)


ROOT.Math.MinimizerOptions.SetDefaultStrategy(0)


configMgr.fixSigXSec=True  # fix SigXSec: 0, +/-1sigma
configMgr.blindSR=False #our VR is put in as an SR

# Make sure the directories we want to use exist! 
try: os.mkdir('data/'+analysisNameBase )
except: pass
try: os.mkdir('results/'+configMgr.analysisName )
except: pass

##############
# Cache for discovery fits, use -r srcmet_Nov2_80_100 for example
configMgr.useCacheToTreeFallback = True
configMgr.useHistBackupCacheFile = True # enable the use of an alternate data file
configMgr.histBackupCacheFile =  "data/" + analysisNameBase + "/histCache.root" # the data file of your previous fit (= the backup cache file)

configMgr.outputFileName = "results/" + configMgr.analysisName  + "/Output.root"
configMgr.histCacheFile = "data/" + analysisNameBase + "/histCache.root"

if discovery_key != "":
    configMgr.histBackupCacheFile =  "data/" + analysisNameBase + "/histCache_disc_"+discovery_key+".root"
    if myFitType==FitType.Discovery:
        configMgr.outputFileName = "results/" + configMgr.analysisName   + "/Output_disc_" + discovery_key + ".root"
    else:
        configMgr.outputFileName = "results/" + configMgr.analysisName  + "/Output_bkg_" + discovery_key + ".root"
    configMgr.histCacheFile = "data/" + analysisNameBase + "/histCache_disc_"+discovery_key+".root"


if not configMgr.readFromTree:
    inputHistFile = ROOT.TFile(configMgr.histBackupCacheFile)
    if inputHistFile.IsOpen():
        print("Loading histograms from {}".format(inputHistFile) )
        for h in inputHistFile.GetListOfKeys():
            name = h.GetName()
            configMgr.hists[ h.GetName() ] = inputHistFile.Get( name )





######## Event Weights
configMgr.weights = ["weight"]
configMgr.cutsDict = {"SR":"m>100.",
                      "CR":"m<100."}

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


dataSample = Sample("data", kBlack)
dataSample.addInputs( [input_file] )
dataSample.setData()

sigSample = Sample("signal", kRed)
sigSample.addInputs( [input_file] )
sigSample.setNormByTheory(True)
sigSample.setNormFactor("mu_SIG",1.,0,100)

######### Systematics
bkg1Sample.addSystematic( Systematic('user_overallSys', '', 1.05, 0.95, 'user', 'overallSys') )
bkg1Sample.addSystematic( Systematic('weight_sys', configMgr.weights, ['weight','sys_weight'], ['weight','1./sys_weight'], 'weight', 'histoSys') )

bkg2Sample.addSystematic( Systematic('tree_sys', '', '_sys', '_sys', 'tree', 'normHistoSysOneSideSym') )

sigSample.addSystematic( Systematic('flat_sys', '', 1.10, 0.90, 'user', 'overallSys') )

########## Fit Config Base ##########
bkgName = "BkgOnly"
if discovery_key != "":
    bkgName += "_" + discovery_key
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
    SR = cfg_fit.addChannel('m',["SR_disc"],1,150,200)
else:
    SR = cfg_fit.addChannel('m',["SR"],2,100,200)
SRs.append(SR)

# Don't include overflow
for sr in SRs:
    sr.useOverflowBin = False

cfg_fit.addSignalChannels(SRs)
    
######################
## Control Regions
CRs = list()
CR = cfg_fit.addChannel('m',["CR"],1,50,100)
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
