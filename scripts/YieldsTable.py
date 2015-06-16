#!/usr/bin/env python
"""
 * Project : HistFitter - A ROOT-based package for statistical data analysis      *
 * Package : HistFitter                                                           *
 * Script  : YieldsTable.py                                                       *
 * Created : November 2012                                                        *
 *                                                                                *
 * Description:                                                                   *
 *      Script for producing publication-quality yields tables                    *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group                                                          *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
""" 

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True

from ROOT import gROOT,gSystem,gDirectory, PyConfig
gSystem.Load("libSusyFitter.so")
gROOT.Reset()

from ROOT import TFile, RooWorkspace, TObject, TString, RooAbsReal, RooRealVar, RooFitResult, RooDataSet, RooAddition, RooArgSet, RooFormulaVar, RooAbsData, RooRandom, RooArgList, RooBinningCategory
from ROOT import TMath, TMap, RooExpandedFitResult, Util

from cmdLineUtils import getPdfInRegions,getName,getPdfInRegionsWithRangeName

from YieldsTableTex import *
import os
import sys

def latexfitresults(filename,regionList,sampleList,dataname='obsData',showSum=False, doAsym=True, blinded=False, splitBins=False):
  """
  Calculate before/after-fit yields in all channels given
  
  @param filename The filename containing afterFit workspace
  @param regionList A list of regions to be considered
  @param sampleList A list of samples to be considered
  @param dataname The name of dataset (default='obsData')
  @param showSum Calculates sum of all regions if set to true (default=False)
  @param doAsym Calculates asymmetric errors taken from MINOS (default=True)
  @param blinded Observed event count will not be shown if set to True (default=False)
  @param splitBins Calculates bin-by-bin yields for all regions if set to True (default=False)
  """

  """
  pick up workspace from file
  """
  workspacename = 'w'
  w = Util.GetWorkspaceFromFile(filename,'w')
  if w==None:
    print "ERROR : Cannot open workspace : ", workspacename
    sys.exit(1) 

  """
  pick up after-fit RooExpandedFitResult from workspace
  """
  resultAfterFit = w.obj('RooExpandedFitResult_afterFit')
  if resultAfterFit==None:
    print "ERROR : Cannot open fit result after fit RooExpandedFitResult_afterFit"
    sys.exit(1)

  """
  pick up before-fit RooExpandedFitResult from workspace
  """
  resultBeforeFit = w.obj('RooExpandedFitResult_beforeFit')
  if resultBeforeFit==None:
    print "ERROR : Cannot open fit result before fit RooExpandedFitResult_beforeFit"
    sys.exit(1)

  """
  pick up dataset from workspace
  """
  data_set = w.data(dataname)
  if data_set==None:
    print "ERROR : Cannot open dataset : ", "data_set"+suffix
    sys.exit(1)
      
  """
  pick up channel category (RooCategory) from workspace
  """
  regionCat = w.obj("channelCat")
  if not blinded:
    data_set.table(regionCat).Print("v")

  """
  find full (long) name list of regions (i.e. short=SR3J, long=SR3J_meffInc30_JVF25pt50)
  """
  regionFullNameList = [ Util.GetFullRegionName(regionCat, region) for region in regionList]


  """
  load afterFit workspace snapshot (=set all parameters to values after fit)
  """
  snapshot =  'snapshot_paramsVals_RooExpandedFitResult_afterFit'
  w.loadSnapshot(snapshot)

  if not w.loadSnapshot(snapshot):
    print "ERROR : Cannot load snapshot : ", snapshot
    sys.exit(1)

  """
  define set, for all names/yields to be saved in
  """
  tablenumbers = {}

  """
  if showSum=True define names for sum of all regions and add to regionList
  """
  sumName = ""
  for index, reg in enumerate(regionList):
    if index == 0:
      sumName = reg
    else:
      sumName = sumName + " + " + reg
  
  regionListWithSum = list(regionList)
  if showSum:
    regionListWithSum.append(sumName)

  tablenumbers['names'] = regionListWithSum

  """
  make a list of channelCat calls for every region
  """
  regionCatList = [ 'channelCat==channelCat::' +region.Data() for region in regionFullNameList]
  
  """
  retrieve number of observed (=data) events per region
  """
  regionDatasetList = [data_set.reduce(regioncat) for regioncat in regionCatList]
  for index, data in enumerate(regionDatasetList):
    data.SetName("data_" + regionList[index])
    data.SetTitle("data_" + regionList[index])
    
  nobs_regionList = [ data.sumEntries() for data in regionDatasetList]

  """
  if showSum=True calculate the total number of observed events in all regions  
  """
  sumNobs = 0.
  for nobs in nobs_regionList:
    sumNobs += nobs
  if showSum:
    nobs_regionList.append(sumNobs)
  tablenumbers['nobs'] = nobs_regionList


  """
  FROM HERE ON OUT WE CALCULATE THE FITTED NUMBER OF EVENTS __AFTER__ THE FIT
  """

  """
  get a list of pdf's and variables per region
  """
  pdfinRegionList = [ Util.GetRegionPdf(w, region)  for region in regionList]
  varinRegionList =  [ Util.GetRegionVar(w, region) for region in regionList]
  
  """
  if splitBins=True get the list of Nbins, binMax and binMin; make a list of new region names for each bin
  """
  varNbinsInRegionList =  [] 
  varBinLowInRegionList = []  
  varBinHighInRegionList =  [] 
  rangeNameBinsInRegionList = [] 
  if splitBins:
    varNbinsInRegionList = [Util.GetRegionVar(w, region).getBinning().numBins() for region in regionList]
    varBinLowInRegionList = [[Util.GetRegionVar(w, region).getBinning((region+"binning")).binLow(ibin) for ibin in range(0, varNbinsInRegionList[idx]) ] for idx,region in enumerate(regionList)]
    varBinHighInRegionList = [[Util.GetRegionVar(w, region).getBinning((region+"binning")).binHigh(ibin) for ibin in range(0, varNbinsInRegionList[idx]) ] for idx,region in enumerate(regionList)]
    rangeNameBinsInRegionList = [[regionList[idx]+"_bin"+str(ibin) for ibin in range(0, varNbinsInRegionList[idx]) ] for idx,region in enumerate(regionList)]
    for index,region in enumerate(regionList):
      if varNbinsInRegionList[index]==1:
        print " \n YieldsTable.py: WARNING: you have called -P (= per-bin yields) but this region ", region, " has only 1 bin \n"

  

  """
  if splitBins=True reshuffle the regionName list; each region name is followed by names of each bin (i.e. regionNameList=['SR3J','SR3J_bin1','SR3j_bin2','SR4J','SR4J_bin1'])
  """
  regionListWithBins = []
  if splitBins:
    for index,region in enumerate(regionList):
      regionListWithBins.append(region)
      for ibin in range(0,varNbinsInRegionList[index]):
        regionListWithBins.append(rangeNameBinsInRegionList[index][ibin])
    tablenumbers['names'] = regionListWithBins
  

  """
  calculate number of observed(=data) events per bin
  """
  nobs_regionListWithBins = []
  if splitBins:
    binFuncInRegionList = [RooBinningCategory("bin_"+region,"bin_"+region,varinRegionList[index]) for index,region in enumerate(regionList)]
    for index, data in enumerate(regionDatasetList):
      data.addColumn(binFuncInRegionList[index])
      if not blinded:
        data.table(binFuncInRegionList[index]).Print("v")
      nobs_regionListWithBins.append(data.sumEntries())
      for ibin in range(0,varNbinsInRegionList[index]):
        nobs_regionListWithBins.append((data.reduce(binFuncInRegionList[index].GetName()+"=="+binFuncInRegionList[index].GetName()+"::"+varinRegionList[index].GetName()+"_bin"+str(ibin))).sumEntries())

    tablenumbers['nobs'] = nobs_regionListWithBins

  """
  if blinded=True, set all numbers of observed events to -1
  """
  if blinded: 
    for index, nobs in enumerate(nobs_regionListWithBins):
      nobs_regionListWithBins[index] = -1
    tablenumbers['nobs'] = nobs_regionListWithBins


  """
  get a list of RooRealSumPdf per region (RooRealSumPdf is the top-pdf per region containing all samples)
  """
  rrspdfinRegionList = []
  for index,pdf in enumerate(pdfinRegionList):
    prodList = pdf.pdfList()
    foundRRS = 0
    for idx in range(prodList.getSize()):
      if prodList[idx].InheritsFrom("RooRealSumPdf"):
        rrspdfInt =  prodList[idx].createIntegral(RooArgSet(varinRegionList[index]))
        rrspdfinRegionList.append(rrspdfInt)
        if splitBins:
          origMin = varinRegionList[index].getMin()
          origMax = varinRegionList[index].getMax()
          for ibin in range(0,varNbinsInRegionList[index]):
            rangeName = rangeNameBinsInRegionList[index][ibin]
            varinRegionList[index].setRange(rangeName,varBinLowInRegionList[index][ibin],varBinHighInRegionList[index][ibin])
            rrspdfInt =  prodList[idx].createIntegral(RooArgSet(varinRegionList[index]),rangeName)
            rrspdfinRegionList.append(rrspdfInt)
          varinRegionList[index].setRange(origMin,origMax)
        foundRRS += 1
    if foundRRS >1 or foundRRS==0:
      print " \n\n WARNING: ", pdf.GetName(), " has ", foundRRS, " instances of RooRealSumPdf"
      print pdf.GetName(), " component list:", prodList.Print("v")
    
  """
  calculate total pdf number of fitted events and error
  """
  nFittedInRegionList =  [ pdf.getVal() for index, pdf in enumerate(rrspdfinRegionList)]
  pdfFittedErrInRegionList = [ Util.GetPropagatedError(pdf, resultAfterFit, doAsym) for pdf in rrspdfinRegionList]


  """
  if showSum=True calculate the total number of fitted events in all regions  
  """
  if showSum:
    pdfInAllRegions = RooArgSet()
    for index, pdf in enumerate(rrspdfinRegionList):
      pdfInAllRegions.add(pdf)
    pdfSumInAllRegions = RooAddition( "pdf_AllRegions_AFTER", "pdf_AllRegions_AFTER", RooArgList(pdfInAllRegions))
    nPdfSumVal = pdfSumInAllRegions.getVal()
    nPdfSumError = Util.GetPropagatedError(pdfSumInAllRegions, resultAfterFit, doAsym)
    nFittedInRegionList.append(nPdfSumVal)
    pdfFittedErrInRegionList.append(nPdfSumError)
  
  tablenumbers['TOTAL_FITTED_bkg_events']    =  nFittedInRegionList
  tablenumbers['TOTAL_FITTED_bkg_events_err']    =  pdfFittedErrInRegionList
 
  """
  calculate the fitted number of events and propagated error for each requested sample, by splitting off each sample pdf
  """
  for isam, sample in enumerate(sampleList):
    sampleName=getName(sample)
    nSampleInRegionVal = []
    nSampleInRegionError = []
    sampleInAllRegions = RooArgSet()
    for ireg, region in enumerate(regionList):
      sampleInRegion=getPdfInRegions(w,sample,region)
      sampleInRegionVal = 0.
      sampleInRegionError = 0.
      if not sampleInRegion==None:
        sampleInRegionVal = sampleInRegion.getVal()
        sampleInRegionError = Util.GetPropagatedError(sampleInRegion, resultAfterFit, doAsym) 
        sampleInAllRegions.add(sampleInRegion)
      else:
        print " \n YieldsTable.py: WARNING: sample =", sampleName, " non-existent (empty) in region =",region, "\n"
      nSampleInRegionVal.append(sampleInRegionVal)
      nSampleInRegionError.append(sampleInRegionError)
      
      """
      if splitBins=True calculate numbers of fitted events plus error per bin      
      """
      if splitBins:
        origMin = varinRegionList[ireg].getMin()
        origMax = varinRegionList[ireg].getMax()
        for ibin in range(0,varNbinsInRegionList[ireg]):
          rangeName = rangeNameBinsInRegionList[ireg][ibin]
          sampleInRegion=getPdfInRegionsWithRangeName(w,sample,region,rangeName)
          sampleInRegionVal = 0.
          sampleInRegionError = 0.
          if not sampleInRegion==None:
            varinRegionList[ireg].setRange(rangeName,varBinLowInRegionList[ireg][ibin],varBinHighInRegionList[ireg][ibin])
            sampleInRegionVal = sampleInRegion.getVal()
            sampleInRegionError = Util.GetPropagatedError(sampleInRegion, resultAfterFit, doAsym)
          else:
            print " \n YieldsTable.py: WARNING: sample =", sampleName, " non-existent (empty) in region=",region, " bin=",ibin, " \n"
          nSampleInRegionVal.append(sampleInRegionVal)
          nSampleInRegionError.append(sampleInRegionError)
 
        varinRegionList[ireg].setRange(origMin,origMax)

    """
    if showSum=True calculate the total number of fitted events in all regions  
    """
    if showSum:
      sampleSumInAllRegions = RooAddition( (sampleName+"_AllRegions_FITTED"), (sampleName+"_AllRegions_FITTED"), RooArgList(sampleInAllRegions))
      nSampleSumVal = sampleSumInAllRegions.getVal()
      nSampleSumError = Util.GetPropagatedError(sampleSumInAllRegions, resultAfterFit, doAsym)
      nSampleInRegionVal.append(nSampleSumVal)
      nSampleInRegionError.append(nSampleSumError)
    tablenumbers['Fitted_events_'+sampleName]   = nSampleInRegionVal
    tablenumbers['Fitted_err_'+sampleName]   = nSampleInRegionError


  
  print "\n starting BEFORE-FIT calculations \n"
  """
  FROM HERE ON OUT WE CALCULATE THE EXPECTED NUMBER OF EVENTS __BEFORRE__ THE FIT
  """

  """
  load beforeFit workspace snapshot (=set all parameters to values before fit)
  """
  w.loadSnapshot('snapshot_paramsVals_RooExpandedFitResult_beforeFit')

  """
  check if any of the initial scaling factors is != 1
  """
  _result = w.obj('RooExpandedFitResult_beforeFit')
  _muFacs = _result.floatParsFinal()

  for i in range(len(_muFacs)):
    if "mu_" in _muFacs[i].GetName() and _muFacs[i].getVal() != 1.0:
      print  " \n WARNING: scaling factor %s != 1.0 (%g) expected MC yield WILL BE WRONG!" % (_muFacs[i].GetName(), _muFacs[i].getVal())
  
  """
  get a list of pdf's and variables per region
  """
  pdfinRegionList = [ Util.GetRegionPdf(w, region)  for region in regionList]
  varinRegionList =  [ Util.GetRegionVar(w, region) for region in regionList]

  """
  get a list of RooRealSumPdf per region (RooRealSumPdf is the top-pdf per region containing all samples)
  """
  rrspdfinRegionList = []
  for index,pdf in enumerate(pdfinRegionList):
    prodList = pdf.pdfList()
    foundRRS = 0
    for idx in range(prodList.getSize()):
      if prodList[idx].InheritsFrom("RooRealSumPdf"):
        rrspdfInt =  prodList[idx].createIntegral(RooArgSet(varinRegionList[index]))
        rrspdfinRegionList.append(rrspdfInt)
        if splitBins:
          origMin = varinRegionList[index].getMin()
          origMax = varinRegionList[index].getMax()
          for ibin in range(0,varNbinsInRegionList[index]):
            rangeName = rangeNameBinsInRegionList[index][ibin]
            varinRegionList[index].setRange(rangeName,varBinLowInRegionList[index][ibin],varBinHighInRegionList[index][ibin])
            rrspdfInt =  prodList[idx].createIntegral(RooArgSet(varinRegionList[index]),rangeName)
            rrspdfinRegionList.append(rrspdfInt)
          varinRegionList[index].setRange(origMin,origMax)
        foundRRS += 1
    if foundRRS >1 or foundRRS==0:
      print " \n\n WARNING: ", pdf.GetName(), " has ", foundRRS, " instances of RooRealSumPdf"
      print pdf.GetName(), " component list:", prodList.Print("v")

  """
  calculate total pdf number of expected events and error
  """
  nExpInRegionList =  [ pdf.getVal() for index, pdf in enumerate(rrspdfinRegionList)]
  pdfExpErrInRegionList = [ Util.GetPropagatedError(pdf, resultBeforeFit, doAsym)  for pdf in rrspdfinRegionList]
  
  """
  if showSum=True calculate the total number of expected events in all regions  
  """
  if showSum:
    pdfInAllRegions = RooArgSet()
    for index, pdf in enumerate(rrspdfinRegionList):
      pdfInAllRegions.add(pdf)
    pdfSumInAllRegions = RooAddition( "pdf_AllRegions_BEFORE", "pdf_AllRegions_BEFORE", RooArgList(pdfInAllRegions))
    nPdfSumVal = pdfSumInAllRegions.getVal()
    nPdfSumError = Util.GetPropagatedError(pdfSumInAllRegions, resultBeforeFit, doAsym)
    nExpInRegionList.append(nPdfSumVal)
    pdfExpErrInRegionList.append(nPdfSumError)
  
  tablenumbers['TOTAL_MC_EXP_BKG_events']    =  nExpInRegionList
  tablenumbers['TOTAL_MC_EXP_BKG_err']    =  pdfExpErrInRegionList
  
  """
  calculate the fitted number of events and propagated error for each requested sample, by splitting off each sample pdf
  """
  for isam, sample in enumerate(sampleList):
    sampleName=getName(sample)
    nMCSampleInRegionVal = []
    nMCSampleInRegionError = []
    MCSampleInAllRegions = RooArgSet()
    for ireg, region in enumerate(regionList):
      MCSampleInRegion = getPdfInRegions(w,sample,region)
      MCSampleInRegionVal = 0.
      MCSampleInRegionError = 0.
      if not MCSampleInRegion==None:
        MCSampleInRegionVal = MCSampleInRegion.getVal()
        MCSampleInRegionError = Util.GetPropagatedError(MCSampleInRegion, resultBeforeFit, doAsym) 
        MCSampleInAllRegions.add(MCSampleInRegion)
      else:
        print " \n WARNING: sample=", sampleName, " non-existent (empty) in region=",region
      nMCSampleInRegionVal.append(MCSampleInRegionVal)
      nMCSampleInRegionError.append(MCSampleInRegionError)

      """
      if splitBins=True calculate numbers of fitted events plus error per bin      
      """ 
      if splitBins:
        origMin = varinRegionList[ireg].getMin()
        origMax = varinRegionList[ireg].getMax()
        for ibin in range(0,varNbinsInRegionList[ireg]):
          rangeName = rangeNameBinsInRegionList[ireg][ibin]
          MCSampleInRegion=getPdfInRegionsWithRangeName(w,sample,region,rangeName)
          MCSampleInRegionVal = 0.
          MCSampleInRegionError = 0.
          if not MCSampleInRegion==None:
            varinRegionList[ireg].setRange(rangeName,varBinLowInRegionList[ireg][ibin],varBinHighInRegionList[ireg][ibin])
            MCSampleInRegionVal = MCSampleInRegion.getVal()
            MCSampleInRegionError = Util.GetPropagatedError(MCSampleInRegion, resultBeforeFit, doAsym)
          else:
            print " \n YieldsTable.py: WARNING: sample =", sampleName, " non-existent (empty) in region=",region, " bin=",ibin, " \n"
          nMCSampleInRegionVal.append(MCSampleInRegionVal)
          nMCSampleInRegionError.append(MCSampleInRegionError)
 
        varinRegionList[ireg].setRange(origMin,origMax)

    """
    if showSum=True calculate the total number of fitted events in all regions  
    """
    if showSum:
      MCSampleSumInAllRegions = RooAddition( (sampleName+"_AllRegions_MC"), (sampleName+"_AllRegions_MC"), RooArgList(MCSampleInAllRegions))
      nMCSampleSumVal = MCSampleSumInAllRegions.getVal()
      nMCSampleSumError = Util.GetPropagatedError(MCSampleSumInAllRegions, resultBeforeFit, doAsym)
      nMCSampleInRegionVal.append(nMCSampleSumVal)
      nMCSampleInRegionError.append(nMCSampleSumError)
    tablenumbers['MC_exp_events_'+sampleName] = nMCSampleInRegionVal
    tablenumbers['MC_exp_err_'+sampleName] = nMCSampleInRegionError

  """
  sort the tablenumbers set
  """
  map_listofkeys = tablenumbers.keys()
  map_listofkeys.sort()
  
  """
  print the sorted tablenumbers set
  """
  for name in map_listofkeys:
    if tablenumbers.has_key(name) :
      print name, ": ", tablenumbers[name]
      
  return tablenumbers




