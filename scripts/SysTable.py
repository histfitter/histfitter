#!/usr/bin/env python
"""
 * Project : HistFitter - A ROOT-based package for statistical data analysis      *
 * Package : HistFitter                                                           *
 * Script  : SysTable.py                                                          *
 * Created : November 2012                                                        *
 *                                                                                *
 * Description:                                                                   *
 *      Script for producing publication-quality systematics breakdown tables     *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group                                                          *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
"""

from ROOT import gROOT,gSystem,gDirectory
gSystem.Load("libSusyFitter.so")
from ROOT import ConfigMgr,FitConfig #this module comes from gSystem.Load("libSusyFitter.so")
gROOT.Reset()

from ROOT import TFile, RooWorkspace, TObject, TString, RooAbsReal, RooRealVar, RooFitResult, RooDataSet, RooAddition, RooArgSet,RooAbsData,RooRandom,RooArgList 
from ROOT import Util, TMath
from ROOT import RooFit
from ROOT import RooExpandedFitResult

from cmdLineUtils import getPdfInRegions,getName

import os
import sys
from sys import exit

from SysTableTex import *
import pickle

from logger import Logger
log = Logger('SysTable')
  

def latexfitresults( filename, namemap, region='3jL', sample='', resultName="RooExpandedFitResult_afterFit", dataname='obsData', doAsym=True):
  """
  Method-1: set all parameters constant, except for the one you're interested in, 
           calculate the systematic/error propagated due to that parameter

  @param filename The filename containing afterFit workspace
  @param namemap Defines whether any systematics need to be grouped in calculation (by default not defined, hence each parameter gets used one by one)
  @param resultname The name of fit result (typically='RooExpandedFitResult_afterFit' or 'RooExpandedFitResult_beforeFit'
  @param region The region to be used for systematics breakdown calculation
  @param sample The sample to be used insted of total pdf (default='' not defined, hence total pdf used)
  @param dataname The name of dataset (default='obsData')
  @param doAsym Calculates asymmetric errors taken from MINOS (default=True)
"""

  """
  pick up workspace from file
  """
  workspacename = 'w'
  w = Util.GetWorkspaceFromFile(filename,workspacename)
  if w==None:
    print "ERROR : Cannot open workspace : ", workspacename
    sys.exit(1) 

  """
  pick up RooExpandedFitResult from workspace with name resultName (either before or after fit)
  """
  result = w.obj(resultName)
  if result==None:
    print "ERROR : Cannot open fit result ", resultName
    sys.exit(1)

  """
  load workspace snapshot related to resultName (=set all parameters to values after fit)
  """
  snapshot =  'snapshot_paramsVals_' + resultName
  w.loadSnapshot(snapshot)

  """
  pick up dataset from workspace
  """
  data_set = w.data(dataname)
  if data_set==None:
    print "ERROR : Cannot open dataset : ", "data_set"
    sys.exit(1)
      
  """
  pick up channel category (RooCategory) from workspace
  """
  regionCat = w.obj("channelCat")
  data_set.table(regionCat).Print("v");

  """
  find full (long) name list of region (i.e. short=SR3J, long=SR3J_meffInc30_JVF25pt50)
  """
  regionFullName = Util.GetFullRegionName(regionCat, region);

  """
  set a boolean whether we're looking at a sample or the full (multi-sample) pdf/model
  """
  chosenSample = False
  if sample is not '':
    chosenSample = True
        
  """
  define regSys set, for all names/numbers to be saved in
  """
  regSys = {}

  """
  define channelCat call for this region and reduce the dataset to this category/region
  """
  regionCatStr = 'channelCat==channelCat::' + regionFullName.Data()
  dataRegion = data_set.reduce(regionCatStr)
  
  """
  retrieve and save number of observed (=data) events in region
  """
  nobsRegion = 0.
  if dataRegion:
    nobsRegion = dataRegion.sumEntries()
  else:
    print " ERROR : dataset-category dataRegion not found"
    
  """
  if looking at a sample, there is no equivalent N_obs (only for the full model)
  """
  if chosenSample:
    regSys['sqrtnobsa'] = 0.
  else:
    regSys['sqrtnobsa'] = TMath.Sqrt(nobsRegion)


  """
  get the pdf for the total model or just for the sample in region
  """
  if chosenSample:
    pdfInRegion=getPdfInRegions(w,sample,region)
  else:
    rawPdfInRegion = Util.GetRegionPdf(w, region)
    varInRegion =  Util.GetRegionVar(w, region)
    prodList = rawPdfInRegion.pdfList()
    foundRRS = 0
    for idx in range(prodList.getSize()):
      if prodList[idx].InheritsFrom("RooRealSumPdf"):
        rrspdfInt =  prodList[idx].createIntegral(RooArgSet(varInRegion));
        pdfInRegion = rrspdfInt
        foundRRS += 1
    if foundRRS >1 or foundRRS==0:
      print " \n\n WARNING: ", pdf.GetName(), " has ", foundRRS, " instances of RooRealSumPdf"
      print pdf.GetName(), " component list:", prodList.Print("v")

  if not pdfInRegion:
    if chosenSample:
      print " \n Warning, could not find pdf in region = ",region, " for sample = ",sample
    else:
      print " \n Warning, could not find pdf in region = ",region

  """
  calculate fitted pdf number of events and full error
  """
  nFittedInRegion=pdfInRegion.getVal()
  regSys['sqrtnfitted'] = TMath.Sqrt(nFittedInRegion)
  regSys['nfitted'] = nFittedInRegion

  pdfFittedErrInRegion = Util.GetPropagatedError(pdfInRegion, result, doAsym) 
  regSys['totsyserr'] = pdfFittedErrInRegion


  """
  calculate error per (floating) parameter in fitresult
  get a list of floating parameters to loop over
  """
  fpf = result.floatParsFinal() 
  
  """
  set all floating parameters constant
  """
  for idx in range(fpf.getSize()):
    parname = fpf[idx].GetName()
    par = w.var(parname)
    par.setConstant()

  """
  if several systematatic/parameters are pre-defined in namemap, they will be floated together
  or in other words, one will get the error due to all pre-defined systematics
  """
  """
  else, float each parameter one by one and calculate the error due to it
  """
  if len(namemap)>0: 
    for key in namemap.keys():
      print namemap[key]
      for parname in namemap[key]:
        par = w.var(parname)
        par.setConstant(False)
        pass
      sysError  = Util.GetPropagatedError(pdfInRegion, result, doAsym)
      regSys['syserr_'+key] =  sysError
      for idx in range(fpf.getSize()):
        parname = fpf[idx].GetName()
        par = w.var(parname)
        par.setConstant()
        pass
  else: 
    for idx in range(fpf.getSize()):
      parname = fpf[idx].GetName()
      par = w.var(parname)
      par.setConstant(False)
      sysError  = Util.GetPropagatedError(pdfInRegion, result, doAsym)
      regSys['syserr_'+parname] =  sysError
      par.setConstant() 

  return regSys




