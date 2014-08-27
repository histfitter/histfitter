
#include "TString.h"

void makelistfiles()
{
  gSystem->Load("libSusyFitter.so");

  // input root file with HypoTestInverterResults, 
  // as obtained from running: 
  // SusyFitter.py -f python/MySimpleChannelConfig.py
  const char* inputfile  = "$HISTFITTER/results/MySimpleChannelAnalysis_fixSigXSecNominal_hypotest.root"; //MySimpleChannelAnalysisOutput_hypotest.root" ;
  // search for objects labelled
  const char* format     = "hypo_SU_%f_%f_0_10";
  // interpret %f's above respectively as two variables of interest (separated by ':')
  const char* interpretation = "m0:m12";
  // cut string on m0 and m12 value, eg "m0>1200"
  const char* cutStr = "1"; // accept everything

  //  TString outputfile = Combination::CollectAndWriteHypoTestResults( inputfile, format, interpretation, cutStr ) ;
  TString outputfile = CollectAndWriteHypoTestResults( inputfile, format, interpretation, cutStr ) ;

  // load the listfile in root with:
  // root -l summary_harvest_tree_description.h
  // or look directly at the outputfile in vi.
}

