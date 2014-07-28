// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Namespace: Util                                                                *
 *                                                                                *
 * Description:                                                                   *
 *      Util functions for processing of workspaces and hypotest results          *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *      Lorenzo Moneta, CERN, Geneva  <Lorenzo.Moneta@cern.h>
 *      Wouter Verkerke, Nikhef, Amsterdam <verkerke@nikhef.nl>
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

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
#include "RooExpandedFitResult.h"
#include "ChannelStyle.h"

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
 
  // Functions related to RooWorkspace

  RooWorkspace* GetWorkspaceFromFile( const TString& infile, const TString& wsname );
  void WriteWorkspace(RooWorkspace* w, TString outFileName="./results/BkgForumTest_combined_ComHistoSysOverConst_model.root", TString suffix = "");
  void LoadSnapshotInWorkspace(RooWorkspace* w, TString snapshot= "");
  void SaveInitialSnapshot(RooWorkspace* w);
  void ImportInWorkspace( RooWorkspace* wspace, TObject* obj=NULL, TString name="");

  void DecomposeWS(const char* infile, const char* wsname, const char* outfile);
  void SetPdfParError(RooWorkspace* w, RooAbsPdf* regionPdf, double Nsigma = 0.);

  void resetAllErrors( RooWorkspace* wspace );
  void resetError( RooWorkspace* wspace, const RooArgList& parList, const RooArgList& vetoList = RooArgList() ) ;

  void resetAllValues( RooWorkspace* wspace );
  void resetValue( RooWorkspace* wspace, const RooArgList& parList, const RooArgList& vetoList = RooArgList() ) ;

  void resetAllNominalValues( RooWorkspace* wspace );
  void resetNominalValue( RooWorkspace* wspace, const RooArgSet& globSet ) ;


  // Plotting related functions
  /**
     Top-level C++ side function called from HistFitter.py
     @param fc FitConfig name connected to fit and plot details
     @param anaName Analysis name defined in config file, mainly used for output file/dir naming
     @param drawBeforeFit Boolean deciding whether before-fit plots are produced
     @param drawAfterFit Boolean deciding whether after-fit plots are produced
     @param drawCorrelationMatrix Boolean deciding whether correlation matrix plot is produced
     @param drawSeparateComponents Boolean deciding whether separate component (=sample) plots are produced
     @param drawLogLikelihood Boolean deciding whether log-likelihood plots are produced
     @param minos Boolean deciding whether asymmetric errors are calculated, eg whether MINOS is run
     @param minosPars When minos is called, defining what parameters need asymmetric error calculation
  */  
  void GenerateFitAndPlot(TString fcName, TString anaName, Bool_t drawBeforeFit, Bool_t drawAfterFit, Bool_t plotCorrelationMatrix, Bool_t plotSeparateComponents, Bool_t plotNLL, 
			  Bool_t minos = kFALSE, TString minosPars="");
  
  /**
     Function to plot each region with data, pdf and pdf-components(=samples)  
     @param w RooWorkspace pointer
     @param fcName Fitconfig name as TString, pre-defined in RooWorkspace
     @param anaName Analysis name defined in config file, mainly used for output file/dir naming
     @param plotRegions Regions to be plotted, default = "ALL"
     @param outputPrefix Output prefix, mainly used for TCanvas naming
     @param rFit RooFitResult pointer to plot the propagated uncertainty on the fitted model
     @param inputData RooAbsData pointer pointing to a toy/asimov-dataset, default='' meaning that it takes obsData from RooWorkspace
  */   
  void PlotPdfWithComponents(RooWorkspace* w, TString fcName = "Example3b", TString anaName="Analysis", TString plotRegions = "ALL", 
			     TString outputPrefix = "", RooFitResult* rFit = NULL, RooAbsData* inputData=0);
  /**
     Function to plot each region with data, pdf and pdf-components(=samples) 
     @param w RooWorkspace pointer
     @param fc FitConfig pointer
     @sa PlotPdfWithComponents() 
  */ 
  void PlotPdfWithComponents(RooWorkspace* w, FitConfig* fc,  TString anaName="Analysis", TString plotRegions= "ALL", TString outputPrefix = "", 
			     RooFitResult* rFit= NULL, RooAbsData* inputData=0 );
 
  /**
     Function to add components(=samples) in plot, called for each region in turn
     @param w RooWorkspace pointer
     @param fc FitConfig pointer
     @param frame RooPlot pointer to which the components need to be added to
     @param regionPdf RooAbsPdf pointer to the total-pdf for this specific region
     @param regionData RooAbsData pointer to the data for this region
     @param obsRegion RooRealVar pointer to the observable for this region
     @param regionCatLabel TString that defines this region in simultaneous pdf
     @param style Instance of ChannelStyle class defined for the FitConfig fc, that carries info on plot colors etc
  */
  void AddComponentsToPlot(RooWorkspace* w,FitConfig* fc, RooPlot* frame, RooAbsPdf* regionPdf, RooAbsData* regionData, RooRealVar* obsRegion, TString regionCatLabel, ChannelStyle style);
  
  /**
     Function to plot each component(=sample) separately in each region
     @param w RooWorkspace pointer
     @param fcName Fitconfig name as TString, pre-defined in RooWorkspace
     @param anaName Analysis name defined in config file, mainly used for output file/dir naming
     @param plotRegions Regions to be plotted, default = "ALL"
     @param outputPrefix Output prefix, mainly used for TCanvas naming
     @param rFit RooFitResult pointer to plot the propagated uncertainty on the fitted model
     @param inputData RooAbsData pointer pointing to a toy/asimov-dataset, default='' meaning that it takes obsData from RooWorkspace
  */   
  void PlotSeparateComponents(RooWorkspace* w, TString fcName = "Example3b", TString anaName="Analysis", TString plotRegions = "ALL", 
			      TString outputPrefix = "", RooFitResult* rFit = NULL, RooAbsData* inputData=0 );
  
  /**
     Function to plot correlation matrix
     @param rFit RooFitResult pointer to get the correlation matrix for
     @param anaName Analysis name defined in config file, mainly used for output file/dir naming
  */
  TH2D* PlotCorrelationMatrix(RooFitResult* rFit = NULL, TString anaName="Analysis");

  /**
     Function to scan correlation matrix for high correlations, set by threshhold
     @param rFit RooFitResult pointer to get the correlation matrix for
     @param threshold A double to define the threshold of the scan
     @param anaName Analysis name defined in config file, mainly used for output file/dir naming
  */
  TH2D* GetCorrelations(RooFitResult* rFit = NULL, double threshold = 0.9, TString anaName="Analysis");
 
  /**
     Function to plot log-likelihood (NLL) and profile log-likelihood (PLL)
     @param w RooWorkspace pointer
     @param rFit RooFitResult pointer to get the floating parameters, for which NLL/PLL can be defined
     @param plotPLL Boolean deciding whether PLL is plotted, default=False
     @param anaName Analysis name defined in config file, mainly used for output file/dir naming
     @param outputPrefix Output prefix, mainly used for TCanvas naming
     @param inputData RooAbsData pointer pointing to a toy/asimov-dataset, default='' meaning that it takes obsData from RooWorkspace
     @param plotPars Comma-separated input TString of parameters for which NLL/PLL should be plotted for
     @param fitRegions Comma-separated input TString of regions used for the fit, hence also used to build the NLL/PLL (as also done in FitPdf())
     @param lumiConst Boolean deciding whether "Lumi" parameter (with a special treatment in HistFactory) is to be set constant or not (as also done in FitPdf())
  */
  void PlotNLL(RooWorkspace* w, RooFitResult* rFit = NULL,  Bool_t plotPLL = false, TString anaName="Analysis", TString outputPrefix = "", RooAbsData* inputData=0, TString plotPars="", TString fitRegions="ALL", Bool_t lumiConst=false);

  /**
     Function to construct a band (RooCurve) with the ratio of the nominal pdf curve w.r.t the pdf curve +/- 1 sigma
     @param w RooWorkspace pointer
     @param regionPdf RooAbsPdf pointer to the total-pdf for this specific region
     @param regionData RooAbsData pointer to the data for this region
     @param regionVar RooRealVar pointer to the observable for this region
     @param rFit RooFitResult pointer used to construct +/-1 sigma curves
     @param Nsigma Number of sigmas to be plotted, default= 1.
  */
  RooCurve* MakePdfErrorRatioHist(RooWorkspace* w, RooAbsData* regionData, RooAbsPdf* regionPdf, RooRealVar* regionVar, RooFitResult* rFit, Double_t Nsigma = 1.);

  /**
     Add ATLAS label to plot
   */
  void ATLASLabel(Double_t x,Double_t y, const char* text=NULL,Color_t color=kBlack) ;

  /**
     Add text to plot
   */
  void AddText(Double_t x,Double_t y,char* text=NULL,Color_t color=kBlack) ;
  
  /**
     Get human-readable title for x-axis -- OUTDATED, FIXME
  */
  TString GetXTitle(RooRealVar* regionVar);
  


  // Fitting related functions

  RooFitResult* FitPdf(RooWorkspace* w,  TString fitRegions="ALL", Bool_t lumiConst=false, RooAbsData* inputData=0, TString suffix ="", Bool_t minos = kFALSE, TString minosPars="");
  double GetPropagatedError(RooAbsReal* var, const RooFitResult& fr, const bool& doAsym=false); //, RooArgList varlist=RooArgList() ) ; 
  void RemoveEmptyDataBins(RooWorkspace* w, RooPlot* frame);

  void SetInterpolationCode(RooWorkspace* w, Int_t code);


  // Simultaneous PDF related functions, to decompose PDF

  RooAbsReal* GetComponent(RooWorkspace* w, TString component, TString region, const bool exactRegionName=false, TString rangeName="");
  RooAbsPdf* GetRegionPdf(RooWorkspace* w, TString region);
  RooRealVar* GetRegionVar(RooWorkspace* w, TString region);
  //  RooAbsReal* GetRegionPdfIntegral(RooWorkspace* w, TString region);

  Double_t GetComponentFrac(RooWorkspace* w, const char* Component, const char* RRSPdf, RooRealVar* observable, RooRealVar* binWidth);
  Double_t GetComponentFracInRegion(RooWorkspace* w, TString component, TString region);
  
  std::vector<TString> GetRegionsVec(TString regions="ALL", RooCategory* regionCat = NULL);
  std::vector<TString> GetAllComponentNamesInRegion(TString region, RooAbsPdf* regionPdf);
  std::vector<double> GetAllComponentFracInRegion(RooWorkspace* w, TString region, RooAbsPdf* regionPdf, RooRealVar* obsRegion, RooRealVar* binWidth);
  
  TString GetFullRegionName(RooCategory* regionCat,  TString regionShortName);
  TString GetShortCompName(TString compName);
  

  // Helper functions - to be moved
  double looseToTightVal(const TString& reg, TMap* map);
  double looseToTightErr(const TString& reg, TMap* map);
  double getNonQcdVal(const TString& proc, const TString& reg, TMap* map, const TString& opt);
  
  std::vector<TString> Tokens(TString aline,TString aDelim);
  std::vector<TString> TokensALL(RooCategory* cat);

  TString scanStrForFloats(const TString& toscan, const TString& format);

 
  // Functions for toy generation with ToyMCSampler

  RooStats::ModelConfig* GetModelConfig( const RooWorkspace* w, const TString& mcName="ModelConfig", const bool& verbose=true );
  RooFitResult* doFreeFit( RooWorkspace* w, RooDataSet* inputdata=0, const bool& verbose=false, const bool& resetAfterFit=false, Bool_t minos = kFALSE, TString minosPars="" );
  RooRealVar* GetPOI( const RooWorkspace* w );
  RooMCStudy* GetMCStudy( const RooWorkspace* w );

  RooAbsData* GetToyMC( RooWorkspace* inputws=0 ) ;
  RooAbsData* GetAsimovSet( RooWorkspace* inputws=0 ) ;

  RooArgList getFloatParList( const RooAbsPdf& pdf, const RooArgSet& obsSet = RooArgSet() );

  RooAbsReal* CreateNLL( RooWorkspace* w, TString fitRegions, Bool_t lumiConst=false);

}

# endif
