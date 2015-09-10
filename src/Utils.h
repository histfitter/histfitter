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
 *      Lorenzo Moneta, CERN, Geneva  <Lorenzo.Moneta@cern.h>                     *
 *      Wouter Verkerke, Nikhef, Amsterdam <verkerke@nikhef.nl>                   *
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
#include "TFile.h"
#include "TGraphAsymmErrors.h"

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
  /**
     Get RooWorkspace from file
  */
  RooWorkspace* GetWorkspaceFromFile( const TString& infile, const TString& wsname );
  /**
     Wrute RooWorkspace to file
  */ 
  void WriteWorkspace(RooWorkspace* w, TString outFileName="./results/BkgForumTest_combined_ComHistoSysOverConst_model.root", TString suffix = "");
  /**
     Load snapshot
  */
  void LoadSnapshotInWorkspace(RooWorkspace* w, TString snapshot= "");
  /**
     Save initial snapshot of workspace
  */
  void SaveInitialSnapshot(RooWorkspace* w);
  /**
     Import object (typically RooFitResult) into workspace and save snapshot associated to this object
  */
  void ImportInWorkspace( RooWorkspace* wspace, TObject* obj=NULL, TString name="");

  /**
    Decompose RooWorkspace into a separate object for each region, mainly decomposing simultaneous PDF/data 
  */
  void DecomposeWS(const char* infile, const char* wsname, const char* outfile);
  
  /**
     Reset errors of all (nuisance/normalization) parameters in RooWorkspace to 'natural' values
  */
  void resetAllErrors( RooWorkspace* wspace );
  /**
    Find the input parameter (systematic) with the given name and shift that parameter (systematic) by 1-sigma if given; otherwise set error to small number
  */
  void resetError( RooWorkspace* wspace, const RooArgList& parList, const RooArgList& vetoList = RooArgList() ) ;

  /**
     Set all parameter values to initial values
  */
  void resetAllValues( RooWorkspace* wspace );
  /**
     Set  parameter value to initial value
  */
  void resetValue( RooWorkspace* wspace, const RooArgList& parList, const RooArgList& vetoList = RooArgList() ) ;

  /**
     Set all parameter values to nominal values -- FIXME (same functionality as resetAllValues()?)
  */
  void resetAllNominalValues( RooWorkspace* wspace );
  /**
     Set parameters values to nominal values -- FIXME (same functionality as resetValue()?)
  */
  void resetNominalValue( RooWorkspace* wspace, const RooArgSet& globSet ) ;
  /**
     Set parameter to value at nominal value + Nsigma * parameter error
  */
  void SetPdfParError(RooWorkspace* w, double Nsigma = 0.);
  /**
     Get list of floating parameters associated to given pdf
  */
  RooArgList getFloatParList( const RooAbsPdf& pdf, const RooArgSet& obsSet = RooArgSet() );


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
     @param doFixParameters Boolean deciding if some parameters are fixed to a value given or not, default=kFALSE
     @param fixedPars String of parameter1:value1,parameter2:value2 giving information on which parameter to fix to which value if dofixParameter == kTRUE, default='' 
  */  
  void GenerateFitAndPlot(TString fcName, TString anaName, Bool_t drawBeforeFit, Bool_t drawAfterFit, Bool_t plotCorrelationMatrix, 
			  Bool_t plotSeparateComponents, Bool_t plotNLL,  Bool_t minos = kFALSE, TString minosPars="", Bool_t doFixParameters = kFALSE, TString fixedPars="", bool ReduceCorrMatrix = true);
  
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
     @param obsRegion RooRealVar pointer to the observable for this region
     @param regionCatLabel TString that defines this region in simultaneous pdf
     @param style Instance of ChannelStyle class defined for the FitConfig fc, that carries info on plot colors etc
  */
  void AddComponentsToPlot(RooWorkspace* w,FitConfig* fc, RooPlot* frame, RooAbsPdf* regionPdf, 
			   RooRealVar* obsRegion, TString regionCatLabel, ChannelStyle style);
  
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
  TH2D* PlotCorrelationMatrix(RooFitResult* rFit = NULL, TString anaName="Analysis", bool ReduceMatrix = true);

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
  void PlotNLL(RooWorkspace* w, RooFitResult* rFit = NULL,  Bool_t plotPLL = false, TString anaName="Analysis", 
	       TString outputPrefix = "", RooAbsData* inputData=0, TString plotPars="", TString fitRegions="ALL", Bool_t lumiConst=false);
  
  /**
     Function to construct a band (RooCurve) with the ratio of the nominal pdf curve w.r.t the pdf curve +/- 1 sigma
     @param regionPdf RooAbsPdf pointer to the total-pdf for this specific region
     @param regionData RooAbsData pointer to the data for this region
     @param regionVar RooRealVar pointer to the observable for this region
     @param rFit RooFitResult pointer used to construct +/-1 sigma curves
     @param Nsigma Number of sigmas to be plotted, default= 1.
  */
  RooCurve* MakePdfErrorRatioHist(RooAbsData* regionData, RooAbsPdf* regionPdf, 
				  RooRealVar* regionVar, RooFitResult* rFit, Double_t Nsigma = 1.);

  /**
     Add ATLAS label to plot
     # ATLAS specific - FIXME ; remove for public release

  */
  void ATLASLabel(Double_t x,Double_t y, const char* text=NULL,Color_t color=kBlack) ;
  
  /**
     Add text to plot
  */
  void AddText(Double_t x,Double_t y,char* text=NULL,Color_t color=kBlack) ;
  
  /**
     Remove empty bins for data (otherwise a Poisson error on 0 observed events is shown)
     @param frame RooPlot pointer for the frame that needs removing the empty bins
  */
  void RemoveEmptyDataBins(RooPlot* frame);
  

  // Fitting related functions
  /**
     Function to fit PDF using regions given
     @param w RooWorkspace pointer
     @param fitRegions Comma-separated input TString of regions to be used for the fit, default="ALL" meaning all regions/channel in pdf
     @param lumiConst Boolean deciding whether "Lumi" parameter (with a special treatment in HistFactory) is to be set constant or not
     @param inputData RooAbsData pointer pointing to a toy/asimov-dataset, default='' meaning that it takes obsData from RooWorkspace
     @param suffix Output prefix, used for RooFitResult naming
     @param minos Boolean deciding whether asymmetric errors are calculated, eg whether MINOS is run, default=kFALSE
     @param minosPars When minos is called, defining what parameters need asymmetric error calculation, default=''
     @param doFixParameters Boolean deciding if some parameters are fixed to a value given or not, default=kFalse
     @param fixedPars String of parameter1:value1,parameter2:value2 giving information on which parameter to fix to which value if dofixParameter == kTrue, default=''    
     @return RooFitResult pointer continaing the fit result
  */
  RooFitResult* FitPdf(RooWorkspace* w,  TString fitRegions="ALL", Bool_t lumiConst=false, RooAbsData* inputData=0, 
		       TString suffix ="", Bool_t minos = kFALSE, TString minosPars="", Bool_t doFixParameters = kFALSE, TString fixedPars="");

  /**
     Function to calculate the propagated error of given RooAbsReal
     @param var RooAbsReal pointer for the object that the error gets calculated for
     @param fr const RooFitResult reference used contaning the fit result and covariance matrix used for error propagation
     @param doAsym Boolean deciding whether asymmetric (MINOS) errors on parameters get used in an averaged approximation
     @return Returns the propagated error
  */
  double GetPropagatedError(RooAbsReal* var, const RooFitResult& fr, const bool& doAsym=false); 
  
  /**
     Sets interpolation code  
     @param w RooWorkspace pointer
     @param code Typicaly set to code = 4, meaning parabolic interpolation (default now in RooStats). This avoids kinks in the likelihood curve. 
   */
  void SetInterpolationCode(RooWorkspace* w, Int_t code);
  /**
     Get RooStats::ModelConfig out of RooWorkspace
     @param w RooWorkspace pointer
     @param mcName Optional name of ModelConfig, default='ModelConfig'
     @return RooStats::ModelConfig pointer
  */
  RooStats::ModelConfig* GetModelConfig( const RooWorkspace* w, const TString& mcName="ModelConfig");
  /**
     Create log-likelihood (NLL) from workspace and fit-regions given
     @param w RooWorkspace pointer
     @param fitRegions Comma-separated input TString of regions to be used for the fit
     @param lumiConst Boolean deciding whether "Lumi" parameter (with a special treatment in HistFactory) is to be set constant or not
     @return RooAbsReal pointer to log-likelihood
  */
  RooAbsReal* CreateNLL( RooWorkspace* w, TString fitRegions, Bool_t lumiConst=false);
  /**
     Perform fit using PDF/data as stored in ModelCOnfig inside the workspace
     @param w RooWorkspace pointer
     @param inputData RooAbsData pointer pointing to a toy/asimov-dataset, default='' meaning that it takes obsData from RooWorkspace
     @param verbose Boolean deciding whether addiotional print out info is given, default=false
     @param resetAfterFit Boolean deciding whether the workspace parameters are set back to initial values after fit is performed, default=false
     @param hesse Boolean deciding whether to run HESSE or not; default=false
     @param minos Boolean deciding whether asymmetric errors are calculated, eg whether MINOS is run, default=kFALSE
     @param minosPars When minos is called, defining what parameters need asymmetric error calculation, default=''
     @return RooFitResult pointer to fit result 
  */
  RooFitResult* doFreeFit( RooWorkspace* w, RooDataSet* inputdata=0, const bool& verbose=false, 
			   const bool& resetAfterFit=false, bool hesse=false, Bool_t minos = kFALSE, TString minosPars="" );
  /**
     Get asimovData dataset from workspace
  */
  RooAbsData* GetAsimovSet( RooWorkspace* inputws=0 ) ;
  /**
     Generate and return a toyMC set based on the PDF/obsData contained in ModelConfig in workspace. Number of generated events is equal to number of events in obsData.
  */
  RooAbsData* GetToyMC( RooWorkspace* inputws=0 ) ;
  
 
  
  // Simultaneous PDF related functions, to (de)compose PDF and PDF components
  /**
     Get component (sample or mutiple samples as comma-separated string) in region.
     Returns the integral of recomposed RooRealSumPdf (top-level region PDF in HistFactory); only in a specific range, if rangeName is given. 
  */
  RooAbsReal* GetComponent(RooWorkspace* w, TString component, TString region, const bool exactRegionName=false, TString rangeName="");
  /**
     Get PDF in region
  */
  RooAbsPdf* GetRegionPdf(RooWorkspace* w, TString region);
  /**
     Get observable in region
  */
  RooRealVar* GetRegionVar(RooWorkspace* w, TString region);

  /**
     Get component (sample or multiple sample) fraction, called by  GetComponentFracInRegion()
  */
  Double_t GetComponentFrac(RooWorkspace* w, const char* Component, const char* RRSPdf, RooRealVar* observable, RooRealVar* binWidth);
  /**
     Get component (sample or multiple samples) fraction in region
  */
  Double_t GetComponentFracInRegion(RooWorkspace* w, TString component, TString region);
  
  /**
     Get a vector of region names
  */
  std::vector<TString> GetRegionsVec(TString regions="ALL", RooCategory* regionCat = NULL);
  /**
     Get all component (sample) names in region
  */
  std::vector<TString> GetAllComponentNamesInRegion(TString region, RooAbsPdf* regionPdf);
  /**
    Get all component (sample) fractions in region  
  */
  std::vector<double> GetAllComponentFracInRegion(RooWorkspace* w, TString region, RooAbsPdf* regionPdf, RooRealVar* obsRegion, RooRealVar* binWidth);
  
  /**
     Get region name as used in RooCategory of the simultaneous PDF
  */
  TString GetFullRegionName(RooCategory* regionCat,  TString regionShortName);


  // Helper functions - to be moved
  double looseToTightVal(const TString& reg, TMap* map);
  double looseToTightErr(const TString& reg, TMap* map);
  double getNonQcdVal(const TString& proc, const TString& reg, TMap* map, const TString& opt);
  
  std::vector<TString> Tokens(TString aline,TString aDelim);
  std::vector<TString> TokensALL(RooCategory* cat);

  TString scanStrForFloats(const TString& toscan, const TString& format);

 
  // Functions for toy generation with ToyMCSampler
  /**
     Get parameter of interest (POI) out of ModelConfig in workspace
  */
  RooRealVar* GetPOI( const RooWorkspace* w );
  /**
     Get RooMCStudy based on PDF contained in ModelConfig of the workspace
  */
  RooMCStudy* GetMCStudy( const RooWorkspace* w );

  /**
   Get error band for a specific systematic
   @param hNom  -> Nominal Histogram Name
   @param hHigh -> High Systematic Histogram Name
   @param hLow  -> Low Systematic Histogram Name
  */
  TGraph* getErrorBand(TH1F* hNom, TH1F* hHigh, TH1F* hLow);

  /**
  Plot a sample distribution of a specific varible with the error related to a specifc systematic
  @param f          -> histCacheFile
  @param hNomName   -> Nominal Histogram Name
  @param Syst       -> Systematic Name
  @param NameSample -> Sample Name
  @param Region     -> Region:{ex. SR,CR,VR}
  @param Var        -> Varible  
  */
  
  void plotDistribution(TFile* f, TString hNomName, TString Syst, TString NameSample, TString Region, TString Var);

  /**
  Plot the systematic variations due to the considered systematics
  @param f          -> histCacheFile
  @param hNomName   -> Nominal Histogram Name
  @param Syst       -> Systematics
  @param NameSample -> Sample Name
  @param Region     -> Region:{ex. SR,CR,VR}
  @param Var        -> Varible  
  */

 void plotSystematics(TFile* f,TString hNomName, std::vector<TString> Syst, TString NameSample, TString Region, TString Var);

  /**
  Call plotSystematics and plotDistribution
  @param FileName   -> Name of the histCacheFile
  @param NameSample -> Sample Name
  @param SystName   -> List of the Systematics ex. JER,JES (a comma should be used to between each systematic)
  @param Region     -> Region:{ex. SR,CR,VR}
  @param Var        -> Varible  
  */

 void plotUpDown(TString FileName, TString NameSample, TString SystName, TString Region, TString Var);



}

# endif
