#!/usr/bin/env python

# from sys import exit
# from ROOT import gSystem
# gSystem.Load("libCombinationTools")

from ROOT import gROOT,gSystem,gDirectory
gSystem.Load("libSusyFitter.so")
gROOT.Reset()

from ROOT import TFile, RooWorkspace, TObject, TString, RooAbsReal, RooRealVar, RooFitResult, RooDataSet, RooAddition, RooArgSet, RooFormulaVar, RooAbsData, RooRandom, RooArgList 
from ROOT import Util, TMath, TMap, RooExpandedFitResult

from cmdLineUtils import getPdfInRegions,getName

from YieldsTableTex import *
import os
import sys

# Main function calls are defined below.

def latexfitresults(filename,regionList,sampleList,exactRegionNames=False,dataname='obsData',showSum=False, doAsym=True):
  workspacename = 'w'
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

  ######

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
  pdfFittedErrInRegionList = [ Util.GetPropagatedError(pdf, resultAfterFit, doAsym) for pdf in rrspdfinRegionList]

  if showSum:
    pdfInAllRegions = RooArgSet()
    for index, pdf in enumerate(rrspdfinRegionList):
      pdfInAllRegions.add(pdf)
    pdfSumInAllRegions = RooAddition( "pdf_AllRegions_AFTER", "pdf_AllRegions_AFTER", RooArgList(pdfInAllRegions))
    pdfSumInAllRegions.Print()
    nPdfSumVal = pdfSumInAllRegions.getVal()
    nPdfSumError = Util.GetPropagatedError(pdfSumInAllRegions, resultAfterFit, doAsym)
    nFittedInRegionList.append(nPdfSumVal)
    pdfFittedErrInRegionList.append(nPdfSumError)
  
  tablenumbers['TOTAL_FITTED_bkg_events']    =  nFittedInRegionList
  tablenumbers['TOTAL_FITTED_bkg_events_err']    =  pdfFittedErrInRegionList
  
  # components
  for isam, sample in enumerate(sampleList):
    sampleName=getName(sample)
    nSampleInRegionVal = []
    nSampleInRegionError = []
    sampleInAllRegions = RooArgSet()
    for ireg, region in enumerate(regionList):
      sampleInRegion=getPdfInRegions(w,sample,region)
      #sampleInRegion = Util.GetComponent(w,sample,region,exactRegionNames)
      sampleInRegionVal = 0.
      sampleInRegionError = 0.
      if not sampleInRegion==None:
        sampleInRegion.Print()
        sampleInRegionVal = sampleInRegion.getVal()
        sampleInRegionError = Util.GetPropagatedError(sampleInRegion, resultAfterFit, doAsym) 
        sampleInAllRegions.add(sampleInRegion)
      else:
        print " \n YieldsTable.py: WARNING: sample =", sampleName, " non-existent (empty) in region =",region, "\n"
      nSampleInRegionVal.append(sampleInRegionVal)
      nSampleInRegionError.append(sampleInRegionError)
    if showSum:
      sampleSumInAllRegions = RooAddition( (sampleName+"_AllRegions_FITTED"), (sampleName+"_AllRegions_FITTED"), RooArgList(sampleInAllRegions))
      sampleSumInAllRegions.Print()
      nSampleSumVal = sampleSumInAllRegions.getVal()
      nSampleSumError = Util.GetPropagatedError(sampleSumInAllRegions, resultAfterFit, doAsym)
      nSampleInRegionVal.append(nSampleSumVal)
      nSampleInRegionError.append(nSampleSumError)
    tablenumbers['Fitted_events_'+sampleName]   = nSampleInRegionVal
    tablenumbers['Fitted_err_'+sampleName]   = nSampleInRegionError

  print tablenumbers

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
        prodList[idx].Print()
        rrspdfInt =  prodList[idx].createIntegral(RooArgSet(varinRegionList[index]))
        rrspdfinRegionList.append(rrspdfInt)
        foundRRS += 1
    if foundRRS >1 or foundRRS==0:
      print " \n\n WARNING: ", pdf.GetName(), " has ", foundRRS, " instances of RooRealSumPdf"
      print pdf.GetName(), " component list:", prodList.Print("v")

  nExpInRegionList =  [ pdf.getVal() for index, pdf in enumerate(rrspdfinRegionList)]
  pdfExpErrInRegionList = [ Util.GetPropagatedError(pdf, resultBeforeFit, doAsym)  for pdf in rrspdfinRegionList]
  
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
  
  for isam, sample in enumerate(sampleList):
    sampleName=getName(sample)
    nMCSampleInRegionVal = []
    nMCSampleInRegionError = []
    MCSampleInAllRegions = RooArgSet()
    for ireg, region in enumerate(regionList):
      MCSampleInRegion = getPdfInRegions(w,sample,region)
      #MCSampleInRegion = Util.GetComponent(w,sample,region,exactRegionNames)
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
    if showSum:
      MCSampleSumInAllRegions = RooAddition( (sampleName+"_AllRegions_MC"), (sampleName+"_AllRegions_MC"), RooArgList(MCSampleInAllRegions))
      nMCSampleSumVal = MCSampleSumInAllRegions.getVal()
      nMCSampleSumError = Util.GetPropagatedError(MCSampleSumInAllRegions, resultBeforeFit, doAsym)
      nMCSampleInRegionVal.append(nMCSampleSumVal)
      nMCSampleInRegionError.append(nMCSampleSumError)
    tablenumbers['MC_exp_events_'+sampleName] = nMCSampleInRegionVal
    tablenumbers['MC_exp_err_'+sampleName] = nMCSampleInRegionError

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
    print "-y: take symmetrized average of minos errors"
    print "-u: arbitrary string propagated to the latex table caption"
    print "-t: arbitrary string defining the latex table name"

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
    opts, args = getopt.getopt(sys.argv[1:], "o:c:w:s:u:t:bSagy")
  except:
    usage()
  if len(opts)<2:
    usage()

  outputFileName="default"
  exactRegionNames=False #if true, Util.GetComponent() calls will use exact region names, rather than string matching
  showBeforeFitError=False
  showSumAllRegions=False
  useAsimovSet=False
  ignoreLastChannel=False
  doAsym=True
  userString=""
  tableName="table.results.yields"
  for opt,arg in opts:
    if opt == '-c':
      chanStr=arg.replace(",","_").replace("[","").replace("]","")
      chanList=arg.split(",")
    elif opt == '-w':
      wsFileName=arg
    elif opt == '-o':
      outputFileName=arg
    elif opt == '-s':
      sampleStr=arg.replace(",","_")
      from cmdLineUtils import cmdStringToListOfLists
      sampleList=cmdStringToListOfLists(arg)
    elif opt == '-u':
      userString=str(arg)
    elif opt == '-t':
      tableName=str(arg)
    elif opt == '-b':
      showBeforeFitError=True
    elif opt == '-S':
      showSumAllRegions=True
    elif opt == '-a':
      useAsimovSet=True
    elif opt == '-g':
      ignoreLastChannel = True 
    elif opt == '-y':
      doAsym=True

  mentionCh = ""
  if ignoreLastChannel:
      mentionCh = chanList[-1]
      chanList = chanList[0:-1]

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
    print "READING PICKLE FILE"
    f = open(wsFileName, 'r')
    m3 = pickle.load(f)
    f.close()
  else:
    print "OPENING ROOTFIT WORKSPACE"
    m3 = latexfitresults(wsFileName,chanList,sampleList,exactRegionNames,dataname,showSumAllRegions,doAsym)
    f = open(outputFileName.replace(".tex",".pickle"), 'w')
    pickle.dump(m3, f)
    f.close()

  f = open(outputFileName, 'w')
  f.write( tablestart() )
  f.write( tablefragment(m3, '', regionsList_2Digits,sampleList,showBeforeFitError) )
  f.write( tableend(userString,tableName) )
  #f.write( tableend4(regionsList_1Digit, chanStr, mentionCh) )
  f.close()
  print "\nResult written in:"
  print outputFileName

