// vim: ts=4:sw=4
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


