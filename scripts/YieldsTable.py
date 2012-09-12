#!/usr/bin/env python
#from sys import exit
#from ROOT import gSystem
#gSystem.Load("libCombinationTools")

from ROOT import gROOT,gSystem,gDirectory
gSystem.Load("libSusyFitter.so")
gROOT.Reset()

from ROOT import TFile, RooWorkspace, TObject, TString, RooAbsReal, RooRealVar, RooFitResult, RooDataSet, RooAddition, RooArgSet, RooFormulaVar, RooAbsData, RooRandom 
from ROOT import Util, TMath, TMap, RooExpandedFitResult

from YieldsTableTex import *
import os
import sys

# Main function calls are defined below.

def latexfitresults(filename,regionList,sampleList,dataname='obsData',showSum=False):

  w = Util.GetWorkspaceFromFile(filename,'w')

  if w==None:
    print "ERROR : Cannot open workspace : ", workspacename
    sys.exit(1) 

  resultAfterFit = w.obj('RooExpandedFitResult_afterFit')
  if resultAfterFit==None:
    print "ERROR : Cannot open fit result after fit RooExpandedFitResult_afterFit"
    sys.exit(1)

  resultBeforeFit = w.obj('RooExpandedFitResult_beforeFit')
  if resultBeforeFit==None:
    print "ERROR : Cannot open fit result before fit RooExpandedFitResult_beforeFit"
    sys.exit(1)

  data_set = w.data(dataname)
  if data_set==None:
    print "ERROR : Cannot open dataset : ", "data_set"+suffix
    sys.exit(1)
      
  regionCat = w.obj("channelCat")
  data_set.table(regionCat).Print("v");

  regionFullNameList = [ Util.GetFullRegionName(regionCat, region) for region in regionList]
  print regionFullNameList

  ###

  snapshot =  'snapshot_paramsVals_RooExpandedFitResult_afterFit'
  w.loadSnapshot(snapshot)

  if not w.loadSnapshot(snapshot):
    print "ERROR : Cannot load snapshot : ", snapshot
    sys.exit(1)

  tablenumbers = {}

  # SUM ALL REGIONS
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

  regionCatList = [ 'channelCat==channelCat::' +region.Data() for region in regionFullNameList]
  
  regionDatasetList = [data_set.reduce(regioncat) for regioncat in regionCatList]
  for index, data in enumerate(regionDatasetList):
    data.SetName("data_" + regionList[index])
    data.SetTitle("data_" + regionList[index])
    
  nobs_regionList = [ data.sumEntries() for data in regionDatasetList]
  #SUM
  sumNobs = 0.
  for nobs in nobs_regionList:
    sumNobs += nobs
    ## print " \n XXX nobs = ", nobs, "    sumNobs = ", sumNobs
  if showSum:
    nobs_regionList.append(sumNobs)
  tablenumbers['nobs'] = nobs_regionList
 
  ######
  ######
  ######  FROM HERE ON OUT WE CALCULATE THE FITTED NUMBER OF EVENTS __AFTER__ THE FIT
  ######
  ######

  # total pdf, not splitting in components
  pdfinRegionList = [ Util.GetRegionPdf(w, region)  for region in regionList]
  varinRegionList =  [ Util.GetRegionVar(w, region) for region in regionList]
  rrspdfinRegionList = []
  for index,pdf in enumerate(pdfinRegionList):
