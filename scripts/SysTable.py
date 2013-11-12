#!/usr/bin/env python
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
#log.setLevel('DEBUG')
  

def latexfitresults( filename, namemap, region='3jL', sample='', resultName="RooExpandedFitResult_afterFit", dataname='obsData', doAsym=True):
  #Method-1: set all parameters constant, except for the one you're interested in, 
  #          calculate the error propagated due to that parameter

  workspacename = 'w'
  w = Util.GetWorkspaceFromFile(filename,workspacename)

  if w==None:
    print "ERROR : Cannot open workspace : ", workspacename
    sys.exit(1) 

  result = w.obj(resultName)
  if result==None:
    print "ERROR : Cannot open fit result ", resultName
    sys.exit(1)

  snapshot =  'snapshot_paramsVals_' + resultName
  w.loadSnapshot(snapshot)

  data_set = w.data(dataname)
  if data_set==None:
    print "ERROR : Cannot open dataset : ", "data_set"
    sys.exit(1)
      
  regionCat = w.obj("channelCat")
  data_set.table(regionCat).Print("v");

  regionFullName = Util.GetFullRegionName(regionCat, region);

  chosenSample = False
  if sample is not '':
    chosenSample = True
        
  ######################################################

  regSys = {}

  regionCatStr = 'channelCat==channelCat::' + regionFullName.Data()
  dataRegion = data_set.reduce(regionCatStr)
  
  nobsRegion = 0.
  
  if dataRegion:
    nobsRegion = dataRegion.sumEntries()
  else:
    print " ERROR : dataset-category dataRegion not found"
    
  if chosenSample:
    regSys['sqrtnobsa'] = 0.
  else:
    regSys['sqrtnobsa'] = TMath.Sqrt(nobsRegion)

  ####

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

  nFittedInRegion=pdfInRegion.getVal()
  regSys['sqrtnfitted'] = TMath.Sqrt(nFittedInRegion)
  regSys['nfitted'] = nFittedInRegion

  pdfFittedErrInRegion = Util.GetPropagatedError(pdfInRegion, result, doAsym) 
  regSys['totsyserr'] = pdfFittedErrInRegion


  # calculate error per parameter on  fitresult
  fpf = result.floatParsFinal() 
  
  # set all floating parameters constant
  for idx in range(fpf.getSize()):
    parname = fpf[idx].GetName()
    par = w.var(parname)
    par.setConstant()

  if len(namemap)>0: 
    #pre-defined systematics, optionally merged
    for key in namemap.keys():
      print namemap[key]
      #
      for parname in namemap[key]:
        par = w.var(parname)
        par.setConstant(False)
        pass
      #
      sysError  = Util.GetPropagatedError(pdfInRegion, result, doAsym)
      regSys['syserr_'+key] =  sysError
      #
      for idx in range(fpf.getSize()):
        parname = fpf[idx].GetName()
        par = w.var(parname)
        par.setConstant()
        pass
  else: 
    #all systematics, one-by-one
    for idx in range(fpf.getSize()):
      parname = fpf[idx].GetName()
      par = w.var(parname)
      par.setConstant(False)
      sysError  = Util.GetPropagatedError(pdfInRegion, result, doAsym)
      regSys['syserr_'+parname] =  sysError
      par.setConstant() 

  return regSys
  


##################################
##################################
##################################

# MAIN

if __name__ == "__main__":
  
  import os, sys
  import getopt
  def usage():
    print "Usage:"
    print "SysTable.py [-c channels] [-w workspace_afterFit] [-o outputFileName] [-o outputFileName] [-s sample] [-%] [-b] <python/MySystTableConfig.py> \n"
    print "Minimal set of inputs [-c channels] [-w workspace_afterFit]"
    print "*** Options are: "
    print "-c <channels>: single channel (region) string or comma separated list accepted (OBLIGATORY)"
    print "-w <workspaceFileName>: single name accepted only (OBLIGATORY) ;   if multiple channels/regions given in -c, assumes the workspace file contains all channels/regions"
    print "-s <sample>: single unique sample name or comma separated list accepted (sample systematics will be calculated for every region given)"
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
    opts, args = getopt.getopt(sys.argv[1:], "o:c:w:s:%by")
  except:
    usage()
  if len(opts)<2:
    usage()

  outputFileName="default"
  showAfterFitError=True
  showPercent=False
  doAsym=True
  sampleStr=''
  chosenSample = False
  for opt,arg in opts:
    if opt == '-c':
      chanStr=arg.replace(",","_")
      chanList=arg.split(",")
    elif opt == '-w':
      wsFileName=arg
    elif opt == '-o':
      outputFileName=arg
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

  for chan in origChanList:

    if not chosenSample:
      regSys = latexfitresults(wsFileName,namemap,chan,'',resultName,'obsData',doAsym)
      chanSys[chan] = regSys
      chanList.append(chan)
    else:
      for sample in sampleList:
        sampleName=getName(sample)
        regSys = latexfitresults(wsFileName,namemap,chan,sample,resultName,'obsData',doAsym)
        chanSys[chan+"_"+sampleName] = regSys
        chanList.append(chan+"_"+sampleName)
        pass
      pass

  line_chanSysTight = tablefragment(chanSys,'Signal',chanList,skiplist,chanStr,showPercent)
  
  f = open(outputFileName, 'w')
  f.write( line_chanSysTight )
  f.close()
  print "\nwrote results in file: %s"%(outputFileName)

