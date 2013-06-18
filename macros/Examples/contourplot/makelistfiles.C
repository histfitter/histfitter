
#include "TString.h"

void makelistfiles()
{
  gSystem->Load("libSusyFitter.so");

  // input root file with HypoTestInverterResults, 
  // as obtained from running: 
  // SusyFitter.py -f python/MySimpleChannelConfig.py
  const char* inputfile  = "SoftLeptonMoriond2013_SRs1L_SM_GG1step_500_400_60_upperlimit.root";
  //const char* inputfile  = "/afs/cern.ch/user/m/mbaak/Work/private/HistFitterUser/MET_jets_leptons/output/Merged_Output_hypotestSoftLeptonMoriond2013_SR2b_StopBCharDeg_5gevfixSigXSecNominal_hypotest.root" ;
  // search for objects labelled
  const char* format     = "hypo_SM_GG1step_%f_%f_%f";
  // interpret %f's above respectively as (seperated by ':')
  const char* interpretation = "m0:mchi:m12";
  // cut string on m0 and m12 value, eg "m0>1200"
  const char* cutStr = "1"; // accept everything

  TString outputfile = CollectAndWriteHypoTestResults( inputfile, format, interpretation, cutStr ) ;

  // load the listfile in root with:
  // root -l summary_harvest_tree_description.h
  // or look directly at the outputfile in vi.
}

