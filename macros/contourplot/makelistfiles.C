#include "TString.h"

void makelistfiles(const char* inputfile="../../../results/Merged_Output_hypotest.root")
{
  gSystem->Load("libSusyFitter.so");

  // input root file with HypoTestInverterResults, 
  // as obtained from running: 
  // SusyFitter.py -f python/MySimpleChannelConfig.py

  // search for objects labelled
  const char* format     = "hypo_SU_%f_%f";

  // interpret %f's above respectively as (seperated by ':')
  const char* interpretation = "m0:m12";

  // cut string on m0 and m12 value, eg "m0>1200"
  const char* cutStr = "1"; // accept everything

  TString outputfile = CollectAndWriteHypoTestResults( inputfile, format, interpretation, cutStr ) ;

  // load the listfile in root with:
  // root -l summary_harvest_tree_description.h
  // or look directly at the outputfile in vi.
}

