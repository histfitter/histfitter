#include "RooRandom.h"

using namespace RooFit;
using namespace RooStats;

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
  gSystem->Load("libSusyFitter.so");

  RooMsgService::instance().setGlobalKillBelow(RooFit::FATAL); // Reduce the noise from RooFit
  ROOT::Math::MinimizerOptions::SetDefaultMinimizer("Minuit2"); // More stable minimizer - otherwise "Minuit"
  ROOT::Math::MinimizerOptions::SetDefaultStrategy(0); // Standard default
  ROOT::Math::MinimizerOptions::SetDefaultPrintLevel(-1); // Quiet please...

  TFile *file = TFile::Open("example_channel1_GaussExample_model.root");
  RooWorkspace* w = (RooWorkspace *)file->Get("channel1"); 
  
  // set random seed for toy generation
  RooRandom::randomGenerator()->SetSeed(seed);

  // option to turn off the luminosity and signal uncertainty.
  if (false) { 
    w->exportToCint();
    using namespace channel1;
    Lumi.setConstant(); 
    alpha_syst1.setConstant();
  }

  // determine the upper limit and make a plot
  RooStats::HypoTestInverterResult* hypo = RooStats::MakeUpperLimitPlot(fileprefix,w,calculatorType,testStatType,ntoys,useCLs,npoints);

  // to reproduce the plot, do:
  //RooStats::AnalyzeHypoTestInverterResult(hypo,calculatorType,testStatType,useCLs,npoints);

  delete hypo;
  
  file->Close();
}

