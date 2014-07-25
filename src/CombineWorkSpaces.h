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

std::map<TString,float> ParseWorkspaceID( const TString& wid );


bool MatchingCountingExperiments (    const TString& of,     const TString& opref, 
				      const TString& if1,    const TString& f1,    const TString& i1,
				      const TString& if2,    const TString& f2,    const TString& i2,
				      const TString& if3,    const TString& f3,    const TString& i3,
				      const TString& if4,    const TString& f4,    const TString& i4,
				      const TString& cutStr="1", const Int_t& combinationMode=0, TTree* ORTree=0 );
bool MatchingCountingExperiments (    const TString& of,     const TString& opref,
				      const TString& if1,    const TString& f1,    const TString& i1,
				      const TString& if2,    const TString& f2,    const TString& i2,
				      const TString& if3,    const TString& f3,    const TString& i3,
				      const TString& cutStr="1", const Int_t& combinationMode=0, TTree* ORTree=0 );
bool MatchingCountingExperiments    ( const TString& of,     const TString& opref,
				      const TString& if1,    const TString& f1,    const TString& i1,
				      const TString& if2,    const TString& f2,    const TString& i2,
				      const TString& cutStr="1", const Int_t& combinationMode=0, TTree* ORTree=0 );
bool MatchingCountingExperiments    ( const TString& of,  const TString& opref, 
				      const TString& if1, const TString& f1, const TString& i1, 
				      const TString& cutStr="1" );

bool MatchingCountingExperiments( const TString& of,  const TString& opref,
                             const std::vector<TString>& infile1, const TString& f1,
                             const std::vector<TString>& infile2, const TString& f2,
                             const TString& interpretation, const TString& combineVars="", const TString& cutStr="1" );

bool MatchingCountingExperiments( const TString& of,  const TString& opref,
                             const std::vector<TString>& infile1, const TString& f1,
                             const std::vector<TString>& infile2, const TString& f2,
                             const std::vector<TString>& infile3, const TString& f3,
                             const TString& interpretation, const TString& combineVars="", const TString& cutStr="1" );

bool MatchingCountingExperimentsVec ( const TString& outfile, const TString& outws_prefix,
				      const std::vector<TString>& infile, const std::vector<TString>& format, const std::vector<TString>& interpretation, 
				      const TString& cutStr="1", const Int_t& combinationMode=0, TTree* ORTree=0, const TString& combineVars="" );

RooWorkspace* ConstructCombinedModel(std::vector<RooWorkspace*> chs, const TString& correlateVarsStr="") ;
RooWorkspace* ConstructCombinedModel(RooWorkspace* ws1, const TString& correlateVarsStr="") ;
RooWorkspace* ConstructCombinedModel(RooWorkspace* ws1, RooWorkspace* ws2, const TString& correlateVarsStr="") ;

#endif

