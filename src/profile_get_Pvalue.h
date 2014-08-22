// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 *                                                                                *
 * Description:                                                                   *
 *             Functions to call a profile likelihood fit return p-values         *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

#ifndef profile_get_PvalueDEF
#define profile_get_PvalueDEF 

#include "TString.h"
#include "LimitResult.h"

class RooWorkspace;
class RooDataSet;
class RooFitResult;

// make a profile likelihood fit and return the p values using wilck's theorem
void doFreeFit( const RooWorkspace* fullwspace, RooDataSet* inputdata=0, bool verbose=false );
RooFitResult* doFreeFitSave( const RooWorkspace* fullwspace, RooDataSet* inputdata=0, bool verbose=false );

#endif


