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
    myRegionDict["CRQ"] = "renamed"
   
    return myRegionDict

# Build a list with all the regions you want to use
def makeRegionList():
    regionList = ["CRY", "CRQ", "CRW", "CRT", "VRZ", "VRZf", "VRQ", "SR"]

    return regionList

# Define the colors for the pull bars
def getRegionColor(name):
    if name.find("VRZ") != -1: return ROOT.kBlue+3
    if name.find("VRQ") != -1: return kOrange
    if name.find("SR")  != -1: return ROOT.kBlack
    
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
    output_dir = "/glusterfs/atlas1/users/gbesjes/ZeroLeptonFitter/Paper13/20131115_results_bkgFits/results/"
    output_dir += "ZL2013_SR2j-meff800-metomeff0-met160-jet1pt130-jet2pt60-jet3pt0-jet4pt0-jet5pt0-jet6pt0-metSig8-dPhi0-Wunres0-Wres0-dPhiR0_Background" 
    filename = output_dir+"/Fit__Background_combined_NormalMeasurement_model_afterFit.root"
    
    # Run blinded?
    doBlind = True

    # Used as plot title
    region = "SR2jl"

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
