/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Creation: March 2012, Alex Koutsman (CERN/TRIUMF)                               //
// Class derived from RooFitResult, to be able to add more parameters       //
//    for error propagation (calculation & visualization)                                   //
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#ifndef EXPANDEDROOFITRESULT_H
#define EXPANDEDROOFITRESULT_H

#include "TString.h"
#include "RooFitResult.h"
#include "RooArgList.h"

#include <iostream>
#include <vector>

class ExpandedRooFitResult: public RooFitResult{
 
 public:
  // ExpandedRooFitResult();
  ExpandedRooFitResult(RooFitResult* origResult, RooArgList extraPars);
  ExpandedRooFitResult(RooArgList extraPars);
  
  ~ExpandedRooFitResult(){}
  
  ClassDef(ExpandedRooFitResult,1) // Container class for fit result
};

#endif