#    pdf.Print("t")
    prodList = pdf.pdfList()
    foundRRS = 0
    for idx in range(prodList.getSize()):
      #      if "BG" in prodList[idx].GetName():
      #        prodList[idx].Print("t")
      if prodList[idx].InheritsFrom("RooRealSumPdf"):
        rrspdfInt =  prodList[idx].createIntegral(RooArgSet(varinRegionList[index]));
        rrspdfinRegionList.append(rrspdfInt)
        foundRRS += 1
    if foundRRS >1 or foundRRS==0:
      print " \n\n WARNING: ", pdf.GetName(), " has ", foundRRS, " instances of RooRealSumPdf"
      print pdf.GetName(), " component list:", prodList.Print("v")
    
  nFittedInRegionList =  [ pdf.getVal() for index, pdf in enumerate(rrspdfinRegionList)]
  pdfFittedErrInRegionList = [ Util.GetPropagatedError(pdf, resultAfterFit) for pdf in rrspdfinRegionList]

  if showSum:
    pdfInAllRegions = RooArgSet()
    for index, pdf in enumerate(rrspdfinRegionList):
      pdfInAllRegions.add(pdf)
    pdfSumInAllRegions = RooAddition( "pdf_AllRegions_AFTER", "pdf_AllRegions_AFTER", pdfInAllRegions)
    pdfSumInAllRegions.Print()
    nPdfSumVal = pdfSumInAllRegions.getVal()
    nPdfSumError = Util.GetPropagatedError(pdfSumInAllRegions, resultAfterFit)
    nFittedInRegionList.append(nPdfSumVal)
    pdfFittedErrInRegionList.append(nPdfSumError)
  
  tablenumbers['TOTAL_FITTED_bkg_events']    =  nFittedInRegionList
  tablenumbers['TOTAL_FITTED_bkg_events_err']    =  pdfFittedErrInRegionList
  
  # components
  for isam, sample in enumerate(sampleList):
    nSampleInRegionVal = []
    nSampleInRegionError = []
    sampleInAllRegions = RooArgSet()
    for ireg, region in enumerate(regionList):
      sampleInRegion = Util.GetComponent(w,sample,region)
      sampleInRegionVal = 0.
      sampleInRegionError = 0.
      if not sampleInRegion==None:
        sampleInRegion.Print()
        sampleInRegionVal = sampleInRegion.getVal()
        sampleInRegionError = Util.GetPropagatedError(sampleInRegion, resultAfterFit) 
        sampleInAllRegions.add(sampleInRegion)
      else:
        print " \n YieldsTable.py: WARNING: sample =", sample, " non-existent (empty) in region =",region, "\n"
      nSampleInRegionVal.append(sampleInRegionVal)
      nSampleInRegionError.append(sampleInRegionError)
    # print " \n\n  XXX-AFTER sample = ", sample
    if showSum:
      sampleSumInAllRegions = RooAddition( (sample+"_AllRegions_FITTED"), (sample+"_AllRegions_FITTED"), sampleInAllRegions)
      sampleSumInAllRegions.Print()
      nSampleSumVal = sampleSumInAllRegions.getVal()
      nSampleSumError = Util.GetPropagatedError(sampleSumInAllRegions, resultAfterFit)
      nSampleInRegionVal.append(nSampleSumVal)
      nSampleInRegionError.append(nSampleSumError)
    tablenumbers['Fitted_events_'+sample]   = nSampleInRegionVal
    tablenumbers['Fitted_err_'+sample]   = nSampleInRegionError


  ######
  ######
  ######  FROM HERE ON OUT WE CALCULATE THE EXPECTED NUMBER OF EVENTS __BEFORE__ THE FIT
  ######
  ######

  #  FROM HERE ON OUT WE CALCULATE THE EXPECTED NUMBER OF EVENTS BEFORE THE FIT
  w.loadSnapshot('snapshot_paramsVals_RooExpandedFitResult_beforeFit')
  
  pdfinRegionList = [ Util.GetRegionPdf(w, region)  for region in regionList]
  varinRegionList =  [ Util.GetRegionVar(w, region) for region in regionList]
  rrspdfinRegionList = []
  for index,pdf in enumerate(pdfinRegionList):
    prodList = pdf.pdfList()
    foundRRS = 0
    for idx in range(prodList.getSize()):
      if prodList[idx].InheritsFrom("RooRealSumPdf"):
        #      print " \n\n  XXX-BEFORE  prodList[idx] = ", prodList[idx].GetName()
        prodList[idx].Print()
        rrspdfInt =  prodList[idx].createIntegral(RooArgSet(varinRegionList[index]))
        rrspdfinRegionList.append(rrspdfInt)
        foundRRS += 1
    if foundRRS >1 or foundRRS==0:
      print " \n\n WARNING: ", pdf.GetName(), " has ", foundRRS, " instances of RooRealSumPdf"
      print pdf.GetName(), " component list:", prodList.Print("v")

  nExpInRegionList =  [ pdf.getVal() for index, pdf in enumerate(rrspdfinRegionList)]
  pdfExpErrInRegionList = [ Util.GetPropagatedError(pdf, resultBeforeFit)  for pdf in rrspdfinRegionList]
  
  if showSum:
    pdfInAllRegions = RooArgSet()
    for index, pdf in enumerate(rrspdfinRegionList):
      pdfInAllRegions.add(pdf)
    pdfSumInAllRegions = RooAddition( "pdf_AllRegions_BEFORE", "pdf_AllRegions_BEFORE", pdfInAllRegions)
    nPdfSumVal = pdfSumInAllRegions.getVal()
    nPdfSumError = Util.GetPropagatedError(pdfSumInAllRegions, resultAfterFit)
    nExpInRegionList.append(nPdfSumVal)
    pdfExpErrInRegionList.append(nPdfSumError)
  
  tablenumbers['TOTAL_MC_EXP_BKG_events']    =  nExpInRegionList
  tablenumbers['TOTAL_MC_EXP_BKG_err']    =  pdfExpErrInRegionList
  
  for isam, sample in enumerate(sampleList):
    nMCSampleInRegionVal = []
    nMCSampleInRegionError = []
    sampleInAllRegions = RooArgSet()
    for ireg, region in enumerate(regionList):
      MCSampleInRegion = Util.GetComponent(w,sample,region)
      MCSampleInRegionVal = 0.
      MCSampleInRegionError = 0.
      if not MCSampleInRegion==None:
        MCSampleInRegionVal = MCSampleInRegion.getVal()
        MCSampleInRegionError = Util.GetPropagatedError(MCSampleInRegion, resultBeforeFit) 
        sampleInAllRegions.add(sampleInRegion)
      else:
        print " \n WARNING: sample=", sample, " non-existent (empty) in region=",region
      nMCSampleInRegionVal.append(MCSampleInRegionVal)
      nMCSampleInRegionError.append(MCSampleInRegionError)
    #print " \n\n  XXX-BEFORE  sample = ", sample
    if showSum:
      sampleSumInAllRegions = RooAddition( (sample+"_AllRegions_MC"), (sample+"_AllRegions_MC"), sampleInAllRegions)
      nSampleSumVal = sampleSumInAllRegions.getVal()
      nSampleSumError = Util.GetPropagatedError(sampleSumInAllRegions, resultBeforeFit)
      nMCSampleInRegionVal.append(nSampleSumVal)
      nMCSampleInRegionError.append(nSampleSumError)
    tablenumbers['MC_exp_events_'+sample]   = nMCSampleInRegionVal
    tablenumbers['MC_exp_err_'+sample]   = nMCSampleInRegionError

    #  sorted(tablenumbers, key=lambda sample: sample[1])   # sort by age
  map_listofkeys = tablenumbers.keys()
  map_listofkeys.sort()
  
  for name in map_listofkeys:
    if tablenumbers.has_key(name) :
      print name, ": ", tablenumbers[name]
      
  ###
  return tablenumbers




