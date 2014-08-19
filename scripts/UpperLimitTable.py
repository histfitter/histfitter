#!/usr/bin/env python
"""
 * Project : HistFitter - A ROOT-based package for statistical data analysis      *
 * Package : HistFitter                                                           *
 * Script  : UpperLimitTable.py                                                   *
 * Created : November 2012                                                        *
 *                                                                                *
 * Description:                                                                   *
 *      Script for calculating upper limits, based on model-independent signal    *
 *      fit and producing publication-quality tables                              *
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
from ROOT import ConfigMgr,FitConfig 
gROOT.Reset()

from ROOT import TFile, RooWorkspace, TObject, TString, RooAbsReal, RooRealVar, RooFitResult, RooDataSet, RooAddition, RooArgSet,RooAbsData,RooRandom 
from ROOT import Util, TMath, RooStats
from ROOT import RooFit

from UpperLimitTableTex import *

import pickle
import os
import sys

def latexfitresults(filename, poiname='mu_SIG', lumiFB=1.0, nTOYS=3000, asimov=False, wname='combined'):
  """
  Calculate before/after-fit yields in all channels given
  
  @param filename The filename containing afterFit workspace
  @param poiname Name of ParameterOfInterest = POI (default='mu_SIG')
  @param lumiFB Given lumi in fb-1 to translate upper limit on N_events into xsection limit (default='1.0')
  @param nTOYS Number of toys to be run
  @param asimov Boolean to run asimov or not (default=False)
  @param wname RooWorkspace name in file (default='combined')
  """

  """
  pick up workspace from file
  """
  workspacename=wname
  w = Util.GetWorkspaceFromFile(filename,workspacename)
  if w==None:
    print "ERROR : Cannot open workspace : ", workspacename
    sys.exit(1) 

    
  """
  Set the POI in ModelConfig
  """
  if len(poiname)==0:
    print " "
  else:
    modelConfig = w.obj("ModelConfig")
    poi = w.var(poiname)
    if poi==None:
      print "ERROR : Cannot find POI with name: ", poiname, " in workspace from file ", filename
      sys.exit(1)
    modelConfig.SetParametersOfInterest(RooArgSet(poi))
    modelConfig.GetNuisanceParameters().remove(poi)

  """
  set some default values for nToys, calculator type and npoints to be scanned
  """
  ntoys = 3000
  calctype = 0   # toys = 0, asymptotic (asimov) = 2
  npoints = 20

  if nTOYS != 3000 and nTOYS>0:
    ntoys = nTOYS
  if asimov:
    calctype = 2
 
  """
  set the range of POI to be scanned and perform HypoTest inversion
  """
  murangelow = 0.0
  murangehigh = 40.0
  hti_result = RooStats.DoHypoTestInversion(w,ntoys,calctype,3,True,npoints,murangelow,murangehigh)

  """
  save and print the HypoTest result
  """
  outFileName = "./htiResult_poi_" + poiname + "_ntoys_" + str(ntoys) + "_calctype_" + str(calctype) + "_npoints_" + str(npoints) + ".root"
  hti_result.SaveAs(outFileName)
  hti_result.Print()

  """
  get the upper limit on N_obs out of hypotest result, and transform to limit on visible xsection
  """
  uL_nobsinSR = hti_result.UpperLimit()
  uL_visXsec = uL_nobsinSR / lumiFB

  """
  get the expected upper limit and one scan point up and down to calculate the error on upper limit
  """
  uL_nexpinSR = hti_result.GetExpectedUpperLimit(0)
  uL_nexpinSR_P = hti_result.GetExpectedUpperLimit(1) 
  uL_nexpinSR_M = hti_result.GetExpectedUpperLimit(-1)
  if uL_nexpinSR > uL_nexpinSR_P or uL_nexpinSR < uL_nexpinSR_M:
    print " \n something very strange, either the uL_nexpinSR > uL_nexpinSR_P or uL_nexpinSR < uL_nexpinSR_M"
    print "  uL_nexpinSR = ", uL_nexpinSR , " uL_nexpinSR_P = ", uL_nexpinSR_P, " uL_nexpinSR_M = ", uL_nexpinSR_M
  uL_nexpinSRerrP = hti_result.GetExpectedUpperLimit(1) - uL_nexpinSR
  uL_nexpinSRerrM = uL_nexpinSR - hti_result.GetExpectedUpperLimit(-1)

  """
  find the CLB values at indexes above and below observed CLs p-value
  """
  CLB_P = 0.
  CLB_M = 0.
  mu_P = 0.
  mu_M = 0.
  index_P = 0
  indexFound = False
  for iresult in range(hti_result.ArraySize()):
    xval = hti_result.GetXValue(iresult) 
    yval = hti_result.GetYValue(iresult)
    if xval>uL_nobsinSR and not indexFound:
      index_P = iresult
      CLB_P = hti_result.CLb(iresult)
      mu_P = xval
      if iresult>0:
        CLB_M = hti_result.CLb(iresult-1)
        mu_M = hti_result.GetXValue(iresult-1)
        indexFound = True

  """
  interpolate (linear) the value of CLB to be exactly above upperlimit p-val
  """
  try:
    alpha_CLB = (CLB_P - CLB_M) / (mu_P - mu_M)
    beta_CLB = CLB_P - alpha_CLB*mu_P
    CLB = alpha_CLB * uL_nobsinSR + beta_CLB
  except ZeroDivisionError:
    print "WARNING ZeroDivisionError while calculating CLb. Setting CLb=0."
    CLB=0.0

   
  print "\n\n\n\n  ***---  now doing p-value (s=0) calculation ---*** \n\n\n\n"

  """
  reset parameter values and errors for p(s=0) calculation by reopening workspace
  """
  w2 = Util.GetWorkspaceFromFile(filename,workspacename) 
  
  if w2==None:
    print "ERROR : Cannot open workspace : ", workspacename
    sys.exit(1) 
        
  """
  calculate p(s=0) from the workspace given
  """
  pval = RooStats.get_Presult(w2,False,ntoys,calctype)
  
  ulList = [uL_visXsec, uL_nobsinSR, uL_nexpinSR, uL_nexpinSRerrP, uL_nexpinSRerrM, CLB, pval ]

  return ulList





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
    print "UpperLimitTable.py [-c channels] [-w workspace] [-l lumi] [-n nTOYS] [-a asymptotic/Asimov] [-o outputFileName] [-p poiName] [-i]"
    print "Minimal set of inputs [-c channels] [-w workspace] [-l lumi] "
    print "UpperLimitTable.py needs the workspace file _before_ the fit, so not XXX_afterFit.root"
    print "Every channel (=SR) needs to have its own workspace file, with the same naming scheme only replacing the channel (SR) name in the workspace file name \n"
    print "*** Options are: "
    print "-c <channels>: single channel string (=SR) or comma separated list accepted (OBLIGATORY)"
    print "-w <workspaceFileName>: single name accepted only (OBLIGATORY) ;   if multiple channels given in -c, assumes the workspace filenaming scheme is general (discussed above)"
    print "-l <lumi>: same unit as used for creating the workspace by HistFitter (OBLIGATORY)"
    print "-n <nTOYS>: sets number of TOYs (default = 3000)"
    print "-a : use asimov dataset, ie asymptotic calculation insted of toys (default is toys)"
    print "-p <poiNames>: single POI name string (mu_<SRname>) or comma separated list accepted, only needed if your workspace contains a different POI then mu_<SRname>"
    print "-o <outputFileName>: sets the output table file name"
    print "-i stays in interactive session after executing the script (default off)"
    
    print "\nFor example:"
    print "UpperLimitTable.py -c SR4jTEl -w /afs/cern.ch/user/k/koutsman/HistFitterUser/MET_jets_leptons/results/MyDiscoveryAnalysis_Lumi_SR4jTEl_SPlusB_combined_NormalMeasurement_model.root -l 4.713"
    print "UpperLimitTable.py -c SR4jTEl,SR4jTMu -w /afs/cern.ch/user/k/koutsman/HistFitterUser/MET_jets_leptons/results/MyDiscoveryAnalysis_Lumi_SR4jTEl_SPlusB_combined_NormalMeasurement_model.root -l 4.713 -p mu_SR4jTEl,mu_SR4jTMu"
    print "UpperLimitTable.py -c SR4jTEl,SR4jTMu -w /afs/cern.ch/user/k/koutsman/HistFitterUser/MET_jets_leptons/results/MyDiscoveryAnalysis_Lumi_SR4jTEl_SPlusB_combined_NormalMeasurement_model.root -l 4.713 -p mu_SR4jTEl,mu_SR4jTMu -i"
    print "UpperLimitTable.py -c SR4jTEl -w /afs/cern.ch/user/k/koutsman/HistFitterUser/MET_jets_leptons/results/MyDiscoveryAnalysis_Lumi_SR4jTEl_SPlusB_combined_NormalMeasurement_model.root -l 4.713 -o MyUpperLimit_SR4jTEl.tex"
    print "UpperLimitTable.py -c SR4jTEl -w /afs/cern.ch/user/k/koutsman/HistFitterUser/MET_jets_leptons/results/MyDiscoveryAnalysis_Lumi_SR4jTEl_SPlusB_combined_NormalMeasurement_model.root -l 4.713 -n 5000"
    print "UpperLimitTable.py -c SR4jTEl -w /afs/cern.ch/user/k/koutsman/HistFitterUser/MET_jets_leptons/results/MyDiscoveryAnalysis_Lumi_SR4jTEl_SPlusB_combined_NormalMeasurement_model.root -l 4.713 -a"
    sys.exit(0)        

  wsFileName='/results/MyOneLeptonKtScaleFit_HardLepR17_BkgOnlyKt_combined_NormalMeasurement_model_afterFit.root'
  try:
    opts, args = getopt.getopt(sys.argv[1:], "c:w:l:o:n:p:ai")
  except:
    usage()
  if len(opts)<3:
    usage()

  """
  set some default options
  """
  runInterpreter = False
  outputFileName = "default"
  lumiFB = -1
  useAsimovSet = False
  nTOYS = -1
  poiName = "default"

  """
  set options as given by the user call
  """
  for opt,arg in opts:
    if opt == '-c':
      chanStr = arg.replace(",","_")
      chanList = arg.split(",")
    elif opt == '-w':
      wsFileName = arg
    elif opt == '-o':
      outputFileName = arg
    elif opt == '-l':
      lumiFB = float(arg)
    elif opt == '-n':
      nTOYS = int(arg)
    elif opt == '-a':
      useAsimovSet = True
    elif opt == '-p':
      poiName = arg
      poiList = arg.split(",")
    elif opt == '-i':
      runInterpreter = True

  if lumiFB == -1:
    print " Luminosity must be given with -l option\n"
    usage()
      
  if outputFileName == "default":
    outputFileName = "UpperLimitTable_"+chanStr+".tex"
    if useAsimovSet:
      outputFileName = "UpperLimitTable_"+chanStr+"_asimov.tex"
    elif nTOYS >0:
      outputFileName = "UpperLimitTable_"+chanStr+"_nToys"+str(nTOYS)+".tex"
    pass

  if useAsimovSet and nTOYS>0:
    print "Info: -a means you will use the Asimov dataset, no need to specify nTOYS (with -n) as it will not be used in this case"
    sys.exit(0)
  
  """
  make a list of workspace (outputfile, poi) names, if multiple channels/regions are required.
  assumption is that the only difference in the wsname is the channel/region -- FIXME
  """
  wsFileNameList = []
  outputFileNameList = []
  if poiName == "default":
    poiList = []

  for chan in chanList:
    if os.path.isfile(wsFileName):
      wsFileNameList.append(wsFileName)
    else:
      print " \n\n\n Warning: workspace file ", wsFileName, " does not exist, remove this channel from command or make this workspace file available"
      sys.exit(0)
    tmp_outputFileName = "UpperLimitTable_"+chan+".tex"
    if useAsimovSet:
      tmp_outputFileName = "UpperLimitTable_"+chan+"_asimov.tex"
    elif nTOYS >0:
      tmp_outputFileName = "UpperLimitTable_"+chan+"_nToys"+str(nTOYS)+".tex"
    outputFileNameList.append(tmp_outputFileName)
    if poiName == "default":
      tmp_poiName = "mu_" + chan
      poiList.append(tmp_poiName)

  if len(chanList) != len(poiList):
    print " \n Warning: given list of channels has different size than list of POI names:  len(chanList) = ", len(chanList), "  len(poiList) = ", len(poiList)
    sys.exit(0)

  if len(chanList) != len(wsFileNameList):
    print " \n Warning: given list of channels has different size than created list of workspace names:  len(chanList) = ", len(chanList), "  len(wsFileNameList) = ", len(wsFileNameList)

  """
  call the function to calculate the upper limits
  """
  upLim = {}
  for index,chan in enumerate(chanList):      
    poiNameChan = poiList[index]
    wsFileNameChan = wsFileNameList[index]
    outputFileNameChan = outputFileNameList[index]
      
    """
    calculate upper limit
    """
    ulMapChan = latexfitresults(wsFileNameChan, poiNameChan, lumiFB, nTOYS, useAsimovSet) #, chan)
    upLim[chan] = ulMapChan
    """
    print file for every channel separately
    """
    if len(chanList)>1:
      upLimSingleChan = {}
      upLimSingleChan[chan] = ulMapChan
      tablename = 'upperlimit.' + chan
      line_upLim = tablefragment(upLimSingleChan,tablename)
      f = open(outputFileNameChan,'w')
      f.write( line_upLim )
      f.close()
      print "\nResult written in:"
      print outputFileNameChan

  """
  write out LaTeX table by calling function from UpperLimitTableTex.py
  """
  tablename = 'upperlimit.' + chanStr
  line_upLim = tablefragment(upLim,tablename)
  f = open(outputFileName,'w')
  f.write( line_upLim )
  f.close()
  print "\nResult written in:"
  print outputFileName

  if runInterpreter:
    from code import InteractiveConsole
    from ROOT import Util
    cons = InteractiveConsole(locals())
    cons.interact("Continuing interactive session... press Ctrl+d to exit")
    pass