##################################
##################################
##################################

"""
Main function calls start here ....
"""

if __name__ == "__main__":
  
  import os, sys
  import getopt
  """
  Print out of usage, options and examples
  """
  def usage():
    print "Usage:"
    print "YieldsTable.py [-o outputFileName] [-c channels] [-w workspace_afterFit] [-s samples] [-b]\n"
    print "Minimal set of inputs [-c channels] [-w workspace_afterFit] [-s samples] "
    print "*** Options are: "
    print "-c <channels>: single channel (region) string or comma separated list accepted (OBLIGATORY)"
    print "-w <workspaceFileName>: single name accepted only (OBLIGATORY) ;   if multiple channels/regions given in -c, assumes the workspace file contains all channels/regions"
    print "-s <sample>: single unique sample name or comma separated list accepted (OBLIGATORY)"
    print "-o <outputFileName>: sets the output table file name"
    print "-B: run blinded; replace nObs(SR) by -1"
    print "-a: use Asimov dataset (off by default)"
    print "-b: shows also the error on samples Before the fit (off by default)"
    print "-S: also show the sum of all regions (off by default)"
    print "-y: take symmetrized average of minos errors"
    print "-C: full table caption"
    print "-L: full table label" 
    print "-u: arbitrary string propagated to the latex table caption"
    print "-t: arbitrary string defining the latex table name"
    print "-P: calculate yields per bin for each region"


    print "\nFor example:"
    print "YieldsTable.py -c SR7jTEl,SR7jTMu -s WZ,Top -w /afs/cern.ch/user/k/koutsman/HistFitterUser/MET_jets_leptons/results/Combined_KFactorFit_5Channel_Validation_combined_BasicMeasurement_model_afterFit.root"
    print "YieldsTable.py -c SR7jTEl,SR7jTMu -w  /afs/cern.ch/user/k/koutsman/HistFitterUser/MET_jets_leptons/results/Combined_KFactorFit_5Channel_Validation_combined_BasicMeasurement_model_afterFit.root  -o MyTableMultiJetsSR.tex"
    print "YieldsTable.py -c SR3jTEl,SR3jTMu,SR4jTEl,SR4jTMu -s WZ,Top -w /afs/cern.ch/user/c/cote/susy0/users/cote/HistFitter5/results/Combined_KFactorFit_5Channel_bkgonly_combined_BasicMeasurement_model_afterFit.root -o MyTableSR.tex"
    print "YieldsTable.py -c S2eeT,S2mmT,S2emT,S4eeT,S4mmT,S4emT -w /afs/cern.ch/user/c/cote/susy0/users/cote/HistFitter5/results/Combined_KFactorFit_5Channel_bkgonly_combined_BasicMeasurement_model_afterFit.root -o MyTableDilep.tex"
    print "YieldsTable.py -c S2eeT,S2mmT,S2emT,S4eeT,S4mmT,S4emT -w /afs/cern.ch/user/c/cote/susy0/users/cote/HistFitter5/results/Combined_KFactorFit_5Channel_bkgonly_combined_BasicMeasurement_model_afterFit.root -o MyTableDilep.tex -b"
    print "YieldsTable.py -c S2eeT,S2mmT,S2emT,S4eeT,S4mmT,S4emT -w /afs/cern.ch/user/c/cote/susy0/users/cote/HistFitter5/results/Combined_KFactorFit_5Channel_bkgonly_combined_BasicMeasurement_model_afterFit.root -o MyTableDilep.tex -b -S"
    print "YieldsTable.py -c S2eeT,S2mmT,S2emT,S4eeT,S4mmT,S4emT -w /afs/cern.ch/user/c/cote/susy0/users/cote/HistFitter5/results/Combined_KFactorFit_5Channel_bkgonly_combined_BasicMeasurement_model_afterFit.root -o MyTableDilep.tex -a"
    sys.exit(0)        

  wsFileName='/results/MyOneLeptonKtScaleFit_HardLepR17_BkgOnlyKt_combined_NormalMeasurement_model_afterFit.root'
  try:
    opts, args = getopt.getopt(sys.argv[1:], "o:c:w:s:u:L:C:t:bBSagyP")
  except:
    usage()
  if len(opts)<2:
    usage()

  """
  set some default options
  """
  outputFileName = "default"
  showBeforeFitError = False
  showSumAllRegions = False
  useAsimovSet = False
  ignoreLastChannel = False
  blinded = False
  doAsym = True
  splitBins = False
  userString = ""
  tableName = "table.results.yields"
   
  tableLabel = ""
  tableCaption = ""
  
  """
  set options as given by the user call
  """
  for opt,arg in opts:
    if opt == '-c':
      chanStr = arg.replace(",","_").replace("[","").replace("]","")
      chanList = arg.split(",")
    elif opt == '-w':
      wsFileName = arg
    elif opt == '-o':
      outputFileName = arg
    elif opt == '-s':
      sampleStr = arg.replace(",","_")
      from cmdLineUtils import cmdStringToListOfLists
      sampleList = cmdStringToListOfLists(arg)
    elif opt == '-u':
      userString = str(arg)
    elif opt == '-C':
      tableCaption = str(arg)
    elif opt == '-L':
      tableLabel = str(arg)
    elif opt == '-t':
      tableName = str(arg)
    elif opt == '-b':
      showBeforeFitError = True
    elif opt == '-B':
      blinded = True
    elif opt == '-S':
      showSumAllRegions = True
    elif opt == '-a':
      useAsimovSet = True
    elif opt == '-g':
      ignoreLastChannel = True 
    elif opt == '-y':
      doAsym = True
    elif opt == '-P':
      splitBins = True

  mentionCh = ""
  if ignoreLastChannel:
      mentionCh = chanList[-1]
      chanList = chanList[0:-1]

  if outputFileName=="default":
    outputFileName=sampleStr+"_inRegions_"+chanStr+'_YieldsTable.tex'
    pass


  """
  possible separation for LaTeX table to write one or two digits out, for now turned off
  """
  regionsList_1Digit = chanList
  regionsList_2Digits = chanList

  dataname = "obsData"
  if useAsimovSet:
    dataname = "asimovData"
    
  """
  call the function to calculate the numbers, or take numbers from pickle file  
  """
  import pickle
  if wsFileName.endswith(".pickle"):
    print "READING PICKLE FILE"
    f = open(wsFileName, 'r')
    m3 = pickle.load(f)
    f.close()
  else:
    m3 = latexfitresults(wsFileName,chanList,sampleList,dataname,showSumAllRegions,doAsym, blinded, splitBins)
    f = open(outputFileName.replace(".tex",".pickle"), 'w')
    pickle.dump(m3, f)
    f.close()



  """
  when multiple samples to be evaluated together (for example [SingleTop,ttbarV] when calling with -s 'TTbar,[SingleTop,ttbarV]')
  the names need to re-specified, as a set of samples produces only one number
  """
  sampleList_decoded = []
  for isam, sample in enumerate(sampleList):
    sampleName=getName(sample)
    sampleList_decoded.append(sampleName)

     
  """
  write out LaTeX table by calling function from YieldsTableTex.py
  """
  f = open(outputFileName, 'w')
  f.write( tablestart() )
  f.write( tablefragment(m3, tableName, regionsList_2Digits,sampleList_decoded,showBeforeFitError) )
  if tableCaption != "" or tableLabel != "":
      f.write( tableEndWithCaptionAndLabel(tableCaption, tableLabel) )
  else:
      f.write( tableend(userString,tableName) )
  f.close()
  print "\nResult written in:"
  print outputFileName

