#ifdef __CINT__

#pragma link off all globals;
#pragma link off all classes;
#pragma link off all functions;

#pragma link C++ nestedclass;

#pragma link C++ class SigmaLR;
#pragma link C++ class Heaviside;
#pragma link C++ class ConfigMgr;
#pragma link C++ class FitConfig;
#pragma link C++ class RooExpandedFitResult;
#pragma link C++ class XtraValues;
#pragma link C++ class TMsgLogger;

#pragma link C++ namespace Util;
#pragma link C++ function Util::GetToyMC;

#pragma link C++ namespace ValidationUtils;
#pragma link C++ function ValidationUtils::PullPlot3;


//////////////////////////////////////
/// Functions from combination package

#pragma link C++ class TEasyFormula ;

#pragma link C++ function GetMCStudy;
#pragma link C++ function GetWorkspaceFromFile;
#pragma link C++ function CollectAndWriteResultSet;

#pragma link C++ namespace StatTools;
#pragma link C++ class StatTools::SRootFinder;
#pragma link C++ function StatTools::GetProbFromSigma;
#pragma link C++ function StatTools::GetSigma;
#pragma link C++ function StatTools::DmLogL_PA ;
#pragma link C++ function StatTools::GetSimpleP1 ;

#pragma link C++ function StatTools::FindS95 ;
#pragma link C++ function StatTools::GetDLL ;
#pragma link C++ function StatTools::FindXS95 ;
#pragma link C++ function StatTools::FindSNSigma ;
#pragma link C++ function StatTools::FindXSNSigma;

#pragma link C++ namespace DrawUtil;
#pragma link C++ function DrawUtil::triwsmooth;
#pragma link C++ function DrawUtil::makesignificancehistos;
#pragma link C++ function DrawUtil::linearsmooth;

#pragma link C++ namespace RooStats;
#pragma link C++ function RooStats::toyMC_gen_fit;
#pragma link C++ function RooStats::DoHypoTestInversion;
#pragma link C++ function RooStats::DoHypoTest;
#pragma link C++ function RooStats::AnalyzeHypoTestInverterResult;
#pragma link C++ function RooStats::get_Pvalue;
#pragma link C++ function RooStats::get_Presult;
#pragma link C++ function RooStats::get_htr;

#pragma link C++ class RooStats::HypoTestTool;

#pragma link C++ class LimitResult;

#endif

