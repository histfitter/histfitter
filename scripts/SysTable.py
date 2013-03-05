#!/usr/bin/env python
from ROOT import gROOT,gSystem,gDirectory
gSystem.Load("libSusyFitter.so")
from ROOT import ConfigMgr,FitConfig #this module comes from gSystem.Load("libSusyFitter.so")
gROOT.Reset()

from ROOT import TFile, RooWorkspace, TObject, TString, RooAbsReal, RooRealVar, RooFitResult, RooDataSet, RooAddition, RooArgSet,RooAbsData,RooRandom 
from ROOT import Util, TMath
from ROOT import RooFit
from ROOT import RooExpandedFitResult
    
import os
import sys
from sys import exit

from SysTableTex import *
import pickle


def getnamemap():

  namemap = {}
  namemap['alpha_JSig'] = 'Jet energy scale signal'

  namemap['alpha_BT'] = 'B tagging'
  namemap['alpha_JER'] = 'Jet energy resolution'
  namemap['alpha_JES'] = 'Jet energy scale'
  namemap['alpha_LE'] = 'Lepton efficiency'

  namemap['alpha_pythgen'] = 'TTbar: Pythia/Alpgen difference'
  namemap['alpgen_mes'] = 'Muon energy scale'

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
  namemap['alpha_pythwig'] = 'TTbar: PowhegPythia/PowhegJimmy difference'
  namemap['alpha_sherpgen'] = 'W: SherpaWMassiveB/AlpgenJimmyW difference'
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
  namemap['alpha_err'] = 'MC Background'
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
  namemap['alpha_LE'] = 'Lepton efficiency'
  namemap['alpha_PU'] = 'Pile-up'
  namemap['alpha_TE'] = 'Trigger weight'
  namemap['alpha_JR'] = 'Jet energy resolution'

  namemap['mu_SR3jT'] = 'Signal yield 3jT'
  namemap['mu_SR4jT'] = 'Signal yield 4jT'

  namemap['mu_SS'] = 'Signal yield soft lepton SR'
  namemap['mu_SR1s2j'] = 'Signal yield s1l2j'

  return namemap

  

def latexfitresults( filename, region='3jL', sample='', resultName="RooExpandedFitResult_afterFit", dataname='obsData'):

  namemap = {} ## add this if I want description
  namemap = getnamemap() ## add this if I want description

  ############################################
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
        
  #####################################################

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

  nFittedInRegion = pdfInRegion.getVal()
  regSys['sqrtnfitted'] = TMath.Sqrt(nFittedInRegion)
  regSys['nfitted'] = nFittedInRegion

  pdfFittedErrInRegion = Util.GetPropagatedError(pdfInRegion, result) 
  regSys['totsyserr'] = pdfFittedErrInRegion


  # calculate error per parameter on  fitresult
  fpf = result.floatParsFinal() 
  
  # set all floating parameters constant
  for idx in range(fpf.getSize()):
    parname = fpf[idx].GetName()
    par = w.var(parname)
    par.setConstant()
    
  for idx in range(fpf.getSize()):
    parname = fpf[idx].GetName()
    par = w.var(parname)
    par.setConstant(False)
    sysError  = Util.GetPropagatedError(pdfInRegion, result)
    if namemap.has_key(parname): ## add this if I want description
      parname = namemap[parname] ## add this if I want description
    regSys['syserr_'+parname] =  sysError
    par.setConstant() 

  

  return regSys





##################################
##################################
##################################


def latexfitresults_method2(filename,resultname='RooExpandedFitResult_afterFit', region='3jL', sample='', fitregions = 'WR,TR,S3,S4,SR3jT,SR4jT', dataname='obsData'):

