/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Macro  : upperlimit.C                                                          *
 * Created: 12 June 2012                                                          *
 *                                                                                *
 * Description:                                                                   *
 *      Calculates the upper limit for the "simple channel" workspcaes taken      *
 *      from HistFitter/analysis/simplechannel/README and produces an upper limit *
 *      plot                                                                      *                               
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

#include "RooRandom.h"

using namespace RooFit;
using namespace RooStats;

/**
1. Execute:
root -b -q upperlimit.C

... to produce a nice upper limit plot based on the "simple channel" workspace taken from :
HistFitter/analysis/simplechannel/README

2. This produces two files:
The plot: upperlimit_cls_poi_example_Asym_CLs_grid_ts3.root.eps
The hypothesis test results that can be used to recreate the plot:
example_Asym_CLs_grid_ts3.root

3. Run the macro with:

int calculatorType=2;  // frequentist
int npoints=6; 

and again:

root -l upperlimit.C

to see the actual test statistic distributions used to determine the upper limit!
*/
void
upperlimit()
{
  int seed=1;           // 0 = cpu clock, so random 
  const char* fileprefix = "example";
  int calculatorType=2; // 2=asymptotic limit. 0=frequentist
  int testStatType=3;   // one-sided test profile statistic
  int ntoys=5000;
  bool useCLs=true;
  int npoints=20;       // number of points on the signal strength axis.

  // open the workspace
  gSystem->Load("libHistFitter.so");

  RooMsgService::instance().setGlobalKillBelow(RooFit::FATAL); // Reduce the noise from RooFit
  ROOT::Math::MinimizerOptions::SetDefaultMinimizer("Minuit2"); // More stable minimizer - otherwise "Minuit"
  ROOT::Math::MinimizerOptions::SetDefaultStrategy(0); // Standard default
  ROOT::Math::MinimizerOptions::SetDefaultPrintLevel(-1); // Quiet please...

  TFile *file = TFile::Open("example_channel1_GaussExample_model.root");
  RooWorkspace* w = (RooWorkspace *)file->Get("channel1"); 
  
  // set random seed for toy generation
  RooRandom::randomGenerator()->SetSeed(seed);

  // option to turn off the luminosity and signal uncertainty.
  //  if (false) { 
  //    w->exportToCint();
  //    using namespace channel1;
  //    Lumi.setConstant(); 
  //    alpha_syst1.setConstant();
  //  }

  // compute p-value
  LimitResult result = RooStats::get_Pvalue( w, useCLs, ntoys, calculatorType, testStatType );

  // determine the upper limit and make a plot
  RooStats::HypoTestInverterResult* hypo = RooStats::MakeUpperLimitPlot(fileprefix,w,calculatorType,testStatType,ntoys,useCLs,npoints);

  // to reproduce the plot, do:
  //RooStats::AnalyzeHypoTestInverterResult(hypo,calculatorType,testStatType,useCLs,npoints);

  delete hypo;
  
  file->Close();
}