##################################
##################################
##################################

#### Main function calls start here ....

if __name__ == "__main__":
  
  import os, sys
  import getopt
  def usage():
    print "Usage:"
    print "YieldsTable.py [-o outputFileName] [-c channels] [-w workspace_afterFit] [-s samples] [-b]\n"
    print "Minimal set of inputs [-c channels] [-w workspace_afterFit] [-s samples] "
    print "*** Options are: "
    print "-c <channels>: single channel (region) string or comma separated list accepted (OBLIGATORY)"
    print "-w <workspaceFileName>: single name accepted only (OBLIGATORY) ;   if multiple channels/regions given in -c, assumes the workspace file contains all channels/regions"
    print "-s <sample>: single unique sample name or comma separated list accepted (OBLIGATORY)"
    print "-o <outputFileName>: sets the output table file name"
    print "-a: use Asimov dataset (off by default)"
    print "-b: shows also the error on samples Before the fit (off by default)"
    print "-S: also show the sum of all regions (off by default)"

    print "\nFor example:"
    print "./YieldsTable.py -c SR7jTEl,SR7jTMu -s WZ,Top -w /afs/cern.ch/user/k/koutsman/HistFitterUser/MET_jets_leptons/results/Combined_KFactorFit_5Channel_Validation_combined_BasicMeasurement_model_afterFit.root"
    print "./YieldsTable.py -c SR7jTEl,SR7jTMu -w  /afs/cern.ch/user/k/koutsman/HistFitterUser/MET_jets_leptons/results/Combined_KFactorFit_5Channel_Validation_combined_BasicMeasurement_model_afterFit.root  -o MyTableMultiJetsSR.tex"
    print "./YieldsTable.py -c SR3jTEl,SR3jTMu,SR4jTEl,SR4jTMu -s WZ,Top -w /afs/cern.ch/user/c/cote/susy0/users/cote/HistFitter5/results/Combined_KFactorFit_5Channel_bkgonly_combined_BasicMeasurement_model_afterFit.root -o MyTableSR.tex"
    print "./YieldsTable.py -c S2eeT,S2mmT,S2emT,S4eeT,S4mmT,S4emT -w /afs/cern.ch/user/c/cote/susy0/users/cote/HistFitter5/results/Combined_KFactorFit_5Channel_bkgonly_combined_BasicMeasurement_model_afterFit.root -o MyTableDilep.tex"
    print "./YieldsTable.py -c S2eeT,S2mmT,S2emT,S4eeT,S4mmT,S4emT -w /afs/cern.ch/user/c/cote/susy0/users/cote/HistFitter5/results/Combined_KFactorFit_5Channel_bkgonly_combined_BasicMeasurement_model_afterFit.root -o MyTableDilep.tex -b"
    print "./YieldsTable.py -c S2eeT,S2mmT,S2emT,S4eeT,S4mmT,S4emT -w /afs/cern.ch/user/c/cote/susy0/users/cote/HistFitter5/results/Combined_KFactorFit_5Channel_bkgonly_combined_BasicMeasurement_model_afterFit.root -o MyTableDilep.tex -b -S"
    print "./YieldsTable.py -c S2eeT,S2mmT,S2emT,S4eeT,S4mmT,S4emT -w /afs/cern.ch/user/c/cote/susy0/users/cote/HistFitter5/results/Combined_KFactorFit_5Channel_bkgonly_combined_BasicMeasurement_model_afterFit.root -o MyTableDilep.tex -a"
    sys.exit(0)        

  wsFileName='/results/MyOneLeptonKtScaleFit_HardLepR17_BkgOnlyKt_combined_NormalMeasurement_model_afterFit.root'
  try:
    opts, args = getopt.getopt(sys.argv[1:], "o:c:w:s:bSa")
  except:
    usage()
  if len(opts)<2:
    usage()

  outputFileName="default"
  showBeforeFitError=False
  showSumAllRegions=False
  useAsimovSet=False
  for opt,arg in opts:
    if opt == '-c':
      chanStr=arg.replace(",","_")
      chanList=arg.split(",")
    elif opt == '-w':
      wsFileName=arg
    elif opt == '-o':
      outputFileName=arg
    elif opt == '-s':
      sampleStr=arg.replace(",","_")
      sampleList=arg.split(",")
    elif opt == '-b':
      showBeforeFitError=True
    elif opt == '-S':
      showSumAllRegions=True
    elif opt == '-a':
      useAsimovSet=True

      
  if outputFileName=="default":
    outputFileName=sampleStr+"_inRegions_"+chanStr+'_YieldsTable.tex'
    pass

  regionsList_1Digit = chanList
  regionsList_2Digits = chanList

  dataname = "obsData"
  if useAsimovSet:
    dataname = "asimovData"

  import pickle
  if wsFileName.endswith(".pickle"):
    f = open(wsFileName, 'r')
    m3 = pickle.load(f)
    f.close()
  else:
    m3 = latexfitresults(wsFileName,chanList,sampleList,dataname,showSumAllRegions)
    f = open(outputFileName.replace(".tex",".pickle"), 'w')
    pickle.dump(m3, f)
    f.close()

  f = open(outputFileName, 'w')
  f.write( tablestart() )
  f.write( tablefragment(m3, '', regionsList_2Digits,sampleList,showBeforeFitError) )
  f.write( tableend4(regionsList_1Digit, chanStr) )
  f.close()
  print "\nResult written in:"
  print outputFileName
