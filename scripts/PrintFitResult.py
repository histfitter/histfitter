#!/usr/bin/env python
"""
 * Project : HistFitter - A ROOT-based package for statistical data analysis      *
 * Package : HistFitter                                                           *
 * Script  : PrintFitResult.py                                                    *
 *                                                                                *
 * Description:                                                                   *
 *               Script to produce LaTeX table for fit result                     *
 *                                                                                *
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
from ROOT import Util, TMath
from ROOT import RooFit
from ROOT import RooExpandedFitResult
    
import os
import sys
from sys import exit

from PrintFitResultTex import *
import pickle


def getnamemap():
  """
  Function changing HitFactory naming-scheme into human-readable scheme (to be adjusted by each user, if wanted)
  """

  namemap = {}
  namemap['alpha_JSig'] = 'Jet energy scale signal'

  namemap['alpha_BT'] = 'B tagging'
  namemap['alpha_JER'] = 'Jet energy resolution'
  namemap['alpha_JES'] = 'Jet energy scale'
  namemap['alpha_LE'] = 'Lepton efficiency'

  namemap['alpha_RESOST'] = 'CellOut energy resolution'
  namemap['alpha_SCALEST'] = 'CellOut energy scale'
  namemap['alpha_TE'] = 'Trigger weight'
  

  namemap['alpha_QCDNorm_SR1a'] = 'QCD estimate SR1a'
  namemap['alpha_QCDNorm_SR1b'] = 'QCD estimate SR1b'
  namemap['alpha_QCDNorm_SR2a'] = 'QCD estimate SR2a'
  namemap['alpha_QCDNorm_SR2b'] = 'QCD estimate SR2b'
  namemap['alpha_QCDNorm_SR2l'] = 'QCD estimate SR2l'
  namemap['alpha_QCDNorm_SR1L3j'] = 'QCD estimate SR1L3j'
  namemap['alpha_QCDNorm_SR1L5j'] = 'QCD estimate SR1L5j'
  namemap['alpha_QCDNorm_SR1L1Ba'] = 'QCD estimate SR1L1Ba'
  namemap['alpha_QCDNorm_SR1L1Bc'] = 'QCD estimate SR1L1Bc'
  namemap['alpha_QCDNorm_SR1L2Ba'] = 'QCD estimate SR1L2Ba'
  namemap['alpha_QCDNorm_SR1L2Bc'] = 'QCD estimate SR1L2Bc'
  namemap['alpha_QCDNorm_SR2L'] = 'QCD estimate SR2L'
  namemap['alpha_QCDNorm_CRT'] = 'QCD estimate CRT'
  namemap['alpha_QCDNorm_CRW'] = 'QCD estimate CRW'
  namemap['alpha_QCDNorm_CRT5j'] = 'QCD estimate CRT5j'
  namemap['alpha_QCDNorm_CRW5j'] = 'QCD estimate CRW5j'
  namemap['alpha_QCDNorm_CRWbb'] = 'QCD estimate CRWbb'
  namemap['alpha_QCDNorm_VR1'] = 'QCD estimate VR1'
  namemap['alpha_QCDNorm_VR2'] = 'QCD estimate VR2'


  namemap['alpha_WTheoNpart'] = 'W theoretical uncertainty'
  namemap['alpha_pdfInter'] = 'pdf (none) uncertainty'
  namemap['alpha_pdfIntra'] = 'pdf (Intra,Inter) uncertainty'
  namemap['alpha_pythwig'] = 'TTbar uncertainty: PowhegPythia/PowhegJimmy difference'
  namemap['alpha_sherpgen'] = 'W uncertainty: SherpaWMassiveB/AlpgenJimmyW difference'
  namemap['alpha_topTheoFacSc'] = 'top theoretical uncertainty: FacSc'
  namemap['alpha_topTheoPS'] = 'top theoretical uncertainty: PS'
  namemap['alpha_topTheoRenSc'] = 'top theoretical uncertainty: RenSc'
  namemap['alpha_wbb'] = 'Wbb uncertainty'
 
  namemap['alpha_eglow'] = 'Electron energy scale: low-pt uncertainty'
  namemap['alpha_egmat'] = 'Electron energy scale: material uncertainty'
  namemap['alpha_egps'] = 'Electron energy scale: presampler scale uncertainty'
  namemap['alpha_egres'] = 'Electron energy resolution'
  namemap['alpha_egzee'] = 'Electron energy scale: Z scale uncertainty'

  namemap['alpha_LRImu'] = 'Muon energy resolution with inner detector'
  namemap['alpha_LRMmu'] = 'Muon energy resolution with muon system'
  
  namemap['alpha_iqoptW'] = 'kT scale Alpgen W+jets'
  namemap['alpha_ktfacT'] = 'kT scale Alpgen ttbar'
  namemap['alpha_ktfacW'] = 'kT scale Alpgen W+jets'
  namemap['alpha_qfacT'] = 'Q scale Alpgen ttbar'
  namemap['alpha_qfacW'] = 'Q scale Alpgen W+jets'
  

  namemap['alpha_pileup'] = 'Pile-up'


  namemap['gamma_stat_CRW_cuts_bin_0'] = 'MC statistics CRW bin 0'
  namemap['gamma_stat_CRT_cuts_bin_0'] = 'MC statistics CRT bin 0'
  namemap['gamma_stat_CRW5j_cuts_bin_0'] = 'MC statistics CRW5j bin 0'
  namemap['gamma_stat_CRT5j_cuts_bin_0'] = 'MC statistics CRT5j bin 0'
  namemap['gamma_stat_SR1L3j_cuts_bin_0'] = 'MC statistics SR1L3j bin 0'
  namemap['gamma_stat_SR1L5j_cuts_bin_0'] = 'MC statistics SR1L5j bin 0'
  namemap['gamma_stat_SR1L3j_cuts_bin_0'] = 'MC statistics SR1L3j bin 0'
  namemap['gamma_stat_SR1L5j_cuts_bin_0'] = 'MC statistics SR1L5j bin 0'
  namemap['gamma_stat_SR1L1Ba_cuts_bin_0'] = 'MC statistics SR1L1Ba bin 0'
  namemap['gamma_stat_SR1L1Bc_cuts_bin_0'] = 'MC statistics SR1L1Bc bin 0'
  namemap['gamma_stat_SR1L2Ba_cuts_bin_0'] = 'MC statistics SR1L2Ba bin 0'
  namemap['gamma_stat_SR1L2Bc_cuts_bin_0'] = 'MC statistics SR1L2Bc bin 0'
  namemap['gamma_stat_SR2L_cuts_bin_0'] = 'MC statistics SR2L bin 0'
  namemap['gamma_stat_VR1_cuts_bin_0'] = 'MC statistics VR1 bin 0'
  namemap['gamma_stat_VR2_cuts_bin_0'] = 'MC statistics VR2 bin 0'
  namemap['gamma_stat_VR3_cuts_bin_0'] = 'MC statistics VR3 bin 0'

  namemap['alpha_errBG'] = 'Systematics Background'
  namemap['alpha_errDB'] = 'Systematics Dibosons'
  namemap['alpha_errDY'] = 'Systematics AlpgenDrellYan'
  namemap['alpha_errST'] = 'Systematics SingleTop'
  namemap['alpha_errTV'] = 'Systematics ttbarV'
  namemap['alpha_errZ'] = 'Systematics AlpgenZ'
  namemap['mu_Top'] =  'ttbar yield'
  namemap['mu_WZ'] = 'W(Z)+jets yield'


  
  namemap['alpha_JR3T'] = 'Jet energy resolution 3jT'
  namemap['alpha_JR4T'] =  'Jet energy resolution 4jT'

  namemap['alpha_LES'] = 'Lepton energy scale'
  namemap['alpha_LRI'] = 'Lepton energy resolution with inner detector'
  namemap['alpha_LRI3T'] = 'Lepton energy resolution with inner detector 3jT'
  namemap['alpha_LRI4T'] = 'Lepton energy resolution with inner detector 4jT'
  namemap['alpha_LRM'] =  'Lepton energy resolution with muon system'
  namemap['alpha_LRM3T'] =  'Lepton energy resolution with muon system 3jT'
  namemap['alpha_LRM4T'] =  'Lepton energy resolution with muon system 4jT'
  namemap['alpha_MC'] = 'MET cell-out'
  namemap['alpha_MC3T'] = 'MET cell-out 3jT'
  namemap['alpha_MC4T'] = 'MET cell-out 4jT'
  namemap['alpha_MP'] = 'MET pile-up'
  namemap['alpha_MP3T'] = 'MET pile-up 3jT'
  namemap['alpha_MP4T'] = 'MET pile-up 4jT'

  namemap['alpha_PtMinTop3T'] = 'pTmin ttbar 3jT'
  namemap['alpha_PtMinTop4T'] = 'pTmin ttbar 4jT'
  namemap['alpha_PtMinTopC'] =  'pTmin ttbar control regions'
  namemap['alpha_PtMinTopS2T'] =  'pTmin ttbar s1l2j'
  namemap['alpha_PtMinWZ3T'] =  'pTmin W+jets 3jT'
  namemap['alpha_PtMinWZ4T'] =  'pTmin W+jets 4jT'
  namemap['alpha_PtMinWZC'] =  'pTmin W+jets control regions'
  namemap['alpha_PtMinWZS2T'] =  'pTmin W+jets s1l2j'

  namemap['alpha_QCDNorm_S3_cuts'] = 'QCD estimate 3j'
  namemap['alpha_QCDNorm_S4_cuts'] = 'QCD estimate 4j'
  namemap['alpha_QCDNorm_TR_nJet'] =  'QCD estimate TRL1'
  namemap['alpha_QCDNorm_WR_nJet'] =  'QCD estimate WRL1'
  namemap['alpha_QCDNorm_SR1s2j_cuts'] = 'QCD estimate s1l2j' 
  namemap['alpha_QCDNorm_SR3jT_cuts'] = 'QCD estimate 3jT'	   
  namemap['alpha_QCDNorm_SR4jT_cuts'] = 'QCD estimate 4jT'   


  namemap['alpha_WP'] = 'W pT reweighting'

  namemap['gamma_J3T_bin_0'] = 'Jet energy scale 3jT'
  namemap['gamma_J4T_bin_0'] = 'Jet energy scale 4jT'
  namemap['gamma_JS2T_bin_0'] = 'Jet energy scale s1l2j'

  namemap['gamma_JC_bin_0'] = 'Jet energy scale control regions bin 0'
  namemap['gamma_JC_bin_1'] = 'Jet energy scale control regions bin 1'
  namemap['gamma_JC_bin_2'] = 'Jet energy scale control regions bin 2'
  namemap['gamma_JC_bin_3'] = 'Jet energy scale control regions bin 3'
  namemap['gamma_JC_bin_4'] = 'Jet energy scale control regions bin 4'
  namemap['gamma_JC_bin_5'] = 'Jet energy scale control regions bin 5'
  namemap['gamma_JC_bin_6'] = 'Jet energy scale control regions bin 6'


  namemap['mu_S3'] = 'Signal yield 3j'
  namemap['mu_S4'] = 'Signal yield 4j'
  namemap['mu_Top'] =  'ttbar yield'
  namemap['mu_WZ'] = 'W(Z)+jets yield'

  namemap['alpha_KtScaleTop'] = 'kT scale Alpgen ttbar'
  namemap['alpha_KtScaleWZ'] = 'kT scale Alpgen W+jets'
  namemap['alpha_LE'] = 'Lepto efficiency'
  namemap['alpha_PU'] = 'Pile-up'
  namemap['alpha_TE'] = 'Trigger weight'
  namemap['alpha_JR'] = 'Jet energy resolution'

  namemap['mu_SR3jT'] = 'Signal yield 3jT'
  namemap['mu_SR4jT'] = 'Signal yield 4jT'

  namemap['mu_SS'] = 'Signal yield soft lepton SR'
  namemap['mu_SR1s2j'] = 'Signal yield s1l2j'

  return namemap

  

def latexfitresults( filename, resultName="RooExpandedFitResult_afterFit", outName="test.tex" ):
  """
  Take out fit result and extract after/before-fit values and errors
  
  @param filename The filename containing afterFit workspace
  @param resultname The name of fit result (typically='RooExpandedFitResult_afterFit' or 'RooExpandedFitResult_beforeFit'
  @param outname Output file name
  """
  
  namemap = {}
  namemap = getnamemap()

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

  regSys = {}

  """
  extract all floating parameter values and error, both before and after fit
  """
  fpf = result.floatParsFinal() 
  fpi = result.floatParsInit()

  for idx in range(fpf.getSize()):
    parname = fpf[idx].GetName()
    ip = fpi[idx]
    ipv  = ip.getVal()
    ipe  = ip.getError()
    ipel = ip.getErrorLo()
    ipeh = ip.getErrorHi()

    fp = fpf[idx]
    fpv  = fp.getVal()
    fpe  = fp.getError()
    fpel = fp.getErrorLo()
    fpeh = fp.getErrorHi()

    name = parname
    if namemap.has_key(name): name = namemap[name]

    regSys[name] = (ipv,ipe,ipel,ipeh,fpv,fpe,fpel,fpeh)

  return regSys




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
    print "PrintFitResult.py [-c channel] [-w workspace_afterFit] [-o outputFileName]\n"
    print "Minimal set of inputs [-c channels] [-w workspace_afterFit]"
    print "*** Options are: "
    print "-c <analysis name>: single name accepted only (OBLIGATORY) "
    print "-w <workspaceFileName>: single name accepted only (OBLIGATORY) ;   if multiple channels/regions given in -c, assumes the workspace file contains all channels/regions"

    print "\nFor example:"
    print "PrintFitResult.py -w MyName_combined_BasicMeasurement_model_afterFit.root  -c SR7j -o fitResultSR7j.tex"    

    sys.exit(0)        

  wsFileName='/results/MyOneLeptonKtScaleFit_HardLepR17_BkgOnlyKt_combined_NormalMeasurement_model_afterFit.root'
  try:
    opts, args = getopt.getopt(sys.argv[1:], "o:c:w:m:f:s:%b")
  except:
    usage()
  if len(opts)<1:
    usage()
    
  """
  set some default options
  """
  analysisName = ''
  outputFileName="default"
  method="1"
  showAfterFitError=True
  showPercent=False

  """
  set options as given by the user call
  """
  for opt,arg in opts:
    if opt == '-c':
      analysisName=arg
    if opt == '-w':
      wsFileName=arg

  resultName = 'RooExpandedFitResult_afterFit'
  if not showAfterFitError:
    resultName =  'RooExpandedFitResult_beforeFit'

  """
  extract values/errors of parameters from fit result
  """
  regSys = latexfitresults(wsFileName,resultName,outputFileName)
  
  """
  write out LaTeX table by calling function from PrintFitResultTex.py function tablefragment
  """
  line_chanSysTight = tablefragment(regSys,analysisName)
  outputFileName = "fitresult_" + analysisName + ".tex"
  f = open(outputFileName, 'w')
  f.write( line_chanSysTight )
  f.close()
  print "\nwrote results in file: %s"%(outputFileName)

