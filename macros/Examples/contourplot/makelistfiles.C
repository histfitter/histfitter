/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Macro  : makelistfiles.C                                                       *
 * Created: 12 June 2012                                                          *
 *                                                                                *
 * Description:                                                                   *
 *      Convert the root file with hypo test results into a readable 'list' file. *                                                                     *                               
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

#include "TString.h"

/**
Convert the root file with hypo test results into a readable 'list' file.
The name of the file containing the hypo test results needs to be set within the macro.
Also, this file might require adaptions to the specific model to be processed, i.e. the naming convention of that model.
Check the macro for further information.
*/
void makelistfiles()
{
  gSystem->Load("libSusyFitter.so");

  // input root file with HypoTestInverterResults, 
  // as obtained from running: 
  // SusyFitter.py -p python/MySimpleChannelConfig.py
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

