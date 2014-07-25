// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : RooExpandedFitResult                                                  *
 *                                                                                *
 * Description:                                                                   *
 *      Class derived from RooFitResult, to be able to add more parameters        *
 *      for error propagation (calculation & visualization)                       *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

#ifndef ROOEXPANDEDFITRESULT_H
#define ROOEXPANDEDFITRESULT_H

#include "TString.h"
#include "RooFitResult.h"
#include "RooArgList.h"

#include <iostream>
#include <vector>

class RooExpandedFitResult: public RooFitResult{

    public:
        RooExpandedFitResult(RooFitResult* origResult, RooArgList extraPars);
        RooExpandedFitResult(RooArgList extraPars);

        ~RooExpandedFitResult(){}

        ClassDef(RooExpandedFitResult,1) // Container class for expanded fit result
};

#endif
