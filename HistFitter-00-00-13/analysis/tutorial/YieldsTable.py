#!/usr/bin/env python
#from sys import exit
#from ROOT import gSystem
#gSystem.Load("libCombinationTools")

from ROOT import gROOT,gSystem,gDirectory
gSystem.Load("libSusyFitter.so")
gROOT.Reset()

from ROOT import TFile, RooWorkspace, TObject, TString, RooAbsReal, RooRealVar, RooFitResult, RooDataSet, RooAddition, RooArgSet, RooFormulaVar, RooAbsData, RooRandom 
from ROOT import Util, TMath, TMap, RooExpandedFitResult

from TexYieldsTable import *
import os
import sys

# Main function calls are defined below.

def latexfitresults(filename = os.environ['SUSYFITTER'] + '/results/MyOneLeptonKtScaleFit_BkgOnlyKt_combined_NormalMeasurement_model_afterFit.root',regionList='3jL', dataname='obsData'):

  print "hallo"
  ####

  w = Util.GetWorkspaceFromFile(filename,'w')

  if w==None:
    print "ERROR : Cannot open workspace : ", workspacename
    sys.exit(1) 

  resultname = 'RooExpandedFitResult_afterFit'
  result = w.obj(resultname)

  if result==None:
    print "ERROR : Cannot open fit result : ", resultname
    sys.exit(1)

  snapshot =  'snapshot_paramsVals_' + resultname
  w.loadSnapshot(snapshot)

  if not w.loadSnapshot(snapshot):
    print "ERROR : Cannot load snapshot : ", snapshot
    sys.exit(1)

    
  data_set = w.data(dataname)
  if data_set==None:
    print "ERROR : Cannot open dataset : ", "data_set"+suffix
    sys.exit(1)
      
  regionCat = w.obj("channelCat")
  data_set.table(regionCat).Print("v");

  regionFullNameList = [ Util.GetFullRegionName(regionCat, region) for region in regionList]
  print " \n Requested regions = ",  regionFullNameList, "\n\n"


  ###

  tablenumbers = {}
  tablenumbers['names'] = regionList 
 
  regionCatList = [ 'channelCat==channelCat::' +region.Data() for region in regionFullNameList]
  
  regionDatasetList = [data_set.reduce(regioncat) for regioncat in regionCatList]
  for index, data in  enumerate(regionDatasetList):
    data.SetName("data_" + regionList[index])
    data.SetTitle("data_" + regionList[index])
    
  nobs_regionList = [ data.sumEntries() for data in regionDatasetList]
  tablenumbers['nobs'] = nobs_regionList
 
  ####

  bkginRegionList = [ Util.GetComponent(w,"Top,WZ,QCD,BG",region) for region in regionList]
  nbkginRegionList = [  bkginRegion.getVal() for bkginRegion in bkginRegionList]
  [region.Print() for region in bkginRegionList]
  print "\n N bkgs in regions = ", nbkginRegionList

  nbkgerrinRegionList = [ Util.GetPropagatedError(bkginRegion, result)  for bkginRegion in bkginRegionList]
  print "\n error N bkgs in regions = ", nbkgerrinRegionList

  WZinRegionList = [ Util.GetComponent(w,"WZ",region) for region in regionList]
  TopinRegionList = [ Util.GetComponent(w,"Top",region) for region in regionList]

  nWZinRegionList = [  WZinRegion.getVal() for WZinRegion in WZinRegionList]
  nTopinRegionList = [  TopinRegion.getVal() for TopinRegion in TopinRegionList]

  print "\n N WZ in regions = ", nWZinRegionList
  print  "\n N Top in regions = ", nTopinRegionList

  nWZerrinRegionList = [ Util.GetPropagatedError(WZinRegion, result)  for WZinRegion in WZinRegionList]
  nToperrinRegionList = [ Util.GetPropagatedError(TopinRegion, result)  for TopinRegion in TopinRegionList]

  print "\n error N WZ in regions = ", nWZerrinRegionList
  print "\n error N Top in regions = ", nToperrinRegionList

  ######
  # Example how to add multiple backgrounds in multiple(!) regions
  TopWZinRegionList = [ RooAddition( ("TopWZin" + regionList[index]),("TopWZin" + regionList[index]),RooArgSet(TopinRegionList[index],WZinRegionList[index]))  for index, region in enumerate (regionList)]
  nTopWZinRegionList = [ TopWZinRegion.getVal() for TopWZinRegion in TopWZinRegionList]
  nTopWZerrinRegionList = [ Util.GetPropagatedError(TopWZinRegion, result)   for TopWZinRegion in TopWZinRegionList]
   

  ######
  ######
  ######  FROM HERE ON OUT WE CALCULATE THE EXPECTED NUMBER OF EVENTS __BEFORE__ THE FIT
  ######
  ######

  #  FROM HERE ON OUT WE CALCULATE THE EXPECTED NUMBER OF EVENTS BEFORE THE FIT
  w.loadSnapshot('snapshot_paramsVals_RooExpandedFitResult_beforeFit')
  
  pdfinRegionList = [ Util.GetRegionPdf(w, region)  for region in regionList]

  varinRegionList =  [ Util.GetRegionVar(w, region) for region in regionList]

  nexpinRegionList =  [ pdf.expectedEvents(RooArgSet(varinRegionList[index])) for index, pdf in enumerate(pdfinRegionList)]
  print "\n N expected in regions = ", nexpinRegionList
    
  fracWZinRegionList   = [ Util.GetComponentFracInRegion(w,"WZ",region)  for region in regionList]
  fracTopinRegionList   = [ Util.GetComponentFracInRegion(w,"Top",region)  for region in regionList]

  mcWZinRegionList    = [  fracWZinRegionList[index]*nexpinRegionList[index]   for index, region in enumerate(regionList)]
  mcTopinRegionList   = [  fracTopinRegionList[index]*nexpinRegionList[index]   for index, region in enumerate(regionList)]
  
  #  mcSMinRegionList = [ mcWZinRegionList[index] + mcTopinRegionList[index] +  mcQCDinRegionList[index] + mcBGinRegionList[index]  for index, region in enumerate(regionList)]
  mcSMinRegionList = [ mcWZinRegionList[index] + mcTopinRegionList[index]  for index, region in enumerate(regionList)]
  print "\n N expected WZ in regions = ", mcWZinRegionList   
  print "\n N expected Top in regions = ", mcTopinRegionList  
  
  tablenumbers['MC_exp_top_WZ_events'] = [ mcWZinRegionList[index] + mcTopinRegionList[index]   for index, region in enumerate(regionList)]
  tablenumbers['MC_exp_top_events']    = [ mcTopinRegion  for mcTopinRegion  in mcTopinRegionList ]
  tablenumbers['MC_exp_WZ_events']    = [ mcWZinRegion  for mcWZinRegion  in mcWZinRegionList ]
  tablenumbers['MC_exp_SM_events']    = [ mcSMinRegion  for mcSMinRegion  in mcSMinRegionList ]
  
  tablenumbers['Fitted_bkg_events']    =  nbkginRegionList
  tablenumbers['Fitted_bkg_events_err']    =  nbkgerrinRegionList

  tablenumbers['Fitted_top_events']    = nTopinRegionList
  tablenumbers['Fitted_top_events_err']    = nToperrinRegionList

  tablenumbers['Fitted_WZ_events']    = nWZinRegionList
  tablenumbers['Fitted_WZ_events_err']    = nWZerrinRegionList
  
  tablenumbers['Fitted_top_WZ_events'] = nTopWZinRegionList
  tablenumbers['Fitted_top_WZ_events_err'] = nTopWZerrinRegionList
  
  ###
  return tablenumbers




##################################
##################################
##################################

#### Main function calls start here ....

filename = os.environ['SUSYFITTER'] + '/results/MyHistFitterExample_BkgOnly_combined_NormalMeasurement_model_afterFit.root'
regionsList = ['SLWR','SLTR']
signalregionsList = ['SLWR']

m3 = latexfitresults(filename,regionsList)

f = open('SLWR_SLTR_yields_data.tex', 'w')
f.write( tablestart() )
f.write( tablefragment(m3, '', signalregionsList) )
f.write( tableend4(regionsList, 'slwr.sltr') )
f.close()

