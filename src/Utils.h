#ifndef Utils_hh
#define Utils_hh

#include <map>
#include <vector>
#include <string>
#include "TString.h"
#include "TH1.h"
#include "TH2.h"

#include <iostream>

#include "RooFitResult.h"
#include "RooArgSet.h"
#include "RooArgList.h"

class TMap;
class TTree;

class RooAbsReal;
class RooDataSet;
class RooWorkspace;
class RooRealVar;
class RooAbsPdf;
class RooAbsData;
class RooSimultaneous;
class RooCategory;
class RooPlot;
//class RooFitResult;
class RooMCStudy;
class FitConfig;
class RooProdPdf;
class RooHist;
class RooCurve;

namespace RooStats {
  class HypoTestResult;
  class ModelConfig;
}

namespace Util
{
  double looseToTightVal(const TString& reg, TMap* map);
  double looseToTightErr(const TString& reg, TMap* map);
  double getNonQcdVal(const TString& proc, const TString& reg, TMap* map, const TString& opt);


  RooWorkspace* GetWorkspaceFromFile( const TString& infile, const TString& wsname );
  void WriteWorkspace(RooWorkspace* w, TString outFileName="./results/BkgForumTest_combined_ComHistoSysOverConst_model.root", TString suffix = "");
  void LoadSnapshotInWorkspace(RooWorkspace* w, TString snapshot= "");
  void SaveInitialSnapshot(RooWorkspace* w);
  void ImportInWorkspace( RooWorkspace* wspace, TObject* obj=NULL, TString name="");

  void PlotPdfWithComponents(RooWorkspace* w, TString setupName = "Example3b",TString plotRegions = "ALL", 
			     TString outputPrefix = "", RooFitResult* rFit = NULL, RooAbsData* inputData=0, Bool_t plotRatio=kFALSE );
  void AddComponentsToPlot(RooWorkspace* w,FitConfig* fc, RooPlot* frame, RooAbsPdf* regionPdf, RooAbsData* regionData, RooRealVar* obsRegion, TString regionCatLabel);
  void PlotSeparateComponents(RooWorkspace* w, TString setupName = "Example3b",TString plotRegions = "ALL", 
			      TString outputPrefix = "", RooFitResult* rFit = NULL, RooAbsData* inputData=0 );
  TH2D* PlotCorrelationMatrix(RooFitResult* rFit = NULL);
  TH2D* GetCorrelations(RooFitResult* rFit = NULL, double threshold = 0.9);
  void PlotNLL(RooWorkspace* w, RooFitResult* rFit = NULL,  Bool_t plotPLL = false, TString outputPrefix = "", RooAbsData* inputData=0);
  RooCurve* MakePdfErrorRatioHist(RooWorkspace* w, RooAbsData* regionData, RooAbsPdf* regionPdf, RooRealVar* regionVar, RooFitResult* rFit, Double_t Nsigma = 1.);

  RooFitResult* FitPdf(RooWorkspace* w,  TString fitRegions="ALL", bool lumiConst=false, RooAbsData* inputData=0, TString suffix ="");
  double GetPropagatedError(RooAbsReal* var, const RooFitResult& fr); //, RooArgList varlist=RooArgList() ) ; 

  RooAbsReal* GetComponent(RooWorkspace* w, TString component, TString region);
  RooAbsPdf* GetRegionPdf(RooWorkspace* w, TString region);
  RooRealVar* GetRegionVar(RooWorkspace* w, TString region);

  Double_t GetComponentFrac(RooWorkspace* w, const char* Component, const char* RRSPdf, RooRealVar* observable, RooRealVar* binWidth);
  Double_t GetComponentFracInRegion(RooWorkspace* w, TString component, TString region);
  
  std::vector<TString> GetRegionsVec(TString regions="ALL", RooCategory* regionCat = NULL);
  std::vector<TString> Tokens(TString aline,TString aDelim);
  std::vector<TString> TokensALL(RooCategory* cat);
  
  std::vector<TString> GetAllComponentNamesInRegion(TString region, RooAbsPdf* regionPdf);
  std::vector<double> GetAllComponentFracInRegion(RooWorkspace* w, TString region, RooAbsPdf* regionPdf, RooRealVar* obsRegion, RooRealVar* binWidth);
  
  TString GetFullRegionName(RooCategory* regionCat,  TString regionShortName);
  TString GetShortCompName(TString compName);
  
  void SetPdfParError(RooWorkspace* w, RooAbsPdf* regionPdf, double Nsigma = 0.);

  void ATLASLabel(Double_t x,Double_t y, const char* text=NULL,Color_t color=kBlack) ;
  void AddText(Double_t x,Double_t y,char* text=NULL,Color_t color=kBlack) ;
  
  TString GetXTitle(RooRealVar* regionVar);
  

  /// Functions for toy generation with ToyMCSampler

  RooStats::ModelConfig* GetModelConfig( const RooWorkspace* w, const TString& mcName="ModelConfig", const bool& verbose=true );
  RooFitResult* doFreeFit( RooWorkspace* w, RooDataSet* inputdata=0, const bool& verbose=false, const bool& resetAfterFit=false );
  RooRealVar* GetPOI( const RooWorkspace* w );
  RooMCStudy* GetMCStudy( const RooWorkspace* w );

  RooAbsData* GetToyMC( RooWorkspace* inputws=0 ) ;
  RooAbsData* GetAsimovSet( RooWorkspace* inputws=0 ) ;

  void resetAllErrors( RooWorkspace* wspace );
  void resetError( RooWorkspace* wspace, const RooArgList& parList, const RooArgList& vetoList = RooArgList() ) ;

  RooArgList getFloatParList( const RooAbsPdf& pdf, const RooArgSet& obsSet = RooArgSet() );
  
}

# endif
