#!/usr/bin/env python
"""
Merge separate syst table runs using hte -k option
of SysTable.py into a combined table

To dump the dict into a file, do something like this:
cat job_*.out | grep grepkey | sed 's/grepkey/regSys/g' > srmed.dict

Jonathan Long
Dec, 2021
"""
import ast

from ROOT import gROOT,gSystem,gDirectory
gSystem.Load("libSusyFitter.so")

from SysTableTex import *

# list out your regions
for chan in ["SRLow", "SRMed", "SRHigh"]:

    # arguments to be passed to tablefragment
    chanList = []
    skiplist = ['sqrtnobsa', 'totbkgsysa', 'poisqcderr','sqrtnfitted','totsyserr','nfitted']
    # chanStr is an underscore separated list of the regions used for the label
    chanStr = chan + "_"+chan.replace("SR","CR")
    showPercent = True
    outputFileName = f"systable_{chan.lower()}_bkg_comb_postfitm2.tex"
    
    regSys = {}
    chanSys = {}
    
    # paste pathes to dictionaries here
    if chan == "SRLow":
        execfile("srlow.dict")
    elif chan == "SRMed":
        execfile("srmed.dict")
    elif chan == "SRHigh":
        execfile("srhigh.dict")
    
    # append name of region
    chanList.append(chan)
    chanSys[chan] = regSys
    
    line_chanSysTight = tablefragment(chanSys,chanList,skiplist,chanStr,showPercent)
    f = open(outputFileName, 'w')
    f.write( line_chanSysTight )
    f.close()
    
    print(f"Wrote to {outputFileName}")
