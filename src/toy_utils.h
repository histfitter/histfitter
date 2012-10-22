// vim: ts=4:sw=4
#ifndef toy_utilsDEF
#define toy_utilsDEF 

#include "TString.h"
#include "LimitResult.h"
#include <list>
#include <map>

class RooArgSet;
class RooWorkspace;
class RooDataSet;
class RooFitResult;
class RooRealVar;

LimitResult get_Pvalue( RooWorkspace* w, const int& mode=0, const int& n_toys=10000, const int& do_ul=1, const TString& wid="" );

// run and collect harvest, based on workspace results
std::list<LimitResult> CollectLimitResults( const TString& infile, const TString& format, const TString& interpretation, const TString& cutStr="1", const int& mode=0, const int& n_toys=10000, const int& do_ul=1 );
const char* WriteResultSet(const std::list<LimitResult>& summary, const TString& listname, const TString& outDir="./");
const char* CollectAndWriteResultSet( const TString& infile, const TString& format, const TString& interpretation, const TString& cutStr="1", 
        const int& mode=0, const int& par1=100000 /*nexp*/, const int& par2=0 /*nobssigma*/, const int& par3=0, 
        const TString& outDir="./", const TString& fileprefix="" );

// same, but collect and convert hypotest results
const char* CollectAndWriteHypoTestResults( const TString& infile, const TString& format, const TString& interpretation, const TString& cutStr="1", const TString& outDir="./", const TString& fileprefix="" );
std::list<LimitResult> CollectHypoTestResults( const TString& infile, const TString& format, const TString& interpretation, const TString& cutStr="1" );


#endif
