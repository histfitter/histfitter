
#include "TString.h"

void makelistfiles_SM()
{
  gSystem->Load("libSusyFitter.so");

  // input root file with HypoTestInverterResults, 
  // as obtained from running: 
  // SusyFitter.py -f python/MySimpleChannelConfig.py
  //const char* inputfile  = "../../results/MySimpleChannelAnalysisOutput_hypotest.root" ;
  //const char* inputfile  = "../../results/MySoftOneLeptonKtScaleFitMeffR17_Output_hypotest.root" ;
  //const char* inputfile  = "../../results/MySoftOneLeptonKtScaleFitMeffR17_Output_hypotest.root" ;
  const char* inputfile  = "../../results/MySoftOneLeptonKtScaleFitMetMeff_SM_GG_onestepCC_R17_Output_upperlimit.root" ;
  // search for objects labelled
  //  const char* format     = "hypo_SU_%f_%f_0_10";
  //hypo_SM_GG_onestepCC_985_945_905
  const char* format     = "hypo_SM_GG_onestepCC_%f_%f_%f";
  // interpret %f's above respectively as (seperated by ':')
  const char* interpretation = "m0:mc:m12";
  // cut string on m0 and m12 value, eg "m0>1200"
  const char* cutStr = "1"; // accept everything

  TString outputfile = Combination::CollectAndWriteHypoTestResults( inputfile, format, interpretation, cutStr );

  // load the listfile in root with:
  // root -l summary_harvest_tree_description.h
  // or look directly at the outputfile in vi.
}

