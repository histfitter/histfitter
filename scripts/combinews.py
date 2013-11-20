#!/afs/cern.ch/sw/lcg/external/Python/2.6.5/x86_64-slc5-gcc46-opt/bin/python

import glob,sys
from ROOT import gROOT,gSystem,gDirectory,RooAbsData,RooRandom,RooWorkspace,TFile,vector,TString

try:
    gSystem.Load("libSusyFitter.so")
    from ROOT import *

except Exception, msg:
    print "Couldn't import HistFitter - please setup appropriate root version"
    sys.exit()

### file lists

fi1 = glob.glob('SoftLeptonMoriond2013_SRs1L_SM_GG1step_*/Fit_SRs1L_SM_GG1step_*_combined_BasicMeasurement_model.root')
fi2 = glob.glob('Sig_SM_SS1step_*_combined_BasicMeasurement_model.root')
#fi3 = glob.glob('Sig_SM_SS1step_*_combined_BasicMeasurement_model.root')

f1 = vector('TString')()
f2 = vector('TString')()
#f3 = vector('TString')()
for file in fi1: f1.push_back(TString(file))
for file in fi2: f2.push_back(TString(file))
#for file in fi3: f3.push_back(TString(file))

format1 = 'filename+SoftLeptonMoriond2013_SRs1L_SM_GG1step_%f_%f_%f+combined'
format2 = 'filename+Sig_SM_SS1step_%f_%f_%f+combined'
#format3 = 'filename+Sig_SM_SS1step_%f_%f_%f'

interpretation = 'm1:m2:m3'

outfile = 'combined+wsid' ## workspace id will be added to filename
outws_prefix = 'combined' ## prefix for workspace name

selection = '1' # select all points, can depend on m1,m2,m3
combineVars = ''  # correlate these variables between the various analysis. Default is parameter of interest, Lumi.

### example combination with two analyses
status = MatchingCountingExperiments( outfile, outws_prefix, f1, format1, f2, format2, interpretation, selection, combineVars )




### example with three analyses
#status = MatchingCountingExperiments( outfile, outws_prefix, f1, format1, f2, format2, f3, format3, interpretation )


