/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Macro  : pvalue.C                                                              *
 * Created: 12 June 2012                                                          *
 *                                                                                *
 * Description:                                                                   *
 *      To determine the CLs/p-values (observed, expected, +/-1 sigma             *
 *      uncertainties) of the "simple channel"                                    *
 *      counting experiment created at :                                          *
 *      analysis/simplechannel/                                                   *
 *      The p-values are printed on the screen.                                   *
 *      Options (e.g. exclusion or discovery) can be set in the macro.            *
 *                                                                                *
 *      Run with: root -b -q pvalue.C                                             *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

//include RooRandom for toy generation later
#include "RooRandom.h"

//using RoFit and RooStats tools further down
using namespace RooFit;
using namespace RooStats;


/**
This function determines the CLs/p-values (observed, expected, +/-1 sigma
uncertainties) of the "simple channel" counting experiment created 
at: analysis/simplechannel/
The p-values are printed on the screen.
Options (e.g. exclusion or discovery) can be set in the macro.
Run with: root -b -q pvalue.C
*/
void
pvalue()
{
  //definition of variables
  int seed=1;            // 0 = cpu clock, so random, 1 to make reproducible results
  const char* fileprefix = "example";
  int  calculatorType=0; // 2=asymptotic approximation limit. 0=frequentist limit
  int  testStatType=3;   // one-sided test profile statistic (ATLAS standard)
  int  ntoys=5000;
  bool doUL = true;      // true = exclusion, false = discovery

  // load the linaray of HistFitter
  gSystem->Load("libHistFitter.so");


  // open workspace containing the statistical model
  TFile *file = TFile::Open("example_channel1_GaussExample_model.root");
  //RooWorkspace* w = (RooWorkspace *)file->Get("channel1"); 
 
  //TFile *file = TFile::Open("/afs/cern.ch/user/k/koutsman/HistFitterTrunk/results/Fit_Combined_softhard_SM_GG1step_1025_545_65_combined_BasicMeasurement_model.root");
  //TFile *file = TFile::Open("/afs/cern.ch/user/j/jlorenz/public/Fit_Combined_softhard_SM_GG1step_1025_545_65_combined_BasicMeasurement_model.root");
//  TFile* file = TFile::Open("/afs/cern.ch/atlas/project/cern/susy/users/jlorenz/Combination_softhard3_GG1stepx12/Fit_Combined_softhard_SM_GG1step_825_705_585_combined_BasicMeasurement_model.root");
  //TFile *file = TFile::Open("/afs/cern.ch/user/j/jlorenz/public/Fit_Combined_softhard_SM_GG1step_1025_865_705_combined_BasicMeasurement_model.root");

  //TFile *file = TFile::Open("MyUserAnalysis_SPlusB_combined_NormalMeasurement_model.root");
  RooWorkspace* w = (RooWorkspace *)file->Get("channel1");
 
  if (w->var("Lumi")!=NULL) { w->var("Lumi")->setConstant(); }

  // set random seed for toy generation
  RooRandom::randomGenerator()->SetSeed(seed);

  //Util::doFreeFit(w);

  // do hypothesis test and get p-value
  LimitResult result = RooStats::get_Pvalue( w, doUL, ntoys, calculatorType, testStatType );
  result.Summary();

  //close the file containing the workspace
  file->Close();
}


