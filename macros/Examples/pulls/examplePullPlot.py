#!/usr/bin/env python

import ROOT
from ROOT import *
ROOT.PyConfig.IgnoreCommandLineOptions = True
gSystem.Load("libSusyFitter.so")
gROOT.Reset()
ROOT.gROOT.SetBatch(True)

import os, pickle, subprocess

import pullPlotUtils
from pullPlotUtils import makePullPlot 

# Build a dictionary that remaps region names
def renameRegions():
    myRegionDict = {}

    # Remap region names using the old name as index, e.g.:
    myRegionDict["VRWTPlus"] = "VRWT+"
    myRegionDict["VRWTMinus"] = "VRWT-"
    myRegionDict["VRWTPlusf"] = "VRWTf+"
    myRegionDict["VRWTMinusf"] = "VRWTf-"
    
    return myRegionDict

# Build a list with all the regions you want to use
def makeRegionList():
    regionList=[]

    regionList += ["CRW","CRT", "CRY", "CRQ"]
    regionList += ["VRZ", "VRZf"]
    regionList += ["VRWf", "VRWMf", "VRWM"]
    regionList += ["VRTf", "VRTMf", "VRTM"]

    regionList += ["VRT2L"]    
    regionList += ["VRWTPlus","VRWTMinus"]
    regionList += ["VRWTPlusf","VRWTMinusf"]
 
    regionList += ["VRQ1","VRQ2"]
    regionList += ["VRQ3","VRQ4"]
   
    regionList += ["VRWTau", "VRttbarTau"]        

    regionList += ["SR"]

    return regionList

# Define the colors for the pull bars
def getRegionColor(name):
    if name.find("VRZ") != -1: return kBlue+3
    if name.find("VRQ") != -1: return kOrange
    if name.find("SR")  != -1: return kBlack
    if name.find("VRZ") != -1: return kBlue+3
    if name.find("VRW") != -1: return kAzure-4
    if name.find("VRT") != -1: return kGreen-9
    if name.find("VRWT") != -1: return kYellow
    if name.find("VRQ") != -1: return kOrange
    if name.find("VRWTau") != -1: return kRed
    if name.find("VRttbarTau") != -1: return kRed
    if name.find("CRW") != -1: return kAzure-4
    if name.find("CRT") != -1: return kGreen-9
    if name.find("SR") != -1: return kBlack
    if name.find("BVR") != -1: return kRed+2

    return 1

# Define the colors for the stacked samples
def getSampleColor(sample):
    if sample == "Top":         return kGreen - 9
    if sample == "Wjets":       return kAzure - 4
    if sample == "Zjets":       return kBlue + 3
    if sample == "Multijets":   return kOrange
    if sample == "GAMMAjets":   return kYellow
    if sample == "Diboson":     return kRed + 3

    return 1

def main():
    # Override pullPlotUtils' default colours (which are all black)
    pullPlotUtils.getRegionColor = getRegionColor
    pullPlotUtils.getSampleColor = getSampleColor

    # Where's the background file? 
    filename = os.getenv("HISTFITTER")+"/macros/Examples/pulls/0lepton_bkgFit_example.root"
    
    # Run blinded?
    doBlind = True

    # Used as plot title
    region = "SRAm"

    # Samples to stack on top of eachother in each region
    samples = "Diboson,GAMMAjets,Multijets,Top,Wjets,Zjets"
    
    # Which regions do we use? 
    regionList = makeRegionList()

    # Regions for which the label gets changed
    renamedRegions = renameRegions()

    if not os.path.exists(filename):
        print "filename %s does not exist" % filename
        return
    
    # Run YieldsTable.py with all regions and samples requested
    cmd = "YieldsTable.py -c %s -s %s -w %s -o yield_%s_all.tex -t %sall" % (",".join(regionList), samples, filename, region, region)
    print cmd
    subprocess.call(cmd, shell=True)
    
    # Open the pickle
    pickleFilename = "yield_%s_all.pickle" % (region)
    makePullPlot(pickleFilename, regionList, samples, renamedRegions, region, doBlind)

if __name__ == "__main__":
    main()
