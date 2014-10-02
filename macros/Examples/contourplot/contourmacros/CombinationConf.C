/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Macro  : CombinationConf.C                                                     *
 * Created: 12 June 2012                                                          *
 *                                                                                *
 * Description:                                                                   *
 *      some useful definitions for the contour plots                             *                              
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

// some defintions
#ifndef Combination_CombinationConf
#define Combination_CombinationConf

namespace CombinationConf
{
   // use paper style (plot logo)
   const Bool_t UsePaperStyle = kFALSE;

   // date appears in the logo
   //const TString date = "EPS 09"; 
   const TString date = "Jul 10"; 

   // path of root  files
   const TString path = "../../apps/gsm/data";

   const TString goblique_path = "../../apps/goblique/data";
   const TString gstu_path     = "../../apps/gstu/data";
   
   // experimental SM Higgs limit 
   const Double_t expHiggsLimitLEP = 114.4;
   const Double_t expHiggsLimitMin = 162;
   const Double_t expHiggsLimitMax = 166;

   // --- physical values used in some macros
   const Double_t val_MZ = 91.1875; // Z mass value
   const Double_t err_MZ = 0.0023;  // Z mass error

   const Double_t val_MW = 80.399; // W mass value
   const Double_t err_MW = 0.023;  // W mass error

   const Double_t val_sineff = 0.23153; // sineff value
   const Double_t err_sineff = 0.00016;  // sineff error

   const Double_t val_mt = 173.1;  // top mass value
   const Double_t err_mt = 1.25;    // top mass error
   //const Double_t val_mt = 168.9;  // top mass value
   //const Double_t err_mt = 3.5;    // top mass error

   const Double_t val_DAlphaHad  = 0.02768;  // Delta_Alpha_had
   const Double_t err_DAlphaHad  = 0.00022;  // error

}

#endif
