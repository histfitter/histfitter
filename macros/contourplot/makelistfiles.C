
#include "TString.h"

void makelistfiles()
{
  gSystem->Load("libSusyFitter.so");

/*

SoftLeptonMoriond2013_SR1a_StopBCharDeg_20gev_fixSigXSecNominal_hypotest.root
SoftLeptonMoriond2013_SR1b_StopBCharDeg_20gev_fixSigXSecNominal_hypotest.root
SoftLeptonMoriond2013_SR2a_StopBCharDeg_20gev_fixSigXSecNominal_hypotest.root
SoftLeptonMoriond2013_SR2b_StopBCharDeg_20gev_fixSigXSecNominal_hypotest.root
SoftLeptonMoriond2013_SR1a_StopBCharDeg_5gev_fixSigXSecNominal_hypotest.root
SoftLeptonMoriond2013_SR1b_StopBCharDeg_5gev_fixSigXSecNominal_hypotest.root
SoftLeptonMoriond2013_SR2a_StopBCharDeg_5gev_fixSigXSecNominal_hypotest.root
SoftLeptonMoriond2013_SR2b_StopBCharDeg_5gev_fixSigXSecNominal_hypotest.root
*/

  // input root file with HypoTestInverterResults, 
  // as obtained from running: 
  // SusyFitter.py -f python/MySimpleChannelConfig.py
  const char* inputfile  = "~/Work/private/HistFitterUser/MET_jets_leptons/SoftLeptonMoriond2013_SR1a_StopBCharDeg_20gev_fixSigXSecNominal_hypotest.root";
  //const char* inputfile  = "/afs/cern.ch/user/m/mbaak/Work/private/HistFitterUser/MET_jets_leptons/output/Merged_Output_hypotestSoftLeptonMoriond2013_SR2b_StopBCharDeg_5gevfixSigXSecNominal_hypotest.root" ;
  // search for objects labelled
  const char* format     = "hypo_StopBCharDeg_%f_%f_%f";
  // interpret %f's above respectively as (seperated by ':')
  const char* interpretation = "m0:mchi:m12";
  // cut string on m0 and m12 value, eg "m0>1200"
  const char* cutStr = "1"; // accept everything

  TString outputfile;
  format = "hypo_mUED2Lfilter_%f_%f" ;
  interpretation = "m0:m12" ;

  // SoftLeptonMoriond2013_SRs2LmUED2Lfilter__fixSigXSecNominal_hypotest.root
  outputfile = CollectAndWriteHypoTestResults( "~/Work/private/HistFitterUser/MET_jets_leptons/SoftLeptonMoriond2013_SRs2LmUED2Lfilter__fixSigXSecNominal_hypotest.root", format, interpretation, cutStr ) ;

  return;

  outputfile = CollectAndWriteHypoTestResults( "~/Work/private/HistFitterUser/MET_jets_leptons/SoftLeptonMoriond2013_SR1a_StopBCharDeg_20gev_fixSigXSecNominal_hypotest.root", format, interpretation, cutStr ) ;
  outputfile = CollectAndWriteHypoTestResults( "~/Work/private/HistFitterUser/MET_jets_leptons/SoftLeptonMoriond2013_SR1b_StopBCharDeg_20gev_fixSigXSecNominal_hypotest.root", format, interpretation, cutStr ) ;
  outputfile = CollectAndWriteHypoTestResults( "~/Work/private/HistFitterUser/MET_jets_leptons/SoftLeptonMoriond2013_SR2a_StopBCharDeg_20gev_fixSigXSecNominal_hypotest.root", format, interpretation, cutStr ) ;
  outputfile = CollectAndWriteHypoTestResults( "~/Work/private/HistFitterUser/MET_jets_leptons/SoftLeptonMoriond2013_SR2b_StopBCharDeg_20gev_fixSigXSecNominal_hypotest.root", format, interpretation, cutStr ) ;

  outputfile = CollectAndWriteHypoTestResults( "~/Work/private/HistFitterUser/MET_jets_leptons/SoftLeptonMoriond2013_SR1a_StopBCharDeg_5gev_fixSigXSecNominal_hypotest.root", format, interpretation, cutStr ) ;
  outputfile = CollectAndWriteHypoTestResults( "~/Work/private/HistFitterUser/MET_jets_leptons/SoftLeptonMoriond2013_SR1b_StopBCharDeg_5gev_fixSigXSecNominal_hypotest.root", format, interpretation, cutStr ) ;
  outputfile = CollectAndWriteHypoTestResults( "~/Work/private/HistFitterUser/MET_jets_leptons/SoftLeptonMoriond2013_SR2a_StopBCharDeg_5gev_fixSigXSecNominal_hypotest.root", format, interpretation, cutStr ) ;
  outputfile = CollectAndWriteHypoTestResults( "~/Work/private/HistFitterUser/MET_jets_leptons/SoftLeptonMoriond2013_SR2b_StopBCharDeg_5gev_fixSigXSecNominal_hypotest.root", format, interpretation, cutStr ) ;

  // load the listfile in root with:
  // root -l summary_harvest_tree_description.h
  // or look directly at the outputfile in vi.
}

