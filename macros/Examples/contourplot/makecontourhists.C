/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Macro  : makecontourhists.C                                                    *
 * Created: 12 June 2012                                                          *
 *                                                                                *
 * Description:                                                                   *
 *      make contour histograms based on the list text files produced by          *
 *      makelistfiles                                                             *                              
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/


#include "contourmacros/m0_vs_m12_nofloat.C"

/**
make contour histograms based on the list text files produced by makelistfiles.C
The name of the file containing this list needs to be set within the macro.
The macro calls contourmacros/m0_vs_m12_nofloat.C
*/
void makecontourhists() 
{
  const char* ehistfile = m0_vs_m12_nofloat("MySimpleChannelAnalysis_fixSigXSecNominal_hypotest__1_harvest_list"); 
}



