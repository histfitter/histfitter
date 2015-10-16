// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Namespace: -                                                                   *
 *                                                                                *
 * Description:                                                                   *
 *      Util functions for processing of workspaces and hypotest results          *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

#ifndef CombineWorkSpaces_hh
#define CombineWorkSpaces_hh

#include "TString.h"
#include <string>
#include <vector>
#include <map>

// -------------------------------
// Combines workspaces 
// -------------------------------

class RooWorkspace;
class RooArgSet;
class RooRealVar;
class RooMCStudy;
class TTree;
class RooFitResult;

namespace RooStats {
    class HypoTestInverterResult;
}

std::map<TString,TString> GetMatchingWorkspaces( const TString& infile, const TString& theformat, const TString& interpretation, const TString& cutStr="1", const Int_t& fID=-1, TTree* ORTree=0 );
std::vector<RooWorkspace*> CollectWorkspaces( const std::map< TString,TString >& fwnameMap, const TString& wid );

void clearVec( std::vector<RooWorkspace*>& wsVec );

RooWorkspace* GetWorkspaceFromFile( const TString& infile, const TString& wsname );

RooStats::HypoTestInverterResult* GetHypoTestResultFromFile( const TString& infile, const TString& wsname );

RooFitResult* GetFitResultFromFile( const TString& infile, const TString& fitname );

RooMCStudy* GetMCStudy( const RooWorkspace* w );

std::map<std::string, float> ParseWorkspaceID( const TString& wid );

#endif

