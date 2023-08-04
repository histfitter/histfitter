// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Namespace: -                                                                   *
 *                                                                                *
 * Description:                                                                   *
 *      Utils functions for processing of multiple hypotest results               *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

#ifndef HF_TOYUTILS_H
#define HF_TOYUTILS_H

// STL include(s)
#include <list>
#include <map>

// ROOT include(s)
#include "TString.h"

// HistFitter include(s)
#include "LimitResult.h"

class RooArgSet;
class RooWorkspace;
class RooDataSet;
class RooFitResult;
class RooRealVar;

namespace hf{

LimitResult get_Pvalue( RooWorkspace* w, const int& mode=0, const int& n_toys=10000, const int& do_ul=1, const TString& wid="" );

// run and collect harvest, based on workspace results
std::list<hf::LimitResult> CollectLimitResults( const TString& infile, const TString& format, const TString& interpretation, const TString& cutStr="1", const int& mode=0, const int& n_toys=10000, const int& do_ul=1 );
void WriteResultSetJSON(const std::list<hf::LimitResult>& summary, const TString& listname, const TString& outDir="");
void WriteResultSet(const std::list<hf::LimitResult>& summary, const TString& listname, const TString& outDir="");
void CollectAndWriteResultSet( const TString& infile, const TString& format, const TString& interpretation, const TString& cutStr="1",
        const int& mode=0, const int& par1=100000 /*nexp*/, const int& par2=0 /*nobssigma*/, const int& par3=0,
        const TString& outDir="", const TString& fileprefix="" );

// same, but collect and convert hypotest results
void CollectAndWriteHypoTestResults( const TString& infile, const TString& format, const TString& interpretation, const TString& cutStr="1", const bool rejectFailedPrefit=true, const TString& outDir="", const TString& fileprefix="" );
std::list<hf::LimitResult> CollectHypoTestResults( const TString& infile, const TString& format, const TString& interpretation, const TString& cutStr="1", const bool& rejectFailedPrefit=true );

}  // namespace hf

#endif  // HF_TOYUTILS_H
