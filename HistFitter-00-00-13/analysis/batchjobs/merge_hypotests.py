#!/usr/bin/env python
# author: Matthias Lungwitz (matthias.lungwitz@cern.ch)
#
# Merge HypoTestInverterResult for a single Signal point
#

import glob,sys
from ROOT import gROOT,gSystem,gDirectory,RooAbsData,RooRandom,RooWorkspace,TFile

try:
##    from ROOT import HypoTestInverterResult
    gSystem.Load("libSusyFitter.so")
    from ROOT import *

except Exception, msg:
    print "Couldn't import HypoTestInverterResult - please setup appropriate root version"
    sys.exit()

##directories = glob.glob("GMSB*hypotestresult")
directories = glob.glob("GMSB_3_2d_8*hypotestresult")


for dir in directories:
    print dir
    files = glob.glob(dir+"/*/*.root")

    first=True
    
    outfile = TFile(dir+"/Merged_Output_hypotest.root","RECREATE")

    resultname = "hypo_"+dir.replace("_hypotestresult","")

    global combinedresult

    for f in files:
        file = TFile.Open(f)
        hyporesult = file.Get(resultname)

        if first:
            combinedresult = hyporesult

            first = False
        else:
            combinedresult.Add(hyporesult)


    outfile.cd()
    combinedresult.Write()
    outfile.Write()
    outfile.Close()

