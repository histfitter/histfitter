#ifndef HF_LINKDEF_H
#define HF_LINKDEF_H


#ifdef __CLING__

#pragma link off all globals;
#pragma link off all classes;
#pragma link off all functions;
#pragma link off all namespaces;

#pragma link C++ nestedclass;
#pragma link C++ nestedtypedef;

//#pragma link C++ namespace hf::TMsgLogger;
//#pragma link C++ namespace hf
#pragma link C++ class hf::TMsgLogger+;
#pragma link C++ class hf::ConfigMgr+;
#pragma link C++ class hf::FitConfig+;
#pragma link C++ class hf::RooExpandedFitResult+;
#pragma link C++ class hf::XtraValues+;

//#pragma link C++ TMsgLogger hf::TMsgLogger;

#pragma link C++ namespace hf::Util+;
#pragma link C++ function hf::Util::GetToyMC+;

#pragma link C++ namespace hf::ValidationUtils+;
#pragma link C++ function hf::ValidationUtils::PullPlot3+;

#pragma link C++ class hf::ChannelStyle+;
#pragma link C++ class std::vector<hf::ChannelStyle>+;
#pragma link C++ class vector<hf::ChannelStyle>::iterator+;

//////////////////////////////////////
/// Functions from combination package

// up to 'namespace StatTools', these were previously included
// by including the entire (now dropped) Combination namespace

//CombinationUtils.cxx
#pragma link C++ function hf::resetFloatPars;

//CombineWorkSpaces.cxx

//#pragma link C++ function clearVec;
//#pragma link C++ function CollectWorkspaces;
//pragma link C++ function GetMatchingWorkspaces;
//#pragma link C++ function GetWorkspaceFromFile;
//#pragma link C++ function GetHypoTestResultFromFile;
//#pragma link C++ function GetFitResultFromFile;
//#pragma link C++ function GetMCStudy;
//#pragma link C++ function ParseWorkspaceID;

#pragma link C++ defined_in "../hf/CombineWorkSpaces.h";

//TEasyFormula.cxx
#pragma link C++ class hf::TEasyFormula ;

//TMsgLogger.cxx
#pragma link C++ class hf::TMsgLogger;

//toy_utils.cxx
#pragma link C++ function hf::get_Pvalue;
#pragma link C++ function hf::CollectLimitResults;
#pragma link C++ function hf::WriteResultSet;
#pragma link C++ function hf::CollectAndWriteResultSet;
#pragma link C++ function hf::CollectAndWriteHypoTestResults;
#pragma link C++ function hf::CollectHypoTestResults;

//StatTools namespace is in Significance.h
#pragma link C++ namespace hf::StatTools;
#pragma link C++ function hf::StatTools::GetProbFromSigma;
#pragma link C++ function hf::StatTools::GetSigma;
#pragma link C++ function hf::StatTools::DmLogL_PA ;
#pragma link C++ function hf::StatTools::GetSimpleP1 ;

#pragma link C++ function hf::StatTools::FindS95 ;
#pragma link C++ function hf::StatTools::GetDLL ;
#pragma link C++ function hf::StatTools::FindXS95 ;
#pragma link C++ function hf::StatTools::FindSNSigma ;
#pragma link C++ function hf::StatTools::FindXSNSigma;

//json.cxx
#pragma link C++ class JSON;
#pragma link C++ class JSONException;

//DrawUtils.cxx
#pragma link C++ namespace hf::DrawUtil;
#pragma link C++ function hf::DrawUtil::triwsmooth;
#pragma link C++ function hf::DrawUtil::makesignificancehistos;
#pragma link C++ function hf::DrawUtil::linearsmooth;

//StatTools.cxx
#pragma link C++ namespace RooStats;
#pragma link C++ function RooStats::toyMC_gen_fit;
#pragma link C++ function RooStats::DoHypoTestInversion;
#pragma link C++ function RooStats::DoHypoTest;
#pragma link C++ function RooStats::AnalyzeHypoTestInverterResult;
#pragma link C++ function RooStats::get_Pvalue;
#pragma link C++ function RooStats::get_Presult;
#pragma link C++ function RooStats::get_htr;

//HypoTestTool.cxx
#pragma link C++ class RooStats::HypoTestTool;
#pragma link C++ class hf::LimitResult;

#endif // __CINT__
#endif // not HF_LINKDEF_H