#  namemap = {}
#  namemap = getnamemap()

 ############################################
   
  w = Util.GetWorkspaceFromFile(filename,'w')
  if w==None:
    print "ERROR : Cannot open workspace : "
    sys.exit(1) 

  result = w.obj(resultname)
  if result==None:
    print "ERROR : Cannot open fit result : ", resultname
    sys.exit(1)

  resultlistOrig = result.floatParsFinal()
    
  snapshot =  'snapshot_paramsVals_' + resultname
  w.loadSnapshot(snapshot)

  data_set = w.data(dataname)
  if data_set==None:
    print "ERROR : Cannot open dataset : ", "data_set"
    sys.exit(1)
      
  regionCat = w.obj("channelCat")
  data_set.table(regionCat).Print("v");

  regionFullName = Util.GetFullRegionName(regionCat, region)

  fitRegionsList = fitregions.split(",")
  fitRegionsFullName = ""
  for reg in fitRegionsList:
    regFullName = Util.GetFullRegionName(regionCat, reg)
    if fitRegionsFullName == "":
      fitRegionsFullName = regFullName.Data()
    else:
      fitRegionsFullName = fitRegionsFullName + "," + regFullName.Data()

  chosenSample = False
  if sample is not '':
    chosenSample = True

  #####################################################

  regSys = {}

  regionCatStr = 'channelCat==channelCat::' + regionFullName.Data()
  dataRegion = data_set.reduce(regionCatStr)
  nobsRegion = 0.
  
  if dataRegion:
    nobsRegion = dataRegion.sumEntries()
  else:
    print " ERROR : dataset-category", regionCatStr, " not found"
    
  if chosenSample:
    regSys['sqrtnobsa'] = 0.
  else:
    regSys['sqrtnobsa'] = TMath.Sqrt(nobsRegion)

  ####

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

  nFittedInRegion = pdfInRegion.getVal()
  regSys['sqrtnfitted'] = TMath.Sqrt(nFittedInRegion)

  pdfFittedErrInRegion = Util.GetPropagatedError(pdfInRegion, result) 
  regSys['totsyserr'] = pdfFittedErrInRegion
  
  # redo the fit for every parameter being fixed
  lumiConst = True
  fpf = result.floatParsFinal()
  
  # redo the fit for every parameter being fixed
  for idx in range(fpf.getSize()):
    
    parname = fpf[idx].GetName()
    print "\n Method-2: redoing fit with fixed parameter ", parname

    # the parameter that is fixed, needs to have the value of the default fit
    w.loadSnapshot(snapshot)
    par = w.var(parname)

    #     # before redoing the fit, set the values of parameters to initial snapshot, otherwise MIGRAD cannot find improvement
    #     w.loadSnapshot('snapshot_paramsVals_initial')
    #     par.setVal(parDefVal)
    par.setConstant(True)
    suffix = parname + "Fixed"
    result_1parfixed = Util.FitPdf(w, fitRegionsFullName, lumiConst, data_set, suffix)

    expResultAfter_1parfixed = RooExpandedFitResult(result_1parfixed, resultlistOrig)

    nFittedInRegion_1parfixed = pdfInRegion.getVal()
    pdfFittedErrInRegion_1parfixed = Util.GetPropagatedError(pdfInRegion, expResultAfter_1parfixed) #  result_1parfixed)

    if pdfFittedErrInRegion_1parfixed > pdfFittedErrInRegion:
      print "\n\n  WARNING  parameter ", parname," gives a larger error when set constant. Do you expect this?"
      print "  WARNING          pdfFittedErrInRegion = ", pdfFittedErrInRegion, "    pdfFittedErrInRegion_1parfixed = ", pdfFittedErrInRegion_1parfixed

    systError  =  TMath.Sqrt(abs(pdfFittedErrInRegion*pdfFittedErrInRegion - pdfFittedErrInRegion_1parfixed*pdfFittedErrInRegion_1parfixed))
    par.setConstant(False)

    if result_1parfixed.status()==0 and result_1parfixed.covQual()==3:   #and result_1parfixed.numStatusHistory()==2 and  result_1parfixed.statusCodeHistory(0)==0 and  result_1parfixed.statusCodeHistory(1) ==0:
      systError = systError
    else:
      systError = 0.0
      print "        WARNING :   for parameter ",parname," fixed the fit does not converge, as status=",result_1parfixed.status(), "(converged=0),  and covariance matrix quality=", result_1parfixed.covQual(), " (full accurate==3)"
      print "        WARNING: setting systError = 0 for parameter ",parname

      #if namemap.has_key(parname):
      #  parname = namemap[parname]
    regSys['syserr_'+parname] =  systError

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
    print "SysTable.py [-c channels] [-w workspace_afterFit] [-o outputFileName] [-o outputFileName] [-s sample] [-m method] [-f fitregions] [-%] [-b]\n"
    print "Minimal set of inputs [-c channels] [-w workspace_afterFit]"
    print "*** Options are: "
    print "-c <channels>: single channel (region) string or comma separated list accepted (OBLIGATORY)"
    print "-w <workspaceFileName>: single name accepted only (OBLIGATORY) ;   if multiple channels/regions given in -c, assumes the workspace file contains all channels/regions"
    print "-s <sample>: single unique sample name or comma separated list accepted (sample systematics will be calculated for every region given)"
    print "-o <outputFileName>: sets the output table file name, name defined by regions if none provided"
    print "-b: shows the error on samples Before the fit (by default After fit is shown)"
    print "-%: also show the individual errors as percentage of the total systematic error (off by default)"

    print "\nFor example:"
    print "SysTable.py -w /afs/cern.ch/user/k/koutsman/HistFitterUser/MET_jets_leptons/results/Combined_KFactorFit_5Channel_Validation_combined_BasicMeasurement_model_afterFit.root  -c SR7jTEl_meffInc,SR7jTMu_meffInc"
    print "SysTable.py -w  /afs/cern.ch/user/c/cote/susy0/users/cote/HistFitter5/results/Combined_KFactorFit_5Channel_bkgonly_combined_BasicMeasurement_model_afterFit.root  -c SR7jTEl_meffInc,SR7jTMu_meffInc -o SystematicsMultiJetsSR.tex"
    print "SysTable.py -w  /afs/cern.ch/user/k/koutsman/HistFitterUser/MET_jets_leptons/results/Combined_KFactorFit_5Channel_Validation_combined_BasicMeasurement_model_afterFit.root  -c SR7jTEl,SR7jTMu -m 2 -f WREl,WRMu,TREl,TRMu"
    print "SysTable.py -w  /afs/cern.ch/user/k/koutsman/HistFitterUser/MET_jets_leptons/results/Combined_KFactorFit_5Channel_Validation_combined_BasicMeasurement_model_afterFit.root  -c SR7jTEl,SR7jTMu -s Top,WZ"
    print "SysTable.py -w ~/Combined_KFactorFit_5Channel_Validation_combined_BasicMeasurement_model_afterFit.root -c SR7jTEl -m 2 -f TRee_nJet,TRem_nJet,TRmm_nJet,TREl_nJet,TRMu_nJet,ZRee_nJet,ZRmm_nJet,WREl_nJet,WRMu_nJet"

    print "\n  Method-1: set all parameters constant, except for the one you're interested in, calculate the error propagated due to that parameter"
    print "  Method-2: set the parameter you're interested in constant, redo the fit with all other parameters floating, calculate the quadratic difference between default fit and your new model with parameter fixed"
    sys.exit(0)        

  wsFileName='/results/MyOneLeptonKtScaleFit_HardLepR17_BkgOnlyKt_combined_NormalMeasurement_model_afterFit.root'
  try:
    opts, args = getopt.getopt(sys.argv[1:], "o:c:w:m:f:s:%b")
  except:
    usage()
  if len(opts)<2:
    usage()

  outputFileName="default"
  method="1"
  showAfterFitError=True
  showPercent=False
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
      sampleStr=arg.replace(",","_")
      sampleList=arg.split(",")
    elif opt == '-b':
      showAfterFitError=False
    elif opt == '-%':
      showPercent=True
     
  if outputFileName=="default":
    outputFileName=chanStr+'_SysTable.tex'
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

  chosenSample = False
  try:
    sampleList
    chosenSample=True
  except NameError:
    pass

 
  resultName = 'RooExpandedFitResult_afterFit'
  if not showAfterFitError:
    resultName =  'RooExpandedFitResult_beforeFit'

  skiplist = ['sqrtnobsa', 'totbkgsysa', 'poisqcderr','sqrtnfitted','totsyserr','nfitted']

  chanSys = {}
  origChanList = list(chanList)
  for chan in origChanList:
    if method == "2":
      regSys = latexfitresults_method2(wsFileName,resultName,chan,'',fitRegionsStr,'obsData')
    else:
      regSys = latexfitresults(wsFileName,chan,'',resultName,'obsData')
    chanSys[chan] = regSys

    if chosenSample:
      for sample in sampleList:
        if method == "2":
          regSys = latexfitresults_method2(wsFileName,resultName,chan,sample,fitRegionsStr,'obsData')
        else:
          regSys = latexfitresults(wsFileName,chan,sample,resultName,'obsData')
        chanSys[chan+"_"+sample] = regSys
        chanList.append(chan+"_"+sample)

  line_chanSysTight = tablefragment(chanSys,'Signal',chanList,skiplist,chanStr,showPercent)
  
  f = open(outputFileName, 'w')
  f.write( line_chanSysTight )
  f.close()
  print "\nwrote results in file: %s"%(outputFileName)

