"""
 **********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 *                                                                                *
 * Description:                                                                   *
 *      Example pull plot based on the pullPlotUtils module. Adapt to create      *
 *      your own style of pull plot. Illustrates all functions to redefine to     *
 *      change labels, colours, etc.                                              * 
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************
"""

#!/usr/bin/env python

import ROOT
from ROOT import *
ROOT.PyConfig.IgnoreCommandLineOptions = True
gSystem.Load("libHistFitter.so")
#gROOT.Reset()
ROOT.gROOT.SetBatch(True)

import os, pickle, subprocess

import pullPlotUtils
from pullPlotUtils import makePullPlot 

# Build a dictionary that remaps region names
def renameRegions():
    myRegionDict = {}

    # Remap region names using the old name as index, e.g.:
    myRegionDict["SS_metmeff2Jet"] = "SR exclusion"
    myRegionDict["SLVR2_nJet"] = "VR2"
    
    
    return myRegionDict

# Build a list with all the regions you want to use
def makeRegionList():
    regionList=[]

    regionList += ["SLWR_nJet","SLTR_nJet"]
    regionList += ["SR1sl2j_cuts","SLVR2_nJet","SSloose_metmeff2Jet"]
    regionList += ["SS_metmeff2Jet"]

    return regionList

# Define the colors for the pull bars
def getRegionColor(name):
    if name.find("SLWR") != -1: return kBlue+3
    if name.find("SLTR") != -1: return kBlue+3
    if name.find("SR") != -1: return kOrange
    if name.find("SLVR")  != -1: return kOrange
    if name.find("SSloose")  != -1: return kOrange
    if name.find("SS_") != -1: return kRed
 
    return 1

# Define the colors for the stacked samples
def getSampleColor(sample):
    if sample == "Top":         return kGreen - 9
    if sample == "WZ":       return kAzure + 1
    if sample == "BG":     return kYellow - 3
    if sample == "QCD":     return kGray + 1
    else:
        print("cannot find color for sample (",sample,")")

    return 1

def main():
    # Override pullPlotUtils' default colours (which are all black)
    pullPlotUtils.getRegionColor = getRegionColor
    pullPlotUtils.getSampleColor = getSampleColor

    # Where's the workspace file? 
    wsfilename = "./results/MyConfigExample/BkgOnly_combined_NormalMeasurement_model_afterFit.root" # 

    # Where's the pickle file?
    pickleFilename = "./results/MyYieldsTable.pickle"
    
    # Run blinded?
    doBlind = True

    # Used as plot title
    region = "SS_metmeff2Jet"

    # Samples to stack on top of eachother in each region
    samples = "Top,WZ,BG,QCD"
    
    # Which regions do we use? 
    regionList = makeRegionList()

    # Regions for which the label gets changed
    renamedRegions = renameRegions()

    if not os.path.exists(pickleFilename):
        print("pickle filename %s does not exist" % pickleFilename)
        print("will proceed to run yieldstable again")
        
        # Run YieldsTable.py with all regions and samples requested
        cmd = "YieldsTable.py -c {} -s {} -w {} -o results/MyYieldsTable.tex".format(",".join(regionList), samples, wsfilename)
        print(cmd)
        subprocess.call(cmd, shell=True)

    if not os.path.exists(pickleFilename):
        print("pickle filename %s still does not exist" % pickleFilename)
        return
    
    # Open the pickle and make the pull plot
    makePullPlot(pickleFilename, regionList, samples, renamedRegions, region, doBlind, plotSignificance=False)

if __name__ == "__main__":
    main()