def latexfitresults_method2(filename,resultname='RooExpandedFitResult_afterFit', region='3jL', sample='', fitregions = 'WR,TR,S3,S4,SR3jT,SR4jT', dataname='obsData', doAsym=False):
  """
  Method-2: set the parameter you're interested in constant,
  redo the fit with all other parameters floating,
  calculate the quadratic difference between default fit and your new model with parameter fixed

  @param filename The filename containing afterFit workspace
  @param resultname The name of fit result (typically='RooExpandedFitResult_afterFit' or 'RooExpandedFitResult_beforeFit'
  @param region The region to be used for systematics breakdown calculation
  @param sample The sample to be used insted of total pdf (default='' not defined, hence total pdf used)
  @param fitregions Fit regions to perform the re-fit (default= 'WR,TR,S3,S4,SR3jT,SR4jT' but needs to be specified by user)
  @param dataname The name of dataset (default='obsData')
  @param doAsym Calculates asymmetric errors taken from MINOS (default=False) 
  """

  """
  pick up workspace from file
  """
  w = Util.GetWorkspaceFromFile(filename,'w')
  if w==None:
    print "ERROR : Cannot open workspace : "
    sys.exit(1) 

  """
  pick up RooExpandedFitResult from workspace with name resultName (either before or after fit)
  """
  result = w.obj(resultname)
  if result==None:
    print "ERROR : Cannot open fit result : ", resultname
    sys.exit(1)

  """
  save the original (after-fit result) fit parameters list
  """
  resultlistOrig = result.floatParsFinal()
    
  """
  load workspace snapshot related to resultName (=set all parameters to values after fit)
  """
  snapshot =  'snapshot_paramsVals_' + resultname
  w.loadSnapshot(snapshot)

  """
  pick up dataset from workspace
  """
  data_set = w.data(dataname)
  if data_set==None:
    print "ERROR : Cannot open dataset : ", "data_set"
    sys.exit(1)
      
  """
  pick up channel category (RooCategory) from workspace
  """
  regionCat = w.obj("channelCat")
  data_set.table(regionCat).Print("v");

  """
  find full (long) name list of region (i.e. short=SR3J, long=SR3J_meffInc30_JVF25pt50)
  """
  regionFullName = Util.GetFullRegionName(regionCat, region)

  """
  find and save the list of all regions used for the fit, as the fit will be redone
  """
  fitRegionsList = fitregions.split(",")
  fitRegionsFullName = ""
  for reg in fitRegionsList:
    regFullName = Util.GetFullRegionName(regionCat, reg)
    if fitRegionsFullName == "":
      fitRegionsFullName = regFullName.Data()
    else:
      fitRegionsFullName = fitRegionsFullName + "," + regFullName.Data()

  """
  set a boolean whether we're looking at a sample or the full (multi-sample) pdf/model
  """
  chosenSample = False
  if sample is not '':
    chosenSample = True


  """
  define regSys set, for all names/numbers to be saved in
  """
  regSys = {}

  """
  define channelCat call for this region and reduce the dataset to this category/region
  """
  regionCatStr = 'channelCat==channelCat::' + regionFullName.Data()
  dataRegion = data_set.reduce(regionCatStr)
  nobsRegion = 0.
  
  if dataRegion:
    nobsRegion = dataRegion.sumEntries()
  else:
    print " ERROR : dataset-category", regionCatStr, " not found"
    
  """
  if looking at a sample, there is no equivalent N_obs (only for the full model)
  """
  if chosenSample:
    regSys['sqrtnobsa'] = 0.
  else:
    regSys['sqrtnobsa'] = TMath.Sqrt(nobsRegion)


  """
  get the pdf for the total model or just for the sample in region
  """
  if chosenSample:
    pdfInRegion  = Util.GetComponent(w,sample,region)
  else:
    rawPdfInRegion = Util.GetRegionPdf(w, region)
    varInRegion =  Util.GetRegionVar(w, region)
    prodList = rawPdfInRegion.pdfList()
    foundRRS = 0
    for idx in range(prodList.getSize()):
      if prodList[idx].InheritsFrom("RooRealSumPdf"):
        rrspdfInt =  prodList[idx].createIntegral(RooArgSet(varInRegion));
        pdfInRegion = rrspdfInt
        foundRRS += 1
    if foundRRS >1 or foundRRS==0:
      print " \n\n WARNING: ", pdf.GetName(), " has ", foundRRS, " instances of RooRealSumPdf"
      print pdf.GetName(), " component list:", prodList.Print("v")
    
  if not pdfInRegion:
    if chosenSample:
      print " \n Warning, could not find pdf in region = ",region, " for sample = ",sample
    else:
      print " \n Warning, could not find pdf in region = ",region

  """
  calculate fitted pdf number of events and full error
  """
  nFittedInRegion = pdfInRegion.getVal()
  regSys['sqrtnfitted'] = TMath.Sqrt(nFittedInRegion)
  regSys['nfitted'] = nFittedInRegion

  pdfFittedErrInRegion = Util.GetPropagatedError(pdfInRegion, result, doAsym) 
  regSys['totsyserr'] = pdfFittedErrInRegion
  
  """
  set lumi parameter constant for the refit -- FIXME
  """
  lumiConst = True
  
  fpf = result.floatParsFinal()

  """
  redo the fit for every parameter being fixed
  """
  for idx in range(fpf.getSize()):
    parname = fpf[idx].GetName()
    print "\n Method-2: redoing fit with fixed parameter ", parname

    """
    the parameter that is fixed, needs to have the value of the default fit
    """
    w.loadSnapshot(snapshot)
    par = w.var(parname)
    par.setConstant(True)

    """
    perform the fit again with one parameter fixed
    """
    suffix = parname + "Fixed"
    result_1parfixed = Util.FitPdf(w, fitRegionsFullName, lumiConst, data_set, suffix, doAsym, "all")

    """
    create a new RooExpandedFitResult based on the new fit
     and all parameters saved in the original fit result (as some parameters might only be floating in VRs)
    """
    expResultAfter_1parfixed = RooExpandedFitResult(result_1parfixed, resultlistOrig)

    """
    calculate newly fitted number of events and full error
    """
    nFittedInRegion_1parfixed = pdfInRegion.getVal()
    pdfFittedErrInRegion_1parfixed = Util.GetPropagatedError(pdfInRegion, expResultAfter_1parfixed, doAsym) #  result_1parfixed)

    """
    check whether original total error is smaller then newly-fitted total error
      if one does anew fit with less floating parameters (systematics), it can be expected to see smaller error
      (this assumption does not take correlations into account)
    """
    if pdfFittedErrInRegion_1parfixed > pdfFittedErrInRegion:
      print "\n\n  WARNING  parameter ", parname," gives a larger error when set constant. Do you expect this?"
      print "  WARNING          pdfFittedErrInRegion = ", pdfFittedErrInRegion, "    pdfFittedErrInRegion_1parfixed = ", pdfFittedErrInRegion_1parfixed

    """
    calculate systematic error as the quadratic difference between original and re-fitted errors
    """
    systError  =  TMath.Sqrt(abs(pdfFittedErrInRegion*pdfFittedErrInRegion - pdfFittedErrInRegion_1parfixed*pdfFittedErrInRegion_1parfixed))
    par.setConstant(False)

    """
    print a warning if new fit with 1 par fixed did not converge - meaning that sys error cannot be trusted 
    """
    if result_1parfixed.status()==0 and result_1parfixed.covQual()==3:   #and result_1parfixed.numStatusHistory()==2 and  result_1parfixed.statusCodeHistory(0)==0 and  result_1parfixed.statusCodeHistory(1) ==0:
      systError = systError
    else:
      systError = 0.0
      print "        WARNING :   for parameter ",parname," fixed the fit does not converge, as status=",result_1parfixed.status(), "(converged=0),  and covariance matrix quality=", result_1parfixed.covQual(), " (full accurate==3)"
      print "        WARNING: setting systError = 0 for parameter ",parname

    regSys['syserr_'+parname] =  systError

  return regSys

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
    print "SysTable.py [-c channels] [-w workspace_afterFit] [-o outputFileName] [-o outputFileName] [-s sample] [-m method] [-f fitregions] [-%] [-b] <python/MySystTableConfig.py> \n"
    print "Minimal set of inputs [-c channels] [-w workspace_afterFit]"
    print "*** Options are: "
    print "-c <channels>: single channel (region) string or comma separated list accepted (OBLIGATORY)"
    print "-w <workspaceFileName>: single name accepted only (OBLIGATORY) ;   if multiple channels/regions given in -c, assumes the workspace file contains all channels/regions"
    print "-s <sample>: single unique sample name or comma separated list accepted (sample systematics will be calculated for every region given)"
    print "-m <method>: switch between method 1 (extrapolation) and method 2 (refitting with 1 parameter constant)"
    print "-o <outputFileName>: sets the output table file name, name defined by regions if none provided"
    print "-b: shows the error on samples Before the fit (by default After fit is shown)"
    print "-%: also show the individual errors as percentage of the total systematic error (off by default)"
    print "-y: take symmetrized average of minos errors"

    print "\nFor example:"
    print "SysTable.py -w MyName_combined_BasicMeasurement_model_afterFit.root  -c SR7jTEl_meffInc,SR7jTMu_meffInc -o SystematicsMultiJetsSR.tex"    
    print "SysTable.py -w MyName_combined_BasicMeasurement_model_afterFit.root  -c SR7jTEl,SR7jTMu -s Top,WZ"
    print "SysTable.py -c SR3Lhigh_disc_cuts -s '[topZ,topW,ttbarHiggs,singleTopZ],[diBosonWZ,diBosonPowhegZZ,triBoson],fakes' -w MyName_combined_NormalMeasurement_model_afterFit.root -o MySystTable.tex python/MySystTableConfig.py"
    sys.exit(0)        

  wsFileName=''
  try:
    opts, args = getopt.getopt(sys.argv[1:], "o:c:w:m:f:s:%by")
  except:
    usage()
  if len(opts)<2:
    usage()

  """
  set some default options
  """
  outputFileName="default"
  method="1"
  showAfterFitError=True
  showPercent=False
  doAsym=True
  sampleStr=''
  chosenSample = False

  """
  set options as given by the user call
  """
  for opt,arg in opts:
    if opt == '-c':
      chanStr=arg.replace(",","_")
      chanList=arg.split(",")
    elif opt == '-w':
      wsFileName=arg
    elif opt == '-o':
      outputFileName=arg
    elif opt == '-m':
      if arg == "2" or arg == "1":
        method = arg
      else:
        print "Warning, only methods 1 or 2 are possible. You set method (-m) = ", arg
        sys.exit(0)
    elif opt == '-f':
      fitRegionsStr=arg
      fitRegionsList=arg.split(",")
    elif opt == '-s':
      sampleStr=arg.replace(",","_") + "_"
      from cmdLineUtils import cmdStringToListOfLists
      sampleList=cmdStringToListOfLists(arg)
      chosenSample=True
    elif opt == '-b':
      showAfterFitError=False
    elif opt == '-%':
      showPercent=True
    elif opt == '-y':
      doAsym=True
     
  if outputFileName=="default":
    outputFileName=sampleStr+chanStr+'_SysTable.tex'
    pass

  try:
    fitRegionsList
    if fitRegionsList and not method=="2":
      print "Warning, you set fitRegions (-f) = ", fitRegionsStr, " but not method 2 (-m 2). Fitregions can only be set together with method 2"
      sys.exit(0)
  except NameError:
    pass

  if method=="2":
    try:
      fitRegionsList
    except NameError:
      print "Warning, you did not set fitRegions (-f), but set method 2 (-m 2). Fitregions must be specified when running method 2"
      sys.exit(0)

  for xtraFile in args:
    execfile(xtraFile)

  if not vars().has_key("namemap"):
    namemap={}
 
  resultName = 'RooExpandedFitResult_afterFit'
  if not showAfterFitError:
    resultName =  'RooExpandedFitResult_beforeFit'

  skiplist = ['sqrtnobsa', 'totbkgsysa', 'poisqcderr','sqrtnfitted','totsyserr','nfitted']

  chanSys = {}
  origChanList = list(chanList)
  chanList = []
  """
  calculate the systematics breakdown for each channel/region given in chanList
   choose whether to use method-1 or method-2
   choose whether calculate systematic for full model or just a sample chosen by user
  """
  for chan in origChanList:

    if not chosenSample:
      if method == "2":
        regSys = latexfitresults_method2(wsFileName,resultName,chan,'',fitRegionsStr,'obsData',doAsym) 
      else:
        regSys = latexfitresults(wsFileName,namemap,chan,'',resultName,'obsData',doAsym)
      chanSys[chan] = regSys
      chanList.append(chan)
    else:
      for sample in sampleList:
        sampleName=getName(sample)
        if method == "2":
          regSys = latexfitresults_method2(wsFileName,resultName,chan,sample,fitRegionsStr,'obsData',doAsym) 
        else:
          regSys = latexfitresults(wsFileName,namemap,chan,sample,resultName,'obsData',doAsym) 
        chanSys[chan+"_"+sampleName] = regSys
        chanList.append(chan+"_"+sampleName)
        pass
      pass

  """
  write out LaTeX table by calling function from SysTableTex.py function tablefragment
  """
  line_chanSysTight = tablefragment(chanSys,chanList,skiplist,chanStr,showPercent)
  
  f = open(outputFileName, 'w')
  f.write( line_chanSysTight )
  f.close()
  print "\nwrote results in file: %s"%(outputFileName)

