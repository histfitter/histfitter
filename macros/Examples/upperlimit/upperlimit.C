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
  int ntoys=2500;
  bool useCLs=true;
  int npoints=20;       // number of points on the signal strength axis.

  // open the workspace
  gSystem->Load("libSusyFitter.so");
  TFile *file = TFile::Open("../../../results/statsys.root");
  RooWorkspace* w = (RooWorkspace *)file->Get("combined"); 
  
  // set random seed for toy generation
  RooRandom::randomGenerator()->SetSeed(seed);

  // option to turn of the luminosity and signal uncertainty.
  if (false) { 
    w->exportToCint();
    using namespace combined;
    Lumi.setConstant(); 
    alpha_SigXSec.setConstant();
  }

  // determine the upper limit and make a plot
  RooStats::HypoTestInverterResult* hypo = RooStats::MakeUpperLimitPlot(fileprefix,w,calculatorType,testStatType,ntoys,useCLs,npoints);

  // to reproduce the plot, do:
  //RooStats::AnalyzeHypoTestInverterResult(hypo,calculatorType,testStatType,useCLs,npoints);

  delete hypo;
  
  file->Close();
}

