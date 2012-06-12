#include "RooRandom.h"

using namespace RooFit;
using namespace RooStats;

void
pvalue()
{
  int seed=1;            // 0 = cpu clock, so random 
  const char* fileprefix = "example";
  int  calculatorType=0; // 2=asymptotic approximation limit. 0=frequentist limit
  int  testStatType=3;   // one-sided test profile statistic (ATLAS standard)
  int  ntoys=5000;
  bool doUL = true;      // true = exclusion, false = discovery

  // open the workspace
  gSystem->Load("libSusyFitter.so");
  TFile *file = TFile::Open("example_channel1_GaussExample_model.root");
  RooWorkspace* w = (RooWorkspace *)file->Get("channel1"); 
  
  // set random seed for toy generation
  RooRandom::randomGenerator()->SetSeed(seed);

  // do hypothesis test and get p-value
  LimitResult result = RooStats::get_Pvalue( w, doUL, ntoys, calculatorType, testStatType );
  result.Summary();

  file->Close();
}


