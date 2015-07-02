#ifdef __CLING__

#pragma link off all globals;
#pragma link off all classes;
#pragma link off all functions;

#pragma link C++ nestedclass;

#pragma link C++ class ConfigMgr;
#pragma link C++ class FitConfig;
#pragma link C++ class RooExpandedFitResult;
#pragma link C++ class XtraValues;
#pragma link C++ class TMsgLogger;

#pragma link C++ namespace Util;
#pragma link C++ function Util::GetToyMC;

#pragma link C++ namespace ValidationUtils;
#pragma link C++ function ValidationUtils::PullPlot3;

#pragma link C++ class ChannelStyle;
#pragma link C++ class std::vector<ChannelStyle>;
#pragma link C++ class vector<ChannelStyle>::iterator;

//////////////////////////////////////
/// Functions from combination package

// up to 'namespace StatTools', these were previously included
// by including the entire (now dropped) Combination namespace

//CombinationUtils.cxx
#pragma link C++ function resetFloatPars;

//CombineWorkSpaces.cxx
#pragma link C++ function clearVec;
#pragma link C++ function CollectWorkspaces;
#pragma link C++ function GetMatchingWorkspaces;
#pragma link C++ function GetWorkspaceFromFile;
#pragma link C++ function GetHypoTestResultFromFile;
#pragma link C++ function GetFitResultFromFile;
#pragma link C++ function GetMCStudy;
#pragma link C++ function ParseWorkspaceID;

//TEasyFormula.cxx
#pragma link C++ class TEasyFormula ;

//TMsgLogger.cxx
#pragma link C++ class TMsgLogger;

//toy_utils.cxx
#pragma link C++ function get_Pvalue;
#pragma link C++ function CollectLimitResults;
#pragma link C++ function WriteResultSet;
#pragma link C++ function CollectAndWriteResultSet;
#pragma link C++ function CollectAndWriteHypoTestResults;
#pragma link C++ function CollectHypoTestResults;

#pragma link C++ namespace StatTools;
#pragma link C++ function StatTools::GetProbFromSigma;
#pragma link C++ function StatTools::GetSigma;
#pragma link C++ function StatTools::DmLogL_PA ;
#pragma link C++ function StatTools::GetSimpleP1 ;

#pragma link C++ function StatTools::FindS95 ;
#pragma link C++ function StatTools::GetDLL ;
#pragma link C++ function StatTools::FindXS95 ;
#pragma link C++ function StatTools::FindSNSigma ;
#pragma link C++ function StatTools::FindXSNSigma;

//json.cxx
#pragma link C++ class JSON;
#pragma link C++ class JSONException;

//DrawUtils.cxx
#pragma link C++ namespace DrawUtil;
#pragma link C++ function DrawUtil::triwsmooth;
#pragma link C++ function DrawUtil::makesignificancehistos;
#pragma link C++ function DrawUtil::linearsmooth;

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

#pragma link C++ class LimitResult;

#endif

