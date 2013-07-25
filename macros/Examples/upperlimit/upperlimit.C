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
  int ntoys=20000;
  bool useCLs=true;
  int npoints=30;       // number of points on the signal strength axis.

  // open the workspace
  gSystem->Load("libSusyFitter.so");

  //RooMsgService::instance().setGlobalKillBelow(RooFit::FATAL); // Reduce the noise from RooFit
  //ROOT::Math::MinimizerOptions::SetDefaultMinimizer("Minuit2"); // More stable minimizer - otherwise "Minuit"
  //ROOT::Math::MinimizerOptions::SetDefaultStrategy(0); // Standard default
  //ROOT::Math::MinimizerOptions::SetDefaultPrintLevel(-1); // Quiet please...

  TFile *file = TFile::Open("/afs/cern.ch/work/k/ksuruliz/public/forMax/profiling/Sig_sbottom_650_1_combined_NormalMeasurement_model.root");
  RooWorkspace* w = (RooWorkspace *)file->Get("combined"); 
  
  // set random seed for toy generation
  RooRandom::randomGenerator()->SetSeed(seed);

  // option to turn of the luminosity and signal uncertainty.
  if (true) { 
    w->exportToCint();
    using namespace combined;
    //Lumi.setConstant(); 
    //alpha_syst1.setConstant();
  }

  // determine the upper limit and make a plot
  //RooStats::HypoTestInverterResult* hypo = RooStats::MakeUpperLimitPlot(fileprefix,w,calculatorType,testStatType,ntoys,useCLs,npoints);

  double murangelow = 0;
  double murangehigh = 10.0;
  RooStats::HypoTestInverterResult* hypo = RooStats::DoHypoTestInversion(combined,ntoys,calculatorType,testStatType,true,npoints,murangelow,murangehigh);

  // to reproduce the plot, do:
  RooStats::AnalyzeHypoTestInverterResult(hypo,calculatorType,testStatType,useCLs,npoints);

  delete hypo;
  
  file->Close();
}

