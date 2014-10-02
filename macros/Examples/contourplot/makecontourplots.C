/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Macro  : makecontourplots.C                                                    *
 * Created: 12 June 2012                                                          *
 *                                                                                *
 * Description:                                                                   *
 *      make final plots based on histograms obtained from makecontourhists.C     *                      
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

#include "contourmacros/SUSY_m0_vs_m12_all_withBand_cls.C"

/**
Make final plots based on histograms obtained from makecontourhists.C
The macro calls contourmacros/SUSY_m0_vs_m12_all_withBand_cls.C
*/
void makecontourplots() 
{ 
  //various settings
  bool showsignal(false);
  int  discexcl; // 0=discovery, 1=exclusion
  bool showtevatron(true);
  bool showcms(false);
  bool doOneSigmaBand(true);
  bool showfixSigXSecBand(true);
  int applyfix(0);

  // simple channel contour plot
  SUSY_m0_vs_m12_all_withBand_cls("MySimpleChannelAnalysis_fixSigXSecNominal_hypotest__1_harvest_list.root","MySimpleChannelAnalysis_fixSigXSecUp_hypotest__1_harvest_list.root","MySimpleChannelAnalysis_fixSigXSecDown_hypotest__1_harvest_list.root", "", "Tutorial contour", 4.7, showsignal, discexcl=1, showtevatron, showcms, doOneSigmaBand, showfixSigXSecBand, channel=2 );

}

