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

#ifndef HF_COMBINEWORKSPACES_H
#define HF_COMBINEWORKSPACES_H

// STL include(s):
#include <string>
#include <vector>
#include <map>

// HistFitter include(s)
#include "TString.h"

// -------------------------------
// Combines workspaces
// -------------------------------



class RooWorkspace;
class RooArgSet;
class RooRealVar;
class RooMCStudy;
class TTree;
class RooFitResult;
class TFile;

namespace RooStats {
    class HypoTestInverterResult;
}

namespace hf{

std::map<TString,TString> GetMatchingWorkspaces( const TString& infile, const TString& theformat, const TString& interpretation, const TString& cutStr="1", const Int_t& fID=-1, TTree* ORTree=0 );
std::vector<RooWorkspace*> CollectWorkspaces( const std::map< TString,TString >& fwnameMap, const TString& wid );

void clearVec( std::vector<RooWorkspace*>& wsVec );

RooStats::HypoTestInverterResult* GetHypoTestResultFromFile( TFile* file, const TString& wsname );

RooFitResult* GetFitResultFromFile( TFile* file, const TString& fitname );

RooMCStudy* GetMCStudy( const RooWorkspace* w );

std::map<std::string, float> ParseWorkspaceID( const TString& wid );

}  // namespace hf

#endif  // HF_COMBINEWORKSPACES_H

