
#include "TString.h"

void makelistfiles(TString inputfile="/atlas_tmp/lungwitz/HypoTests/Merged_Output_hypotest.root")
{
  gSystem->Load("libSusyFitter.so");

  // input root file with HypoTestInverterResults, 
  // as obtained from running: 
  // SusyFitter.py -f python/MySimpleChannelConfig.py
  //const char* inputfile  = "../../test/MySimpleChannelAnalysisOutput_hypotest.root" ;
  //const char* inputfile  = "../../test/2lepSusyFitterAnalysisOutput_hypotest.root";
  // search for objects labelled
  const char* format     = "hypo_SU_%f_%f_0_10";
  //const char* format     =  "hypo_GMSB_3_2d_%f_250_3_%f_1_1";
    // interpret %f's above respectively as (seperated by ':')
  const char* interpretation = "m0:m12";
  // cut string on m0 and m12 value, eg "m0>1200"
  const char* cutStr = "1"; // accept everything

  //TString outputfile = Combination::CollectAndWriteHypoTestResults( inputfile, format, interpretation, cutStr ) ;

   const char* inputfile2  = "../../results/2lepSusyFitterAnalysisOutput_ee_global_allsys_hypotest.root";
   const char* inputfile3  = "../../results/2lepSusyFitterAnalysisOutput_emu_global_allsys_hypotest.root";
   const char* inputfile4  = "../../results/2lepSusyFitterAnalysisOutput_mumu_global_allsys_hypotest.root";
  const char* inputfile5  = "../../results/2lepSusyFitterAnalysisOutput_combined_global_allsys_hypotest.root";
  //  const char* inputfile6 = "../../results/2lepSusyFitterAnalysisOutput_combined_global_allsys_toys_hypotest.root";
  //  const char* inputfile6 = "../../results/SUGRA_hypotests/2lepSusyFitterAnalysisOutput_combined_global_allsys_hypotest.root";
  //  const char* inputfile6 = "../../results/2lepSusyFitterAnalysisOutput_combined_global_allsys_SR4_hypotest.root";
  //  const char* inputfile6 = "../../../results/Combined_KFactorFit_5Channel_hypotest.root";
  //  const char* inputfile6 = "/atlas_tmp/lungwitz/HypoTests_GMSB_combined/Merged_GMSB_combined.root";
  //const char* inputfile6 = "/atlas_tmp/lungwitz/HypoTests/Merged_Output_hypotest.root";
  const char* inputfile6 = inputfile;
//const char* inputfile5  =  "/afs/cern.ch/user/m/matthias/susyoutput/GMSB_hypotestresult.root";
//   const char* inputfile6  = "../../results/2lepSusyFitterAnalysisOutput_added_global_fitsys_hypotest.root";
//    TString outputfile = Combination::CollectAndWriteHypoTestResults( inputfile2, format, interpretation, cutStr ) ;
//    TString outputfile = Combination::CollectAndWriteHypoTestResults( inputfile3, format, interpretation, cutStr ) ;
//    TString outputfile = Combination::CollectAndWriteHypoTestResults( inputfile4, format, interpretation, cutStr ) ;
  //TString outputfile = Combination::CollectAndWriteHypoTestResults( inputfile5, format, interpretation, cutStr ) ;
  TString outputfile = Combination::CollectAndWriteHypoTestResults( inputfile6, format, interpretation, cutStr ) ;
  //  TString outputfile = Combination::CollectAndWriteHypoTestResults( inputfile6, format, interpretation, cutStr ) ;
  // load the listfile in root with:
  // root -l summary_harvest_tree_description.h
  // or look directly at the outputfile in vi.
}

